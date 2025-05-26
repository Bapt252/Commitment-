#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SuperSmartMatch - Service Unifié de Matching

Ce service regroupe TOUS les algorithmes de matching de Nexten :
- Smart Match (bidirectionnel avec géolocalisation)
- Enhanced Matching Engine (moteur avancé)
- Analyseur Sémantique (compétences)
- Job Analyzer (analyse des offres)
- Algorithme Original vs Personnalisé

Auteur: Nexten Team
Version: 1.0.0
"""

import os
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from algorithm_manager import AlgorithmManager
from algorithm_selector import AlgorithmSelector
from unified_api import UnifiedMatchingAPI

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/supersmartmatch.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration FastAPI
app = FastAPI(
    title="SuperSmartMatch API",
    description="Service unifié regroupant tous les algorithmes de matching Nexten",
    version="1.0.0",
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

# Initialisation des composants
algorithm_manager = AlgorithmManager()
algorithm_selector = AlgorithmSelector()
unified_api = UnifiedMatchingAPI(algorithm_manager, algorithm_selector)

# Modèles Pydantic
class CandidateData(BaseModel):
    """Données du candidat"""
    competences: List[str] = Field(default=[], description="Liste des compétences")
    adresse: str = Field(default="", description="Adresse du candidat")
    mobilite: str = Field(default="local", description="Préférence de mobilité (local/regional/national/remote/hybrid)")
    annees_experience: int = Field(default=0, description="Années d'expérience")
    salaire_souhaite: int = Field(default=0, description="Salaire souhaité en euros")
    contrats_recherches: List[str] = Field(default=["CDI"], description="Types de contrats recherchés")
    disponibilite: str = Field(default="immediate", description="Disponibilité")
    date_disponibilite: Optional[str] = Field(default=None, description="Date de disponibilité (format DD/MM/YYYY)")
    formation: str = Field(default="", description="Niveau de formation")
    domaines_interets: List[str] = Field(default=[], description="Domaines d'intérêt")
    temps_trajet_max: int = Field(default=60, description="Temps de trajet maximum en minutes")

class JobData(BaseModel):
    """Données d'une offre d'emploi"""
    id: int = Field(description="Identifiant unique de l'offre")
    titre: str = Field(description="Titre du poste")
    competences: List[str] = Field(default=[], description="Compétences requises")
    localisation: str = Field(default="", description="Localisation du poste")
    type_contrat: str = Field(default="CDI", description="Type de contrat")
    salaire: str = Field(default="", description="Fourchette de salaire")
    politique_remote: str = Field(default="office", description="Politique télétravail (office/hybrid/remote)")
    experience: str = Field(default="", description="Expérience requise")
    date_debut: Optional[str] = Field(default=None, description="Date de début souhaitée")
    entreprise: str = Field(default="", description="Nom de l'entreprise")
    description: str = Field(default="", description="Description du poste")
    avantages: List[str] = Field(default=[], description="Avantages proposés")

class MatchingRequest(BaseModel):
    """Requête de matching"""
    candidate: CandidateData = Field(description="Données du candidat")
    jobs: List[JobData] = Field(description="Liste des offres d'emploi")
    algorithm: str = Field(
        default="auto",
        description="Algorithme à utiliser (auto/smart-match/enhanced/semantic/hybrid/comparison)"
    )
    options: Dict[str, Any] = Field(default_factory=dict, description="Options supplémentaires")
    limit: int = Field(default=10, description="Nombre maximum de résultats")

class MatchingResponse(BaseModel):
    """Réponse de matching"""
    success: bool = Field(description="Succès de l'opération")
    algorithm_used: str = Field(description="Algorithme utilisé")
    processing_time: float = Field(description="Temps de traitement en secondes")
    total_jobs: int = Field(description="Nombre total d'offres analysées")
    returned_jobs: int = Field(description="Nombre d'offres retournées")
    matches: List[Dict[str, Any]] = Field(description="Résultats de matching")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées supplémentaires")

class AlgorithmInfo(BaseModel):
    """Informations sur un algorithme"""
    name: str = Field(description="Nom de l'algorithme")
    version: str = Field(description="Version")
    description: str = Field(description="Description")
    strengths: List[str] = Field(description="Points forts")
    best_for: List[str] = Field(description="Cas d'usage optimaux")
    performance: Dict[str, Any] = Field(description="Métriques de performance")

# Routes principales
@app.get("/", tags=["Health"])
async def root():
    """Route racine"""
    return {
        "service": "SuperSmartMatch",
        "version": "1.0.0",
        "description": "Service unifié de matching Nexten",
        "status": "operational",
        "algorithms_available": algorithm_manager.get_available_algorithms(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Vérification de santé du service"""
    try:
        # Test de tous les algorithmes
        algorithm_status = algorithm_manager.health_check()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "algorithms": algorithm_status,
            "uptime": time.time(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/algorithms", response_model=List[AlgorithmInfo], tags=["Algorithms"])
async def list_algorithms():
    """Liste tous les algorithmes disponibles"""
    return algorithm_manager.get_algorithms_info()

@app.get("/algorithms/{algorithm_name}", response_model=AlgorithmInfo, tags=["Algorithms"])
async def get_algorithm_info(algorithm_name: str):
    """Obtient les informations détaillées d'un algorithme"""
    try:
        return algorithm_manager.get_algorithm_info(algorithm_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/v1/match", response_model=MatchingResponse, tags=["Matching"])
async def match_candidate_with_jobs(request: MatchingRequest):
    """Endpoint principal de matching unifié"""
    start_time = time.time()
    
    try:
        logger.info(f"Nouvelle requête de matching - Algorithme: {request.algorithm}, Jobs: {len(request.jobs)}")
        
        # Validation des données
        if not request.jobs:
            raise HTTPException(status_code=400, detail="Aucune offre d'emploi fournie")
        
        if request.limit <= 0 or request.limit > 100:
            raise HTTPException(status_code=400, detail="Limite doit être entre 1 et 100")
        
        # Exécution du matching via l'API unifiée
        result = await unified_api.match(
            candidate_data=request.candidate.dict(),
            jobs_data=[job.dict() for job in request.jobs],
            algorithm=request.algorithm,
            options=request.options,
            limit=request.limit
        )
        
        processing_time = time.time() - start_time
        
        response = MatchingResponse(
            success=True,
            algorithm_used=result["algorithm_used"],
            processing_time=processing_time,
            total_jobs=len(request.jobs),
            returned_jobs=len(result["matches"]),
            matches=result["matches"],
            metadata={
                "selection_reason": result.get("selection_reason", ""),
                "algorithm_version": result.get("algorithm_version", ""),
                "performance_metrics": result.get("performance_metrics", {}),
                **request.options
            }
        )
        
        logger.info(f"Matching terminé - Temps: {processing_time:.3f}s, Algorithme: {result['algorithm_used']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Erreur lors du matching: {str(e)}, Temps: {processing_time:.3f}s")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@app.post("/api/v1/compare", tags=["Comparison"])
async def compare_algorithms(request: MatchingRequest):
    """Compare tous les algorithmes sur le même dataset"""
    try:
        logger.info(f"Comparaison d'algorithmes demandée - Jobs: {len(request.jobs)}")
        
        result = await unified_api.compare_all_algorithms(
            candidate_data=request.candidate.dict(),
            jobs_data=[job.dict() for job in request.jobs],
            limit=request.limit
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Erreur lors de la comparaison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@app.post("/api/v1/recommend-algorithm", tags=["Algorithms"])
async def recommend_algorithm(request: MatchingRequest):
    """Recommande le meilleur algorithme pour une situation donnée"""
    try:
        recommendation = algorithm_selector.recommend_algorithm(
            candidate_data=request.candidate.dict(),
            jobs_count=len(request.jobs),
            options=request.options
        )
        
        return {
            "recommended_algorithm": recommendation["algorithm"],
            "confidence": recommendation["confidence"],
            "reasoning": recommendation["reasoning"],
            "alternatives": recommendation.get("alternatives", []),
            "performance_prediction": recommendation.get("performance_prediction", {})
        }
        
    except Exception as e:
        logger.error(f"Erreur lors de la recommandation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

@app.get("/api/v1/stats", tags=["Statistics"])
async def get_service_stats():
    """Statistiques d'utilisation du service"""
    try:
        return algorithm_manager.get_usage_stats()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(e)}")

# Route de test pour le développement
@app.post("/api/v1/test", tags=["Development"])
async def test_endpoint(request: MatchingRequest):
    """Endpoint de test pour le développement"""
    return {
        "message": "Test réussi",
        "received_data": {
            "candidate_skills": request.candidate.competences,
            "jobs_count": len(request.jobs),
            "algorithm": request.algorithm,
            "limit": request.limit
        },
        "timestamp": datetime.now().isoformat()
    }

# Gestionnaire d'erreurs
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erreur non gérée: {str(exc)}")
    return {
        "error": "Erreur interne du serveur",
        "detail": str(exc),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    # Configuration pour le développement
    port = int(os.getenv("PORT", 5070))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Démarrage de SuperSmartMatch sur {host}:{port}")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT", "production") == "development",
        log_level="info"
    )
