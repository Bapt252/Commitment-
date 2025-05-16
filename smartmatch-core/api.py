"""
Exemple d'API REST pour exposer les fonctionnalités de SmartMatch
------------------------------------------------------------
Ce module fournit une implémentation simple d'API REST avec FastAPI
pour exposer les fonctionnalités de matching de l'algorithme SmartMatch.
"""

import os
import logging
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from smartmatch import SmartMatcher

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'API
app = FastAPI(
    title="SmartMatch API",
    description="API pour le matching entre candidats et offres d'emploi",
    version="1.0.0"
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
matcher = SmartMatcher(api_key=GOOGLE_MAPS_API_KEY)

# Modèles de données
class Skill(BaseModel):
    name: str
    level: Optional[str] = "intermediate"
    
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

class MatchResult(BaseModel):
    candidate_id: str
    job_id: str
    overall_score: float
    category_scores: Dict[str, float]
    insights: List[Dict[str, Any]]

# Routes API
@app.get("/")
async def root():
    return {"message": "Bienvenue dans l'API SmartMatch"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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
        return matcher.load_test_data()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données de test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données de test: {str(e)}")

# Lancement du serveur
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5052)
