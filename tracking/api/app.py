"""
Application FastAPI pour l'API de tracking et la gestion des événements.
"""

import logging
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncpg
import time
from prometheus_client import Counter, Histogram, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST

# Configuration des logs
logging.basicConfig(
    level=logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="Commitment Tracking API",
    description="API pour la collecte et l'analyse des données de tracking",
    version="1.0.0",
)

# Métriques Prometheus
REQUEST_COUNT = Counter(
    "tracking_api_requests_total", "Total count of requests by method and path", ["method", "path"]
)
REQUEST_LATENCY = Histogram(
    "tracking_api_request_latency_seconds", "Request latency in seconds", ["method", "path"]
)

# Middleware pour les métriques
@app.middleware("http")
async def track_requests(request: Request, call_next):
    request_path = request.url.path
    request_method = request.method
    
    # Ne pas tracker les requêtes de monitoring
    if request_path == "/metrics" or request_path == "/health":
        return await call_next(request)
    
    REQUEST_COUNT.labels(method=request_method, path=request_path).inc()
    start_time = time.time()
    
    response = await call_next(request)
    
    REQUEST_LATENCY.labels(method=request_method, path=request_path).observe(
        time.time() - start_time
    )
    
    return response

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, limiter aux origines spécifiques
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales pour les connexions
db_pool = None
redis = None

@app.on_event("startup")
async def startup_db_client():
    global db_pool
    
    # Connexion à PostgreSQL
    try:
        db_pool = await asyncpg.create_pool(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", "5432")),
            user=os.environ.get("POSTGRES_USER", "postgres"),
            password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
            database=os.environ.get("POSTGRES_DB", "commitment"),
        )
        logger.info("Connected to PostgreSQL")
    except Exception as e:
        logger.error(f"Error connecting to PostgreSQL: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    global db_pool
    
    if db_pool:
        await db_pool.close()
        logger.info("Closed PostgreSQL connection")

# Endpoint de santé
@app.get("/health")
async def health():
    return {"status": "ok"}

# Endpoint pour les métriques Prometheus
@app.get("/metrics")
async def metrics():
    return JSONResponse(
        content=generate_latest().decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST,
    )

# Import des routers API
from api.events_api import router as events_router
from api.consent_api import router as consent_router
from api.feedback_api import router as feedback_router

# Enregistrement des routers
app.include_router(events_router)
app.include_router(consent_router)
app.include_router(feedback_router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
