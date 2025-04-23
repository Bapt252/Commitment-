import os
import jwt
import time
from typing import Dict, Any, Optional, Tuple, List

# Clé secrète partagée pour les JWT inter-services
SHARED_SECRET = os.environ.get("SERVICES_JWT_SECRET", "dev-shared-secret-key")

def generate_service_token(service_name: str, exp_seconds: int = 3600) -> str:
    """Génère un token JWT pour l'authentification entre services.
    
    Args:
        service_name: Nom du service émetteur
        exp_seconds: Durée de validité en secondes
        
    Returns:
        Token JWT pour l'authentification inter-services
    """
    now = int(time.time())
    payload = {
        "iss": service_name,  # émetteur
        "sub": "service_auth",  # sujet
        "iat": now,  # issued at (émis à)
        "exp": now + exp_seconds,  # expiration
        "service": service_name  # nom du service pour la vérification
    }
    
    return jwt.encode(payload, SHARED_SECRET, algorithm="HS256")

def validate_service_token(token: str, allowed_services: Optional[List[str]] = None) -> Tuple[bool, Dict[str, Any]]:
    """Valide un token JWT émis par un autre service.
    
    Args:
        token: Token JWT à valider
        allowed_services: Liste des services autorisés (None pour accepter tous les services)
        
    Returns:
        Tuple (is_valid, payload)
    """
    try:
        payload = jwt.decode(token, SHARED_SECRET, algorithms=["HS256"])
        
        # Vérifier si le service est dans la liste des services autorisés
        if allowed_services and payload.get("service") not in allowed_services:
            return False, {}
        
        return True, payload
    except jwt.ExpiredSignatureError:
        return False, {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return False, {"error": "Invalid token"}

def extract_user_permissions(user_token: str) -> Dict[str, Any]:
    """Extrait les informations utilisateur et les permissions depuis un token JWT.
    
    Args:
        user_token: Token JWT utilisateur
        
    Returns:
        Dictionnaire contenant les informations utilisateur et permissions
    """
    try:
        # Note: La clé secrète devrait être la même que celle utilisée par le service d'identité
        identity_secret = os.environ.get("JWT_SECRET_KEY", "dev-key-not-for-production")
        payload = jwt.decode(user_token, identity_secret, algorithms=["HS256"])
        
        # Extraire les informations utilisateur
        user_info = payload.get("sub", {})
        
        # Extraire les permissions si présentes
        permissions = payload.get("permissions", [])
        
        return {
            "user_id": user_info.get("id"),
            "email": user_info.get("email"),
            "user_type": user_info.get("user_type"),
            "permissions": permissions
        }
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}
    except Exception as e:
        return {"error": str(e)}