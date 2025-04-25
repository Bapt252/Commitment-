"""
Middleware de sécurité pour le service de parsing CV.
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
    """Middleware pour ajouter les headers de sécurité."""
    
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

def setup_middleware(app: FastAPI, allowed_origins: list = None):
    """Configure les middlewares de sécurité."""
    
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
    
    logger.info("Security middleware configured for CV parser service")