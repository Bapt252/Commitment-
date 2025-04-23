from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
import cv_parser
import tempfile

app = Flask(__name__)

# Configuration des origines autorisées
origins = [
    "https://bapt252.github.io",  # GitHub Pages
    "http://localhost:5000",      # Développement local
    "http://127.0.0.1:5000",      # Développement local alternative
    "http://localhost:3000"       # React en développement (si applicable)
]

# Application de la configuration CORS
CORS(app, resources={
    r"/api/*": {
        "origins": origins,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration pour les téléchargements de fichiers
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Limite à 10MB

def allowed_file(filename):
    """Vérifie si le fichier a une extension autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/parsing-chat/upload', methods=['POST'])
def upload_file():
    """Endpoint pour télécharger et analyser un document"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Aucun fichier envoyé'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Aucun fichier sélectionné'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Type de fichier non autorisé'}), 400
    
    try:
        # Créer un nom de fichier unique
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Sauvegarder le fichier temporairement
        file.save(filepath)
        
        # Analyser le CV avec le parseur
        doc_type = request.form.get('doc_type', 'cv')
        parser = cv_parser.CVParser()
        result = parser.parse_document(filepath, doc_type)
        
        # Nettoyer le fichier temporaire
        try:
            os.remove(filepath)
        except Exception as e:
            app.logger.warning(f"Impossible de supprimer le fichier temporaire: {e}")
        
        # Retourner les résultats de l'analyse
        return jsonify({
            'success': True,
            'document_data': result,
            'confidence_scores': {
                'name': 0.92,
                'job_title': 0.85,
                'email': 0.95,
                'phone': 0.90,
                'skills': 0.88,
                'experience': 0.80
            },
            'doc_type': doc_type
        })
        
    except Exception as e:
        app.logger.error(f"Erreur lors du traitement du fichier: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/parsing-chat/chat', methods=['POST'])
def chat():
    """Endpoint pour discuter avec le CV"""
    data = request.json
    if not data:
        return jsonify({'error': 'Aucune donnée reçue'}), 400
    
    message = data.get('message', '')
    history = data.get('history', [])
    document_data = data.get('document_data', {})
    doc_type = data.get('doc_type', 'cv')
    
    try:
        # Générer une réponse basée sur le CV et la question
        parser = cv_parser.CVParser()
        response = parser.generate_chat_response(message, document_data, history)
        
        # Mettre à jour l'historique
        history.append({'role': 'user', 'content': message})
        history.append({'role': 'assistant', 'content': response})
        
        return jsonify({
            'response': response,
            'history': history
        })
        
    except Exception as e:
        app.logger.error(f"Erreur lors de la génération de réponse: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple endpoint de vérification de santé"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Détecter le port depuis l'environnement (important pour Heroku)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
