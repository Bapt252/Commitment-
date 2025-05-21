from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import json
from datetime import datetime
import uuid

# Configuration du logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Activer CORS pour toutes les routes

# Stockage temporaire en mémoire pour les tests
feedbacks = {}

@app.route("/health", methods=["GET"])
def health_check():
    """Endpoint de vérification de santé."""
    return {"status": "healthy", "service": "feedback-service-simplified"}

@app.route("/api/feedback", methods=["POST"])
def collect_feedback():
    """Version simplifiée de la collecte de feedback."""
    data = request.json
    
    if not data or 'content' not in data:
        return jsonify({'error': 'Le contenu du feedback est requis'}), 400
    
    # Créer un ID unique
    feedback_id = str(uuid.uuid4())
    
    # Créer le feedback
    feedback = {
        'id': feedback_id,
        'user_id': data.get('user_id'),
        'content': data.get('content'),
        'source': data.get('source', 'web_app'),
        'type': data.get('type', 'explicit'),
        'rating': data.get('rating'),
        'category': data.get('category'),
        'context': data.get('context', {}),
        'created_at': datetime.now().isoformat()
    }
    
    # Analyser le sentiment (simulation)
    sentiment = {
        'polarity': 0.5,  # Valeur positive simulée
        'subjectivity': 0.6,
        'label': 'positive'
    }
    
    # Extraire les sujets (simulation)
    topics = ["matching", "précision"] if "précis" in data.get('content', '').lower() else []
    
    # Enrichir le feedback
    feedback['sentiment'] = sentiment
    feedback['topics'] = topics
    feedback['satisfaction_score'] = 75  # Score simulé
    
    # Stocker le feedback
    feedbacks[feedback_id] = feedback
    
    logger.info(f"Feedback collecté avec ID: {feedback_id}")
    
    return jsonify({
        'id': feedback_id,
        'status': 'success',
        'sentiment': sentiment,
        'topics': topics,
        'satisfaction_score': 75
    }), 201

@app.route("/api/feedback", methods=["GET"])
def get_feedbacks():
    """Récupère les feedbacks."""
    return jsonify(list(feedbacks.values()))

@app.route("/api/feedback/<feedback_id>", methods=["GET"])
def get_feedback(feedback_id):
    """Récupère un feedback spécifique."""
    if feedback_id not in feedbacks:
        return jsonify({'error': 'Feedback non trouvé'}), 404
    
    return jsonify(feedbacks[feedback_id])

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5058))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    logger.info(f"Démarrage du service de feedback simplifié sur le port {port}, debug={debug}")
    app.run(host="0.0.0.0", port=port, debug=debug)
