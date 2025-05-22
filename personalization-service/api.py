#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API Flask pour le service de personnalisation du matching

Ce service fournit des API pour personnaliser les résultats de matching
en fonction des préférences utilisateur et du comportement passé.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import datetime
import redis
import json

# Import des modèles et utilitaires
from models.collaborative_filter import CollaborativeFilter
from models.preference_model import PreferenceModel
from models.cold_start import ColdStartHandler
from models.temporal_drift import TemporalDriftDetector
from utils.ab_testing import ABTestManager
from utils.data_loader import DataLoader
import config

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialisation des composants
redis_client = redis.Redis(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    db=config.REDIS_DB,
    password=config.REDIS_PASSWORD
)

data_loader = DataLoader(redis_client)
preference_model = PreferenceModel(data_loader)
collaborative_filter = CollaborativeFilter(data_loader)
cold_start_handler = ColdStartHandler(data_loader)
temporal_drift_detector = TemporalDriftDetector()
ab_test_manager = ABTestManager(redis_client)

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de vérification de la santé du service
    """
    return jsonify({
        'status': 'ok',
        'version': config.VERSION,
        'service': 'personalization-service',
        'timestamp': datetime.datetime.now().isoformat()
    })

@app.route('/api/v1/personalize/matching', methods=['POST'])
def personalize_matching():
    """
    Personnalise les poids pour le matching en fonction de l'utilisateur
    
    Body:
    {
        "user_id": "string",       # ID de l'utilisateur
        "job_id": number,          # ID de l'offre (optionnel)
        "candidate_id": number,    # ID du candidat (optionnel)
        "original_weights": {      # Poids originaux
            "skills": 0.4,
            "experience": 0.3,
            "education": 0.2,
            "certifications": 0.1
        }
    }
    
    Returns:
        Poids personnalisés
    """
    data = request.json
    user_id = data.get('user_id')
    job_id = data.get('job_id')
    candidate_id = data.get('candidate_id')
    original_weights = data.get('original_weights', {})
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    # Décider quelle méthode utiliser pour la personnalisation (test A/B)
    test_group = ab_test_manager.get_user_test_group(user_id, 'weight_personalization')
    
    try:
        # Vérifier si l'utilisateur est nouveau
        is_new_user = cold_start_handler.is_new_user(user_id)
        
        if is_new_user:
            # Traitement utilisateur nouveau (cold start)
            personalized_weights = cold_start_handler.get_default_weights(
                user_id, job_id, candidate_id, original_weights
            )
        else:
            # Vérifier la dérive temporelle (si préférences obsolètes)
            if temporal_drift_detector.has_drifted(user_id):
                logger.info(f"Dérive temporelle détectée pour l'utilisateur {user_id}")
                temporal_drift_detector.reset_user_model(user_id)
            
            # Obtenir les poids personnalisés selon le groupe de test
            if test_group == 'control':
                personalized_weights = original_weights
            elif test_group == 'preference_model':
                personalized_weights = preference_model.get_personalized_weights(
                    user_id, job_id, candidate_id, original_weights
                )
            elif test_group == 'collaborative':
                personalized_weights = collaborative_filter.get_similar_users_weights(
                    user_id, job_id, candidate_id, original_weights
                )
            else:
                # Groupe par défaut: modèle de préférence
                personalized_weights = preference_model.get_personalized_weights(
                    user_id, job_id, candidate_id, original_weights
                )
        
        return jsonify({
            'status': 'success',
            'weights': personalized_weights,
            'test_group': test_group,
            'is_new_user': is_new_user
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de la personnalisation des poids: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e),
            'weights': original_weights
        }), 500

@app.route('/api/v1/personalize/job-search', methods=['POST'])
def personalize_job_search():
    """
    Personnalise l'ordre des résultats de recherche pour un utilisateur
    
    Body:
    {
        "user_id": "string",       # ID de l'utilisateur
        "results": [],             # Liste des résultats à réordonner
        "search_query": "string",  # Requête de recherche (optionnel)
        "context": {}              # Contexte de la recherche (optionnel)
    }
    
    Returns:
        Résultats personnalisés
    """
    data = request.json
    user_id = data.get('user_id')
    results = data.get('results', [])
    search_query = data.get('search_query', '')
    context = data.get('context', {})
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    if not results:
        return jsonify({'results': []})
    
    # Décider quelle méthode utiliser pour la personnalisation (test A/B)
    test_group = ab_test_manager.get_user_test_group(user_id, 'results_personalization')
    
    try:
        # Vérifier si l'utilisateur est nouveau
        is_new_user = cold_start_handler.is_new_user(user_id)
        
        if is_new_user:
            # Simple diversification pour les nouveaux utilisateurs
            personalized_results = cold_start_handler.diversify_results(results)
        else:
            # Vérifier la dérive temporelle
            if temporal_drift_detector.has_drifted(user_id):
                logger.info(f"Dérive temporelle détectée pour l'utilisateur {user_id}")
                temporal_drift_detector.reset_user_model(user_id)
            
            # Obtenir les résultats personnalisés selon le groupe de test
            if test_group == 'control':
                personalized_results = results
            elif test_group == 'preference_model':
                personalized_results = preference_model.rerank_results(
                    user_id, results, search_query, context
                )
            elif test_group == 'collaborative':
                personalized_results = collaborative_filter.rerank_results(
                    user_id, results, search_query, context
                )
            else:
                # Groupe par défaut: modèle de préférence
                personalized_results = preference_model.rerank_results(
                    user_id, results, search_query, context
                )
        
        return jsonify({
            'status': 'success',
            'results': personalized_results,
            'test_group': test_group,
            'is_new_user': is_new_user
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de la personnalisation des résultats: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e),
            'results': results
        }), 500

@app.route('/api/v1/preferences/<user_id>', methods=['GET'])
def get_user_preferences(user_id):
    """
    Récupère les préférences d'un utilisateur
    
    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        Préférences de l'utilisateur
    """
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        preferences = preference_model.get_user_preferences(user_id)
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'preferences': preferences
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des préférences: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/v1/preferences', methods=['POST'])
def save_user_preferences():
    """
    Sauvegarde les préférences d'un utilisateur
    
    Body:
    {
        "user_id": "string",       # ID de l'utilisateur
        "preferences": {}          # Préférences à sauvegarder
    }
    
    Returns:
        Statut de l'opération
    """
    data = request.json
    user_id = data.get('user_id')
    preferences = data.get('preferences', {})
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        success = preference_model.save_user_preferences(user_id, preferences)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Préférences sauvegardées avec succès'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Échec lors de la sauvegarde des préférences'
            }), 500
    
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde des préférences: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/v1/feedback', methods=['POST'])
def record_feedback():
    """
    Enregistre un feedback utilisateur
    
    Body:
    {
        "user_id": "string",       # ID de l'utilisateur
        "job_id": number,          # ID de l'offre (optionnel)
        "candidate_id": number,    # ID du candidat (optionnel)
        "action": "string",        # Type d'action (like, dislike, bookmark, apply, etc.)
        "context": {}              # Contexte du feedback (source, position, etc.)
    }
    
    Returns:
        Statut de l'opération
    """
    data = request.json
    user_id = data.get('user_id')
    job_id = data.get('job_id')
    candidate_id = data.get('candidate_id')
    action = data.get('action', '')
    context = data.get('context', {})
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    if not action:
        return jsonify({'error': 'action is required'}), 400
    
    if not job_id and not candidate_id:
        return jsonify({'error': 'Either job_id or candidate_id is required'}), 400
    
    try:
        # Enregistrer le feedback
        timestamp = datetime.datetime.now().isoformat()
        
        feedback_data = {
            'user_id': user_id,
            'job_id': job_id,
            'candidate_id': candidate_id,
            'action': action,
            'context': context,
            'timestamp': timestamp
        }
        
        # Persistance du feedback
        data_loader.save_feedback(feedback_data)
        
        # Mise à jour du modèle de préférence
        preference_model.update_from_feedback(feedback_data)
        
        # Mettre à jour le modèle collaboratif
        collaborative_filter.update_from_feedback(feedback_data)
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback enregistré avec succès'
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du feedback: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/v1/stats/user/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """
    Récupère les statistiques pour un utilisateur
    
    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        Statistiques de l'utilisateur
    """
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    try:
        # Obtenir le nombre de feedbacks
        feedback_count = data_loader.get_user_feedback_count(user_id)
        
        # Obtenir la segmentation de l'utilisateur
        user_segment = preference_model.get_user_segment(user_id)
        
        # Obtenir les poids personnalisés courants
        current_weights = preference_model.get_personalized_weights(
            user_id, None, None, 
            {
                'skills': 0.4,
                'experience': 0.3,
                'education': 0.2,
                'certifications': 0.1
            }
        )
        
        # Obtenir les utilisateurs similaires
        similar_users = collaborative_filter.get_similar_users(user_id, limit=5)
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'feedback_count': feedback_count,
            'segment': user_segment,
            'current_weights': current_weights,
            'similar_users': similar_users
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/v1/ab-tests', methods=['GET'])
def get_ab_tests():
    """
    Récupère la liste des tests A/B actifs
    
    Returns:
        Liste des tests A/B
    """
    try:
        tests = ab_test_manager.get_active_tests()
        return jsonify({
            'status': 'success',
            'tests': tests
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tests A/B: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/v1/ab-tests/results', methods=['GET'])
def get_ab_test_results():
    """
    Récupère les résultats des tests A/B
    
    Returns:
        Résultats des tests A/B
    """
    try:
        results = ab_test_manager.get_test_results()
        return jsonify({
            'status': 'success',
            'results': results
        })
    
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des résultats de tests A/B: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5060)))
