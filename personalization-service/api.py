#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API Flask du service de personnalisation pour le projet Commitment

Ce service permet de personnaliser les résultats de matching en fonction
des préférences des utilisateurs et de leur comportement passé.
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import redis
import psycopg2
import json

# Import des modules du service de personnalisation
from models.preference_model import PreferenceModel
from models.collaborative_filter import CollaborativeFilter
from models.cold_start import ColdStartHandler
from models.temporal_drift import TemporalDriftHandler
from utils.data_loader import DataLoader
from utils.ab_testing import ABTestManager

# Chargement des variables d'environnement
load_dotenv()

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration de la base de données
db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@postgres:5432/nexten')

# Configuration de Redis
redis_host = os.getenv('REDIS_HOST', 'redis')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_db = int(os.getenv('REDIS_DB', 0))

# Configuration du service de matching
matching_service_url = os.getenv('MATCHING_SERVICE_URL', 'http://matching-api:5000')

# Configuration du service de personnalisation
AB_TESTING_ENABLED = os.getenv('AB_TESTING_ENABLED', 'false').lower() == 'true'
COLLABORATIVE_FILTER_ENABLED = os.getenv('COLLABORATIVE_FILTER_ENABLED', 'true').lower() == 'true'
TEMPORAL_DRIFT_ENABLED = os.getenv('TEMPORAL_DRIFT_ENABLED', 'true').lower() == 'true'

# Initialisation des composants
redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
data_loader = DataLoader(db_url, redis_client)
preference_model = PreferenceModel(data_loader)
collab_filter = CollaborativeFilter(data_loader)
cold_start_handler = ColdStartHandler(data_loader)
temporal_drift_handler = TemporalDriftHandler(data_loader)
ab_test_manager = ABTestManager(redis_client)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de vérification de santé du service
    """
    return jsonify({
        'status': 'healthy',
        'service': 'personalization-service',
        'version': '1.0.0'
    })

@app.route('/', methods=['GET'])
def root():
    """
    Endpoint racine du service
    """
    return jsonify({
        'service': 'Commitment Personalization Service',
        'description': 'Service de personnalisation pour le matching de CV et offres d\'emploi',
        'version': '1.0.0',
        'endpoints': [
            '/health',
            '/api/v1/personalize/job-search',
            '/api/v1/personalize/matching',
            '/api/v1/preferences',
            '/api/v1/preferences/<user_id>',
            '/api/v1/feedback'
        ]
    })

@app.route('/api/v1/personalize/job-search', methods=['POST'])
def personalize_job_search():
    """
    Personnalise les résultats de recherche d'offres d'emploi pour un utilisateur
    
    Body:
    {
        "user_id": "123",
        "results": [
            {"job_id": 1, "score": 0.8, ...},
            {"job_id": 2, "score": 0.7, ...}
        ],
        "search_query": "développeur python",
        "context": {"location": "Paris", "filters": {"remote": true}}
    }
    """
    data = request.json
    user_id = data.get('user_id')
    results = data.get('results', [])
    search_query = data.get('search_query', '')
    context = data.get('context', {})
    
    if not user_id or not results:
        return jsonify({'error': 'user_id et results sont requis'}), 400
    
    try:
        # Vérifier si l'utilisateur est nouveau (cold start)
        is_new_user = cold_start_handler.is_new_user(user_id)
        
        # Si AB testing est activé, assigner l'utilisateur à un groupe
        if AB_TESTING_ENABLED:
            group = ab_test_manager.get_user_group(user_id)
            if group == 'control':
                # Groupe de contrôle: pas de personnalisation
                logger.info(f"AB Testing - Utilisateur {user_id} dans le groupe de contrôle, pas de personnalisation")
                return jsonify({'results': results, 'personalized': False, 'group': 'control'})
        
        # Obtenir les préférences utilisateur
        if is_new_user:
            # Stratégie de démarrage à froid pour les nouveaux utilisateurs
            user_preferences = cold_start_handler.get_initial_preferences(user_id, search_query, context)
            logger.info(f"Nouvel utilisateur {user_id} - Application de la stratégie cold start")
        else:
            # Préférences personnalisées pour les utilisateurs existants
            user_preferences = preference_model.get_user_preferences(user_id)
            
            # Appliquer la correction de dérive temporelle si activée
            if TEMPORAL_DRIFT_ENABLED:
                user_preferences = temporal_drift_handler.adjust_preferences(
                    user_id, user_preferences, search_query, context
                )
                logger.info(f"Ajustement temporel appliqué pour l'utilisateur {user_id}")
        
        # Personnaliser les résultats avec les préférences
        personalized_results = preference_model.apply_preferences(results, user_preferences)
        
        # Appliquer le filtrage collaboratif si activé
        if COLLABORATIVE_FILTER_ENABLED and not is_new_user:
            personalized_results = collab_filter.enhance_results(
                user_id, personalized_results, search_query, context
            )
            logger.info(f"Filtrage collaboratif appliqué pour l'utilisateur {user_id}")
        
        # Enregistrer cette interaction pour apprentissage futur
        data_loader.save_interaction(user_id, 'search_jobs', {
            'query': search_query,
            'context': context,
            'results_count': len(results)
        })
        
        return jsonify({
            'results': personalized_results,
            'personalized': True,
            'is_new_user': is_new_user
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la personnalisation: {str(e)}", exc_info=True)
        # En cas d'erreur, retourner les résultats originaux
        return jsonify({'results': results, 'personalized': False, 'error': str(e)})

@app.route('/api/v1/personalize/matching', methods=['POST'])
def personalize_matching():
    """
    Personnalise les poids de matching pour un utilisateur spécifique
    
    Body:
    {
        "user_id": "123",
        "job_id": 456,
        "candidate_id": 789,
        "original_weights": {
            "skills": 0.4,
            "experience": 0.3,
            "education": 0.2,
            "certifications": 0.1
        }
    }
    """
    data = request.json
    user_id = data.get('user_id')
    job_id = data.get('job_id')
    candidate_id = data.get('candidate_id')
    original_weights = data.get('original_weights', {})
    
    if not user_id:
        return jsonify({'error': 'user_id est requis'}), 400
    
    try:
        # Vérifier si l'utilisateur est nouveau (cold start)
        is_new_user = cold_start_handler.is_new_user(user_id)
        
        # Si AB testing est activé, assigner l'utilisateur à un groupe
        if AB_TESTING_ENABLED:
            group = ab_test_manager.get_user_group(user_id)
            if group == 'control':
                # Groupe de contrôle: pas de personnalisation
                logger.info(f"AB Testing - Utilisateur {user_id} dans le groupe de contrôle, pas de personnalisation")
                return jsonify({
                    'weights': original_weights, 
                    'personalized': False, 
                    'group': 'control'
                })
        
        # Obtenir les poids personnalisés
        if is_new_user:
            # Stratégie de démarrage à froid pour les nouveaux utilisateurs
            custom_weights = cold_start_handler.get_initial_weights(user_id, job_id, candidate_id)
            logger.info(f"Nouvel utilisateur {user_id} - Application de la stratégie cold start pour les poids")
        else:
            # Préférences personnalisées pour les utilisateurs existants
            custom_weights = preference_model.get_custom_weights(user_id, job_id, candidate_id)
            
            # Appliquer la correction de dérive temporelle si activée
            if TEMPORAL_DRIFT_ENABLED:
                custom_weights = temporal_drift_handler.adjust_weights(
                    user_id, custom_weights, job_id, candidate_id
                )
                logger.info(f"Ajustement temporel appliqué pour l'utilisateur {user_id}")
        
        # Fusionner les poids originaux avec les poids personnalisés
        final_weights = {**original_weights, **custom_weights}
        
        # Normaliser les poids (somme = 1)
        weight_sum = sum(final_weights.values())
        if weight_sum > 0:
            final_weights = {k: v/weight_sum for k, v in final_weights.items()}
        
        # Enregistrer cette interaction pour apprentissage futur
        data_loader.save_interaction(user_id, 'personalize_weights', {
            'job_id': job_id,
            'candidate_id': candidate_id,
            'original_weights': original_weights,
            'custom_weights': custom_weights,
            'final_weights': final_weights
        })
        
        return jsonify({
            'weights': final_weights,
            'personalized': True,
            'is_new_user': is_new_user
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de la personnalisation des poids: {str(e)}", exc_info=True)
        # En cas d'erreur, retourner les poids originaux
        return jsonify({'weights': original_weights, 'personalized': False, 'error': str(e)})

@app.route('/api/v1/preferences', methods=['POST'])
def save_preferences():
    """
    Sauvegarde les préférences d'un utilisateur
    
    Body:
    {
        "user_id": "123",
        "preferences": {
            "job_type": ["CDI", "Freelance"],
            "location": ["Paris", "Remote"],
            "skills": ["Python", "JavaScript"],
            "company_size": ["Startup", "PME"],
            "weights": {
                "skills": 0.5,
                "experience": 0.3,
                "education": 0.2
            }
        }
    }
    """
    data = request.json
    user_id = data.get('user_id')
    preferences = data.get('preferences', {})
    
    if not user_id:
        return jsonify({'error': 'user_id est requis'}), 400
    
    try:
        # Sauvegarder les préférences
        success = preference_model.save_user_preferences(user_id, preferences)
        
        # Enregistrer cette interaction
        data_loader.save_interaction(user_id, 'update_preferences', {
            'preferences': preferences
        })
        
        if success:
            return jsonify({'status': 'success', 'message': 'Préférences sauvegardées'})
        else:
            return jsonify({'status': 'error', 'message': 'Erreur lors de la sauvegarde des préférences'}), 500
    
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des préférences: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/v1/preferences/<user_id>', methods=['GET'])
def get_preferences(user_id):
    """
    Récupère les préférences d'un utilisateur
    """
    if not user_id:
        return jsonify({'error': 'user_id est requis'}), 400
    
    try:
        # Récupérer les préférences
        preferences = preference_model.get_user_preferences(user_id)
        
        # Enregistrer cette interaction
        data_loader.save_interaction(user_id, 'get_preferences', {})
        
        return jsonify({
            'user_id': user_id,
            'preferences': preferences
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des préférences: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/v1/feedback', methods=['POST'])
def record_feedback():
    """
    Enregistre le feedback utilisateur pour améliorer les recommandations
    
    Body:
    {
        "user_id": "123",
        "job_id": 456,
        "candidate_id": 789,
        "action": "like",  # like, dislike, bookmark, apply, ignore
        "context": {"source": "search_results", "position": 3}
    }
    """
    data = request.json
    user_id = data.get('user_id')
    job_id = data.get('job_id')
    candidate_id = data.get('candidate_id')
    action = data.get('action')
    context = data.get('context', {})
    
    if not user_id or not action or (not job_id and not candidate_id):
        return jsonify({'error': 'user_id, action et (job_id ou candidate_id) sont requis'}), 400
    
    try:
        # Enregistrer le feedback
        feedback_data = {
            'user_id': user_id,
            'job_id': job_id,
            'candidate_id': candidate_id,
            'action': action,
            'context': context
        }
        
        # Sauvegarder le feedback
        success = data_loader.save_feedback(feedback_data)
        
        # Mettre à jour le modèle de préférences avec ce feedback
        if success:
            preference_model.update_with_feedback(user_id, feedback_data)
            
            # Si c'est un feedback positif fort et que le filtrage collaboratif est activé
            if action in ['like', 'bookmark', 'apply'] and COLLABORATIVE_FILTER_ENABLED:
                # Mettre à jour le modèle collaboratif
                collab_filter.update_model(user_id, job_id, candidate_id, action)
        
        return jsonify({'status': 'success', 'message': 'Feedback enregistré'})
    
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du feedback: {str(e)}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Point d'entrée principal
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5060))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"Démarrage du service de personnalisation sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
