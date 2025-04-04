from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from app.ml.questionnaire_analyzer import analyze_questionnaire_responses

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/{questionnaire_id}/analyze", response_model=Dict[str, Any])
async def analyze_responses(
    questionnaire_id: int,
    answers: Dict[str, Any]
):
    """
    Analyse les réponses d'un candidat à un questionnaire.
    Retourne une analyse détaillée avec scores, forces, faiblesses et recommandations.
    """
    try:
        # Vérifier les données reçues
        if not answers or "candidate_id" not in answers or "answers" not in answers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Les données doivent inclure candidate_id et answers"
            )
            
        # Appel au modèle ML pour analyser les réponses
        analysis_result = await analyze_questionnaire_responses(
            questionnaire_id=questionnaire_id,
            candidate_id=answers["candidate_id"],
            answers=answers["answers"]
        )
        
        return analysis_result
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse des réponses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur est survenue lors de l'analyse des réponses: {str(e)}"
        )

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_questionnaire(
    questionnaire: Dict[str, Any]
):
    """
    Crée un nouveau questionnaire.
    """
    try:
        # Vérifier les données minimales
        if "title" not in questionnaire or "questions" not in questionnaire:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le questionnaire doit avoir au minimum un titre et des questions"
            )
        
        # Création en DB (à implémenter)
        # ...
        
        # Retourne le questionnaire créé
        return {
            "id": 1,  # Placeholder
            "title": questionnaire["title"],
            "description": questionnaire.get("description", ""),
            "questions": questionnaire["questions"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erreur lors de la création du questionnaire: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur est survenue lors de la création du questionnaire: {str(e)}"
        )

@router.get("/", response_model=List[Dict[str, Any]])
async def get_questionnaires():
    """
    Récupère la liste des questionnaires.
    """
    # Simuler une liste de questionnaires (à remplacer par une requête DB)
    return [
        {
            "id": 1,
            "title": "Évaluation des compétences techniques",
            "description": "Questionnaire pour évaluer les compétences techniques des candidats",
            "questions": [
                {
                    "id": 1,
                    "text": "Quel est votre niveau en Python?",
                    "type": "rating",
                    "options": ["1", "2", "3", "4", "5"]
                },
                {
                    "id": 2,
                    "text": "Quelles sont vos technologies préférées?",
                    "type": "text"
                }
            ],
            "created_at": "2025-04-01T10:00:00",
            "updated_at": "2025-04-01T10:00:00"
        }
    ]

@router.get("/{questionnaire_id}", response_model=Dict[str, Any])
async def get_questionnaire(questionnaire_id: int):
    """
    Récupère un questionnaire spécifique.
    """
    # Simuler une récupération de questionnaire (à remplacer par une requête DB)
    return {
        "id": questionnaire_id,
        "title": "Évaluation des compétences techniques",
        "description": "Questionnaire pour évaluer les compétences techniques des candidats",
        "questions": [
            {
                "id": 1,
                "text": "Quel est votre niveau en Python?",
                "type": "rating",
                "options": ["1", "2", "3", "4", "5"]
            },
            {
                "id": 2,
                "text": "Quelles sont vos technologies préférées?",
                "type": "text"
            }
        ],
        "created_at": "2025-04-01T10:00:00",
        "updated_at": "2025-04-01T10:00:00"
    }
