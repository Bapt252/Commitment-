from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from typing import List, Any, Optional
from app.nlp.job_parser import parse_job_description
from pydantic import BaseModel

router = APIRouter()

class JobDescription(BaseModel):
    text: str

class JobDescriptionResponse(BaseModel):
    titre: Optional[str] = None
    experience: Optional[str] = None
    competences: Optional[List[str]] = None
    formation: Optional[Any] = None
    contrat: Optional[str] = None
    localisation: Optional[str] = None
    remuneration: Optional[str] = None
    confidence_scores: Optional[dict] = None

@router.post("/parse", response_model=JobDescriptionResponse)
async def parse_job_posting(job_description: JobDescription):
    """Parse une fiche de poste à partir de texte"""
    try:
        result = parse_job_description(job_description.text)
        
        return {
            **result["extracted_data"],
            "confidence_scores": result["confidence_scores"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du parsing: {str(e)}"
        )

@router.post("/parse-file", response_model=JobDescriptionResponse)
async def parse_job_posting_from_file(file: UploadFile = File(...)):
    """Parse une fiche de poste à partir d'un fichier texte"""
    try:
        content = await file.read()
        text = content.decode("utf-8")
        
        result = parse_job_description(text)
        
        return {
            **result["extracted_data"],
            "confidence_scores": result["confidence_scores"]
        }
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier n'est pas encodé en UTF-8"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du parsing: {str(e)}"
        )

@router.get("/", response_model=List[dict])
def get_jobs():
    """Liste des offres d'emploi"""
    # Cette fonction servirait à récupérer les offres depuis une base de données
    return [{"id": 1, "titre": "Développeur Python"}]