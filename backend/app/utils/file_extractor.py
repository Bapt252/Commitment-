import os
import tempfile
import magic
from typing import Tuple

# Support pour différents formats de fichiers
def extract_text_from_file(file_content: bytes, filename: str) -> Tuple[str, str]:
    """
    Extrait le texte de différents formats de fichiers
    
    Args:
        file_content: Contenu binaire du fichier
        filename: Nom du fichier
        
    Returns:
        Tuple: (texte extrait, type mime)
    """
    # Détecter le type de fichier
    mime_type = magic.Magic(mime=True).from_buffer(file_content)
    
    # Texte brut
    if mime_type == 'text/plain':
        try:
            return file_content.decode('utf-8'), mime_type
        except UnicodeDecodeError:
            # Essayer d'autres encodages
            try:
                return file_content.decode('latin-1'), mime_type
            except:
                return file_content.decode('cp1252', errors='ignore'), mime_type
    
    # PDF
    elif mime_type == 'application/pdf':
        return extract_text_from_pdf(file_content), mime_type
    
    # Word
    elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        return extract_text_from_word(file_content), mime_type
    
    # Format non supporté
    else:
        raise ValueError(f"Format de fichier non supporté: {mime_type}")

def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extrait le texte d'un fichier PDF
    
    Args:
        file_content: Contenu binaire du fichier PDF
        
    Returns:
        str: Texte extrait
    """
    from pdfminer.high_level import extract_text
    from io import BytesIO
    
    # Utiliser BytesIO pour éviter d'écrire le fichier sur le disque
    with BytesIO(file_content) as pdf_file:
        text = extract_text(pdf_file)
    
    return text

def extract_text_from_word(file_content: bytes) -> str:
    """
    Extrait le texte d'un fichier Word
    
    Args:
        file_content: Contenu binaire du fichier Word
        
    Returns:
        str: Texte extrait
    """
    import docx2txt
    with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name
    
    try:
        text = docx2txt.process(temp_file_path)
        return text
    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)