# CV Parser Service - Application FastAPI

# Import des librairies
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import des modules internes
from app.core.config import settings
from app.core.logging import setup_logging

# Setup logging
logger = setup_logging()

# Création de l'application FastAPI
app = FastAPI(
    title="CV Parser Service",
    description="Service de parsing de CV asynchrone utilisant GPT-4o-mini",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import des routes (doit être après la création de l'app)
from app.api.routes import router as api_router
from app.api.direct_routes import direct_router

# Inclusion des routes
app.include_router(api_router, prefix="/api")
app.include_router(direct_router, prefix="/api")

# Route de santé
@app.get("/health")
async def health_check():
    """Endpoint de vérification de la santé du service"""
    return {"status": "healthy", "service": "cv-parser"}

# Endpoint pour les métriques Prometheus
@app.get("/metrics")
async def metrics():
    """Expose les métriques Prometheus"""
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except ImportError:
        # Si prometheus_client n'est pas installé, retourner un placeholder
        return Response("# Prometheus metrics not available\n", media_type="text/plain")

# Initialisation de l'application
@app.on_event("startup")
async def startup_event():
    logger.info("CV Parser Service démarré")

# Nettoyage à l'arrêt
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("CV Parser Service arrêté")
