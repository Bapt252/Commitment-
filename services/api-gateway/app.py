"""
SuperSmartMatch V2 - API Gateway
Point d'entrée unifié pour orchestrer tous les microservices
Port: 5050
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from config.settings import get_settings
from routes import auth, parsers, matching, health
from middleware.auth_middleware import JWTMiddleware
from middleware.rate_limiting import RateLimitMiddleware
from middleware.logging import LoggingMiddleware

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    logger.info("🚀 SuperSmartMatch V2 API Gateway démarrage...")
    logger.info(f"🔧 Mode: {settings.ENVIRONMENT}")
    logger.info(f"🔗 CV Parser: {settings.CV_PARSER_URL}")
    logger.info(f"🔗 Job Parser: {settings.JOB_PARSER_URL}")
    logger.info(f"🔗 Matching Service: {settings.MATCHING_SERVICE_URL}")
    
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
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware personnalisés
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(JWTMiddleware)

# Routes principales
app.include_router(health.router, prefix="/api/gateway", tags=["Health"])
app.include_router(auth.router, prefix="/api/gateway", tags=["Authentication"])
app.include_router(parsers.router, prefix="/api/gateway", tags=["Parsers"])
app.include_router(matching.router, prefix="/api/gateway", tags=["Matching"])

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
        "endpoints": {
            "health": "/api/gateway/health",
            "auth": "/api/gateway/auth",
            "cv_parser": "/api/gateway/parse-cv",
            "job_parser": "/api/gateway/parse-job",
            "matching": "/api/gateway/match",
            "docs": "/api/gateway/docs"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=5050,
        reload=settings.DEBUG,
        log_level="info"
    )
