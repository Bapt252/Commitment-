"""
SuperSmartMatch V2 - Application FastAPI principale

Service intelligent unifiant Nexten Matcher (5052) et SuperSmartMatch V1 (5062)
avec sélection automatique d'algorithme et circuit breakers.
"""

import asyncio
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional

from .config import get_settings
from .services.algorithm_selector import AlgorithmSelector
from .services.matching_orchestrator import MatchingOrchestrator
from .models.matching_models import (
    MatchingRequestV2,
    MatchingRequestV1,
    MatchingResponse,
    HealthResponse,
    MetricsResponse
)
from .monitoring.metrics_collector import MetricsCollector
from .utils.logging_config import setup_logging

# Configuration globale
settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)

# Services globaux
metrics_collector = MetricsCollector()
algorithm_selector = AlgorithmSelector()
matching_orchestrator = MatchingOrchestrator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    # Startup
    logger.info("🚀 Démarrage SuperSmartMatch V2")
    
    try:
        # Initialisation des services
        await matching_orchestrator.initialize()
        await metrics_collector.initialize()
        
        # Validation des services externes
        await matching_orchestrator.validate_external_services()
        
        logger.info("✅ SuperSmartMatch V2 initialisé avec succès")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        raise
    finally:
        # Shutdown
        logger.info("🛑 Arrêt SuperSmartMatch V2")
        await matching_orchestrator.cleanup()
        await metrics_collector.cleanup()


# Application FastAPI
app = FastAPI(
    title="SuperSmartMatch V2",
    description="Service de matching intelligent unifié",
    version="2.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire global d'exceptions"""
    logger.error(f"Erreur non gérée: {exc}", exc_info=True)
    
    await metrics_collector.record_error(
        error_type=type(exc).__name__,
        endpoint=str(request.url.path)
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "type": "internal_server_error",
            "request_id": getattr(request.state, 'request_id', None)
        }
    )


# === ENDPOINTS PRINCIPAUX ===

@app.post("/api/v2/match", response_model=MatchingResponse)
async def match_v2(
    request: MatchingRequestV2,
    background_tasks: BackgroundTasks
) -> MatchingResponse:
    """
    Endpoint principal SuperSmartMatch V2
    
    Sélection automatique d'algorithme optimal selon les règles métier :
    - Nexten Matcher : Si questionnaires complets
    - Smart-Match : Pour géolocalisation
    - Enhanced : Pour profils seniors
    - Semantic : Pour NLP complexe
    - Basic : Fallback
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        logger.info(f"🎯 Nouvelle requête de matching V2: {len(request.jobs)} jobs")
        
        # Sélection automatique d'algorithme
        selected_algorithm = algorithm_selector.select_algorithm(
            cv_data=request.cv_data,
            jobs=request.jobs,
            force_algorithm=request.options.force_algorithm if request.options else None
        )
        
        logger.info(f"🧠 Algorithme sélectionné: {selected_algorithm}")
        
        # Exécution du matching
        result = await matching_orchestrator.execute_matching(
            algorithm=selected_algorithm,
            cv_data=request.cv_data,
            jobs=request.jobs,
            options=request.options
        )
        
        # Collecte des métriques en arrière-plan
        background_tasks.add_task(
            metrics_collector.record_matching_request,
            algorithm=selected_algorithm,
            duration=asyncio.get_event_loop().time() - start_time,
            success=True,
            num_jobs=len(request.jobs),
            num_results=len(result.matches)
        )
        
        logger.info(f"✅ Matching terminé: {len(result.matches)} résultats")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du matching: {e}", exc_info=True)
        
        # Métriques d'erreur
        background_tasks.add_task(
            metrics_collector.record_matching_request,
            algorithm=getattr(locals().get('selected_algorithm'), 'value', 'unknown'),
            duration=asyncio.get_event_loop().time() - start_time,
            success=False,
            num_jobs=len(request.jobs),
            num_results=0
        )
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Erreur lors du matching",
                "type": "matching_error",
                "message": str(e)
            }
        )


@app.post("/api/v1/match", response_model=MatchingResponse)
async def match_v1_compatibility(
    request: MatchingRequestV1,
    background_tasks: BackgroundTasks
) -> MatchingResponse:
    """
    Endpoint de compatibilité avec SuperSmartMatch V1
    
    Maintient 100% de compatibilité backward avec l'API V1
    tout en bénéficiant des améliorations V2.
    """
    logger.info("🔄 Requête de compatibilité V1 reçue")
    
    # Conversion vers format V2
    v2_request = MatchingRequestV2(
        cv_data=request.cv_data,
        jobs=request.job_data,  # V1 utilise 'job_data' au lieu de 'jobs'
        options=None
    )
    
    # Si algorithme spécifié, forcer la sélection
    if hasattr(request, 'algorithm') and request.algorithm:
        from .models.matching_models import MatchingOptions
        v2_request.options = MatchingOptions(
            force_algorithm=request.algorithm
        )
    
    # Délégation vers l'endpoint V2
    return await match_v2(v2_request, background_tasks)


# === ENDPOINTS DE MONITORING ===

@app.get("/api/v2/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Vérification de santé du service et des dépendances externes
    """
    logger.debug("🏥 Vérification de santé demandée")
    
    try:
        # Vérification des services externes
        external_services = await matching_orchestrator.check_external_services_health()
        
        return HealthResponse(
            status="healthy",
            version="2.0.0",
            timestamp=asyncio.get_event_loop().time(),
            external_services=external_services
        )
        
    except Exception as e:
        logger.error(f"❌ Problème de santé détecté: {e}")
        
        return HealthResponse(
            status="unhealthy",
            version="2.0.0",
            timestamp=asyncio.get_event_loop().time(),
            external_services={},
            error=str(e)
        )


@app.get("/api/v2/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """
    Métriques de performance et d'utilisation
    """
    logger.debug("📊 Métriques demandées")
    
    try:
        metrics = await metrics_collector.get_current_metrics()
        return MetricsResponse(**metrics)
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la collecte des métriques: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la collecte des métriques"
        )


@app.get("/api/v2/algorithms/status")
async def get_algorithms_status():
    """
    Status des algorithmes et circuit breakers
    """
    logger.debug("🔧 Status des algorithmes demandé")
    
    try:
        status = await matching_orchestrator.get_algorithms_status()
        return status
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la récupération du status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération du status des algorithmes"
        )


# === ENDPOINTS UTILITAIRES ===

@app.get("/")
async def root():
    """Page d'accueil avec informations sur le service"""
    return {
        "service": "SuperSmartMatch V2",
        "version": "2.0.0",
        "description": "Service de matching intelligent unifié",
        "status": "running",
        "endpoints": {
            "matching_v2": "/api/v2/match",
            "matching_v1_compat": "/api/v1/match",
            "health": "/api/v2/health",
            "metrics": "/api/v2/metrics",
            "algorithms_status": "/api/v2/algorithms/status"
        },
        "unified_services": {
            "nexten_matcher": "port 5052",
            "supersmartmatch_v1": "port 5062"
        },
        "features": [
            "Sélection automatique d'algorithme",
            "Circuit breakers et fallback",
            "Monitoring temps réel",
            "Compatibilité backward V1",
            "Performance +13%"
        ]
    }


@app.get("/dashboard")
async def dashboard():
    """Dashboard de monitoring (redirection ou page simple)"""
    return {
        "message": "Dashboard SuperSmartMatch V2",
        "metrics_endpoint": "/api/v2/metrics",
        "health_endpoint": "/api/v2/health",
        "algorithms_status": "/api/v2/algorithms/status"
    }


if __name__ == "__main__":
    logger.info(f"🚀 Démarrage SuperSmartMatch V2 sur port {settings.port}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True
    )
