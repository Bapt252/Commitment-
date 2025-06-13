#!/usr/bin/env python3
"""
🚀 SuperSmartMatch V2.1 Enhanced - API CORRIGÉE
API corrigée pour retourner les scores de matching dans le bon format
Problème résolu : matching_score, confidence, recommendation maintenant présents
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
import json
import logging
import time
from datetime import datetime
import os
import tempfile
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuration
CV_PARSER_URL = "http://localhost:5051"
JOB_PARSER_URL = "http://localhost:5053"
UPLOAD_FOLDER = tempfile.gettempdir()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gestion des erreurs
class MatchingAPIError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

@app.errorhandler(MatchingAPIError)
def handle_matching_error(error):
    response = jsonify({
        'error': error.message,
        'status': 'error',
        'timestamp': datetime.now().isoformat()
    })
    response.status_code = error.status_code
    return response

# Fonctions de calcul de scoring (reprises de l'interface)
def calculate_mission_score(cv_data, job_data):
    """Calcul du score des missions (40%)"""
    try:
        cv_missions = cv_data.get('professional_experience', [{}])[0].get('missions', [])
        job_missions = job_data.get('missions', [])
        
        # Extraction des catégories
        cv_categories = []
        for mission in cv_missions:
            if isinstance(mission, dict) and 'category' in mission:
                cv_categories.append(mission['category'])
            elif isinstance(mission, str):
                # Fallback pour missions textuelles simples
                cv_categories.append('general')
        
        job_categories = []
        for mission in job_missions:
            if isinstance(mission, dict) and 'category' in mission:
                job_categories.append(mission['category'])
            elif isinstance(mission, str):
                job_categories.append('general')
        
        # Calcul des correspondances
        cv_categories = [cat for cat in cv_categories if cat]
        job_categories = [cat for cat in job_categories if cat]
        
        if not job_categories:
            return {
                'score': 50,
                'cv_missions': cv_missions,
                'job_missions': job_missions,
                'matched_categories': [],
                'coverage_rate': 0,
                'explanation': 'Aucune catégorie de mission identifiée dans l\'offre'
            }
        
        matches = [cat for cat in cv_categories if cat in job_categories]
        coverage = (len(matches) / len(job_categories)) * 100
        
        return {
            'score': min(coverage, 100),
            'cv_missions': cv_missions,
            'job_missions': job_missions,
            'matched_categories': matches,
            'coverage_rate': coverage,
            'explanation': f'{len(matches)} catégories de missions correspondent sur {len(job_categories)} requises ({round(coverage)}% de couverture)'
        }
    except Exception as e:
        logger.error(f"Erreur calcul mission score: {e}")
        return {
            'score': 0,
            'cv_missions': [],
            'job_missions': [],
            'matched_categories': [],
            'coverage_rate': 0,
            'explanation': f'Erreur lors du calcul: {str(e)}'
        }

def calculate_skills_score(cv_data, job_data):
    """Calcul du score des compétences (30%)"""
    try:
        cv_skills = []
        cv_skills.extend(cv_data.get('technical_skills', []))
        cv_skills.extend(cv_data.get('soft_skills', []))
        
        job_skills = []
        job_requirements = job_data.get('requirements', {})
        job_skills.extend(job_requirements.get('technical_skills', []))
        job_skills.extend(job_requirements.get('soft_skills', []))
        
        if not job_skills:
            return {
                'score': 50,
                'cv_skills': cv_skills,
                'job_skills': job_skills,
                'exact_matches': [],
                'partial_matches': [],
                'explanation': 'Aucune compétence spécifiée dans l\'offre'
            }
        
        # Normalisation pour comparaison
        cv_skills_lower = [skill.lower() for skill in cv_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Correspondances exactes
        exact_matches = [skill for skill in job_skills_lower if skill in cv_skills_lower]
        
        # Correspondances partielles
        partial_matches = []
        for job_skill in job_skills_lower:
            if job_skill not in exact_matches:
                for cv_skill in cv_skills_lower:
                    if job_skill in cv_skill or cv_skill in job_skill:
                        partial_matches.append(job_skill)
                        break
        
        # Calcul du score
        score = ((len(exact_matches) * 1.0 + len(partial_matches) * 0.5) / len(job_skills)) * 100
        
        return {
            'score': min(score, 100),
            'cv_skills': cv_skills,
            'job_skills': job_skills,
            'exact_matches': exact_matches,
            'partial_matches': partial_matches,
            'explanation': f'{len(exact_matches)} compétences parfaitement alignées et {len(partial_matches)} partiellement compatibles'
        }
    except Exception as e:
        logger.error(f"Erreur calcul skills score: {e}")
        return {
            'score': 0,
            'cv_skills': [],
            'job_skills': [],
            'exact_matches': [],
            'partial_matches': [],
            'explanation': f'Erreur lors du calcul: {str(e)}'
        }

def calculate_experience_score(cv_data, job_data):
    """Calcul du score d'expérience (15%)"""
    try:
        cv_experience = cv_data.get('experience_years', 0)
        required_experience = job_data.get('requirements', {}).get('experience_level', '0-2 ans')
        
        # Extraction de la fourchette d'expérience
        import re
        matches = re.findall(r'(\d+)', required_experience)
        if len(matches) >= 2:
            min_exp, max_exp = int(matches[0]), int(matches[1])
        elif len(matches) == 1:
            min_exp, max_exp = int(matches[0]), int(matches[0]) + 2
        else:
            min_exp, max_exp = 0, 2
        
        # Calcul du score
        if min_exp <= cv_experience <= max_exp + 2:
            score = 100  # Expérience parfaitement alignée
        elif cv_experience >= min_exp:
            score = 85   # Surqualifié mais acceptable
        else:
            score = max(30, (cv_experience / min_exp) * 70) if min_exp > 0 else 30
        
        return {
            'score': score,
            'cv_experience': cv_experience,
            'required_experience': required_experience,
            'explanation': f'{cv_experience} ans d\'expérience vs {required_experience} requis'
        }
    except Exception as e:
        logger.error(f"Erreur calcul experience score: {e}")
        return {
            'score': 50,
            'cv_experience': 0,
            'required_experience': 'Non spécifié',
            'explanation': f'Erreur lors du calcul: {str(e)}'
        }

def calculate_quality_score(cv_data, job_data):
    """Calcul du score de qualité (15%)"""
    try:
        score = 0
        factors = []
        
        # Vérification de la complétude du CV
        if cv_data.get('candidate_name'):
            score += 20
            factors.append('Nom du candidat')
        
        if cv_data.get('professional_experience') and len(cv_data['professional_experience']) > 0:
            score += 25
            factors.append('Expérience professionnelle')
        
        if cv_data.get('technical_skills') and len(cv_data['technical_skills']) > 0:
            score += 20
            factors.append('Compétences techniques')
        
        mission_summary = cv_data.get('mission_summary', {})
        if mission_summary.get('confidence_avg', 0) > 0.8:
            score += 20
            factors.append('Missions bien détaillées')
        
        if cv_data.get('professional_experience', [{}])[0].get('missions') and \
           len(cv_data['professional_experience'][0]['missions']) >= 3:
            score += 15
            factors.append('Missions détaillées')
        
        return {
            'score': min(score, 100),
            'quality_factors': factors,
            'explanation': f'Qualité évaluée sur {len(factors)} critères de complétude'
        }
    except Exception as e:
        logger.error(f"Erreur calcul quality score: {e}")
        return {
            'score': 50,
            'quality_factors': [],
            'explanation': f'Erreur lors du calcul: {str(e)}'
        }

def calculate_advanced_score(cv_data, job_data):
    """Calcul du score global avec détails complets"""
    # Calcul des composants
    mission_analysis = calculate_mission_score(cv_data, job_data)
    skills_analysis = calculate_skills_score(cv_data, job_data)
    experience_analysis = calculate_experience_score(cv_data, job_data)
    quality_analysis = calculate_quality_score(cv_data, job_data)
    
    # Score final pondéré
    total_score = round(
        (mission_analysis['score'] * 0.40) +
        (skills_analysis['score'] * 0.30) +
        (experience_analysis['score'] * 0.15) +
        (quality_analysis['score'] * 0.15)
    )
    
    # Génération de la recommandation
    if total_score >= 85:
        recommendation = "Candidat fortement recommandé"
        confidence = "high"
    elif total_score >= 70:
        recommendation = "Candidat recommandé avec réserves"
        confidence = "high"
    elif total_score >= 50:
        recommendation = "Candidat à considérer selon contexte"
        confidence = "medium"
    else:
        recommendation = "Candidat non recommandé pour ce poste"
        confidence = "low"
    
    return {
        'total_score': total_score,
        'recommendation': recommendation,
        'confidence': confidence,
        'mission_analysis': mission_analysis,
        'skills_analysis': skills_analysis,
        'experience_analysis': experience_analysis,
        'quality_analysis': quality_analysis,
        'detailed_breakdown': {
            'missions': {
                'score': round(mission_analysis['score'] * 0.40),
                'weight': 40,
                'details': mission_analysis
            },
            'skills': {
                'score': round(skills_analysis['score'] * 0.30),
                'weight': 30,
                'details': skills_analysis
            },
            'experience': {
                'score': round(experience_analysis['score'] * 0.15),
                'weight': 15,
                'details': experience_analysis
            },
            'quality': {
                'score': round(quality_analysis['score'] * 0.15),
                'weight': 15,
                'details': quality_analysis
            }
        }
    }

# Routes API
@app.route('/health', methods=['GET'])
def health_check():
    """Health check de l'API"""
    return jsonify({
        'service': 'SuperSmartMatch V2.1 Enhanced FIXED',
        'status': 'healthy',
        'version': '2.1',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'matching_complete': '/api/matching/complete',
            'calculate_matching': '/api/calculate-matching',  # ⭐ NOUVEAU ENDPOINT
            'matching_files': '/api/matching/files',
            'matching_enhanced': '/api/matching/enhanced',   # ⭐ ALIAS ENDPOINT
            'parse_cv': '/api/parse/cv',
            'parse_job': '/api/parse/job'
        },
        'fix_info': {
            'issue': 'Missing matching_score, confidence, recommendation in response',
            'solution': 'Added proper response format and missing endpoints',
            'compatibility': 'Backward compatible with existing tests'
        }
    })

@app.route('/api/matching/complete', methods=['POST'])
def matching_complete():
    """
    Endpoint pour matching complet avec données JSON (format original)
    """
    try:
        data = request.json
        if not data or 'cv_data' not in data or 'job_data' not in data:
            raise MatchingAPIError('cv_data et job_data requis dans le body JSON')
        
        cv_data = data['cv_data']
        job_data = data['job_data']
        
        # Calcul du matching
        start_time = time.time()
        matching_result = calculate_advanced_score(cv_data, job_data)
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'processing_time_ms': processing_time,
            'matching_analysis': matching_result,
            'api_version': '2.1',
            'algorithm': 'SuperSmartMatch V2.1 Enhanced'
        })
        
    except MatchingAPIError:
        raise
    except Exception as e:
        logger.error(f"Erreur matching complet: {e}")
        raise MatchingAPIError(f'Erreur lors du calcul de matching: {str(e)}', 500)

@app.route('/api/calculate-matching', methods=['POST'])
@app.route('/api/matching/enhanced', methods=['POST'])
def calculate_matching():
    """
    🚀 ENDPOINT CORRIGÉ pour les tests massifs
    Retourne matching_score, confidence, recommendation au niveau racine
    """
    try:
        data = request.json
        if not data or 'cv_data' not in data or 'job_data' not in data:
            raise MatchingAPIError('cv_data et job_data requis dans le body JSON')
        
        cv_data = data['cv_data']
        job_data = data['job_data']
        
        # Calcul du matching
        start_time = time.time()
        matching_result = calculate_advanced_score(cv_data, job_data)
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        # ⭐ FORMAT CORRIGÉ : scores au niveau racine pour les tests
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'processing_time_ms': processing_time,
            'api_version': '2.1',
            'algorithm': 'SuperSmartMatch V2.1 Enhanced',
            
            # ⭐ CHAMPS ATTENDUS PAR LES TESTS
            'matching_score': matching_result['total_score'],
            'confidence': matching_result['confidence'],
            'recommendation': matching_result['recommendation'],
            
            # Détails complets
            'details': matching_result,
            'matching_analysis': matching_result  # Garde compatibilité
        })
        
    except MatchingAPIError:
        raise
    except Exception as e:
        logger.error(f"Erreur calcul matching: {e}")
        raise MatchingAPIError(f'Erreur lors du calcul de matching: {str(e)}', 500)

@app.route('/api/matching/files', methods=['POST'])
def matching_files():
    """
    Endpoint pour matching avec upload de fichiers PDF
    """
    try:
        if 'cv_file' not in request.files or 'job_file' not in request.files:
            raise MatchingAPIError('cv_file et job_file requis')
        
        cv_file = request.files['cv_file']
        job_file = request.files['job_file']
        
        if cv_file.filename == '' or job_file.filename == '':
            raise MatchingAPIError('Fichiers vides non autorisés')
        
        # Sauvegarde temporaire des fichiers
        cv_filename = secure_filename(cv_file.filename)
        job_filename = secure_filename(job_file.filename)
        
        cv_path = os.path.join(UPLOAD_FOLDER, f"cv_{int(time.time())}_{cv_filename}")
        job_path = os.path.join(UPLOAD_FOLDER, f"job_{int(time.time())}_{job_filename}")
        
        cv_file.save(cv_path)
        job_file.save(job_path)
        
        try:
            # Parsing du CV
            with open(cv_path, 'rb') as f:
                cv_response = requests.post(
                    f"{CV_PARSER_URL}/api/parse-cv/",
                    files={'file': f},
                    data={'force_refresh': 'false'},
                    timeout=30
                )
            
            if not cv_response.ok:
                raise MatchingAPIError(f'Erreur parsing CV: {cv_response.status_code}')
            
            cv_data = cv_response.json()
            
            # Parsing du Job
            with open(job_path, 'rb') as f:
                job_response = requests.post(
                    f"{JOB_PARSER_URL}/api/parse-job",
                    files={'file': f},
                    data={'force_refresh': 'false'},
                    timeout=30
                )
            
            if not job_response.ok:
                raise MatchingAPIError(f'Erreur parsing Job: {job_response.status_code}')
            
            job_data = job_response.json()
            
            # Calcul du matching
            start_time = time.time()
            matching_result = calculate_advanced_score(cv_data, job_data)
            processing_time = round((time.time() - start_time) * 1000, 2)
            
            return jsonify({
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'processing_time_ms': processing_time,
                'files_processed': {
                    'cv_file': cv_filename,
                    'job_file': job_filename
                },
                'cv_data': cv_data,
                'job_data': job_data,
                
                # ⭐ FORMAT CORRIGÉ pour compatibilité
                'matching_score': matching_result['total_score'],
                'confidence': matching_result['confidence'],
                'recommendation': matching_result['recommendation'],
                'details': matching_result,
                'matching_analysis': matching_result,
                'api_version': '2.1'
            })
            
        finally:
            # Nettoyage des fichiers temporaires
            try:
                os.remove(cv_path)
                os.remove(job_path)
            except:
                pass
        
    except MatchingAPIError:
        raise
    except Exception as e:
        logger.error(f"Erreur matching fichiers: {e}")
        raise MatchingAPIError(f'Erreur lors du traitement des fichiers: {str(e)}', 500)

@app.route('/api/parse/cv', methods=['POST'])
def parse_cv_proxy():
    """Proxy vers le CV Parser V2"""
    try:
        if 'file' not in request.files:
            raise MatchingAPIError('Fichier CV requis')
        
        file = request.files['file']
        response = requests.post(
            f"{CV_PARSER_URL}/api/parse-cv/",
            files={'file': file},
            data=request.form,
            timeout=30
        )
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Erreur proxy CV: {e}")
        raise MatchingAPIError(f'Erreur proxy CV Parser: {str(e)}', 500)

@app.route('/api/parse/job', methods=['POST'])
def parse_job_proxy():
    """Proxy vers le Job Parser V2"""
    try:
        if 'file' not in request.files:
            raise MatchingAPIError('Fichier Job requis')
        
        file = request.files['file']
        response = requests.post(
            f"{JOB_PARSER_URL}/api/parse-job",
            files={'file': file},
            data=request.form,
            timeout=30
        )
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Erreur proxy Job: {e}")
        raise MatchingAPIError(f'Erreur proxy Job Parser: {str(e)}', 500)

@app.route('/api/export/report', methods=['POST'])
def export_report():
    """Export de rapport de matching en JSON"""
    try:
        data = request.json
        if not data or 'matching_analysis' not in data:
            raise MatchingAPIError('matching_analysis requis dans le body JSON')
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'candidate': data.get('candidate', 'Candidat Anonyme'),
            'job_title': data.get('job_title', 'Poste Non Spécifié'),
            'matching_analysis': data['matching_analysis'],
            'version': 'SuperSmartMatch V2.1 Enhanced FIXED',
            'api_version': '2.1'
        }
        
        # Création du fichier temporaire
        report_filename = f"SuperSmartMatch_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(UPLOAD_FOLDER, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return send_file(
            report_path,
            as_attachment=True,
            download_name=report_filename,
            mimetype='application/json'
        )
        
    except MatchingAPIError:
        raise
    except Exception as e:
        logger.error(f"Erreur export rapport: {e}")
        raise MatchingAPIError(f'Erreur lors de l\'export: {str(e)}', 500)

if __name__ == '__main__':
    print("🚀 SuperSmartMatch V2.1 Enhanced - API CORRIGÉE")
    print("=" * 50)
    print("✅ CORRECTIONS APPLIQUÉES:")
    print("   🔧 Endpoint /api/calculate-matching ajouté")
    print("   🔧 Endpoint /api/matching/enhanced ajouté (alias)")
    print("   🔧 Champs matching_score, confidence, recommendation au niveau racine")
    print("   🔧 Rétrocompatibilité avec les tests existants")
    print("")
    print("📡 Endpoints disponibles:")
    print("   GET  /health                      - Health check")
    print("   POST /api/matching/complete       - Matching avec données JSON")
    print("   POST /api/calculate-matching      - 🆕 CORRIGÉ pour tests massifs")
    print("   POST /api/matching/enhanced       - 🆕 Alias pour tests")
    print("   POST /api/matching/files          - Matching avec upload fichiers")
    print("   POST /api/parse/cv                - Proxy CV Parser")
    print("   POST /api/parse/job               - Proxy Job Parser")
    print("   POST /api/export/report           - Export rapport JSON")
    print("")
    print("🌐 Serveur démarré sur: http://localhost:5055")
    print("🎯 Prêt pour les 213 tests massifs !")
    
    app.run(host='0.0.0.0', port=5055, debug=True)
