# Job Parser Service - Service de parsing de fiches de poste

import os
import time
import logging
from typing import Dict, Any, Optional, List, BinaryIO
import tempfile
import json
import traceback
import re

from app.core.config import settings
from app.services.resilience import resilient_openai_call

# Setup logging
logger = logging.getLogger(__name__)

def parse_job(file_path: str, file_format: Optional[str] = None) -> Dict[str, Any]:
    """Parse une fiche de poste pour en extraire les informations structurées
    
    Args:
        file_path: Chemin vers le fichier de fiche de poste
        file_format: Format du fichier (.pdf, .docx, etc.)
        
    Returns:
        Dict[str, Any]: Informations structurées extraites de la fiche de poste
    """
    # 1. Déterminer le format si non fourni
    if not file_format and file_path:
        file_format = os.path.splitext(file_path)[1].lower()
    
    # Logging du fichier traité pour le debugging
    logger.info(f"Traitement du fichier: {os.path.basename(file_path)} (format: {file_format})")
    
    try:
        # 2. Extraire le texte de la fiche de poste selon le format
        job_text = extract_text_from_file(file_path, file_format)
        
        # Log de la taille du texte extrait pour debug
        logger.info(f"Texte extrait: {len(job_text)} caractères")
        if len(job_text) < 100:  # Si le texte extrait est très court, c'est probablement un problème
            logger.warning(f"Texte extrait très court ({len(job_text)} caractères), possible problème d'extraction")
            logger.debug(f"Contenu extrait: {job_text}")
        
        # Pré-traitement du texte pour améliorer la détection
        job_text = preprocess_job_text(job_text)
        
        # 3. Utiliser OpenAI pour analyser la fiche de poste
        start_time = time.time()
        
        try:
            # Utiliser l'API OpenAI
            parsed_data = analyze_job_with_gpt(job_text)
            
            # Post-traitement pour corriger et enrichir les données
            parsed_data = postprocess_job_data(parsed_data, job_text)
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de la fiche de poste: {str(e)}.")
            logger.error(f"Stacktrace: {traceback.format_exc()}")
            # Créer un dict minimal avec une structure valide
            parsed_data = {
                "title": "",
                "company": "",
                "location": "",
                "contract_type": "",
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": [],
                "requirements": [],
                "benefits": []
            }
        
        processing_time = time.time() - start_time
        logger.info(f"Fiche de poste parsée en {processing_time:.2f} secondes")
        
        # 4. Ajouter des métadonnées au résultat
        result = {
            "processing_time": processing_time,
            "parsed_at": time.time(),
            "file_format": file_format,
            "model": settings.OPENAI_MODEL,
            "data": parsed_data
        }
        
        return result
    except Exception as e:
        logger.error(f"Erreur pendant le parsing de la fiche de poste {os.path.basename(file_path)}: {str(e)}")
        logger.error(f"Stacktrace: {traceback.format_exc()}")
        
        # Retourner un résultat avec l'erreur mais une structure minimale valide
        return {
            "processing_time": 0,
            "parsed_at": time.time(),
            "file_format": file_format,
            "model": "error",
            "error": str(e),
            "data": {
                "title": "",
                "company": "",
                "location": "",
                "contract_type": "",
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": [],
                "requirements": [],
                "benefits": []
            }
        }

def preprocess_job_text(text: str) -> str:
    """Prétraite le texte de la fiche de poste pour améliorer la qualité de l'analyse"""
    if not text:
        return ""
        
    # Remplacer les séquences de plusieurs espaces par un seul
    text = re.sub(r' +', ' ', text)
    
    # Remplacer les séquences de plusieurs lignes vides par une seule
    text = re.sub(r'\n+', '\n', text)
    
    return text

def postprocess_job_data(data: Dict[str, Any], original_text: str) -> Dict[str, Any]:
    """Post-traitement des données extraites pour corriger et enrichir les informations"""
    if not data:
        return {}
    
    # S'assurer que tous les champs requis existent
    required_fields = [
        "title", "company", "location", "contract_type", 
        "required_skills", "preferred_skills", "responsibilities", 
        "requirements", "benefits"
    ]
    
    for field in required_fields:
        if field not in data:
            if field in ["required_skills", "preferred_skills", "responsibilities", "requirements", "benefits"]:
                data[field] = []
            else:
                data[field] = ""
    
    # Extraire le type de contrat s'il n'est pas détecté
    if not data.get("contract_type"):
        contract_type = extract_contract_type(original_text)
        if contract_type:
            data["contract_type"] = contract_type
    
    return data

def extract_contract_type(text: str) -> str:
    """Extrait le type de contrat du texte de la fiche de poste"""
    contract_patterns = [
        r'(?i)\b(CDI|contrat à durée indéterminée)\b',
        r'(?i)\b(CDD|contrat à durée déterminée)\b',
        r'(?i)\b(stage|internship)\b',
        r'(?i)\b(freelance|indépendant)\b',
        r'(?i)\b(alternance|apprentissage)\b',
        r'(?i)\b(temps partiel|part[ -]time)\b',
        r'(?i)\b(temps plein|full[ -]time)\b'
    ]
    
    for pattern in contract_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0).capitalize()
    
    return ""

def extract_text_from_file(file_path: str, file_format: Optional[str] = None) -> str:
    """Extrait le texte d'un fichier
    
    Args:
        file_path: Chemin vers le fichier
        file_format: Format du fichier
        
    Returns:
        str: Texte extrait du fichier
    """
    logger.info(f"Extraction du texte depuis {file_path} (format: {file_format})")
    
    # Déterminer le format si non fourni
    if not file_format:
        file_format = os.path.splitext(file_path)[1].lower()
    
    # Vérifier si le fichier existe pour éviter des erreurs
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier n'existe pas: {file_path}")
    
    # Log de la taille du fichier
    file_size = os.path.getsize(file_path)
    logger.info(f"Taille du fichier: {file_size / 1024:.2f} KB")
    
    # Extraction selon le format avec gestion d'erreur améliorée
    try:
        if file_format.lower() in [".pdf", ".PDF"]:
            from PyPDF2 import PdfReader
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        elif file_format.lower() in [".docx", ".DOCX"]:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        elif file_format.lower() in [".doc", ".DOC"]:
            # Pour les .doc, on peut utiliser antiword si disponible
            try:
                import subprocess
                result = subprocess.run(['antiword', file_path], stdout=subprocess.PIPE)
                return result.stdout.decode('utf-8')
            except:
                # Fallback: tenter d'ouvrir comme un fichier texte
                with open(file_path, 'rb') as f:
                    return f.read().decode('utf-8', errors='ignore')
        elif file_format.lower() in [".txt", ".TXT", ".text"]:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        else:
            # Format non supporté
            logger.warning(f"Format de fichier non supporté: {file_format}")
            # Tentative simple de lecture du fichier comme texte
            with open(file_path, 'rb') as file:
                return file.read().decode('utf-8', errors='ignore')
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte: {str(e)}")
        raise

def analyze_job_with_gpt(job_text: str) -> Dict[str, Any]:
    """Analyse une fiche de poste avec GPT pour en extraire les informations structurées
    
    Args:
        job_text: Texte de la fiche de poste
        
    Returns:
        Dict[str, Any]: Informations structurées extraites de la fiche de poste
    """
    logger.info(f"Analyse de la fiche de poste avec {settings.OPENAI_MODEL} (longueur: {len(job_text)} caractères)")
    
    # Si le texte est vide ou trop court, retourner une structure vide
    if not job_text or len(job_text) < 50:
        logger.warning(f"Texte de fiche de poste trop court ({len(job_text)} caractères), impossible d'analyser")
        return {
            "title": "",
            "company": "",
            "location": "",
            "contract_type": "",
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": [],
            "requirements": [],
            "benefits": []
        }
    
    # Si le texte est trop long, le tronquer pour éviter des problèmes avec l'API
    max_tokens = 15000  # Approximativement 15000 caractères
    if len(job_text) > max_tokens:
        logger.warning(f"Fiche de poste trop longue ({len(job_text)} caractères), troncature à {max_tokens} caractères")
        job_text = job_text[:max_tokens] + "...[texte tronqué]"
    
    # Définir le prompt pour l'extraction d'information structurée
    prompt = f"""
Tu es un expert en analyse de fiches de poste pour l'industrie du recrutement.
Tu dois extraire avec précision toutes les informations importantes d'une fiche de poste.

INSTRUCTIONS IMPÉRATIVES:
1. Extrait UNIQUEMENT les informations réellement présentes dans la fiche de poste.
2. Ne génère JAMAIS d'informations fictives.
3. Pour tout champ non présent dans la fiche de poste, renvoie une valeur vide (chaîne vide ou tableau vide).
4. Sois particulièrement attentif au titre du poste, à l'entreprise, au lieu de travail et au type de contrat.
5. Différencie bien les compétences requises des compétences souhaitées.

EXTRACTION DEMANDÉE:
Retourne un JSON avec cette structure précise et TOUS ces champs, même vides:

{{
  "title": "",           // Titre du poste
  "company": "",        // Nom de l'entreprise
  "location": "",       // Lieu de travail
  "contract_type": "",  // Type de contrat (CDI, CDD, freelance, etc.)
  "required_skills": [  // Compétences requises (obligatoires)
    "Compétence 1",
    "Compétence 2"
  ],
  "preferred_skills": [ // Compétences souhaitées (optionnelles)
    "Compétence A",
    "Compétence B"
  ],
  "responsibilities": [  // Missions et responsabilités
    "Responsabilité 1",
    "Responsabilité 2"
  ],
  "requirements": [     // Prérequis (formation, expérience, etc.)
    "Prérequis 1",
    "Prérequis 2"
  ],
  "benefits": [        // Avantages proposés
    "Avantage 1",
    "Avantage 2"
  ],
  "salary_range": "",  // Fourchette de salaire (si mentionnée)
  "remote_policy": "", // Politique de télétravail (si mentionnée)
  "application_process": "", // Processus de candidature
  "company_description": ""  // Description de l'entreprise
}}

FICHE DE POSTE À ANALYSER:
{job_text}

IMPORTANT: Tu dois retourner UNIQUEMENT le JSON avec toutes les informations récupérées de la fiche de poste, sans aucun texte d'introduction ou commentaire.
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
            try:
                parsed_result = json.loads(response_text)
                return parsed_result
            except json.JSONDecodeError:
                pass
                
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
                
                # En dernier recours, renvoyer un dictionnaire par défaut
                return {
                    "error": "Format JSON invalide dans la réponse",
                    "title": "",
                    "company": "",
                    "location": "",
                    "contract_type": "",
                    "required_skills": [],
                    "preferred_skills": [],
                    "responsibilities": [],
                    "requirements": [],
                    "benefits": []
                }
        except Exception as parse_err:
            logger.error(f"Erreur lors du parsing de la réponse: {str(parse_err)}")
            # Structure de retour par défaut en cas d'erreur
            return {
                "error": f"Erreur de parsing: {str(parse_err)}",
                "title": "",
                "company": "",
                "location": "",
                "contract_type": "",
                "required_skills": [],
                "preferred_skills": [],
                "responsibilities": [],
                "requirements": [],
                "benefits": []
            }
    
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse de la fiche de poste avec GPT: {str(e)}")
        # Structure de retour par défaut en cas d'erreur
        return {
            "error": f"Erreur d'analyse: {str(e)}",
            "title": "",
            "company": "",
            "location": "",
            "contract_type": "",
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": [],
            "requirements": [],
            "benefits": []
        }
