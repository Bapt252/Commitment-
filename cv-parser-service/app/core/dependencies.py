# CV Parser Service - Dépendances FastAPI

import time
import logging
from fastapi import HTTPException, Header, Request, Depends
from starlette import status
from typing import Optional, Dict, Any, List, Callable
from fastapi.security.api_key import APIKeyHeader

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Rate limiting
class RateLimiter:
    """Limiteur de débit pour les requêtes API"""
    
    def __init__(self, limit: int = 10, window: int = 60):
        """Initialisation du limiteur de débit
        
        Args:
            limit: Nombre maximum de requêtes
            window: Période de temps en secondes
        """
        self.limit = limit
        self.window = window
        self.clients: Dict[str, List[float]] = {}
    
    def __call__(self, request: Request) -> bool:
        """Vérifier si la requête respecte les limites
        
        Args:
            request: Requête FastAPI
            
        Returns:
            bool: True si la requête est autorisée
            
        Raises:
            HTTPException: Si la limite est dépassée
        """
        # Ignorer la limitation si elle est désactivée
        if not settings.RATE_LIMIT_ENABLED:
            return True
            
        # Identifier le client (IP ou identifiant)
        client_id = request.client.host
        
        # Timestamp actuel
        now = time.time()
        
        # Créer ou nettoyer l'historique du client
        if client_id not in self.clients:
            self.clients[client_id] = [now]
            return True
            
        # Nettoyer les timestamps expirés
        self.clients[client_id] = [
            ts for ts in self.clients[client_id] if now - ts < self.window
        ]
        
        # Vérifier si la limite est dépassée
        if len(self.clients[client_id]) >= self.limit:
            oldest = min(self.clients[client_id])
            reset_time = oldest + self.window - now
            logger.warning(f"Rate limit dépassé pour {client_id}: {len(self.clients[client_id])} requêtes")
            
            headers = {"X-RateLimit-Limit": str(self.limit),
                      "X-RateLimit-Remaining": "0",
                      "X-RateLimit-Reset": str(int(reset_time))}
                      
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Trop de requêtes. Réessayez dans {int(reset_time)} secondes.",
                headers=headers
            )
        
        # Ajouter le timestamp actuel
        self.clients[client_id].append(now)
        
        # Headers d'information
        remaining = self.limit - len(self.clients[client_id])
        request.state.rate_limit_remaining = remaining
        
        return True

# Validation de clé API
def validate_api_key(api_key: Optional[str] = Header(None)) -> bool:
    """Valide la clé API fournie dans les headers"""
    # Ignorer la validation si désactivée
    if not settings.REQUIRE_API_KEY:
        return True
        
    # Vérifier si une clé API est requise mais non fournie
    if not api_key:
        logger.warning("Tentative d'accès sans clé API")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API manquante"
        )
    
    # Vérifier si la clé API est valide
    if api_key != settings.API_KEY:
        logger.warning(f"Tentative d'accès avec une clé API invalide: {api_key[:5]}...")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clé API invalide"
        )
    
    return True
