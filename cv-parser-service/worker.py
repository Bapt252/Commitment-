# CV Parser Service - Script de démarrage du worker RQ

import os
import sys
import time
import logging
import redis
from rq import Worker, Queue, Connection

from app.core.config import settings
from app.core.logging import setup_logging

# Setup logging
logger = setup_logging()

# Configuration de connexion Redis
redis_conn = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD or None
)

# Noms des queues à écouter (par ordre de priorité)
QUEUE_NAMES = [
    'cv_parsing_premium',  # Prioritaire
    'cv_parsing_standard',
    'cv_parsing_batch',
    'cv_parsing_failed'    # Dead letter queue
]

def main():
    """Fonction principale de démarrage du worker RQ"""
    try:
        logger.info("Démarrage du worker CV Parser...")
        
        # Vérifier la connexion Redis
        try:
            redis_ping = redis_conn.ping()
            logger.info(f"Test de connexion Redis: {'OK' if redis_ping else 'ÉCHEC'}")
            
            if not redis_ping:
                logger.error("Impossible de se connecter à Redis. Arrêt...")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Erreur lors du test de connexion Redis: {str(e)}")
            sys.exit(1)
        
        # Créer les queues si elles n'existent pas
        for queue_name in QUEUE_NAMES:
            queue = Queue(queue_name, connection=redis_conn)
            logger.info(f"Queue {queue_name} prête: {queue.count} jobs en attente")
        
        # Démarrer le worker
        with Connection(redis_conn):
            worker_name = f"cv_parser_worker_{os.getpid()}"
            
            worker = Worker(
                queues=[Queue(name) for name in QUEUE_NAMES],
                name=worker_name,
                exception_handlers=["default"]
            )
            
            logger.info(f"Worker démarré avec PID {os.getpid()}, écoute sur queues: {', '.join(QUEUE_NAMES)}")
            worker.work(with_scheduler=True)
    
    except KeyboardInterrupt:
        logger.info("Worker arrêté par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erreur du worker: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
