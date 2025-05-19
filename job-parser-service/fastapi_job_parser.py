#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Job Parser Service API avec métriques Prometheus
Service FastAPI pour l'analyse des fiches de poste avec GPT
"""

import os
import sys
import json
import logging
import tempfile
import time
import re
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import PyPDF2
import openai

# Import du middleware de métriques
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.middleware.metrics import (
    PrometheusMiddleware, 
    metrics_endpoint,
    track_ml_inference,
    track_parsing_accuracy,
    track_file_processing
)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("job-parser-api")

# Configuration de l'application FastAPI
app = FastAPI(
    title="Job Parser Service API",
    description="API pour l'analyse automatique des fiches de poste avec GPT et métriques",
    version="1.1.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# **AJOUT : Middleware de métriques Prometheus**
app.add_middleware(PrometheusMiddleware, service_name="job-parser")

# Taille maximale des fichiers (5 Mo)
MAX_FILE_SIZE = 5 * 1024 * 1024

# Types de fichiers autorisés
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}

# Configuration OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY", "")

# Modèles Pydantic
class JobAnalysisRequest(BaseModel):
    text: str

class JobInfo(BaseModel):
    title: str = ""
    company: str = ""
    location: str = ""
    contract_type: str = ""
    skills: list = []
    experience: str = ""
    education: str = ""
    salary: str = ""
    responsibilities: list = []
    benefits: list = []

class JobAnalysisResponse(BaseModel):
    status: str
    job_info: JobInfo
    metadata: Dict[str, Any]

def allowed_file(filename: str) -> bool:
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path: str) -> str:
    """Extrait le texte d'un fichier PDF."""
    logger.info(f"Extraction du texte du fichier PDF: {file_path}")
    
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() + "\n"
        
        logger.info(f"Texte extrait: {len(text)} caractères")
        return text
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte: {str(e)}")
        raise

def extract_text_from_file(file_path: str) -> str:
    """Extrait le texte d'un fichier en fonction de son extension."""
    if file_path.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.txt'):
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    else:
        raise ValueError(f"Type de fichier non pris en charge: {file_path}")

def analyze_with_gpt(text: str) -> Dict[str, Any]:
    """Analyse le texte avec l'API OpenAI."""
    logger.info("Envoi du texte à l'API OpenAI (GPT)...")
    
    if not openai.api_key:
        logger.error("Clé API OpenAI non définie.")
        raise ValueError("Clé API OpenAI non définie.")
    
    # Si le texte est trop long, le tronquer
    max_tokens = 15000
    if len(text) > max_tokens:
        logger.warning(f"Texte trop long ({len(text)} caractères), troncature à {max_tokens} caractères")
        text = text[:max_tokens] + "...[texte tronqué]"
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse de fiches de poste."},
                {"role": "user", "content": f"""
Analyse cette fiche de poste et extrait les informations importantes.
Réponds UNIQUEMENT au format JSON.

FICHE DE POSTE:
{text}

EXTRAIRE LES INFORMATIONS SUIVANTES (JSON UNIQUEMENT):
{{
  "title": "",
  "company": "",
  "location": "",
  "contract_type": "",
  "skills": [],
  "experience": "",
  "education": "",
  "salary": "",
  "responsibilities": [],
  "benefits": []
}}
"""}
            ],
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        
        # Tentative d'extraction d'un JSON de la réponse
        try:
            json_pattern = r'(\{[\s\S]*\})'
            match = re.search(json_pattern, content)
            if match:
                json_str = match.group(1)
                parsed_result = json.loads(json_str)
                logger.info("Parsing JSON réussi")
                return parsed_result
            else:
                parsed_result = json.loads(content)
                return parsed_result
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {str(e)}")
            logger.error(f"Réponse: {content}")
            raise ValueError("Impossible de parser la réponse JSON de GPT")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à l'API OpenAI: {str(e)}")
        raise

@app.get("/")
async def root():
    """Point d'entrée racine"""
    return {"message": "Job Parser Service API v1.1.0 with Metrics"}

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "ok", 
        "service": "job-parser", 
        "timestamp": time.time(),
        "version": "1.1.0"
    }

# **AJOUT : Endpoint pour les métriques Prometheus**
@app.get("/metrics")
async def get_metrics():
    """Endpoint pour exposer les métriques Prometheus"""
    return await metrics_endpoint()

@app.post("/analyze", response_model=JobAnalysisResponse)
async def analyze_job_posting(request: JobAnalysisRequest):
    """Endpoint pour l'analyse d'une fiche de poste par texte."""
    start_time = time.time()
    
    try:
        # Vérifier que le texte n'est pas vide
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Le texte de la fiche de poste est vide")
        
        # **MÉTRIQUES : Track file processing (text)**
        track_file_processing("text", "job-parser", len(request.text.encode('utf-8')))
        
        # Analyser le texte avec GPT
        ml_start_time = time.time()
        try:
            result = analyze_with_gpt(request.text)
            
            # **MÉTRIQUES : Track ML inference success**
            ml_duration = time.time() - ml_start_time
            track_ml_inference("gpt-4o-mini", "job-parser", ml_duration, success=True)
            
            # **MÉTRIQUES : Track parsing accuracy (basé sur le nombre de champs remplis)**
            filled_fields = sum(1 for key, value in result.items() if value)
            total_fields = len(result)
            accuracy = filled_fields / total_fields if total_fields > 0 else 0.0
            track_parsing_accuracy("job", "text", accuracy)
            
            job_info = JobInfo(**result)
            
            return JobAnalysisResponse(
                status="success",
                job_info=job_info,
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "parser_version": "1.1.0-gpt",
                    "processing_time": time.time() - start_time,
                    "accuracy_score": accuracy
                }
            )
            
        except Exception as e:
            # **MÉTRIQUES : Track ML inference failure**
            ml_duration = time.time() - ml_start_time
            track_ml_inference("gpt-4o-mini", "job-parser", ml_duration, success=False)
            raise HTTPException(status_code=500, detail=f"Erreur d'analyse GPT: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-file", response_model=JobAnalysisResponse)
async def analyze_job_posting_file(file: UploadFile = File(...)):
    """Endpoint pour l'analyse d'une fiche de poste à partir d'un fichier."""
    start_time = time.time()
    file_size = 0
    
    try:
        # Vérifications du fichier
        if not file.filename:
            raise HTTPException(status_code=400, detail="Nom de fichier invalide")
        
        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"Type de fichier non autorisé. Autorisés: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Lire le contenu du fichier
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="Fichier trop volumineux")
        
        # **MÉTRIQUES : Track file processing**
        file_extension = file.filename.split('.')[-1].lower()
        track_file_processing(file_extension, "job-parser", file_size)
        
        # Sauvegarder temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as temp:
            temp.write(content)
            file_path = temp.name
        
        try:
            # Extraire le texte
            text = extract_text_from_file(file_path)
            
            # Analyser avec GPT
            ml_start_time = time.time()
            try:
                result = analyze_with_gpt(text)
                
                # **MÉTRIQUES : Track ML inference success**
                ml_duration = time.time() - ml_start_time
                track_ml_inference("gpt-4o-mini", "job-parser", ml_duration, success=True)
                
                # **MÉTRIQUES : Track parsing accuracy**
                filled_fields = sum(1 for key, value in result.items() if value)
                total_fields = len(result)
                accuracy = filled_fields / total_fields if total_fields > 0 else 0.0
                track_parsing_accuracy("job", file_extension, accuracy)
                
                job_info = JobInfo(**result)
                
                return JobAnalysisResponse(
                    status="success",
                    job_info=job_info,
                    metadata={
                        "filename": file.filename,
                        "file_size": file_size,
                        "file_type": file_extension,
                        "analyzed_at": datetime.now().isoformat(),
                        "parser_version": "1.1.0-gpt",
                        "processing_time": time.time() - start_time,
                        "accuracy_score": accuracy
                    }
                )
                
            except Exception as e:
                # **MÉTRIQUES : Track ML inference failure**
                ml_duration = time.time() - ml_start_time
                track_ml_inference("gpt-4o-mini", "job-parser", ml_duration, success=False)
                raise HTTPException(status_code=500, detail=f"Erreur d'analyse GPT: {str(e)}")
            
        finally:
            # Cleanup
            if os.path.exists(file_path):
                os.unlink(file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du fichier: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Gestionnaire global d'exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Une erreur inattendue s'est produite: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "fastapi_job_parser:app",
        host="0.0.0.0",
        port=5055,
        reload=True,
        log_level="info"
    )
