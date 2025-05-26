"""
Point d'entrée principal du service de matching.
Configure l'application FastAPI et les middlewares.
"""
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.logging import setup_logging
from app.core.database import get_db, init_db
from app.api import routes  # Import du module routes.py directement
from app.core.config import settings

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire du cycle de vie de l'application FastAPI
    Exécute le code de démarrage et d'arrêt
    """
    # Code de démarrage
    setup_logging()
    logger.info("Démarrage du service de matching")
    init_db()
    yield
    # Code d'arrêt
    logger.info("Arrêt du service de matching")

app = FastAPI(
    title="API du Service de Matching",
    description="Service de matching entre candidats et offres d'emploi pour Nexten",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes API - utiliser le router du module routes.py
app.include_router(routes.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {"status": "healthy", "service": "matching-service"}

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "service": "Nexten Matching Service",
        "version": "1.0.0",
        "description": "Service de calcul de matching entre candidats et offres d'emploi"
    }
