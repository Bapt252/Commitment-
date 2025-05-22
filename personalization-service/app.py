from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import redis
import json
from datetime import datetime
import logging
import os

# Import des métriques Prometheus
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
CORS(app)

# Configuration Redis
try:
    redis_conn = redis.Redis(
        host=os.getenv('REDIS_HOST', 'redis'),
        port=int(os.getenv('REDIS_PORT', 6379)),    
        db=int(os.getenv('REDIS_DB', 0)),
        decode_responses=True
    )
except Exception as e:
    print(f"Erreur connexion Redis: {e}")
    redis_conn = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Poids globaux par défaut
GLOBAL_WEIGHTS = {
    'skills_match': 0.25,
    'experience_match': 0.20,
    'education_match': 0.15,
    'location_match': 0.10,
    'salary_match': 0.15,
    'company_culture': 0.10,
    'growth_opportunity': 0.05
}

# Seuil de cold start
COLD_START_THRESHOLD = 5

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de santé du service"""
    try:
        redis_status = 'connected'
        if redis_conn:
            redis_conn.ping()
        else:
            redis_status = 'disconnected'
        return jsonify({
            'status': 'healthy',
            'service': 'personalization-service',
            'redis': redis_status,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/metrics', methods=['GET'])
def metrics():
    """Endpoint pour exposer les métriques Prometheus"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route('/api/feedback', methods=['POST'])
def collect_feedback():
    """Collecte le feedback utilisateur"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'job_id', 'action']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        # Conversion action -> rating
        rating_map = {
            'apply': 5.0,
            'save': 4.0,
            'view': 3.0,
            'ignore': 2.0,
            'reject': 1.0
        }
        
        feedback = {
            'user_id': data['user_id'],
            'job_id': data['job_id'],
            'action': data['action'],
            'match_score': data.get('match_score', 0.0),
            'timestamp': datetime.now().isoformat(),
            'implicit_rating': rating_map.get(data['action'], 2.0)
        }
        
        # Stockage dans Redis avec TTL de 6 mois
        if redis_conn:
            key = f"user_feedback:{data['user_id']}:{data['job_id']}"
            redis_conn.setex(key, 86400 * 180, json.dumps(feedback))
            
            # Mise à jour des statistiques utilisateur
            _update_user_stats(data['user_id'], data['action'])
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback collected successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error collecting feedback: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def _update_user_stats(user_id, action):
    """Met à jour les statistiques comportementales de l'utilisateur"""
    if not redis_conn:
        return
        
    stats_key = f"user_stats:{user_id}"
    stats = redis_conn.get(stats_key)
    
    if stats:
        stats = json.loads(stats)
    else:
        stats = {'total_actions': 0, 'action_counts': {}}
        
    stats['total_actions'] += 1
    stats['action_counts'][action] = stats['action_counts'].get(action, 0) + 1
    stats['last_activity'] = datetime.now().isoformat()
    
    redis_conn.setex(stats_key, 86400 * 180, json.dumps(stats))

@app.route('/api/personalized-weights/<user_id>', methods=['GET'])
def get_personalized_weights(user_id):
    """Récupère les poids personnalisés pour un utilisateur"""
    try:
        # Vérifier si l'utilisateur a assez d'historique
        is_cold_start = _is_cold_start_user(user_id)
        
        if is_cold_start:
            return jsonify({
                'user_id': user_id,
                'personalized_weights': GLOBAL_WEIGHTS,
                'status': 'cold_start',
                'timestamp': datetime.now().isoformat()
            }), 200
        
        # Récupérer les préférences utilisateur
        preferences = _analyze_user_preferences(user_id)
        
        # Personnaliser les poids
        personalized_weights = GLOBAL_WEIGHTS.copy()
        
        # Ajustement basé sur les préférences détectées
        for criterion, preference_score in preferences.items():
            if criterion in personalized_weights:
                # Augmentation du poids si forte préférence
                adjustment = (preference_score - 0.5) * 0.2  # Max ±10%
                personalized_weights[criterion] += adjustment
        
        # Normalisation pour que la somme reste 1
        total_weight = sum(personalized_weights.values())
        if total_weight > 0:
            personalized_weights = {k: v/total_weight for k, v in personalized_weights.items()}
        
        return jsonify({
            'user_id': user_id,
            'personalized_weights': personalized_weights,
            'preferences': preferences,
            'status': 'personalized',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting personalized weights: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def _is_cold_start_user(user_id):
    """Vérifie si l'utilisateur est en situation de cold start"""
    if not redis_conn:
        return True
        
    stats_key = f"user_stats:{user_id}"
    stats = redis_conn.get(stats_key)
    
    if not stats:
        return True
        
    stats = json.loads(stats)
    return stats.get('total_actions', 0) < COLD_START_THRESHOLD

def _analyze_user_preferences(user_id):
    """Analyse les préférences utilisateur basées sur l'historique"""
    if not redis_conn:
        return {}
        
    pattern = f"user_feedback:{user_id}:*"
    feedback_keys = redis_conn.keys(pattern)
    
    if not feedback_keys:
        return {}
    
    # Récupérer tous les feedbacks
    positive_actions = 0
    total_actions = 0
    avg_positive_score = 0
    
    for key in feedback_keys:
        feedback = json.loads(redis_conn.get(key))
        total_actions += 1
        
        if feedback['implicit_rating'] >= 4.0:
            positive_actions += 1
            avg_positive_score += feedback.get('match_score', 0.0)
    
    if positive_actions == 0:
        return {}
    
    avg_positive_score /= positive_actions
    
    # Analyse des préférences basée sur les patterns
    preferences = {}
    
    # Si l'utilisateur accepte des matches avec des scores plus bas,
    # il privilégie peut-être d'autres critères
    if avg_positive_score < 0.7:
        preferences['company_culture'] = 0.8
        preferences['growth_opportunity'] = 0.7
    else:
        preferences['skills_match'] = 0.8
        preferences['experience_match'] = 0.7
    
    return preferences

@app.route('/api/hybrid-score', methods=['POST'])
def calculate_hybrid_score():
    """Calcule le score hybride pour une recommandation"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'job_id', 'base_match_score']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        base_score = data['base_match_score']
        user_id = data['user_id']
        
        # Score collaboratif
        collaborative_score = _get_collaborative_score(user_id, data['job_id'])
        
        # Score basé sur les préférences personnelles
        personal_score = _get_personal_preference_score(user_id, data['job_id'])
        
        # Combinaison pondérée
        hybrid_score = (
            0.5 * base_score +
            0.3 * collaborative_score +
            0.2 * personal_score
        )
        
        # Clamp entre 0 et 1
        hybrid_score = min(1.0, max(0.0, hybrid_score))
        
        return jsonify({
            'user_id': user_id,
            'job_id': data['job_id'],
            'base_score': base_score,
            'collaborative_score': collaborative_score,
            'personal_score': personal_score,
            'hybrid_score': hybrid_score,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error calculating hybrid score: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def _get_collaborative_score(user_id, job_id):
    """Calcule le score collaboratif (version simplifiée)"""
    if not redis_conn:
        return 0.5
    
    # Version simplifiée - en pratique, cela nécessiterait
    # une analyse plus complexe des utilisateurs similaires
    pattern = f"user_feedback:*:{job_id}"
    feedback_keys = redis_conn.keys(pattern)
    
    if not feedback_keys:
        return 0.5
    
    total_rating = 0
    count = 0
    
    for key in feedback_keys:
        feedback = json.loads(redis_conn.get(key))
        if feedback['user_id'] != user_id:  # Exclure l'utilisateur actuel
            total_rating += feedback['implicit_rating']
            count += 1
    
    if count == 0:
        return 0.5
    
    # Normaliser le score moyen entre 0 et 1
    avg_rating = total_rating / count
    return min(1.0, avg_rating / 5.0)

def _get_personal_preference_score(user_id, job_id):
    """Calcule un score basé sur les préférences personnelles historiques"""
    if not redis_conn:
        return 0.5
    
    # Récupérer l'historique de l'utilisateur
    pattern = f"user_feedback:{user_id}:*"
    feedback_keys = redis_conn.keys(pattern)
    
    if not feedback_keys:
        return 0.5
    
    # Calculer le score moyen des actions positives
    positive_scores = []
    
    for key in feedback_keys:
        feedback = json.loads(redis_conn.get(key))
        if feedback['implicit_rating'] >= 4.0:
            positive_scores.append(feedback.get('match_score', 0.5))
    
    if not positive_scores:
        return 0.5
    
    return sum(positive_scores) / len(positive_scores)

@app.route('/api/ab-test', methods=['POST'])
def assign_ab_test():
    """Assigne un utilisateur à un variant de test A/B"""
    try:
        data = request.get_json()
        
        if 'user_id' not in data or 'variant' not in data:
            return jsonify({
                'error': 'Missing user_id or variant'
            }), 400
        
        valid_variants = ['control', 'demographic', 'collaborative', 'hybrid']
        if data['variant'] not in valid_variants:
            return jsonify({
                'error': 'Invalid variant',
                'valid_variants': valid_variants
            }), 400
        
        if redis_conn:
            # Enregistrement de l'assignation du variant
            test_key = f"ab_test:{data['user_id']}"
            test_data = {
                'user_id': data['user_id'],
                'variant': data['variant'],
                'assigned_at': datetime.now().isoformat()
            }
            redis_conn.setex(test_key, 86400 * 30, json.dumps(test_data))  # 30 jours
        
        return jsonify({
            'user_id': data['user_id'],
            'assigned_variant': data['variant'],
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error assigning A/B test: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/user-stats/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """Récupère les statistiques d'un utilisateur"""
    try:
        if not redis_conn:
            return jsonify({
                'user_id': user_id,
                'message': 'Redis not available',
                'is_cold_start': True
            }), 200
            
        stats_key = f"user_stats:{user_id}"
        stats = redis_conn.get(stats_key)
        
        if not stats:
            return jsonify({
                'user_id': user_id,
                'message': 'No stats available',
                'is_cold_start': True
            }), 200
        
        stats = json.loads(stats)
        is_cold_start = _is_cold_start_user(user_id)
        
        return jsonify({
            'user_id': user_id,
            'stats': stats,
            'is_cold_start': is_cold_start,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/collaborative-recommendations', methods=['POST'])
def get_collaborative_recommendations():
    """Génère des recommandations collaboratives"""
    try:
        data = request.get_json()
        
        if 'user_id' not in data or 'candidate_jobs' not in data:
            return jsonify({
                'error': 'Missing user_id or candidate_jobs'
            }), 400
        
        recommendations = {}
        
        for job_id in data['candidate_jobs']:
            score = _get_collaborative_score(data['user_id'], job_id)
            recommendations[job_id] = score
        
        return jsonify({
            'user_id': data['user_id'],
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5060))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', 'false').lower() == 'true')
