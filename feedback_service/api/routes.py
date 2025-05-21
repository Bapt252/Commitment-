from flask import Blueprint, jsonify, request
from datetime import datetime
import logging
import json
import uuid
from feedback_service.models.feedback import (
    FeedbackSource, FeedbackType, FeedbackAnalyzer, 
    FeedbackCollector, SatisfactionPredictor
)
from feedback_service.db.repository import FeedbackRepository

logger = logging.getLogger(__name__)
feedback_api = Blueprint('feedback_api', __name__)

# Initialiser les services
feedback_repository = FeedbackRepository()
feedback_collector = FeedbackCollector(feedback_repository)
feedback_analyzer = FeedbackAnalyzer(feedback_repository)
satisfaction_predictor = SatisfactionPredictor()

@feedback_api.route('/feedback', methods=['POST'])
def collect_feedback():
    """Collecte du feedback explicite depuis différentes sources."""
    data = request.json
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Le contenu du feedback est requis'}), 400
    
    # Collecter les données nécessaires
    feedback_data = {
        'id': str(uuid.uuid4()),
        'user_id': data.get('user_id'),
        'content': data.get('content'),
        'source': data.get('source', FeedbackSource.WEB_APP.value),
        'type': data.get('type', FeedbackType.EXPLICIT.value),
        'rating': data.get('rating'),
        'category': data.get('category'),
        'context': data.get('context', {}),
        'created_at': datetime.now().isoformat()
    }
    
    # Sauvegarder le feedback
    feedback_id = feedback_collector.collect(feedback_data)
    
    # Analyser le feedback pour des insights immédiats
    sentiment = feedback_analyzer.analyze_sentiment(feedback_data['content'])
    topics = feedback_analyzer.extract_topics(feedback_data['content'])
    
    # Enrichir le feedback avec les résultats d'analyse
    feedback_repository.update(feedback_id, {
        'sentiment': sentiment,
        'topics': topics
    })
    
    # Prédire la satisfaction utilisateur
    if data.get('user_id'):
        satisfaction_score = satisfaction_predictor.predict({
            'user_id': data['user_id'],
            'feedback': feedback_data,
            'sentiment': sentiment
        })
        
        # Enregistrer la prédiction
        feedback_repository.update(feedback_id, {
            'satisfaction_score': satisfaction_score
        })
    
    return jsonify({
        'id': feedback_id,
        'status': 'success',
        'sentiment': sentiment,
        'topics': topics,
        'satisfaction_score': satisfaction_score if data.get('user_id') else None
    }), 201

@feedback_api.route('/feedback/implicit', methods=['POST'])
def collect_implicit_feedback():
    """Collecte du feedback implicite depuis les interactions utilisateur."""
    data = request.json
    
    if not data or 'interactions' not in data:
        return jsonify({'error': 'Les interactions sont requises'}), 400
    
    user_id = data.get('user_id')
    interactions = data.get('interactions', [])
    
    if not user_id:
        return jsonify({'error': 'L\'ID utilisateur est requis'}), 400
    
    # Transformer les interactions en feedback implicite
    feedback_items = []
    
    for interaction in interactions:
        feedback_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'content': json.dumps(interaction),
            'source': FeedbackSource.INTERACTION.value,
            'type': FeedbackType.IMPLICIT.value,
            'context': {
                'action_type': interaction.get('action_type'),
                'item_id': interaction.get('item_id'),
                'timestamp': interaction.get('timestamp')
            },
            'created_at': datetime.now().isoformat()
        }
        
        # Collecter le feedback implicite
        feedback_id = feedback_collector.collect(feedback_data)
        feedback_items.append(feedback_id)
    
    # Prédire la satisfaction utilisateur basée sur les interactions
    satisfaction_score = satisfaction_predictor.predict_from_interactions({
        'user_id': user_id,
        'interactions': interactions
    })
    
    return jsonify({
        'feedback_ids': feedback_items,
        'status': 'success',
        'satisfaction_score': satisfaction_score
    }), 201

@feedback_api.route('/feedback', methods=['GET'])
def get_feedback():
    """Récupère les feedbacks avec filtrage optionnel."""
    # Paramètres de filtrage
    user_id = request.args.get('user_id')
    source = request.args.get('source')
    feedback_type = request.args.get('type')
    category = request.args.get('category')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Construction du filtre
    filters = {}
    if user_id:
        filters['user_id'] = user_id
    if source:
        filters['source'] = source
    if feedback_type:
        filters['type'] = feedback_type
    if category:
        filters['category'] = category
    if start_date:
        filters['start_date'] = start_date
    if end_date:
        filters['end_date'] = end_date
    
    # Récupérer les feedbacks filtrés
    feedbacks = feedback_repository.find_all(filters)
    
    return jsonify(feedbacks)

@feedback_api.route('/feedback/<feedback_id>', methods=['GET'])
def get_feedback_by_id(feedback_id):
    """Récupère un feedback spécifique par son ID."""
    feedback = feedback_repository.find_by_id(feedback_id)
    
    if not feedback:
        return jsonify({'error': 'Feedback non trouvé'}), 404
    
    return jsonify(feedback)

@feedback_api.route('/analytics/sentiment', methods=['GET'])
def get_sentiment_analytics():
    """Récupère les analytics de sentiment."""
    # Paramètres de filtrage
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Construction du filtre
    filters = {}
    if user_id:
        filters['user_id'] = user_id
    if start_date:
        filters['start_date'] = start_date
    if end_date:
        filters['end_date'] = end_date
    
    # Analyser le sentiment global
    sentiment_analytics = feedback_analyzer.analyze_sentiment_trends(filters)
    
    return jsonify(sentiment_analytics)

@feedback_api.route('/analytics/topics', methods=['GET'])
def get_topic_analytics():
    """Récupère les analytics des sujets mentionnés dans les feedbacks."""
    # Paramètres de filtrage
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Construction du filtre
    filters = {}
    if user_id:
        filters['user_id'] = user_id
    if start_date:
        filters['start_date'] = start_date
    if end_date:
        filters['end_date'] = end_date
    
    # Analyser les sujets populaires
    topic_analytics = feedback_analyzer.analyze_topic_trends(filters)
    
    return jsonify(topic_analytics)

@feedback_api.route('/prediction/satisfaction', methods=['GET'])
def get_satisfaction_prediction():
    """Récupère la prédiction de satisfaction pour un utilisateur."""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'L\'ID utilisateur est requis'}), 400
    
    # Récupérer les données utilisateur
    user_feedbacks = feedback_repository.find_all({'user_id': user_id})
    
    # Prédire la satisfaction
    satisfaction_score = satisfaction_predictor.predict_overall({
        'user_id': user_id,
        'feedbacks': user_feedbacks
    })
    
    return jsonify({
        'user_id': user_id,
        'satisfaction_score': satisfaction_score,
        'prediction_date': datetime.now().isoformat()
    })

@feedback_api.route('/learning/retrain', methods=['POST'])
def retrain_model():
    """Déclenche le réentraînement du modèle prédictif."""
    data = request.json or {}
    full_retrain = data.get('full_retrain', False)
    
    # Réentraîner le modèle
    training_result = satisfaction_predictor.retrain(full_retrain)
    
    return jsonify({
        'status': 'success',
        'model_version': training_result.get('model_version'),
        'metrics': training_result.get('metrics'),
        'training_date': datetime.now().isoformat()
    })

@feedback_api.route('/integration/behavior', methods=['POST'])
def integrate_with_behavior():
    """Intègre les données du service d'analyse comportementale."""
    data = request.json
    
    if not data or 'profiles' not in data:
        return jsonify({'error': 'Les profils utilisateur sont requis'}), 400
    
    profiles = data.get('profiles', [])
    
    # Mise à jour du modèle prédictif avec les profils comportementaux
    update_result = satisfaction_predictor.update_with_behavior_profiles(profiles)
    
    return jsonify({
        'status': 'success',
        'updated_profiles': len(profiles),
        'model_improvement': update_result.get('improvement')
    })
