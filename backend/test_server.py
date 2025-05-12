"""
Serveur de test simplifié pour le Job Parser
Usage: python test_server.py
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from job_parser_service import job_parser

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'application Flask
app = Flask(__name__)
CORS(app)  # Permettre les requêtes cross-origin

@app.route('/api/job-parser/queue', methods=['POST'])
def queue_job():
    """Point d'entrée pour soumettre un job d'analyse de fiche de poste"""
    try:
        logger.info("Réception d'une requête de file d'attente")
        
        # Vérifier si un fichier a été envoyé
        if 'file' in request.files:
            file = request.files['file']
            file_content = file.read()
            
            logger.info(f"Fichier reçu: {file.filename}, taille: {len(file_content)} octets")
            
            # Détecter le type de fichier
            if file.filename.lower().endswith('.pdf'):
                logger.info("Traitement PDF")
                try:
                    content = job_parser.parse_pdf(file_content)
                    logger.info(f"Extraction PDF réussie: {len(content)} caractères")
                except ValueError as e:
                    logger.error(f"Erreur lors de l'extraction PDF: {e}")
                    return jsonify({"error": str(e)}), 400
            else:
                # Pour les autres formats (txt, docx, etc.)
                content = file_content.decode('utf-8', errors='ignore')
                logger.info(f"Décodage de texte: {len(content)} caractères")
                
        # Sinon, vérifier si le texte a été envoyé
        elif request.form.get('text'):
            content = request.form.get('text')
            logger.info(f"Texte reçu: {len(content)} caractères")
        else:
            logger.error("Aucun fichier ou texte fourni")
            return jsonify({"error": "Aucun fichier ou texte fourni"}), 400
        
        # Prévisualisation du contenu
        preview = content[:200].replace('\n', ' ')
        logger.info(f"Début du contenu: '{preview}...'")
        
        # Mettre le job en file d'attente pour l'analyse
        result = job_parser.queue_job(content)
        logger.info(f"Job créé avec l'ID: {result['job_id']}")
        
        return jsonify(result)
    
    except Exception as e:
        logger.exception(f"Erreur lors de la soumission du job: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/job-parser/result/<job_id>', methods=['GET'])
def get_job_result(job_id):
    """Point d'entrée pour récupérer le résultat d'un job"""
    try:
        logger.info(f"Demande de résultat pour le job: {job_id}")
        result, status_code = job_parser.get_job_result(job_id)
        logger.info(f"Statut du job {job_id}: {result.get('status')}")
        return jsonify(result), status_code if isinstance(status_code, int) else 200
    except Exception as e:
        logger.exception(f"Erreur lors de la récupération du résultat du job: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/job-parser/health', methods=['GET'])
def health_check():
    """Point d'entrée pour vérifier la santé du service"""
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "api_status": "available" if job_parser.api_key else "api_key_missing"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7000))
    logger.info(f"Démarrage du serveur de test sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
