import asyncio
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

from api import events_api, consent_api, feedback_api
from tracking.privacy import PrivacyManager
from tracking.collector import EventCollector
from analysis.ml_feedback_loop import MLFeedbackLoop
from analysis.metrics_calculator import MatchingMetricsCalculator
from dashboard.data_connectors import DataConnector
from dashboard.performance_monitors import PerformanceMonitor

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialisation des composants globaux
privacy_manager = PrivacyManager()
event_collector = EventCollector(privacy_manager)

# Configuration de la connexion à la base de données
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'commitment')
}

# Création des connecteurs de données
data_connector = DataConnector(db_config)

# Initialisation des analyseurs et moniteurs
ml_feedback_loop = MLFeedbackLoop("models/ml_optimizer.pkl")
metrics_calculator = MatchingMetricsCalculator(data_connector)
performance_monitor = PerformanceMonitor(metrics_calculator)

# Gestionnaire de démarrage/arrêt de l'application
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Démarrer les tâches de fond
    collector_task = asyncio.create_task(event_collector.process_events_worker())
    ml_update_task = asyncio.create_task(ml_feedback_loop.scheduled_update_task())
    monitor_task = asyncio.create_task(performance_monitor.monitoring_worker())
    
    # Créer les alertes par défaut
    performance_monitor.create_default_alerts()
    
    logger.info("Application started, background tasks running")
    
    yield  # L'application fonctionne ici
    
    # Arrêter proprement les tâches de fond
    collector_task.cancel()
    ml_update_task.cancel()
    monitor_task.cancel()
    try:
        await collector_task
        await ml_update_task
        await monitor_task
    except asyncio.CancelledError:
        pass
    
    logger.info("Application shutting down")

# Création de l'application FastAPI
app = FastAPI(
    title="Commitment - Tracking et Analyse",
    description="Système de tracking et d'analyse des données de matching",
    version="1.0.0",
    lifespan=lifespan
)

# Ajout des routers API
app.include_router(events_api.router)
app.include_router(consent_api.router)
app.include_router(feedback_api.router)

# Route d'accueil
@app.get("/")
async def root():
    return {
        "name": "Commitment - Tracking et Analyse",
        "version": "1.0.0",
        "status": "running"
    }

# Route de diagnostic
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "services": {
            "collector": "running",
            "ml_feedback": "running",
            "monitoring": "running"
        }
    }

# Routes pour les métriques de performance
@app.get("/api/metrics/performance")
async def get_performance_metrics():
    return await metrics_calculator.calculate_matching_efficiency()

# Route pour visualiser l'impact des contraintes
@app.get("/api/metrics/constraints-impact")
async def get_constraints_impact():
    return await metrics_calculator.calculate_constraint_satisfaction_impact()

# Route pour récupérer les statistiques de satisfaction
@app.get("/api/metrics/satisfaction")
async def get_satisfaction_metrics():
    return await metrics_calculator.calculate_satisfaction_metrics()

# Route pour récupérer les statistiques d'engagement
@app.get("/api/metrics/engagement")
async def get_engagement_metrics():
    return await metrics_calculator.calculate_engagement_metrics()

# Point d'entrée principal
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=os.getenv("HOST", "0.0.0.0"), 
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )