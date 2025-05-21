"""
API REST pour le service de personnalisation des matchs.
Expose les fonctionnalités de personnalisation aux autres services.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from flask import Flask, request, jsonify, g
import psycopg2
from psycopg2.extras import RealDictCursor
import os

from .matcher import PersonalizedMatcher

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Configuration de la base de données
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "database": os.getenv("DB_NAME", "commitment"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
    "port": int(os.getenv("DB_PORT", 5432))
}

def get_db():
    """
    Obtient une connexion à la base de données
    """
    if 'db' not in g:
        g.db = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    """
    Ferme la connexion à la base de données
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def get_matcher():
    """
    Obtient une instance du PersonalizedMatcher
    """
    if 'matcher' not in g:
        g.matcher = PersonalizedMatcher(get_db())
    return g.matcher

@app.route('/api/personalization/matches/<int:user_id>', methods=['GET'])
def get_personalized_matches(user_id: int):
    """
    Endpoint pour obtenir des matchs personnalisés pour un utilisateur
    """
    try:
        # Paramètres de requête
        limit = int(request.args.get('limit', 10))
        context = json.loads(request.args.get('context', '{}'))
        
        # Récupérer les candidats de base depuis la base de données
        base_candidates = _get_base_candidates(user_id, limit * 2)  # Récupérer plus pour avoir de la marge
        
        # Obtenir les matchs personnalisés
        matcher = get_matcher()
        matches = matcher.get_personalized_matches(
            user_id, 
            base_candidates, 
            limit=limit, 
            context=context
        )
        
        return jsonify({"matches": matches})
    
    except Exception as e:
        logger.error(f"Error getting personalized matches: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/personalization/feedback', methods=['POST'])
def record_feedback():
    """
    Endpoint pour enregistrer le feedback d'un utilisateur
    """
    try:
        data = request.json
        
        # Validation des données
        required_fields = ['user_id', 'candidate_id', 'feedback_type', 'feedback_value']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Enregistrer le feedback
        matcher = get_matcher()
        success = matcher.update_feedback(
            data['user_id'],
            data['candidate_id'],
            data['feedback_type'],
            data['feedback_value']
        )
        
        if success:
            return jsonify({"status": "success"})
        else:
            return jsonify({"error": "Failed to update feedback"}), 500
    
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/personalization/user_weights/<int:user_id>', methods=['GET'])
def get_user_weights(user_id: int):
    """
    Endpoint pour obtenir les poids personnalisés d'un utilisateur
    """
    try:
        matcher = get_matcher()
        weights = matcher.weight_manager.get_user_weights(user_id)
        
        if weights:
            return jsonify({
                "attribute_weights": weights.attribute_weights,
                "category_modifiers": weights.category_modifiers
            })
        else:
            return jsonify({"error": "User weights not found"}), 404
    
    except Exception as e:
        logger.error(f"Error getting user weights: {e}")
        return jsonify({"error": str(e)}), 500

def _get_base_candidates(user_id: int, limit: int) -> List[Dict[str, Any]]:
    """
    Récupère les candidats de base depuis la base de données
    """
    db = get_db()
    cursor = db.cursor()
    
    # Cette requête doit être adaptée à votre schéma de base de données
    query = """
    SELECT c.id, c.name, c.age, c.gender, c.location, c.interests, c.category,
           c.created_at, c.last_activity
    FROM candidates c
    JOIN candidate_visibility cv ON c.id = cv.candidate_id
    WHERE cv.visible = TRUE
    AND c.id != %s
    LIMIT %s
    """
    
    cursor.execute(query, (user_id, limit))
    candidates = cursor.fetchall()
    
    # Convertir les objets de base de données en dictionnaires
    result = []
    for candidate in candidates:
        result.append(dict(candidate))
    
    return result

if __name__ == '__main__':
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Démarrer le serveur
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
