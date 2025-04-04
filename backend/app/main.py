from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api.api import api_router
from app.nlp.init_matching import init_matching_engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configuration CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "https://bapt252.github.io"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API Commitment"}

@app.on_event("startup")
async def startup_event():
    """
    Initialise les ressources nécessaires au démarrage de l'application
    """
    logger.info("Démarrage de l'application...")
    
    # Initialiser le moteur de matching
    try:
        logger.info("Initialisation du système de matching...")
        init_matching_engine()
        logger.info("Système de matching initialisé avec succès.")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation du système de matching: {str(e)}")
        logger.warning("L'application continue à démarrer mais certaines fonctionnalités de matching pourraient ne pas être disponibles.")
    
    logger.info("Application démarrée et prête à recevoir des requêtes.")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Libère les ressources à l'arrêt de l'application
    """
    logger.info("Arrêt de l'application...")
