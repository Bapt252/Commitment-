"""
Script d'entrée du worker de matching.
Lance le worker RQ pour traiter les tâches de matching.
"""
import sys
import logging
from app.workers.worker import setup_worker
from app.core.logging import setup_logging

if __name__ == "__main__":
    # Configuration du logging
    setup_logging()
    logger = logging.getLogger("matching-worker")
    
    logger.info("Démarrage du worker de matching")
    
    try:
        # Démarrage du worker RQ
        setup_worker()
    except KeyboardInterrupt:
        logger.info("Worker arrêté manuellement")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erreur lors du démarrage du worker: {str(e)}", exc_info=True)
        sys.exit(1)
