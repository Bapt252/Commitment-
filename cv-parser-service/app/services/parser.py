# CV Parser Service - Service de parsing CV

import os
import time
import logging
from typing import Dict, Any, Optional, List, BinaryIO
import tempfile
import json

# Import du client OpenAI et des erreurs associées
import openai
from openai import OpenAI

from app.core.config import settings
from app.services.resilience import resilient_openai_call

# Setup logging
logger = logging.getLogger(__name__)

# Initialiser le client OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def parse_cv(file_path: str, file_format: Optional[str] = None) -> Dict[str, Any]:
    """Parse un CV pour en extraire les informations structurées
    
    Args:
        file_path: Chemin vers le fichier CV
        file_format: Format du fichier (.pdf, .docx, etc.)
        
    Returns:
        Dict[str, Any]: Informations structurées extraites du CV
    """
    # 1. Déterminer le format si non fourni
    if not file_format and file_path:
        file_format = os.path.splitext(file_path)[1].lower()
    
    # 2. Extraire le texte du CV selon le format
    cv_text = extract_text_from_file(file_path, file_format)
    
    # 3. Utiliser OpenAI pour analyser le CV
    start_time = time.time()
    
    parsed_data = analyze_cv_with_gpt(cv_text)
    
    processing_time = time.time() - start_time
    logger.info(f"CV parsé en {processing_time:.2f} secondes")
    
    # 4. Ajouter des métadonnées au résultat
    result = {
        "processing_time": processing_time,
        "parsed_at": time.time(),
        "file_format": file_format,
        "model": settings.OPENAI_MODEL,
        "data": parsed_data
    }
    
    return result

def extract_text_from_file(file_path: str, file_format: Optional[str] = None) -> str:
    """Extrait le texte d'un fichier CV
    
    Args:
        file_path: Chemin vers le fichier
        file_format: Format du fichier
        
    Returns:
        str: Texte extrait du CV
    """
    logger.info(f"Extraction du texte depuis {file_path} (format: {file_format})")
    
    # Déterminer le format si non fourni
    if not file_format:
        file_format = os.path.splitext(file_path)[1].lower()
    
    # Extraction selon le format
    if file_format in [".pdf", ".PDF"]:
        return extract_text_from_pdf(file_path)
    elif file_format in [".docx", ".DOCX"]:
        return extract_text_from_docx(file_path)
    elif file_format in [".doc", ".DOC"]:
        return extract_text_from_doc(file_path)
    elif file_format in [".txt", ".TXT", ".text"]:
        return extract_text_from_txt(file_path)
    elif file_format in [".rtf", ".RTF"]:
        return extract_text_from_rtf(file_path)
    else:
        raise ValueError(f"Format de fichier non supporté: {file_format}")

def extract_text_from_pdf(file_path: str) -> str:
    """Extrait le texte d'un fichier PDF"""
    try:
        # Utiliser PyPDF2 ou pdfminer.six selon la disponibilité
        try:
            from PyPDF2 import PdfReader
            
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            # Fallback à pdfminer.six
            from pdfminer.high_level import extract_text
            return extract_text(file_path)
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte PDF: {str(e)}")
        raise

def extract_text_from_docx(file_path: str) -> str:
    """Extrait le texte d'un fichier DOCX"""
    try:
        import docx
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte DOCX: {str(e)}")
        raise

def extract_text_from_doc(file_path: str) -> str:
    """Extrait le texte d'un fichier DOC (ancien format Word)"""
    try:
        # Essayer avec textract (nécessite installation système)
        try:
            import textract
            text = textract.process(file_path).decode('utf-8')
            return text
        except ImportError:
            # Fallback: convertir en texte avec AntipC ou autre outil
            raise NotImplementedError("L'extraction de texte des fichiers DOC n'est pas encore implémentée")
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte DOC: {str(e)}")
        raise

def extract_text_from_txt(file_path: str) -> str:
    """Extrait le texte d'un fichier texte"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Essayer avec des encodages alternatifs
        for encoding in ['latin-1', 'windows-1252', 'iso-8859-1']:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte TXT: {str(e)}")
        raise

def extract_text_from_rtf(file_path: str) -> str:
    """Extrait le texte d'un fichier RTF"""
    try:
        # Essayer avec striprtf
        try:
            from striprtf.striprtf import rtf_to_text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            return rtf_to_text(content)
        except ImportError:
            # Fallback à textract
            import textract
            text = textract.process(file_path).decode('utf-8')
            return text
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte RTF: {str(e)}")
        raise

def analyze_cv_with_gpt(cv_text: str) -> Dict[str, Any]:
    """Analyse un CV avec GPT pour en extraire les informations structurées
    
    Args:
        cv_text: Texte du CV
        
    Returns:
        Dict[str, Any]: Informations structurées extraites du CV
    """
    logger.info(f"Analyse du CV avec {settings.OPENAI_MODEL} (longueur: {len(cv_text)} caractères)")
    
    # Définir le prompt pour l'extraction d'information structurée
    prompt = f"""
Tu es un assistant spécialisé dans l'extraction d'informations à partir de CV.
Extrait les informations suivantes du CV ci-dessous et retourne-les dans un format JSON structuré.

N'invente AUCUNE information. S'il manque une info, laisse le champ vide.
Inclus les catégories suivantes:

1. Informations personnelles (nom, email, téléphone, adresse, nationalité, date de naissance si présente, LinkedIn/site web/profils)
2. Compétences techniques et linguistiques
3. Expériences professionnelles (entreprise, poste, date début, date fin, description)
4. Formation (établissement, diplôme, date début, date fin)
5. Certifications et formations complémentaires
6. Langues et niveau (débutant, intermédiaire, avancé, bilingue, natif)
7. Intérêts et activités extra-professionnelles

CV:
{cv_text}

Retourne uniquement un objet JSON sans introduction ni commentaire.
"""
    
    try:
        # Appel résilient à OpenAI (avec circuit breaker et retry)
        response_text = resilient_openai_call(
            prompt=prompt, 
            model=settings.OPENAI_MODEL,
            temperature=0.1,
            max_tokens=4000
        )
        
        # Parser la réponse JSON
        try:
            parsed_result = json.loads(response_text)
            return parsed_result
        except json.JSONDecodeError:
            logger.error("Erreur de parsing JSON dans la réponse d'OpenAI")
            # Tenter d'extraire le JSON si la réponse contient du texte additionnel
            import re
            json_pattern = r'\{[\s\S]*\}'
            match = re.search(json_pattern, response_text)
            if match:
                json_str = match.group(0)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            # Si l'extraction a échoué, retourner un résultat partiel
            return {
                "error": "Format JSON invalide dans la réponse",
                "raw_response": response_text[:1000]  # Tronquer pour éviter les réponses trop longues
            }
    
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du CV avec GPT: {str(e)}")
        return {
            "error": f"Erreur lors de l'analyse: {str(e)}"
        }
