import os
import sys
import tempfile
import shutil
import logging
import time
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import du middleware de métriques
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from shared.middleware.metrics import (
    PrometheusMiddleware, 
    metrics_endpoint,
    track_ml_inference,
    track_parsing_accuracy,
    track_file_processing
)

from services.cv_parser import parse_cv, CVParserError
from app.models.cv_model import CVModel

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Commitment CV Parser API",
    description="API pour extraire automatiquement les informations des CV avec métriques avancées",
    version="1.1.0",
)

# Configuration des CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines exactes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# **AJOUT : Middleware de métriques Prometheus**
app.add_middleware(PrometheusMiddleware, service_name="cv-parser")

@app.get("/")
async def root():
    """Point d'entrée racine pour vérifier que l'API est en ligne"""
    return {"message": "Commitment CV Parser API v1.1.0 with Metrics"}

@app.get("/health")
async def health_check():
    """Endpoint de health check pour la surveillance de l'application"""
    return {"status": "ok", "service": "cv-parser", "timestamp": time.time()}

# **AJOUT : Endpoint pour les métriques Prometheus**
@app.get("/metrics")
async def get_metrics():
    """Endpoint pour exposer les métriques Prometheus"""
    return await metrics_endpoint()

@app.post("/api/parse-cv/", response_model=CVModel)
async def parse_cv_endpoint(
    file: UploadFile = File(...),
    force_refresh: bool = Form(False),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Parse un CV (PDF ou DOCX) et extrait les informations structurées.
    
    - **file**: Fichier CV (PDF ou DOCX)
    - **force_refresh**: Forcer le rafraîchissement du cache (défaut: False)
    
    Retourne un objet structuré contenant les informations du CV.
    """
    start_time = time.time()
    file_size = 0
    
    # Vérification de l'extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = ['.pdf', '.docx', '.doc']
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Format de fichier non supporté. Formats supportés: {', '.join(allowed_extensions)}"
        )
    
    # Sauvegarde temporaire du fichier
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
    try:
        # Copie du contenu et mesure de la taille
        with temp_file as buffer:
            shutil.copyfileobj(file.file, buffer)
            file_size = os.path.getsize(temp_file.name)
        
        # **MÉTRIQUES : Track file processing**
        track_file_processing(file_extension[1:], "cv-parser", file_size)
        
        # Parsing du CV avec métriques ML
        ml_start_time = time.time()
        try:
            cv_model, from_cache = parse_cv(open(temp_file.name, 'rb'), file.filename, force_refresh)
            
            # **MÉTRIQUES : Track ML inference success**
            ml_duration = time.time() - ml_start_time
            track_ml_inference("cv-parser-gpt", "cv-parser", ml_duration, success=True)
            
            # **MÉTRIQUES : Track parsing accuracy si disponible**
            if hasattr(cv_model, 'confidence_score') and cv_model.confidence_score:
                track_parsing_accuracy("cv", file_extension[1:], cv_model.confidence_score)
            elif hasattr(cv_model, 'quality_score'):
                # Alternative si le modèle utilise quality_score
                track_parsing_accuracy("cv", file_extension[1:], cv_model.quality_score)
            else:
                # Score par défaut basé sur le nombre de champs remplis
                filled_fields = 0
                total_fields = 0
                if hasattr(cv_model, 'personal_info') and cv_model.personal_info:
                    for field, value in cv_model.personal_info.__dict__.items():
                        total_fields += 1
                        if value and value != "":
                            filled_fields += 1
                
                if total_fields > 0:
                    estimated_accuracy = filled_fields / total_fields
                    track_parsing_accuracy("cv", file_extension[1:], estimated_accuracy)
            
            logger.info(f"CV parsed successfully, from cache: {from_cache}, duration: {ml_duration:.2f}s")
            
            # Nettoyage du fichier en arrière-plan
            background_tasks.add_task(os.unlink, temp_file.name)
            
            # Enrichir la réponse avec des métadonnées
            response_data = cv_model.dict() if hasattr(cv_model, 'dict') else cv_model
            if isinstance(response_data, dict):
                response_data["metadata"] = {
                    "file_size": file_size,
                    "file_type": file_extension[1:],
                    "processing_time": time.time() - start_time,
                    "from_cache": from_cache,
                    "timestamp": time.time()
                }
            
            return cv_model
            
        except CVParserError as e:
            # **MÉTRIQUES : Track ML inference failure**
            ml_duration = time.time() - ml_start_time
            track_ml_inference("cv-parser-gpt", "cv-parser", ml_duration, success=False)
            
            logger.error(f"Error parsing CV: {str(e)}")
            raise HTTPException(status_code=422, detail=str(e))
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # **MÉTRIQUES : Track ML inference failure pour erreurs inattendues**
        if 'ml_start_time' in locals():
            ml_duration = time.time() - ml_start_time
            track_ml_inference("cv-parser-gpt", "cv-parser", ml_duration, success=False)
        
        # Nettoyage en cas d'erreur
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Une erreur inattendue s'est produite: {str(e)}")

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Gestionnaire global d'exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Une erreur inattendue s'est produite: {str(exc)}"}
    )

# Point d'entrée pour uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT", "production").lower() == "development"
    )
