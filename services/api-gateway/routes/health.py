"""
Routes de health check et monitoring pour l'API Gateway
Surveillance complète de tous les microservices
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time
import asyncio
import logging
from datetime import datetime

from config.settings import get_settings
from utils.proxy import proxy_manager
from routes.auth import get_current_user

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter()

# Modèles pour les health checks
class ServiceHealth(BaseModel):
    """État de santé d'un service"""
    service_name: str
    status: str  # healthy, unhealthy, degraded
    response_time: Optional[float] = None
    last_check: datetime
    error: Optional[str] = None
    version: Optional[str] = None
    uptime: Optional[float] = None

class SystemHealth(BaseModel):
    """État de santé global du système"""
    status: str  # healthy, degraded, unhealthy
    timestamp: datetime
    services: Dict[str, ServiceHealth]
    gateway_info: Dict[str, Any]
    performance_metrics: Dict[str, float]

# Cache pour les health checks (éviter de surcharger les services)
health_cache = {}
CACHE_TTL = 10  # secondes

@router.get("/health", response_model=SystemHealth)
async def health_check():
    """
    Health check global de tous les services
    Point d'entrée principal pour la surveillance
    """
    try:
        start_time = time.time()
        
        # Vérifier le cache
        now = time.time()
        if "last_check" in health_cache and (now - health_cache["last_check"]) < CACHE_TTL:
            logger.debug("Retour health check depuis cache")
            return health_cache["data"]
        
        logger.debug("Exécution nouveau health check")
        
        # Vérifier tous les services en parallèle
        services_health = await proxy_manager.health_check_all()
        
        # Analyser les résultats
        system_status = "healthy"
        healthy_services = 0
        total_services = len(services_health)
        
        service_details = {}
        
        for service_name, health_data in services_health.items():
            if isinstance(health_data, dict) and "error" not in health_data:
                # Service avec plusieurs URLs
                service_status = "healthy"
                response_times = []
                
                for url, url_health in health_data.items():
                    if url_health.get("status") != "healthy":
                        service_status = "unhealthy"
                    else:
                        response_times.append(url_health.get("response_time", 0))
                
                if service_status == "healthy":
                    healthy_services += 1
                
                avg_response_time = sum(response_times) / len(response_times) if response_times else None
                
                service_details[service_name] = ServiceHealth(
                    service_name=service_name,
                    status=service_status,
                    response_time=avg_response_time,
                    last_check=datetime.now(),
                    error=None if service_status == "healthy" else "Service unavailable"
                )
            else:
                # Service en erreur
                service_details[service_name] = ServiceHealth(
                    service_name=service_name,
                    status="unhealthy",
                    response_time=None,
                    last_check=datetime.now(),
                    error=health_data.get("error", "Unknown error")
                )
        
        # Déterminer le statut global
        if healthy_services == total_services:
            system_status = "healthy"
        elif healthy_services > 0:
            system_status = "degraded"
        else:
            system_status = "unhealthy"
        
        # Métriques de performance
        total_time = time.time() - start_time
        performance_metrics = {
            "health_check_duration": total_time,
            "healthy_services_ratio": healthy_services / total_services if total_services > 0 else 0,
            "gateway_uptime": time.time(),  # Simplified uptime
            "cache_hit_ratio": 0.95  # Exemple
        }
        
        # Informations sur le gateway
        gateway_info = {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "debug_mode": settings.DEBUG,
            "services_managed": total_services
        }
        
        # Construire la réponse
        health_response = SystemHealth(
            status=system_status,
            timestamp=datetime.now(),
            services=service_details,
            gateway_info=gateway_info,
            performance_metrics=performance_metrics
        )
        
        # Mettre en cache
        health_cache.update({
            "last_check": now,
            "data": health_response
        })
        
        logger.info(f"Health check terminé: {system_status} ({healthy_services}/{total_services} services)")
        return health_response
        
    except Exception as e:
        logger.error(f"Erreur health check global: {e}")
        return SystemHealth(
            status="unhealthy",
            timestamp=datetime.now(),
            services={},
            gateway_info={"error": str(e)},
            performance_metrics={}
        )

@router.get("/health/{service_name}")
async def health_check_service(service_name: str):
    """Health check pour un service spécifique"""
    try:
        if service_name not in ["cv_parser", "job_parser", "matching"]:
            raise HTTPException(status_code=404, detail="Service non trouvé")
        
        proxy = proxy_manager.get_proxy(service_name)
        health_data = await proxy.health_check()
        
        return {
            "service": service_name,
            "timestamp": datetime.now(),
            "health": health_data
        }
        
    except Exception as e:
        logger.error(f"Erreur health check {service_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur health check: {str(e)}")

@router.get("/health/detailed/all")
async def detailed_health_check(current_user: dict = Depends(get_current_user)):
    """
    Health check détaillé avec métriques avancées
    Réservé aux utilisateurs authentifiés
    """
    try:
        # Vérifier le rôle admin pour les détails avancés
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Accès admin requis pour les détails avancés")
        
        # Health check basique
        basic_health = await health_check()
        
        # Métriques détaillées additionnelles
        detailed_metrics = {
            "circuit_breakers": {},
            "connection_pools": {},
            "memory_usage": {},
            "request_stats": {}
        }
        
        # État des circuit breakers
        for service_name, proxy in proxy_manager.proxies.items():
            detailed_metrics["circuit_breakers"][service_name] = {}
            for url, cb in proxy.circuit_breakers.items():
                detailed_metrics["circuit_breakers"][service_name][url] = {
                    "state": cb.state.value,
                    "failure_count": cb.failure_count,
                    "success_count": cb.success_count,
                    "last_failure": cb.last_failure_time
                }
        
        return {
            "basic_health": basic_health,
            "detailed_metrics": detailed_metrics,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Erreur health check détaillé: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur health check détaillé: {str(e)}")

@router.get("/metrics")
async def get_metrics():
    """
    Métriques Prometheus pour monitoring externe
    Format compatible Prometheus
    """
    try:
        # Health check pour obtenir les métriques
        health_data = await health_check()
        
        metrics = []
        
        # Métriques de base
        metrics.append("# HELP supersmartmatch_gateway_up Gateway availability")
        metrics.append("# TYPE supersmartmatch_gateway_up gauge")
        metrics.append("supersmartmatch_gateway_up 1")
        
        # Statut des services
        metrics.append("# HELP supersmartmatch_service_up Service availability")
        metrics.append("# TYPE supersmartmatch_service_up gauge")
        
        for service_name, service_health in health_data.services.items():
            status_value = 1 if service_health.status == "healthy" else 0
            metrics.append(f'supersmartmatch_service_up{{service="{service_name}"}} {status_value}')
        
        # Temps de réponse
        metrics.append("# HELP supersmartmatch_service_response_time Service response time in seconds")
        metrics.append("# TYPE supersmartmatch_service_response_time gauge")
        
        for service_name, service_health in health_data.services.items():
            if service_health.response_time is not None:
                metrics.append(f'supersmartmatch_service_response_time{{service="{service_name}"}} {service_health.response_time}')
        
        # Métriques de performance du gateway
        metrics.append("# HELP supersmartmatch_gateway_health_check_duration Health check duration in seconds")
        metrics.append("# TYPE supersmartmatch_gateway_health_check_duration gauge")
        metrics.append(f"supersmartmatch_gateway_health_check_duration {health_data.performance_metrics.get('health_check_duration', 0)}")
        
        metrics.append("# HELP supersmartmatch_gateway_healthy_services_ratio Ratio of healthy services")
        metrics.append("# TYPE supersmartmatch_gateway_healthy_services_ratio gauge")
        metrics.append(f"supersmartmatch_gateway_healthy_services_ratio {health_data.performance_metrics.get('healthy_services_ratio', 0)}")
        
        # Circuit breaker states
        metrics.append("# HELP supersmartmatch_circuit_breaker_failures Circuit breaker failure count")
        metrics.append("# TYPE supersmartmatch_circuit_breaker_failures counter")
        
        for service_name, proxy in proxy_manager.proxies.items():
            for url, cb in proxy.circuit_breakers.items():
                metrics.append(f'supersmartmatch_circuit_breaker_failures{{service="{service_name}",url="{url}"}} {cb.failure_count}')
        
        return "\n".join(metrics)
        
    except Exception as e:
        logger.error(f"Erreur génération métriques: {e}")
        return "# Erreur génération métriques\n"

@router.get("/status")
async def simple_status():
    """
    Status simple pour load balancers
    Retourne 200 OK si le gateway fonctionne
    """
    try:
        # Check basique sans appeler les services
        return {
            "status": "ok",
            "service": settings.APP_NAME,
            "version": settings.VERSION,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erreur status simple: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")

@router.post("/health/reset-cache")
async def reset_health_cache(current_user: dict = Depends(get_current_user)):
    """Réinitialiser le cache des health checks"""
    try:
        # Vérifier le rôle admin
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Accès admin requis")
        
        global health_cache
        health_cache.clear()
        
        logger.info(f"Cache health check réinitialisé par {current_user['email']}")
        return {"message": "Cache réinitialisé avec succès"}
        
    except Exception as e:
        logger.error(f"Erreur reset cache: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du reset du cache")

@router.get("/health/history")
async def get_health_history(current_user: dict = Depends(get_current_user)):
    """
    Historique des health checks
    Utile pour analyser les tendances de disponibilité
    """
    try:
        # Vérifier le rôle admin
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Accès admin requis")
        
        # Pour l'instant, on retourne un exemple
        # En production, ceci devrait venir d'une base de données
        return {
            "message": "Fonctionnalité d'historique à implémenter",
            "suggestion": "Intégrer avec une base de données time-series comme InfluxDB"
        }
        
    except Exception as e:
        logger.error(f"Erreur historique health: {e}")
        raise HTTPException(status_code=500, detail="Erreur récupération historique")
