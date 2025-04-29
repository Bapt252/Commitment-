
# CV Parser Service - Service de parsing CV

import os
import time
import logging
from typing import Dict, Any, Optional, List, BinaryIO
import tempfile
import json

from app.core.config import settings
from app.services.resilience import resilient_openai_call
from app.services.mock_parser import get_mock_cv_data

# Setup logging
logger = logging.getLogger(__name__)

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
    
    try:
        # Si USE_MOCK_PARSER est activé, utiliser le mock au lieu de l'API
        if settings.USE_MOCK_PARSER:
            logger.info(f"Utilisation du mock parser (mode de simulation) pour {file_path}")
            parsed_data = get_mock_cv_data(cv_text, os.path.basename(file_path))
        else:
            # Sinon, utiliser l'API OpenAI
            parsed_data = analyze_cv_with_gpt(cv_text)
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du CV: {str(e)}. Fallback sur le mock parser.")
        # En cas d'erreur, utiliser le mock parser comme fallback
        parsed_data = get_mock_cv_data(cv_text, os.path.basename(file_path))
    
    processing_time = time.time() - start_time
    logger.info(f"CV parsé en {processing_time:.2f} secondes")
    
    # 4. Ajouter des métadonnées au résultat
    result = {
        "processing_time": processing_time,
        "parsed_at": time.time(),
        "file_format": file_format,
        "model": "mock" if settings.USE_MOCK_PARSER else settings.OPENAI_MODEL,
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
    
    # Définir le prompt pour l'extraction d'information structurée avec instructions améliorées
    prompt = f"""
Tu es un assistant spécialisé dans l'extraction d'informations à partir de CV.
Analyse ce CV avec précision et extrait UNIQUEMENT les informations qui sont RÉELLEMENT présentes.

IMPORTANT:
- N'INVENTE JAMAIS d'informations comme "John Doe" ou "johndoe@example.com"
- Si une information n'est pas présente, laisse le champ vide (null ou chaîne vide "")
- Ne génère pas de valeurs par défaut ou fictives
- Sois très précis dans tes extractions

Retourne un objet JSON avec la structure suivante:

{
  "personal_info": {
    "name": "", // Nom complet de la personne (laisse vide si non précisé)
    "email": "", // Email (laisse vide si non présent)
    "phone": "", // Téléphone (laisse vide si non présent)
    "address": "" // Adresse (laisse vide si non présente)
  },
  "position": "", // Poste actuel ou recherché (laisse vide si non précisé)
  "skills": [], // Liste des compétences techniques
  "languages": [
    {
      "language": "", // Langue (ex: Français)
      "level": "" // Niveau (ex: natif, courant, etc.)
    }
  ],
  "experience": [
    {
      "title": "", // Titre du poste
      "company": "", // Nom de l'entreprise
      "start_date": "", // Date de début
      "end_date": "", // Date de fin (ou "Présent")
      "description": "" // Description du poste
    }
  ],
  "education": [
    {
      "degree": "", // Intitulé du diplôme
      "institution": "", // Nom de l'établissement
      "start_date": "", // Date de début
      "end_date": "" // Date de fin
    }
  ]
}

CV à analyser:
{cv_text}

Retourne uniquement un objet JSON valide sans introduction ni commentaire.
"""
    
    try:
        # Appel résilient à OpenAI (avec circuit breaker et retry)
        response_text = resilient_openai_call(
            prompt=prompt, 
            model=settings.OPENAI_MODEL,
            temperature=0.1,
            max_tokens=4000
        )
        
        logger.debug(f"Réponse brute d'OpenAI: {response_text}")
        
        # Parser la réponse JSON
        try:
            # Nettoyage du texte pour s'assurer qu'il ne contient que du JSON
            import re
            json_pattern = r'(\{[\s\S]*\})' 
            match = re.search(json_pattern, response_text)
            if match:
                json_str = match.group(1)
                try:
                    parsed_result = json.loads(json_str)
                    logger.info("Parsing JSON réussi")
                    return parsed_result
                except json.JSONDecodeError as json_err:
                    logger.error(f"Erreur de décodage JSON après extraction: {str(json_err)}")
            
            # Essayer de parser directement si l'extraction a échoué
            parsed_result = json.loads(response_text)
            return parsed_result
            
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON dans la réponse d'OpenAI: {str(e)}")
            
            # Tentative de nettoyage et d'extraction plus agressive
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            clean_text = clean_text.strip()
            
            try:
                return json.loads(clean_text)
            except json.JSONDecodeError:
                logger.error("Échec de la tentative de nettoyage JSON")
                
                # En dernier recours, renvoyer un dictionnaire avec la réponse brute
                return {
                    "error": "Format JSON invalide dans la réponse",
                    "raw_response": response_text[:1000],  # Tronquer pour éviter les réponses trop longues
                    "personal_info": {
                        "name": "",
                        "email": "",
                        "phone": ""
                    },
                    "position": "",
                    "skills": [],
                    "experience": []
                }
    
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du CV avec GPT: {str(e)}")
        raise  # Remonter l'exception pour le fallback
