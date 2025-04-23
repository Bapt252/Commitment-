import os
import tempfile
import json
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_cors import CORS
from parsing_service import extract_text_from_file, parse_cv_with_gpt, chat_with_cv_data

app = Flask(__name__, static_folder='../templates', static_url_path='/')
CORS(app, resources={r"/api/*": {"origins": "*"}})

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/parsing-chat/upload', methods=['POST'])
def upload_file():
    """Point d'entrée pour télécharger et analyser un CV"""
    try:
        # Vérification de la présence du fichier
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "Aucun fichier trouvé"}), 400
        
        file = request.files['file']
        
        # Vérification du nom de fichier
        if file.filename == '':
            return jsonify({"success": False, "error": "Nom de fichier invalide"}), 400
        
        # Vérification du type de fichier
        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "Type de fichier non autorisé"}), 400
        
        # Vérification du type de document (cv ou autre)
        doc_type = request.form.get('doc_type', 'cv')
        if doc_type not in ['cv', 'job_description']:
            return jsonify({"success": False, "error": "Type de document non supporté"}), 400
        
        # Création d'un fichier temporaire pour stocker le fichier téléchargé
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        file.save(temp_file.name)
        
        # Extraction du texte du fichier
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        file_content = extract_text_from_file(temp_file.name, file_extension)
        
        # Suppression du fichier temporaire
        os.unlink(temp_file.name)
        
        # Analyse du contenu avec GPT selon le type de document
        if doc_type == 'cv':
            result = parse_cv_with_gpt(file_content, file_extension)
        else:
            # Pour d'autres types de documents, à implémenter selon les besoins
            result = {"success": False, "error": "Type de document non implémenté"}
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/parsing-chat/chat', methods=['POST'])
def chat():
    """Point d'entrée pour le chat avec l'IA sur le CV"""
    try:
        data = request.json
        
        # Vérification des paramètres requis
        if not data or 'message' not in data:
            return jsonify({"error": "Message manquant"}), 400
        
        message = data.get('message')
        history = data.get('history', [])
        document_data = data.get('document_data', {})
        doc_type = data.get('doc_type', 'cv')
        
        # Chat avec l'IA à propos du document
        if doc_type == 'cv':
            response = chat_with_cv_data(message, history, document_data)
        else:
            # Pour d'autres types de documents, à implémenter selon les besoins
            response = {"error": "Type de document non supporté pour le chat"}
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Pour le déploiement avec Gunicorn
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)