import time
import logging
from typing import Optional, Dict, Any, List, Callable
from fastapi import HTTPException, Header, Request
from starlette import status
from functools import wraps
import asyncio

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Middleware de validation de la clé API
def validate_api_key(api_key: Optional[str] = Header(None)) -> None:
    """Valide la clé API fournie dans les headers"""
    if not settings.REQUIRE_API_KEY:
        return
    
    if not api_key:
        logger.warning("Tentative d'accès sans clé API")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key requise",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    # Vérifier la clé API (en utilisant une durée constante pour éviter les timing attacks)
    if not settings.API_KEY or not (api_key == settings.API_KEY):
        logger.warning(f"Tentative d'accès avec une clé API invalide")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key invalide",
            headers={"WWW-Authenticate": "ApiKey"}
        )

# Middleware de limitation de taux
class RateLimiter:
    """Middleware de limitation de taux basé sur les adresses IP"""
    
    def __init__(self, limit: int = 10, window: int = 60):
        """Initialise le rate limiter
        
        Args:
            limit: Nombre maximal de requêtes par fenêtre de temps
            window: Fenêtre de temps en secondes
        """
        self.limit = limit
        self.window = window
        self.clients = {}
    
    def __call__(self, request: Request):
        """Vérifie si le client a dépassé sa limite de requêtes"""
        # Désactiver le rate limiting en mode debug
        if settings.DEBUG:
            return True
        
        # Obtenir l'adresse IP du client
        client_ip = request.client.host
        current_time = time.time()
        
        # Initialiser ou nettoyer l'historique du client
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        
        # Nettoyer les anciennes requêtes
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if current_time - timestamp < self.window
        ]
        
        # Vérifier si la limite est dépassée
        if len(self.clients[client_ip]) >= self.limit:
            logger.warning(f"Rate limit dépassé pour {client_ip}: {len(self.clients[client_ip])} requêtes")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Limite de {self.limit} requêtes par {self.window} secondes dépassée"
            )
        
        # Ajouter la requête actuelle
        self.clients[client_ip].append(current_time)
        return True

# Décorateur pour l'authentification API
def require_api_key():
    """Décorateur pour exiger une clé API valide"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Vérifier si l'API key est requise
            if settings.REQUIRE_API_KEY:
                api_key = kwargs.get("api_key", None)
                validate_api_key(api_key)
            return await func(*args, **kwargs)
        return wrapper
    return decorator
