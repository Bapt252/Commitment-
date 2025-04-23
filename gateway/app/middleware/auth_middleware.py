from functools import wraps
from flask import request, jsonify, current_app
import jwt
import requests

def token_required(f):
    """Décorateur pour vérifier le token JWT d'authentification"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Vérifier si le token est dans l'en-tête Authorization
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        # Si aucun token n'est trouvé
        if not token:
            return jsonify({'message': 'Token d\'authentification manquant!'}), 401
        
        try:
            # Validation du token auprès du User Service
            user_service_url = current_app.config['USER_SERVICE_URL']
            response = requests.post(
                f"{user_service_url}/auth/validate-token",
                json={"token": token},
                timeout=current_app.config['TIMEOUT']
            )
            
            # Si le token n'est pas valide
            if response.status_code != 200:
                return jsonify({'message': 'Token invalide ou expiré!'}), 401
            
            # Ajouter les informations utilisateur au contexte de la requête
            current_user = response.json().get('user')
            
            # Passer les informations utilisateur à la fonction décorée
            return f(*args, current_user=current_user, **kwargs)
        
        except requests.exceptions.RequestException:
            # Si le service d'authentification n'est pas disponible
            return jsonify({'message': 'Service d\'authentification non disponible!'}), 503
        
        except Exception as e:
            return jsonify({'message': f'Erreur lors de l\'authentification: {str(e)}'}), 500
    
    return decorated
