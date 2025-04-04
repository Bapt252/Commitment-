from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

from app.ml.job_parser import parse_job_post
from app.core.errors import handle_exceptions

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_job_post(
    file: Optional[UploadFile] = File(None),
    job_data: Optional[str] = Form(None)
):
    """
    Upload et enregistre une fiche de poste.
    Accepte soit un fichier (PDF, DOCX, etc.), soit des données JSON.
    """
    try:
        if file:
            # Lecture et traitement du fichier
            contents = await file.read()
            job_post_data = await parse_job_post(contents, file.filename)
        elif job_data:
            # Utilisation des données JSON fournies
            import json
            job_post_data = json.loads(job_data)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un fichier ou des données JSON doivent être fournis"
            )

        # Retourner une réponse
        return {
            "id": 1,  # Placeholder, serait remplacé par l'ID généré en DB
            "title": job_post_data.get("title", ""),
            "description": job_post_data.get("description", ""),
            "company": job_post_data.get("company", ""),
            "location": job_post_data.get("location", ""),
            "contract_type": job_post_data.get("contract_type", ""),
            "salary_range": job_post_data.get("salary_range", ""),
            "skills": job_post_data.get("skills", []),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur lors de la création d'une fiche de poste: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur est survenue lors du traitement de la fiche de poste: {str(e)}"
        )

@router.post("/parse", response_model=Dict[str, Any])
async def parse_job_post_endpoint(
    file: UploadFile = File(...)
):
    """
    Parse une fiche de poste sans l'enregistrer en base.
    Retourne les données structurées extraites.
    """
    try:
        contents = await file.read()
        job_post_data = await parse_job_post(contents, file.filename)
        return job_post_data
    except Exception as e:
        logger.error(f"Erreur lors du parsing d'une fiche de poste: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Une erreur est survenue lors du parsing de la fiche de poste: {str(e)}"
        )

@router.get("/", response_model=List[Dict[str, Any]])
async def get_job_posts():
    """
    Récupère la liste des fiches de poste.
    """
    # Simulation d'une liste de fiches de poste (à remplacer par une requête DB)
    return [
        {
            "id": 1,
            "title": "Développeur Full Stack",
            "description": "Poste de développeur full stack...",
            "company": "Tech Company",
            "location": "Paris",
            "contract_type": "CDI",
            "salary_range": "45K-55K",
            "skills": ["Python", "JavaScript", "React"],
            "created_at": "2025-04-01T10:00:00",
            "updated_at": "2025-04-01T10:00:00"
        }
    ]

@router.get("/{job_post_id}", response_model=Dict[str, Any])
async def get_job_post(job_post_id: int):
    """
    Récupère une fiche de poste spécifique.
    """
    # Simulation d'une requête DB (à remplacer)
    return {
        "id": job_post_id,
        "title": "Développeur Full Stack",
        "description": "Poste de développeur full stack...",
        "company": "Tech Company",
        "location": "Paris",
        "contract_type": "CDI",
        "salary_range": "45K-55K",
        "skills": ["Python", "JavaScript", "React"],
        "created_at": "2025-04-01T10:00:00",
        "updated_at": "2025-04-01T10:00:00"
    }
