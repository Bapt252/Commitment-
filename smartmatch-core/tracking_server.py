import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import json
from datetime import datetime, timedelta
import os

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importer les dépendances
from api.tracking_api import router as tracking_router
from analysis.metrics_calculator import MatchingMetricsCalculator
from analysis.ml_feedback_loop import MLFeedbackLoop
from tracking.privacy import PrivacyManager

# Créer l'application FastAPI
app = FastAPI(title="SmartMatch Tracking API", version="1.0.0")

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser les composants
metrics_calculator = MatchingMetricsCalculator()
ml_feedback_loop = MLFeedbackLoop()
privacy_manager = PrivacyManager()

# Intégrer les routes API
app.include_router(tracking_router)

@app.get("/")
async def root():
    return {
        "name": "SmartMatch Tracking API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/metrics/acceptance")
async def get_acceptance_metrics(days: int = 30):
    return metrics_calculator.calculate_acceptance_rate(days)

@app.get("/api/metrics/satisfaction")
async def get_satisfaction_metrics(days: int = 30):
    return metrics_calculator.calculate_satisfaction_metrics(days)

@app.get("/api/metrics/constraints")
async def get_constraints_impact(days: int = 30):
    return metrics_calculator.calculate_constraint_impact(days)

@app.post("/api/ml/update")
async def trigger_ml_update():
    success = ml_feedback_loop.update_ml_model()
    return {"success": success}

@app.post("/api/privacy/cleanup")
async def trigger_privacy_cleanup():
    privacy_manager.clean_expired_data()
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(
        "tracking_server:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8001")),
        reload=True
    )