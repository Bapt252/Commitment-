"""
Middleware personnalisés pour SuperSmartMatch V2

Middleware pour :
- Logging des requêtes/réponses
- Monitoring de performance
- Rate limiting
- Gestion d'erreurs
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import asyncio
from typing import Dict, Any
import json

from .logger import RequestLogger, get_logger
from .config import get_config

config = get_config()
request_logger = RequestLogger()
logger = get_logger(__name__)

# Stockage en mémoire pour rate limiting (en production, utiliser Redis)
rate_limit_storage: Dict[str, Dict[str, Any]] = {}

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware de logging des requêtes et réponses"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Logger la requête entrante
        request_logger.log_request(
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_ip=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown")
        )
        
        response = await call_next(request)
        
        # Calculer la durée
        duration_ms = (time.time() - start_time) * 1000
        
        # Logger la réponse
        request_logger.log_response(
            status_code=response.status_code,
            duration_ms=duration_ms,
            response_size=response.headers.get("content-length", "unknown")
        )
        
        # Ajouter des headers de performance
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"
        response.headers["X-Service-Version"] = "2.0.0"
        
        return response

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware de monitoring des performances"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.performance_data = {
            "total_requests": 0,
            "total_response_time": 0,
            "slow_requests": 0,
            "error_requests": 0
        }
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculer les métriques
            duration_ms = (time.time() - start_time) * 1000
            
            # Mettre à jour les statistiques
            self.performance_data["total_requests"] += 1
            self.performance_data["total_response_time"] += duration_ms
            
            # Détecter les requêtes lentes
            if duration_ms > config.max_response_time_ms:
                self.performance_data["slow_requests"] += 1
                logger.warning(
                    "Slow request detected",
                    path=request.url.path,
                    duration_ms=duration_ms,
                    threshold_ms=config.max_response_time_ms
                )
            
            # Détecter les erreurs
            if response.status_code >= 400:
                self.performance_data["error_requests"] += 1
            
            # Ajouter les métriques aux headers
            response.headers["X-Performance-Total-Requests"] = str(self.performance_data["total_requests"])
            avg_time = self.performance_data["total_response_time"] / self.performance_data["total_requests"]
            response.headers["X-Performance-Avg-Time"] = f"{avg_time:.2f}ms"
            
            return response
            
        except Exception as e:
            self.performance_data["error_requests"] += 1
            duration_ms = (time.time() - start_time) * 1000
            
            logger.error(
                "Request processing error",
                path=request.url.path,
                duration_ms=duration_ms,
                error=str(e)
            )
            
            raise

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware de limitation de taux"""
    
    async def dispatch(self, request: Request, call_next):
        if not config.enable_circuit_breaker:  # Utiliser le flag pour désactiver
            return await call_next(request)
        
        # Identifier le client (IP + User-Agent)
        client_id = f"{request.client.host if request.client else 'unknown'}_{request.headers.get('user-agent', 'unknown')}"
        current_time = time.time()
        
        # Initialiser les données du client si nécessaire
        if client_id not in rate_limit_storage:
            rate_limit_storage[client_id] = {
                "minute_requests": [],
                "hour_requests": []
            }
        
        client_data = rate_limit_storage[client_id]
        
        # Nettoyer les anciennes requêtes
        client_data["minute_requests"] = [
            req_time for req_time in client_data["minute_requests"]
            if current_time - req_time < 60
        ]
        client_data["hour_requests"] = [
            req_time for req_time in client_data["hour_requests"]
            if current_time - req_time < 3600
        ]
        
        # Vérifier les limites
        if len(client_data["minute_requests"]) >= config.rate_limit_per_minute:
            logger.warning(
                "Rate limit exceeded (per minute)",
                client_id=client_id,
                requests_count=len(client_data["minute_requests"]),
                limit=config.rate_limit_per_minute
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": True,
                    "message": "Rate limit exceeded - too many requests per minute",
                    "retry_after": 60
                }
            )
        
        if len(client_data["hour_requests"]) >= config.rate_limit_per_hour:
            logger.warning(
                "Rate limit exceeded (per hour)",
                client_id=client_id,
                requests_count=len(client_data["hour_requests"]),
                limit=config.rate_limit_per_hour
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": True,
                    "message": "Rate limit exceeded - too many requests per hour",
                    "retry_after": 3600
                }
            )
        
        # Enregistrer la requête
        client_data["minute_requests"].append(current_time)
        client_data["hour_requests"].append(current_time)
        
        response = await call_next(request)
        
        # Ajouter les headers de rate limiting
        response.headers["X-RateLimit-Limit-Minute"] = str(config.rate_limit_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            max(0, config.rate_limit_per_minute - len(client_data["minute_requests"]))
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(config.rate_limit_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            max(0, config.rate_limit_per_hour - len(client_data["hour_requests"]))
        )
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware de gestion centralisée des erreurs"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
            
        except asyncio.TimeoutError:
            logger.error(
                "Request timeout",
                path=request.url.path,
                method=request.method
            )
            return JSONResponse(
                status_code=504,
                content={
                    "error": True,
                    "message": "Request timeout - service temporarily unavailable",
                    "status_code": 504,
                    "timestamp": int(time.time())
                }
            )
            
        except Exception as e:
            logger.error(
                "Unhandled middleware error",
                path=request.url.path,
                method=request.method,
                error=str(e),
                exc_info=True
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "message": "Internal server error",
                    "status_code": 500,
                    "timestamp": int(time.time())
                }
            )