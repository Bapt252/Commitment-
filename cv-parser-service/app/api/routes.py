import os
import tempfile
import json
import datetime
from flask import Blueprint, request, jsonify, current_app
from app.core.parser import extract_text_from_file, parse_cv_with_gpt, chat_with_cv_data
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import uuid

api = Blueprint('api', __name__)

# Connexion à MongoDB
def get_mongo_client():
    return MongoClient(current_app.config['MONGODB_URI'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@api.route('/upload', methods=['POST'])
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
            
            # Stockage des données dans MongoDB
            if result["success"]:
                # Générer un ID unique pour le document
                document_id = str(uuid.uuid4())
                
                # Ajouter l'ID au résultat
                result["document_id"] = document_id
                
                # Récupérer les informations de l'utilisateur si disponibles
                user_id = request.headers.get('X-User-ID', 'anonymous')
                
                # Préparer le document pour MongoDB
                cv_document = {
                    "_id": document_id,
                    "user_id": user_id,
                    "filename": secure_filename(file.filename),
                    "file_type": file_extension,
                    "content": file_content,
                    "parsed_data": result["document_data"],
                    "confidence_scores": result["confidence_scores"],
                    "created_at": datetime.datetime.utcnow()
                }
                
                # Sauvegarder dans MongoDB
                with get_mongo_client() as client:
                    db = client.get_database()
                    db.cv_documents.insert_one(cv_document)
        else:
            # Pour d'autres types de documents, à implémenter selon les besoins
            result = {"success": False, "error": "Type de document non implémenté"}
        
        return jsonify(result)
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors du traitement du fichier: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@api.route('/chat', methods=['POST'])
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
            
            # Stocker l'historique des conversations si un document_id est fourni
            document_id = data.get('document_id')
            if document_id:
                user_id = request.headers.get('X-User-ID', 'anonymous')
                chat_entry = {
                    "document_id": document_id,
                    "user_id": user_id,
                    "message": message,
                    "response": response["response"],
                    "timestamp": datetime.datetime.utcnow()
                }
                
                with get_mongo_client() as client:
                    db = client.get_database()
                    db.chat_history.insert_one(chat_entry)
        else:
            # Pour d'autres types de documents, à implémenter selon les besoins
            response = {"error": "Type de document non supporté pour le chat"}
        
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors du chat: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Endpoint pour récupérer un CV analysé par ID
@api.route('/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Récupérer un document CV analysé par son ID"""
    try:
        with get_mongo_client() as client:
            db = client.get_database()
            document = db.cv_documents.find_one({"_id": document_id})
            
        if not document:
            return jsonify({"error": "Document non trouvé"}), 404
        
        # Convertir _id en chaîne pour la sérialisation JSON
        document["_id"] = str(document["_id"])
        
        # Supprimer le contenu brut pour alléger la réponse
        if "content" in document:
            del document["content"]
        
        return jsonify(document)
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération du document: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Endpoint pour lister les documents CV d'un utilisateur
@api.route('/documents', methods=['GET'])
def list_documents():
    """Lister les documents CV d'un utilisateur"""
    try:
        user_id = request.headers.get('X-User-ID', 'anonymous')
        
        with get_mongo_client() as client:
            db = client.get_database()
            documents = list(db.cv_documents.find(
                {"user_id": user_id},
                {"_id": 1, "filename": 1, "parsed_data": 1, "created_at": 1}
            ))
        
        # Convertir _id en chaîne pour la sérialisation JSON
        for doc in documents:
            doc["_id"] = str(doc["_id"])
        
        return jsonify(documents)
    
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la récupération des documents: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
