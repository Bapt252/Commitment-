from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.ml.matching_engine import generate_matches

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=List[Dict[str, Any]])
async def create_matching(
    matching_request: Dict[str, Any]
):
    """
    Génère des recommandations de matching entre une fiche de poste et des candidats.
    """
    try:
        # Vérifier les données reçues
        if "job_post_id" not in matching_request:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La requête doit inclure job_post_id"
            )
        
        # Récupérer les paramètres
        job_post_id = matching_request["job_post_id"]
        candidate_ids = matching_request.get("candidate_ids", None)
        min_score = matching_request.get("min_score", 0.0)
        
        # Si candidate_ids n'est pas fourni, on utilise une liste fictive (à remplacer par une requête DB)
        if not candidate_ids:
            candidate_ids = [1, 2, 3]  # Exemple pour l'API
        
        # Générer les matchings
        matching_results = await generate_matches(
            job_post_id=job_post_id,
            candidate_ids=candidate_ids,
            min_score=min_score
        )
        
        return matching_results
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erreur lors de la génération de matchings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur est survenue lors de la génération de matchings: {str(e)}"
        )

@router.get("/{matching_id}", response_model=Dict[str, Any])
async def get_matching(matching_id: int):
    """
    Récupère un résultat de matching spécifique.
    """
    # Exemple de résultat de matching (à remplacer par une requête DB)
    return {
        "id": matching_id,
        "job_post_id": 1,
        "candidate_id": 2,
        "overall_score": 0.85,
        "score_details": [
            {"category": "skills", "score": 0.9, "explanation": "Compétences techniques correspondantes"},
            {"category": "experience", "score": 0.8, "explanation": "5 ans d'expérience"}
        ],
        "strengths": ["Python", "Machine Learning"],
        "gaps": ["Cloud AWS"],
        "recommendations": ["Formation AWS recommandée"],
        "created_at": "2025-04-01T10:00:00"
    }

@router.get("/job/{job_post_id}", response_model=List[Dict[str, Any]])
async def get_matchings_by_job(
    job_post_id: int,
    min_score: float = 0.0
):
    """
    Récupère tous les matchings pour une fiche de poste spécifique.
    """
    # Exemple de résultats de matching (à remplacer par une requête DB)
    return [
        {
            "id": 1,
            "job_post_id": job_post_id,
            "candidate_id": 1,
            "overall_score": 0.85,
            "score_details": [
                {"category": "skills", "score": 0.9, "explanation": "Compétences techniques correspondantes"},
                {"category": "experience", "score": 0.8, "explanation": "5 ans d'expérience"}
            ],
            "strengths": ["Python", "Machine Learning"],
            "gaps": ["Cloud AWS"],
            "recommendations": ["Formation AWS recommandée"],
            "created_at": "2025-04-01T10:00:00"
        },
        {
            "id": 2,
            "job_post_id": job_post_id,
            "candidate_id": 2,
            "overall_score": 0.75,
            "score_details": [
                {"category": "skills", "score": 0.8, "explanation": "Compétences techniques partielles"},
                {"category": "experience", "score": 0.7, "explanation": "3 ans d'expérience"}
            ],
            "strengths": ["JavaScript", "React"],
            "gaps": ["Python", "Data Science"],
            "recommendations": ["Formation Python recommandée"],
            "created_at": "2025-04-01T10:00:00"
        }
    ]

@router.get("/candidate/{candidate_id}", response_model=List[Dict[str, Any]])
async def get_matchings_by_candidate(
    candidate_id: int,
    min_score: float = 0.0
):
    """
    Récupère tous les matchings pour un candidat spécifique.
    """
    # Exemple de résultats de matching (à remplacer par une requête DB)
    return [
        {
            "id": 1,
            "job_post_id": 1,
            "candidate_id": candidate_id,
            "overall_score": 0.85,
            "score_details": [
                {"category": "skills", "score": 0.9, "explanation": "Compétences techniques correspondantes"},
                {"category": "experience", "score": 0.8, "explanation": "5 ans d'expérience"}
            ],
            "strengths": ["Python", "Machine Learning"],
            "gaps": ["Cloud AWS"],
            "recommendations": ["Formation AWS recommandée"],
            "created_at": "2025-04-01T10:00:00"
        },
        {
            "id": 3,
            "job_post_id": 2,
            "candidate_id": candidate_id,
            "overall_score": 0.65,
            "score_details": [
                {"category": "skills", "score": 0.7, "explanation": "Compétences techniques partielles"},
                {"category": "experience", "score": 0.6, "explanation": "Expérience limitée"}
            ],
            "strengths": ["JavaScript", "UI/UX"],
            "gaps": ["Java", "Backend"],
            "recommendations": ["Formation Java recommandée"],
            "created_at": "2025-04-01T10:00:00"
        }
    ]
