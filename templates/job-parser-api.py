#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Job Parser API
-------------
API simple pour l'intégration du parser de fiches de poste avec le formulaire client.
"""

import os
import json
import tempfile
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import sys

# Ajout du répertoire parent au chemin Python pour pouvoir importer job_parser_cli
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from job_parser_cli import extract_text_from_pdf, extract_job_info, parse_job_posting

# Configuration
UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__, static_folder='../static')
CORS(app)  # Activer CORS pour toutes les routes

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("job-parser-api")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite à 16 MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('../templates', 'client-questionnaire.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('../static', path)

@app.route('/api/parse-job-post', methods=['POST'])
def parse_job_post():
    """Endpoint pour analyser une fiche de poste téléchargée."""
    # Vérifier si la requête contient un fichier
    if 'job_post_file' not in request.files:
        return jsonify({'error': 'Aucun fichier trouvé dans la requête'}), 400
    
    file = request.files['job_post_file']
    
    # Vérifier si un fichier a été sélectionné
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    # Vérifier si le fichier est au format autorisé
    if not allowed_file(file.filename):
        return jsonify({'error': 'Format de fichier non autorisé. Seuls les fichiers PDF sont acceptés.'}), 400
    
    try:
        # Sauvegarder le fichier temporairement
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"Fichier sauvegardé: {filepath}")
        
        # Analyser la fiche de poste
        result = parse_job_posting(filepath)
        
        # Supprimer le fichier temporaire
        os.remove(filepath)
        
        # Extraire les informations pertinentes pour le formulaire
        job_info = result["job_info"]
        form_data = {
            "jobTitle": job_info.get("titre_poste", ""),
            "company": job_info.get("entreprise", ""),
            "location": job_info.get("localisation", ""),
            "contractType": job_info.get("type_contrat", ""),
            "skills": job_info.get("competences", []),
            "experience": job_info.get("experience", ""),
            "education": job_info.get("formation", ""),
            "salary": job_info.get("salaire", ""),
            "description": job_info.get("description", "")
        }
        
        return jsonify({
            'success': True,
            'message': 'Analyse réussie',
            'data': form_data
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Erreur lors de l'analyse du fichier: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5055, debug=True)
