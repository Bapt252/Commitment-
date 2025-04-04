from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from enum import Enum, auto

from app.ml.feedback_processor import process_feedback

router = APIRouter()

logger = logging.getLogger(__name__)

class FeedbackType(str, Enum):
    JOB_PARSING = "job_parsing"
    MATCHING = "matching"
    QUESTIONNAIRE = "questionnaire"

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback: Dict[str, Any]
):
    """
    Enregistre un feedback pour amélioration continue.
    """
    try:
        # Vérifier les données reçues
        required_fields = ["entity_type", "entity_id", "rating"]
        for field in required_fields:
            if field not in feedback:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Le champ {field} est obligatoire"
                )
        
        # Vérifier que entity_type est valide
        try:
            entity_type = FeedbackType(feedback["entity_type"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"entity_type doit être l'un des suivants: {', '.join([e.value for e in FeedbackType])}"
            )
        
        # Vérifier que rating est entre 1 et 5
        if not isinstance(feedback["rating"], int) or feedback["rating"] < 1 or feedback["rating"] > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="rating doit être un entier entre 1 et 5"
            )
            
        # Traiter le feedback pour améliorer les modèles ML
        await process_feedback(feedback)
        
        # Retourner le feedback créé
        return {
            "id": 1,  # Placeholder
            "entity_type": feedback["entity_type"],
            "entity_id": feedback["entity_id"],
            "rating": feedback["rating"],
            "comments": feedback.get("comments"),
            "submitted_by": feedback.get("submitted_by"),
            "created_at": datetime.now().isoformat()
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement du feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur est survenue lors de l'enregistrement du feedback: {str(e)}"
        )

@router.post("/batch", response_model=List[Dict[str, Any]], status_code=status.HTTP_201_CREATED)
async def create_batch_feedback(
    batch: Dict[str, Any]
):
    """
    Enregistre plusieurs feedbacks en une seule requête.
    """
    try:
        # Vérifier les données reçues
        if "feedbacks" not in batch or not isinstance(batch["feedbacks"], list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La requête doit inclure un tableau 'feedbacks'"
            )
            
        responses = []
        
        for i, feedback in enumerate(batch["feedbacks"]):
            # Vérifier les données de chaque feedback
            required_fields = ["entity_type", "entity_id", "rating"]
            for field in required_fields:
                if field not in feedback:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Le feedback #{i+1} doit inclure le champ {field}"
                    )
            
            # Vérifier que entity_type est valide
            try:
                entity_type = FeedbackType(feedback["entity_type"])
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Le feedback #{i+1} a un entity_type invalide. Valeurs acceptées: {', '.join([e.value for e in FeedbackType])}"
                )
            
            # Vérifier que rating est entre 1 et 5
            if not isinstance(feedback["rating"], int) or feedback["rating"] < 1 or feedback["rating"] > 5:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Le feedback #{i+1} doit avoir un rating entre 1 et 5"
                )
                
            # Traiter le feedback
            await process_feedback(feedback)
            
            # Ajouter à la liste de réponses
            responses.append({
                "id": i + 1,  # Placeholder
                "entity_type": feedback["entity_type"],
                "entity_id": feedback["entity_id"],
                "rating": feedback["rating"],
                "comments": feedback.get("comments"),
                "submitted_by": feedback.get("submitted_by"),
                "created_at": datetime.now().isoformat()
            })
        
        return responses
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement des feedbacks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur est survenue lors de l'enregistrement des feedbacks: {str(e)}"
        )

@router.get("/", response_model=List[Dict[str, Any]])
async def get_feedbacks(
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None
):
    """
    Récupère la liste des feedbacks, avec possibilité de filtrer.
    """
    # Exemple de feedbacks (à remplacer par une requête DB)
    feedbacks = [
        {
            "id": 1,
            "entity_type": "job_parsing",
            "entity_id": 1,
            "rating": 4,
            "comments": "Bonne extraction des compétences mais quelques oublis",
            "submitted_by": "user1@example.com",
            "created_at": "2025-04-01T10:00:00"
        },
        {
            "id": 2,
            "entity_type": "matching",
            "entity_id": 1,
            "rating": 5,
            "comments": "Excellent matching, toutes les recommandations sont pertinentes",
            "submitted_by": "user2@example.com",
            "created_at": "2025-04-02T14:30:00"
        }
    ]
    
    # Appliquer les filtres si fournis
    if entity_type:
        feedbacks = [f for f in feedbacks if f["entity_type"] == entity_type]
    if entity_id is not None:
        feedbacks = [f for f in feedbacks if f["entity_id"] == entity_id]
        
    return feedbacks

@router.get("/{feedback_id}", response_model=Dict[str, Any])
async def get_feedback(feedback_id: int):
    """
    Récupère un feedback spécifique.
    """
    # Exemple de feedback (à remplacer par une requête DB)
    return {
        "id": feedback_id,
        "entity_type": "job_parsing",
        "entity_id": 1,
        "rating": 4,
        "comments": "Bonne extraction des compétences mais quelques oublis",
        "submitted_by": "user1@example.com",
        "created_at": "2025-04-01T10:00:00"
    }

@router.get("/stats", response_model=Dict[str, Any])
async def get_feedback_stats():
    """
    Récupère des statistiques sur les feedbacks.
    """
    # Exemple de statistiques (à remplacer par des calculs réels)
    return {
        "total_feedbacks": 150,
        "average_rating": 4.2,
        "by_entity_type": {
            "job_parsing": {
                "count": 50,
                "average_rating": 4.1
            },
            "matching": {
                "count": 70,
                "average_rating": 4.4
            },
            "questionnaire": {
                "count": 30,
                "average_rating": 3.9
            }
        },
        "trend": {
            "last_30_days": 4.3,
            "previous_30_days": 4.1,
            "evolution": "+0.2"
        }
    }
