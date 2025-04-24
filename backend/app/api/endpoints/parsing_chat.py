from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import tempfile
import os
import uuid
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.services.parsing_service import extract_text_from_file, parse_cv_with_gpt, chat_with_cv_data

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    history: List[Dict[str, str]] = []
    document_data: Dict[str, Any] = {}
    doc_type: str = "cv"

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    doc_type: str = Form("cv")
):
    """Point d'entrée pour télécharger et analyser un CV"""
    try:
        # Vérification du type de document (cv ou autre)
        if doc_type not in ['cv', 'job_description']:
            raise HTTPException(status_code=400, detail="Type de document non supporté")
        
        # Vérification de l'extension du fichier
        file_extension = file.filename.split('.')[-1].lower()
        allowed_extensions = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Type de fichier non autorisé")
        
        # Création d'un fichier temporaire pour stocker le fichier téléchargé
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp:
            temp.write(await file.read())
            temp_path = temp.name
        
        try:
            # Extraction du texte du fichier
            file_content = extract_text_from_file(temp_path, file_extension)
            
            # Analyse du contenu avec GPT selon le type de document
            if doc_type == 'cv':
                result = parse_cv_with_gpt(file_content, file_extension)
            else:
                # Pour d'autres types de documents, à implémenter selon les besoins
                result = {"success": False, "error": "Type de document non implémenté"}
            
            return result
        finally:
            # Nettoyage - suppression du fichier temporaire
            os.unlink(temp_path)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(chat_request: ChatMessage):
    """Point d'entrée pour le chat avec l'IA sur le CV"""
    try:
        # Chat avec l'IA à propos du document
        if chat_request.doc_type == 'cv':
            response = chat_with_cv_data(
                chat_request.message,
                chat_request.history,
                chat_request.document_data
            )
        else:
            # Pour d'autres types de documents, à implémenter selon les besoins
            raise HTTPException(status_code=400, detail="Type de document non supporté pour le chat")
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))