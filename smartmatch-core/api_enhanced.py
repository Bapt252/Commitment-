# -*- coding: utf-8 -*-
"""
API REST améliorée pour SmartMatch avec support complet des questionnaires
---------------------------------------------------------------------
Cette API expose les fonctionnalités de SmartMatcherEnhanced et permet
l'intégration directe des questionnaires web via des endpoints dédiés.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Body, Query, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from smartmatch_enhanced import SmartMatcherEnhanced
from questionnaire_integration import process_questionnaires

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'API
app = FastAPI(
    title="SmartMatch API Étendue",
    description="API pour le matching entre candidats et offres d'emploi avec support des questionnaires",
    version="1.1.0"
)

# Configuration CORS pour permettre les requêtes cross-origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À modifier en production pour limiter aux origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation du matcher
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
matcher = SmartMatcherEnhanced(api_key=GOOGLE_MAPS_API_KEY)

# Modèles de données
class JobSkill(BaseModel):
    name: str
    required: bool = True
    weight: float = 1.0
    level: Optional[str] = None
    
class SalaryRange(BaseModel):
    min: int = 0
    max: int = 0

class Candidate(BaseModel):
    id: str
    name: Optional[str] = None
    skills: List[str]
    location: str
    years_of_experience: int
    education_level: str
    remote_work: bool = False
    salary_expectation: int = 0
    job_type: Optional[str] = None
    industry: Optional[str] = None
    alternative_industries: Optional[List[str]] = None
    office_preference: Optional[str] = None
    motivation_priorities: Optional[List[str]] = None
    structure_preference: Optional[List[str]] = None
    transport_preferences: Optional[Dict[str, int]] = None
    currently_employed: bool = False
    availability: Optional[str] = None

class Job(BaseModel):
    id: str
    title: Optional[str] = None
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = []
    location: str
    min_years_of_experience: int
    max_years_of_experience: Optional[int] = None
    required_education: str
    offers_remote: bool = False
    salary_range: Optional[SalaryRange] = None
    job_type: Optional[str] = None
    industry: Optional[str] = None
    work_environment: Optional[str] = None
    company_size: Optional[str] = None
    sector_knowledge_required: bool = False
    can_handle_notice: bool = True
    notice_duration: Optional[str] = None
    evolution_perspectives: Optional[str] = None
    benefits_description: Optional[str] = None

class QuestionnaireRequest(BaseModel):
    candidate_data: Dict[str, Any]
    job_data: Dict[str, Any]
    client_data: Dict[str, Any]

class MatchResult(BaseModel):
    candidate_id: str
    job_id: str
    overall_score: float
    category_scores: Dict[str, float]
    additional_scores: Optional[Dict[str, float]] = None
    insights: List[Dict[str, Any]]

# Routes API
@app.get("/")
async def root():
    return {"message": "Bienvenue dans l'API SmartMatch Étendue"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "enhanced": True, "semantic_enabled": True}

@app.post("/api/match", response_model=MatchResult)
async def calculate_match(candidate: Candidate, job: Job):
    """
    Calcule le score de matching entre un candidat et une offre d'emploi
    """
    try:
        result = matcher.calculate_match(candidate.dict(), job.dict())
        return result
    except Exception as e:
        logger.error(f"Erreur lors du calcul du matching: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul du matching: {str(e)}")

@app.post("/api/batch-match", response_model=List[MatchResult])
async def batch_match(candidates: List[Candidate], jobs: List[Job]):
    """
    Calcule les scores de matching pour plusieurs candidats et offres d'emploi
    """
    try:
        candidates_dict = [c.dict() for c in candidates]
        jobs_dict = [j.dict() for j in jobs]
        
        results = matcher.batch_match(candidates_dict, jobs_dict)
        return results
    except Exception as e:
        logger.error(f"Erreur lors du calcul du batch matching: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul du batch matching: {str(e)}")

@app.post("/api/questionnaire-match", response_model=MatchResult)
async def questionnaire_match(request: QuestionnaireRequest):
    """
    Calcule le score de matching à partir des données des questionnaires web
    
    Args:
        request: Les données des questionnaires candidat et client
    """
    try:
        # Traiter les données des questionnaires
        candidate, job = process_questionnaires(
            request.candidate_data,
            request.job_data,
            request.client_data
        )
        
        # Calculer le match
        result = matcher.calculate_match(candidate, job)
        return result
    except Exception as e:
        logger.error(f"Erreur lors du matching des questionnaires: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du matching des questionnaires: {str(e)}")

@app.post("/api/process-questionnaires")
async def process_questionnaire_data(request: QuestionnaireRequest):
    """
    Traite les données des questionnaires sans calculer le matching
    Utile pour valider la transformation des données
    
    Args:
        request: Les données des questionnaires candidat et client
    """
    try:
        # Traiter les données des questionnaires
        candidate, job = process_questionnaires(
            request.candidate_data,
            request.job_data,
            request.client_data
        )
        
        return {
            "candidate": candidate,
            "job": job
        }
    except Exception as e:
        logger.error(f"Erreur lors du traitement des questionnaires: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement des questionnaires: {str(e)}")

@app.post("/api/find-best-matches/candidate")
async def find_best_matches_for_candidate(
    candidate: Candidate,
    jobs: List[Job],
    limit: int = Query(5, ge=1, le=100, description="Nombre maximum de résultats à retourner")
):
    """
    Trouve les meilleures offres d'emploi pour un candidat
    """
    try:
        jobs_dict = [j.dict() for j in jobs]
        results = matcher.batch_match([candidate.dict()], jobs_dict)
        
        # Trier par score global décroissant
        results.sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Retourner les N meilleurs résultats
        return results[:limit]
    except Exception as e:
        logger.error(f"Erreur lors de la recherche des meilleures offres: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche des meilleures offres: {str(e)}")

@app.post("/api/find-best-matches/job")
async def find_best_matches_for_job(
    job: Job,
    candidates: List[Candidate],
    limit: int = Query(5, ge=1, le=100, description="Nombre maximum de résultats à retourner")
):
    """
    Trouve les meilleurs candidats pour une offre d'emploi
    """
    try:
        candidates_dict = [c.dict() for c in candidates]
        results = matcher.batch_match(candidates_dict, [job.dict()])
        
        # Trier par score global décroissant
        results.sort(key=lambda x: x["overall_score"], reverse=True)
        
        # Retourner les N meilleurs résultats
        return results[:limit]
    except Exception as e:
        logger.error(f"Erreur lors de la recherche des meilleurs candidats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche des meilleurs candidats: {str(e)}")

@app.get("/api/test-data")
async def get_test_data():
    """
    Récupère des données de test pour le matching
    """
    try:
        data = matcher.load_test_data()
        
        # Ajouter des données supplémentaires pour les tests
        for candidate in data["candidates"]:
            candidate["office_preference"] = "open-space"
            candidate["motivation_priorities"] = ["evolution", "remuneration", "flexibility"]
            candidate["structure_preference"] = ["startup", "pme"]
            candidate["transport_preferences"] = {"public-transport": 45, "bike": 30}
        
        for job in data["jobs"]:
            job["work_environment"] = "open-space"
            job["company_size"] = "startup"
            job["evolution_perspectives"] = "Possibilité d'évoluer vers un poste de lead developer"
        
        return data
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données de test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données de test: {str(e)}")

# Point d'entrée pour l'exécution directe
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_enhanced:app", host="0.0.0.0", port=5052, reload=True)