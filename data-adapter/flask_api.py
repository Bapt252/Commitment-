"""
SmartMatch API - Middleware d'adaptation pour le matching de CV et offres d'emploi
--------------------------------------------------------------------------------
Ce module expose des endpoints Flask pour convertir et adapter les données
entre les parsers (CV et Job) et l'algorithme de matching SmartMatch.

Auteur: Claude
Date: 16/05/2025
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify, Blueprint

# Importer l'adaptateur
from smartmatch_data_adapter import SmartMatchDataAdapter

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer l'adaptateur
adapter = SmartMatchDataAdapter()

# Créer un blueprint Flask pour les routes d'adaptation de données
data_adapter_bp = Blueprint('data_adapter', __name__)

@data_adapter_bp.route('/health', methods=['GET'])
def health_check():
    """Point de contrôle pour vérifier la disponibilité du service"""
    return jsonify({"status": "ok", "message": "SmartMatch Data Adapter is running"}), 200

@data_adapter_bp.route('/adapt-cv', methods=['POST'])
def adapt_cv():
    """
    Endpoint pour adapter les données d'un CV au format SmartMatch
    
    Accepte les données au format JSON ou fichier
    Retourne les données adaptées au format SmartMatch
    """
    try:
        cv_id = request.args.get('id', None)
        
        # Récupérer les données du CV
        if 'file' in request.files:
            # Depuis un fichier
            cv_file = request.files['file']
            cv_data = json.loads(cv_file.read().decode('utf-8'))
        elif request.json:
            # Depuis JSON
            cv_data = request.json
        else:
            return jsonify({"error": "No CV data provided"}), 400
        
        # Adapter les données
        smartmatch_data = adapter.cv_to_smartmatch_format(cv_data, cv_id)
        
        return jsonify(smartmatch_data), 200
    
    except Exception as e:
        logger.error(f"Error in adapt-cv: {str(e)}")
        return jsonify({"error": str(e)}), 500

@data_adapter_bp.route('/adapt-job', methods=['POST'])
def adapt_job():
    """
    Endpoint pour adapter les données d'une offre d'emploi au format SmartMatch
    
    Accepte les données au format JSON ou fichier
    Retourne les données adaptées au format SmartMatch
    """
    try:
        job_id = request.args.get('id', None)
        
        # Récupérer les données de l'offre d'emploi
        if 'file' in request.files:
            # Depuis un fichier
            job_file = request.files['file']
            job_data = json.loads(job_file.read().decode('utf-8'))
        elif request.json:
            # Depuis JSON
            job_data = request.json
        else:
            return jsonify({"error": "No job data provided"}), 400
        
        # Adapter les données
        smartmatch_data = adapter.job_to_smartmatch_format(job_data, job_id)
        
        return jsonify(smartmatch_data), 200
    
    except Exception as e:
        logger.error(f"Error in adapt-job: {str(e)}")
        return jsonify({"error": str(e)}), 500

@data_adapter_bp.route('/batch-adapt-cv', methods=['POST'])
def batch_adapt_cv():
    """
    Endpoint pour adapter un lot de données CV au format SmartMatch
    
    Accepte un tableau JSON de CVs
    Retourne les données adaptées au format SmartMatch
    """
    try:
        # Récupérer les données des CVs
        if not request.json or not isinstance(request.json, list):
            return jsonify({"error": "Expected JSON array of CV data"}), 400
        
        cv_data_list = request.json
        
        # Adapter les données
        smartmatch_data_list = adapter.batch_convert(cv_data_list, 'cv')
        
        return jsonify(smartmatch_data_list), 200
    
    except Exception as e:
        logger.error(f"Error in batch-adapt-cv: {str(e)}")
        return jsonify({"error": str(e)}), 500

@data_adapter_bp.route('/batch-adapt-job', methods=['POST'])
def batch_adapt_job():
    """
    Endpoint pour adapter un lot de données d'offres d'emploi au format SmartMatch
    
    Accepte un tableau JSON d'offres d'emploi
    Retourne les données adaptées au format SmartMatch
    """
    try:
        # Récupérer les données des offres d'emploi
        if not request.json or not isinstance(request.json, list):
            return jsonify({"error": "Expected JSON array of job data"}), 400
        
        job_data_list = request.json
        
        # Adapter les données
        smartmatch_data_list = adapter.batch_convert(job_data_list, 'job')
        
        return jsonify(smartmatch_data_list), 200
    
    except Exception as e:
        logger.error(f"Error in batch-adapt-job: {str(e)}")
        return jsonify({"error": str(e)}), 500

@data_adapter_bp.route('/match', methods=['POST'])
def match():
    """
    Endpoint pour adapter les données puis effectuer un matching
    
    Accepte un CV et une offre d'emploi au format JSON
    Retourne le résultat du matching
    """
    try:
        # Récupérer les données
        if not request.json or 'cv' not in request.json or 'job' not in request.json:
            return jsonify({"error": "Both 'cv' and 'job' data are required"}), 400
        
        cv_data = request.json['cv']
        job_data = request.json['job']
        
        # Adapter les données
        cv_smartmatch = adapter.cv_to_smartmatch_format(cv_data)
        job_smartmatch = adapter.job_to_smartmatch_format(job_data)
        
        # Ici, vous appelleriez l'algorithme de matching
        # Dans cette démo, nous simulons un résultat de matching
        match_result = simulate_match_result(cv_smartmatch, job_smartmatch)
        
        return jsonify(match_result), 200
    
    except Exception as e:
        logger.error(f"Error in match: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Nouveaux endpoints pour l'enrichissement avec les questionnaires

@data_adapter_bp.route('/enrich-cv-with-questionnaire', methods=['POST'])
def enrich_cv_with_questionnaire():
    """
    Endpoint pour enrichir les données CV avec les réponses du questionnaire candidat
    
    Accepte les données CV et les réponses au questionnaire au format JSON
    Retourne les données CV enrichies
    """
    try:
        # Récupérer les données
        if not request.json:
            return jsonify({"error": "JSON data required"}), 400
        
        cv_data = request.json.get('cv_data', {})
        questionnaire_data = request.json.get('questionnaire_data', {})
        cv_id = request.json.get('cv_id')
        
        if not cv_data:
            return jsonify({"error": "CV data is required"}), 400
        
        # Enrichir les données CV avec les réponses au questionnaire
        enriched_cv = adapter.enrich_cv_data_with_questionnaire(cv_data, questionnaire_data, cv_id)
        
        return jsonify(enriched_cv), 200
    
    except Exception as e:
        logger.error(f"Error in enrich-cv-with-questionnaire: {str(e)}")
        return jsonify({"error": str(e)}), 500

@data_adapter_bp.route('/enrich-job-with-questionnaire', methods=['POST'])
def enrich_job_with_questionnaire():
    """
    Endpoint pour enrichir les données d'offre d'emploi avec les réponses du questionnaire client
    
    Accepte les données d'offre d'emploi et les réponses au questionnaire au format JSON
    Retourne les données d'offre d'emploi enrichies
    """
    try:
        # Récupérer les données
        if not request.json:
            return jsonify({"error": "JSON data required"}), 400
        
        job_data = request.json.get('job_data', {})
        questionnaire_data = request.json.get('questionnaire_data', {})
        job_id = request.json.get('job_id')
        
        if not job_data:
            return jsonify({"error": "Job data is required"}), 400
        
        # Enrichir les données d'offre d'emploi avec les réponses au questionnaire
        enriched_job = adapter.enrich_job_data_with_questionnaire(job_data, questionnaire_data, job_id)
        
        return jsonify(enriched_job), 200
    
    except Exception as e:
        logger.error(f"Error in enrich-job-with-questionnaire: {str(e)}")
        return jsonify({"error": str(e)}), 500

@data_adapter_bp.route('/smart-match', methods=['POST'])
def smart_match():
    """
    Endpoint pour effectuer un matching avancé tenant compte des données de questionnaires
    
    Accepte les données CV et offre d'emploi enrichies au format JSON
    Retourne le résultat du matching avancé
    """
    try:
        # Récupérer les données
        if not request.json:
            return jsonify({"error": "JSON data required"}), 400
        
        cv_data = request.json.get('cv', {})
        job_data = request.json.get('job', {})
        
        if not cv_data or not job_data:
            return jsonify({"error": "Both 'cv' and 'job' data are required"}), 400
        
        # Vérifier si des données de questionnaires sont incluses
        cv_questionnaire = request.json.get('cv_questionnaire', {})
        job_questionnaire = request.json.get('job_questionnaire', {})
        
        # Enrichir les données si des questionnaires sont fournis
        if cv_questionnaire:
            cv_data = adapter.enrich_cv_data_with_questionnaire(cv_data, cv_questionnaire)
            
        if job_questionnaire:
            job_data = adapter.enrich_job_data_with_questionnaire(job_data, job_questionnaire)
        
        # Effectuer le matching avancé
        match_result = adapter.enhanced_match(cv_data, job_data)
        
        return jsonify(match_result), 200
    
    except Exception as e:
        logger.error(f"Error in smart-match: {str(e)}")
        return jsonify({"error": str(e)}), 500

def simulate_match_result(cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simule un résultat de matching (à remplacer par l'appel réel à SmartMatcher)
    
    Args:
        cv_data (Dict): Données CV au format SmartMatch
        job_data (Dict): Données d'offre d'emploi au format SmartMatch
        
    Returns:
        Dict: Résultat de matching simulé
    """
    # Simuler un score global
    overall_score = 0.75
    
    # Simuler des scores par catégorie
    category_scores = {
        "skills": 0.85,
        "location": 0.70,
        "experience": 0.80,
        "education": 0.90,
        "preferences": 0.60
    }
    
    # Simuler des insights
    insights = [
        {
            "type": "skill_match",
            "message": "Excellente correspondance des compétences techniques",
            "score": 0.85,
            "category": "strength"
        },
        {
            "type": "location_match",
            "message": "Temps de trajet optimal",
            "score": 0.70,
            "category": "strength"
        }
    ]
    
    # Construire le résultat
    return {
        "candidate_id": cv_data.get("id", ""),
        "job_id": job_data.get("id", ""),
        "candidate_name": cv_data.get("name", ""),
        "job_title": job_data.get("title", ""),
        "company": job_data.get("company", ""),
        "overall_score": overall_score,
        "category_scores": category_scores,
        "insights": insights
    }

def create_app() -> Flask:
    """
    Crée et configure l'application Flask
    
    Returns:
        Flask: Application Flask configurée
    """
    app = Flask(__name__)
    
    # Enregistrer le blueprint
    app.register_blueprint(data_adapter_bp, url_prefix='/api/adapter')
    
    return app

# Point d'entrée pour exécution directe
if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5053))
    app.run(host="0.0.0.0", port=port, debug=True)
