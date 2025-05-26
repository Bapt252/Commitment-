#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SuperSmartMatch - Service unifié de matching pour Nexten
Regroupe tous les algorithmes de matching sous une seule API
"""

import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import importlib.util

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SuperSmartMatch:
    """
    Service unifié de matching qui regroupe tous les algorithmes disponibles
    """
    
    def __init__(self):
        self.algorithms = {}
        self.default_algorithm = "enhanced"
        self.load_algorithms()
    
    def load_algorithms(self):
        """Charge tous les algorithmes disponibles"""
        try:
            # Import de l'algorithme original
            from matching_engine import match_candidate_with_jobs as original_algo
            self.algorithms['original'] = original_algo
            logger.info("✅ Algorithme ORIGINAL chargé")
        except ImportError as e:
            logger.warning(f"❌ Impossible de charger l'algorithme original: {e}")
        
        try:
            # Import de l'algorithme Enhanced
            from matching_engine_enhanced import enhanced_match_candidate_with_jobs as enhanced_algo
            self.algorithms['enhanced'] = enhanced_algo
            logger.info("✅ Algorithme ENHANCED chargé")
        except ImportError as e:
            logger.warning(f"❌ Impossible de charger l'algorithme enhanced: {e}")
        
        try:
            # Import de votre algorithme personnalisé
            from my_matching_engine import match_candidate_with_jobs as custom_algo
            self.algorithms['custom'] = custom_algo
            logger.info("✅ Algorithme CUSTOM chargé")
        except ImportError as e:
            logger.warning(f"❌ Impossible de charger l'algorithme custom: {e}")
        
        try:
            # Import du SmartMatch
            self.load_smart_match()
        except Exception as e:
            logger.warning(f"❌ Impossible de charger SmartMatch: {e}")
        
        # Algorithme hybride (combine plusieurs algorithmes)
        self.algorithms['hybrid'] = self.hybrid_matching
        logger.info("✅ Algorithme HYBRID configuré")
        
        logger.info(f"🎯 {len(self.algorithms)} algorithmes chargés: {list(self.algorithms.keys())}")
    
    def load_smart_match(self):
        """Charge l'algorithme SmartMatch si disponible"""
        try:
            # Tenter de charger SmartMatch
            spec = importlib.util.spec_from_file_location("smartmatch", "../app/smartmatch.py")
            if spec and spec.loader:
                smartmatch_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(smartmatch_module)
                
                def smart_match_adapter(cv_data, questionnaire_data, job_data):
                    """Adaptateur pour SmartMatch"""
                    engine = smartmatch_module.SmartMatchEngine()
                    
                    # Conversion des données pour SmartMatch
                    candidates = [{
                        'id': 'candidate_1',
                        'skills': cv_data.get('competences', []),
                        'experience': cv_data.get('annees_experience', 0),
                        'location': questionnaire_data.get('adresse', ''),
                        'remote_preference': questionnaire_data.get('mobilite', 'on_site'),
                        'salary_expectation': questionnaire_data.get('salaire_souhaite', 0)
                    }]
                    
                    companies = []
                    for i, job in enumerate(job_data):
                        companies.append({
                            'id': f'company_{i}',
                            'required_skills': job.get('competences', []),
                            'location': job.get('localisation', ''),
                            'remote_policy': job.get('politique_remote', 'on_site'),
                            'salary_range': {'min': 0, 'max': 100000},
                            'required_experience': job.get('experience_requise', 0)
                        })
                    
                    # Exécution du matching
                    results = engine.match(candidates, companies)
                    
                    # Conversion des résultats
                    formatted_results = []
                    for result in results:
                        job_index = int(result['company_id'].split('_')[1])
                        job_copy = job_data[job_index].copy()
                        job_copy['matching_score'] = int(result['score'] * 100)
                        formatted_results.append(job_copy)
                    
                    return formatted_results
                
                self.algorithms['smart_match'] = smart_match_adapter
                logger.info("✅ Algorithme SMART_MATCH chargé")
                
        except Exception as e:
            logger.warning(f"Impossible de charger SmartMatch: {e}")
    
    def hybrid_matching(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict]) -> List[Dict]:
        """
        Algorithme hybride qui combine plusieurs approches pour un meilleur résultat
        """
        logger.info("🔄 Exécution de l'algorithme HYBRID")
        
        all_results = {}
        algorithms_used = []
        
        # Exécuter les algorithmes disponibles
        for name, algo in self.algorithms.items():
            if name == 'hybrid':  # Éviter la récursion
                continue
                
            try:
                start_time = time.time()
                results = algo(cv_data, questionnaire_data, job_data)
                exec_time = time.time() - start_time
                
                algorithms_used.append({
                    'name': name,
                    'execution_time': exec_time,
                    'results_count': len(results)
                })
                
                # Stocker les résultats par ID de job
                for result in results:
                    job_id = result.get('id', result.get('job_id', f"job_{len(all_results)}"))
                    if job_id not in all_results:
                        all_results[job_id] = {
                            'job_data': result.copy(),
                            'scores': {},
                            'algorithms_count': 0
                        }
                    
                    score = result.get('matching_score', 0)
                    all_results[job_id]['scores'][name] = score
                    all_results[job_id]['algorithms_count'] += 1
                
                logger.info(f"✅ {name}: {len(results)} résultats en {exec_time:.3f}s")
                
            except Exception as e:
                logger.error(f"❌ Erreur avec l'algorithme {name}: {e}")
        
        # Calcul du score hybride
        final_results = []
        for job_id, data in all_results.items():
            if data['algorithms_count'] == 0:
                continue
            
            # Calcul de différentes métriques
            scores = list(data['scores'].values())
            
            # Score hybride : moyenne pondérée + bonus de consensus
            weights = {
                'enhanced': 0.4,    # Poids le plus élevé pour l'algorithme enhanced
                'custom': 0.3,      # Votre algorithme personnalisé
                'smart_match': 0.2, # SmartMatch
                'original': 0.1     # Algorithme original comme baseline
            }
            
            weighted_score = 0
            total_weight = 0
            
            for algo_name, score in data['scores'].items():
                weight = weights.get(algo_name, 0.1)
                weighted_score += score * weight
                total_weight += weight
            
            if total_weight > 0:
                hybrid_score = weighted_score / total_weight
            else:
                hybrid_score = sum(scores) / len(scores)
            
            # Bonus de consensus : si tous les algorithmes sont d'accord
            score_variance = sum((s - hybrid_score) ** 2 for s in scores) / len(scores)
            consensus_bonus = max(0, 10 - score_variance/10)  # Bonus max de 10 points
            
            final_score = min(100, hybrid_score + consensus_bonus)
            
            # Préparer le résultat final
            result = data['job_data'].copy()
            result['matching_score'] = round(final_score)
            result['hybrid_details'] = {
                'individual_scores': data['scores'],
                'algorithms_used': list(data['scores'].keys()),
                'consensus_bonus': round(consensus_bonus, 1),
                'score_variance': round(score_variance, 1)
            }
            
            final_results.append(result)
        
        # Tri par score décroissant
        final_results.sort(key=lambda x: x['matching_score'], reverse=True)
        
        logger.info(f"🎯 HYBRID terminé: {len(final_results)} résultats finaux")
        return final_results
    
    def match(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict], 
              algorithm: str = "auto", limit: int = 10) -> Dict[str, Any]:
        """
        Méthode principale de matching
        
        Args:
            cv_data: Données du CV
            questionnaire_data: Données du questionnaire
            job_data: Liste des offres d'emploi
            algorithm: Algorithme à utiliser ("auto", "original", "enhanced", "smart_match", "custom", "hybrid", "comparison")
            limit: Nombre maximum de résultats
            
        Returns:
            Dictionnaire avec les résultats et métadonnées
        """
        start_time = time.time()
        
        # Sélection automatique de l'algorithme
        if algorithm == "auto":
            algorithm = self.select_best_algorithm(cv_data, questionnaire_data, job_data)
        
        # Mode comparaison : exécute tous les algorithmes
        if algorithm == "comparison":
            return self.comparison_mode(cv_data, questionnaire_data, job_data, limit)
        
        # Vérifier que l'algorithme existe
        if algorithm not in self.algorithms:
            available = list(self.algorithms.keys())
            return {
                'error': f"Algorithme '{algorithm}' non disponible",
                'available_algorithms': available,
                'fallback_used': False
            }
        
        try:
            # Exécution de l'algorithme sélectionné
            logger.info(f"🚀 Exécution de l'algorithme: {algorithm.upper()}")
            results = self.algorithms[algorithm](cv_data, questionnaire_data, job_data)
            
            # Limitation du nombre de résultats
            if limit > 0:
                results = results[:limit]
            
            execution_time = time.time() - start_time
            
            return {
                'algorithm_used': algorithm,
                'execution_time': round(execution_time, 3),
                'total_results': len(results),
                'results': results,
                'metadata': {
                    'timestamp': int(time.time()),
                    'candidate_skills_count': len(cv_data.get('competences', [])),
                    'jobs_analyzed': len(job_data)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur avec l'algorithme {algorithm}: {e}")
            
            # Fallback vers l'algorithme par défaut
            if algorithm != self.default_algorithm and self.default_algorithm in self.algorithms:
                logger.info(f"🔄 Fallback vers {self.default_algorithm}")
                fallback_results = self.algorithms[self.default_algorithm](cv_data, questionnaire_data, job_data)
                execution_time = time.time() - start_time
                
                return {
                    'algorithm_used': self.default_algorithm,
                    'execution_time': round(execution_time, 3),
                    'total_results': len(fallback_results),
                    'results': fallback_results[:limit] if limit > 0 else fallback_results,
                    'fallback_used': True,
                    'original_algorithm_error': str(e)
                }
            
            return {
                'error': f"Erreur lors de l'exécution: {e}",
                'algorithm_used': algorithm,
                'fallback_used': False
            }
    
    def select_best_algorithm(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict]) -> str:
        """
        Sélectionne automatiquement le meilleur algorithme en fonction du contexte
        """
        # Analyse du contexte pour choisir le meilleur algorithme
        skills_count = len(cv_data.get('competences', []))
        jobs_count = len(job_data)
        has_location = bool(questionnaire_data.get('adresse'))
        has_salary = bool(questionnaire_data.get('salaire_souhaite'))
        
        # Logique de sélection
        if jobs_count > 50 and skills_count > 10:
            # Pour de gros volumes, utiliser l'algorithme hybride
            return 'hybrid'
        elif has_location and has_salary and skills_count >= 5:
            # Cas complet avec géolocalisation
            return 'smart_match' if 'smart_match' in self.algorithms else 'enhanced'
        elif skills_count >= 3:
            # Cas standard avec compétences
            return 'enhanced'
        else:
            # Cas simple
            return 'original' if 'original' in self.algorithms else 'enhanced'
    
    def comparison_mode(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict], limit: int) -> Dict[str, Any]:
        """
        Mode comparaison : exécute tous les algorithmes et compare les résultats
        """
        logger.info("🔬 Mode COMPARAISON activé")
        start_time = time.time()
        
        comparison_results = {}
        
        for algorithm_name, algorithm_func in self.algorithms.items():
            if algorithm_name == 'hybrid':  # Skip hybrid en mode comparaison
                continue
                
            try:
                algo_start = time.time()
                results = algorithm_func(cv_data, questionnaire_data, job_data)
                algo_time = time.time() - algo_start
                
                if limit > 0:
                    results = results[:limit]
                
                # Calcul de statistiques
                scores = [r.get('matching_score', 0) for r in results]
                comparison_results[algorithm_name] = {
                    'results': results,
                    'execution_time': round(algo_time, 3),
                    'results_count': len(results),
                    'average_score': round(sum(scores) / len(scores) if scores else 0, 1),
                    'max_score': max(scores) if scores else 0,
                    'min_score': min(scores) if scores else 0
                }
                
                logger.info(f"✅ {algorithm_name}: {len(results)} résultats, score moyen: {comparison_results[algorithm_name]['average_score']}%")
                
            except Exception as e:
                logger.error(f"❌ {algorithm_name}: {e}")
                comparison_results[algorithm_name] = {
                    'error': str(e),
                    'results': [],
                    'execution_time': 0
                }
        
        total_time = time.time() - start_time
        
        # Analyse comparative
        valid_algorithms = [name for name, data in comparison_results.items() if 'error' not in data]
        
        if valid_algorithms:
            best_algorithm = max(valid_algorithms, 
                               key=lambda x: comparison_results[x]['average_score'])
            fastest_algorithm = min(valid_algorithms, 
                                  key=lambda x: comparison_results[x]['execution_time'])
        else:
            best_algorithm = fastest_algorithm = None
        
        return {
            'mode': 'comparison',
            'total_execution_time': round(total_time, 3),
            'algorithms_tested': list(comparison_results.keys()),
            'successful_algorithms': valid_algorithms,
            'best_scoring_algorithm': best_algorithm,
            'fastest_algorithm': fastest_algorithm,
            'detailed_results': comparison_results,
            'summary': {
                'total_algorithms': len(comparison_results),
                'successful_algorithms': len(valid_algorithms),
                'failed_algorithms': len(comparison_results) - len(valid_algorithms)
            }
        }

# Instance globale du service
smart_match_service = SuperSmartMatch()

# Routes API
@app.route('/')
def index():
    """Page d'accueil du service"""
    return jsonify({
        'service': 'SuperSmartMatch',
        'version': '1.0.0',
        'description': 'Service unifié de matching pour Nexten',
        'available_algorithms': list(smart_match_service.algorithms.keys()),
        'endpoints': {
            'match': '/api/match',
            'algorithms': '/api/algorithms',
            'health': '/api/health'
        }
    })

@app.route('/api/health')
def health():
    """Endpoint de santé du service"""
    return jsonify({
        'status': 'healthy',
        'service': 'SuperSmartMatch',
        'algorithms_loaded': len(smart_match_service.algorithms),
        'available_algorithms': list(smart_match_service.algorithms.keys())
    })

@app.route('/api/algorithms')
def list_algorithms():
    """Liste des algorithmes disponibles"""
    algorithms_info = {}
    
    for name in smart_match_service.algorithms.keys():
        algorithms_info[name] = {
            'name': name,
            'description': get_algorithm_description(name),
            'status': 'available'
        }
    
    return jsonify({
        'algorithms': algorithms_info,
        'total_count': len(algorithms_info),
        'default_algorithm': smart_match_service.default_algorithm
    })

def get_algorithm_description(algorithm_name: str) -> str:
    """Retourne la description d'un algorithme"""
    descriptions = {
        'original': 'Algorithme de matching original avec calculs de base',
        'enhanced': 'Algorithme amélioré avec pondération dynamique et nouveaux critères',
        'smart_match': 'Algorithme bidirectionnel avec géolocalisation et analyse sémantique',
        'custom': 'Algorithme personnalisé optimisé pour vos besoins spécifiques',
        'hybrid': 'Algorithme hybride combinant tous les autres pour un résultat optimal'
    }
    return descriptions.get(algorithm_name, 'Algorithme de matching avancé')

@app.route('/api/match', methods=['POST'])
def match_endpoint():
    """
    Endpoint principal de matching
    
    Body JSON:
    {
        "cv_data": {...},
        "questionnaire_data": {...},
        "job_data": [...],
        "algorithm": "auto|original|enhanced|smart_match|custom|hybrid|comparison",
        "limit": 10
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Validation des données requises
        required_fields = ['cv_data', 'questionnaire_data', 'job_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Paramètres
        cv_data = data['cv_data']
        questionnaire_data = data['questionnaire_data']
        job_data = data['job_data']
        algorithm = data.get('algorithm', 'auto')
        limit = data.get('limit', 10)
        
        # Validation basique
        if not isinstance(job_data, list) or len(job_data) == 0:
            return jsonify({'error': 'job_data must be a non-empty list'}), 400
        
        # Exécution du matching
        logger.info(f"🎯 Nouvelle demande de matching: {algorithm}, {len(job_data)} jobs, limit={limit}")
        result = smart_match_service.match(cv_data, questionnaire_data, job_data, algorithm, limit)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erreur dans l'endpoint de matching: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Démarrage de SuperSmartMatch")
    logger.info(f"📊 {len(smart_match_service.algorithms)} algorithmes chargés")
    
    port = int(os.environ.get('PORT', 5060))
    app.run(host='0.0.0.0', port=port, debug=True)
