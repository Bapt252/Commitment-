import os
import json
import hashlib
import openai
from typing import Dict, Any, BinaryIO, Optional
import io
from docx import Document
import PyPDF2
from app.models.cv_model import CVModel
import redis

# Connexion Redis pour le cache
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=False  # Conserver les données binaires pour le cache
)

def calculate_file_hash(file: BinaryIO) -> str:
    """Calcule un hash SHA-256 du contenu du fichier pour l'utiliser comme clé de cache."""
    file.seek(0)
    file_content = file.read()
    file_hash = hashlib.sha256(file_content).hexdigest()
    file.seek(0)  # Réinitialiser le curseur pour une utilisation ultérieure
    return file_hash

def extract_text_from_pdf(file: BinaryIO) -> str:
    """Extrait le texte d'un fichier PDF."""
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:  # Vérifier que le texte n'est pas None
            text += page_text + "\n"
    return text

def extract_text_from_docx(file: BinaryIO) -> str:
    """Extrait le texte d'un fichier DOCX."""
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
    
    return text

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

def parse_cv_with_openai(cv_text: str) -> Dict[str, Any]:
    """Parse un CV en utilisant l'API OpenAI GPT-4o-mini."""
    # Récupérer la clé API d'OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("La clé API OpenAI n'est pas configurée dans les variables d'environnement.")
    
    openai.api_key = api_key
    
    # Créer le prompt pour GPT-4o-mini
    system_prompt = """
    Tu es un expert du parsing de CV. Extrais précisément les informations suivantes du CV fourni:
    
    Renvoie UNIQUEMENT un objet JSON valide avec les champs suivants, sans aucun texte supplémentaire:
    {
        "nom": "string",
        "prenom": "string",
        "poste": "string",
        "competences": ["string", "string", ...],
        "logiciels": ["string", "string", ...],
        "soft_skills": ["string", "string", ...],
        "email": "string",
        "telephone": "string",
        "adresse": "string"
    }
    
    Instructions spécifiques:
    - nom et prénom: identifie correctement le nom et le prénom
    - poste: poste actuel ou recherché
    - competences: liste des compétences techniques (langages, frameworks, méthodologies)
    - logiciels: liste des logiciels et outils maîtrisés
    - soft_skills: liste des compétences comportementales (travail en équipe, communication, etc.)
    - email: adresse email du candidat
    - telephone: numéro de téléphone du candidat
    - adresse: adresse postale complète du candidat

    Si une information n'est pas présente, utilise une chaîne vide ou une liste vide selon le type de champ.
    Assure-toi que ta réponse est un JSON valide et rien d'autre.
    """
    
    # Appeler l'API OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": cv_text}
            ],
            temperature=0.3
        )
        
        # Extraire le contenu de la réponse
        content = response["choices"][0]["message"]["content"]
        
        # Nettoyer le contenu au cas où GPT aurait ajouté des backticks ou commentaires
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        # Parser le JSON
        data = json.loads(content)
        
        # Vérifier que toutes les clés nécessaires sont présentes
        required_keys = ["nom", "prenom", "poste", "competences", "logiciels", "soft_skills", "email", "telephone", "adresse"]
        for key in required_keys:
            if key not in data:
                data[key] = [] if key in ["competences", "logiciels", "soft_skills"] else ""
        
        return data
        
    except json.JSONDecodeError as e:
        # En cas d'erreur de parsing JSON
        raise ValueError(f"Impossible de parser la réponse de l'API OpenAI en JSON valide: {str(e)}")
    except Exception as e:
        # Autres erreurs
        raise ValueError(f"Erreur lors du parsing du CV avec OpenAI: {str(e)}")

def parse_cv(file: BinaryIO, filename: str) -> CVModel:
    """
    Fonction principale qui parse un CV en utilisant l'API OpenAI avec cache Redis.
    
    Args:
        file: Fichier CV (PDF ou DOCX)
        filename: Nom du fichier avec extension
        
    Returns:
        Une instance de CVModel avec les informations extraites
    """
    # Déterminer l'extension du fichier
    _, file_extension = os.path.splitext(filename)
    
    # Calculer le hash du fichier pour la clé de cache
    file_hash = calculate_file_hash(file)
    cache_key = f"cv_parse:{file_hash}"
    
    # Vérifier si le résultat est déjà en cache
    cached_result = redis_client.get(cache_key)
    if cached_result:
        try:
            # Désérialiser le résultat du cache
            cv_data = json.loads(cached_result)
            
            # Créer une instance de CVModel avec les données du cache
            return CVModel(
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
        except (json.JSONDecodeError, Exception) as e:
            # Si erreur avec le cache, on continue avec le traitement normal
            print(f"Erreur lors de la récupération du cache: {str(e)}")
    
    # Si pas en cache ou erreur de cache, procéder au traitement
    try:
        # 1. Extraire le texte brut du document
        cv_text = extract_text(file, file_extension)
        
        # 2. Envoyer le texte à l'API OpenAI et récupérer les informations structurées
        cv_data = parse_cv_with_openai(cv_text)
        
        # 3. Mettre en cache le résultat
        redis_client.set(cache_key, json.dumps(cv_data), ex=3600*24*7)  # Expire après 7 jours
        
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
        
        return cv_model
    except Exception as e:
        raise ValueError(f"Erreur lors du parsing du CV: {str(e)}")
