"""
Exemple d'intégration du middleware de métriques dans un service FastAPI
Adaptez ce code à vos services existants
"""
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
import os
from typing import Optional

# Import du middleware de métriques
from shared.middleware.metrics import (
    PrometheusMiddleware, 
    metrics_endpoint,
    track_ml_inference,
    track_parsing_accuracy,
    track_file_processing
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'app FastAPI
app = FastAPI(
    title="CV Parser Service",
    description="Service de parsing de CV avec métriques avancées",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# **IMPORTANT: Ajout du middleware de métriques**
app.add_middleware(PrometheusMiddleware, service_name="cv-parser")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cv-parser", "timestamp": time.time()}

# **IMPORTANT: Endpoint métriques pour Prometheus**
@app.get("/metrics")
async def get_metrics():
    return await metrics_endpoint()

# Exemple d'intégration dans un endpoint de parsing
@app.post("/api/parse-cv/")
async def parse_cv_endpoint(
    file: UploadFile = File(...),
    force_refresh: bool = Form(False),
    extract_skills: bool = Form(True)
):
    start_time = time.time()
    file_size = 0
    
    try:
        # Lecture du fichier
        file_content = await file.read()
        file_size = len(file_content)
        file_type = file.filename.split('.')[-1].lower()
        
        # **Track file processing metrics**
        track_file_processing(file_type, "cv-parser", file_size)
        
        # Parsing ML
        ml_start_time = time.time()
        try:
            # Votre logique de parsing existante ici
            # parsed_data = await parse_cv_with_ml(file_content, file_type)
            
            # Simulation pour l'exemple
            parsed_data = {
                "name": "John Doe",
                "skills": ["Python", "Machine Learning"],
                "experience": "5 years",
                "confidence_score": 0.95
            }
            
            # **Track ML inference success**
            ml_duration = time.time() - ml_start_time
            track_ml_inference("gpt-4o-mini", "cv-parser", ml_duration, success=True)
            
            # **Track parsing accuracy si disponible**
            if "confidence_score" in parsed_data:
                track_parsing_accuracy("cv", file_type, parsed_data["confidence_score"])
            
        except Exception as ml_error:
            # **Track ML inference failure**
            ml_duration = time.time() - ml_start_time
            track_ml_inference("gpt-4o-mini", "cv-parser", ml_duration, success=False)
            raise HTTPException(status_code=500, detail=f"ML processing failed: {str(ml_error)}")
        
        # Préparer la réponse
        response = {
            "success": True,
            "data": parsed_data,
            "metadata": {
                "file_size": file_size,
                "file_type": file_type,
                "processing_time": time.time() - start_time,
                "timestamp": time.time()
            }
        }
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in CV parsing: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

# Middleware pour logs structurés
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Information de la requête
    request_info = {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "client_ip": request.client.host if request.client else None
    }
    
    # Traitement de la requête
    response = await call_next(request)
    
    # Information de la réponse
    process_time = time.time() - start_time
    response_info = {
        "status_code": response.status_code,
        "process_time": process_time
    }
    
    # Log structuré
    logger.info(
        "Request processed",
        extra={
            **request_info,
            **response_info,
            "service": "cv-parser"
        }
    )
    
    # Ajouter le temps de traitement dans les headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Point d'entrée pour le développement
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 5051))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
