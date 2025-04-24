# CV Parser Service - Utilitaires de validation

import os
import io
import logging
import re
from urllib.parse import urlparse
from typing import Dict, Any, Optional, List, BinaryIO

from fastapi import UploadFile, HTTPException
from starlette import status

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Import optionnels (selon disponibilité)
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("python-magic non disponible, la validation des types de fichiers sera limitée")

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 non disponible, la validation des PDF sera limitée")

async def validate_cv_file(file: UploadFile) -> bool:
    """Validation approfondie d'un fichier CV
    
    Vérifie:
    - Extension de fichier
    - Type MIME (si python-magic disponible)
    - Taille
    - Signature de fichier
    - Structure de fichier (pour PDF si PyPDF2 disponible)
    
    Args:
        file: Fichier téléchargé
        
    Returns:
        bool: True si la validation réussit
        
    Raises:
        HTTPException: Si la validation échoue
    """
    # Vérifier l'extension
    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Format de fichier non supporté: {ext}. Formats acceptés: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Vérifier la taille
    content = await file.read()
    file_size = len(content)
    
    if file_size > settings.MAX_CONTENT_LENGTH:
        await file.seek(0)  # Réinitialiser la position
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Fichier trop volumineux: {file_size / (1024 * 1024):.2f}MB. Taille max: {settings.MAX_CONTENT_LENGTH / (1024 * 1024):.0f}MB"
        )
    
    # Réinitialiser le curseur pour lectures ultérieures
    await file.seek(0)
    
    # Vérifier le type MIME avec python-magic si disponible
    if MAGIC_AVAILABLE:
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(content)
        
        # Mappings des extensions vers types MIME attendus
        mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.rtf': 'application/rtf'
        }
        
        # Vérifier si le type MIME correspond à l'extension
        if ext in mime_types and not mime_type.startswith(mime_types[ext].split('/')[0]):
            await file.seek(0)  # Réinitialiser la position
            logger.warning(f"Type MIME mismatch: {mime_type} vs extension {ext}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le type de contenu ({mime_type}) ne correspond pas à l'extension du fichier ({ext})"
            )
    
    # Validation spécifique par type de fichier
    if ext == '.pdf' and PYPDF2_AVAILABLE:
        # Vérifier la signature PDF
        if not content.startswith(b'%PDF-'):
            await file.seek(0)  # Réinitialiser la position
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Signature PDF invalide"
            )
            
        # Vérifier la structure du PDF
        try:
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Vérifier qu'il y a au moins une page
            if len(pdf_reader.pages) < 1:
                await file.seek(0)  # Réinitialiser la position
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="PDF invalide: aucune page trouvée"
                )
                
            # Vérifier si le PDF est chiffré (optionnel - peut être autorisé)
            if pdf_reader.is_encrypted:
                logger.warning(f"PDF chiffré: {filename}")
                # Optionnel: rejeter les PDF chiffrés
                # raise HTTPException(
                #     status_code=status.HTTP_400_BAD_REQUEST,
                #     detail="Les PDF chiffrés ne sont pas acceptés"
                # )
                
        except PyPDF2.errors.PdfReadError as e:
            await file.seek(0)  # Réinitialiser la position
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"PDF corrompu ou invalide: {str(e)}"
            )
            
    # Réinitialiser le curseur pour lectures ultérieures
    await file.seek(0)
    
    logger.info(f"Fichier validé avec succès: {filename} ({file_size / 1024:.1f}KB)")
    return True

def validate_webhook_url(url: str) -> str:
    """Valide une URL de callback webhook
    
    Args:
        url: URL à valider
        
    Returns:
        str: URL validée
        
    Raises:
        ValueError: Si l'URL est invalide
    """
    if not url:
        raise ValueError("URL de webhook vide")
        
    # Valider l'URL
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValueError("URL mal formée")
            
        # Vérifier le protocole (https recommandé)
        if result.scheme not in ["http", "https"]:
            raise ValueError(f"Protocole non supporté: {result.scheme}")
            
        # Avertissement pour HTTP non sécurisé
        if result.scheme == "http":
            logger.warning(f"URL de webhook non sécurisée (HTTP): {url}")
            
        # Vérifier les hôtes interdits (localhost, etc.)
        # Optionnel: liste d'hôtes interdits
        forbidden_hosts = ["localhost", "127.0.0.1", "0.0.0.0", "[::1]"]
        if result.netloc.split(":")[0] in forbidden_hosts:
            raise ValueError(f"Hôte non autorisé: {result.netloc}")
        
        # Optionnel: validation des ports
        if result.port and result.port < 1024:
            logger.warning(f"Port privilégié utilisé ({result.port}) dans l'URL webhook: {url}")
            
        return url
    except Exception as e:
        logger.error(f"Validation webhook URL échouée: {str(e)}")
        raise ValueError(f"URL de webhook invalide: {str(e)}")
