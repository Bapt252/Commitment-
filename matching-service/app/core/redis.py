"""
Utilitaires pour la gestion de Redis et des jobs RQ.
"""
import uuid
from redis import Redis
from rq import Queue, Dependency
from rq.job import Job
from typing import Any, Dict, List, Optional, Callable, Union
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

def get_redis_connection() -> Redis:
    """Obtient une connexion Redis à partir de l'URL"""
    return Redis.from_url(settings.REDIS_URL)

def get_redis() -> Redis:
    """Dépendance FastAPI pour la connexion Redis"""
    return get_redis_connection()

def enqueue_job(
    redis_conn: Redis,
    func: Callable,
    args: tuple = (),
    kwargs: Dict[str, Any] = None,
    queue_name: str = settings.QUEUE_DEFAULT,
    job_id: str = None,
    job_depends_on: Optional[str] = None,
    meta: Dict[str, Any] = None,
    timeout: int = settings.REDIS_JOB_TIMEOUT,
    ttl: int = settings.REDIS_JOB_TTL,
    retry: int = settings.MAX_RETRIES
) -> str:
    """
    Met un job en file d'attente dans Redis Queue
    
    Args:
        redis_conn: Connexion Redis
        func: Fonction à exécuter
        args: Arguments de la fonction
        kwargs: Arguments nommés de la fonction
        queue_name: Nom de la file d'attente RQ
        job_id: ID personnalisé du job (généré si None)
        job_depends_on: ID du job dont dépend ce job
        meta: Métadonnées du job
        timeout: Timeout d'exécution du job
        ttl: Durée de vie du résultat du job
        retry: Nombre de tentatives
        
    Returns:
        str: ID du job
    """
    queue = Queue(queue_name, connection=redis_conn)
    
    # Génère un ID de job si non fourni
    if job_id is None:
        job_id = str(uuid.uuid4())
    
    # Configure la dépendance de job si nécessaire
    dependency = None
    if job_depends_on:
        dependency = Dependency(redis_conn, job_depends_on)
    
    # Crée les métadonnées avec le statut
    job_meta = meta or {}
    job_meta["status"] = "queued"
    
    # Met le job en file d'attente
    job = queue.enqueue(
        func,
        args=args,
        kwargs=kwargs or {},
        job_id=job_id,
        depends_on=dependency,
        meta=job_meta,
        timeout=timeout,
        result_ttl=ttl,
        retry=retry
    )
    
    logger.info(f"Job {job_id} mis en file d'attente dans la queue {queue_name}")
    return job_id

def get_job_result(redis_conn: Redis, job_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère le résultat d'un job depuis Redis
    
    Args:
        redis_conn: Connexion Redis
        job_id: ID du job
        
    Returns:
        dict: Résultat du job ou None si non disponible
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        return job.result
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du job {job_id}: {str(e)}")
        return None

def get_job_status(redis_conn: Redis, job_id: str) -> str:
    """
    Récupère le statut d'un job depuis Redis
    
    Args:
        redis_conn: Connexion Redis
        job_id: ID du job
        
    Returns:
        str: Statut du job
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        # Vérifie les métadonnées du job pour un statut personnalisé
        if job.meta and "status" in job.meta:
            return job.meta["status"]
            
        # Retourne le statut du job
        if job.is_queued:
            return "queued"
        elif job.is_started:
            return "processing"
        elif job.is_finished:
            return "completed"
        elif job.is_failed:
            return "failed"
        else:
            return "unknown"
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut du job {job_id}: {str(e)}")
        return "not_found"

def update_job_status(redis_conn: Redis, job_id: str, status: str) -> bool:
    """
    Met à jour le statut d'un job dans Redis
    
    Args:
        redis_conn: Connexion Redis
        job_id: ID du job
        status: Nouveau statut
        
    Returns:
        bool: Indicateur de succès
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        job.meta["status"] = status
        job.save_meta()
        logger.debug(f"Statut du job {job_id} mis à jour à {status}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du statut du job {job_id}: {str(e)}")
        return False

def update_job_meta(redis_conn: Redis, job_id: str, meta: Dict[str, Any]) -> bool:
    """
    Met à jour les métadonnées d'un job dans Redis
    
    Args:
        redis_conn: Connexion Redis
        job_id: ID du job
        meta: Métadonnées à mettre à jour
        
    Returns:
        bool: Indicateur de succès
    """
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        for key, value in meta.items():
            job.meta[key] = value
        job.save_meta()
        logger.debug(f"Métadonnées du job {job_id} mises à jour")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des métadonnées du job {job_id}: {str(e)}")
        return False
