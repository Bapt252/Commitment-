"""
Initialisation des routes de l'application
"""
import os
import importlib
import pkgutil
import logging
from flask import Blueprint

logger = logging.getLogger(__name__)

def register_routes(app):
    """
    Enregistre toutes les routes définies dans les modules du package
    
    Chaque module doit exposer une fonction register_routes(app)
    """
    
    # Enregistrer les routes spéciales du job parser
    try:
        from app.routes.job_parser import register_routes as register_job_parser_routes
        register_job_parser_routes(app)
        logger.info("Routes du Job Parser enregistrées")
    except ImportError as e:
        logger.warning(f"Impossible d'importer les routes du Job Parser: {e}")
    
    # Trouver tous les autres modules dans le package actuel
    current_dir = os.path.dirname(__file__)
    modules = pkgutil.iter_modules([current_dir])
    
    for _, module_name, _ in modules:
        # Ignorer job_parser car déjà chargé séparément
        if module_name == 'job_parser':
            continue
            
        try:
            # Importer le module et enregistrer ses routes s'il définit register_routes
            module = importlib.import_module(f'app.routes.{module_name}')
            if hasattr(module, 'register_routes'):
                module.register_routes(app)
                logger.info(f"Routes de {module_name} enregistrées")
            elif hasattr(module, 'bp') and isinstance(module.bp, Blueprint):
                app.register_blueprint(module.bp)
                logger.info(f"Blueprint de {module_name} enregistré")
        except Exception as e:
            logger.warning(f"Erreur lors de l'enregistrement des routes du module {module_name}: {e}")
