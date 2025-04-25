"""
Worker RQ pour le service de parsing CV.
Gère l'exécution asynchrone des tâches de parsing avec gestion avancée des signaux.
"""
# Import du module de compatibilité OpenAI
import compat

import os
import sys
import signal
import logging
from redis import Redis
from rq import Worker, Queue, Connection
from app.core.config import settings
from app.core.logging import setup_logging

# Configuration du logging
setup_logging()
logger = logging.getLogger("cv-parser-worker")

class GracefulKiller:
    """Gestionnaire de signaux pour l'arrêt propre du worker."""
    kill_now = False
    
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
    
    def exit_gracefully(self, signum, frame):
        logger.info(f"Signal {signum} reçu, arrêt propre du worker...")
        self.kill_now = True

def run_worker():
    """Point d'entrée principal du worker RQ."""
    # Connexion Redis
    redis_conn = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=False  # Important pour RQ
    )
    
    # Configuration des queues avec priorités
    queue_names = ['cv_parsing_premium', 'cv_parsing_standard', 'cv_parsing_batch']
    logger.info(f"Démarrage du worker pour les queues: {', '.join(queue_names)}")
    
    # Configuration des timeouts par défaut
    default_config = {
        'default_timeout': 600,  # 10 minutes
        'result_ttl': 3600,      # 1 heure
        'failure_ttl': 86400     # 24 heures
    }
    
    # Créer les queues avec leur configuration
    queues = []
    for queue_name in queue_names:
        queue = Queue(
            name=queue_name,
            connection=redis_conn,
            default_timeout=default_config['default_timeout'],
            failure_ttl=default_config['failure_ttl']
        )
        queues.append(queue)
    
    # Gestionnaire de signaux
    killer = GracefulKiller()
    
    # Configuration du worker
    with Connection(redis_conn):
        worker = Worker(
            queues=queues,  # Surveille les trois queues
            connection=redis_conn,
            default_result_ttl=default_config['result_ttl']
        )
        
        # Démarrer le worker avec gestion des signaux
        try:
            worker.work(
                burst=False,
                with_scheduler=True,
                logging_level=settings.LOG_LEVEL
            )
        except Exception as e:
            logger.error(f"Erreur dans le worker: {e}")
            sys.exit(1)
        finally:
            if killer.kill_now:
                logger.info("Worker arrêté proprement")
            else:
                logger.warning("Worker arrêté de manière inattendue")

if __name__ == "__main__":
    run_worker()