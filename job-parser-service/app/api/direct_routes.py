# Job Parser Service - Routes directes pour le parsing de fiches de poste

import os
import time
import tempfile
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Header, BackgroundTasks
from starlette import status
from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.core.dependencies import validate_api_key, RateLimiter
from app.utils.validation import validate_job_file
from app.services.parser import parse_job

# Setup logging
logger = logging.getLogger(__name__)

# Créer le router FastAPI
direct_router = APIRouter()

@direct_router.post("/parse-job", status_code=status.HTTP_200_OK)
async def parse_job_direct(
    file: UploadFile = File(...),
    force_refresh: bool = Query(False, description="Forcer le rafraîchissement du cache"),
    api_key: Optional[str] = Header(None, description="Clé API pour authentification"),
):
    """Parse une fiche de poste directement sans passer par la file d'attente Redis"""
    
    # 1. Valider l'API key si configurée
    if settings.REQUIRE_API_KEY:
        validate_api_key(api_key)
    
    try:
        # 2. Valider le fichier (taille, type, signature, etc.)
        await validate_job_file(file)
        
        # 3. Créer un fichier temporaire
        file_extension = os.path.splitext(file.filename)[1].lower()
        suffix = file_extension if file_extension.startswith('.') else f".{file_extension}"
        
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            # Écrire le contenu du fichier uploadé dans le fichier temporaire
            content = await file.read()
            temp.write(content)
            temp_path = temp.name
        
        try:
            # 4. Parser la fiche de poste directement
            start_time = time.time()
            result = parse_job(temp_path, file_extension)
            processing_time = time.time() - start_time
            
            # 5. Ajouter des métadonnées supplémentaires
            result["file_name"] = file.filename
            result["content_type"] = file.content_type
            result["size"] = len(content)
            result["processing_time"] = processing_time
            
            logger.info(f"Fiche de poste parsée directement en {processing_time:.2f}s: {file.filename}")
            
            return result
            
        finally:
            # 6. Nettoyer le fichier temporaire
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except ValueError as e:
        # Erreurs de validation
        logger.warning(f"Erreur de validation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Erreurs inattendues
        logger.error(f"Erreur lors du parsing direct de la fiche de poste: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du parsing de la fiche de poste: {str(e)}"
        )
