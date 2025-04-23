from flask import Flask
from flask_cors import CORS
import os
from config import config

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # Chargement de la configuration
    app.config.from_object(config[config_name])
    
    # Configuration CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Enregistrement des blueprints
    from app.api.routes import api as api_blueprint
    app.register_blueprint(api_blueprint)
    
    # Route de santé
    @app.route('/health')
    def health():
        return {'status': 'ok'}
    
    return app

# Création d'une instance de l'application
app = create_app(os.getenv('FLASK_ENV', 'development'))
