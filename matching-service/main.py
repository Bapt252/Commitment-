"""
Point d'entrée principal du service de matching.
Lance le serveur FastAPI avec uvicorn.
"""
import uvicorn
import logging
from app.core.config import settings
from app.core.logging import setup_logging

if __name__ == "__main__":
    # Configuration du logging
    setup_logging()
    logger = logging.getLogger("matching-service")
    
    logger.info(f"Démarrage du serveur FastAPI sur le port {settings.PORT}")
    
    # Démarrage du serveur FastAPI
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
