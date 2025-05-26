from flask import Blueprint, jsonify, request
from datetime import datetime
import logging
from profiles.profile_builder import UserProfileBuilder
from clustering.kmeans_clustering import UserClusterer
from patterns.sequence_detection import PatternDetector
from scoring.preference_calculator import PreferenceScoreCalculator

logger = logging.getLogger(__name__)
behavior_api = Blueprint('behavior_api', __name__)

# Initialiser les services
profile_builder = UserProfileBuilder()
user_clusterer = UserClusterer()
pattern_detector = PatternDetector()
preference_calculator = PreferenceScoreCalculator()

# Variables globales pour stocker les données (en mémoire pour simplicité)
# Dans une implémentation de production, utiliser une BD
user_profiles = {}
user_clusters = {}
user_patterns = {}
preference_scores = {}

@behavior_api.route('/profiles', methods=['GET'])
def get_profiles():
    """Récupère tous les profils utilisateur ou un profil spécifique."""
    user_id = request.args.get('user_id')
    
    if user_id:
        if user_id in user_profiles:
            return jsonify(user_profiles[user_id])
        else:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
    else:
        return jsonify(list(user_profiles.values()))

@behavior_api.route('/profiles', methods=['POST'])
def create_profile():
    """Crée ou met à jour un profil utilisateur."""
    data = request.json
    
    if not data or 'user_id' not in data:
        return jsonify({'error': 'ID utilisateur requis'}), 400
        
    user_id = data['user_id']
    user_data = {k: v for k, v in data.items() if k != 'interactions'}
    
    # Traiter les interactions si présentes
    interactions = data.get('interactions', [])
    
    if interactions:
        # Construire ou mettre à jour le profil
        if not user_profiles:
            # Premier profil
            user_profiles.update(profile_builder.build_user_profiles(interactions, [user_data]))
        elif user_id in user_profiles:
            # Mise à jour d'un profil existant
            updated_profiles = profile_builder.update_profiles(user_profiles, interactions)
            user_profiles.update(updated_profiles)
        else:
            # Nouveau profil
            new_profile = profile_builder.build_user_profiles(interactions, [user_data])
            user_profiles.update(new_profile)
    else:
        # Profil de base sans interactions
        user_profiles[user_id] = {
            'user_id': user_id,
            **user_data,
            'action_count': 0,
            'created_at': datetime.now().isoformat()
        }
    
    return jsonify(user_profiles[user_id]), 201

@behavior_api.route('/clusters', methods=['GET'])
def get_clusters():
    """Récupère les clusters d'utilisateurs."""
    return jsonify({
        'clusters': user_clusters.get('cluster_profiles', []),
        'user_assignments': user_clusters.get('user_assignments', {})
    })

@behavior_api.route('/clusters', methods=['POST'])
def create_clusters():
    """Crée des clusters basés sur les profils utilisateur existants."""
    if not user_profiles:
        return jsonify({'error': 'Aucun profil utilisateur disponible'}), 400
        
    # Paramètres optionnels
    data = request.json or {}
    n_clusters = data.get('n_clusters', 5)
    
    # Clustering
    clusterer = UserClusterer(n_clusters=n_clusters)
    user_assignments = clusterer.fit(list(user_profiles.values())).predict(list(user_profiles.values()))
    cluster_profiles = clusterer.get_cluster_profiles()
    
    # Stocker les résultats
    user_clusters['cluster_profiles'] = cluster_profiles
    user_clusters['user_assignments'] = user_assignments
    
    return jsonify({
        'clusters': cluster_profiles,
        'user_assignments': user_assignments
    }), 201

@behavior_api.route('/patterns', methods=['GET'])
def get_patterns():
    """Récupère les patterns comportementaux des utilisateurs."""
    user_id = request.args.get('user_id')
    
    if user_id:
        if user_id in user_patterns:
            return jsonify({user_id: user_patterns[user_id]})
        else:
            return jsonify({'error': 'Patterns non trouvés pour cet utilisateur'}), 404
    else:
        return jsonify(user_patterns)

@behavior_api.route('/patterns', methods=['POST'])
def detect_patterns():
    """Détecte des patterns comportementaux à partir des actions utilisateur."""
    data = request.json
    
    if not data or 'actions' not in data:
        return jsonify({'error': 'Actions utilisateur requises'}), 400
        
    actions = data['actions']
    
    # Configuration optionnelle
    window_size = data.get('window_size', 30)
    min_occurrences = data.get('min_occurrences', 3)
    
    # Détecter les patterns
    detector = PatternDetector(window_size=window_size, min_occurrences=min_occurrences)
    patterns = detector.detect_patterns(actions)
    
    # Stocker les résultats
    user_patterns.update(patterns)
    
    # Patterns communs
    common_patterns = detector.get_common_patterns()
    
    return jsonify({
        'user_patterns': patterns,
        'common_patterns': common_patterns
    }), 201

@behavior_api.route('/preference-scores', methods=['GET'])
def get_preference_scores():
    """Récupère les scores de préférence des utilisateurs."""
    user_id = request.args.get('user_id')
    
    if user_id:
        if user_id in preference_scores:
            return jsonify({user_id: preference_scores[user_id]})
        else:
            return jsonify({'error': 'Scores non trouvés pour cet utilisateur'}), 404
    else:
        return jsonify(preference_scores)

@behavior_api.route('/preference-scores', methods=['POST'])
def calculate_preference_scores():
    """Calcule les scores de préférence à partir des actions utilisateur."""
    data = request.json
    
    if not data or 'actions' not in data:
        return jsonify({'error': 'Actions utilisateur requises'}), 400
        
    actions = data['actions']
    
    # Configuration optionnelle
    categories = data.get('categories')
    recency_decay = data.get('recency_decay', 0.9)
    time_window_days = data.get('time_window_days', 30)
    
    # Calculer les scores
    calculator = PreferenceScoreCalculator(
        recency_decay=recency_decay,
        time_window_days=time_window_days
    )
    scores = calculator.calculate_preference_scores(actions, categories)
    
    # Stocker les résultats
    preference_scores.update(scores)
    
    return jsonify(scores), 201

@behavior_api.route('/interactions', methods=['POST'])
def add_interactions():
    """Ajoute de nouvelles interactions et met à jour tous les modèles."""
    data = request.json
    
    if not data or 'interactions' not in data:
        return jsonify({'error': 'Interactions requises'}), 400
        
    interactions = data['interactions']
    
    # Mettre à jour les profils
    if user_profiles:
        updated_profiles = profile_builder.update_profiles(user_profiles, interactions)
        user_profiles.update(updated_profiles)
    else:
        user_profiles.update(profile_builder.build_user_profiles(interactions))
    
    # Mettre à jour les clusters si existants
    if user_clusters:
        clusterer = UserClusterer(n_clusters=len(user_clusters.get('cluster_profiles', [])))
        user_assignments = clusterer.fit(list(user_profiles.values())).predict(list(user_profiles.values()))
        cluster_profiles = clusterer.get_cluster_profiles()
        
        user_clusters['cluster_profiles'] = cluster_profiles
        user_clusters['user_assignments'] = user_assignments
    
    # Mettre à jour les patterns
    if interactions:
        detector = PatternDetector()
        patterns = detector.detect_patterns(interactions)
        for user_id, pattern in patterns.items():
            if user_id in user_patterns:
                # Fusion des patterns (simplifiée)
                for pattern_type, values in pattern.items():
                    if pattern_type in user_patterns[user_id]:
                        # Fusion spécifique selon le type
                        if pattern_type == 'time_patterns':
                            for period_type, period_values in values.items():
                                user_patterns[user_id][pattern_type][period_type] = period_values
                        else:
                            user_patterns[user_id][pattern_type].update(values)
                    else:
                        user_patterns[user_id][pattern_type] = values
            else:
                user_patterns[user_id] = pattern
    
    # Mettre à jour les scores de préférence
    if preference_scores and interactions:
        calculator = PreferenceScoreCalculator()
        updated_scores = calculator.update_preference_scores(preference_scores, interactions)
        preference_scores.update(updated_scores)
    elif interactions:
        calculator = PreferenceScoreCalculator()
        scores = calculator.calculate_preference_scores(interactions)
        preference_scores.update(scores)
    
    return jsonify({
        'success': True,
        'updated_profiles': list(user_profiles.keys()),
        'updated_patterns': list(user_patterns.keys()),
        'updated_scores': list(preference_scores.keys())
    }), 200