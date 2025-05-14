#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Flask pour l'analyse des fiches de poste avec GPT

Ce service fournit un endpoint API pour l'analyse des fiches de poste
en utilisant GPT. Il est destiné à être utilisé par l'interface web.
"""

import os
import sys
import json
import logging
import tempfile
import PyPDF2
import re
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from werkzeug.utils import secure_filename

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gpt-parser-api")

# Configuration de l'application Flask
app = Flask(__name__)
CORS(app)  # Autoriser les requêtes cross-origin

# Taille maximale des fichiers (5 Mo)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# Types de fichiers autorisés
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

# Configurer l'API OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY", "")

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extrait le texte d'un fichier PDF."""
    logger.info(f"Extraction du texte du fichier PDF: {file_path}")
    
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() + "\n"
        
        logger.info(f"Texte extrait: {len(text)} caractères")
        return text
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte: {str(e)}")
        raise

def extract_text_from_file(file_path):
    """Extrait le texte d'un fichier en fonction de son extension."""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    else:
        # Pour les autres types de fichiers (docx, doc, etc.)
        # Vous pourriez implémenter d'autres extracteurs ici
        raise ValueError(f"Type de fichier non pris en charge: {file_path}")

def analyze_with_gpt(text):
    """Analyse le texte avec l'API OpenAI."""
    logger.info("Envoi du texte à l'API OpenAI (GPT)...")
    
    if not openai.api_key:
        logger.error("Clé API OpenAI non définie.")
        raise ValueError("Clé API OpenAI non définie.")
    
    # Si le texte est trop long, le tronquer
    max_tokens = 15000  # Approximativement 15000 caractères
    if len(text) > max_tokens:
        logger.warning(f"Texte trop long ({len(text)} caractères), troncature à {max_tokens} caractères")
        text = text[:max_tokens] + "...[texte tronqué]"
    
    try:
        # Appel à l'API OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Ou un autre modèle disponible
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse de fiches de poste."},
                {"role": "user", "content": f"""
Analyse cette fiche de poste et extrait les informations importantes.
Réponds UNIQUEMENT au format JSON.

FICHE DE POSTE:
{text}

EXTRAIRE LES INFORMATIONS SUIVANTES (JSON UNIQUEMENT):
{{
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
}}
"""}
            ],
            temperature=0.1
        )
        
        # Extraire la réponse
        content = response.choices[0].message.content
        
        # Tentative d'extraction d'un JSON de la réponse
        try:
            # Nettoyage du texte pour s'assurer qu'il ne contient que du JSON
            json_pattern = r'(\{[\s\S]*\})'
            match = re.search(json_pattern, content)
            if match:
                json_str = match.group(1)
                parsed_result = json.loads(json_str)
                logger.info("Parsing JSON réussi")
                return parsed_result
            else:
                # Essayer de parser directement
                parsed_result = json.loads(content)
                return parsed_result
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {str(e)}")
            logger.error(f"Réponse: {content}")
            raise ValueError("Impossible de parser la réponse JSON de GPT")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}")
        raise

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de l'état de santé de l'API."""
    return jsonify({"status": "ok", "api": "gpt-parser", "version": "1.0.0"})

@app.route('/analyze', methods=['POST'])
def analyze_job_posting():
    """Endpoint pour l'analyse d'une fiche de poste par texte."""
    try:
        # Vérifier si la requête contient le texte de la fiche de poste
        if not request.json or 'text' not in request.json:
            return jsonify({"error": "Le texte de la fiche de poste n'a pas été fourni"}), 400
        
        text = request.json['text']
        
        # Vérifier que le texte n'est pas vide
        if not text.strip():
            return jsonify({"error": "Le texte de la fiche de poste est vide"}), 400
        
        # Analyser le texte avec GPT
        result = analyze_with_gpt(text)
        
        return jsonify({
            "status": "success",
            "job_info": result,
            "metadata": {
                "analyzed_at": datetime.now().isoformat(),
                "parser_version": "1.0.0-gpt"
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/analyze-file', methods=['POST'])
def analyze_job_posting_file():
    """Endpoint pour l'analyse d'une fiche de poste à partir d'un fichier."""
    try:
        # Vérifier si la requête contient un fichier
        if 'file' not in request.files:
            return jsonify({"error": "Aucun fichier n'a été envoyé"}), 400
        
        file = request.files['file']
        
        # Vérifier que le fichier est valide
        if file.filename == '':
            return jsonify({"error": "Nom de fichier invalide"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": f"Type de fichier non autorisé. Autorisés: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        # Sauvegarder le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            file_path = temp.name
            file.save(file_path)
        
        try:
            # Extraire le texte du fichier
            text = extract_text_from_file(file_path)
            
            # Analyser le texte avec GPT
            result = analyze_with_gpt(text)
            
            return jsonify({
                "status": "success",
                "job_info": result,
                "metadata": {
                    "filename": secure_filename(file.filename),
                    "analyzed_at": datetime.now().isoformat(),
                    "parser_version": "1.0.0-gpt"
                }
            })
            
        finally:
            # Supprimer le fichier temporaire
            if os.path.exists(file_path):
                os.unlink(file_path)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du fichier: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Si la clé API n'est pas définie, utiliser une clé par défaut pour le développement
    if not openai.api_key:
        logger.warning("OPENAI_API_KEY n'est pas défini. Utilisation d'une clé fictive pour le développement.")
        # Ne définissez jamais réellement une clé API ici en production
    
    # Démarrer le serveur en mode développement
    app.run(host='0.0.0.0', port=5055, debug=True)
