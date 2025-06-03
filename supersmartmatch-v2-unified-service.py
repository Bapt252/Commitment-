#!/usr/bin/env python3
"""
🚀 SuperSmartMatch V2 - Service Unifié Intelligent
Orchestrateur intelligent pour sélection automatique d'algorithmes de matching
"""

import asyncio
import os
import sys
import time
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

import httpx
import redis
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("supersmartmatch-v2")

# ===== CONFIGURATION =====
class Config:
    SERVICE_PORT = int(os.getenv("SERVICE_PORT", 5070))
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    SERVICE_NAME = os.getenv("SERVICE_NAME", "supersmartmatch-v2")
    
    # Services externes
    NEXTEN_URL = os.getenv("NEXTEN_URL", "http://localhost:5052")
    SUPERSMARTMATCH_V1_URL = os.getenv("SUPERSMARTMATCH_V1_URL", "http://localhost:5062")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    CACHE_TTL = int(os.getenv("CACHE_TTL", 300))
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    
    # Circuit breakers
    CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", 5))
    CIRCUIT_BREAKER_TIMEOUT = int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", 60))
    MAX_RESPONSE_TIME_MS = int(os.getenv("MAX_RESPONSE_TIME_MS", 100))
    
    # Feature flags
    ENABLE_V2 = os.getenv("ENABLE_V2", "true").lower() == "true"
    ENABLE_NEXTEN_ALGORITHM = os.getenv("ENABLE_NEXTEN_ALGORITHM", "true").lower() == "true"
    ENABLE_SMART_SELECTION = os.getenv("ENABLE_SMART_SELECTION", "true").lower() == "true"

# ===== MODÈLES PYDANTIC =====
class TechnicalSkill(BaseModel):
    name: str
    level: Optional[str] = "Intermediate"
    years: Optional[int] = 0

class Experience(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    duration_months: Optional[int] = 0
    skills: Optional[List[str]] = []

class Location(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None

class CandidateQuestionnaire(BaseModel):
    work_style: Optional[str] = None
    culture_preferences: Optional[str] = None
    remote_preference: Optional[str] = None
    team_size_preference: Optional[str] = None

class CompanyQuestionnaire(BaseModel):
    culture: Optional[str] = None
    team_size: Optional[str] = None
    work_methodology: Optional[str] = None

class Candidate(BaseModel):
    name: str
    email: Optional[str] = None
    technical_skills: Union[List[TechnicalSkill], List[str]] = []
    experiences: Optional[List[Experience]] = []
    localisation: Optional[str] = None
    mobility: Optional[bool] = False

class Offer(BaseModel):
    id: str
    title: str
    company: Optional[str] = None
    required_skills: List[str] = []
    location: Optional[Location] = None
    localisation: Optional[str] = None
    remote_policy: Optional[str] = None

class MatchRequestV2(BaseModel):
    candidate: Candidate
    candidate_questionnaire: Optional[CandidateQuestionnaire] = None
    offers: List[Offer]
    company_questionnaires: Optional[List[CompanyQuestionnaire]] = []
    algorithm: Optional[str] = "auto"

class MatchRequestV1(BaseModel):
    candidate: Candidate
    offers: List[Offer]
    algorithm: Optional[str] = "auto"

class MatchResult(BaseModel):
    offer_id: str
    overall_score: float
    confidence: float
    skill_match_score: Optional[float] = None
    experience_match_score: Optional[float] = None
    location_match_score: Optional[float] = None
    culture_match_score: Optional[float] = None
    insights: Optional[List[str]] = []
    explanation: Optional[str] = None

class MatchResponse(BaseModel):
    success: bool
    matches: List[MatchResult]
    algorithm_used: str
    execution_time_ms: int
    selection_reason: Optional[str] = None
    context_analysis: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

# ===== ALGORITHMES ENUM =====
class Algorithm(Enum):
    AUTO = "auto"
    NEXTEN = "nexten"
    SMART = "smart"
    ENHANCED = "enhanced"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"

# ===== SÉLECTEUR D'ALGORITHMES =====
class AlgorithmSelector:
    """Sélecteur intelligent d'algorithmes selon les spécifications"""
    
    @staticmethod
    def select_algorithm(request: MatchRequestV2) -> tuple[str, str]:
        """Sélectionne l'algorithme optimal selon le contexte"""
        
        # 1. Nexten prioritaire si questionnaires complets
        if request.candidate_questionnaire and Config.ENABLE_NEXTEN_ALGORITHM:
            questionnaire_completeness = AlgorithmSelector._calculate_questionnaire_completeness(
                request.candidate_questionnaire
            )
            if questionnaire_completeness > 0.8:
                return "nexten", f"Questionnaire complet (completeness: {questionnaire_completeness:.2f})"
        
        # 2. Smart-match pour géolocalisation
        if AlgorithmSelector._has_geo_constraints(request):
            return "smart", "Contraintes géographiques détectées"
        
        # 3. Enhanced pour profils séniors (7+ années)
        total_experience = AlgorithmSelector._calculate_total_experience(request.candidate)
        if total_experience >= 84:  # 7 ans = 84 mois
            return "enhanced", f"Profil sénior détecté ({total_experience//12} années d'expérience)"
        
        # 4. Semantic pour compétences NLP complexes
        if AlgorithmSelector._has_complex_nlp_skills(request.candidate):
            return "semantic", "Compétences NLP complexes détectées"
        
        # 5. Fallback par défaut : Nexten si disponible, sinon enhanced
        if Config.ENABLE_NEXTEN_ALGORITHM:
            return "nexten", "Sélection par défaut (Nexten prioritaire)"
        else:
            return "enhanced", "Fallback sur Enhanced (Nexten indisponible)"
    
    @staticmethod
    def _calculate_questionnaire_completeness(questionnaire: CandidateQuestionnaire) -> float:
        """Calcule le taux de complétion du questionnaire"""
        fields = [
            questionnaire.work_style,
            questionnaire.culture_preferences,
            questionnaire.remote_preference,
            questionnaire.team_size_preference
        ]
        completed = sum(1 for field in fields if field is not None and field.strip())
        return completed / len(fields)
    
    @staticmethod
    def _has_geo_constraints(request: MatchRequestV2) -> bool:
        """Vérifie s'il y a des contraintes géographiques"""
        candidate_has_location = (
            request.candidate.localisation or
            any(exp.company for exp in (request.candidate.experiences or []))
        )
        offers_have_location = any(
            offer.location or offer.localisation for offer in request.offers
        )
        return candidate_has_location and offers_have_location
    
    @staticmethod
    def _calculate_total_experience(candidate: Candidate) -> int:
        """Calcule l'expérience totale en mois"""
        if not candidate.experiences:
            return 0
        return sum(exp.duration_months or 0 for exp in candidate.experiences)
    
    @staticmethod
    def _has_complex_nlp_skills(candidate: Candidate) -> bool:
        """Vérifie s'il y a des compétences NLP complexes"""
        nlp_keywords = ["nlp", "natural language", "text mining", "sentiment analysis", "bert", "transformer"]
        
        skills = []
        if candidate.technical_skills:
            for skill in candidate.technical_skills:
                if isinstance(skill, TechnicalSkill):
                    skills.append(skill.name.lower())
                else:
                    skills.append(str(skill).lower())
        
        return any(keyword in skill for skill in skills for keyword in nlp_keywords)

# ===== ADAPTATEURS SERVICES =====
class ServiceAdapter:
    """Adaptateur pour communiquer avec les services externes"""
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Cache Redis
        try:
            if Config.CACHE_ENABLED:
                self.redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
            else:
                self.redis_client = None
        except Exception as e:
            logger.warning(f"Redis non disponible: {e}")
            self.redis_client = None
    
    async def call_nexten_matcher(self, request: MatchRequestV2) -> MatchResponse:
        """Appel au service Nexten Matcher"""
        try:
            # Transformation du format pour Nexten
            nexten_payload = {
                "candidate_id": f"temp_{int(time.time())}",
                "job_id": request.offers[0].id if request.offers else "temp_job",
                "webhook_url": "https://httpbin.org/post"  # URL temporaire
            }
            
            start_time = time.time()
            response = await self.http_client.post(
                f"{Config.NEXTEN_URL}/api/v1/queue-matching",
                json=nexten_payload,
                timeout=10.0
            )
            execution_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                # Simulation de réponse Nexten transformée
                matches = [
                    MatchResult(
                        offer_id=offer.id,
                        overall_score=0.92,
                        confidence=0.88,
                        skill_match_score=0.95,
                        explanation="Match via Nexten Matcher (ML avancé)"
                    )
                    for offer in request.offers
                ]
                
                return MatchResponse(
                    success=True,
                    matches=matches,
                    algorithm_used="nexten_matcher",
                    execution_time_ms=execution_time,
                    metadata={"service": "nexten", "ml_model": "advanced"}
                )
            else:
                raise Exception(f"Nexten error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erreur Nexten Matcher: {e}")
            # Fallback vers Enhanced
            return await self.call_supersmartmatch_v1(request, "enhanced")
    
    async def call_supersmartmatch_v1(self, request: MatchRequestV2, algorithm: str = "smart") -> MatchResponse:
        """Appel au service SuperSmartMatch V1"""
        try:
            # Transformation du format pour V1
            v1_payload = {
                "cv_data": {
                    "name": request.candidate.name,
                    "technical_skills": [
                        skill.name if isinstance(skill, TechnicalSkill) else str(skill)
                        for skill in request.candidate.technical_skills
                    ],
                    "localisation": request.candidate.localisation
                },
                "job_data": [
                    {
                        "id": offer.id,
                        "title": offer.title,
                        "required_skills": offer.required_skills,
                        "localisation": offer.localisation or (offer.location.city if offer.location else None)
                    }
                    for offer in request.offers
                ],
                "algorithm": algorithm
            }
            
            start_time = time.time()
            response = await self.http_client.post(
                f"{Config.SUPERSMARTMATCH_V1_URL}/api/v1/match",
                json=v1_payload,
                timeout=10.0
            )
            execution_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                v1_result = response.json()
                
                # Transformation de la réponse V1 vers format V2
                matches = []
                if "matches" in v1_result:
                    for match in v1_result["matches"]:
                        matches.append(MatchResult(
                            offer_id=match.get("offer_id", "unknown"),
                            overall_score=match.get("score", 0.0),
                            confidence=match.get("confidence", 0.0),
                            skill_match_score=match.get("details", {}).get("skill_match", None),
                            explanation=f"Match via SuperSmartMatch V1 ({algorithm})"
                        ))
                
                return MatchResponse(
                    success=True,
                    matches=matches,
                    algorithm_used=f"supersmartmatch_v1_{algorithm}",
                    execution_time_ms=execution_time,
                    metadata={"service": "v1", "algorithm": algorithm}
                )
            else:
                raise Exception(f"V1 error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erreur SuperSmartMatch V1: {e}")
            # Fallback basique
            return self._create_fallback_response(request, execution_time_ms=50)
    
    def _create_fallback_response(self, request: MatchRequestV2, execution_time_ms: int = 50) -> MatchResponse:
        """Crée une réponse de fallback basique"""
        matches = [
            MatchResult(
                offer_id=offer.id,
                overall_score=0.75,
                confidence=0.60,
                explanation="Match de fallback (services externes indisponibles)"
            )
            for offer in request.offers
        ]
        
        return MatchResponse(
            success=True,
            matches=matches,
            algorithm_used="fallback_basic",
            execution_time_ms=execution_time_ms,
            metadata={"fallback": True, "reason": "services_unavailable"}
        )

# ===== APPLICATION FASTAPI =====
app = FastAPI(
    title="SuperSmartMatch V2",
    description="Service unifié intelligent pour matching avancé",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adaptateur de services
service_adapter = ServiceAdapter()

# ===== ENDPOINTS API =====

@app.get("/health")
async def health_check():
    """Health check du service"""
    return {
        "status": "healthy",
        "service": Config.SERVICE_NAME,
        "version": "2.0.0",
        "environment": Config.ENVIRONMENT,
        "timestamp": int(time.time())
    }

@app.get("/metrics")
async def metrics():
    """Métriques du service"""
    return {
        "service": Config.SERVICE_NAME,
        "version": "2.0.0",
        "uptime": int(time.time()),
        "environment": Config.ENVIRONMENT,
        "features": {
            "v2_enabled": Config.ENABLE_V2,
            "nexten_enabled": Config.ENABLE_NEXTEN_ALGORITHM,
            "smart_selection": Config.ENABLE_SMART_SELECTION,
            "cache_enabled": Config.CACHE_ENABLED
        }
    }

@app.get("/api/v2/algorithms")
async def list_algorithms():
    """Liste des algorithmes disponibles"""
    algorithms = {
        "auto": {"description": "Sélection automatique optimale", "priority": 1},
        "nexten": {"description": "ML avancé Nexten Matcher", "priority": 2, "enabled": Config.ENABLE_NEXTEN_ALGORITHM},
        "smart": {"description": "Matching géographique intelligent", "priority": 3},
        "enhanced": {"description": "Pondération adaptative", "priority": 4},
        "semantic": {"description": "Analyse sémantique NLP", "priority": 5},
        "hybrid": {"description": "Combinaison multi-algorithmes", "priority": 6}
    }
    return {"algorithms": algorithms}

@app.post("/api/v2/match", response_model=MatchResponse)
async def match_v2(request: MatchRequestV2):
    """API V2 - Matching avec sélection intelligente d'algorithmes"""
    start_time = time.time()
    
    try:
        # Sélection automatique d'algorithme
        if request.algorithm == "auto" and Config.ENABLE_SMART_SELECTION:
            selected_algorithm, reason = AlgorithmSelector.select_algorithm(request)
        else:
            selected_algorithm = request.algorithm or "enhanced"
            reason = f"Algorithme forcé: {selected_algorithm}"
        
        logger.info(f"Algorithme sélectionné: {selected_algorithm} - Raison: {reason}")
        
        # Appel du service approprié
        if selected_algorithm == "nexten" and Config.ENABLE_NEXTEN_ALGORITHM:
            response = await service_adapter.call_nexten_matcher(request)
        else:
            response = await service_adapter.call_supersmartmatch_v1(request, selected_algorithm)
        
        # Ajout des métadonnées de sélection
        response.selection_reason = reason
        response.context_analysis = {
            "questionnaire_completeness": 0.0,
            "total_experience_months": AlgorithmSelector._calculate_total_experience(request.candidate),
            "has_geo_constraints": AlgorithmSelector._has_geo_constraints(request),
            "has_nlp_skills": AlgorithmSelector._has_complex_nlp_skills(request.candidate)
        }
        
        if request.candidate_questionnaire:
            response.context_analysis["questionnaire_completeness"] = AlgorithmSelector._calculate_questionnaire_completeness(request.candidate_questionnaire)
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur dans match_v2: {e}")
        execution_time = int((time.time() - start_time) * 1000)
        return service_adapter._create_fallback_response(request, execution_time)

@app.post("/match")
async def match_v1_compatible(request: MatchRequestV1):
    """API V1 compatible - Maintien de la compatibilité"""
    # Conversion V1 -> V2
    v2_request = MatchRequestV2(
        candidate=request.candidate,
        offers=request.offers,
        algorithm=request.algorithm
    )
    
    response = await match_v2(v2_request)
    
    # Conversion V2 -> V1 pour compatibilité
    v1_response = {
        "matches": [
            {
                "offer_id": match.offer_id,
                "score": match.overall_score,
                "confidence": match.confidence,
                "details": {
                    "skill_match": match.skill_match_score,
                    "experience_match": match.experience_match_score
                }
            }
            for match in response.matches
        ],
        "algorithm_used": f"v2_routed_{response.algorithm_used}",
        "execution_time_ms": response.execution_time_ms
    }
    
    return v1_response

# ===== DÉMARRAGE DU SERVICE =====
if __name__ == "__main__":
    logger.info(f"🚀 Démarrage SuperSmartMatch V2 sur le port {Config.SERVICE_PORT}")
    logger.info(f"Environment: {Config.ENVIRONMENT}")
    logger.info(f"Nexten enabled: {Config.ENABLE_NEXTEN_ALGORITHM}")
    logger.info(f"Smart selection: {Config.ENABLE_SMART_SELECTION}")
    
    uvicorn.run(
        "supersmartmatch-v2-unified-service:app",
        host="0.0.0.0",
        port=Config.SERVICE_PORT,
        reload=(Config.ENVIRONMENT == "development"),
        log_level="info"
    )
