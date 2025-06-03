"""
SuperSmartMatch V2 - Application FastAPI principale

Service unifié qui intègre intelligemment :
- Nexten Matcher (port 5052)
- SuperSmartMatch V1 (port 5062)
"""

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from typing import Dict, Any

from .config import get_config
from .routers import v1_router, v2_router, admin_router
from .middleware import (
    LoggingMiddleware,
    PerformanceMiddleware, 
    RateLimitMiddleware,
    ErrorHandlingMiddleware
)
from .dependencies import get_service_orchestrator
from .models import HealthResponse
from .logger import get_logger

# Configuration
config = get_config()
logger = get_logger(__name__)

# Application FastAPI
app = FastAPI(
    title="SuperSmartMatch V2",
    description="Service unifié intelligent de matching candidat-offre",
    version="2.0.0",
    docs_url="/docs" if config.debug else None,
    redoc_url="/redoc" if config.debug else None,
    openapi_url="/openapi.json" if config.debug else None
)

# Middleware de sécurité
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if config.debug else ["localhost", "127.0.0.1"]
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if config.debug else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware personnalisés
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(PerformanceMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)

# Routers
app.include_router(v1_router.router, prefix="/api/v1", tags=["V1 Compatible"])
app.include_router(v2_router.router, prefix="/api/v2", tags=["V2 Enhanced"])
app.include_router(admin_router.router, prefix="/admin", tags=["Administration"])

# Routes de base
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Page d'accueil - Information sur le service"""
    return {
        "service": "SuperSmartMatch V2",
        "version": "2.0.0",
        "description": "Service unifié intelligent de matching",
        "status": "operational",
        "features": {
            "nexten_integration": config.enable_nexten,
            "smart_selection": config.enable_smart_selection,
            "v1_compatibility": config.enable_v1_compatibility,
            "circuit_breaker": config.enable_circuit_breaker
        },
        "endpoints": {
            "v1_match": "/api/v1/match",
            "v2_match": "/api/v2/match", 
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs" if config.debug else None
        }
    }

@app.get("/health", response_model=HealthResponse)
async def health_check(orchestrator = Depends(get_service_orchestrator)):
    """Vérification de santé du service"""
    try:
        # Vérifier la santé des services externes
        health_status = await orchestrator.check_health()
        
        return HealthResponse(
            status="healthy",
            version="2.0.0",
            timestamp=int(time.time()),
            services=health_status,
            features={
                "nexten_enabled": config.enable_nexten,
                "smart_selection": config.enable_smart_selection,
                "v1_compatibility": config.enable_v1_compatibility
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503, 
            detail="Service temporarily unavailable"
        )

@app.get("/metrics")
async def metrics():
    """Métriques Prometheus"""
    # TODO: Implémenter les métriques Prometheus
    return {"message": "Metrics endpoint - TODO implement Prometheus"}

# Compatibilité V1 - Endpoint direct sans /api/v1
@app.post("/match")
async def match_v1_direct(request: Request, orchestrator = Depends(get_service_orchestrator)):
    """Endpoint de matching V1 compatible (route directe)"""
    from .routers.v1_router import match_v1
    return await match_v1(request, orchestrator)

# Gestion d'événements
@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    logger.info("🚀 SuperSmartMatch V2 démarrage...")
    logger.info(f"📍 Configuration: {config.environment}")
    logger.info(f"🧠 Mode intelligent: {'✅' if config.enable_smart_selection else '❌'}")
    
@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt"""
    logger.info("⏹️ SuperSmartMatch V2 arrêt en cours...")

# Gestion d'erreurs globale
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestionnaire d'erreurs HTTP"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": int(time.time())
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Gestionnaire d'erreurs général"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "timestamp": int(time.time())
        }
    )