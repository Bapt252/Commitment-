"""
API Routes pour le matching bidirectionnel
-----------------------------------------
Endpoints pour le nouveau service de matching bidirectionnel.

Auteur: Claude/Anthropic
Date: 14/05/2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from redis import Redis
import logging

from app.core.database import get_db
from app.core.redis import get_redis, enqueue_job
from app.models.matching import (
    MatchingBidirectionalResponse,
    JobMatchingRequest,
    CandidateMatchingRequest,
    MatchingResultResponse
)
from app.workers.tasks import (
    bidirectional_matching_single_task,
    find_jobs_for_candidate_task,
    find_candidates_for_job_task
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v2", tags=["matching-bidirectional"])

@router.post("/match", response_model=MatchingBidirectionalResponse)
async def queue_bidirectional_matching(
    candidate_id: int = Query(..., description="ID du candidat"),
    job_id: int = Query(..., description="ID de l'offre d'emploi"),
    with_commute_time: bool = Query(True, description="Calculer le temps de trajet"),
    webhook_url: Optional[str] = Query(None, description="URL de webhook pour notification"),
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """
    Met en file d'attente un calcul de matching bidirectionnel entre un candidat et une offre d'emploi.
    Prend en compte le temps de trajet et la mobilité si with_commute_time=True.
    
    Args:
        candidate_id: ID du candidat
        job_id: ID de l'offre d'emploi
        with_commute_time: Utiliser l'API Google Maps pour calculer le temps de trajet
        webhook_url: URL de webhook pour notification des résultats
    
    Returns:
        Réponse avec job_id et statut
    """
    logger.info(f"Mise en file d'attente du calcul de matching bidirectionnel pour candidat={candidate_id}, job={job_id}")
    
    # Enqueue task
    job_id_str = enqueue_job(
        redis,
        bidirectional_matching_single_task,
        args=(candidate_id, job_id, with_commute_time),
        queue_name="matching_high",
        meta={
            "candidate_id": candidate_id,
            "job_id": job_id,
            "webhook_url": webhook_url,
            "with_commute_time": with_commute_time
        }
    )
    
    return MatchingBidirectionalResponse(
        job_id=job_id_str,
        status="queued",
        message=f"Calcul de matching bidirectionnel mis en file d'attente pour candidat={candidate_id}, job={job_id}"
    )

@router.post("/find-jobs", response_model=MatchingBidirectionalResponse)
async def find_jobs_for_candidate(
    request: JobMatchingRequest,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """
    Recherche les meilleures offres d'emploi pour un candidat.
    
    Args:
        request: Paramètres de la recherche
    
    Returns:
        Réponse avec job_id et statut
    """
    logger.info(f"Recherche des meilleures offres pour le candidat {request.candidate_id}")
    
    # Enqueue task
    job_id = enqueue_job(
        redis,
        find_jobs_for_candidate_task,
        args=(request.candidate_id, request.limit, request.min_score, request.with_commute_time),
        queue_name="matching_bulk",
        meta={
            "candidate_id": request.candidate_id,
            "webhook_url": request.webhook_url,
            "with_commute_time": request.with_commute_time
        }
    )
    
    return MatchingBidirectionalResponse(
        job_id=job_id,
        status="queued",
        message=f"Recherche des meilleures offres pour le candidat {request.candidate_id} mise en file d'attente"
    )

@router.post("/find-candidates", response_model=MatchingBidirectionalResponse)
async def find_candidates_for_job(
    request: CandidateMatchingRequest,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """
    Recherche les meilleurs candidats pour une offre d'emploi.
    
    Args:
        request: Paramètres de la recherche
    
    Returns:
        Réponse avec job_id et statut
    """
    logger.info(f"Recherche des meilleurs candidats pour l'offre {request.job_id}")
    
    # Enqueue task
    job_id = enqueue_job(
        redis,
        find_candidates_for_job_task,
        args=(request.job_id, request.limit, request.min_score, request.with_commute_time),
        queue_name="matching_bulk",
        meta={
            "job_id": request.job_id,
            "webhook_url": request.webhook_url,
            "with_commute_time": request.with_commute_time
        }
    )
    
    return MatchingBidirectionalResponse(
        job_id=job_id,
        status="queued",
        message=f"Recherche des meilleurs candidats pour l'offre {request.job_id} mise en file d'attente"
    )
