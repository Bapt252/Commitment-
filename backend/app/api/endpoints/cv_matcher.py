from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.models.cv import CV
from app.models.job import JobPosition
from app.models.matching import MatchingRequest, MatchingResponse, MatchingScore
from app.services.cv_matcher import cv_matcher_service

router = APIRouter()


@router.post("/match-cv", response_model=MatchingResponse, summary="Évalue la correspondance entre un CV et une offre d'emploi")
async def match_cv(request: MatchingRequest):
    """
    Évalue la correspondance entre un CV et une offre d'emploi et retourne un score de matching.
    
    Cet endpoint prend en entrée un CV et une fiche de poste et calcule
    à quel point le candidat correspond aux exigences du poste. Il retourne
    un score détaillé dans différentes catégories :
    - Score global de correspondance
    - Correspondance des compétences
    - Correspondance des connaissances logicielles
    - Correspondance de l'expérience
    - Correspondance de la formation
    
    Il fournit également une analyse détaillée des compétences et logiciels
    qui correspondent et ceux qui manquent.
    
    Returns:
        MatchingResponse: Résultats détaillés du matching
    """
    try:
        # Conversion des dictionnaires en objets modèles
        cv = CV(**request.cv)
        job = JobPosition(**request.job)
        
        # Calcul du matching
        matching_score = cv_matcher_service.match_cv_to_job(cv, job)
        
        return MatchingResponse(matching=matching_score)
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du matching du CV: {str(e)}"
        )
