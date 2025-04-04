"""Routes API pour le parsing de fiches de poste et CV."""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
import os

from app.parser.job_parser import parse_job_description
from app.parser.file_extractor import extract_text_from_file

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

class JobTextRequest(BaseModel):
    """Modèle pour la requête d'analyse de texte."""
    text: str = Field(..., description="Texte de la fiche de poste à analyser")

@router.post("/parse")
async def parse_job_text(job_request: JobTextRequest):
    """Endpoint pour analyser un texte de fiche de poste."""
    try:
        if not job_request.text or len(job_request.text) < 10:
            raise HTTPException(status_code=400, detail="Le texte fourni est trop court")
        
        result = parse_job_description(job_request.text)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'analyse: {str(e)}")

@router.post("/parse-file")
async def parse_job_file(file: UploadFile = File(...)):
    """Endpoint pour analyser un fichier de fiche de poste."""
    try:
        # Vérification des extensions autorisées
        allowed_extensions = ['txt', 'pdf', 'docx', 'doc']
        file_extension = file.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Format de fichier non supporté. Extensions acceptées: {', '.join(allowed_extensions)}"
            )
        
        # Lire le contenu du fichier
        file_content = await file.read()
        
        # Vérifier la taille du fichier (max 5MB)
        if len(file_content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Le fichier est trop volumineux (max 5MB)")
        
        # Extraire le texte du fichier
        extracted_text = await extract_text_from_file(file_content, file_extension)
        
        # Analyser le texte extrait
        if not extracted_text or len(extracted_text) < 10:
            raise HTTPException(status_code=400, detail="Impossible d'extraire du texte du fichier ou contenu trop court")
        
        result = parse_job_description(extracted_text)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de traitement du fichier: {str(e)}")