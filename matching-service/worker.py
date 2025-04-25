"""
Worker RQ pour le service de matching.
Gère l'exécution asynchrone des tâches de matching avec gestion avancée des signaux.
"""
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
logger = logging.getLogger("matching-worker")

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
        decode_responses=True
    )
    
    # Déterminer la queue à écouter
    queue_name = os.getenv('QUEUE_DEFAULT', 'matching_standard')
    logger.info(f"Démarrage du worker pour la queue: {queue_name}")
    
    # Configuration des timeouts par queue
    queue_configs = {
        'matching_high': {
            'default_timeout': 300,  # 5 minutes
            'result_ttl': 3600,      # 1 heure
            'failure_ttl': 86400     # 24 heures
        },
        'matching_standard': {
            'default_timeout': 600,  # 10 minutes
            'result_ttl': 7200,      # 2 heures
            'failure_ttl': 86400     # 24 heures
        },
        'matching_bulk': {
            'default_timeout': 1800, # 30 minutes
            'result_ttl': 86400,     # 24 heures
            'failure_ttl': 86400     # 24 heures
        }
    }
    
    # Appliquer la configuration spécifique à la queue
    config = queue_configs.get(queue_name, queue_configs['matching_standard'])
    
    # Créer la queue avec la configuration
    queue = Queue(
        name=queue_name,
        connection=redis_conn,
        default_timeout=config['default_timeout'],
        failure_ttl=config['failure_ttl']
    )
    
    # Gestionnaire de signaux
    killer = GracefulKiller()
    
    # Configuration du worker
    with Connection(redis_conn):
        worker = Worker(
            queues=[queue],
            connection=redis_conn,
            default_result_ttl=config['result_ttl']
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