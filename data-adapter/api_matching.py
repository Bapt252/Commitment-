#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API FastAPI pour le matching Commitment-
=======================================
API de production pour recevoir les données parsées et effectuer le matching
avec votre ImprovedMatchingEngine.

Auteur: Claude
Date: 26/05/2025
Version: 1.0.0
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import logging
import asyncio
import time
from datetime import datetime
import uuid

# Import de votre adaptateur
from data_adapter import (
    CommitmentDataAdapter, 
    create_matching_response, 
    create_error_response
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="Commitment- Matching API",
    description="API de matching entre CV et offres d'emploi utilisant ImprovedMatchingEngine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware CORS pour le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Instance globale de l'adaptateur
adapter = CommitmentDataAdapter()

# Cache simple pour les résultats (à remplacer par Redis en production)
results_cache = {}

# ============================================================================
# MODÈLES PYDANTIC
# ============================================================================

class CVData(BaseModel):
    """Modèle pour les données CV"""
    nom: Optional[str] = ""
    prenom: Optional[str] = ""
    email: Optional[str] = ""
    telephone: Optional[str] = ""
    adresse: Optional[str] = ""
    poste: Optional[str] = ""
    competences: List[str] = Field(..., min_items=1, description="Au moins une compétence requise")
    logiciels: Optional[List[str]] = []
    formation: Optional[str] = ""
    experience: Optional[str] = ""
    langues: Optional[List[str]] = []
    soft_skills: Optional[List[str]] = []
    
    @validator('competences')
    def validate_competences(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Au moins une compétence est requise')
        return [skill.strip() for skill in v if skill.strip()]


class QuestionnaireData(BaseModel):
    """Modèle pour les données du questionnaire"""
    adresse: Optional[str] = ""
    temps_trajet_max: Optional[int] = Field(60, ge=5, le=180)
    fourchette_salaire: Optional[str] = ""
    types_contrat: Optional[List[str]] = []
    disponibilite: Optional[str] = ""
    secteurs_interesse: Optional[List[str]] = []
    teletravail: Optional[bool] = False
    mobilite: Optional[bool] = True
    
    @validator('temps_trajet_max')
    def validate_temps_trajet(cls, v):
        if v and (v < 5 or v > 180):
            raise ValueError('Le temps de trajet doit être entre 5 et 180 minutes')
        return v


class JobData(BaseModel):
    """Modèle pour une offre d'emploi"""
    id: Optional[str] = ""
    titre: str = Field(..., min_length=3, description="Titre du poste requis")
    entreprise: Optional[str] = ""
    localisation: Optional[str] = ""
    description: Optional[str] = ""
    competences: List[str] = Field(..., min_items=1, description="Au moins une compétence requise")
    experience: Optional[str] = ""
    formation: Optional[str] = ""
    type_contrat: Optional[str] = "CDI"
    salaire: Optional[str] = ""
    date_debut: Optional[str] = ""
    avantages: Optional[List[str]] = []
    secteur: Optional[str] = ""
    
    @validator('competences')
    def validate_competences(cls, v):
        if not v or len(v) == 0:
            raise ValueError('Au moins une compétence est requise pour l\'offre')
        return [skill.strip() for skill in v if skill.strip()]


class MatchingOptions(BaseModel):
    """Options pour le matching"""
    limit: Optional[int] = Field(10, ge=1, le=100)
    min_score: Optional[int] = Field(0, ge=0, le=100)
    include_details: Optional[bool] = True


class CompleteMatchingRequest(BaseModel):
    """Requête complète de matching"""
    cv_data: CVData
    questionnaire_data: Optional[QuestionnaireData] = QuestionnaireData()
    jobs_data: List[JobData] = Field(..., min_items=1, max_items=100)
    options: Optional[MatchingOptions] = MatchingOptions()


class BatchMatchingRequest(BaseModel):
    """Requête de matching en lot"""
    candidates: List[Dict[str, Any]]  # Plusieurs candidats
    jobs_data: List[JobData]
    options: Optional[MatchingOptions] = MatchingOptions()


# ============================================================================
# UTILITAIRES
# ============================================================================

async def get_adapter():
    """Dependency injection pour l'adaptateur"""
    return adapter


def generate_request_id():
    """Génère un ID unique pour la requête"""
    return str(uuid.uuid4())


def cache_results(request_id: str, results: Any, ttl: int = 3600):
    """Met en cache les résultats (simplifié)"""
    results_cache[request_id] = {
        'data': results,
        'timestamp': time.time(),
        'ttl': ttl
    }


def get_cached_results(request_id: str) -> Optional[Any]:
    """Récupère les résultats du cache"""
    if request_id in results_cache:
        cached = results_cache[request_id]
        if time.time() - cached['timestamp'] < cached['ttl']:
            return cached['data']
        else:
            del results_cache[request_id]
    return None


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Point de contrôle de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Commitment- Matching API",
        "version": "1.0.0"
    }


@app.get("/status")
async def status_check():
    """Statut détaillé du service"""
    try:
        # Test de l'adaptateur
        test_cv = {"competences": ["Python"]}
        adapter.adapt_cv_data(test_cv)
        adapter_status = "OK"
    except Exception as e:
        adapter_status = f"ERROR: {str(e)}"
    
    return {
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "data_adapter": adapter_status,
            "cache": f"{len(results_cache)} items",
            "matching_engine": "Available"
        }
    }


@app.post("/api/matching/complete")
async def complete_matching(
    request: CompleteMatchingRequest,
    background_tasks: BackgroundTasks,
    adapter: CommitmentDataAdapter = Depends(get_adapter)
):
    """
    Endpoint principal pour le matching complet
    Traite CV + Questionnaire + Offres d'emploi
    """
    request_id = generate_request_id()
    start_time = time.time()
    
    try:
        logger.info(f"[{request_id}] Début matching: {len(request.jobs_data)} offres")
        
        # Validation supplémentaire
        if not request.cv_data.competences:
            raise HTTPException(
                status_code=400,
                detail="Au moins une compétence est requise dans le CV"
            )
        
        # Conversion en dictionnaires pour l'adaptateur
        cv_dict = request.cv_data.dict()
        questionnaire_dict = request.questionnaire_data.dict()
        jobs_dict = [job.dict() for job in request.jobs_data]
        
        # Lancer le matching
        results = adapter.run_matching(
            cv_data=cv_dict,
            questionnaire_data=questionnaire_dict,
            jobs_data=jobs_dict,
            limit=request.options.limit
        )
        
        # Filtrer par score minimum si spécifié
        if request.options.min_score > 0:
            results = [r for r in results if r.get('matching_score', 0) >= request.options.min_score]
        
        # Calculer les statistiques
        stats = adapter.get_matching_statistics(results)
        
        # Ajouter des métadonnées
        stats['request_id'] = request_id
        stats['processing_time'] = round(time.time() - start_time, 2)
        stats['jobs_processed'] = len(request.jobs_data)
        
        # Créer la réponse
        response = create_matching_response(results, stats)
        
        # Mise en cache en arrière-plan
        background_tasks.add_task(cache_results, request_id, response)
        
        logger.info(f"[{request_id}] Matching terminé: {len(results)} résultats en {stats['processing_time']}s")
        
        return response
        
    except Exception as e:
        logger.error(f"[{request_id}] Erreur matching: {str(e)}")
        error_response = create_error_response(
            f"Erreur lors du matching: {str(e)}",
            "MATCHING_ERROR"
        )
        return JSONResponse(
            status_code=500,
            content=error_response
        )


@app.post("/api/matching/single")
async def single_job_matching(
    cv_data: CVData,
    questionnaire_data: Optional[QuestionnaireData] = None,
    job_data: JobData = ...,
    adapter: CommitmentDataAdapter = Depends(get_adapter)
):
    """
    Matching entre un CV et une seule offre d'emploi
    Utile pour tester un match spécifique
    """
    try:
        # Utiliser questionnaire vide si non fourni
        if questionnaire_data is None:
            questionnaire_data = QuestionnaireData()
        
        # Conversion et matching
        cv_dict = cv_data.dict()
        questionnaire_dict = questionnaire_data.dict()
        job_dict = job_data.dict()
        
        results = adapter.run_matching(
            cv_data=cv_dict,
            questionnaire_data=questionnaire_dict,
            jobs_data=[job_dict],
            limit=1
        )
        
        if results:
            return {
                "success": True,
                "result": results[0],
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "Aucun résultat de matching",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Erreur matching single: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=create_error_response(str(e), "SINGLE_MATCHING_ERROR")
        )


@app.post("/api/matching/batch")
async def batch_matching(
    request: BatchMatchingRequest,
    background_tasks: BackgroundTasks,
    adapter: CommitmentDataAdapter = Depends(get_adapter)
):
    """
    Matching en lot pour plusieurs candidats
    """
    request_id = generate_request_id()
    
    try:
        batch_results = []
        
        for i, candidate in enumerate(request.candidates):
            try:
                # Extraire CV et questionnaire du candidat
                cv_data = candidate.get('cv_data', {})
                questionnaire_data = candidate.get('questionnaire_data', {})
                
                # Valider que le CV a des compétences
                if not cv_data.get('competences'):
                    continue
                
                # Lancer le matching pour ce candidat
                results = adapter.run_matching(
                    cv_data=cv_data,
                    questionnaire_data=questionnaire_data,
                    jobs_data=[job.dict() for job in request.jobs_data],
                    limit=request.options.limit
                )
                
                batch_results.append({
                    'candidate_index': i,
                    'candidate_id': cv_data.get('email', f'candidate_{i}'),
                    'results': results,
                    'stats': adapter.get_matching_statistics(results)
                })
                
            except Exception as e:
                logger.error(f"Erreur candidat {i}: {str(e)}")
                batch_results.append({
                    'candidate_index': i,
                    'error': str(e)
                })
        
        return {
            'success': True,
            'request_id': request_id,
            'processed_candidates': len(batch_results),
            'results': batch_results,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"[{request_id}] Erreur batch matching: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=create_error_response(str(e), "BATCH_MATCHING_ERROR")
        )


@app.get("/api/matching/results/{request_id}")
async def get_cached_matching_results(request_id: str):
    """
    Récupère les résultats d'un matching précédent depuis le cache
    """
    try:
        cached_results = get_cached_results(request_id)
        
        if cached_results:
            return cached_results
        else:
            raise HTTPException(
                status_code=404,
                detail="Résultats non trouvés ou expirés"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=create_error_response(str(e), "CACHE_ERROR")
        )


@app.post("/api/data/validate")
async def validate_data(
    cv_data: Optional[CVData] = None,
    questionnaire_data: Optional[QuestionnaireData] = None,
    job_data: Optional[JobData] = None
):
    """
    Valide les données sans effectuer de matching
    Utile pour le debugging côté frontend
    """
    try:
        validation_results = {
            'cv_data': None,
            'questionnaire_data': None,
            'job_data': None
        }
        
        if cv_data:
            validation_results['cv_data'] = {
                'valid': True,
                'competences_count': len(cv_data.competences),
                'normalized_skills': adapter.normalize_skills(cv_data.competences)
            }
        
        if questionnaire_data:
            validation_results['questionnaire_data'] = {
                'valid': True,
                'salary_parsed': adapter.parse_salary_range(questionnaire_data.fourchette_salaire)
            }
        
        if job_data:
            validation_results['job_data'] = {
                'valid': True,
                'competences_count': len(job_data.competences),
                'normalized_skills': adapter.normalize_skills(job_data.competences)
            }
        
        return {
            'success': True,
            'validation_results': validation_results,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content=create_error_response(str(e), "VALIDATION_ERROR")
        )


# ============================================================================
# GESTION DES ERREURS GLOBALES
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Gestionnaire d'erreurs HTTP personnalisé"""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(exc.detail, "HTTP_ERROR")
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Gestionnaire d'erreurs générales"""
    logger.error(f"Erreur non gérée: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            "Erreur interne du serveur",
            "INTERNAL_SERVER_ERROR"
        )
    )


# ============================================================================
# ÉVÉNEMENTS DE LIFECYCLE
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Actions au démarrage de l'application"""
    logger.info("🚀 Démarrage de l'API Commitment- Matching")
    logger.info("✅ Adaptateur de données initialisé")
    logger.info("✅ Cache en mémoire activé")
    logger.info("📡 API prête à recevoir des requêtes")


@app.on_event("shutdown")
async def shutdown_event():
    """Actions à l'arrêt de l'application"""
    logger.info("🛑 Arrêt de l'API Commitment- Matching")
    logger.info("🧹 Nettoyage du cache...")
    results_cache.clear()
    logger.info("✅ Arrêt propre terminé")


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    # Configuration pour le développement
    uvicorn.run(
        "api_matching:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
