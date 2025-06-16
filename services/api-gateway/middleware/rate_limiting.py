"""
Middleware de rate limiting pour l'API Gateway
Protection contre les abus et surcharge avec Redis
"""

import time
import redis
import logging
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Connection Redis pour le rate limiting
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    logger.info("Connexion Redis pour rate limiting établie")
except Exception as e:
    logger.error(f"Erreur connexion Redis rate limiting: {e}")
    redis_client = None

class RateLimitConfig:
    """Configuration du rate limiting"""
    
    def __init__(self):
        # Limites par défaut (requêtes par minute)
        self.default_limit = settings.RATE_LIMIT_PER_MINUTE
        self.default_window = 60  # secondes
        
        # Limites spécifiques par endpoint
        self.endpoint_limits = {
            # Authentification - plus strict
            "/api/gateway/auth/login": (10, 60),  # 10 req/min
            "/api/gateway/auth/register": (5, 60),  # 5 req/min
            
            # Parsing - modéré (fichiers lourds)
            "/api/gateway/parse-cv": (20, 60),  # 20 req/min
            "/api/gateway/parse-job": (30, 60),  # 30 req/min
            "/api/gateway/parse-job/batch": (5, 60),  # 5 req/min
            
            # Matching - normal
            "/api/gateway/match": (50, 60),  # 50 req/min
            "/api/gateway/match/batch": (10, 60),  # 10 req/min
            
            # Health checks - très permissif
            "/api/gateway/health": (120, 60),  # 120 req/min
            "/api/gateway/status": (300, 60),  # 300 req/min
        }
        
        # Limites par rôle utilisateur
        self.role_limits = {
            "candidat": (50, 60),    # 50 req/min
            "recruteur": (200, 60),  # 200 req/min
            "admin": (1000, 60)      # 1000 req/min
        }
        
        # Burst allowance
        self.burst_allowance = settings.RATE_LIMIT_BURST

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de rate limiting avec algorithme token bucket"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.config = RateLimitConfig()
        
    async def dispatch(self, request: Request, call_next):
        """Vérifier les limites de taux pour chaque requête"""
        
        # Skip rate limiting pour certaines routes critiques
        if request.url.path in ["/api/gateway/health", "/api/gateway/status"]:
            return await call_next(request)
        
        if not redis_client:
            logger.warning("Redis indisponible, rate limiting désactivé")
            return await call_next(request)
        
        try:
            # Identifier le client
            client_id = await self._get_client_identifier(request)
            
            # Obtenir les limites pour cette requête
            limit, window = self._get_limits_for_request(request)
            
            # Vérifier les limites
            allowed = await self._check_rate_limit(client_id, limit, window, request.url.path)
            
            if not allowed:
                # Préparer les headers de rate limiting
                headers = await self._get_rate_limit_headers(client_id, limit, window, request.url.path)
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": True,
                        "message": "Trop de requêtes",
                        "code": "RATE_LIMIT_EXCEEDED",
                        "retry_after": window
                    },
                    headers=headers
                )
            
            # Traiter la requête
            response = await call_next(request)
            
            # Ajouter les headers de rate limiting à la réponse
            headers = await self._get_rate_limit_headers(client_id, limit, window, request.url.path)
            for key, value in headers.items():
                response.headers[key] = value
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur rate limiting middleware: {e}")
            # En cas d'erreur, laisser passer (fail open)
            return await call_next(request)
    
    async def _get_client_identifier(self, request: Request) -> str:
        """Identifier le client (utilisateur ou IP)"""
        
        # Si utilisateur authentifié, utiliser son ID
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user['id']}"
        
        # Sinon, utiliser l'IP
        client_ip = request.client.host
        
        # Check pour X-Forwarded-For (proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Check pour X-Real-IP (nginx)
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            client_ip = real_ip
        
        return f"ip:{client_ip}"
    
    def _get_limits_for_request(self, request: Request) -> tuple[int, int]:
        """Obtenir les limites pour une requête donnée"""
        
        path = request.url.path
        
        # Limites spécifiques par endpoint
        if path in self.config.endpoint_limits:
            return self.config.endpoint_limits[path]
        
        # Limites par rôle utilisateur
        if hasattr(request.state, "user") and request.state.user:
            role = request.state.user.get("role", "candidat")
            if role in self.config.role_limits:
                return self.config.role_limits[role]
        
        # Limite par défaut
        return self.config.default_limit, self.config.default_window
    
    async def _check_rate_limit(self, client_id: str, limit: int, window: int, path: str) -> bool:
        """Vérifier si le client dépasse les limites (token bucket algorithm)"""
        
        try:
            current_time = int(time.time())
            key = f"rate_limit:{client_id}:{path}"
            
            # Obtenir les données actuelles
            pipe = redis_client.pipeline()
            pipe.hgetall(key)
            result = pipe.execute()
            
            bucket_data = result[0] if result and result[0] else {}
            
            # Initialiser le bucket s'il n'existe pas
            if not bucket_data:
                bucket_data = {
                    "tokens": str(limit),
                    "last_refill": str(current_time)
                }
            
            tokens = float(bucket_data.get("tokens", limit))
            last_refill = int(bucket_data.get("last_refill", current_time))
            
            # Calculer les tokens à ajouter depuis le dernier refill
            time_passed = current_time - last_refill
            tokens_to_add = (time_passed / window) * limit
            
            # Refill du bucket (max = limit + burst)
            max_tokens = limit + self.config.burst_allowance
            tokens = min(max_tokens, tokens + tokens_to_add)
            
            # Vérifier si on peut consommer un token
            if tokens >= 1:
                tokens -= 1
                allowed = True
            else:
                allowed = False
            
            # Mettre à jour le bucket dans Redis
            pipe = redis_client.pipeline()
            pipe.hset(key, mapping={
                "tokens": str(tokens),
                "last_refill": str(current_time)
            })
            pipe.expire(key, window * 2)  # TTL = 2 * window
            pipe.execute()
            
            return allowed
            
        except Exception as e:
            logger.error(f"Erreur vérification rate limit: {e}")
            return True  # Fail open
    
    async def _get_rate_limit_headers(self, client_id: str, limit: int, window: int, path: str) -> Dict[str, str]:
        """Obtenir les headers de rate limiting pour la réponse"""
        
        try:
            key = f"rate_limit:{client_id}:{path}"
            bucket_data = redis_client.hgetall(key)
            
            if bucket_data:
                tokens = float(bucket_data.get("tokens", limit))
                remaining = max(0, int(tokens))
            else:
                remaining = limit
            
            reset_time = int(time.time()) + window
            
            return {
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time),
                "X-RateLimit-Window": str(window)
            }
            
        except Exception as e:
            logger.error(f"Erreur headers rate limit: {e}")
            return {}

class RateLimitManager:
    """Gestionnaire pour les opérations de rate limiting"""
    
    @staticmethod
    async def reset_user_limits(user_id: str):
        """Réinitialiser les limites pour un utilisateur"""
        if not redis_client:
            return False
        
        try:
            pattern = f"rate_limit:user:{user_id}:*"
            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Erreur reset limits utilisateur: {e}")
            return False
    
    @staticmethod
    async def get_user_stats(user_id: str) -> Dict[str, Any]:
        """Obtenir les statistiques de rate limiting pour un utilisateur"""
        if not redis_client:
            return {}
        
        try:
            pattern = f"rate_limit:user:{user_id}:*"
            keys = redis_client.keys(pattern)
            
            stats = {}
            for key in keys:
                bucket_data = redis_client.hgetall(key)
                endpoint = key.split(":")[-1]
                stats[endpoint] = {
                    "tokens_remaining": float(bucket_data.get("tokens", 0)),
                    "last_refill": int(bucket_data.get("last_refill", 0))
                }
            
            return stats
        except Exception as e:
            logger.error(f"Erreur stats rate limiting: {e}")
            return {}
    
    @staticmethod
    async def block_ip(ip: str, duration: int = 3600):
        """Bloquer temporairement une IP"""
        if not redis_client:
            return False
        
        try:
            key = f"blocked_ip:{ip}"
            redis_client.setex(key, duration, "1")
            return True
        except Exception as e:
            logger.error(f"Erreur blocage IP: {e}")
            return False
    
    @staticmethod
    async def is_ip_blocked(ip: str) -> bool:
        """Vérifier si une IP est bloquée"""
        if not redis_client:
            return False
        
        try:
            key = f"blocked_ip:{ip}"
            return redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Erreur vérification IP bloquée: {e}")
            return False

# Instance globale du gestionnaire
rate_limit_manager = RateLimitManager()
