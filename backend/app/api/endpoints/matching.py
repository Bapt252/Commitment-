"""
API pour le système de matching XGBoost avancé.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body

# Import du moteur de matching
from ...nlp.advanced_xgboost_matching import get_matching_engine

# Import des modèles de données (schemas)
from ..schemas.matching import (
    MatchingRequest, CandidateMatchingResponse, JobMatchingResponse,
    DetailedMatchingResponse, CandidateProfile, JobProfile
)

# Création du router
router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/candidates/match", response_model=List[CandidateMatchingResponse])
async def match_candidates(request: MatchingRequest):
    """
    Trouve les candidats les plus pertinents pour une offre d'emploi.
    
    Args:
        request: Requête contenant l'offre d'emploi et les candidats à évaluer
        
    Returns:
        List[CandidateMatchingResponse]: Liste des candidats classés par pertinence
    """
    try:
        # Récupérer le moteur de matching
        matching_engine = get_matching_engine()
        
        # Exécuter le matching
        results = matching_engine.rank_candidates_for_job(
            request.candidates,
            request.job_profile,
            request.limit
        )
        
        if not results:
            return []
        
        return results
    except Exception as e:
        logger.error(f"Erreur lors du matching des candidats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du matching des candidats: {str(e)}"
        )

@router.post("/jobs/match", response_model=List[JobMatchingResponse])
async def match_jobs(request: MatchingRequest):
    """
    Trouve les offres d'emploi les plus pertinentes pour un candidat.
    
    Args:
        request: Requête contenant le profil candidat et les offres à évaluer
        
    Returns:
        List[JobMatchingResponse]: Liste des offres classées par pertinence
    """
    try:
        # Récupérer le moteur de matching
        matching_engine = get_matching_engine()
        
        # Exécuter le matching
        results = matching_engine.rank_jobs_for_candidate(
            request.jobs,
            request.candidate_profile,
            request.limit
        )
        
        if not results:
            return []
        
        return results
    except Exception as e:
        logger.error(f"Erreur lors du matching des offres: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du matching des offres: {str(e)}"
        )

@router.post("/explain", response_model=DetailedMatchingResponse)
async def explain_matching(
    candidate_profile: CandidateProfile,
    job_profile: JobProfile
):
    """
    Génère une explication détaillée du matching entre un candidat et une offre.
    
    Args:
        candidate_profile: Profil du candidat
        job_profile: Profil de l'offre d'emploi
        
    Returns:
        DetailedMatchingResponse: Explication détaillée du matching
    """
    try:
        # Récupérer le moteur de matching
        matching_engine = get_matching_engine()
        
        # Générer l'explication
        explanation = matching_engine.explain_match(
            candidate_profile.model_dump(),
            job_profile.model_dump()
        )
        
        if not explanation:
            raise HTTPException(
                status_code=404,
                detail="Impossible de générer une explication"
            )
        
        return explanation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la génération de l'explication: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la génération de l'explication: {str(e)}"
        )

@router.post("/train", response_model=Dict[str, Any])
async def train_matching_models(
    training_data: Dict[str, Any] = Body(...)
):
    """
    Entraîne les modèles de matching XGBoost avec les données fournies.
    
    Args:
        training_data: Données d'entraînement
        
    Returns:
        Dict[str, Any]: Résultats de l'entraînement
    """
    try:
        # Récupérer le moteur de matching
        matching_engine = get_matching_engine()
        
        # Entraîner les modèles
        results = matching_engine.train_models(training_data)
        
        if not results:
            raise HTTPException(
                status_code=404,
                detail="Échec de l'entraînement des modèles"
            )
        
        return results
    except Exception as e:
        logger.error(f"Erreur lors de l'entraînement des modèles: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'entraînement des modèles: {str(e)}"
        )
