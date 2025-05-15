#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""API REST pour le service de matching SmartMatch."""

import os
import json
import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Union

from fastapi import FastAPI, HTTPException, Body, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.adapters.matching_pipeline import MatchingPipeline
from app.adapters.parsing_adapter import ParsingAdapter

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MatchingAPI")

# Définition des modèles Pydantic pour la validation des données
class HealthResponse(BaseModel):
    status: str
    timestamp: float

class DirectMatchRequest(BaseModel):
    cv_data: Dict[str, Any] = Field(..., description="Données du CV à parser")
    job_data: Dict[str, Any] = Field(..., description="Données de la fiche de poste à parser")

class MatchResponse(BaseModel):
    status: str
    candidate: Dict[str, Any]
    job: Dict[str, Any]
    score: float
    details: Dict[str, Any]

def create_app(parsing_adapter: Optional[ParsingAdapter] = None, 
               results_dir: str = "matching_results"):
    """
    Crée et configure l'application FastAPI.
    
    Args:
        parsing_adapter (ParsingAdapter, optional): Adaptateur de parsing
        results_dir (str): Répertoire pour stocker les résultats
        
    Returns:
        FastAPI: Application FastAPI configurée
    """
    # Initialisation du pipeline de matching avec l'adaptateur de parsing
    pipeline = MatchingPipeline(parsing_adapter, results_dir)
    
    # Création de l'application FastAPI
    app = FastAPI(
        title="SmartMatch API",
        description="API pour le service de matching SmartMatch",
        version="1.0.0"
    )
    
    # Configuration CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    @app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
    async def health_check():
        """
        Vérifie l'état de santé du service.
        """
        return {"status": "healthy", "timestamp": time.time()}
    
    @app.post("/match/direct", response_model=MatchResponse, tags=["Matching"])
    async def match_direct(request: DirectMatchRequest):
        """
        Parse et match directement un CV et une fiche de poste à partir de leurs données brutes.
        """
        try:
            result = await pipeline.parse_and_match_cv_job(request.cv_data, request.job_data)
            
            if result.get("status") == "success":
                return result
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=result.get("message", "Erreur lors du matching direct")
                )
        except Exception as e:
            logger.error(f"Erreur lors du matching direct: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/match/cv-to-job", response_model=MatchResponse, tags=["Matching"])
    async def match_cv_to_job(
        cv_file: UploadFile = File(...),
        job_description: str = Form(...)
    ):
        """
        Match un CV (fichier) avec une description de poste (texte).
        """
        try:
            cv_content = await cv_file.read()
            
            result = await pipeline.match_cv_to_job(cv_content, cv_file.filename, job_description)
            
            if result.get("status") == "success":
                return result
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=result.get("message", "Erreur lors du matching CV vers Job")
                )
        except Exception as e:
            logger.error(f"Erreur lors du matching CV vers Job: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/match/job-to-cv", response_model=MatchResponse, tags=["Matching"])
    async def match_job_to_cv(
        job_description: str = Form(...),
        cv_file: UploadFile = File(...)
    ):
        """
        Match une description de poste (texte) avec un CV (fichier).
        """
        try:
            cv_content = await cv_file.read()
            
            result = await pipeline.match_job_to_cv(job_description, cv_content, cv_file.filename)
            
            if result.get("status") == "success":
                return result
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=result.get("message", "Erreur lors du matching Job vers CV")
                )
        except Exception as e:
            logger.error(f"Erreur lors du matching Job vers CV: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/match/job-file-to-cv", response_model=MatchResponse, tags=["Matching"])
    async def match_job_file_to_cv(
        job_file: UploadFile = File(...),
        cv_file: UploadFile = File(...)
    ):
        """
        Match une fiche de poste (fichier) avec un CV (fichier).
        """
        try:
            job_content = await job_file.read()
            cv_content = await cv_file.read()
            
            result = await pipeline.match_job_file_to_cv(job_content, job_file.filename, cv_content, cv_file.filename)
            
            if result.get("status") == "success":
                return result
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=result.get("message", "Erreur lors du matching Job file vers CV")
                )
        except Exception as e:
            logger.error(f"Erreur lors du matching Job file vers CV: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app
