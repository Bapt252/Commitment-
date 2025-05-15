#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""API REST pour le service de matching SmartMatch."""

import os
import json
import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Union

from fastapi import FastAPI, HTTPException, Depends, Body
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

class MatchResponse(BaseModel):
    status: str
    matches_count: int
    insights_count: Optional[int] = None
    top_matches: List[Dict[str, Any]] = []
    insights: Optional[List[Dict[str, Any]]] = None

class SimpleMatchResponse(BaseModel):
    status: str
    matches_count: int
    results: List[Dict[str, Any]] = []

class SpecificMatchResponse(BaseModel):
    status: str
    result: Dict[str, Any]

class CVMatchRequest(BaseModel):
    cv_data: Dict[str, Any] = Field(..., description="Données du CV à parser")
    job_ids: Optional[List[str]] = Field(None, description="Liste d'IDs de fiches de poste à matcher")

class JobMatchRequest(BaseModel):
    job_data: Dict[str, Any] = Field(..., description="Données de la fiche de poste à parser")
    candidate_ids: Optional[List[str]] = Field(None, description="Liste d'IDs de candidats à matcher")

class DirectMatchRequest(BaseModel):
    cv_data: Dict[str, Any] = Field(..., description="Données du CV à parser")
    job_data: Dict[str, Any] = Field(..., description="Données de la fiche de poste à parser")

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
    
    @app.post("/match", response_model=MatchResponse, tags=["Matching"])
    async def match_all():
        """
        Lance un matching complet entre tous les CVs et fiches de poste.
        """
        try:
            # Exécuter le pipeline complet
            matching_results, insights = pipeline.run_full_pipeline()
            
            # Préparer la réponse
            response = {
                "status": "success",
                "matches_count": len(matching_results),
                "insights_count": len(insights),
                "top_matches": matching_results[:10] if matching_results else [],
                "insights": insights[:5] if insights else []
            }
            
            return response
        except Exception as e:
            logger.error(f"Erreur lors du matching complet: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/match/cv/{cv_id}/job/{job_id}", response_model=SpecificMatchResponse, tags=["Matching"])
    async def match_specific(cv_id: str, job_id: str):
        """
        Lance un matching spécifique entre un CV et une fiche de poste.
        """
        try:
            # Utiliser la version asynchrone du matching spécifique
            result = await pipeline.match_specific_async(cv_id, job_id)
            
            if result:
                return {"status": "success", "result": result}
            else:
                raise HTTPException(
                    status_code=404, 
                    detail="Matching impossible ou aucun résultat trouvé"
                )
        except Exception as e:
            logger.error(f"Erreur lors du matching spécifique: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/match/cv/{cv_id}/all", response_model=SimpleMatchResponse, tags=["Matching"])
    async def match_cv_with_all(cv_id: str):
        """
        Lance un matching entre un CV et toutes les fiches de poste.
        """
        try:
            # Utiliser la version asynchrone du matching CV avec tous
            results = await pipeline.match_cv_with_all_jobs_async(cv_id)
            
            # Trier les résultats par score décroissant
            results.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            return {
                "status": "success", 
                "matches_count": len(results),
                "results": results
            }
        except Exception as e:
            logger.error(f"Erreur lors du matching CV avec toutes les fiches: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/match/job/{job_id}/all", response_model=SimpleMatchResponse, tags=["Matching"])
    async def match_job_with_all(job_id: str):
        """
        Lance un matching entre une fiche de poste et tous les CVs.
        """
        try:
            # Utiliser la version asynchrone du matching fiche avec tous
            results = await pipeline.match_job_with_all_cvs_async(job_id)
            
            # Trier les résultats par score décroissant
            results.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            return {
                "status": "success", 
                "matches_count": len(results),
                "results": results
            }
        except Exception as e:
            logger.error(f"Erreur lors du matching fiche de poste avec tous les CVs: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/match/direct", response_model=SpecificMatchResponse, tags=["Matching"])
    async def match_direct(request: DirectMatchRequest):
        """
        Parse et match directement un CV et une fiche de poste à partir de leurs données brutes.
        """
        try:
            # Utiliser la méthode de parsing et matching direct
            result = await pipeline.parse_and_match_cv_job(request.cv_data, request.job_data)
            
            if result.get("status") == "success":
                return result
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=result.get("message", "Erreur lors du matching direct")
                )
        except Exception as e:
            logger.error(f"Erreur lors du matching direct: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/match/cv", response_model=SimpleMatchResponse, tags=["Matching"])
    async def match_cv_with_jobs(request: CVMatchRequest):
        """
        Parse un CV et le match avec des fiches de poste spécifiques ou toutes les fiches disponibles.
        """
        try:
            # Parser le CV
            parsed_cv = await pipeline.parsing_adapter.parse_cv(request.cv_data)
            
            if not parsed_cv:
                raise HTTPException(
                    status_code=400, 
                    detail="Erreur lors du parsing du CV"
                )
            
            # Convertir au format SmartMatch
            candidate = pipeline.parsing_adapter.cv_to_candidate(parsed_cv)
            
            # Si des job_ids sont fournis, récupérer uniquement ces fiches de poste
            if request.job_ids:
                companies = []
                for job_id in request.job_ids:
                    job_data = await pipeline.parsing_adapter.get_job_data_async(job_id)
                    if job_data:
                        companies.append(pipeline.parsing_adapter.job_to_company(job_data))
            else:
                # Sinon, récupérer toutes les fiches de poste
                companies = pipeline.parsing_adapter.convert_all_jobs()
            
            # Exécuter le matching
            results = pipeline.matcher.match([candidate], companies)
            
            # Trier les résultats par score décroissant
            results.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            return {
                "status": "success", 
                "matches_count": len(results),
                "results": results
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur lors du matching CV avec fiches de poste: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/match/job", response_model=SimpleMatchResponse, tags=["Matching"])
    async def match_job_with_candidates(request: JobMatchRequest):
        """
        Parse une fiche de poste et la match avec des candidats spécifiques ou tous les candidats disponibles.
        """
        try:
            # Parser la fiche de poste
            parsed_job = await pipeline.parsing_adapter.parse_job(request.job_data)
            
            if not parsed_job:
                raise HTTPException(
                    status_code=400, 
                    detail="Erreur lors du parsing de la fiche de poste"
                )
            
            # Convertir au format SmartMatch
            company = pipeline.parsing_adapter.job_to_company(parsed_job)
            
            # Si des candidate_ids sont fournis, récupérer uniquement ces candidats
            if request.candidate_ids:
                candidates = []
                for candidate_id in request.candidate_ids:
                    cv_data = await pipeline.parsing_adapter.get_cv_data_async(candidate_id)
                    if cv_data:
                        candidates.append(pipeline.parsing_adapter.cv_to_candidate(cv_data))
            else:
                # Sinon, récupérer tous les candidats
                candidates = pipeline.parsing_adapter.convert_all_cvs()
            
            # Exécuter le matching
            results = pipeline.matcher.match(candidates, [company])
            
            # Trier les résultats par score décroissant
            results.sort(key=lambda x: x.get("score", 0), reverse=True)
            
            return {
                "status": "success", 
                "matches_count": len(results),
                "results": results
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erreur lors du matching fiche de poste avec candidats: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/match/results", tags=["Results"])
    async def get_all_results():
        """
        Récupère tous les résultats de matching.
        """
        try:
            # Lister tous les fichiers de résultats dans le répertoire
            result_files = [f for f in os.listdir(results_dir) if f.startswith("matching_results_")]
            result_files.sort(reverse=True)  # Tri par date décroissante
            
            # Récupérer les 5 derniers résultats
            latest_results = []
            for filename in result_files[:5]:
                filepath = os.path.join(results_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    results = json.load(f)
                    latest_results.append({
                        "filename": filename,
                        "timestamp": filename.split("_")[-1].split(".")[0],
                        "matches_count": len(results),
                        "results": results[:10]  # Limiter à 10 résultats par fichier
                    })
            
            return {
                "status": "success", 
                "count": len(latest_results),
                "results": latest_results
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des résultats: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/match/insights", tags=["Results"])
    async def get_all_insights():
        """
        Récupère tous les insights générés.
        """
        try:
            # Lister tous les fichiers d'insights dans le répertoire
            insight_files = [f for f in os.listdir(results_dir) if f.startswith("insights_")]
            insight_files.sort(reverse=True)  # Tri par date décroissante
            
            # Récupérer les 5 derniers insights
            latest_insights = []
            for filename in insight_files[:5]:
                filepath = os.path.join(results_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    insights = json.load(f)
                    latest_insights.append({
                        "filename": filename,
                        "timestamp": filename.split("_")[-1].split(".")[0],
                        "insights_count": len(insights),
                        "insights": insights  # Inclure tous les insights
                    })
            
            return {
                "status": "success", 
                "count": len(latest_insights),
                "results": latest_insights
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des insights: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app

def start_api(host="0.0.0.0", port=5052, debug=False):
    """
    Démarre l'API REST.
    
    Args:
        host (str): Adresse d'hôte
        port (int): Port d'écoute
        debug (bool): Mode debug
    """
    import uvicorn
    
    # Configuration depuis les variables d'environnement
    cv_parser_url = os.environ.get("CV_PARSER_URL", "http://localhost:5051")
    job_parser_url = os.environ.get("JOB_PARSER_URL", "http://localhost:5055")
    results_dir = os.environ.get("MATCHING_RESULTS_DIR", "matching_results")
    
    # Créer l'application
    app = create_app(cv_parser_url, job_parser_url, results_dir)
    
    # Démarrer le serveur
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    # Démarrer l'API
    start_api()
