from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_flask_exporter import PrometheusMetrics

from config import config
from app.utils.db import setup_db

# Initialisation des extensions
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
metrics = PrometheusMetrics()

def create_app(config_name='default'):
    """Fonction de fabrique d'application Flask."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialiser les extensions
    CORS(app)
    jwt.init_app(app)
    limiter.init_app(app)
    metrics.init_app(app)
    
    # Configurer la base de données
    setup_db(app)
    
    # Enregistrer les blueprints
    from app.api import blueprint as api_blueprint
    app.register_blueprint(
        api_blueprint,
        url_prefix=app.config['API_PREFIX']
    )
    
    # Gérer les erreurs 404
    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify(error="Not found"), 404

    # Gérer les erreurs 500
    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify(error="Internal server error"), 500

    # Point de terminaison pour le statut de santé
    @app.route('/health')
    def health():
        return jsonify(status="ok")

    # Point de terminaison pour les métriques (déjà fourni par PrometheusMetrics)
    
    return app