"""
Middleware de logging pour l'API Gateway
Logging détaillé des requêtes avec métriques de performance
"""

import time
import json
import logging
import uuid
from typing import Dict, Any
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Logger spécialisé pour les métriques
metrics_logger = logging.getLogger("supersmartmatch.metrics")
metrics_logger.setLevel(logging.INFO)

# Handler pour les métriques en format JSON
if not metrics_logger.handlers:
    metrics_handler = logging.StreamHandler()
    metrics_formatter = logging.Formatter(
        '%(asctime)s - METRICS - %(message)s'
    )
    metrics_handler.setFormatter(metrics_formatter)
    metrics_logger.addHandler(metrics_handler)
    metrics_logger.propagate = False

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware pour le logging détaillé des requêtes"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.sensitive_headers = {
            "authorization", "cookie", "x-api-key", 
            "x-auth-token", "x-csrf-token"
        }
        self.sensitive_paths = {
            "/api/gateway/auth/login",
            "/api/gateway/auth/register"
        }
    
    async def dispatch(self, request: Request, call_next):
        """Logger chaque requête avec métriques détaillées"""
        
        # Générer un ID unique pour cette requête
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Extraire les informations de la requête
        request_info = await self._extract_request_info(request, request_id)
        
        # Logger le début de la requête
        logger.info(f"[{request_id}] {request.method} {request.url.path} - START")
        
        try:
            # Traiter la requête
            response = await call_next(request)
            
            # Calculer le temps de traitement
            process_time = time.time() - start_time
            
            # Extraire les informations de la réponse
            response_info = self._extract_response_info(response, process_time)
            
            # Logger la fin de la requête
            log_level = self._get_log_level(response.status_code)
            log_message = f"[{request_id}] {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)"
            
            logger.log(log_level, log_message)
            
            # Logger les métriques détaillées
            await self._log_metrics(request_info, response_info, request_id)
            
            # Ajouter des headers de debugging
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            
            return response
            
        except Exception as e:
            # Logger les erreurs
            process_time = time.time() - start_time
            error_message = f"[{request_id}] {request.method} {request.url.path} - ERROR: {str(e)} ({process_time:.3f}s)"
            logger.error(error_message, exc_info=True)
            
            # Logger les métriques d'erreur
            error_info = {
                "status_code": 500,
                "error": str(e),
                "process_time": process_time
            }
            await self._log_metrics(request_info, error_info, request_id)
            
            raise
    
    async def _extract_request_info(self, request: Request, request_id: str) -> Dict[str, Any]:
        """Extraire les informations pertinentes de la requête"""
        
        # Headers (filtrer les données sensibles)
        headers = dict(request.headers)
        filtered_headers = {
            k: "***FILTERED***" if k.lower() in self.sensitive_headers else v
            for k, v in headers.items()
        }
        
        # Informations utilisateur si disponible
        user_info = None
        if hasattr(request.state, "user") and request.state.user:
            user_info = {
                "id": request.state.user.get("id"),
                "email": request.state.user.get("email"),
                "role": request.state.user.get("role")
            }
        
        # Body size (sans lire le contenu pour éviter les problèmes)
        content_length = request.headers.get("content-length")
        body_size = int(content_length) if content_length else 0
        
        return {
            "request_id": request_id,
            "timestamp": time.time(),
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": filtered_headers,
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "user_info": user_info,
            "body_size": body_size,
            "is_sensitive_path": request.url.path in self.sensitive_paths
        }
    
    def _extract_response_info(self, response: Response, process_time: float) -> Dict[str, Any]:
        """Extraire les informations de la réponse"""
        
        # Headers de réponse (filtrer les données sensibles)
        response_headers = dict(response.headers)
        
        # Taille du body de réponse
        content_length = response_headers.get("content-length")
        response_size = int(content_length) if content_length else 0
        
        return {
            "status_code": response.status_code,
            "headers": response_headers,
            "response_size": response_size,
            "process_time": process_time,
            "content_type": response_headers.get("content-type")
        }
    
    def _get_log_level(self, status_code: int) -> int:
        """Déterminer le niveau de log selon le code de status"""
        if status_code < 400:
            return logging.INFO
        elif status_code < 500:
            return logging.WARNING
        else:
            return logging.ERROR
    
    async def _log_metrics(self, request_info: Dict, response_info: Dict, request_id: str):
        """Logger les métriques détaillées en format JSON"""
        
        try:
            # Calculer des métriques dérivées
            is_success = response_info.get("status_code", 500) < 400
            is_slow = response_info.get("process_time", 0) > 1.0
            
            # Catégoriser l'endpoint
            endpoint_category = self._categorize_endpoint(request_info["path"])
            
            metrics_data = {
                "request_id": request_id,
                "timestamp": request_info["timestamp"],
                "method": request_info["method"],
                "endpoint": request_info["path"],
                "endpoint_category": endpoint_category,
                "status_code": response_info.get("status_code"),
                "process_time": response_info.get("process_time"),
                "request_size": request_info["body_size"],
                "response_size": response_info.get("response_size", 0),
                "user_id": request_info["user_info"]["id"] if request_info["user_info"] else None,
                "user_role": request_info["user_info"]["role"] if request_info["user_info"] else None,
                "client_ip": request_info["client_ip"],
                "user_agent": request_info["user_agent"],
                "is_success": is_success,
                "is_slow": is_slow,
                "is_authenticated": request_info["user_info"] is not None,
                "content_type": response_info.get("content_type"),
                "error": response_info.get("error")
            }
            
            # Logger en format JSON pour parsing facile
            metrics_logger.info(json.dumps(metrics_data, default=str))
            
            # Logger des alertes pour des métriques critiques
            await self._check_for_alerts(metrics_data)
            
        except Exception as e:
            logger.error(f"Erreur logging métriques: {e}")
    
    def _categorize_endpoint(self, path: str) -> str:
        """Catégoriser un endpoint pour les métriques"""
        
        if path.startswith("/api/gateway/auth"):
            return "authentication"
        elif path.startswith("/api/gateway/parse"):
            return "parsing"
        elif path.startswith("/api/gateway/match"):
            return "matching"
        elif path.startswith("/api/gateway/health"):
            return "monitoring"
        else:
            return "other"
    
    async def _check_for_alerts(self, metrics_data: Dict):
        """Vérifier des métriques qui nécessitent des alertes"""
        
        # Alertes pour les requêtes lentes
        if metrics_data["is_slow"]:
            logger.warning(
                f"SLOW_REQUEST: {metrics_data['endpoint']} took {metrics_data['process_time']:.3f}s "
                f"for user {metrics_data['user_id'] or 'anonymous'}"
            )
        
        # Alertes pour les erreurs server
        if metrics_data["status_code"] and metrics_data["status_code"] >= 500:
            logger.error(
                f"SERVER_ERROR: {metrics_data['endpoint']} returned {metrics_data['status_code']} "
                f"for user {metrics_data['user_id'] or 'anonymous'}"
            )
        
        # Alertes pour les gros uploads
        if metrics_data["request_size"] > 10 * 1024 * 1024:  # > 10MB
            logger.warning(
                f"LARGE_UPLOAD: {metrics_data['endpoint']} received {metrics_data['request_size']} bytes "
                f"from user {metrics_data['user_id'] or 'anonymous'}"
            )

class MetricsCollector:
    """Collecteur de métriques pour analyses"""
    
    def __init__(self):
        self.metrics_cache = {}
    
    @staticmethod
    def get_request_summary(minutes: int = 60) -> Dict[str, Any]:
        """Obtenir un résumé des requêtes sur une période"""
        # Cette méthode nécessiterait une intégration avec une base de données
        # ou un système de métriques comme Prometheus pour être complètement fonctionnelle
        return {
            "message": "Métriques de résumé à implémenter",
            "suggestion": "Intégrer avec Prometheus ou une base de données time-series"
        }
    
    @staticmethod
    def get_error_rate(minutes: int = 60) -> float:
        """Calculer le taux d'erreur sur une période"""
        # Placeholder - nécessite une implémentation complète
        return 0.05  # 5% d'erreurs par exemple
    
    @staticmethod
    def get_average_response_time(minutes: int = 60) -> float:
        """Calculer le temps de réponse moyen"""
        # Placeholder - nécessite une implémentation complète
        return 0.250  # 250ms par exemple

# Instance globale du collecteur de métriques
metrics_collector = MetricsCollector()
