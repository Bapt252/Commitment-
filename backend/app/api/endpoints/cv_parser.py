from fastapi import APIRouter, UploadFile, File, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from app.models.cv import CV
from app.services.cv_parser import cv_parser_service

router = APIRouter()


@router.post("/parse-cv", response_model=CV, summary="Parse un CV au format PDF ou DOCX")
async def parse_cv(file: UploadFile = File(...)):
    """
    Parse un CV au format PDF ou DOCX et extrait les informations pertinentes.
    
    Cet endpoint accepte un fichier CV (PDF ou DOCX) et extrait de façon structurée :
    - Nom
    - Email
    - Téléphone
    - Poste actuel
    - Compétences
    - Expériences professionnelles
    - Formation
    - Connaissances logicielles
    
    Returns:
        CV: Représentation structurée du CV parsé
    """
    if not file.filename:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Aucun fichier fourni"
        )
    
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ["pdf", "docx", "doc"]:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Format de fichier invalide. Seuls les formats PDF et DOCX sont pris en charge."
        )
    
    try:
        cv = await cv_parser_service.parse_cv(file)
        return cv
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du parsing du CV: {str(e)}"
        )
