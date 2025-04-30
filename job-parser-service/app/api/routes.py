# Job Parser Service - Routes API

import os
import time
import uuid
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Header, BackgroundTasks, Depends, Request
from starlette import status
from typing import Optional, Dict, Any, List
import redis
from rq import Queue
from rq.job import Job

from app.core.config import settings
from app.core.dependencies import validate_api_key, RateLimiter
from app.services.storage import save_temp_file, get_file_from_storage, get_result_multi_tier
from app.utils.validation import validate_job_file, validate_webhook_url
from app.workers.tasks import parse_job_task

# Setup logging
logger = logging.getLogger(__name__)

# Setup Redis connection
redis_conn = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=False
)

# Configuration des priorités et queues
QUEUE_PRIORITIES = {
    "premium": {
        "name": "job_parsing_premium",
        "timeout": 600,  # 10 minutes
        "ttl": 86400,    # 24 heures
        "max_retries": 5
    },
    "standard": {
        "name": "job_parsing_standard",
        "timeout": 300,  # 5 minutes
        "ttl": 43200,    # 12 heures
        "max_retries": 3
    },
    "batch": {
        "name": "job_parsing_batch",
        "timeout": 1800,  # 30 minutes
        "ttl": 172800,   # 48 heures
        "max_retries": 2
    }
}

# Créer les queues
queues = {}
for priority, config in QUEUE_PRIORITIES.items():
    queues[priority] = Queue(config["name"], connection=redis_conn)

# Créer le router FastAPI
router = APIRouter()

# Fonctions utilitaires
def get_estimated_wait_time(priority: str) -> str:
    """Estime le temps d'attente en fonction de la priorité et des jobs en attente"""
    try:
        queue = queues.get(priority)
        if not queue:
            return "inconnu"
            
        count = queue.count
        
        # Logique simplifiée d'estimation
        if priority == "premium":
            return f"{max(count * 2, 5)}s" if count > 0 else "immédiat"
        elif priority == "standard":
            return f"{max(count * 5, 30)}s" if count > 0 else "30s"
        else:  # batch
            return f"{max(count * 10, 60)}s" if count > 0 else "60s"
    except Exception as e:
        logger.error(f"Erreur lors de l'estimation du temps d'attente: {e}")
        return "inconnu"

@router.post("/queue", status_code=status.HTTP_202_ACCEPTED)
async def queue_job_parsing(
    request: Request,
    file: UploadFile = File(...),
    priority: str = Query("standard", enum=list(QUEUE_PRIORITIES.keys())),
    webhook_url: Optional[str] = Query(None, description="URL pour notification de fin de traitement"),
    webhook_secret: Optional[str] = Query(None, description="Secret pour signer le webhook"),
    api_key: Optional[str] = Header(None, description="Clé API pour authentification"),
    rate_limiter: bool = Depends(RateLimiter(limit=10, window=60)),  # 10 req/min
):
    """File d'attente pour le parsing de fiche de poste - Traitement asynchrone"""
    
    # 1. Valider l'API key si configureée
    if settings.REQUIRE_API_KEY:
        validate_api_key(api_key)
    
    try:
        # 2. Générer un ID unique pour le job
        job_id = str(uuid.uuid4())
        
        # 3. Valider le fichier (taille, type, signature, etc.)
        await validate_job_file(file)
        
        # 4. Valider l'URL de webhook si fournie
        if webhook_url:
            webhook_url = validate_webhook_url(webhook_url)
        
        # 5. Enregistrer le fichier dans le stockage temporaire (MinIO ou local)
        file_path = await save_temp_file(file, job_id)
        
        # 6. Obtenir la configuration de queue selon la priorité
        queue_config = QUEUE_PRIORITIES[priority]
        queue = queues[priority]
        
        # 7. Enregistrer les informations de webhook si fournies
        if webhook_url:
            redis_conn.hset(
                f"job:webhook:{job_id}",
                mapping={
                    "url": webhook_url,
                    "secret": webhook_secret or "",
                    "created_at": time.time()
                }
            )
            redis_conn.expire(f"job:webhook:{job_id}", queue_config["ttl"])
        
        # 8. Enqueue le job - Avec tous les arguments nommés pour éviter les confusions
        job = queue.enqueue(
            parse_job_task,
            kwargs={
                "job_id": job_id,
                "file_path": file_path,
                "file_name": file.filename,
                "file_format": os.path.splitext(file.filename)[1].lower(),
                "max_retries": queue_config["max_retries"],
                "webhook_url": webhook_url,
                "webhook_secret": webhook_secret
            },
            job_timeout=queue_config["timeout"],
            result_ttl=queue_config["ttl"],
            failure_ttl=queue_config["ttl"],
            ttl=queue_config["ttl"]
        )
        
        # 9. Enregistrer les métadonnées du job
        redis_conn.hset(
            f"job:meta:{job_id}",
            mapping={
                "priority": priority,
                "filename": file.filename,
                "content_type": file.content_type,
                "size": file.size if hasattr(file, "size") else 0,
                "queued_at": time.time(),
                "queue": queue_config["name"],
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent", "")
            }
        )
        redis_conn.expire(f"job:meta:{job_id}", queue_config["ttl"])
        
        logger.info(f"Job de parsing de fiche de poste {job_id} mis en queue avec priorité {priority}")
        
        # 10. Retourner la réponse
        return {
            "job_id": job_id,
            "status": "queued",
            "priority": priority,
            "estimated_wait": get_estimated_wait_time(priority),
            "webhook_configured": webhook_url is not None
        }
        
    except ValueError as e:
        # Erreurs de validation
        logger.warning(f"Erreur de validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Erreurs inattendues
        logger.error(f"Erreur lors de la mise en queue du job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise en queue du job: {str(e)}"
        )

@router.get("/result/{job_id}", status_code=status.HTTP_200_OK)
async def get_parsing_result(
    job_id: str,
    api_key: Optional[str] = Header(None, description="Clé API pour authentification"),
):
    """Récupérer le résultat d'un job de parsing de fiche de poste"""
    
    # Valider l'API key si configurée
    if settings.REQUIRE_API_KEY:
        validate_api_key(api_key)
    
    try:
        # 1. Essayer de récupérer le job depuis Redis RQ
        try:
            job = Job.fetch(job_id, connection=redis_conn)
            
            # 2. Vérifier le statut du job
            if job.is_finished:
                # Job terminé avec succès
                result = await get_result_multi_tier(job_id)
                return {
                    "status": "done",
                    "job_id": job_id,
                    "result": result,
                    "completed_at": job.ended_at.isoformat() if job.ended_at else None
                }
                
            elif job.is_failed:
                # Job en échec
                error_message = str(job.exc_info) if job.exc_info else "Erreur inconnue"
                return {
                    "status": "failed",
                    "job_id": job_id,
                    "error": error_message,
                    "failed_at": job.ended_at.isoformat() if job.ended_at else None
                }
                
            elif job.is_started:
                # Job en cours d'exécution
                return {
                    "status": "running",
                    "job_id": job_id,
                    "started_at": job.started_at.isoformat() if job.started_at else None
                }
                
            else:
                # Job en attente
                queue_position = job.get_position()
                return {
                    "status": "pending",
                    "job_id": job_id,
                    "enqueued_at": job.enqueued_at.isoformat() if job.enqueued_at else None,
                    "position_in_queue": queue_position
                }
                
        except Exception as e:
            # Le job n'existe pas dans RQ, vérifier s'il est déjà terminé et stocké
            if "No such job" in str(e):
                # 3. Vérifier dans notre stockage multi-tier
                result = await get_result_multi_tier(job_id)
                
                if result:
                    # Résultat trouvé dans le stockage persistant
                    return {
                        "status": "done",
                        "job_id": job_id,
                        "result": result,
                        "note": "Résultat récupéré depuis le stockage permanent"
                    }
                else:
                    # Aucun résultat trouvé
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Aucun job ou résultat trouvé pour l'ID: {job_id}"
                    )
            else:
                # Autre erreur Redis
                logger.error(f"Erreur Redis lors de la récupération du job {job_id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Erreur lors de la récupération du job: {str(e)}"
                )
                
    except HTTPException:
        # On laisse les HTTPException se propager
        raise
        
    except Exception as e:
        # Erreurs inattendues
        logger.error(f"Erreur lors de la récupération du résultat pour job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération du résultat: {str(e)}"
        )