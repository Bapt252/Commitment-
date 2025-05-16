#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API REST pour SmartMatch
------------------------
Expose les fonctionnalités du système SmartMatch via une API REST.

Auteur: Claude
Date: 16/05/2025
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import json
import time
import logging
import os
from typing import Dict, List, Any, Optional

from app.smartmatch import SmartMatcher
from app.smartmatch_transport import enhance_smartmatch_with_transport
from app.api_keys import get_maps_api_key

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer l'application FastAPI
app = FastAPI(
    title="SmartMatch API",
    description="API pour le système de matching avancé SmartMatch",
    version="1.0.0"
)

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser le SmartMatcher
api_key = get_maps_api_key()
matcher = SmartMatcher(api_key=api_key)
matcher = enhance_smartmatch_with_transport(matcher, api_key=api_key)

@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {"message": "Bienvenue sur l'API SmartMatch"}

@app.get("/health")
async def health():
    """Endpoint de vérification de l'état"""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/api/match/single")
async def match_single(candidate: Dict[str, Any], job: Dict[str, Any]):
    """
    Effectue un matching entre un candidat et une offre d'emploi
    
    Args:
        candidate: Profil du candidat
        job: Offre d'emploi
        
    Returns:
        Résultat du matching
    """
    try:
        result = matcher.calculate_match(candidate, job)
        return result
    except Exception as e:
        logger.error(f"Erreur lors du matching: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du matching: {str(e)}")

@app.post("/api/match/batch")
async def match_batch(candidates: List[Dict[str, Any]], jobs: List[Dict[str, Any]]):
    """
    Effectue un matching par lots entre plusieurs candidats et offres d'emploi
    
    Args:
        candidates: Liste des profils candidats
        jobs: Liste des offres d'emploi
        
    Returns:
        Résultats du matching pour toutes les paires
    """
    try:
        results = matcher.batch_match(candidates, jobs)
        return results
    except Exception as e:
        logger.error(f"Erreur lors du matching par lots: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du matching par lots: {str(e)}")

@app.post("/api/match/company")
async def match_with_company(candidates: List[Dict[str, Any]], companies: List[Dict[str, Any]]):
    """
    Effectue un matching entre des candidats et des entreprises
    
    Args:
        candidates: Liste des profils candidats
        companies: Liste des entreprises
        
    Returns:
        Résultats du matching
    """
    try:
        results = matcher.match(candidates, companies)
        return results
    except Exception as e:
        logger.error(f"Erreur lors du matching avec entreprises: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du matching avec entreprises: {str(e)}")

@app.get("/api/skills/expand")
async def expand_skills(skills: str):
    """
    Étend une liste de compétences avec des synonymes
    
    Args:
        skills: Liste de compétences séparées par des virgules
        
    Returns:
        Liste étendue avec synonymes
    """
    try:
        skills_list = [s.strip() for s in skills.split(",")]
        expanded = matcher.expand_skills(skills_list)
        return {"original": skills_list, "expanded": expanded}
    except Exception as e:
        logger.error(f"Erreur lors de l'expansion des compétences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'expansion des compétences: {str(e)}")

@app.get("/api/travel/calculate")
async def calculate_travel(origin: str, destination: str, mode: str = "driving"):
    """
    Calcule le temps de trajet entre deux emplacements
    
    Args:
        origin: Emplacement d'origine (adresse ou coordonnées)
        destination: Emplacement de destination (adresse ou coordonnées)
        mode: Mode de transport (driving, transit, walking, bicycling)
        
    Returns:
        Temps de trajet en minutes
    """
    try:
        travel_time = matcher.commute_extension.maps_client.get_travel_time(
            origin, destination, mode=mode
        )
        return {"origin": origin, "destination": destination, "mode": mode, "time_minutes": travel_time}
    except Exception as e:
        logger.error(f"Erreur lors du calcul du temps de trajet: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul du temps de trajet: {str(e)}")
