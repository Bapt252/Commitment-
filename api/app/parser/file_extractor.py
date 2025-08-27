"""Module pour extraire le texte de différents formats de fichiers."""
import io
import PyPDF2
from docx import Document

async def extract_text_from_file(file_content, file_extension):
    """
    Extrait le texte d'un fichier selon son extension.
    
    Args:
        file_content: Contenu binaire du fichier
        file_extension: Extension du fichier (pdf, docx, txt)
        
    Returns:
        str: Texte extrait du fichier
    """
    try:
        if file_extension.lower() == 'pdf':
            return extract_from_pdf(file_content)
        elif file_extension.lower() in ['docx', 'doc']:
            return extract_from_docx(file_content)
        elif file_extension.lower() == 'txt':
            return file_content.decode('utf-8', errors='ignore')
        else:
            raise ValueError(f"Format de fichier non supporté: {file_extension}")
    except Exception as e:
        raise Exception(f"Erreur d'extraction du fichier: {str(e)}")

def extract_from_pdf(content):
    """Extrait le texte d'un fichier PDF."""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Erreur d'extraction PDF: {str(e)}")

def extract_from_docx(content):
    """Extrait le texte d'un fichier DOCX."""
    text = ""
    try:
        doc = Document(io.BytesIO(content))
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Erreur d'extraction DOCX: {str(e)}")