from fastapi import APIRouter, UploadFile, File, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
from app.services.cv_parser import cv_parser_service
from app.models.cv import CV

router = APIRouter()

@router.post("/parse", response_model=CV, summary="Parse un CV à partir d'un fichier PDF ou DOCX")
async def parse_cv(file: UploadFile = File(...)):
    """
    Parse un CV à partir d'un fichier PDF ou DOCX et extrait les informations pertinentes.
    
    Cet endpoint prend en entrée un fichier CV et renvoie une structure de données
    contenant les informations extraites, notamment :
    - Informations personnelles (nom, email, téléphone)
    - Poste actuel ou recherché
    - Compétences techniques
    - Logiciels maîtrisés
    - Expériences professionnelles
    - Formation
    
    Args:
        file: Fichier CV au format PDF ou DOCX
        
    Returns:
        CV: Objet contenant les informations extraites du CV
    """
    try:
        # Vérifier l'extension du fichier
        if not file.filename or not (file.filename.endswith('.pdf') or 
                                     file.filename.endswith('.docx') or 
                                     file.filename.endswith('.doc')):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Le fichier doit être au format PDF ou DOCX"
            )
        
        # Parse le CV
        parsed_cv = await cv_parser_service.parse_cv(file)
        return parsed_cv
        
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du parsing du CV: {str(e)}"
        )
