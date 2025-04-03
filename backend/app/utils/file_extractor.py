from typing import Tuple, Dict, Any
import logging
from app.utils.document_converter import DocumentConverter

# Fonction de compatibilité avec l'API existante
def extract_text_from_file(file_content: bytes, filename: str = None) -> Tuple[str, str]:
    """
    Extrait le texte de différents formats de fichiers (Compatible avec l'API existante)
    
    Args:
        file_content: Contenu binaire du fichier
        filename: Nom du fichier
        
    Returns:
        Tuple: (texte extrait, type mime)
    """
    # Utiliser le nouveau convertisseur amélioré
    text, mime_type, metadata = DocumentConverter.convert_to_text(file_content, filename)
    
    if not text:
        # Journaliser l'échec
        logging.warning(f"Échec d'extraction pour le fichier {filename}: {metadata.get('errors', 'Raison inconnue')}")
        
        # Format non supporté
        if mime_type not in ['text/plain', 'application/pdf', 'application/msword', 
                            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                            'text/html']:
            raise ValueError(f"Format de fichier non supporté: {mime_type}")
        
        # Échec avec format supporté
        raise ValueError(f"Impossible d'extraire le texte du fichier: {filename}")
    
    return text, mime_type

# Les anciennes fonctions sont conservées dans document_converter.py
# pour maintenir une compatibilité maximale si nécessaire
