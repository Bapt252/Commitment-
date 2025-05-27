#!/usr/bin/env python3

import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Ajouter le répertoire parent
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SuperSmartMatch:
    def __init__(self):
        self.algorithms = {}
        self.load_algorithms()
    
    def load_algorithms(self):
        # Algorithme simple de fallback
        self.algorithms['fallback'] = self.simple_matching
        
        # Essayer de charger les autres algorithmes
        try:
            from matching_engine import match_candidate_with_jobs
            self.algorithms['original'] = match_candidate_with_jobs
            logger.info("✅ Algorithme ORIGINAL chargé")
        except ImportError:
            logger.warning("⚠️ Algorithme original non disponible")
        
        try:
            from matching_engine_enhanced import enhanced_match_candidate_with_jobs
            self.algorithms['enhanced'] = enhanced_match_candidate_with_jobs
            logger.info("✅ Algorithme ENHANCED chargé")
        except ImportError:
            logger.warning("⚠️ Algorithme enhanced non disponible")
        
        # NOUVEAU : Charger l'algorithme avancé
        try:
            from matching_engine_advanced import advanced_match_candidate_with_jobs
            self.algorithms['advanced'] = advanced_match_candidate_with_jobs
            logger.info("✅ Algorithme ADVANCED chargé (avec temps trajet et pondération intelligente)")
        except ImportError:
            logger.warning("⚠️ Algorithme advanced non disponible")
        
        logger.info(f"📊 {len(self.algorithms)} algorithmes chargés")
    
    def simple_matching(self, cv_data, questionnaire_data, job_data):
        """Algorithme simple qui fonctionne toujours"""
        results = []
        candidate_skills = set(cv_data.get('competences', []))
        
        for job in job_data:
            job_skills = set(job.get('competences', []))
            
            if candidate_skills and job_skills:
                common_skills = candidate_skills.intersection(job_skills)
                score = (len(common_skills) / len(job_skills)) * 100 if job_skills else 50
            else:
                score = 50
            
            job_copy = job.copy()
            job_copy['matching_score'] = min(100, max(0, int(score)))
            results.append(job_copy)
        
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def match(self, cv_data, questionnaire_data, job_data, algorithm="auto", limit=10):
        """Méthode principale avec sélection automatique améliorée"""
        try:
            # Sélection de l'algorithme avec priorité au nouveau moteur avancé
            if algorithm == "auto":
                if 'advanced' in self.algorithms:
                    algorithm = 'advanced'  # NOUVEAU : Prioriser advanced
                elif 'enhanced' in self.algorithms:
                    algorithm = 'enhanced'
                elif 'original' in self.algorithms:
                    algorithm = 'original'
                else:
                    algorithm = 'fallback'
            
            if algorithm not in self.algorithms:
                algorithm = 'fallback'
            
            # Exécution
            results = self.algorithms[algorithm](cv_data, questionnaire_data, job_data)
            
            if limit > 0:
                results = results[:limit]
            
            return {
                'success': True,
                'algorithm_used': algorithm,
                'total_results': len(results),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Erreur: {e}")
            # Fallback vers l'algorithme simple
            results = self.simple_matching(cv_data, questionnaire_data, job_data)
            return {
                'success': True,
                'algorithm_used': 'fallback',
                'total_results': len(results),
                'results': results[:limit] if limit > 0 else results,
                'fallback_used': True,
                'error': str(e)
            }

# Instance globale
service = SuperSmartMatch()

@app.route('/')
def index():
    return jsonify({
        'service': 'SuperSmartMatch',
        'status': 'running',
        'algorithms': list(service.algorithms.keys()),
        'version': '2.0 - Advanced Matching with Travel Time'
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'algorithms_loaded': len(service.algorithms),
        'available_algorithms': list(service.algorithms.keys()),
        'features': [
            'Travel time calculation',
            'Intelligent weighting',
            'Detailed explanations',
            'Contract type matching (CDI/CDD/INTERIM)',
            'Salary optimization',
            'Transport mode support'
        ]
    })

@app.route('/api/algorithms')
def algorithms():
    algorithms_info = {}
    for name in service.algorithms.keys():
        if name == 'advanced':
            algorithms_info[name] = {
                'status': 'available',
                'features': ['travel_time', 'intelligent_weighting', 'explanations'],
                'description': 'Moteur avancé avec calcul temps trajet et pondération intelligente'
            }
        elif name == 'enhanced':
            algorithms_info[name] = {
                'status': 'available', 
                'features': ['enhanced_scoring'],
                'description': 'Moteur amélioré avec scoring détaillé'
            }
        elif name == 'original':
            algorithms_info[name] = {
                'status': 'available',
                'features': ['basic_matching'],
                'description': 'Moteur de base du projet'
            }
        else:
            algorithms_info[name] = {
                'status': 'available',
                'features': ['fallback'],
                'description': 'Algorithme simple de secours'
            }
    
    return jsonify({
        'algorithms': algorithms_info,
        'total_count': len(service.algorithms),
        'recommended': 'advanced'
    })

@app.route('/api/match', methods=['POST'])
def match():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON required'}), 400
        
        cv_data = data.get('cv_data', {})
        questionnaire_data = data.get('questionnaire_data', {})
        job_data = data.get('job_data', [])
        algorithm = data.get('algorithm', 'auto')
        limit = data.get('limit', 10)
        
        if not job_data:
            return jsonify({'error': 'job_data required'}), 400
        
        result = service.match(cv_data, questionnaire_data, job_data, algorithm, limit)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur API: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-data')
def get_test_data():
    """Endpoint pour récupérer des données de test réalistes"""
    return jsonify({
        'cv_data_example': {
            'competences': ['Python', 'Django', 'PostgreSQL', 'React'],
            'annees_experience': 5,
            'niveau_etudes': 'Master',
            'derniere_fonction': 'Développeur Full Stack',
            'secteur_activite': 'FinTech'
        },
        'questionnaire_data_example': {
            'adresse': 'Paris 15ème',
            'salaire_souhaite': 55000,
            'types_contrat': ['CDI'],
            'mode_transport': 'metro',
            'temps_trajet_max': 45,
            'date_disponibilite': '2025-06-01',
            'raison_changement': 'evolution',  # Pour pondération intelligente
            'priorite': 'equilibre',
            'objectif': 'competences'
        },
        'job_data_example': [
            {
                'id': 'job-001',
                'titre': 'Développeur Python Senior',
                'entreprise': 'TechCorp',
                'competences': ['Python', 'Django', 'PostgreSQL'],
                'localisation': 'Paris 8ème',
                'type_contrat': 'CDI',
                'salaire_min': 50000,
                'salaire_max': 65000,
                'experience_requise': 3,
                'date_debut_souhaitee': '2025-06-15',
                'teletravail_possible': False,
                'description': 'Développement applications web'
            },
            {
                'id': 'job-002', 
                'titre': 'Full Stack Developer',
                'entreprise': 'StartupInc',
                'competences': ['Python', 'React', 'MySQL'],
                'localisation': 'Levallois-Perret',
                'type_contrat': 'CDI',
                'salaire_min': 45000,
                'salaire_max': 55000,
                'experience_requise': 4,
                'date_debut_souhaitee': '2025-07-01',
                'teletravail_possible': True,
                'politique_remote': 'Télétravail 2j/semaine'
            }
        ]
    })

if __name__ == '__main__':
    port = 5061  # Port 5061 pour éviter les conflits
    logger.info(f"🚀 Démarrage SuperSmartMatch v2.0 sur le port {port}")
    logger.info("🎯 Nouvelles fonctionnalités: temps de trajet, pondération intelligente")
    app.run(host='0.0.0.0', port=port, debug=False)
