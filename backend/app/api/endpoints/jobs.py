from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from typing import List, Any, Optional, Union, Dict
from app.nlp.document_parser import parse_document
from app.utils.file_extractor import extract_text_from_file
from pydantic import BaseModel
import json

router = APIRouter()

class DocumentText(BaseModel):
    text: str

class ParsingResponse(BaseModel):
    doc_type: str
    extracted_data: Dict[str, Any]
    confidence_scores: Dict[str, float]

@router.post("/parse", response_model=ParsingResponse)
async def parse_job_posting(document: DocumentText):
    """
    Parse un document (CV ou fiche de poste) à partir de texte
    """
    try:
        result = parse_document(document.text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du parsing: {str(e)}"
        )

@router.post("/parse-file", response_model=ParsingResponse)
async def parse_from_file(file: UploadFile = File(...)):
    """
    Parse un document (CV ou fiche de poste) à partir d'un fichier
    """
    try:
        content = await file.read()
        
        # Extraire le texte selon le format du fichier
        try:
            text, mime_type = extract_text_from_file(content, file.filename)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        result = parse_document(text)
        # Ajouter des informations sur le fichier source
        result["file_info"] = {
            "filename": file.filename,
            "mime_type": mime_type
        }
        
        return result
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier n'est pas encodable correctement"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du parsing: {str(e)}"
        )

@router.get("/", response_model=List[dict])
def get_jobs():
    """
    Liste des offres d'emploi
    """
    # Cette fonction servirait à récupérer les offres depuis une base de données
    return [{"id": 1, "titre": "Développeur Python"}]