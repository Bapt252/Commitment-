# Utilitaires de validation

import os
import re
import logging
from typing import Optional, List, Dict, Any
from fastapi import UploadFile
import magic

# Setup logging
logger = logging.getLogger(__name__)

# Extensions de fichiers autorisées
ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".txt", ".rtf"
}

# Types MIME autorisés
ALLOWED_MIME_TYPES = {
    "application/pdf",                                                     # PDF
    "application/msword",                                                # DOC
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
    "text/plain",                                                         # TXT
    "application/rtf", "text/rtf"                                        # RTF
}

# Taille maximale de fichier (10 Mo)
MAX_FILE_SIZE = 10 * 1024 * 1024

async def validate_job_file(file: UploadFile) -> bool:
    """Valide un fichier de fiche de poste pour s'assurer qu'il est conforme aux critères de sécurité
    
    Args:
        file: Fichier à valider
        
    Returns:
        bool: True si le fichier est valide
        
    Raises:
        ValueError: Si le fichier ne répond pas aux critères de validation
    """
    # 1. Vérifier si le fichier existe
    if not file:
        raise ValueError("Aucun fichier fourni")
    
    # 2. Vérifier l'extension du fichier
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Extension de fichier non autorisée: {file_extension}. "  
            f"Extensions autorisées: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 3. Vérifier la taille du fichier
    if hasattr(file, "size") and file.size > MAX_FILE_SIZE:
        raise ValueError(
            f"Taille du fichier ({file.size / 1024 / 1024:.2f} Mo) dépasse la limite maximale "
            f"de {MAX_FILE_SIZE / 1024 / 1024} Mo"
        )
    
    # 4. Vérifier le type MIME (peut nécessiter la lecture d'une partie du fichier)
    try:
        # Lire les premiers octets du fichier pour la détection MIME
        current_position = file.tell()  # Sauvegarder la position actuelle
        await file.seek(0)  # Aller au début du fichier
        header = await file.read(2048)  # Lire les premiers octets pour la détection
        await file.seek(current_position)  # Restaurer la position
        
        # Détecter le type MIME avec python-magic
        mime_type = magic.from_buffer(header, mime=True)
        
        if mime_type not in ALLOWED_MIME_TYPES:
            raise ValueError(
                f"Type de fichier non autorisé: {mime_type}. "
                f"Types autorisés: {', '.join(ALLOWED_MIME_TYPES)}"
            )
    except ImportError:
        # Si python-magic n'est pas disponible, on se fie au content_type fourni
        logger.warning("python-magic non disponible, utilisation du content_type")
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise ValueError(
                f"Type de fichier non autorisé: {file.content_type}. "
                f"Types autorisés: {', '.join(ALLOWED_MIME_TYPES)}"
            )
    except Exception as e:
        logger.warning(f"Erreur lors de la vérification du type MIME: {str(e)}")
        # En cas d'erreur, on continue mais on log
    
    logger.info(f"Fichier validé: {file.filename} ({file.content_type})")
    return True

def validate_webhook_url(url: str) -> str:
    """Valide et nettoie une URL de webhook
    
    Args:
        url: URL à valider
        
    Returns:
        str: URL validée et nettoyée
        
    Raises:
        ValueError: Si l'URL n'est pas valide
    """
    # Vérifier que l'URL est non vide
    if not url or not url.strip():
        raise ValueError("URL de webhook vide")
    
    # Nettoyer l'URL
    url = url.strip()
    
    # Vérifier que l'URL commence par http:// ou https://
    if not re.match(r'^https?://', url):
        raise ValueError("L'URL doit commencer par http:// ou https://")
    
    # Vérifier que l'URL est bien formée
    if not re.match(r'^https?://[\w.-]+(:\d+)?(/[\w./()-]*)?$', url):
        raise ValueError("Format d'URL invalide")
    
    # Bloquer les URLs localhost en production (sauf en mode debug)
    from app.core.config import settings
    if not settings.DEBUG and re.search(r'localhost|127\.0\.0\.1', url):
        raise ValueError("Les URLs localhost ne sont pas autorisées en production")
    
    return url
