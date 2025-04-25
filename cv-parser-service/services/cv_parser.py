import os
import json
import hashlib
import logging
import time
from typing import Dict, Any, BinaryIO, Optional, Tuple, List, Union

import redis
import openai
from PyPDF2 import PdfReader
from docx import Document
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.models.cv_model import CVModel

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration de l'API OpenAI - Support pour les deux noms de variables
openai.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI")
if not openai.api_key:
    logger.warning("OpenAI API key not found in environment variables. API calls will fail.")

# Configuration Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_EXPIRY = int(os.getenv("REDIS_EXPIRY", 86400 * 30))  # 30 jours par défaut

# Connexion Redis avec gestion d'erreur
try:
    redis_client = redis.Redis(
        host=REDIS_HOST, 
        port=REDIS_PORT, 
        db=REDIS_DB,
        decode_responses=False  # Conserver les données binaires pour le cache
    )
    redis_client.ping()  # Vérifie si la connexion est établie
    logger.info("Connected to Redis successfully")
except redis.ConnectionError as e:
    logger.warning(f"Redis connection failed: {e}. Cache will be disabled.")
    redis_client = None

# Constantes
CACHE_PREFIX = "cv_parse:"
SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc'}

# Prompt système optimisé avec plus de contexte
SYSTEM_PROMPT = """
Tu es un assistant spécialisé dans l'extraction d'informations à partir de CV.
Analyse méticuleusement le texte du CV et extrait les informations suivantes dans un format JSON:

1. nom: Nom de famille du candidat
2. prenom: Prénom du candidat  
3. poste: Intitulé du poste actuel ou recherché
4. adresse: Adresse postale complète si présente
5. competences: Liste des compétences techniques (langages, frameworks, méthodologies)
6. logiciels: Liste des logiciels, outils ou plateformes maîtrisés
7. soft_skills: Liste des compétences non techniques (communication, travail d'équipe, etc.)
8. email: Adresse email du candidat (respecte le format standard)
9. telephone: Numéro de téléphone du candidat (conserve le format présent dans le CV)

Règles importantes:
- Réponds UNIQUEMENT avec un objet JSON valide sans aucun texte avant ou après.
- Si une information est absente, utilise une chaîne vide ou liste vide.
- Pour les listes, extrais tous les éléments pertinents.
- Normalise les numéros de téléphone au format standard français si possible.
- Ignore les en-têtes, pieds de page et autres éléments non pertinents.
- Différencie bien les compétences techniques des soft skills.
- Sois précis et exhaustif dans l'extraction.
"""

class CVParserError(Exception):
    """Exception personnalisée pour les erreurs de parsing de CV"""
    pass

class FileExtractionError(CVParserError):
    """Exception levée quand l'extraction du texte d'un fichier échoue"""
    pass

class OpenAIError(CVParserError):
    """Exception levée quand l'appel à l'API OpenAI échoue"""
    pass

class JSONParsingError(CVParserError):
    """Exception levée quand le parsing du JSON échoue"""
    pass

def calculate_file_hash(file: BinaryIO) -> str:
    """Calcule un hash SHA-256 du contenu du fichier pour l'utiliser comme clé de cache."""
    file.seek(0)
    file_content = file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    file.seek(0)  # Réinitialiser le curseur pour une utilisation ultérieure
    return file_hash

def extract_text_from_pdf(file: BinaryIO) -> str:
    """Extrait le texte d'un fichier PDF."""
    try:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:  # Vérifier que le texte n'est pas None
                text += page_text + "\n"
        
        if not text.strip():
            logger.warning(f"Extracted empty text from PDF file")
            
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise FileExtractionError(f"PDF extraction error: {str(e)}")

def extract_text_from_docx(file: BinaryIO) -> str:
    """Extrait le texte d'un fichier DOCX."""
    try:
        doc = Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            if paragraph.text:  # Vérifier que le texte n'est pas None
                text += paragraph.text + "\n"
        
        # Extraire également le texte des tableaux
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text:
                        text += cell.text + "\n"
        
        if not text.strip():
            logger.warning(f"Extracted empty text from DOCX file")
            
        return text
    except Exception as e:
        logger.error(f"Error extracting text from DOCX: {str(e)}")
        raise FileExtractionError(f"DOCX extraction error: {str(e)}")

def extract_text(file: BinaryIO, file_extension: str) -> str:
    """Extrait le texte d'un fichier selon son extension."""
    # Reset file cursor position to beginning
    file.seek(0)
    
    if file_extension.lower() == '.pdf':
        return extract_text_from_pdf(file)
    elif file_extension.lower() in ['.docx', '.doc']:
        return extract_text_from_docx(file)
    else:
        raise ValueError(f"Format de fichier non supporté: {file_extension}")

def get_cached_result(cache_key: str) -> Optional[Dict[str, Any]]:
    """
    Récupère un résultat mis en cache dans Redis
    
    Args:
        cache_key: Clé de cache
        
    Returns:
        Le résultat en cache si présent, None sinon
    """
    if redis_client is None:
        return None
        
    try:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        return None
    except Exception as e:
        logger.warning(f"Error retrieving from cache: {str(e)}")
        return None

def cache_result(cache_key: str, result: Dict[str, Any]) -> bool:
    """
    Met en cache un résultat dans Redis
    
    Args:
        cache_key: Clé de cache
        result: Résultat à mettre en cache
        
    Returns:
        True si le caching a réussi, False sinon
    """
    if redis_client is None:
        return False
        
    try:
        redis_client.set(
            cache_key,
            json.dumps(result),
            ex=REDIS_EXPIRY
        )
        return True
    except Exception as e:
        logger.warning(f"Error caching result: {str(e)}")
        return False

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(OpenAIError),
    reraise=True
)
def parse_cv_with_openai(cv_text: str) -> Dict[str, Any]:
    """Parse un CV en utilisant l'API OpenAI GPT-4o-mini avec mécanisme de retry."""
    # Vérifier la clé API
    if not openai.api_key:
        raise OpenAIError("La clé API OpenAI n'est pas configurée dans les variables d'environnement.")
    
    # Limiter la taille du texte pour l'API
    max_tokens = 16000  # Limite prudente pour gpt-4o-mini
    if len(cv_text) > max_tokens:
        logger.warning(f"CV text too long ({len(cv_text)} chars), truncating to {max_tokens} chars")
        cv_text = cv_text[:max_tokens]
    
    # Appeler l'API OpenAI
    try:
        start_time = time.time()
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": cv_text}
            ],
            temperature=0.1,  # Température basse pour plus de cohérence
            max_tokens=2000,  # Suffisant pour un JSON détaillé
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        execution_time = time.time() - start_time
        logger.info(f"OpenAI API request completed in {execution_time:.2f} seconds")
        
        # Extraire le contenu de la réponse
        content = response.choices[0].message.content
        
        # Nettoyer le contenu au cas où GPT aurait ajouté des backticks ou commentaires
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            # Essayer d'extraire uniquement la partie JSON si le modèle a inclus d'autres textes
            json_start = content.find('{')
            json_end = content.rfind('}')
            
            if json_start >= 0 and json_end > json_start:
                content = content[json_start:json_end+1]
            
            # Parser le JSON
            data = json.loads(content)
            
            # Vérifier que toutes les clés nécessaires sont présentes
            required_keys = ["nom", "prenom", "poste", "competences", "logiciels", "soft_skills", "email", "telephone", "adresse"]
            for key in required_keys:
                if key not in data:
                    data[key] = [] if key in ["competences", "logiciels", "soft_skills"] else ""
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from OpenAI response: {content}")
            raise JSONParsingError(f"Invalid JSON format: {str(e)}")
            
    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise OpenAIError(f"OpenAI API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in OpenAI call: {str(e)}")
        raise OpenAIError(f"Unexpected error: {str(e)}")

def fallback_extraction(text: str) -> Dict[str, Any]:
    """
    Méthode de secours pour extraire des informations basiques si OpenAI échoue
    Utilise des règles simples basées sur des regex pour obtenir au moins quelques données
    
    Args:
        text: Texte du CV
        
    Returns:
        Un dictionnaire avec les informations de base
    """
    import re
    
    # Structure par défaut
    result = {
        "nom": "",
        "prenom": "",
        "poste": "",
        "adresse": "",
        "competences": [],
        "logiciels": [],
        "soft_skills": [],
        "email": "",
        "telephone": ""
    }
    
    # Extraction d'email (recherche basique)
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    if email_match:
        result["email"] = email_match.group(0)
    
    # Extraction de numéro de téléphone (format français)
    phone_matches = re.findall(r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}', text)
    if phone_matches:
        result["telephone"] = phone_matches[0]
    
    # Extraction de compétences basiques (recherche de mots-clés courants)
    tech_keywords = ['python', 'java', 'javascript', 'html', 'css', 'sql', 'php', 
                    'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring',
                    'c++', 'c#', 'docker', 'kubernetes', 'git', 'aws', 'azure']
    
    software_keywords = ['office', 'excel', 'word', 'powerpoint', 'photoshop', 
                       'illustrator', 'figma', 'sketch', 'jira', 'confluence',
                       'slack', 'trello', 'notion', 'adobe', 'autocad']
    
    soft_skills_keywords = ['communication', 'travail en équipe', 'leadership', 'autonomie',
                           'adaptabilité', 'gestion de projet', 'organisation', 'proactif',
                           'analyse', 'résolution de problèmes', 'créativité']
    
    for keyword in tech_keywords:
        if re.search(r'\b' + keyword + r'\b', text.lower()):
            result["competences"].append(keyword)
    
    for keyword in software_keywords:
        if re.search(r'\b' + keyword + r'\b', text.lower()):
            result["logiciels"].append(keyword)
            
    for keyword in soft_skills_keywords:
        if keyword in text.lower():
            result["soft_skills"].append(keyword)
    
    return result

def parse_cv(file: BinaryIO, filename: str, force_refresh: bool = False) -> Tuple[CVModel, bool]:
    """
    Fonction principale qui parse un CV en utilisant l'API OpenAI avec cache Redis.
    
    Args:
        file: Fichier CV (PDF ou DOCX)
        filename: Nom du fichier avec extension
        force_refresh: Forcer le rafraîchissement du cache
        
    Returns:
        Une tuple (CVModel, from_cache) avec les informations extraites et si elles viennent du cache
        
    Raises:
        CVParserError: Si le parsing du CV échoue
    """
    # Déterminer l'extension du fichier
    _, file_extension = os.path.splitext(filename)
    
    if file_extension.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Format de fichier non supporté: {file_extension}")
    
    # Calculer le hash du fichier pour la clé de cache
    file_hash = calculate_file_hash(file)
    cache_key = f"{CACHE_PREFIX}{file_hash}"
    
    # Vérifier si le résultat est déjà en cache et si on ne force pas le rafraîchissement
    if not force_refresh:
        cached_result = get_cached_result(cache_key)
        if cached_result:
            try:
                logger.info(f"Cache hit for file {filename}")
                # Créer une instance de CVModel avec les données du cache
                cv_model = CVModel(
                    nom=cached_result.get("nom", ""),
                    prenom=cached_result.get("prenom", ""),
                    poste=cached_result.get("poste", ""),
                    competences=cached_result.get("competences", []),
                    logiciels=cached_result.get("logiciels", []),
                    soft_skills=cached_result.get("soft_skills", []),
                    email=cached_result.get("email", ""),
                    telephone=cached_result.get("telephone", ""),
                    adresse=cached_result.get("adresse", "")
                )
                return cv_model, True
            except Exception as e:
                logger.warning(f"Error using cached data: {str(e)}. Will reprocess file.")
    
    # Si pas en cache ou erreur de cache, procéder au traitement
    try:
        # 1. Extraire le texte brut du document
        cv_text = extract_text(file, file_extension)
        
        if not cv_text.strip():
            logger.warning(f"Extracted empty text from file {filename}")
            raise FileExtractionError("Le texte extrait du fichier est vide")
        
        # 2. Tenter d'envoyer le texte à l'API OpenAI
        try:
            cv_data = parse_cv_with_openai(cv_text)
        except (OpenAIError, JSONParsingError) as e:
            logger.warning(f"OpenAI extraction failed, using fallback: {str(e)}")
            cv_data = fallback_extraction(cv_text)
        
        # 3. Mettre en cache le résultat
        cache_result(cache_key, cv_data)
        
        # 4. Créer une instance de CVModel avec les données extraites
        cv_model = CVModel(
            nom=cv_data.get("nom", ""),
            prenom=cv_data.get("prenom", ""),
            poste=cv_data.get("poste", ""),
            competences=cv_data.get("competences", []),
            logiciels=cv_data.get("logiciels", []),
            soft_skills=cv_data.get("soft_skills", []),
            email=cv_data.get("email", ""),
            telephone=cv_data.get("telephone", ""),
            adresse=cv_data.get("adresse", "")
        )
        
        return cv_model, False
        
    except FileExtractionError as e:
        logger.error(f"File extraction error: {str(e)}")
        raise CVParserError(f"Erreur d'extraction du fichier: {str(e)}")
    except Exception as e:
        logger.error(f"Error parsing CV: {str(e)}", exc_info=True)
        raise CVParserError(f"Erreur lors du parsing du CV: {str(e)}")
