"""
Middleware de sécurité pour l'API NexTen.
Gère les headers de sécurité, CORS et la protection contre les attaques courantes.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware pour ajouter les headers de sécurité à toutes les réponses."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Headers de sécurité
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Headers de monitoring
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware simple de rate limiting."""
    
    def __init__(self, app: FastAPI, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host
        current_minute = int(time.time() / 60)
        
        # Nettoyer les anciennes entrées
        self.request_counts = {
            k: v for k, v in self.request_counts.items() 
            if k[1] == current_minute
        }
        
        key = (client_ip, current_minute)
        self.request_counts[key] = self.request_counts.get(key, 0) + 1
        
        if self.request_counts[key] > self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": "60"}
            )
        
        return await call_next(request)

def setup_middleware(app: FastAPI, allowed_origins: list = None):
    """Configure tous les middlewares pour l'application."""
    
    # CORS
    if allowed_origins is None:
        allowed_origins = ["*"]  # En production, spécifier les domaines autorisés
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Content-Range", "X-Content-Range"]
    )
    
    # Headers de sécurité
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Rate limiting (ajustez selon vos besoins)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
    
    logger.info("Security middleware configured successfully")