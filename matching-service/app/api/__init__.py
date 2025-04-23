from flask import Blueprint

# Création du blueprint principal
blueprint = Blueprint('api', __name__)

# Import des routes
from app.api.routes import matches, algorithms

# Enregistrer les vues de l'API
from app.api.routes.matches import matches_bp
from app.api.routes.algorithms import algorithms_bp

blueprint.register_blueprint(matches_bp)
blueprint.register_blueprint(algorithms_bp)