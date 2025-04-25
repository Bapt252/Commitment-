import os
import jwt
import time
import secrets
from typing import Dict, Any, Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)

# Clé secrète partagée pour les JWT inter-services
# Utilisez une variable d'environnement ou générez une clé aléatoire unique à chaque démarrage
# ATTENTION : En production, utilisez TOUJOURS des variables d'environnement 
# pour les secrets et NE PAS utiliser de valeurs par défaut
SHARED_SECRET = os.environ.get("SERVICES_JWT_SECRET")
if not SHARED_SECRET:
    # Pour le développement uniquement, générer une clé aléatoire
    if os.environ.get("ENV", "development") == "production":
        raise EnvironmentError("SERVICES_JWT_SECRET doit être définie en production")
    else:
        SHARED_SECRET = secrets.token_hex(32)
        logger.warning(
            "ATTENTION: Utilisation d'une clé JWT aléatoire pour l'authentification inter-services. "
            "Cette clé changera à chaque redémarrage. "
            "En production, définissez SERVICES_JWT_SECRET."
        )

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
        # La clé secrète doit être fournie via une variable d'environnement
        identity_secret = os.environ.get("JWT_SECRET_KEY")
        if not identity_secret:
            if os.environ.get("ENV", "development") == "production":
                raise EnvironmentError("JWT_SECRET_KEY doit être définie en production")
            else:
                # Pour le développement uniquement, utiliser une clé temporaire
                identity_secret = secrets.token_hex(32)
                logger.warning(
                    "ATTENTION: Utilisation d'une clé JWT aléatoire pour la validation des tokens utilisateur. "
                    "Cette clé changera à chaque redémarrage. "
                    "En production, définissez JWT_SECRET_KEY."
                )
                
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