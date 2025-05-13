#!/usr/bin/env python3
"""
Job Parser API - Backend pour l'analyse des fiches de poste avec GPT

Ce script fournit une API Flask qui permet d'analyser des fiches de poste
en utilisant GPT pour extraire les informations clés.
"""

import os
import json
import tempfile
from typing import Dict, List, Any, Optional
import logging

# Flask et dépendances
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from werkzeug.utils import secure_filename

# Traitement des fichiers
import PyPDF2
import docx
import io

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("job_parser_api")

# Création de l'application Flask
app = Flask(__name__)
CORS(app)  # Permettre les requêtes CORS

# Configuration
class Config:
    UPLOAD_FOLDER = tempfile.gettempdir()
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
    # Clé API OpenAI (à configurer via variable d'environnement)
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    OPENAI_MODEL = "gpt-3.5-turbo"
    DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")

app.config.from_object(Config)

# Vérifier si l'extension du fichier est autorisée
def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

# Extraire le texte d'un fichier PDF
def extract_text_from_pdf(file_path: str) -> str:
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte PDF: {e}")
        return ""

# Extraire le texte d'un fichier DOCX
def extract_text_from_docx(file_path: str) -> str:
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte DOCX: {e}")
        return ""

# Extraire le texte d'un fichier TXT
def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Essayer avec d'autres encodages si utf-8 échoue
        encodings = ['latin-1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    return file.read()
            except UnicodeDecodeError:
                continue
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte TXT: {e}")
    return ""

# Analyser le texte de la fiche de poste avec GPT
def analyze_job_text_with_gpt(job_text: str) -> Dict[str, Any]:
    """
    Utilise l'API OpenAI pour analyser une fiche de poste
    et en extraire les informations clés.
    """
    if not Config.OPENAI_API_KEY:
        logger.warning("Clé API OpenAI non configurée. Utilisation du parsing local.")
        return analyze_job_locally(job_text)
    
    # Créer le prompt pour GPT
    prompt = f"""
    Extrais les informations clés de cette fiche de poste pour un parser automatique. 
    Pour chaque champ, cherche les informations pertinentes et les retourne au format précis.
    
    Voici la fiche de poste à analyser:
    {job_text}
    
    Retourne les informations au format JSON suivant:
    {{
        "title": "Titre du poste",
        "company": "Nom de l'entreprise",
        "location": "Localisation du poste",
        "contract_type": "Type de contrat (CDI, CDD, etc.)",
        "skills": ["Compétence 1", "Compétence 2", ...],
        "experience": "Niveau d'expérience requis",
        "education": "Formation requise",
        "salary": "Salaire proposé",
        "responsibilities": ["Responsabilité 1", "Responsabilité 2", ...],
        "benefits": ["Avantage 1", "Avantage 2", ...]
    }}
    
    Si certaines informations ne sont pas trouvées, utilise une valeur par défaut comme une chaîne vide ou un tableau vide.
    Réponds uniquement avec le JSON, sans aucun texte supplémentaire.
    """
    
    try:
        # Appel à l'API OpenAI
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.OPENAI_API_KEY}"
        }
        
        payload = {
            "model": Config.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": "Tu es un assistant spécialisé dans l'analyse de fiches de poste. Tu réponds uniquement au format JSON."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        
        response = requests.post(
            Config.OPENAI_API_URL,
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Erreur API OpenAI: {response.status_code} - {response.text}")
            return analyze_job_locally(job_text)
        
        # Parser la réponse
        response_data = response.json()
        if "choices" in response_data and len(response_data["choices"]) > 0:
            content = response_data["choices"][0]["message"]["content"]
            
            # Extraire le JSON de la réponse
            try:
                # Tenter d'extraire le JSON de la réponse s'il est entouré de ```
                json_match = content.strip()
                if json_match.startswith("```json"):
                    json_match = json_match[7:]
                if json_match.endswith("```"):
                    json_match = json_match[:-3]
                
                result = json.loads(json_match.strip())
                logger.info("Analyse GPT réussie")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Erreur lors du parsing JSON de la réponse GPT: {e}")
                logger.debug(f"Contenu reçu: {content}")
                return analyze_job_locally(job_text)
        
        # En cas de problème avec la réponse
        logger.warning("Format de réponse OpenAI inattendu")
        return analyze_job_locally(job_text)
    
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à l'API OpenAI: {e}")
        return analyze_job_locally(job_text)

# Fonction de fallback: analyse locale de la fiche de poste
def analyze_job_locally(job_text: str) -> Dict[str, Any]:
    """
    Analyse la fiche de poste localement avec des expressions régulières.
    Utilisé comme fallback si l'API OpenAI n'est pas disponible.
    """
    import re
    
    # Initialiser l'objet de résultat
    result = {
        "title": "",
        "company": "",
        "location": "",
        "contract_type": "",
        "skills": [],
        "experience": "",
        "education": "",
        "salary": "",
        "responsibilities": [],
        "benefits": []
    }
    
    try:
        # Extraction du titre du poste
        title_patterns = [
            r"(?:^|\n)[\s•]*Poste[\s:]*(.+?)(?:\n|$)",
            r"(?:^|\n)[\s•]*Intitulé du poste[\s:]*(.+?)(?:\n|$)",
            r"(?:^|\n)[\s•]*Offre d'emploi[\s:]*(.+?)(?:\n|$)",
            r"(?:^|\n)[\s•]*([\w\s\-']+(?:développeur|ingénieur|technicien|consultant|manager|responsable|directeur|analyste)[\w\s\-']+)(?:\n|$)"
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, job_text, re.IGNORECASE)
            if match:
                result["title"] = match.group(1).strip()
                break
        
        # Extraction de l'entreprise
        company_patterns = [
            r"(?:^|\n)[\s•]*Entreprise[\s:]*(.+?)(?:\n|$)",
            r"(?:^|\n)[\s•]*Société[\s:]*(.+?)(?:\n|$)",
            r"(?:^|\n)[\s•]*Employeur[\s:]*(.+?)(?:\n|$)"
        ]
        
        for pattern in company_patterns:
            match = re.search(pattern, job_text, re.IGNORECASE)
            if match:
                result["company"] = match.group(1).strip()
                break
        
        # Extraction de la localisation
        location_patterns = [
            r"(?:^|\n)[\s•]*Lieu[\s:]*(.+?)(?:\n|$)",
            r"(?:^|\n)[\s•]*Localisation[\s:]*(.+?)(?:\n|$)",
            r"(?:^|\n)[\s•]*Localité[\s:]*(.+?)(?:\n|$)",
            r"(?:^|\n)[\s•]*Ville[\s:]*(.+?)(?:\n|$)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, job_text, re.IGNORECASE)
            if match:
                result["location"] = match.group(1).strip()
                break
        
        # Extraction du type de contrat
        contract_patterns = [
            r"(?:^|\n)[\s•]*Type de contrat[\s:]*(.+?)(?:\n|$)",
            r"(?:^|\n)[\s•]*Contrat[\s:]*(.+?)(?:\n|$)",
            r"(?:^|\n)[\s•]*(CDI|CDD|Stage|Alternance|Intérim|Freelance)(?:\n|$)"
        ]
        
        for pattern in contract_patterns:
            match = re.search(pattern, job_text, re.IGNORECASE)
            if match:
                result["contract_type"] = match.group(1).strip()
                break
        
        # Et ainsi de suite pour les autres champs...
        # Le code complet serait trop long, cette version simplifiée extrait juste les principaux champs
        
        logger.info("Analyse locale réussie")
        return result
    
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse locale: {e}")
        return result

# Route pour l'analyse de fichier/texte
@app.route('/api/parse-job', methods=['POST'])
def parse_job():
    """
    Endpoint pour analyser une fiche de poste.
    Accepte soit un fichier, soit un texte brut.
    """
    try:
        # Vérifier si un fichier est fourni
        if 'file' in request.files:
            file = request.files['file']
            
            # Vérifier que le fichier est valide
            if file.filename == '':
                return jsonify({"error": "Nom de fichier vide"}), 400
            
            if not file or not allowed_file(file.filename):
                return jsonify({"error": "Type de fichier non autorisé"}), 400
            
            # Sauvegarder le fichier temporairement
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # Extraire le texte selon le type de fichier
            if filename.endswith('.pdf'):
                job_text = extract_text_from_pdf(file_path)
            elif filename.endswith(('.docx', '.doc')):
                job_text = extract_text_from_docx(file_path)
            elif filename.endswith('.txt'):
                job_text = extract_text_from_txt(file_path)
            else:
                return jsonify({"error": "Format de fichier non pris en charge"}), 400
            
            # Supprimer le fichier temporaire
            os.remove(file_path)
            
        # Sinon, vérifier si un texte est fourni
        elif 'text' in request.form:
            job_text = request.form['text']
        else:
            return jsonify({"error": "Aucun fichier ou texte fourni"}), 400
        
        # Vérifier que le texte n'est pas vide
        if not job_text or len(job_text.strip()) == 0:
            return jsonify({"error": "Le texte extrait est vide"}), 400
        
        # Analyser le texte avec GPT
        result = analyze_job_text_with_gpt(job_text)
        
        # Retourner le résultat
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Erreur lors du traitement de la requête")
        return jsonify({"error": str(e)}), 500

# Route pour la santé de l'API
@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint pour vérifier que l'API est fonctionnelle."""
    return jsonify({"status": "ok", "version": "1.0.0"})

# Lancement de l'application
if __name__ == '__main__':
    # Vérifier si la clé API est configurée
    if not Config.OPENAI_API_KEY:
        logger.warning("Aucune clé API OpenAI n'a été configurée. Certaines fonctionnalités seront limitées.")
    
    # Démarrer le serveur
    port = int(os.environ.get("PORT", 5055))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)
