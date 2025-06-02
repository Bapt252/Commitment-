"""
Router Admin - Administration et monitoring SuperSmartMatch V2

Fonctionnalités d'administration :
- Monitoring des services
- Configuration en temps réel
- Circuit breakers
- Cache management
"""

from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Any, Dict, List, Optional
import time

from ..dependencies import get_service_orchestrator, get_admin_service
from ..logger import get_logger

router = APIRouter()
logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)

# Authentification simple (à remplacer par un système plus robuste)
async def verify_admin_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Vérification basique du token admin"""
    if not credentials or credentials.credentials != "admin-secret-token":
        raise HTTPException(status_code=401, detail="Admin access required")
    return credentials

@router.get("/dashboard")
async def admin_dashboard(
    admin_service = Depends(get_admin_service),
    _auth = Depends(verify_admin_token)
) -> Dict[str, Any]:
    """
    Dashboard administrateur avec vue d'ensemble
    """
    try:
        dashboard_data = await admin_service.get_dashboard_data()
        
        return {
            "timestamp": int(time.time()),
            "service_status": {
                "supersmartmatch_v2": "healthy",
                "nexten_matcher": dashboard_data.get("nexten_status", "unknown"),
                "supersmartmatch_v1": dashboard_data.get("v1_status", "unknown")
            },
            "current_load": {
                "requests_per_minute": dashboard_data.get("rpm", 0),
                "active_connections": dashboard_data.get("connections", 0),
                "queue_size": dashboard_data.get("queue_size", 0)
            },
            "performance_summary": {
                "avg_response_time_ms": dashboard_data.get("avg_response_time", 0),
                "success_rate_24h": dashboard_data.get("success_rate", 1.0),
                "precision_average": dashboard_data.get("precision", 0.91)
            },
            "algorithm_distribution": dashboard_data.get("algorithm_usage", {}),
            "alerts": dashboard_data.get("active_alerts", [])
        }
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(status_code=500, detail="Dashboard data unavailable")

@router.get("/services/status")
async def services_status(
    orchestrator = Depends(get_service_orchestrator),
    _auth = Depends(verify_admin_token)
) -> Dict[str, Any]:
    """
    Statut détaillé de tous les services externes
    """
    try:
        status = await orchestrator.check_all_services_health()
        
        return {
            "timestamp": int(time.time()),
            "services": {
                "nexten_matcher": {
                    "url": "http://matching-api:5052",
                    "status": status.get("nexten", {}).get("status", "unknown"),
                    "response_time_ms": status.get("nexten", {}).get("response_time", 0),
                    "last_success": status.get("nexten", {}).get("last_success"),
                    "circuit_breaker": status.get("nexten", {}).get("circuit_breaker", "closed")
                },
                "supersmartmatch_v1": {
                    "url": "http://supersmartmatch-service:5062",
                    "status": status.get("v1", {}).get("status", "unknown"),
                    "response_time_ms": status.get("v1", {}).get("response_time", 0),
                    "last_success": status.get("v1", {}).get("last_success"),
                    "circuit_breaker": status.get("v1", {}).get("circuit_breaker", "closed")
                },
                "redis_cache": {
                    "status": status.get("redis", {}).get("status", "unknown"),
                    "memory_usage": status.get("redis", {}).get("memory_usage", 0),
                    "connected_clients": status.get("redis", {}).get("clients", 0)
                }
            },
            "overall_health": "healthy" if all(
                s.get("status") == "healthy" for s in status.values()
            ) else "degraded"
        }
        
    except Exception as e:
        logger.error(f"Services status error: {e}")
        raise HTTPException(status_code=500, detail="Unable to check services status")

@router.post("/circuit-breaker/{service}/reset")
async def reset_circuit_breaker(
    service: str,
    orchestrator = Depends(get_service_orchestrator),
    _auth = Depends(verify_admin_token)
) -> Dict[str, Any]:
    """
    Réinitialiser le circuit breaker d'un service
    """
    try:
        if service not in ["nexten", "v1"]:
            raise HTTPException(status_code=400, detail="Invalid service name")
        
        result = await orchestrator.reset_circuit_breaker(service)
        
        logger.info(f"Circuit breaker reset for {service}", admin_action=True)
        
        return {
            "service": service,
            "action": "circuit_breaker_reset",
            "success": result,
            "timestamp": int(time.time()),
            "message": f"Circuit breaker for {service} has been reset"
        }
        
    except Exception as e:
        logger.error(f"Circuit breaker reset error: {e}")
        raise HTTPException(status_code=500, detail="Circuit breaker reset failed")

@router.post("/cache/clear")
async def clear_cache(
    cache_type: Optional[str] = None,
    admin_service = Depends(get_admin_service),
    _auth = Depends(verify_admin_token)
) -> Dict[str, Any]:
    """
    Vider le cache (total ou partiel)
    """
    try:
        result = await admin_service.clear_cache(cache_type)
        
        logger.info(f"Cache cleared", cache_type=cache_type, admin_action=True)
        
        return {
            "action": "cache_clear",
            "cache_type": cache_type or "all",
            "keys_cleared": result.get("keys_cleared", 0),
            "success": True,
            "timestamp": int(time.time())
        }
        
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail="Cache clear failed")

@router.get("/cache/stats")
async def cache_stats(
    admin_service = Depends(get_admin_service),
    _auth = Depends(verify_admin_token)
) -> Dict[str, Any]:
    """
    Statistiques du cache Redis
    """
    try:
        stats = await admin_service.get_cache_stats()
        
        return {
            "timestamp": int(time.time()),
            "cache_stats": {
                "total_keys": stats.get("total_keys", 0),
                "memory_usage_mb": stats.get("memory_usage_mb", 0),
                "hit_rate_24h": stats.get("hit_rate", 0),
                "miss_rate_24h": stats.get("miss_rate", 0),
                "expired_keys_24h": stats.get("expired_keys", 0)
            },
            "key_distribution": stats.get("key_distribution", {}),
            "performance": {
                "avg_get_time_ms": stats.get("avg_get_time", 0),
                "avg_set_time_ms": stats.get("avg_set_time", 0)
            }
        }
        
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        raise HTTPException(status_code=500, detail="Cache stats unavailable")

@router.post("/algorithm/{algorithm}/toggle")
async def toggle_algorithm(
    algorithm: str,
    enabled: bool,
    admin_service = Depends(get_admin_service),
    _auth = Depends(verify_admin_token)
) -> Dict[str, Any]:
    """
    Activer/désactiver un algorithme
    """
    try:
        valid_algorithms = ["nexten", "enhanced", "smart", "semantic"]
        if algorithm not in valid_algorithms:
            raise HTTPException(status_code=400, detail="Invalid algorithm name")
        
        result = await admin_service.toggle_algorithm(algorithm, enabled)
        
        logger.info(
            f"Algorithm {algorithm} {'enabled' if enabled else 'disabled'}",
            algorithm=algorithm,
            enabled=enabled,
            admin_action=True
        )
        
        return {
            "algorithm": algorithm,
            "action": "toggle",
            "enabled": enabled,
            "success": result,
            "timestamp": int(time.time()),
            "note": "Changes take effect immediately for new requests"
        }
        
    except Exception as e:
        logger.error(f"Algorithm toggle error: {e}")
        raise HTTPException(status_code=500, detail="Algorithm toggle failed")

@router.get("/logs/{level}")
async def get_logs(
    level: str = "INFO",
    limit: int = 100,
    admin_service = Depends(get_admin_service),
    _auth = Depends(verify_admin_token)
) -> Dict[str, Any]:
    """
    Récupérer les logs récents
    """
    try:
        logs = await admin_service.get_recent_logs(level.upper(), limit)
        
        return {
            "timestamp": int(time.time()),
            "log_level": level.upper(),
            "entries_returned": len(logs),
            "entries_limit": limit,
            "logs": logs
        }
        
    except Exception as e:
        logger.error(f"Logs retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Logs unavailable")