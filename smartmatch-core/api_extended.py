"""
API étendue pour SmartMatch avec intégration des questionnaires
---------------------------------------------------------------
Cette API REST expose les fonctionnalités complètes de SmartMatch,
y compris l'intégration des données de questionnaires.
"""

import os
import logging
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Body, Query, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from smartmatch import SmartMatcher
from smartmatch_extended import SmartMatcherExtended, create_extended_matcher
from questionnaire_integration import (
    transform_candidate_questionnaire_to_smartmatch,
    transform_client_questionnaire_to_smartmatch
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'API
app = FastAPI(
    title="SmartMatch API Étendue",
    description="API pour le matching entre candidats et offres d'emploi avec intégration des questionnaires",
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
matcher = create_extended_matcher(api_key=GOOGLE_MAPS_API_KEY)

# Modèles de données
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
    transport_preferences: Optional[Dict[str, int]] = None
    motivation_priorities: Optional[List[str]] = None

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
    salary_range: Optional[Dict[str, int]] = None
    job_type: Optional[str] = None
    industry: Optional[str] = None
    work_environment: Optional[str] = None

class MatchResult(BaseModel):
    candidate_id: str
    job_id: str
    overall_score: float
    category_scores: Dict[str, float]
    insights: List[Dict[str, Any]]

class QuestionnaireData(BaseModel):
    data: Dict[str, Any] = Field(..., description="Données du questionnaire au format JSON")

# Routes API
@app.get("/")
async def root():
    return {"message": "Bienvenue dans l'API SmartMatch Étendue"}

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

# Nouvelles routes pour l'intégration des questionnaires
@app.post("/api/questionnaire/candidate/transform")
async def transform_candidate_questionnaire(questionnaire: QuestionnaireData):
    """
    Transforme les données du questionnaire candidat au format SmartMatch
    """
    try:
        candidate = transform_candidate_questionnaire_to_smartmatch(questionnaire.data)
        return candidate
    except Exception as e:
        logger.error(f"Erreur lors de la transformation du questionnaire candidat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la transformation: {str(e)}")

@app.post("/api/questionnaire/client/transform")
async def transform_client_questionnaire(
    questionnaire: QuestionnaireData,
    job_data: Dict[str, Any] = Body(..., description="Données extraites de la fiche de poste")
):
    """
    Transforme les données du questionnaire client et de la fiche de poste au format SmartMatch
    """
    try:
        job = transform_client_questionnaire_to_smartmatch(questionnaire.data, job_data)
        return job
    except Exception as e:
        logger.error(f"Erreur lors de la transformation du questionnaire client: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de la transformation: {str(e)}")

@app.post("/api/questionnaire/match")
async def match_questionnaires(
    candidate_questionnaire: Dict[str, Any] = Body(..., description="Données du questionnaire candidat"),
    client_questionnaire: Dict[str, Any] = Body(..., description="Données du questionnaire client"),
    job_data: Dict[str, Any] = Body(..., description="Données extraites de la fiche de poste"),
    cv_data: Optional[Dict[str, Any]] = Body(None, description="Données extraites du CV (optionnel)")
):
    """
    Calcule le matching entre des questionnaires candidat et client
    """
    try:
        # Transformer les données des questionnaires
        candidate = transform_candidate_questionnaire_to_smartmatch(candidate_questionnaire)
        job = transform_client_questionnaire_to_smartmatch(client_questionnaire, job_data)
        
        # Si des données de CV sont fournies, les intégrer
        if cv_data:
            if "skills" in cv_data and cv_data["skills"]:
                candidate["skills"] = cv_data["skills"]
            
            if "years_of_experience" in cv_data:
                candidate["years_of_experience"] = cv_data["years_of_experience"]
            
            if "education_level" in cv_data:
                candidate["education_level"] = cv_data["education_level"]
        
        # Vérifier que les données essentielles sont présentes
        if not candidate.get("skills"):
            candidate["skills"] = []  # Liste vide par défaut
        
        if not candidate.get("years_of_experience"):
            candidate["years_of_experience"] = 0  # Valeur par défaut
        
        if not candidate.get("education_level"):
            candidate["education_level"] = "bachelor"  # Valeur par défaut
        
        # Calculer le matching
        result = matcher.calculate_match(candidate, job)
        return result
    except Exception as e:
        logger.error(f"Erreur lors du matching des questionnaires: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du matching: {str(e)}")

# Lancement du serveur
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5052)
