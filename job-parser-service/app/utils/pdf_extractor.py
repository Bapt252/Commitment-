"""
Module d'extraction de texte PDF amélioré
Ce module fournit des méthodes robustes pour extraire du texte à partir de fichiers PDF,
y compris des PDF complexes ou scannés.
"""

import os
import logging
import io
import re
import tempfile
import subprocess
from typing import Optional, List

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extrait le texte d'un fichier PDF en utilisant plusieurs méthodes
    pour une robustesse maximale.
    
    Args:
        pdf_path: Chemin vers le fichier PDF
        
    Returns:
        str: Texte extrait du PDF
    """
    logger.info(f"Extraction de texte depuis PDF: {pdf_path}")
    
    # Liste des textes extraits par différentes méthodes
    extracted_texts = []
    
    # 1. Extraction avec PyPDF2
    try:
        text_pypdf = _extract_with_pypdf2(pdf_path)
        if text_pypdf and len(text_pypdf) > 100:
            logger.info(f"PyPDF2 a extrait {len(text_pypdf)} caractères")
            extracted_texts.append(text_pypdf)
    except Exception as e:
        logger.warning(f"Échec de l'extraction avec PyPDF2: {str(e)}")
    
    # 2. Extraction avec pdfminer
    try:
        text_pdfminer = _extract_with_pdfminer(pdf_path)
        if text_pdfminer and len(text_pdfminer) > 100:
            logger.info(f"pdfminer a extrait {len(text_pdfminer)} caractères")
            extracted_texts.append(text_pdfminer)
    except Exception as e:
        logger.warning(f"Échec de l'extraction avec pdfminer: {str(e)}")
    
    # 3. Extraction avec pdfplumber
    try:
        text_pdfplumber = _extract_with_pdfplumber(pdf_path)
        if text_pdfplumber and len(text_pdfplumber) > 100:
            logger.info(f"pdfplumber a extrait {len(text_pdfplumber)} caractères")
            extracted_texts.append(text_pdfplumber)
    except Exception as e:
        logger.warning(f"Échec de l'extraction avec pdfplumber: {str(e)}")
    
    # 4. Extraction avec OCR si les autres méthodes échouent ou donnent peu de résultats
    if not extracted_texts or max(len(text) for text in extracted_texts) < 200:
        try:
            text_ocr = _extract_with_ocr(pdf_path)
            if text_ocr and len(text_ocr) > 100:
                logger.info(f"OCR a extrait {len(text_ocr)} caractères")
                extracted_texts.append(text_ocr)
        except Exception as e:
            logger.warning(f"Échec de l'extraction avec OCR: {str(e)}")
    
    # Sélectionner le meilleur texte extrait (le plus long)
    if extracted_texts:
        best_text = max(extracted_texts, key=len)
        
        # Nettoyage du texte extrait
        cleaned_text = _clean_pdf_text(best_text)
        
        logger.info(f"Texte nettoyé: {len(cleaned_text)} caractères")
        return cleaned_text
    else:
        logger.error("Aucune méthode d'extraction n'a réussi")
        return "Échec de l'extraction de texte depuis ce PDF."

def _extract_with_pypdf2(pdf_path: str) -> str:
    """Extrait le texte avec PyPDF2"""
    from PyPDF2 import PdfReader
    
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    
    return text

def _extract_with_pdfminer(pdf_path: str) -> str:
    """Extrait le texte avec pdfminer.six"""
    from pdfminer.high_level import extract_text
    
    text = extract_text(pdf_path)
    return text

def _extract_with_pdfplumber(pdf_path: str) -> str:
    """Extrait le texte avec pdfplumber"""
    import pdfplumber
    
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    
    return text

def _extract_with_ocr(pdf_path: str) -> str:
    """Extrait le texte avec OCR via Tesseract"""
    try:
        import pytesseract
        from pdf2image import convert_from_path
        
        logger.info("Conversion du PDF en images pour OCR")
        
        # Convertir les pages PDF en images
        images = convert_from_path(pdf_path)
        
        text = ""
        for i, image in enumerate(images):
            logger.info(f"OCR de la page {i+1}/{len(images)}")
            page_text = pytesseract.image_to_string(image, lang='fra+eng')
            text += page_text + "\n"
        
        return text
    except ImportError:
        logger.warning("pytesseract ou pdf2image non disponible pour l'OCR")
        
        # Tentative avec OCRmyPDF si disponible
        return _extract_with_ocrmypdf(pdf_path)

def _extract_with_ocrmypdf(pdf_path: str) -> str:
    """Utilise OCRmyPDF comme alternative pour l'OCR"""
    try:
        # Créer un fichier temporaire pour le PDF océrisé
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            output_path = temp_file.name
        
        # Exécuter OCRmyPDF
        subprocess.run(
            ['ocrmypdf', '--force-ocr', '--skip-text', pdf_path, output_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Extraire le texte du PDF océrisé
        from pdfminer.high_level import extract_text
        text = extract_text(output_path)
        
        # Supprimer le fichier temporaire
        os.unlink(output_path)
        
        return text
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logger.warning(f"OCRmyPDF non disponible ou échec: {str(e)}")
        return ""

def _clean_pdf_text(text: str) -> str:
    """
    Nettoie le texte extrait d'un PDF pour supprimer les artefacts
    et améliorer la qualité du texte.
    """
    if not text:
        return ""
    
    # 1. Supprimer les lignes d'entête ou de pied de page PDF (objets PDF)
    lines = text.split('\n')
    cleaned_lines = []
    
    # Filtrer les lignes qui contiennent des artefacts PDF
    pdf_artifacts = [
        r'^\s*\d+\s+\d+\s+obj\b',      # Objets PDF (ex: "1 0 obj")
        r'^\s*endobj\b',               # Fin d'objet
        r'^\s*xref\b',                 # Table de référence
        r'^\s*trailer\b',              # Trailer
        r'^\s*startxref\b',            # Début de xref
        r'^\s*stream\b',               # Début de stream
        r'^\s*endstream\b',            # Fin de stream
        r'^\s*<<',                     # Dictionnaire PDF
        r'^\s*>>',                     # Fin de dictionnaire
        r'^\s*%PDF-\d+\.\d+',          # En-tête PDF
        r'^\s*%\s*[A-F0-9]+\s*$',      # Commentaire hexadécimal
    ]
    
    # Expression pour détecter les numéros de page isolés
    page_number_pattern = r'^\s*\d+\s*$'
    
    for line in lines:
        # Vérifier si la ligne correspond à un artefact PDF
        is_artifact = any(re.match(pattern, line) for pattern in pdf_artifacts)
        
        # Vérifier si c'est juste un numéro de page
        is_page_number = re.match(page_number_pattern, line)
        
        if not is_artifact and not is_page_number:
            cleaned_lines.append(line)
    
    # 2. Supprimer les lignes vides consécutives
    result_lines = []
    prev_empty = False
    
    for line in cleaned_lines:
        if line.strip():
            result_lines.append(line)
            prev_empty = False
        elif not prev_empty:
            result_lines.append(line)
            prev_empty = True
    
    # 3. Supprimer les caractères non imprimables
    text = '\n'.join(result_lines)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    
    # 4. Normaliser les espaces multiples
    text = re.sub(r' +', ' ', text)
    
    # 5. Normaliser les fins de ligne
    text = re.sub(r'\n+', '\n', text)
    
    return text.strip()
