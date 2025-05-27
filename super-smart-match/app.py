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
        self.reverse_algorithms = {}
        self.load_algorithms()
    
    def load_algorithms(self):
        # Algorithmes candidat → jobs
        self.algorithms['fallback'] = self.simple_matching
        
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
        
        try:
            from matching_engine_advanced import advanced_match_candidate_with_jobs
            self.algorithms['advanced'] = advanced_match_candidate_with_jobs
            logger.info("✅ Algorithme ADVANCED chargé (candidat → jobs)")
        except ImportError:
            logger.warning("⚠️ Algorithme advanced non disponible")
        
        # NOUVEAU : Algorithmes entreprise → candidats
        self.reverse_algorithms['reverse_fallback'] = self.simple_reverse_matching
        
        try:
            from matching_engine_reverse import reverse_match_job_with_candidates
            self.reverse_algorithms['reverse_advanced'] = reverse_match_job_with_candidates
            logger.info("✅ Algorithme REVERSE ADVANCED chargé (entreprise → candidats)")
        except ImportError:
            logger.warning("⚠️ Algorithme reverse non disponible")
        
        logger.info(f"📊 {len(self.algorithms)} algorithmes candidat, {len(self.reverse_algorithms)} algorithmes entreprise")
    
    def simple_matching(self, cv_data, questionnaire_data, job_data):
        """Algorithme simple candidat → jobs"""
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
    
    def simple_reverse_matching(self, job_data, candidates_data):
        """Algorithme simple entreprise → candidats"""
        results = []
        job_skills = set(job_data.get('competences', []))
        
        for candidate in candidates_data:
            cv_data = candidate.get('cv_data', {})
            candidate_skills = set(cv_data.get('competences', []))
            
            if candidate_skills and job_skills:
                common_skills = candidate_skills.intersection(job_skills)
                score = (len(common_skills) / len(job_skills)) * 100 if job_skills else 50
            else:
                score = 50
            
            candidate_copy = candidate.copy()
            candidate_copy['matching_score'] = min(100, max(0, int(score)))
            results.append(candidate_copy)
        
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def match(self, cv_data, questionnaire_data, job_data, algorithm="auto", limit=10):
        """Méthode matching candidat → jobs"""
        try:
            if algorithm == "auto":
                if 'advanced' in self.algorithms:
                    algorithm = 'advanced'
                elif 'enhanced' in self.algorithms:
                    algorithm = 'enhanced'
                elif 'original' in self.algorithms:
                    algorithm = 'original'
                else:
                    algorithm = 'fallback'
            
            if algorithm not in self.algorithms:
                algorithm = 'fallback'
            
            results = self.algorithms[algorithm](cv_data, questionnaire_data, job_data)
            
            if limit > 0:
                results = results[:limit]
            
            return {
                'success': True,
                'matching_mode': 'candidate_to_jobs',
                'algorithm_used': algorithm,
                'total_results': len(results),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Erreur matching candidat: {e}")
            results = self.simple_matching(cv_data, questionnaire_data, job_data)
            return {
                'success': True,
                'matching_mode': 'candidate_to_jobs',
                'algorithm_used': 'fallback',
                'total_results': len(results),
                'results': results[:limit] if limit > 0 else results,
                'fallback_used': True,
                'error': str(e)
            }
    
    def reverse_match(self, job_data, candidates_data, algorithm="auto", limit=10):
        """NOUVEAU : Méthode matching entreprise → candidats"""
        try:
            if algorithm == "auto":
                if 'reverse_advanced' in self.reverse_algorithms:
                    algorithm = 'reverse_advanced'
                else:
                    algorithm = 'reverse_fallback'
            
            if algorithm not in self.reverse_algorithms:
                algorithm = 'reverse_fallback'
            
            if algorithm == 'reverse_advanced':
                results = self.reverse_algorithms[algorithm](job_data, candidates_data, limit)
            else:
                results = self.reverse_algorithms[algorithm](job_data, candidates_data)
            
            if limit > 0 and algorithm == 'reverse_fallback':
                results = results[:limit]
            
            return {
                'success': True,
                'matching_mode': 'company_to_candidates',
                'algorithm_used': algorithm,
                'job_analyzed': {
                    'id': job_data.get('id', 'unknown'),
                    'titre': job_data.get('titre', 'Poste sans titre'),
                    'entreprise': job_data.get('entreprise', 'Entreprise non spécifiée')
                },
                'total_results': len(results),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Erreur matching entreprise: {e}")
            results = self.simple_reverse_matching(job_data, candidates_data)
            return {
                'success': True,
                'matching_mode': 'company_to_candidates',
                'algorithm_used': 'reverse_fallback',
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
        'version': '2.1 - Bidirectional Matching',
        'modes': {
            'candidate_to_jobs': 'Matching candidat vers emplois',
            'company_to_candidates': 'Matching entreprise vers candidats'
        },
        'algorithms': {
            'candidate_algorithms': list(service.algorithms.keys()),
            'company_algorithms': list(service.reverse_algorithms.keys())
        }
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'candidate_algorithms_loaded': len(service.algorithms),
        'company_algorithms_loaded': len(service.reverse_algorithms),
        'available_algorithms': {
            'candidate_to_jobs': list(service.algorithms.keys()),
            'company_to_candidates': list(service.reverse_algorithms.keys())
        },
        'features': [
            'Bidirectional matching (candidate ↔ company)',
            'Travel time calculation',
            'Intelligent weighting',
            'Detailed explanations',
            'Contract type matching (CDI/CDD/INTERIM)',
            'Salary optimization',
            'Transport mode support',
            'Career goals alignment',
            'Adaptability scoring'
        ]
    })

@app.route('/api/algorithms')
def algorithms():
    candidate_algorithms = {}
    for name in service.algorithms.keys():
        if name == 'advanced':
            candidate_algorithms[name] = {
                'status': 'available',
                'features': ['travel_time', 'intelligent_weighting', 'explanations'],
                'description': 'Moteur avancé candidat vers jobs'
            }
        elif name == 'enhanced':
            candidate_algorithms[name] = {
                'status': 'available', 
                'features': ['enhanced_scoring'],
                'description': 'Moteur amélioré candidat vers jobs'
            }
        elif name == 'original':
            candidate_algorithms[name] = {
                'status': 'available',
                'features': ['basic_matching'],
                'description': 'Moteur de base candidat vers jobs'
            }
        else:
            candidate_algorithms[name] = {
                'status': 'available',
                'features': ['fallback'],
                'description': 'Algorithme simple candidat vers jobs'
            }
    
    company_algorithms = {}
    for name in service.reverse_algorithms.keys():
        if name == 'reverse_advanced':
            company_algorithms[name] = {
                'status': 'available',
                'features': ['intelligent_company_weighting', 'career_goals_matching', 'adaptability_scoring'],
                'description': 'Moteur avancé entreprise vers candidats'
            }
        else:
            company_algorithms[name] = {
                'status': 'available',
                'features': ['fallback'],
                'description': 'Algorithme simple entreprise vers candidats'
            }
    
    return jsonify({
        'candidate_algorithms': candidate_algorithms,
        'company_algorithms': company_algorithms,
        'total_count': len(service.algorithms) + len(service.reverse_algorithms),
        'recommended': {
            'candidate_to_jobs': 'advanced',
            'company_to_candidates': 'reverse_advanced'
        }
    })

@app.route('/api/match', methods=['POST'])
def match():
    """Endpoint existant : matching candidat → jobs"""
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
        logger.error(f"Erreur API match: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/match-candidates', methods=['POST'])
def match_candidates():
    """NOUVEAU : Endpoint matching entreprise → candidats"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON required'}), 400
        
        job_data = data.get('job_data', {})
        candidates_data = data.get('candidates_data', [])
        algorithm = data.get('algorithm', 'auto')
        limit = data.get('limit', 10)
        
        if not job_data:
            return jsonify({'error': 'job_data required'}), 400
        
        if not candidates_data:
            return jsonify({'error': 'candidates_data required'}), 400
        
        result = service.reverse_match(job_data, candidates_data, algorithm, limit)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur API match-candidates: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-data')
def get_test_data():
    """Données de test pour les deux modes"""
    return jsonify({
        'candidate_to_jobs_example': {
            'cv_data': {
                'competences': ['Python', 'Django', 'PostgreSQL', 'React'],
                'annees_experience': 5,
                'niveau_etudes': 'Master',
                'derniere_fonction': 'Développeur Full Stack',
                'secteur_activite': 'FinTech'
            },
            'questionnaire_data': {
                'adresse': 'Paris 15ème',
                'salaire_souhaite': 55000,
                'types_contrat': ['CDI'],
                'mode_transport': 'metro',
                'temps_trajet_max': 45,
                'date_disponibilite': '2025-06-01',
                'raison_changement': 'evolution',
                'priorite': 'equilibre',
                'objectif': 'competences'
            },
            'job_data': [
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
                }
            ]
        },
        'company_to_candidates_example': {
            'job_data': {
                'id': 'startup-lead-001',
                'titre': 'Lead Developer',
                'entreprise': 'TechStartup',
                'competences': ['Python', 'Django', 'React', 'AWS'],
                'localisation': 'Paris 2ème',
                'type_contrat': 'CDI',
                'salaire_min': 65000,
                'salaire_max': 80000,
                'experience_requise': 5,
                'teletravail_possible': True,
                'type_entreprise': 'startup',
                'niveau_poste': 'senior',
                'description': 'Lead une équipe de 4 développeurs, architecture technique, évolution vers CTO possible'
            },
            'candidates_data': [
                {
                    'candidate_id': 'cand-001',
                    'cv_data': {
                        'nom': 'Marie Dupont',
                        'competences': ['Python', 'Django', 'PostgreSQL', 'AWS'],
                        'annees_experience': 6,
                        'niveau_etudes': 'Master',
                        'derniere_fonction': 'Senior Developer'
                    },
                    'questionnaire_data': {
                        'adresse': 'Paris 11ème',
                        'salaire_souhaite': 70000,
                        'types_contrat': ['CDI'],
                        'mode_transport': 'metro',
                        'temps_trajet_max': 60,
                        'objectif': 'evolution',
                        'niveau_ambition': 'élevé',
                        'mobilite': 'moyen',
                        'accepte_teletravail': True
                    }
                },
                {
                    'candidate_id': 'cand-002', 
                    'cv_data': {
                        'nom': 'Jean Martin',
                        'competences': ['JavaScript', 'React', 'Node.js'],
                        'annees_experience': 3,
                        'niveau_etudes': 'Bachelor'
                    },
                    'questionnaire_data': {
                        'adresse': 'Boulogne-Billancourt',
                        'salaire_souhaite': 50000,
                        'types_contrat': ['CDI', 'CDD'],
                        'mode_transport': 'voiture',
                        'objectif': 'stabilite',
                        'niveau_ambition': 'moyen'
                    }
                }
            ]
        }
    })

if __name__ == '__main__':
    port = 5061
    logger.info(f"🚀 Démarrage SuperSmartMatch v2.1 BIDIRECTIONNEL sur le port {port}")
    logger.info("🎯 Nouvelles fonctionnalités: matching candidat ↔ entreprise")
    app.run(host='0.0.0.0', port=port, debug=False)
