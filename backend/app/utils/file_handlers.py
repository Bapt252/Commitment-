import os
import tempfile
from typing import Callable, Any, Optional
from fastapi import UploadFile


async def process_uploaded_file(
    file: UploadFile,
    processor: Callable[[str], Any],
    allowed_extensions: Optional[list] = None
) -> Any:
    """
    Traite un fichier uploadé en le sauvegardant temporairement puis en appliquant
    une fonction de traitement.
    
    Args:
        file: Le fichier uploadé
        processor: La fonction qui traitera le fichier (chemin -> résultat)
        allowed_extensions: Liste des extensions autorisées
        
    Returns:
        Le résultat de la fonction de traitement
    """
    if allowed_extensions:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            allowed_ext_str = ', '.join(allowed_extensions)
            raise ValueError(f"Format de fichier non pris en charge. Extensions autorisées: {allowed_ext_str}")
    
    temp_file_path = None
    try:
        # Sauvegarde dans un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
        
        # Traitement du fichier
        result = processor(temp_file_path)
        return result
    
    finally:
        # Nettoyage du fichier temporaire
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
