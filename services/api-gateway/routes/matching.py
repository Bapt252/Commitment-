"""
Routes pour le service de matching ML
Redirection vers les 9 algorithmes avec auto-sélection intelligente
"""

from fastapi import APIRouter, Depends, Request, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from routes.auth import get_current_user
from utils.proxy import forward_to_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Modèles Pydantic pour le matching
class MatchingRequest(BaseModel):
    """Requête de matching candidat-poste"""
    candidate_profile: Dict[str, Any]
    job_offer: Dict[str, Any]
    algorithm: Optional[str] = None  # Auto-sélection si None
    weights: Optional[Dict[str, float]] = None
    filters: Optional[Dict[str, Any]] = None

class BatchMatchingRequest(BaseModel):
    """Requête de matching en lot"""
    candidates: List[Dict[str, Any]]
    jobs: List[Dict[str, Any]]
    algorithm: Optional[str] = None
    max_matches_per_candidate: int = 5
    min_score_threshold: float = 0.5

class MatchingResult(BaseModel):
    """Résultat d'un matching"""
    candidate_id: str
    job_id: str
    overall_score: float
    detailed_scores: Dict[str, float]
    algorithm_used: str
    explanation: str
    recommendations: List[str]

# Routes principales de matching
@router.post("/match")
async def match_candidate_job(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Matcher un candidat avec un poste
    Utilise l'auto-sélection d'algorithme ou l'algorithme spécifié
    """
    try:
        logger.info(f"Matching pour utilisateur {current_user['email']}")
        
        # Lire le body de la requête
        body = await request.body()
        
        # Rediriger vers le service de matching
        response = await forward_to_service(
            service_name="matching",
            path="api/v1/match",
            request=request,
            body=body
        )
        
        logger.info(f"Matching réussi pour {current_user['email']}")
        return response
        
    except Exception as e:
        logger.error(f"Erreur matching: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du matching: {str(e)}")

@router.post("/match/batch")
async def match_batch(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Matching en lot pour plusieurs candidats et postes
    Optimisé pour le traitement massif
    """
    try:
        logger.info(f"Matching batch pour utilisateur {current_user['email']}")
        
        # Vérifier le rôle (seuls recruteurs et admins)
        if current_user.get("role") not in ["recruteur", "admin"]:
            raise HTTPException(
                status_code=403,
                detail="Seuls les recruteurs et admins peuvent faire du matching en lot"
            )
        
        body = await request.body()
        
        response = await forward_to_service(
            service_name="matching",
            path="api/v1/match/batch",
            request=request,
            body=body
        )
        
        logger.info(f"Matching batch réussi pour {current_user['email']}")
        return response
        
    except Exception as e:
        logger.error(f"Erreur matching batch: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du matching batch: {str(e)}")

@router.get("/match/algorithms")
async def get_available_algorithms(current_user: dict = Depends(get_current_user)):
    """Obtenir la liste des algorithmes de matching disponibles"""
    try:
        response = await forward_to_service(
            service_name="matching",
            path="api/v1/algorithms",
            request=Request(scope={"type": "http", "method": "GET"})
        )
        return response
        
    except Exception as e:
        logger.error(f"Erreur récupération algorithmes: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des algorithmes")

@router.post("/match/explain")
async def explain_matching(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Expliquer pourquoi un candidat matche avec un poste
    Analyse détaillée des critères de matching
    """
    try:
        logger.info(f"Explication matching pour utilisateur {current_user['email']}")
        
        body = await request.body()
        
        response = await forward_to_service(
            service_name="matching",
            path="api/v1/explain",
            request=request,
            body=body
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur explication matching: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'explication du matching")

@router.post("/match/recommendations")
async def get_recommendations(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtenir des recommandations d'amélioration pour un candidat
    Suggestions pour améliorer le score de matching
    """
    try:
        logger.info(f"Recommandations pour utilisateur {current_user['email']}")
        
        body = await request.body()
        
        response = await forward_to_service(
            service_name="matching",
            path="api/v1/recommendations",
            request=request,
            body=body
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur recommandations: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la génération des recommandations")

@router.post("/match/similar-jobs")
async def find_similar_jobs(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Trouver des emplois similaires à un poste donné
    Utilise les algorithmes de similarité sémantique
    """
    try:
        logger.info(f"Recherche jobs similaires pour utilisateur {current_user['email']}")
        
        body = await request.body()
        
        response = await forward_to_service(
            service_name="matching",
            path="api/v1/similar-jobs",
            request=request,
            body=body
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur recherche jobs similaires: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche de jobs similaires")

@router.post("/match/similar-candidates")
async def find_similar_candidates(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Trouver des candidats similaires à un profil donné
    Utile pour élargir la recherche de recrutement
    """
    try:
        logger.info(f"Recherche candidats similaires pour utilisateur {current_user['email']}")
        
        # Vérifier le rôle (seuls recruteurs et admins)
        if current_user.get("role") not in ["recruteur", "admin"]:
            raise HTTPException(
                status_code=403,
                detail="Seuls les recruteurs et admins peuvent rechercher des candidats similaires"
            )
        
        body = await request.body()
        
        response = await forward_to_service(
            service_name="matching",
            path="api/v1/similar-candidates",
            request=request,
            body=body
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur recherche candidats similaires: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la recherche de candidats similaires")

# Routes de monitoring et analytics
@router.get("/match/performance")
async def get_matching_performance(current_user: dict = Depends(get_current_user)):
    """Obtenir les métriques de performance du matching"""
    try:
        # Vérifier le rôle admin
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Accès admin requis")
        
        response = await forward_to_service(
            service_name="matching",
            path="api/v1/performance",
            request=Request(scope={"type": "http", "method": "GET"})
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur métriques performance: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des métriques")

@router.get("/match/analytics")
async def get_matching_analytics(current_user: dict = Depends(get_current_user)):
    """Obtenir les analytics détaillées du matching"""
    try:
        # Vérifier le rôle admin ou recruteur
        if current_user.get("role") not in ["recruteur", "admin"]:
            raise HTTPException(status_code=403, detail="Accès recruteur/admin requis")
        
        response = await forward_to_service(
            service_name="matching",
            path="api/v1/analytics",
            request=Request(scope={"type": "http", "method": "GET"})
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur analytics: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des analytics")

@router.post("/match/feedback")
async def submit_matching_feedback(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Soumettre un feedback sur la qualité du matching
    Permet l'amélioration continue des algorithmes
    """
    try:
        logger.info(f"Feedback matching pour utilisateur {current_user['email']}")
        
        body = await request.body()
        
        response = await forward_to_service(
            service_name="matching",
            path="api/v1/feedback",
            request=request,
            body=body
        )
        
        logger.info(f"Feedback soumis avec succès par {current_user['email']}")
        return response
        
    except Exception as e:
        logger.error(f"Erreur soumission feedback: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la soumission du feedback")

@router.post("/match/calibrate")
async def calibrate_algorithms(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Calibrer les algorithmes de matching avec de nouvelles données
    Réservé aux administrateurs
    """
    try:
        # Vérifier le rôle admin
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Accès admin requis")
        
        logger.info(f"Calibration algorithmes par {current_user['email']}")
        
        body = await request.body()
        
        response = await forward_to_service(
            service_name="matching",
            path="api/v1/calibrate",
            request=request,
            body=body
        )
        
        logger.info("Calibration des algorithmes terminée")
        return response
        
    except Exception as e:
        logger.error(f"Erreur calibration: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la calibration")
