"""
API de profils utilisateurs enrichis.

Ce module expose une API REST pour accéder aux profils utilisateurs enrichis avec
les caractéristiques comportementales, les préférences et les patterns détectés.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import json
import time
from datetime import datetime, timedelta
import traceback

# Flask imports
from flask import Flask, request, jsonify, Blueprint, current_app
from flask_cors import CORS
from functools import wraps

# Import des composants de la Session 8
from session8.config import CONFIG
from session8.profile_manager import ProfileManager
from session8.feature_extractor import FeatureExtractor
from session8.preference_calculator import PreferenceCalculator
from session8.pattern_detector import PatternDetector
from session8.user_clustering import UserClustering

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Création du blueprint Flask pour l'API
api_blueprint = Blueprint('user_profiling_api', __name__)

# Instances des composants (à initialiser lors de l'attachement à l'application)
profile_manager = None
feature_extractor = None
preference_calculator = None
pattern_detector = None
user_clustering = None

# Middleware d'authentification
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Vérification de l'authentification si activée
        if CONFIG["api"]["auth_enabled"]:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({"error": "Unauthorized access"}), 401
            
            token = auth_header.split(' ')[1]
            # Validation du token (à adapter selon votre système d'authentification)
            if token != CONFIG["api"]["secret_key"]:
                return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Middleware de limitation de taux
def rate_limiter(f):
    # Stockage simple des requêtes par IP
    request_counters = {}
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if CONFIG["api"]["rate_limit"]["enabled"]:
            client_ip = request.remote_addr
            current_time = time.time()
            rate_limit = CONFIG["api"]["rate_limit"]["limit"]
            rate_period = CONFIG["api"]["rate_limit"]["period"]
            
            # Nettoyage des anciennes entrées
            for ip in list(request_counters.keys()):
                if current_time - request_counters[ip]["timestamp"] > rate_period:
                    del request_counters[ip]
            
            # Vérification du taux de requêtes
            if client_ip in request_counters:
                if request_counters[client_ip]["count"] >= rate_limit:
                    return jsonify({"error": "Rate limit exceeded"}), 429
                request_counters[client_ip]["count"] += 1
            else:
                request_counters[client_ip] = {
                    "count": 1,
                    "timestamp": current_time
                }
        
        return f(*args, **kwargs)
    return decorated_function

# Endpoints de l'API

@api_blueprint.route('/profiles/<user_id>', methods=['GET'])
@auth_required
@rate_limiter
def get_user_profile(user_id):
    """
    Récupère le profil enrichi d'un utilisateur spécifique.
    
    Args:
        user_id: Identifiant de l'utilisateur
        
    Returns:
        Le profil utilisateur enrichi avec les caractéristiques comportementales
    """
    try:
        # Paramètres optionnels
        include_features = request.args.get('include_features', 'false').lower() == 'true'
        include_preferences = request.args.get('include_preferences', 'false').lower() == 'true'
        include_patterns = request.args.get('include_patterns', 'false').lower() == 'true'
        include_clusters = request.args.get('include_clusters', 'false').lower() == 'true'
        
        # Récupérer le profil de base
        profile = profile_manager.get_profile(user_id)
        if not profile:
            return jsonify({"error": f"Profile not found for user {user_id}"}), 404
        
        # Enrichir avec les caractéristiques si demandé
        if include_features and feature_extractor:
            features = feature_extractor.get_features(user_id)
            profile["features"] = features
        
        # Enrichir avec les préférences si demandé
        if include_preferences and preference_calculator:
            preferences = preference_calculator.get_preferences(user_id)
            profile["preferences"] = preferences
        
        # Enrichir avec les patterns comportementaux si demandé
        if include_patterns and pattern_detector:
            patterns = pattern_detector.get_user_patterns(user_id)
            profile["patterns"] = patterns
        
        # Enrichir avec les informations de cluster si demandé
        if include_clusters and user_clustering:
            user_clusters = user_clustering.get_user_clusters(user_id)
            profile["clusters"] = user_clusters
        
        return jsonify(profile)
    except Exception as e:
        logger.error(f"Error getting profile for user {user_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/profiles', methods=['GET'])
@auth_required
@rate_limiter
def get_user_profiles():
    """
    Récupère plusieurs profils utilisateurs selon des critères de filtrage.
    
    Query params:
        cluster_id: Filtre par cluster d'utilisateurs
        pattern_id: Filtre par pattern comportemental
        feature_value: Filtre par valeur de caractéristique
        limit: Nombre maximum de profils à retourner
        offset: Décalage pour la pagination
        
    Returns:
        Liste des profils utilisateurs correspondant aux critères
    """
    try:
        # Paramètres de filtrage
        cluster_id = request.args.get('cluster_id')
        pattern_id = request.args.get('pattern_id')
        feature_key = request.args.get('feature_key')
        feature_value = request.args.get('feature_value')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Paramètres d'inclusion
        include_features = request.args.get('include_features', 'false').lower() == 'true'
        include_preferences = request.args.get('include_preferences', 'false').lower() == 'true'
        include_patterns = request.args.get('include_patterns', 'false').lower() == 'true'
        include_clusters = request.args.get('include_clusters', 'false').lower() == 'true'
        
        # Récupérer les profils de base
        profiles = profile_manager.get_profiles(limit=limit, offset=offset)
        
        # Filtrer par cluster si demandé
        if cluster_id and user_clustering:
            cluster_users = user_clustering.get_cluster_users(cluster_id)
            profiles = [p for p in profiles if p.get("user_id") in cluster_users]
        
        # Filtrer par pattern si demandé
        if pattern_id and pattern_detector:
            pattern_users = pattern_detector.get_pattern_users(pattern_id)
            profiles = [p for p in profiles if p.get("user_id") in pattern_users]
        
        # Filtrer par caractéristique si demandée
        if feature_key and feature_value and feature_extractor:
            filtered_users = feature_extractor.filter_users_by_feature(feature_key, feature_value)
            profiles = [p for p in profiles if p.get("user_id") in filtered_users]
        
        # Enrichir les profils si demandé
        enriched_profiles = []
        for profile in profiles:
            user_id = profile.get("user_id")
            
            # Enrichir avec les caractéristiques si demandé
            if include_features and feature_extractor:
                features = feature_extractor.get_features(user_id)
                profile["features"] = features
            
            # Enrichir avec les préférences si demandé
            if include_preferences and preference_calculator:
                preferences = preference_calculator.get_preferences(user_id)
                profile["preferences"] = preferences
            
            # Enrichir avec les patterns comportementaux si demandé
            if include_patterns and pattern_detector:
                patterns = pattern_detector.get_user_patterns(user_id)
                profile["patterns"] = patterns
            
            # Enrichir avec les informations de cluster si demandé
            if include_clusters and user_clustering:
                user_clusters = user_clustering.get_user_clusters(user_id)
                profile["clusters"] = user_clusters
            
            enriched_profiles.append(profile)
        
        return jsonify(enriched_profiles)
    except Exception as e:
        logger.error(f"Error getting profiles: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/features/<user_id>', methods=['GET'])
@auth_required
@rate_limiter
def get_user_features(user_id):
    """
    Récupère les caractéristiques comportementales d'un utilisateur.
    
    Args:
        user_id: Identifiant de l'utilisateur
        
    Returns:
        Les caractéristiques comportementales de l'utilisateur
    """
    try:
        if not feature_extractor:
            return jsonify({"error": "Feature extractor not available"}), 503
        
        # Période optionnelle
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str)
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use ISO format."}), 400
        
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str)
            except ValueError:
                return jsonify({"error": "Invalid end_date format. Use ISO format."}), 400
        
        # Récupérer les caractéristiques
        features = feature_extractor.extract_features(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
        
        if not features:
            return jsonify({"error": f"No features found for user {user_id}"}), 404
        
        return jsonify(features)
    except Exception as e:
        logger.error(f"Error getting features for user {user_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/preferences/<user_id>', methods=['GET'])
@auth_required
@rate_limiter
def get_user_preferences(user_id):
    """
    Récupère les préférences calculées pour un utilisateur.
    
    Args:
        user_id: Identifiant de l'utilisateur
        
    Returns:
        Les préférences calculées pour l'utilisateur
    """
    try:
        if not preference_calculator:
            return jsonify({"error": "Preference calculator not available"}), 503
        
        # Récupérer les préférences
        preferences = preference_calculator.get_preferences(user_id)
        
        if not preferences:
            return jsonify({"error": f"No preferences found for user {user_id}"}), 404
        
        return jsonify(preferences)
    except Exception as e:
        logger.error(f"Error getting preferences for user {user_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/patterns/<user_id>', methods=['GET'])
@auth_required
@rate_limiter
def get_user_patterns(user_id):
    """
    Récupère les patterns comportementaux détectés pour un utilisateur.
    
    Args:
        user_id: Identifiant de l'utilisateur
        
    Returns:
        Les patterns comportementaux de l'utilisateur
    """
    try:
        if not pattern_detector:
            return jsonify({"error": "Pattern detector not available"}), 503
        
        # Récupérer les patterns
        patterns = pattern_detector.get_user_patterns(user_id)
        
        if not patterns:
            return jsonify({"error": f"No patterns found for user {user_id}"}), 404
        
        return jsonify(patterns)
    except Exception as e:
        logger.error(f"Error getting patterns for user {user_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/clusters/<user_id>', methods=['GET'])
@auth_required
@rate_limiter
def get_user_clusters(user_id):
    """
    Récupère les clusters auxquels appartient un utilisateur.
    
    Args:
        user_id: Identifiant de l'utilisateur
        
    Returns:
        Les informations de cluster de l'utilisateur
    """
    try:
        if not user_clustering:
            return jsonify({"error": "User clustering not available"}), 503
        
        # Récupérer les clusters
        clusters = user_clustering.get_user_clusters(user_id)
        
        if not clusters:
            return jsonify({"error": f"No cluster information found for user {user_id}"}), 404
        
        return jsonify(clusters)
    except Exception as e:
        logger.error(f"Error getting clusters for user {user_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/recommendations/<user_id>', methods=['GET'])
@auth_required
@rate_limiter
def get_user_recommendations(user_id):
    """
    Récupère des recommandations personnalisées pour un utilisateur.
    
    Args:
        user_id: Identifiant de l'utilisateur
        
    Query params:
        item_type: Type d'élément à recommander (job, cv, etc.)
        limit: Nombre maximum de recommandations
        
    Returns:
        Liste des recommandations avec scores
    """
    try:
        if not preference_calculator:
            return jsonify({"error": "Preference calculator not available"}), 503
        
        # Paramètres
        item_type = request.args.get('item_type', 'job')
        limit = int(request.args.get('limit', 10))
        
        # Les recommandations nécessiteraient un service de recommandation complet
        # On simule ici quelques recommandations basées sur les préférences
        
        # Récupérer les préférences utilisateur
        preferences = preference_calculator.get_preferences(user_id)
        
        if not preferences:
            return jsonify({"error": f"No preferences found for user {user_id}"}), 404
        
        # Simuler des recommandations
        recommendations = []
        for i in range(limit):
            item_id = f"item_{i + 1}"
            score = preference_calculator.get_recommendation_score(user_id, item_id, item_type)
            
            recommendations.append({
                "id": item_id,
                "type": item_type,
                "score": score,
                "title": f"Recommended {item_type} {i + 1}",
                "description": f"This is a simulated recommendation based on user preferences"
            })
        
        # Trier par score
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return jsonify(recommendations)
    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@api_blueprint.route('/stats', methods=['GET'])
@auth_required
@rate_limiter
def get_profiling_stats():
    """
    Récupère des statistiques globales sur les profils utilisateurs.
    
    Returns:
        Statistiques globales sur les profils
    """
    try:
        # Statistiques de base
        total_profiles = len(profile_manager.get_profiles())
        
        # Statistiques de clustering si disponible
        cluster_stats = None
        if user_clustering:
            clusters = user_clustering.get_all_clusters()
            cluster_stats = {
                "total_clusters": len(clusters),
                "cluster_sizes": {cluster_id: len(members) for cluster_id, members in clusters.items()},
                "cluster_details": clusters
            }
        
        # Statistiques de patterns si disponible
        pattern_stats = None
        if pattern_detector:
            patterns = pattern_detector.get_all_patterns()
            pattern_stats = {
                "total_patterns": len(patterns),
                "pattern_types": {
                    "sequence": len([p for p in patterns if p.get("type") == "sequence"]),
                    "temporal": len([p for p in patterns if p.get("type") == "temporal"]),
                    "recurrent": len([p for p in patterns if p.get("type") == "recurrent"])
                }
            }
        
        # Statistiques globales
        stats = {
            "total_profiles": total_profiles,
            "active_profiles": profile_manager.count_active_profiles(),
            "last_update": datetime.now().isoformat(),
            "clusters": cluster_stats,
            "patterns": pattern_stats
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting profiling stats: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# Fonction pour initialiser l'API
def init_api_app():
    """
    Initialise l'application Flask pour l'API.
    
    Returns:
        Application Flask configurée
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = CONFIG["api"]["secret_key"]
    
    # Activation de CORS
    CORS(app, resources={r"/*": {"origins": CONFIG["api"]["cors_origins"]}})
    
    # Enregistrement du blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/profiling')
    
    # Initialisation des composants
    with app.app_context():
        global profile_manager, feature_extractor, preference_calculator, pattern_detector, user_clustering
        
        profile_manager = ProfileManager(storage_path=CONFIG["storage"]["profiles_path"])
        feature_extractor = FeatureExtractor(storage_path=CONFIG["storage"]["features_path"])
        preference_calculator = PreferenceCalculator(
            profile_manager=profile_manager,
            pattern_detector=pattern_detector,
            storage_path=CONFIG["storage"]["preferences_path"]
        )
        pattern_detector = PatternDetector(storage_path=CONFIG["storage"]["patterns_path"])
        user_clustering = UserClustering(storage_path=CONFIG["storage"]["clusters_path"])
    
    return app

# Point d'entrée pour exécuter l'API indépendamment
def run_api_server():
    """
    Exécute le serveur d'API en tant qu'application autonome.
    """
    app = init_api_app()
    app.run(
        host=CONFIG["api"]["host"],
        port=CONFIG["api"]["port"],
        debug=CONFIG["api"]["debug"]
    )

if __name__ == '__main__':
    run_api_server()
