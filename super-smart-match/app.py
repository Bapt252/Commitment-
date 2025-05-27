#!/usr/bin/env python3

import os
import sys
import logging
import time
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
        self.new_algorithms = {}  # Nouveaux algorithmes avec classes
        self.analytics = None  # Analytics system
        self.load_algorithms()
        self.load_analytics()
    
    def load_analytics(self):
        """Charge le système d'analytics"""
        try:
            from analytics import SuperSmartMatchAnalytics
            self.analytics = SuperSmartMatchAnalytics()
            logger.info("✅ Système d'analytics chargé")
        except ImportError as e:
            logger.warning(f"⚠️ Analytics non disponible: {e}")
            self.analytics = None
    
    def load_algorithms(self):
        # Anciens algorithmes candidat → jobs (compatibilité)
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
        
        # NOUVEAU : Chargement des algorithmes basés classes
        try:
            from algorithms.smart_match import SmartMatchAlgorithm
            self.new_algorithms['smart_match'] = SmartMatchAlgorithm()
            logger.info("✅ Algorithme SMART MATCH (classe) chargé")
        except ImportError:
            logger.warning("⚠️ SmartMatchAlgorithm non disponible")
        
        try:
            from algorithms.enhanced import EnhancedAlgorithm
            self.new_algorithms['enhanced_class'] = EnhancedAlgorithm()
            logger.info("✅ Algorithme ENHANCED (classe) chargé")
        except ImportError:
            logger.warning("⚠️ EnhancedAlgorithm non disponible")
            
        try:
            from algorithms.supersmartmatch import SuperSmartMatchAlgorithm
            self.new_algorithms['supersmartmatch'] = SuperSmartMatchAlgorithm()
            logger.info("🚀✅ Algorithme SUPERSMARTMATCH v2.1 chargé - Pondération dynamique!")
        except ImportError as e:
            logger.warning(f"⚠️ SuperSmartMatchAlgorithm v2.1 non disponible: {e}")
        
        # Anciens algorithmes entreprise → candidats
        self.reverse_algorithms['reverse_fallback'] = self.simple_reverse_matching
        
        try:
            from matching_engine_reverse import reverse_match_job_with_candidates
            self.reverse_algorithms['reverse_advanced'] = reverse_match_job_with_candidates
            logger.info("✅ Algorithme REVERSE ADVANCED chargé (entreprise → candidats)")
        except ImportError:
            logger.warning("⚠️ Algorithme reverse non disponible")
        
        logger.info(f"📊 {len(self.algorithms)} anciens algorithmes, {len(self.new_algorithms)} nouveaux algorithmes, {len(self.reverse_algorithms)} algorithmes entreprise")
    
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
        """Méthode matching candidat → jobs avec support des nouveaux algorithmes et analytics"""
        start_time = time.time()
        
        try:
            # Déterminer l'algorithme à utiliser
            if algorithm == "auto":
                if 'supersmartmatch' in self.new_algorithms:
                    algorithm = 'supersmartmatch'
                elif 'enhanced_class' in self.new_algorithms:
                    algorithm = 'enhanced_class'
                elif 'smart_match' in self.new_algorithms:
                    algorithm = 'smart_match'
                elif 'advanced' in self.algorithms:
                    algorithm = 'advanced'
                elif 'enhanced' in self.algorithms:
                    algorithm = 'enhanced'
                elif 'original' in self.algorithms:
                    algorithm = 'original'
                else:
                    algorithm = 'fallback'
            
            # Exécuter avec les nouveaux algorithmes (classes)
            if algorithm in self.new_algorithms:
                algo_instance = self.new_algorithms[algorithm]
                
                # Combiner cv_data et questionnaire_data pour les nouvelles classes
                combined_candidate = {**cv_data, **questionnaire_data}
                
                # Vérifier si l'algorithme supporte ces données
                if hasattr(algo_instance, 'supports') and not algo_instance.supports(combined_candidate, job_data):
                    # Fallback vers un autre algorithme
                    algorithm = 'fallback'
                    results = self.algorithms[algorithm](cv_data, questionnaire_data, job_data)
                else:
                    # Utiliser le nouvel algorithme
                    results = algo_instance.match_candidate_with_jobs(combined_candidate, job_data, limit)
                
                algorithm_type = "new_class"
            
            # Exécuter avec les anciens algorithmes (fonctions)
            elif algorithm in self.algorithms:
                results = self.algorithms[algorithm](cv_data, questionnaire_data, job_data)
                algorithm_type = "legacy_function"
            
            else:
                # Fallback
                algorithm = 'fallback'
                results = self.simple_matching(cv_data, questionnaire_data, job_data)
                algorithm_type = "fallback"
            
            # Limiter les résultats
            if limit > 0 and algorithm_type != "new_class":  # Les nouvelles classes gèrent déjà la limite
                results = results[:limit]
            
            # Analytics
            execution_time = time.time() - start_time
            if self.analytics:
                input_data = {
                    'cv_data': cv_data,
                    'questionnaire_data': questionnaire_data,
                    'job_data': job_data
                }
                self.analytics.log_matching_session(
                    "candidate_to_jobs", 
                    algorithm, 
                    input_data, 
                    results, 
                    execution_time
                )
            
            # ⚡ NOUVEAU v2.1: Ajouter infos pondération dynamique
            response_data = {
                'success': True,
                'matching_mode': 'candidate_to_jobs',
                'algorithm_used': algorithm,
                'algorithm_type': algorithm_type,
                'total_results': len(results),
                'execution_time': execution_time,
                'results': results
            }
            
            # Si SuperSmartMatch v2.1, ajouter les infos spécifiques
            if algorithm == 'supersmartmatch' and results:
                response_data['version'] = '2.1'
                response_data['dynamic_weighting_used'] = 'questionnaire_data' in (cv_data or questionnaire_data or {})
                response_data['features_v21'] = [
                    'dynamic_weighting',
                    'flexibility_scoring', 
                    'bidirectional_matching',
                    'intelligent_reasoning'
                ]
            
            return response_data
            
        except Exception as e:
            logger.error(f"Erreur matching candidat: {e}")
            results = self.simple_matching(cv_data, questionnaire_data, job_data)
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'matching_mode': 'candidate_to_jobs',
                'algorithm_used': 'fallback',
                'algorithm_type': 'fallback',
                'total_results': len(results),
                'execution_time': execution_time,
                'results': results[:limit] if limit > 0 else results,
                'fallback_used': True,
                'error': str(e)
            }
    
    def reverse_match(self, job_data, candidates_data, algorithm="auto", limit=10):
        """NOUVEAU : Méthode matching entreprise → candidats avec SuperSmartMatch et analytics"""
        start_time = time.time()
        
        try:
            # Déterminer l'algorithme à utiliser
            if algorithm == "auto":
                if 'supersmartmatch' in self.new_algorithms:
                    algorithm = 'supersmartmatch'
                elif 'reverse_advanced' in self.reverse_algorithms:
                    algorithm = 'reverse_advanced'
                else:
                    algorithm = 'reverse_fallback'
            
            # Utiliser SuperSmartMatch pour le matching côté entreprise
            if algorithm == 'supersmartmatch' and 'supersmartmatch' in self.new_algorithms:
                algo_instance = self.new_algorithms['supersmartmatch']
                
                # SuperSmartMatch traite candidat par candidat
                results = []
                for candidate in candidates_data:
                    # Combiner cv_data et questionnaire_data
                    combined_candidate = {}
                    if 'cv_data' in candidate:
                        combined_candidate.update(candidate['cv_data'])
                    if 'questionnaire_data' in candidate:
                        combined_candidate.update(candidate['questionnaire_data'])
                    
                    # Utiliser SuperSmartMatch avec un seul "job" mais traiter comme candidat
                    candidate_results = algo_instance.match_candidate_with_jobs(
                        combined_candidate, [job_data], 1
                    )
                    
                    if candidate_results:
                        # Transformer le résultat pour le candidat
                        result = candidate_results[0]
                        candidate_result = {
                            'candidate_id': candidate.get('candidate_id', 'unknown'),
                            'cv_data': candidate.get('cv_data', {}),
                            'questionnaire_data': candidate.get('questionnaire_data', {}),
                            'matching_score_entreprise': result.get('matching_score_entreprise', result.get('matching_score', 0)),
                            'scores_detailles': result.get('scores_detailles', {}),
                            'intelligence': result.get('intelligence', {}),
                            'explications_entreprise': result.get('explications_entreprise', {}),
                            'analyse_risques': result.get('analyse_risques', {}),
                            'profil_candidat': result.get('profil_candidat', {}),
                            # ⚡ NOUVEAU v2.1: Pondération dynamique
                            'ponderation_dynamique': result.get('ponderation_dynamique', {}),
                            **candidate  # Données originales du candidat
                        }
                        results.append(candidate_result)
                
                # Trier par score côté entreprise
                results.sort(key=lambda x: x.get('matching_score_entreprise', 0), reverse=True)
                
                # Limiter les résultats
                if limit > 0:
                    results = results[:limit]
                
                algorithm_type = "supersmartmatch"
            
            # Utiliser les anciens algorithmes
            elif algorithm in self.reverse_algorithms:
                if algorithm == 'reverse_advanced':
                    results = self.reverse_algorithms[algorithm](job_data, candidates_data, limit)
                else:
                    results = self.reverse_algorithms[algorithm](job_data, candidates_data)
                
                algorithm_type = "legacy_reverse"
                
                if limit > 0 and algorithm == 'reverse_fallback':
                    results = results[:limit]
            
            else:
                # Fallback
                algorithm = 'reverse_fallback'
                results = self.simple_reverse_matching(job_data, candidates_data)
                algorithm_type = "fallback"
                
                if limit > 0:
                    results = results[:limit]
            
            # Analytics
            execution_time = time.time() - start_time
            if self.analytics:
                input_data = {
                    'job_data': job_data,
                    'candidates_data': candidates_data
                }
                self.analytics.log_matching_session(
                    "company_to_candidates", 
                    algorithm, 
                    input_data, 
                    results, 
                    execution_time
                )
            
            # ⚡ NOUVEAU v2.1: Réponse enrichie
            response_data = {
                'success': True,
                'matching_mode': 'company_to_candidates',
                'algorithm_used': algorithm,
                'algorithm_type': algorithm_type,
                'job_analyzed': {
                    'id': job_data.get('id', 'unknown'),
                    'titre': job_data.get('titre', 'Poste sans titre'),
                    'entreprise': job_data.get('entreprise', 'Entreprise non spécifiée')
                },
                'total_results': len(results),
                'execution_time': execution_time,
                'results': results
            }
            
            # Si SuperSmartMatch v2.1, ajouter les infos spécifiques
            if algorithm == 'supersmartmatch':
                response_data['version'] = '2.1'
                response_data['features_v21'] = [
                    'dynamic_weighting_per_candidate',
                    'flexibility_scoring', 
                    'intelligent_company_perspective',
                    'detailed_risk_analysis'
                ]
            
            return response_data
            
        except Exception as e:
            logger.error(f"Erreur matching entreprise: {e}")
            results = self.simple_reverse_matching(job_data, candidates_data)
            execution_time = time.time() - start_time
            
            return {
                'success': True,
                'matching_mode': 'company_to_candidates',
                'algorithm_used': 'reverse_fallback',
                'algorithm_type': 'fallback',
                'total_results': len(results),
                'execution_time': execution_time,
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
        'version': '2.1 - Pondération Dynamique + Intelligence + Analytics',
        'description': 'Matching intelligent avec pondération dynamique basée sur priorités candidat',
        'port': 5063,
        'modes': {
            'candidate_to_jobs': 'Matching candidat vers emplois',
            'company_to_candidates': 'Matching entreprise vers candidats (avec SuperSmartMatch!)'
        },
        'algorithms': {
            'legacy_algorithms': list(service.algorithms.keys()),
            'new_class_algorithms': list(service.new_algorithms.keys()),
            'company_algorithms': list(service.reverse_algorithms.keys())
        },
        'analytics_enabled': service.analytics is not None,
        'supersmartmatch_v21_features': [
            '🎛️ Pondération dynamique basée sur 4 leviers candidat',
            '📈 Évolution → Influence Expérience + Compétences',
            '💰 Rémunération → Influence Rémunération',
            '📍 Proximité → Influence Proximité (ex-localisation)',
            '🔄 Flexibilité → Nouveau critère (télétravail, horaires, RTT)',
            '🎯 Questionnaire candidat avec notes 1-10',
            '🧠 Raisonnement intelligent (évolution, stabilité, innovation)',
            '⚠️ Analyse des risques et opportunités',
            '👤 Profil candidat pour recruteur',
            '📊 Analytics et suivi des performances'
        ]
    })

@app.route('/api/health')
def health():
    supersmartmatch_loaded = 'supersmartmatch' in service.new_algorithms
    
    return jsonify({
        'status': 'healthy',
        'port': 5063,
        'version': '2.1',
        'legacy_algorithms_loaded': len(service.algorithms),
        'new_algorithms_loaded': len(service.new_algorithms),
        'company_algorithms_loaded': len(service.reverse_algorithms),
        'supersmartmatch_available': supersmartmatch_loaded,
        'analytics_enabled': service.analytics is not None,
        'available_algorithms': {
            'legacy_candidate': list(service.algorithms.keys()),
            'new_candidate': list(service.new_algorithms.keys()),
            'company_matching': list(service.reverse_algorithms.keys()) + (['supersmartmatch'] if supersmartmatch_loaded else [])
        },
        'features_v21': [
            'Dynamic weighting based on candidate priorities',
            'Bidirectional matching (candidate ↔ company)',
            'SuperSmartMatch with company-side percentages',
            'Flexibility scoring (remote work, flexible hours, RTT)',
            'Intelligent reasoning (evolution, stability, innovation)',
            'Travel time calculation',
            'Risk and opportunity analysis',
            'Detailed scoring breakdown',
            'Performance analytics and monitoring',
            'Contract type matching (CDI/CDD/INTERIM)',
            'Salary optimization from company perspective',
            'Skills analysis (technical, languages, software)',
            'Candidate profiling for recruiters'
        ]
    })

@app.route('/api/algorithms')
def algorithms():
    # Algorithmes candidat (anciens)
    candidate_algorithms = {}
    for name in service.algorithms.keys():
        if name == 'advanced':
            candidate_algorithms[name] = {
                'type': 'legacy_function',
                'status': 'available',
                'features': ['travel_time', 'intelligent_weighting', 'explanations'],
                'description': 'Moteur avancé candidat vers jobs'
            }
        elif name == 'enhanced':
            candidate_algorithms[name] = {
                'type': 'legacy_function',
                'status': 'available', 
                'features': ['enhanced_scoring'],
                'description': 'Moteur amélioré candidat vers jobs'
            }
        elif name == 'original':
            candidate_algorithms[name] = {
                'type': 'legacy_function',
                'status': 'available',
                'features': ['basic_matching'],
                'description': 'Moteur de base candidat vers jobs'
            }
        else:
            candidate_algorithms[name] = {
                'type': 'legacy_function',
                'status': 'available',
                'features': ['fallback'],
                'description': 'Algorithme simple candidat vers jobs'
            }
    
    # Nouveaux algorithmes candidat (classes)
    new_candidate_algorithms = {}
    for name, instance in service.new_algorithms.items():
        if hasattr(instance, 'get_algorithm_info'):
            info = instance.get_algorithm_info()
            new_candidate_algorithms[name] = {
                'type': 'new_class',
                'status': 'available',
                'version': info.get('version', '1.0'),
                'capabilities': info.get('capabilities', {}),
                'description': info.get('description', f'Algorithme {name}'),
                'features': info.get('features', [])
            }
            
            # ⚡ NOUVEAU v2.1: Infos spécifiques SuperSmartMatch
            if name == 'supersmartmatch':
                new_candidate_algorithms[name]['dynamic_levers'] = info.get('dynamic_levers', {})
                new_candidate_algorithms[name]['questionnaire_structure'] = info.get('questionnaire_structure', {})
                new_candidate_algorithms[name]['new_features'] = info.get('new_features', {})
        else:
            new_candidate_algorithms[name] = {
                'type': 'new_class',
                'status': 'available',
                'description': f'Algorithme nouvelle génération {name}'
            }
    
    # Algorithmes entreprise
    company_algorithms = {}
    for name in service.reverse_algorithms.keys():
        if name == 'reverse_advanced':
            company_algorithms[name] = {
                'type': 'legacy_reverse',
                'status': 'available',
                'features': ['intelligent_company_weighting', 'career_goals_matching', 'adaptability_scoring'],
                'description': 'Moteur avancé entreprise vers candidats'
            }
        else:
            company_algorithms[name] = {
                'type': 'legacy_reverse',
                'status': 'available',
                'features': ['fallback'],
                'description': 'Algorithme simple entreprise vers candidats'
            }
    
    # Ajouter SuperSmartMatch pour entreprise
    if 'supersmartmatch' in service.new_algorithms:
        company_algorithms['supersmartmatch'] = {
            'type': 'supersmartmatch_v21',
            'status': 'available',
            'features': [
                'dynamic_weighting_per_candidate',
                'company_side_percentages',
                'intelligent_reasoning',
                'detailed_scoring',
                'flexibility_analysis',
                'risk_analysis',
                'location_travel_time',
                'salary_budget_compatibility',
                'skills_breakdown',
                'candidate_profiling',
                'performance_analytics'
            ],
            'description': '🚀 SuperSmartMatch v2.1 - Pondération dynamique intelligente côté entreprise'
        }
    
    return jsonify({
        'legacy_candidate_algorithms': candidate_algorithms,
        'new_candidate_algorithms': new_candidate_algorithms,
        'company_algorithms': company_algorithms,
        'total_count': len(service.algorithms) + len(service.new_algorithms) + len(service.reverse_algorithms),
        'analytics_enabled': service.analytics is not None,
        'recommended': {
            'candidate_to_jobs': 'supersmartmatch' if 'supersmartmatch' in service.new_algorithms else 'advanced',
            'company_to_candidates': 'supersmartmatch' if 'supersmartmatch' in service.new_algorithms else 'reverse_advanced'
        },
        'version': '2.1'
    })

# ⚡ NOUVEAUX ENDPOINTS v2.1 - PONDÉRATION DYNAMIQUE

@app.route('/api/candidate/<candidate_id>/questionnaire', methods=['POST', 'PUT'])
def update_candidate_questionnaire(candidate_id: str):
    """
    ⚡ NOUVEAU v2.1: Met à jour les priorités d'un candidat
    
    Body:
    {
        "priorites_candidat": {
            "evolution": 8,
            "remuneration": 6,
            "proximite": 4,
            "flexibilite": 9
        },
        "flexibilite_attendue": {
            "teletravail": "partiel",
            "horaires_flexibles": true,
            "rtt_important": true
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validation des priorités
        priorites = data.get('priorites_candidat', {})
        required_levers = ['evolution', 'remuneration', 'proximite', 'flexibilite']
        
        for lever in required_levers:
            if lever not in priorites:
                return jsonify({
                    'error': f'Levier manquant: {lever}',
                    'required_levers': required_levers
                }), 400
            
            note = priorites[lever]
            if not isinstance(note, (int, float)) or not (1 <= note <= 10):
                return jsonify({
                    'error': f'Note invalide pour {lever}: {note} (doit être entre 1 et 10)'
                }), 400
        
        # Validation flexibilité attendue
        flex_attendue = data.get('flexibilite_attendue', {})
        if 'teletravail' in flex_attendue:
            valid_teletravail = ['aucun', 'partiel', 'total']
            if flex_attendue['teletravail'] not in valid_teletravail:
                return jsonify({
                    'error': f'Valeur télétravail invalide: {flex_attendue["teletravail"]}',
                    'valid_values': valid_teletravail
                }), 400
        
        # Prévisualiser la pondération
        if 'supersmartmatch' in service.new_algorithms:
            algorithm = service.new_algorithms['supersmartmatch']
            fake_candidate = {'questionnaire_data': data}
            weights_preview = algorithm.calculate_dynamic_weights(fake_candidate)
            
            # Calculer les variations vs base
            base_weights = algorithm.config['ponderation_base']
            variations = {}
            for critere in weights_preview:
                variation = ((weights_preview[critere] / base_weights[critere]) - 1) * 100
                variations[critere] = round(variation, 1)
            
            preview = {
                'ponderation_adaptee': {k: round(v*100, 1) for k, v in weights_preview.items()},
                'variations_vs_base': variations,
                'levier_dominant': max(priorites, key=priorites.get),
                'note_dominante': max(priorites.values())
            }
        else:
            preview = {'error': 'SuperSmartMatch v2.1 non disponible'}
        
        # Sauvegarder les données questionnaire (ici simulation)
        questionnaire_data = {
            'priorites_candidat': priorites,
            'flexibilite_attendue': flex_attendue,
            'date_maj': time.strftime('%Y-%m-%d'),
            'version': '2.1'
        }
        
        return jsonify({
            'success': True,
            'message': 'Questionnaire mis à jour avec succès',
            'candidate_id': candidate_id,
            'questionnaire_data': questionnaire_data,
            'ponderation_preview': preview
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur questionnaire candidat: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/weighting-impact', methods=['POST'])
def analyze_weighting_impact():
    """
    ⚡ NOUVEAU v2.1: Compare l'impact pondération fixe vs dynamique
    
    Body:
    {
        "candidat": {...},
        "offres": [...],
        "compare_scenarios": true
    }
    """
    try:
        data = request.get_json()
        candidat = data.get('candidat', {})
        offres = data.get('offres', [])
        
        if 'supersmartmatch' not in service.new_algorithms:
            return jsonify({'error': 'SuperSmartMatch v2.1 non disponible'}), 503
        
        algorithm = service.new_algorithms['supersmartmatch']
        
        # Scénario 1: Avec pondération dynamique
        results_dynamic = algorithm.match_candidate_with_jobs(candidat, offres, limit=5)
        
        # Scénario 2: Sans questionnaire (pondération fixe)
        candidat_sans_questionnaire = {k: v for k, v in candidat.items() if k != 'questionnaire_data'}
        results_fixed = algorithm.match_candidate_with_jobs(candidat_sans_questionnaire, offres, limit=5)
        
        # Analyse comparative
        comparison = []
        for i in range(min(len(results_dynamic), len(results_fixed))):
            job_id = results_dynamic[i]['id']
            dynamic_score = results_dynamic[i]['matching_score_entreprise']
            
            # Trouver le même job dans les résultats fixes
            fixed_score = None
            fixed_rank = None
            for j, fixed_result in enumerate(results_fixed):
                if fixed_result['id'] == job_id:
                    fixed_score = fixed_result['matching_score_entreprise']
                    fixed_rank = j + 1
                    break
            
            if fixed_score is not None:
                comparison.append({
                    'job_id': job_id,
                    'job_title': results_dynamic[i]['titre'],
                    'dynamic_score': dynamic_score,
                    'dynamic_rank': i + 1,
                    'fixed_score': fixed_score,
                    'fixed_rank': fixed_rank,
                    'score_difference': dynamic_score - fixed_score,
                    'rank_difference': fixed_rank - (i + 1)
                })
        
        # Statistiques globales
        score_differences = [comp['score_difference'] for comp in comparison]
        rank_differences = [comp['rank_difference'] for comp in comparison]
        
        # Générer des recommandations
        recommendations = []
        if not candidat.get('questionnaire_data'):
            recommendations.append("Faire remplir le questionnaire de priorités pour personnaliser le matching")
        else:
            avg_score_diff = sum(score_differences) / len(score_differences) if score_differences else 0
            if avg_score_diff > 5:
                recommendations.append(f"La pondération dynamique améliore significativement les scores (+{avg_score_diff:.1f}% en moyenne)")
            elif avg_score_diff < -5:
                recommendations.append("La pondération fixe pourrait être plus adaptée pour ce profil")
            else:
                recommendations.append("Impact modéré de la pondération dynamique")
        
        analytics = {
            'has_questionnaire': 'questionnaire_data' in candidat,
            'dynamic_weights': results_dynamic[0]['ponderation_dynamique'] if results_dynamic else None,
            'fixed_weights': algorithm.config['ponderation_base'],
            'comparison': comparison,
            'impact_statistics': {
                'avg_score_difference': sum(score_differences) / len(score_differences) if score_differences else 0,
                'max_score_difference': max(score_differences) if score_differences else 0,
                'min_score_difference': min(score_differences) if score_differences else 0,
                'avg_rank_change': sum(rank_differences) / len(rank_differences) if rank_differences else 0,
                'jobs_improved_ranking': len([r for r in rank_differences if r > 0]),
                'jobs_degraded_ranking': len([r for r in rank_differences if r < 0])
            },
            'recommendations': recommendations
        }
        
        return jsonify({
            'success': True,
            'version': '2.1',
            'analytics': analytics
        }), 200
        
    except Exception as e:
        logger.error(f"Erreur analytics impact: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/demo/candidate-profiles', methods=['GET'])
def get_demo_profiles():
    """
    ⚡ NOUVEAU v2.1: Profils candidat types pour la démo
    """
    profiles = {
        'salaire_prioritaire': {
            'nom': 'Marie Dubois - Salaire Prioritaire',
            'description': 'Candidate expérimentée qui privilégie la rémunération',
            'questionnaire': {
                'priorites_candidat': {'evolution': 4, 'remuneration': 9, 'proximite': 6, 'flexibilite': 5},
                'flexibilite_attendue': {'teletravail': 'partiel', 'horaires_flexibles': False, 'rtt_important': False}
            }
        },
        'evolution_prioritaire': {
            'nom': 'Thomas Martin - Évolution Prioritaire', 
            'description': 'Jeune candidat ambitieux qui veut progresser rapidement',
            'questionnaire': {
                'priorites_candidat': {'evolution': 10, 'remuneration': 3, 'proximite': 5, 'flexibilite': 6},
                'flexibilite_attendue': {'teletravail': 'ouvert', 'horaires_flexibles': True, 'rtt_important': False}
            }
        },
        'flexibilite_prioritaire': {
            'nom': 'Sophie Chen - Flexibilité Prioritaire',
            'description': 'Candidate qui privilégie work-life balance et autonomie',
            'questionnaire': {
                'priorites_candidat': {'evolution': 5, 'remuneration': 4, 'proximite': 3, 'flexibilite': 10},
                'flexibilite_attendue': {'teletravail': 'total', 'horaires_flexibles': True, 'rtt_important': True}
            }
        },
        'proximite_prioritaire': {
            'nom': 'Jean Rousseau - Proximité Prioritaire',
            'description': 'Candidat senior avec contraintes géographiques familiales',
            'questionnaire': {
                'priorites_candidat': {'evolution': 6, 'remuneration': 7, 'proximite': 10, 'flexibilite': 4},
                'flexibilite_attendue': {'teletravail': 'aucun', 'horaires_flexibles': False, 'rtt_important': False}
            }
        }
    }
    
    return jsonify({
        'version': '2.1',
        'profiles': profiles,
        'usage': 'Utilisez ces profils pour tester l\'impact de la pondération dynamique',
        'features': [
            'Pondération adaptée selon priorités candidat',
            'Notes 1-10 pour chaque levier',
            'Impact visualisable sur classement offres',
            'Comparaison pondération fixe vs dynamique'
        ]
    })

@app.route('/api/supersmartmatch/info', methods=['GET'])
def get_supersmartmatch_info():
    """
    ⚡ NOUVEAU v2.1: Informations détaillées sur SuperSmartMatch
    """
    if 'supersmartmatch' not in service.new_algorithms:
        return jsonify({'error': 'SuperSmartMatch v2.1 non disponible'}), 503
    
    algorithm = service.new_algorithms['supersmartmatch']
    info = algorithm.get_algorithm_info()
    
    return jsonify({
        'version': '2.1',
        'algorithm_info': info,
        'api_endpoints': {
            'questionnaire': '/api/candidate/<id>/questionnaire',
            'analytics': '/api/analytics/weighting-impact',
            'demo_profiles': '/api/demo/candidate-profiles',
            'matching': '/api/match',
            'company_matching': '/api/match-candidates'
        },
        'integration_guide': 'Voir PONDERATION_DYNAMIQUE_GUIDE.md pour la documentation complète'
    })

# ENDPOINTS EXISTANTS (conservés)

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Endpoint pour récupérer les statistiques d'utilisation"""
    if not service.analytics:
        return jsonify({'error': 'Analytics non disponible'}), 503
    
    days = request.args.get('days', 7, type=int)
    
    try:
        stats = service.analytics.get_statistics(days)
        return jsonify({
            'success': True,
            'analytics': stats,
            'generated_at': time.time()
        })
    except Exception as e:
        logger.error(f"Erreur analytics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """Résumé rapide des analytics"""
    if not service.analytics:
        return jsonify({'error': 'Analytics non disponible'}), 503
    
    try:
        # Statistiques des 24 dernières heures
        last_24h = service.analytics.get_statistics(1)
        # Statistiques des 7 derniers jours
        last_7d = service.analytics.get_statistics(7)
        
        summary = {
            'last_24h': {
                'sessions': last_24h.get('total_sessions', 0),
                'avg_score': last_24h.get('performance_trends', {}).get('avg_matching_score', 0),
                'intelligence_usage': last_24h.get('intelligence_effectiveness', {}).get('intelligence_usage_rate', 0)
            },
            'last_7d': {
                'sessions': last_7d.get('total_sessions', 0),
                'avg_score': last_7d.get('performance_trends', {}).get('avg_matching_score', 0),
                'top_algorithm': max(last_7d.get('algorithms_usage', {}).items(), key=lambda x: x[1])[0] if last_7d.get('algorithms_usage') else 'unknown'
            },
            'supersmartmatch_performance': {
                'available': 'supersmartmatch' in service.new_algorithms,
                'recommended_usage': '100% pour matching côté entreprise avec pondération dynamique v2.1'
            }
        }
        
        return jsonify({
            'success': True,
            'version': '2.1',
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Erreur analytics summary: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/match', methods=['POST'])
def match():
    """Endpoint existant : matching candidat → jobs avec analytics et support v2.1"""
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
    """NOUVEAU : Endpoint matching entreprise → candidats avec SuperSmartMatch et analytics"""
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
    """Données de test pour les deux modes avec exemples SuperSmartMatch v2.1"""
    return jsonify({
        'version': '2.1',
        'candidate_to_jobs_example': {
            'cv_data': {
                'competences': ['Python', 'Django', 'PostgreSQL', 'React', 'AWS'],
                'annees_experience': 5,
                'niveau_etudes': 'Master',
                'derniere_fonction': 'Développeur Full Stack',
                'secteur_activite': 'FinTech',
                'soft_skills': ['leadership', 'communication', 'autonomie'],
                'langues': ['Français', 'Anglais'],
                'logiciels': ['Git', 'Docker', 'Jenkins']
            },
            'questionnaire_data': {
                'adresse': 'Paris 15ème',
                'salaire_souhaite': 55000,
                'types_contrat': ['CDI'],
                'mobilite': 'moyenne',
                'criteres_importants': {
                    'evolution_rapide': True,
                    'culture_importante': True
                },
                'objectifs_carriere': {
                    'evolution_rapide': True,
                    'ambitions': ['technique', 'management']
                },
                'valeurs_importantes': ['innovation', 'teamwork'],
                
                # ⚡ NOUVEAU v2.1: Priorités candidat
                'priorites_candidat': {
                    'evolution': 8,        # Priorité élevée évolution
                    'remuneration': 6,     # Moyenne
                    'proximite': 4,        # Faible (pas de contrainte géo)
                    'flexibilite': 9       # Très important
                },
                'flexibilite_attendue': {
                    'teletravail': 'partiel',
                    'horaires_flexibles': True,
                    'rtt_important': True
                }
            },
            'job_data': [
                {
                    'id': 'job-001',
                    'titre': 'Développeur Python Senior',
                    'entreprise': 'TechCorp',
                    'competences': ['Python', 'Django', 'PostgreSQL'],
                    'localisation': 'Paris 8ème',
                    'type_contrat': 'CDI',
                    'salaire': '50-65K€',
                    'budget_max': 65000,
                    'experience_requise': 3,
                    'perspectives_evolution': True,
                    'culture_entreprise': {
                        'valeurs': ['innovation', 'collaboration']
                    },
                    'politique_remote': 'télétravail partiel',
                    'horaires_flexibles': True,
                    'jours_rtt': 15
                }
            ]
        },
        'company_to_candidates_supersmartmatch_v21_example': {
            'job_data': {
                'id': 'startup-lead-001',
                'titre': 'Lead Developer',
                'entreprise': 'TechStartup',
                'competences': ['Python', 'Django', 'React', 'AWS'],
                'localisation': 'Paris 2ème',
                'type_contrat': 'CDI',
                'budget_max': 80000,
                'salaire': '65-80K€',
                'experience_requise': 5,
                'perspectives_evolution': True,
                'niveau_poste': 'senior',
                'type_entreprise': 'startup',
                'culture_entreprise': {
                    'valeurs': ['innovation', 'agilité', 'autonomie']
                },
                'responsabilites': 'management équipe',
                'langues_requises': ['Français', 'Anglais'],
                'logiciels_requis': ['Git', 'AWS', 'Docker'],
                'politique_remote': 'télétravail possible',
                'horaires_flexibles': True,
                'jours_rtt': 12,
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
                        'derniere_fonction': 'Senior Developer',
                        'soft_skills': ['leadership', 'innovation'],
                        'langues': ['Français', 'Anglais', 'Espagnol'],
                        'logiciels': ['Git', 'Docker', 'AWS', 'Jenkins']
                    },
                    'questionnaire_data': {
                        'adresse': 'Paris 11ème',
                        'salaire_souhaite': 70000,
                        'contrats_recherches': ['CDI'],
                        'mobilite': 'élevée',
                        'criteres_importants': {
                            'evolution_rapide': True,
                            'responsabilites_importantes': True
                        },
                        'objectifs_carriere': {
                            'evolution_rapide': True,
                            'ambitions': ['management', 'technique']
                        },
                        'valeurs_importantes': ['innovation', 'autonomie'],
                        'disponibilite': 'immédiate',
                        
                        # ⚡ NOUVEAU v2.1: Priorités candidat
                        'priorites_candidat': {
                            'evolution': 10,       # Priorité maximale évolution
                            'remuneration': 7,     # Importante
                            'proximite': 5,        # Moyenne
                            'flexibilite': 6       # Importante
                        },
                        'flexibilite_attendue': {
                            'teletravail': 'partiel',
                            'horaires_flexibles': True,
                            'rtt_important': False
                        }
                    }
                },
                {
                    'candidate_id': 'cand-002', 
                    'cv_data': {
                        'nom': 'Jean Martin',
                        'competences': ['JavaScript', 'React', 'Node.js'],
                        'annees_experience': 3,
                        'niveau_etudes': 'Bachelor',
                        'soft_skills': ['communication', 'adaptabilité'],
                        'langues': ['Français'],
                        'logiciels': ['Git', 'VS Code']
                    },
                    'questionnaire_data': {
                        'adresse': 'Boulogne-Billancourt',
                        'salaire_souhaite': 50000,
                        'contrats_recherches': ['CDI', 'CDD'],
                        'mobilite': 'moyenne',
                        'criteres_importants': {
                            'stabilite': True,
                            'salaire_important': False
                        },
                        'objectifs_carriere': {
                            'evolution_rapide': False
                        },
                        'valeurs_importantes': ['stabilité', 'teamwork'],
                        
                        # ⚡ NOUVEAU v2.1: Priorités candidat
                        'priorites_candidat': {
                            'evolution': 3,        # Faible priorité évolution
                            'remuneration': 9,     # Priorité élevée salaire
                            'proximite': 8,        # Très important proximité
                            'flexibilite': 4       # Faible priorité flexibilité
                        },
                        'flexibilite_attendue': {
                            'teletravail': 'aucun',
                            'horaires_flexibles': False,
                            'rtt_important': False
                        }
                    }
                }
            ]
        }
    })

if __name__ == '__main__':
    port = 5063  # Port sécurisé - Évite les conflits
    logger.info(f"🚀 Démarrage SuperSmartMatch v2.1 avec PONDÉRATION DYNAMIQUE sur le port {port}")
    logger.info("🎛️ Nouveauté v2.1: Pondération adaptée selon priorités candidat")
    logger.info("📈 4 leviers: Évolution, Rémunération, Proximité, Flexibilité")
    logger.info("🔄 Nouveau critère flexibilité: télétravail, horaires, RTT")
    logger.info("🧠 Raisonnement intelligent + Analytics + Matching bidirectionnel")
    logger.info(f"🔗 URL: http://localhost:{port}")
    logger.info("📋 Nouveaux endpoints v2.1:")
    logger.info("   POST /api/candidate/<id>/questionnaire - Priorités candidat")
    logger.info("   POST /api/analytics/weighting-impact - Comparaison impact")
    logger.info("   GET  /api/demo/candidate-profiles - Profils démo")
    logger.info("   GET  /api/supersmartmatch/info - Infos algorithme v2.1")
    app.run(host='0.0.0.0', port=port, debug=False)
