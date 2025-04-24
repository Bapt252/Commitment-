"""
Définition des tâches asynchrones pour le service de matching.
"""
import logging
import time
from rq import get_current_job
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.redis import get_redis_connection, update_job_status, update_job_meta
from app.core.resilience import retry_with_backoff, CircuitBreaker
from app.core.config import settings
from app.services.matching import MatchingService
from app.services.notification import NotificationService

logger = logging.getLogger(__name__)

# Circuit breaker pour les opérations de matching
matching_circuit = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30,
    name="matching_circuit"
)

@retry_with_backoff(max_retries=settings.MAX_RETRIES, delay=settings.RETRY_DELAY)
def calculate_matching_score_task(candidate_id: int, job_id: int):
    """
    Tâche de worker pour calculer le score de matching entre un candidat et une offre d'emploi
    
    Args:
        candidate_id: ID du candidat
        job_id: ID de l'offre d'emploi
        
    Returns:
        dict: Résultats du matching avec score et détails
    """
    job = get_current_job()
    redis_conn = get_redis_connection()
    
    try:
        # Mise à jour du statut du job
        update_job_status(redis_conn, job.id, "processing")
        logger.info(f"Démarrage du calcul de matching pour le candidat {candidate_id} et l'offre {job_id} (Job ID: {job.id})")
        
        # Récupération des données du candidat et de l'offre depuis la base de données
        with get_db_session() as db:
            # Utilisation du pattern circuit breaker pour le calcul du matching
            with matching_circuit:
                # Initialisation du service de matching
                matching_service = MatchingService(db)
                
                # Calcul du score de matching
                start_time = time.time()
                matching_result = matching_service.calculate_matching_score(candidate_id, job_id)
                duration = time.time() - start_time
                
                # Journalisation des métriques de performance
                logger.info(f"Calcul de matching terminé en {duration:.2f}s (Job ID: {job.id})")
                
                # Stockage du résultat dans la base de données
                db_result = matching_service.store_matching_result(
                    job.id, 
                    candidate_id, 
                    job_id, 
                    matching_result["score"], 
                    matching_result["details"]
                )
                
                # Mise à jour des métadonnées du job
                update_job_meta(redis_conn, job.id, {
                    "score": matching_result["score"],
                    "db_result_id": db_result.id,
                    "processing_time": duration
                })
        
        # Résultat à retourner (sera stocké dans Redis)
        result = {
            "job_id": job.id,
            "candidate_id": candidate_id,
            "job_posting_id": job_id,
            "score": matching_result["score"],
            "details": matching_result["details"],
            "processing_time": duration
        }
        
        # Mise à jour du statut du job à terminé
        update_job_status(redis_conn, job.id, "completed")
        
        # Envoi de notification webhook si une URL est fournie
        if job.meta.get("webhook_url"):
            notification_service = NotificationService()
            notification_service.send_webhook(
                job.meta.get("webhook_url"),
                {
                    "job_id": job.id,
                    "status": "completed",
                    "result": result
                }
            )
        
        logger.info(f"Calcul de matching terminé avec succès pour le candidat {candidate_id} et l'offre {job_id} (Job ID: {job.id})")
        return result
        
    except Exception as e:
        # Mise à jour du statut du job à échoué
        update_job_status(redis_conn, job.id, "failed")
        
        error_details = {
            "error": str(e),
            "candidate_id": candidate_id,
            "job_id": job_id
        }
        
        # Journalisation de l'erreur
        logger.error(f"Erreur dans le calcul de matching pour le candidat {candidate_id} et l'offre {job_id}: {str(e)}", exc_info=True)
        
        # Envoi de notification webhook sur l'échec si une URL est fournie
        if job.meta.get("webhook_url"):
            notification_service = NotificationService()
            notification_service.send_webhook(
                job.meta.get("webhook_url"),
                {
                    "job_id": job.id,
                    "status": "failed",
                    "error": str(e)
                }
            )
        
        # Lève à nouveau l'exception pour le mécanisme de retry
        raise
