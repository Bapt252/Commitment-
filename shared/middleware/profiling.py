"""Middleware de profiling pour FastAPI."""
import time
import psutil
import tracemalloc
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import structlog

# Configuration du logger structuré
logger = structlog.get_logger(__name__)


class ProfilingMiddleware(BaseHTTPMiddleware):
    """Middleware pour mesurer les performances des requêtes."""

    def __init__(self, app, enable_memory_profiling: bool = True):
        super().__init__(app)
        self.enable_memory_profiling = enable_memory_profiling
        self.process = psutil.Process()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Démarrage du profiling
        start_time = time.time()
        start_cpu = self.process.cpu_percent()
        start_memory = self.process.memory_info().rss
        
        # Profiling mémoire optionnel
        if self.enable_memory_profiling:
            tracemalloc.start()
        
        # Traitement de la requête
        response = await call_next(request)
        
        # Calcul des métriques
        process_time = time.time() - start_time
        end_cpu = self.process.cpu_percent()
        end_memory = self.process.memory_info().rss
        memory_diff = end_memory - start_memory
        
        # Métriques mémoire
        peak_memory = 0
        if self.enable_memory_profiling:
            current, peak = tracemalloc.get_traced_memory()
            peak_memory = peak
            tracemalloc.stop()
        
        # Log des métriques avec structlog
        logger.info(
            "Request processed",
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            process_time_ms=round(process_time * 1000, 2),
            cpu_usage_percent=round(end_cpu - start_cpu, 2),
            memory_diff_mb=round(memory_diff / (1024 * 1024), 2),
            peak_memory_mb=round(peak_memory / (1024 * 1024), 2) if peak_memory else 0,
            user_agent=request.headers.get("user-agent", ""),
            request_size=len(await request.body()) if hasattr(request, "body") else 0
        )
        
        # Ajout des headers de performance
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        response.headers["X-Memory-Peak"] = str(peak_memory) if peak_memory else "0"
        response.headers["X-Memory-Diff"] = str(memory_diff)
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware pour logger toutes les requêtes."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log de la requête entrante
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent", "")
        )
        
        try:
            response = await call_next(request)
            
            # Log de la réponse
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                response_size=len(getattr(response, "body", b""))
            )
            
            return response
            
        except Exception as e:
            # Log des erreurs
            logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__
            )
            raise


class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Middleware pour gérer les health checks sans logging excessif."""

    def __init__(self, app, health_check_paths: list = None):
        super().__init__(app)
        self.health_check_paths = health_check_paths or ["/health", "/healthz", "/metrics"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Bypass pour les health checks
        if request.url.path in self.health_check_paths:
            return await call_next(request)
        
        # Pour toutes les autres requêtes, continuer normalement
        return await call_next(request)