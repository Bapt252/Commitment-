from flask import Flask
from flask_cors import CORS
from api.routes import feedback_api
import logging
import os

# Configuration du logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Activer CORS pour toutes les routes

# Enregistrer le blueprint des routes
app.register_blueprint(feedback_api, url_prefix="/api")

@app.route("/health", methods=["GET"])
def health_check():
    """Endpoint de vérification de santé."""
    return {"status": "healthy", "service": "feedback-service"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5058))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    logger.info(f"Démarrage du service de feedback sur le port {port}, debug={debug}")
    app.run(host="0.0.0.0", port=port, debug=debug)
