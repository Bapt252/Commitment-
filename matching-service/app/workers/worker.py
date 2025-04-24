"""
Configuration et démarrage du worker RQ pour le service de matching.
"""
import os
import sys
import logging
from redis import Redis
from rq import Worker, Queue, Connection
from rq.serializers import JSONSerializer
from rq.job import Job
import signal

from app.core.config import settings
from app.core.logging import setup_logging

# Configuration des logs
setup_logging()
logger = logging.getLogger(__name__)

# Classe de worker personnalisée avec monitoring et résilience améliorés
class MatchingWorker(Worker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_job_execution = True
        self.serializer = JSONSerializer()
        
    def execute_job(self, job, queue):
        """Exécution de job avec logging et monitoring améliorés"""
        logger.info(f"Exécution du job {job.id} depuis la queue {queue.name}")
        return super().execute_job(job, queue)
    
    def handle_job_failure(self, job, exc_info):
        """Gestion améliorée des échecs avec option DLQ"""
        logger.error(f"Le job {job.id} a échoué: {str(exc_info[1])}")
        
        # Vérifier si on doit déplacer vers la dead letter queue
        if job.retries_left <= 0:
            # Max retries atteint, déplacement vers la dead letter queue
            dlq = Queue('matching_failed', connection=self.connection)
            job_data = self.serializer.dumps({
                'id': job.id,
                'queue': job.origin,
                'payload': job.args,
                'error': str(exc_info[1])
            })
            dlq.enqueue('process_dead_letter', job_data, job_id=f"dlq:{job.id}")
            logger.warning(f"Job {job.id} déplacé vers la dead letter queue après le nombre maximum de tentatives")
            
        return super().handle_job_failure(job, exc_info)
    
    def register_death(self):
        """Arrêt gracieux du worker"""
        logger.info("Worker s'arrête gracieusement")
        super().register_death()

def setup_worker():
    """Configuration du worker RQ avec gestion des signaux et des priorités de queues"""
    # Configuration de la connexion Redis
    redis_conn = Redis.from_url(settings.REDIS_URL)
    
    # Configuration des queues avec priorités (l'ordre est important)
    queues = [Queue(name, connection=redis_conn) for name in settings.QUEUE_NAMES]
    
    # Gestionnaire de signaux pour arrêt gracieux
    def handle_signal(signum, frame):
        logger.info(f"Signal {signum} reçu. Arrêt du worker...")
        raise SystemExit(0)
    
    # Enregistrement des gestionnaires de signaux
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    # Démarrage du worker avec contexte de connexion
    with Connection(redis_conn):
        worker = MatchingWorker(
            queues,
            name=f"matching_worker_{os.getpid()}",
            default_worker_ttl=600,  # 10 minutes TTL pour les workers
            job_monitoring_interval=30,  # Vérification des jobs toutes les 30 secondes
            default_result_ttl=settings.REDIS_JOB_TTL,
            default_timeout=settings.REDIS_JOB_TIMEOUT
        )
        
        logger.info(f"Worker démarré avec les queues: {', '.join(settings.QUEUE_NAMES)}")
        worker.work(with_scheduler=True)

if __name__ == "__main__":
    setup_worker()
