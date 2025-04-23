"""
API endpoints pour le parsing de documents.
"""

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from typing import Optional
import tempfile
import os
import shutil
import uuid
from app.nlp.enhanced_parsing_system import parse_document

router = APIRouter()

@router.post("/parse-document")
async def parse_document_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = Form(...),  # cv, job_posting, company_questionnaire
    use_gpt: Optional[bool] = Form(True)
):
    """
    Parse un document téléchargé (CV, offre d'emploi, questionnaire).
    Utilise GPT par défaut si disponible.
    """
    # Créer un fichier temporaire pour stocker le document
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    
    try:
        # Écrire le contenu du fichier téléchargé dans le fichier temporaire
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()
        
        # Parser le document
        result = parse_document(
            file_path=temp_file.name,
            file_name=file.filename,
            doc_type=doc_type,
            use_gpt=use_gpt
        )
        
        # Ajouter le nettoyage du fichier temporaire aux tâches d'arrière-plan
        background_tasks.add_task(os.unlink, temp_file.name)
        
        return result
    except Exception as e:
        # En cas d'erreur, s'assurer que le fichier temporaire est supprimé
        os.unlink(temp_file.name)
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur lors du parsing: {str(e)}"}
        )

@router.post("/compare-parsing")
async def compare_parsing_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = Form(...)
):
    """
    Parse un document avec et sans GPT pour comparer les résultats.
    """
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    
    try:
        # Écrire le contenu du fichier téléchargé
        shutil.copyfileobj(file.file, temp_file)
        temp_file.close()
        
        # Parser avec GPT
        gpt_result = parse_document(
            file_path=temp_file.name,
            file_name=file.filename,
            doc_type=doc_type,
            use_gpt=True
        )
        
        # Parser sans GPT
        trad_result = parse_document(
            file_path=temp_file.name,
            file_name=file.filename,
            doc_type=doc_type,
            use_gpt=False
        )
        
        # Nettoyer le fichier temporaire
        background_tasks.add_task(os.unlink, temp_file.name)
        
        return {
            "gpt_parsing": gpt_result,
            "traditional_parsing": trad_result
        }
    except Exception as e:
        os.unlink(temp_file.name)
        return JSONResponse(
            status_code=500,
            content={"error": f"Erreur lors du parsing: {str(e)}"}
        )
