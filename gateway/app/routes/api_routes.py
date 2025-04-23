import requests
from flask import Blueprint, request, jsonify, current_app
from app.middleware.auth_middleware import token_required
import json

api = Blueprint('api', __name__)

# Helper pour faire des requêtes aux microservices
def make_service_request(service_url, endpoint, method='GET', data=None, headers=None, files=None, timeout=None):
    """Fonction utilitaire pour faire des requêtes aux microservices"""
    url = f"{service_url}/{endpoint}"
    timeout = timeout or current_app.config['TIMEOUT']
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers, files=files, timeout=timeout)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            return {"error": "Méthode non supportée"}, 400
        
        return response.json(), response.status_code
    except requests.exceptions.Timeout:
        return {"error": "Timeout lors de la requête au service"}, 504
    except requests.exceptions.ConnectionError:
        return {"error": "Impossible de se connecter au service"}, 503
    except Exception as e:
        return {"error": str(e)}, 500

# Routes pour l'authentification
@api.route('/auth/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    service_url = current_app.config['USER_SERVICE_URL']
    data = request.json
    response, status_code = make_service_request(service_url, 'auth/register', method='POST', data=data)
    return jsonify(response), status_code

@api.route('/auth/login', methods=['POST'])
def login():
    """Connexion d'un utilisateur"""
    service_url = current_app.config['USER_SERVICE_URL']
    data = request.json
    response, status_code = make_service_request(service_url, 'auth/login', method='POST', data=data)
    return jsonify(response), status_code

# Routes pour le parsing de CV
@api.route('/cv-parser/upload', methods=['POST'])
@token_required
def upload_cv():
    """Upload et parsing d'un CV"""
    service_url = current_app.config['CV_PARSER_SERVICE_URL']
    
    # Transmission du fichier
    files = {'file': (request.files['file'].filename, request.files['file'].read(), request.files['file'].content_type)}
    
    # Extraction du type de document (CV, lettre de motivation, etc.)
    doc_type = request.form.get('doc_type', 'cv')
    
    # Création des données du formulaire
    data = {'doc_type': doc_type}
    
    # Transmission du token d'authentification
    headers = {}
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    
    response, status_code = make_service_request(
        service_url, 
        'upload', 
        method='POST', 
        data=data,
        headers=headers,
        files=files
    )
    
    return jsonify(response), status_code

@api.route('/cv-parser/chat', methods=['POST'])
@token_required
def chat_with_cv():
    """Chat avec l'IA à propos d'un CV"""
    service_url = current_app.config['CV_PARSER_SERVICE_URL']
    data = request.json
    
    headers = {}
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    
    response, status_code = make_service_request(
        service_url, 
        'chat', 
        method='POST', 
        data=data,
        headers=headers
    )
    
    return jsonify(response), status_code

# Routes pour les profils
@api.route('/profiles', methods=['GET'])
@token_required
def get_profiles():
    """Récupération des profils"""
    service_url = current_app.config['PROFILE_SERVICE_URL']
    
    headers = {}
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    
    response, status_code = make_service_request(
        service_url, 
        'profiles', 
        method='GET',
        headers=headers
    )
    
    return jsonify(response), status_code

@api.route('/profiles/<profile_id>', methods=['GET'])
@token_required
def get_profile(profile_id):
    """Récupération d'un profil spécifique"""
    service_url = current_app.config['PROFILE_SERVICE_URL']
    
    headers = {}
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    
    response, status_code = make_service_request(
        service_url, 
        f'profiles/{profile_id}', 
        method='GET',
        headers=headers
    )
    
    return jsonify(response), status_code

# Routes pour le matching
@api.route('/matching/job/<job_id>/candidates', methods=['GET'])
@token_required
def get_matching_candidates(job_id):
    """Récupération des candidats correspondant à une offre d'emploi"""
    service_url = current_app.config['MATCHING_SERVICE_URL']
    
    headers = {}
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    
    response, status_code = make_service_request(
        service_url, 
        f'job/{job_id}/candidates', 
        method='GET',
        headers=headers
    )
    
    return jsonify(response), status_code

@api.route('/matching/profile/<profile_id>/jobs', methods=['GET'])
@token_required
def get_matching_jobs(profile_id):
    """Récupération des offres d'emploi correspondant à un profil"""
    service_url = current_app.config['MATCHING_SERVICE_URL']
    
    headers = {}
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    
    response, status_code = make_service_request(
        service_url, 
        f'profile/{profile_id}/jobs', 
        method='GET',
        headers=headers
    )
    
    return jsonify(response), status_code

# Routes pour les offres d'emploi
@api.route('/jobs', methods=['GET'])
@token_required
def get_jobs():
    """Récupération des offres d'emploi"""
    service_url = current_app.config['JOB_SERVICE_URL']
    
    headers = {}
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    
    response, status_code = make_service_request(
        service_url, 
        'jobs', 
        method='GET',
        headers=headers
    )
    
    return jsonify(response), status_code

@api.route('/jobs/<job_id>', methods=['GET'])
@token_required
def get_job(job_id):
    """Récupération d'une offre d'emploi spécifique"""
    service_url = current_app.config['JOB_SERVICE_URL']
    
    headers = {}
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    
    response, status_code = make_service_request(
        service_url, 
        f'jobs/{job_id}', 
        method='GET',
        headers=headers
    )
    
    return jsonify(response), status_code

# Route pour les notifications
@api.route('/notifications/send', methods=['POST'])
@token_required
def send_notification():
    """Envoi d'une notification"""
    service_url = current_app.config['NOTIFICATION_SERVICE_URL']
    data = request.json
    
    headers = {}
    if 'Authorization' in request.headers:
        headers['Authorization'] = request.headers['Authorization']
    
    response, status_code = make_service_request(
        service_url, 
        'send', 
        method='POST', 
        data=data,
        headers=headers
    )
    
    return jsonify(response), status_code
