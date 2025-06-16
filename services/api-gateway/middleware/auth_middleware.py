"""
Middleware d'authentification JWT pour l'API Gateway
Vérification automatique des tokens sur toutes les routes protégées
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import jwt
import redis
import logging
from typing import Set

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Routes publiques qui n'ont pas besoin d'authentification
PUBLIC_PATHS: Set[str] = {
    "/api/gateway",
    "/api/gateway/health",
    "/api/gateway/status", 
    "/api/gateway/metrics",
    "/api/gateway/docs",
    "/api/gateway/redoc",
    "/api/gateway/openapi.json",
    "/api/gateway/auth/login",
    "/api/gateway/auth/register",
    "/api/gateway/auth/refresh",
    "/favicon.ico"
}

# Connection Redis pour blacklist
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    logger.info("Connexion Redis pour middleware auth établie")
except Exception as e:
    logger.error(f"Erreur connexion Redis middleware: {e}")
    redis_client = None

class JWTMiddleware(BaseHTTPMiddleware):
    """Middleware pour l'authentification JWT automatique"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Traiter chaque requête pour vérifier l'authentification"""
        
        # Vérifier si la route est publique
        path = request.url.path
        if path in PUBLIC_PATHS or path.startswith("/static/"):
            return await call_next(request)
        
        # Méthodes OPTIONS toujours autorisées (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        try:
            # Extraire le token d'autorisation
            authorization = request.headers.get("authorization")
            if not authorization:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": True,
                        "message": "Token d'autorisation requis",
                        "code": "MISSING_TOKEN"
                    }
                )
            
            # Format: "Bearer <token>"
            if not authorization.startswith("Bearer "):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": True,
                        "message": "Format d'autorisation invalide",
                        "code": "INVALID_TOKEN_FORMAT"
                    }
                )
            
            token = authorization.split(" ")[1]
            
            # Vérifier si le token est blacklisté
            if redis_client and redis_client.get(f"blacklist:{token}"):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": True,
                        "message": "Token révoqué",
                        "code": "TOKEN_REVOKED"
                    }
                )
            
            # Décoder et vérifier le token
            try:
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET,
                    algorithms=[settings.JWT_ALGORITHM]
                )
            except jwt.ExpiredSignatureError:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": True,
                        "message": "Token expiré",
                        "code": "TOKEN_EXPIRED"
                    }
                )
            except jwt.InvalidTokenError:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": True,
                        "message": "Token invalide",
                        "code": "INVALID_TOKEN"
                    }
                )
            
            # Vérifier que c'est bien un token d'accès
            if payload.get("type") != "access":
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": True,
                        "message": "Type de token invalide",
                        "code": "WRONG_TOKEN_TYPE"
                    }
                )
            
            # Ajouter les informations utilisateur à la requête
            request.state.user = {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role"),
                "token": token
            }
            
            logger.debug(f"Requête authentifiée pour {payload.get('email')}")
            
        except Exception as e:
            logger.error(f"Erreur middleware auth: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": True,
                    "message": "Erreur de vérification d'authentification",
                    "code": "AUTH_ERROR"
                }
            )
        
        # Continuer vers le handler de route
        response = await call_next(request)
        return response

def is_public_path(path: str) -> bool:
    """Vérifier si un chemin est public"""
    return path in PUBLIC_PATHS or path.startswith("/static/")

def extract_user_from_request(request: Request) -> dict:
    """Extraire les informations utilisateur de la requête"""
    if hasattr(request.state, "user"):
        return request.state.user
    return None

def require_role(required_role: str):
    """Décorateur pour vérifier le rôle utilisateur"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user = extract_user_from_request(request)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentification requise"
                )
            
            user_role = user.get("role", "")
            
            # Hiérarchie des rôles: admin > recruteur > candidat
            role_hierarchy = {
                "candidat": 1,
                "recruteur": 2,
                "admin": 3
            }
            
            user_level = role_hierarchy.get(user_role, 0)
            required_level = role_hierarchy.get(required_role, 999)
            
            if user_level < required_level:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Rôle {required_role} requis"
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

def get_current_user_from_state(request: Request) -> dict:
    """Obtenir l'utilisateur actuel depuis l'état de la requête"""
    user = extract_user_from_request(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non authentifié"
        )
    return user
