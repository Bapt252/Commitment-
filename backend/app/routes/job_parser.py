"""
Routes pour l'API d'analyse de fiches de poste
"""
from flask import Blueprint, request, jsonify
import logging
from job_parser_service import job_parser

# Configuration du logging
logger = logging.getLogger(__name__)

# Création du blueprint pour les routes de l'API
bp = Blueprint('job_parser', __name__, url_prefix='/api/job-parser')

@bp.route('/queue', methods=['POST'])
def queue_job():
    """Point d'entrée pour soumettre un job d'analyse de fiche de poste"""
    try:
        # Vérifier si un fichier a été envoyé
        if 'file' in request.files:
            file = request.files['file']
            file_content = file.read()
            
            # Détecter le type de fichier
            if file.filename.lower().endswith('.pdf'):
                # Traitement spécifique pour les PDF
                try:
                    content = job_parser.parse_pdf(file_content)
                except ValueError as e:
                    return jsonify({"error": str(e)}), 400
            else:
                # Pour les autres formats (txt, docx, etc.)
                content = file_content.decode('utf-8', errors='ignore')
                
        # Sinon, vérifier si le texte a été envoyé
        elif request.form.get('text'):
            content = request.form.get('text')
        else:
            return jsonify({"error": "Aucun fichier ou texte fourni"}), 400
        
        # Mettre le job en file d'attente pour l'analyse
        result = job_parser.queue_job(content)
        return jsonify(result)
    
    except Exception as e:
        logger.exception(f"Erreur lors de la soumission du job: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/result/<job_id>', methods=['GET'])
def get_job_result(job_id):
    """Point d'entrée pour récupérer le résultat d'un job"""
    try:
        result, status_code = job_parser.get_job_result(job_id)
        return jsonify(result), status_code if isinstance(status_code, int) else 200
    except Exception as e:
        logger.exception(f"Erreur lors de la récupération du résultat du job: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/health', methods=['GET'])
def health_check():
    """Point d'entrée pour vérifier la santé du service"""
    return jsonify({
        "status": "ok",
        "version": "1.0.0",
        "api_status": "available" if job_parser.api_key else "api_key_missing"
    })

def register_routes(app):
    """Enregistrer les routes du blueprint avec l'application Flask"""
    app.register_blueprint(bp)
