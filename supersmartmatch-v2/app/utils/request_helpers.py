"""
Utilitaires pour les requêtes HTTP

Fournit des helpers pour :
- Génération d'IDs de requête
- Validation de taille
- Middleware de traçabilité
- Gestion des timeouts
"""

import uuid
import time
import logging
from typing import Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


def generate_request_id() -> str:
    """
    Génère un ID unique pour une requête
    
    Returns:
        ID de requête unique
    """
    return f"ssm2-{uuid.uuid4().hex[:12]}-{int(time.time())}"


def validate_request_size(data: Dict[str, Any], max_size_mb: float = 10.0) -> tuple[bool, Optional[str]]:
    """
    Valide la taille d'une requête
    
    Args:
        data: Données de la requête
        max_size_mb: Taille maximum en MB
        
    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        import json
        import sys
        
        # Estimation de la taille en mémoire
        json_str = json.dumps(data, default=str)
        size_bytes = len(json_str.encode('utf-8'))
        size_mb = size_bytes / (1024 * 1024)
        
        if size_mb > max_size_mb:
            return False, f"Requête trop volumineuse: {size_mb:.2f}MB (max: {max_size_mb}MB)"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Erreur validation taille: {e}")
        return True, None  # En cas d'erreur, on laisse passer


def timing_decorator(func):
    """
    Décorateur pour mesurer le temps d'exécution
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.debug(f"⏱️ {func.__name__} executed in {duration:.1f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"❌ {func.__name__} failed after {duration:.1f}ms: {e}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000
            logger.debug(f"⏱️ {func.__name__} executed in {duration:.1f}ms")
            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(f"❌ {func.__name__} failed after {duration:.1f}ms: {e}")
            raise
    
    # Retourner le wrapper approprié selon le type de fonction
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class RequestTracker:
    """
    Trackeur de requêtes pour le monitoring
    """
    
    def __init__(self):
        self.active_requests: Dict[str, Dict[str, Any]] = {}
        self.completed_requests: list = []
        self.max_history = 1000
    
    def start_request(self, request_id: str, endpoint: str, **metadata) -> None:
        """
        Démarre le tracking d'une requête
        
        Args:
            request_id: ID unique de la requête
            endpoint: Endpoint appelé
            **metadata: Métadonnées additionnelles
        """
        self.active_requests[request_id] = {
            "request_id": request_id,
            "endpoint": endpoint,
            "start_time": time.time(),
            "metadata": metadata
        }
        
        logger.debug(f"🚀 Request started: {request_id} -> {endpoint}")
    
    def end_request(self, request_id: str, success: bool = True, **result_metadata) -> Optional[Dict[str, Any]]:
        """
        Termine le tracking d'une requête
        
        Args:
            request_id: ID de la requête
            success: Succès ou échec
            **result_metadata: Métadonnées du résultat
            
        Returns:
            Informations de la requête complétée
        """
        if request_id not in self.active_requests:
            logger.warning(f"⚠️ Request ID not found: {request_id}")
            return None
        
        request_info = self.active_requests.pop(request_id)
        end_time = time.time()
        duration = end_time - request_info["start_time"]
        
        completed_info = {
            **request_info,
            "end_time": end_time,
            "duration_seconds": duration,
            "success": success,
            "result_metadata": result_metadata
        }
        
        # Ajouter à l'historique
        self.completed_requests.append(completed_info)
        
        # Limiter la taille de l'historique
        if len(self.completed_requests) > self.max_history:
            self.completed_requests = self.completed_requests[-self.max_history:]
        
        status_emoji = "✅" if success else "❌"
        logger.info(
            f"{status_emoji} Request completed: {request_id} in {duration*1000:.1f}ms",
            extra={
                "request_id": request_id,
                "duration_ms": duration * 1000,
                "success": success,
                "endpoint": request_info["endpoint"]
            }
        )
        
        return completed_info
    
    def get_active_requests(self) -> Dict[str, Dict[str, Any]]:
        """
        Retourne les requêtes actives
        """
        return self.active_requests.copy()
    
    def get_request_stats(self, hours: int = 1) -> Dict[str, Any]:
        """
        Retourne les statistiques des requêtes
        
        Args:
            hours: Période en heures
            
        Returns:
            Statistiques des requêtes
        """
        cutoff_time = time.time() - (hours * 3600)
        recent_requests = [
            req for req in self.completed_requests
            if req["end_time"] >= cutoff_time
        ]
        
        if not recent_requests:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "average_duration_ms": 0.0,
                "active_requests": len(self.active_requests)
            }
        
        successful = [req for req in recent_requests if req["success"]]
        failed = [req for req in recent_requests if not req["success"]]
        
        total_duration = sum(req["duration_seconds"] for req in recent_requests)
        avg_duration = total_duration / len(recent_requests)
        
        return {
            "total_requests": len(recent_requests),
            "successful_requests": len(successful),
            "failed_requests": len(failed),
            "success_rate": len(successful) / len(recent_requests),
            "average_duration_ms": avg_duration * 1000,
            "max_duration_ms": max(req["duration_seconds"] for req in recent_requests) * 1000,
            "min_duration_ms": min(req["duration_seconds"] for req in recent_requests) * 1000,
            "active_requests": len(self.active_requests),
            "period_hours": hours
        }


# Instance globale du tracker
request_tracker = RequestTracker()


class RequestContextMiddleware:
    """
    Middleware pour ajouter le contexte de requête
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Générer un ID de requête
            request_id = generate_request_id()
            
            # Ajouter à l'état de la requête
            if "state" not in scope:
                scope["state"] = {}
            scope["state"]["request_id"] = request_id
            
            # Tracking
            path = scope.get("path", "unknown")
            request_tracker.start_request(request_id, path)
        
        await self.app(scope, receive, send)


def get_request_context() -> Dict[str, Any]:
    """
    Récupère le contexte de la requête courante
    
    Returns:
        Contexte de la requête
    """
    # Cette fonction serait utilisée avec un contexte de requête FastAPI
    # Pour l'instant, retourne un contexte basique
    return {
        "request_id": generate_request_id(),
        "timestamp": time.time()
    }
