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
try:
    from job_parser_cli import extract_text_from_pdf, extract_job_info, parse_job_posting
except ImportError:
    print("ATTENTION: Le module job_parser_cli.py n'a pas été trouvé.")
    print("Utilisation du mode dégradé avec parsage basique.")
    
    # Définition des fonctions de repli basiques
    def extract_text_from_pdf(pdf_path):
        """Extraction de texte basique depuis un PDF."""
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num in range(len(reader.pages)):
                    text += reader.pages[page_num].extract_text() + "\n"
            return text
        except Exception as e:
            logging.error(f"Erreur lors de l'extraction du texte: {str(e)}")
            return "Erreur lors de l'extraction du texte du PDF."
    
    def extract_job_info(text):
        """Extraction basique des informations d'une fiche de poste."""
        import re
        
        # Modèle extrêmement simplifié pour la démonstration
        job_info = {
            "titre_poste": "",
            "entreprise": "",
            "localisation": "",
            "type_contrat": "",
            "competences": [],
            "experience": "",
            "formation": "",
            "salaire": "",
            "description": "",
        }
        
        # Extraction très basique
        title_match = re.search(r"(?:Poste|Intitulé).*?:(.+?)(?:\n|$)", text, re.IGNORECASE)
        if title_match:
            job_info["titre_poste"] = title_match.group(1).strip()
        
        # Localisation
        location_match = re.search(r"(?:Lieu|Localisation).*?:(.+?)(?:\n|$)", text, re.IGNORECASE)
        if location_match:
            job_info["localisation"] = location_match.group(1).strip()
        
        # Type de contrat
        if "CDI" in text:
            job_info["type_contrat"] = "CDI"
        elif "CDD" in text:
            job_info["type_contrat"] = "CDD"
        
        return job_info
    
    def parse_job_posting(pdf_path):
        """Fonction de parsing simplifiée."""
        text = extract_text_from_pdf(pdf_path)
        job_info = extract_job_info(text)
        
        return {
            "parsing_metadata": {
                "pdf_path": pdf_path,
                "filename": os.path.basename(pdf_path),
                "parser_version": "fallback-0.1"
            },
            "job_info": job_info
        }

# Configuration
UPLOAD_FOLDER = tempfile.mkdtemp()
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

app = Flask(__name__, static_folder='../static')
CORS(app, resources={r"/*": {"origins": "*"}})  # Activer CORS pour toutes les routes et origines

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
    """Page d'accueil simple pour vérifier que l'API fonctionne."""
    return jsonify({
        'status': 'online',
        'service': 'Job Parser API',
        'version': '1.0.0',
        'endpoints': [
            {'path': '/api/parse-job-post', 'method': 'POST', 'description': 'Analyser une fiche de poste (fichier ou texte)'}
        ]
    })

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('../static', path)

@app.route('/api/parse-job-post', methods=['POST', 'OPTIONS'])
def parse_job_post():
    """Endpoint pour analyser une fiche de poste téléchargée ou en texte brut."""
    # Gérer les requêtes OPTIONS pour CORS
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        # Déterminer si la requête contient un fichier ou du texte
        if 'job_post_file' in request.files:
            file = request.files['job_post_file']
            
            # Vérifier si un fichier a été sélectionné
            if file.filename == '':
                return jsonify({'error': 'Aucun fichier sélectionné'}), 400
            
            # Vérifier si le fichier est au format autorisé
            if not allowed_file(file.filename):
                return jsonify({'error': 'Format de fichier non autorisé. Formats acceptés: PDF, DOC, DOCX, TXT'}), 400
            
            # Sauvegarder le fichier temporairement
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            logger.info(f"Fichier sauvegardé: {filepath}")
            
            # Analyser la fiche de poste
            result = parse_job_posting(filepath)
            
            # Supprimer le fichier temporaire
            os.remove(filepath)
            
        elif request.is_json and 'job_post_text' in request.json:
            # Analyser le texte brut
            text = request.json['job_post_text']
            
            if not text or not text.strip():
                return jsonify({'error': 'Le texte de la fiche de poste est vide'}), 400
            
            # Créer un fichier temporaire avec le texte
            fd, filepath = tempfile.mkstemp(suffix='.txt')
            try:
                with os.fdopen(fd, 'w') as tmp:
                    tmp.write(text)
                
                # Analyser la fiche de poste
                result = {}
                result["job_info"] = extract_job_info(text)
                result["parsing_metadata"] = {
                    "pdf_path": None,
                    "filename": None,
                    "parsed_at": None,
                    "parser_version": "text-1.0.0"
                }
            finally:
                # Supprimer le fichier temporaire
                os.unlink(filepath)
                
        else:
            return jsonify({'error': 'Aucun fichier ou texte trouvé dans la requête'}), 400
        
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
            'error': f"Erreur lors de l'analyse: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Déterminer les paramètres de démarrage du serveur
    import socket
    import argparse
    
    parser = argparse.ArgumentParser(description='Job Parser API')
    parser.add_argument('--host', default='0.0.0.0', help='Hôte à utiliser pour le serveur (par défaut: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5055, help='Port à utiliser pour le serveur (par défaut: 5055)')
    parser.add_argument('--debug', action='store_true', help='Activer le mode debug')
    
    args = parser.parse_args()
    
    # Afficher l'adresse IP locale
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\n--- Job Parser API ---")
    print(f"Serveur démarré sur {args.host}:{args.port}")
    print(f"URL locale : http://localhost:{args.port}")
    print(f"URL réseau : http://{local_ip}:{args.port}")
    print(f"Mode debug : {'activé' if args.debug else 'désactivé'}")
    print(f"-------------------\n")
    
    # Démarrer le serveur
    app.run(host=args.host, port=args.port, debug=args.debug)
