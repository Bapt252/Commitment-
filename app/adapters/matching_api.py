#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""API REST pour le service de matching SmartMatch."""

import os
import json
import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Union

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.adapters.matching_pipeline import MatchingPipeline

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

def create_app(cv_parser_url: str = "http://localhost:5051", 
               job_parser_url: str = "http://localhost:5055", 
               results_dir: str = "matching_results"):
    """
    Crée et configure l'application FastAPI.
    
    Args:
        cv_parser_url (str): URL du service de parsing de CV
        job_parser_url (str): URL du service de parsing de fiches de poste
        results_dir (str): Répertoire pour stocker les résultats
        
    Returns:
        FastAPI: Application FastAPI configurée
    """
    # Initialisation du pipeline de matching
    pipeline = MatchingPipeline(cv_parser_url, job_parser_url, results_dir)
    
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
    
    return app
