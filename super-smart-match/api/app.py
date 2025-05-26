#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application Flask pour SuperSmartMatch
API unifiée pour tous les algorithmes de matching
"""

import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, InternalServerError
import time

from ..core.engine import SuperSmartMatchEngine, MatchOptions, AlgorithmType
from ..utils.data_adapter import DataAdapter
from ..utils.performance import PerformanceMonitor

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config=None):
    """
    Factory pour créer l'application Flask
    
    Args:
        config: Configuration optionnelle
        
    Returns:
        Application Flask configurée
    """
    app = Flask(__name__)
    
    # Configuration CORS pour permettre les requêtes cross-origin
    CORS(app, origins=["*"])
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-smart-match-dev-key')
    app.config['DEBUG'] = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Initialisation des services
    engine = SuperSmartMatchEngine(config)
    data_adapter = DataAdapter()
    performance_monitor = PerformanceMonitor()
    
    @app.errorhandler(BadRequest)
    def handle_bad_request(e):
        """Gestionnaire d'erreur pour les requêtes malformées"""
        return jsonify({
            "status": "error",
            "error": "bad_request",
            "message": str(e.description),
            "code": 400
        }), 400
    
    @app.errorhandler(InternalServerError)
    def handle_internal_error(e):
        """Gestionnaire d'erreur pour les erreurs serveur"""
        logger.error(f"Erreur interne: {e}")
        return jsonify({
            "status": "error",
            "error": "internal_server_error",
            "message": "Une erreur interne s'est produite",
            "code": 500
        }), 500
    
    @app.route('/', methods=['GET'])
    def home():
        """Page d'accueil du service"""
        return jsonify({
            "service": "SuperSmartMatch",
            "version": "1.0.0",
            "description": "Service unifié de matching intelligent pour Nexten",
            "status": "running",
            "algorithms": engine.get_available_algorithms(),
            "endpoints": {
                "match": "/api/v1/match",
                "compare": "/api/v1/compare",
                "performance": "/api/v1/performance",
                "health": "/api/v1/health",
                "explain": "/api/v1/explain"
            }
        })
    
    @app.route('/api/v1/health', methods=['GET'])
    def health_check():
        """Vérification de l'état du service"""
        return jsonify({
            "status": "healthy",
            "timestamp": time.time(),
            "uptime": performance_monitor.get_uptime(),
            "version": "1.0.0",
            "algorithms_available": len(engine.get_available_algorithms())
        })
    
    @app.route('/api/v1/match', methods=['POST'])
    def match():
        """
        Endpoint principal de matching
        
        Body JSON attendu:
        {
            "candidat": {...},
            "offres": [...],
            "options": {...}
        }
        """
        try:
            # Validation de la requête
            if not request.is_json:
                raise BadRequest("Content-Type doit être application/json")
            
            data = request.get_json()
            
            if not data:
                raise BadRequest("Données JSON manquantes")
            
            # Extraction des données
            candidat = data.get('candidat')
            offres = data.get('offres', [])
            options_dict = data.get('options', {})
            
            if not candidat:
                raise BadRequest("Données candidat manquantes")
            
            if not offres:
                raise BadRequest("Liste d'offres vide")
            
            # Création des options
            options = MatchOptions(
                algorithme=AlgorithmType(options_dict.get('algorithme', 'auto')),
                limite=min(options_dict.get('limite', 10), 50),  # Limite max 50
                seuil_minimum=options_dict.get('seuil_minimum', 0.6),
                details=options_dict.get('details', True),
                explications=options_dict.get('explications', True),
                performance_tracking=options_dict.get('performance_tracking', True)
            )
            
            logger.info(f"Requête de matching: {len(offres)} offres, algorithme: {options.algorithme.value}")
            
            # Exécution du matching
            result = engine.match(candidat, offres, options)
            
            # Conversion en réponse JSON
            return jsonify({
                "status": result.status,
                "algorithme_utilise": result.algorithme_utilise,
                "temps_execution": result.temps_execution,
                "resultats": [
                    {
                        "id": r.id,
                        "titre": r.titre,
                        "score_global": r.score_global,
                        "scores_details": r.scores_details if options.details else {},
                        "explications": r.explications if options.explications else {},
                        "confiance": r.confiance,
                        "donnees_originales": r.donnees_originales
                    }
                    for r in result.resultats
                ],
                "meta": result.meta,
                "erreurs": result.erreurs
            })
            
        except ValueError as e:
            logger.error(f"Erreur de validation: {e}")
            raise BadRequest(str(e))
        except Exception as e:
            logger.error(f"Erreur lors du matching: {e}")
            raise InternalServerError()
    
    @app.route('/api/v1/compare', methods=['POST'])
    def compare_algorithms():
        """
        Compare tous les algorithmes sur les mêmes données
        
        Body JSON attendu:
        {
            "candidat": {...},
            "offres": [...],
            "options": {...}
        }
        """
        try:
            if not request.is_json:
                raise BadRequest("Content-Type doit être application/json")
            
            data = request.get_json()
            candidat = data.get('candidat')
            offres = data.get('offres', [])
            
            if not candidat or not offres:
                raise BadRequest("Données candidat ou offres manquantes")
            
            # Options pour la comparaison
            options = MatchOptions(
                algorithme=AlgorithmType.COMPARISON,
                limite=10,
                details=True,
                explications=True
            )
            
            logger.info(f"Comparaison d'algorithmes: {len(offres)} offres")
            
            # Exécution de la comparaison
            result = engine.match(candidat, offres, options)
            
            # Analyse détaillée des performances
            algorithm_performance = engine.get_algorithm_performance()
            
            return jsonify({
                "status": result.status,
                "comparaison": {
                    "resultats": [
                        {
                            "id": r.id,
                            "titre": r.titre,
                            "score_global": r.score_global,
                            "scores_par_algorithme": r.donnees_originales.get('algorithm_scores', {}),
                            "confiance": r.confiance
                        }
                        for r in result.resultats
                    ],
                    "performance_globale": algorithm_performance,
                    "recommandations": _generate_recommendations(result, algorithm_performance)
                },
                "meta": result.meta,
                "temps_execution": result.temps_execution
            })
            
        except ValueError as e:
            logger.error(f"Erreur de validation: {e}")
            raise BadRequest(str(e))
        except Exception as e:
            logger.error(f"Erreur lors de la comparaison: {e}")
            raise InternalServerError()
    
    @app.route('/api/v1/explain', methods=['POST'])
    def explain_selection():
        """
        Explique la sélection d'algorithme pour des données données
        
        Body JSON attendu:
        {
            "candidat": {...},
            "offres": [...]
        }
        """
        try:
            if not request.is_json:
                raise BadRequest("Content-Type doit être application/json")
            
            data = request.get_json()
            candidat = data.get('candidat')
            offres = data.get('offres', [])
            
            if not candidat or not offres:
                raise BadRequest("Données candidat ou offres manquantes")
            
            # Adaptation des données
            candidat_adapte = data_adapter.adapt_candidate(candidat)
            offres_adaptees = data_adapter.adapt_jobs(offres)
            
            # Explication de la sélection
            explanation = engine.selector.explain_selection(candidat_adapte, offres_adaptees)
            
            return jsonify({
                "status": "success",
                "explication": explanation,
                "donnees_analysees": {
                    "candidat_fields": list(candidat.keys()),
                    "nombre_offres": len(offres),
                    "offres_sample": offres[0] if offres else {}
                }
            })
            
        except ValueError as e:
            logger.error(f"Erreur de validation: {e}")
            raise BadRequest(str(e))
        except Exception as e:
            logger.error(f"Erreur lors de l'explication: {e}")
            raise InternalServerError()
    
    @app.route('/api/v1/performance', methods=['GET'])
    def get_performance():
        """Retourne les statistiques de performance du service"""
        try:
            performance_stats = engine.get_algorithm_performance()
            system_stats = performance_monitor.get_system_stats()
            
            return jsonify({
                "status": "success",
                "performance": {
                    "algorithms": performance_stats,
                    "system": system_stats,
                    "uptime": performance_monitor.get_uptime()
                }
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des performances: {e}")
            raise InternalServerError()
    
    @app.route('/api/v1/benchmark', methods=['POST'])
    def run_benchmark():
        """
        Lance un benchmark des algorithmes
        
        Body JSON attendu:
        {
            "test_cases": [
                {
                    "candidat": {...},
                    "offres": [...]
                }
            ]
        }
        """
        try:
            if not request.is_json:
                raise BadRequest("Content-Type doit être application/json")
            
            data = request.get_json()
            test_cases = data.get('test_cases', [])
            
            if not test_cases:
                raise BadRequest("Cas de test manquants")
            
            logger.info(f"Lancement du benchmark avec {len(test_cases)} cas de test")
            
            # Lancement du benchmark
            benchmark_results = engine.selector.benchmark_algorithms(test_cases)
            
            return jsonify({
                "status": "success",
                "benchmark": benchmark_results,
                "test_cases_count": len(test_cases)
            })
            
        except ValueError as e:
            logger.error(f"Erreur de validation: {e}")
            raise BadRequest(str(e))
        except Exception as e:
            logger.error(f"Erreur lors du benchmark: {e}")
            raise InternalServerError()
    
    @app.route('/api/v1/algorithms', methods=['GET'])
    def list_algorithms():
        """Liste tous les algorithmes disponibles avec leurs capacités"""
        try:
            algorithms = engine.get_available_algorithms()
            
            algorithms_info = []
            for algo_name in algorithms:
                config = engine.selector.get_algorithm_config(algo_name)
                algorithms_info.append(config)
            
            return jsonify({
                "status": "success",
                "algorithms": algorithms_info,
                "total": len(algorithms)
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la liste des algorithmes: {e}")
            raise InternalServerError()
    
    # Route pour servir les fichiers statiques (dashboard web)
    @app.route('/dashboard')
    def dashboard():
        """Dashboard web pour monitorer les performances"""
        return render_template('dashboard.html')
    
    def _generate_recommendations(result, performance_stats):
        """
        Génère des recommandations basées sur les résultats de comparaison
        
        Args:
            result: Résultats de la comparaison
            performance_stats: Statistiques de performance
            
        Returns:
            Liste de recommandations
        """
        recommendations = []
        
        # Analyser les scores moyens par algorithme
        if result.resultats:
            algorithm_scores = {}
            
            for resultat in result.resultats:
                scores_by_algo = resultat.donnees_originales.get('algorithm_scores', {})
                for algo, score in scores_by_algo.items():
                    if algo not in algorithm_scores:
                        algorithm_scores[algo] = []
                    algorithm_scores[algo].append(score)
            
            # Calculer les moyennes
            avg_scores = {
                algo: sum(scores) / len(scores) 
                for algo, scores in algorithm_scores.items()
                if scores
            }
            
            # Trouver le meilleur algorithme
            if avg_scores:
                best_algo = max(avg_scores.items(), key=lambda x: x[1])
                recommendations.append({
                    "type": "best_algorithm",
                    "message": f"L'algorithme '{best_algo[0]}' obtient les meilleurs résultats (score moyen: {best_algo[1]:.1f}%)",
                    "algorithm": best_algo[0],
                    "score": best_algo[1]
                })
            
            # Recommandations de performance
            if performance_stats:
                fastest_algo = min(
                    performance_stats.items(), 
                    key=lambda x: x[1].get('avg_execution_time', float('inf'))
                )
                
                recommendations.append({
                    "type": "performance",
                    "message": f"L'algorithme '{fastest_algo[0]}' est le plus rapide (temps moyen: {fastest_algo[1].get('avg_execution_time', 0):.3f}s)",
                    "algorithm": fastest_algo[0]
                })
        
        return recommendations
    
    return app

# Point d'entrée pour le développement
if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
