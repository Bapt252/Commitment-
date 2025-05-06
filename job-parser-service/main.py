"""
Point d'entrée principal du service de parsing de fiches de poste.
Lance le serveur FastAPI avec pre-loading des modèles.
"""

import logging
import uvicorn
import os
from preload_models import preload_models

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # 1. Précharger les modèles et dépendances
    try:
        logger.info("Préchargement des modèles et dépendances...")
        preload_models()
        logger.info("Préchargement terminé avec succès")
    except Exception as e:
        logger.error(f"Erreur lors du préchargement des modèles: {str(e)}")
        logger.warning("Le service démarre quand même, mais les premières requêtes peuvent être plus lentes")
    
    # 2. Lancer le serveur FastAPI
    logger.info("Démarrage du serveur...")
    
    # Configuration du serveur
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5053))
    reload = os.environ.get("RELOAD", "").lower() == "true"
    
    logger.info(f"Configuration: host={host}, port={port}, reload={reload}")
    
    # Lancement du serveur
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
