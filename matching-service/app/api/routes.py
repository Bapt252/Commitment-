"""
Routes API pour le service de matching.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Body, Path
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from redis import Redis
import logging

from app.models.matching import (
    MatchingRequest, 
    MatchingResponse, 
    MatchingBulkRequest, 
    MatchingResultResponse,
    MatchingJobStatus,
    QueuePriority
)
from app.core.database import get_db
from app.core.redis import get_redis, enqueue_job, get_job_result, get_job_status
from app.workers.tasks import calculate_matching_score_task
from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/queue-matching", response_model=MatchingResponse)
async def queue_matching(
    matching_request: MatchingRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    priority: QueuePriority = Query(QueuePriority.STANDARD),
    depends_on: Optional[str] = Query(None, description="ID du job dont ce job dépend"),
    user_id: Optional[str] = Query(None, description="ID de l'utilisateur demandant le matching")
):
    """
    Met en file d'attente un calcul de matching entre un candidat et une offre d'emploi
    
    Args:
        matching_request: Requête de matching
        priority: Priorité de la file d'attente
        depends_on: ID du job dont ce job dépend (ex: parsing de CV)
        user_id: ID de l'utilisateur demandant le matching (pour personnalisation)
    
    Returns:
        MatchingResponse: Réponse avec l'ID du job et le statut
    """
    logger.info(f"Mise en file d'attente du calcul de matching pour le candidat {matching_request.candidate_id} et l'offre {matching_request.job_id}")
    
    # Mise en file d'attente du job de calcul de matching
    job_id = enqueue_job(
        redis,
        calculate_matching_score_task,
        args=(matching_request.candidate_id, matching_request.job_id),
        kwargs={"user_id": user_id},
        queue_name=priority,
        job_depends_on=depends_on,
        meta={
            "candidate_id": matching_request.candidate_id,
            "job_id": matching_request.job_id,
            "webhook_url": matching_request.webhook_url,
            "user_id": user_id
        }
    )
    
    return MatchingResponse(
        job_id=job_id,
        status="queued",
        queue=priority,
        message=f"Calcul de matching mis en file d'attente pour le candidat {matching_request.candidate_id} et l'offre {matching_request.job_id}"
    )

@router.post("/queue-matching/bulk", response_model=List[MatchingResponse])
async def queue_matching_bulk(
    bulk_request: MatchingBulkRequest,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
    priority: QueuePriority = Query(QueuePriority.BULK),
    user_id: Optional[str] = Query(None, description="ID de l'utilisateur demandant le matching")
):
    """
    Met en file d'attente plusieurs calculs de matching pour un candidat contre plusieurs offres
    
    Args:
        bulk_request: Requête de matching en masse
        priority: Priorité de la file d'attente
        user_id: ID de l'utilisateur demandant le matching (pour personnalisation)
    
    Returns:
        List[MatchingResponse]: Liste des réponses avec IDs de jobs et statuts
    """
    results = []
    for job_id in bulk_request.job_ids:
        # Création des requêtes de matching individuelles
        job_id = enqueue_job(
            redis,
            calculate_matching_score_task,
            args=(bulk_request.candidate_id, job_id),
            kwargs={"user_id": user_id},
            queue_name=priority,
            meta={
                "candidate_id": bulk_request.candidate_id,
                "job_id": job_id,
                "webhook_url": bulk_request.webhook_url,
                "user_id": user_id
            }
        )
        
        results.append(MatchingResponse(
            job_id=job_id,
            status="queued",
            queue=priority,
            message=f"Calcul de matching mis en file d'attente pour le candidat {bulk_request.candidate_id} et l'offre {job_id}"
        ))
    
    return results

@router.get("/result/{job_id}", response_model=MatchingResultResponse)
async def get_matching_result(
    job_id: str = Path(..., description="ID du job pour lequel obtenir les résultats"),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Récupère le résultat d'un calcul de matching
    
    Args:
        job_id: ID du job
    
    Returns:
        MatchingResultResponse: Résultat du calcul de matching
    """
    status = get_job_status(redis, job_id)
    
    if status == "not_found":
        raise HTTPException(status_code=404, detail=f"Job avec l'ID {job_id} non trouvé")
    
    result = get_job_result(redis, job_id)
    
    return MatchingResultResponse(
        job_id=job_id,
        status=status,
        result=result,
    )

@router.get("/status/{job_id}", response_model=MatchingJobStatus)
async def get_job_status_route(
    job_id: str = Path(..., description="ID du job pour lequel obtenir le statut"),
    redis: Redis = Depends(get_redis),
):
    """
    Récupère le statut d'un job de calcul de matching
    
    Args:
        job_id: ID du job
    
    Returns:
        MatchingJobStatus: Statut du job
    """
    status = get_job_status(redis, job_id)
    
    if status == "not_found":
        raise HTTPException(status_code=404, detail=f"Job avec l'ID {job_id} non trouvé")
    
    return MatchingJobStatus(
        job_id=job_id,
        status=status
    )

@router.post("/record-feedback")
async def record_feedback(
    user_id: str = Query(..., description="ID de l'utilisateur"),
    job_id: Optional[int] = Query(None, description="ID de l'offre d'emploi"),
    candidate_id: Optional[int] = Query(None, description="ID du candidat"),
    action: str = Query(..., description="Type d'action (like, dislike, etc.)"),
    context: Dict[str, Any] = Body({}, description="Contexte du feedback")
):
    """
    Enregistre un feedback utilisateur pour améliorer les recommandations futures
    
    Args:
        user_id: ID de l'utilisateur
        job_id: ID de l'offre d'emploi (optionnel)
        candidate_id: ID du candidat (optionnel)
        action: Type d'action (like, dislike, bookmark, apply, ignore)
        context: Contexte du feedback (source, position, etc.)
    
    Returns:
        Dict: Résultat de l'opération
    """
    if not job_id and not candidate_id:
        raise HTTPException(status_code=400, detail="Au moins un job_id ou candidate_id doit être fourni")
    
    try:
        from app.services.personalization_client import PersonalizationClient
        
        # Envoyer le feedback au service de personnalisation
        personalization_client = PersonalizationClient()
        success = personalization_client.record_feedback(
            user_id=user_id,
            job_id=job_id,
            candidate_id=candidate_id,
            action=action,
            context=context
        )
        
        if success:
            return {"status": "success", "message": "Feedback enregistré avec succès"}
        else:
            return {"status": "warning", "message": "Impossible d'enregistrer le feedback"}
            
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du feedback: {str(e)}", exc_info=True)
        return {"status": "error", "message": "Erreur serveur lors de l'enregistrement du feedback"}
