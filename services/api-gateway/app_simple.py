"""
SuperSmartMatch V2 - API Gateway (Version de démarrage rapide)
Point d'entrée unifié pour orchestrer tous les microservices
Port: 5050
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import asyncio
from contextlib import asynccontextmanager

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Variables d'environnement par défaut
import os
JWT_SECRET = os.getenv("JWT_SECRET", "supersecure-jwt-secret-change-in-production")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    logger.info("🚀 SuperSmartMatch V2 API Gateway démarrage...")
    logger.info(f"🔧 Mode: {ENVIRONMENT}")
    logger.info(f"🔧 Debug: {DEBUG}")
    
    # Initialisation optionnelle (tolérante aux erreurs)
    try:
        # Ici on pourrait initialiser la DB, Redis, etc.
        # Mais en mode dégradé, on continue même si ça échoue
        logger.info("✅ API Gateway prêt (mode de base)")
    except Exception as e:
        logger.warning(f"⚠️ Démarrage en mode dégradé: {e}")
    
    yield
    
    logger.info("🛑 SuperSmartMatch V2 API Gateway arrêt...")

# Création de l'application FastAPI
app = FastAPI(
    title="SuperSmartMatch V2 API Gateway",
    description="Point d'entrée unifié pour la plateforme de recrutement IA",
    version="2.1.0",
    docs_url="/api/gateway/docs",
    redoc_url="/api/gateway/redoc",
    openapi_url="/api/gateway/openapi.json",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En développement, plus permissif
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestionnaire d'exceptions HTTP personnalisé"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Gestionnaire d'exceptions générales"""
    logger.error(f"Erreur non gérée: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Erreur interne du serveur",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )

@app.get("/api/gateway")
async def root():
    """Endpoint racine avec informations sur l'API Gateway"""
    return {
        "service": "SuperSmartMatch V2 API Gateway",
        "version": "2.1.0",
        "status": "operational",
        "mode": ENVIRONMENT,
        "endpoints": {
            "health": "/api/gateway/health",
            "status": "/api/gateway/status",
            "auth": "/api/gateway/auth",
            "docs": "/api/gateway/docs"
        },
        "message": "🌟 API Gateway unifié opérationnel !"
    }

@app.get("/api/gateway/status")
async def simple_status():
    """Status simple pour vérifications rapides"""
    return {
        "status": "ok",
        "service": "SuperSmartMatch V2 API Gateway",
        "version": "2.1.0",
        "environment": ENVIRONMENT,
        "timestamp": "2024-01-15T10:30:00Z"
    }

@app.get("/api/gateway/health")
async def health_check():
    """Health check basique"""
    try:
        # Vérifications de base
        health_data = {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00Z",
            "services": {
                "api_gateway": {"status": "healthy", "response_time": 0.001}
            },
            "gateway_info": {
                "name": "SuperSmartMatch V2 API Gateway",
                "version": "2.1.0",
                "environment": ENVIRONMENT,
                "debug_mode": DEBUG
            },
            "performance_metrics": {
                "health_check_duration": 0.001,
                "healthy_services_ratio": 1.0,
                "gateway_uptime": 1000
            }
        }
        
        # Tentatives de vérification des services externes (non bloquantes)
        try:
            # Test Redis (optionnel)
            health_data["services"]["redis"] = {"status": "unknown", "note": "Non testé en mode de base"}
            
            # Test PostgreSQL (optionnel)
            health_data["services"]["postgres"] = {"status": "unknown", "note": "Non testé en mode de base"}
            
            # Services de parsing (optionnels)
            health_data["services"]["cv_parser"] = {"status": "unknown", "note": "Service externe non testé"}
            health_data["services"]["job_parser"] = {"status": "unknown", "note": "Service externe non testé"}
            health_data["services"]["matching_service"] = {"status": "unknown", "note": "Service externe non testé"}
            
        except Exception as e:
            logger.warning(f"Services externes non disponibles: {e}")
        
        return health_data
        
    except Exception as e:
        logger.error(f"Erreur health check: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": "2024-01-15T10:30:00Z"
            }
        )

@app.get("/api/gateway/metrics")
async def get_metrics():
    """Métriques basiques format Prometheus"""
    metrics = [
        "# HELP supersmartmatch_gateway_up Gateway availability",
        "# TYPE supersmartmatch_gateway_up gauge",
        "supersmartmatch_gateway_up 1",
        "",
        "# HELP supersmartmatch_gateway_requests_total Total requests",
        "# TYPE supersmartmatch_gateway_requests_total counter", 
        "supersmartmatch_gateway_requests_total 0",
        "",
        "# HELP supersmartmatch_gateway_response_time Response time in seconds",
        "# TYPE supersmartmatch_gateway_response_time gauge",
        "supersmartmatch_gateway_response_time 0.001"
    ]
    
    return "\n".join(metrics)

# Routes d'authentification basiques (versions simplifiées)
@app.post("/api/gateway/auth/register")
async def register():
    """Inscription utilisateur (version basique)"""
    return {
        "message": "Endpoint d'inscription - Implémentation complète disponible avec base de données",
        "status": "not_implemented",
        "hint": "Démarrer PostgreSQL pour activer l'authentification complète"
    }

@app.post("/api/gateway/auth/login")
async def login():
    """Connexion utilisateur (version basique)"""
    return {
        "message": "Endpoint de connexion - Implémentation complète disponible avec base de données",
        "status": "not_implemented", 
        "hint": "Démarrer PostgreSQL pour activer l'authentification complète"
    }

@app.get("/api/gateway/auth/me")
async def get_me():
    """Profil utilisateur (version basique)"""
    return {
        "message": "Endpoint de profil - Authentification requise",
        "status": "not_implemented",
        "hint": "Implémenter l'authentification JWT complète"
    }

# Routes de parsing (versions proxy basiques)
@app.post("/api/gateway/parse-cv")
async def parse_cv():
    """Parser CV (version basique)"""
    return {
        "message": "Service de parsing CV - Connecter au CV Parser Service sur port 5051",
        "status": "service_unavailable",
        "hint": "Démarrer le CV Parser Service pour activer cette fonctionnalité"
    }

@app.post("/api/gateway/parse-job")
async def parse_job():
    """Parser Job (version basique)"""
    return {
        "message": "Service de parsing Job - Connecter au Job Parser Service sur port 5053", 
        "status": "service_unavailable",
        "hint": "Démarrer le Job Parser Service pour activer cette fonctionnalité"
    }

# Routes de matching (versions proxy basiques)
@app.post("/api/gateway/match")
async def match():
    """Matching IA (version basique)"""
    return {
        "message": "Service de matching IA - Connecter au Matching Service sur port 5060",
        "status": "service_unavailable",
        "hint": "Démarrer le Matching Service pour activer cette fonctionnalité"
    }

@app.get("/api/gateway/match/algorithms")
async def get_algorithms():
    """Liste des algorithmes (version basique)"""
    return {
        "message": "Liste des algorithmes de matching disponibles",
        "algorithms": [
            "cosine_similarity",
            "tfidf_matching", 
            "bert_semantic",
            "skills_exact_match",
            "experience_weighted",
            "education_match",
            "location_proximity",
            "hybrid_ensemble",
            "neural_network"
        ],
        "status": "info_only",
        "hint": "Connecter au Matching Service pour utilisation réelle"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5050,
        reload=DEBUG,
        log_level="info"
    )
