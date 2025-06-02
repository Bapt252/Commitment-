#!/usr/bin/env python3
"""
🚀 SuperSmartMatch V2 - Unified Service on Port 5070

Service intelligent qui unifie :
- SuperSmartMatch V1 (port 5062) - 4 algorithmes existants 
- Nexten Matcher (port 5052) - 40K lignes ML avancé
- Nouveau port 5070 - Service unifié avec sélection intelligente

Architecture :
- Sélecteur d'algorithme intelligent basé sur contexte
- Adaptateurs HTTP pour intégration services existants
- Circuit breakers et fallbacks hiérarchiques
- Compatibilité 100% backward avec API V1
- Monitoring temps réel et métriques de performance
"""

import asyncio
import logging
import time
import json
import aiohttp
import redis.asyncio as redis
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AlgorithmType(Enum):
    """Types d'algorithmes disponibles"""
    NEXTEN = "nexten"           # Prioritaire pour données complètes
    SMART_MATCH = "smart"       # Géolocalisation et mobilité  
    ENHANCED = "enhanced"       # Pondération expérience/séniors
    SEMANTIC = "semantic"       # Analyse sémantique complexe
    BASIC = "basic"            # Fallback basique
    AUTO = "auto"              # Sélection automatique

@dataclass
class ServiceConfig:
    """Configuration des services externes"""
    nexten_url: str = "http://localhost:5052"
    supersmartmatch_v1_url: str = "http://localhost:5062" 
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 300
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60
    max_response_time_ms: int = 100

@dataclass 
class AlgorithmMetrics:
    """Métriques de performance d'un algorithme"""
    name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time_ms: float = 0.0
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    circuit_breaker_open: bool = False

class MatchRequest(BaseModel):
    """Modèle de requête de matching unifié"""
    candidate: Dict[str, Any] = Field(..., description="Données du candidat")
    offers: List[Dict[str, Any]] = Field(..., description="Liste des offres")
    algorithm: str = Field(default="auto", description="Algorithme à utiliser")
    user_id: Optional[str] = Field(default=None, description="ID utilisateur pour A/B testing")
    
    # Données optionnelles pour Nexten
    candidate_questionnaire: Optional[Dict[str, Any]] = None
    company_questionnaires: Optional[List[Dict[str, Any]]] = None
    
    # Options de configuration
    config: Optional[Dict[str, Any]] = None

class MatchResult(BaseModel):
    """Résultat de matching unifié"""
    offer_id: str
    overall_score: float
    confidence: float
    skill_match_score: float = 0.0
    experience_match_score: float = 0.0
    location_match_score: float = 0.0
    culture_match_score: float = 0.0
    insights: List[str] = []
    explanation: str = ""

class MatchResponse(BaseModel):
    """Réponse complète de matching"""
    success: bool
    matches: List[MatchResult]
    algorithm_used: str
    execution_time_ms: float
    selection_reason: str
    metadata: Dict[str, Any] = {}

class CircuitBreaker:
    """Circuit breaker pour protéger les services externes"""
    
    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        """Appel protégé par circuit breaker"""
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Vérifier si on peut tenter une réinitialisation"""
        return (self.last_failure_time and 
                datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout))
    
    def _on_success(self):
        """Reset circuit breaker après succès"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def _on_failure(self):
        """Gérer les échecs et ouvrir le circuit si nécessaire"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")

class IntelligentAlgorithmSelector:
    """Sélecteur intelligent d'algorithme basé sur le contexte"""
    
    def __init__(self):
        self.metrics: Dict[str, AlgorithmMetrics] = {
            algo.value: AlgorithmMetrics(algo.value) 
            for algo in AlgorithmType if algo != AlgorithmType.AUTO
        }
    
    def select_algorithm(self, request: MatchRequest) -> Tuple[AlgorithmType, str]:
        """
        Sélection intelligente d'algorithme basée sur le contexte
        
        Priorités selon les spécifications :
        1. Nexten si questionnaires complets
        2. Smart-match pour géolocalisation
        3. Enhanced pour séniors  
        4. Semantic pour NLP complexe
        5. Basic en fallback
        """
        
        if request.algorithm != "auto":
            try:
                return AlgorithmType(request.algorithm), f"Algorithme demandé: {request.algorithm}"
            except ValueError:
                logger.warning(f"Algorithme invalide: {request.algorithm}, utilisation de l'auto-sélection")
        
        # Analyse du contexte
        context = self._analyze_context(request)
        
        # Règles de sélection selon spécifications
        
        # 1. Nexten prioritaire si questionnaires complets
        if (context["has_complete_questionnaire"] and 
            context["questionnaire_completeness"] > 0.8 and
            not self.metrics["nexten"].circuit_breaker_open):
            return AlgorithmType.NEXTEN, "Questionnaires complets disponibles pour précision ML maximale"
        
        # 2. Smart-match pour contraintes géographiques
        if (context["has_location_constraints"] and 
            context["mobility_mentioned"] and
            not self.metrics["smart"].circuit_breaker_open):
            return AlgorithmType.SMART_MATCH, "Contraintes géographiques détectées avec mobilité"
        
        # 3. Enhanced pour profils séniors
        if (context["is_senior_profile"] and 
            context["experience_years"] >= 7 and
            not self.metrics["enhanced"].circuit_breaker_open):
            return AlgorithmType.ENHANCED, "Profil sénior (7+ ans) avec pondération expérience"
        
        # 4. Semantic pour compétences complexes
        if (context["complex_skills_detected"] and 
            context["skills_complexity_score"] > 0.7 and
            not self.metrics["semantic"].circuit_breaker_open):
            return AlgorithmType.SEMANTIC, "Compétences complexes nécessitant analyse sémantique"
        
        # 5. Fallback hiérarchique selon disponibilité
        fallback_hierarchy = [
            (AlgorithmType.NEXTEN, "Nexten fallback - meilleure performance globale"),
            (AlgorithmType.ENHANCED, "Enhanced fallback - pondération intelligente"), 
            (AlgorithmType.SMART_MATCH, "Smart fallback - géolocalisation"),
            (AlgorithmType.SEMANTIC, "Semantic fallback - analyse textuelle"),
            (AlgorithmType.BASIC, "Basic fallback - algorithme de secours")
        ]
        
        for algo_type, reason in fallback_hierarchy:
            if not self.metrics[algo_type.value].circuit_breaker_open:
                return algo_type, reason
        
        # Dernier recours - utiliser basic même si circuit ouvert
        return AlgorithmType.BASIC, "Fallback ultime - tous les circuits sont ouverts"
    
    def _analyze_context(self, request: MatchRequest) -> Dict[str, Any]:
        """Analyse du contexte de la requête pour la sélection d'algorithme"""
        
        candidate = request.candidate
        offers = request.offers
        questionnaire = request.candidate_questionnaire or {}
        
        # Analyse des questionnaires
        questionnaire_fields = len(questionnaire.keys()) if questionnaire else 0
        has_complete_questionnaire = questionnaire_fields >= 5
        questionnaire_completeness = min(questionnaire_fields / 10.0, 1.0)
        
        # Analyse géographique
        has_location_constraints = (
            candidate.get("localisation") or 
            candidate.get("location") or
            any(offer.get("localisation") or offer.get("location") for offer in offers)
        )
        
        mobility_mentioned = (
            "mobilité" in str(candidate).lower() or
            "mobility" in str(candidate).lower() or
            questionnaire.get("remote_preference") or
            questionnaire.get("mobility_preference")
        )
        
        # Analyse d'expérience
        experiences = candidate.get("experiences", [])
        experience_years = sum(
            exp.get("duration_months", 0) / 12 
            for exp in experiences 
            if isinstance(exp, dict)
        )
        is_senior_profile = experience_years >= 7
        
        # Analyse des compétences
        skills = candidate.get("technical_skills", []) or candidate.get("competences", [])
        skills_complexity_score = self._calculate_skills_complexity(skills)
        complex_skills_detected = skills_complexity_score > 0.7
        
        return {
            "has_complete_questionnaire": has_complete_questionnaire,
            "questionnaire_completeness": questionnaire_completeness,
            "has_location_constraints": has_location_constraints,
            "mobility_mentioned": mobility_mentioned,
            "is_senior_profile": is_senior_profile,
            "experience_years": experience_years,
            "complex_skills_detected": complex_skills_detected,
            "skills_complexity_score": skills_complexity_score,
            "offers_count": len(offers),
            "candidate_fields": len(candidate.keys())
        }
    
    def _calculate_skills_complexity(self, skills: List[Any]) -> float:
        """Calcule la complexité des compétences pour sélection semantic"""
        if not skills:
            return 0.0
        
        complexity_indicators = [
            "machine learning", "ml", "ai", "artificial intelligence",
            "deep learning", "neural networks", "nlp", "computer vision",
            "data science", "big data", "cloud architecture", "microservices",
            "devops", "kubernetes", "docker", "terraform"
        ]
        
        skills_text = " ".join(str(skill).lower() for skill in skills)
        matches = sum(1 for indicator in complexity_indicators if indicator in skills_text)
        
        return min(matches / len(complexity_indicators), 1.0)
    
    def update_metrics(self, algorithm: str, success: bool, response_time_ms: float):
        """Met à jour les métriques d'un algorithme"""
        if algorithm in self.metrics:
            metrics = self.metrics[algorithm]
            metrics.total_requests += 1
            
            if success:
                metrics.successful_requests += 1
                metrics.last_success = datetime.now()
                # Mise à jour moyenne mobile
                if metrics.avg_response_time_ms == 0:
                    metrics.avg_response_time_ms = response_time_ms
                else:
                    metrics.avg_response_time_ms = (
                        metrics.avg_response_time_ms * 0.9 + response_time_ms * 0.1
                    )
            else:
                metrics.failed_requests += 1
                metrics.last_failure = datetime.now()

class DataAdapter:
    """Adaptateur de données pour différents formats de services"""
    
    @staticmethod
    def to_nexten_format(request: MatchRequest) -> Dict[str, Any]:
        """Conversion vers format Nexten Matcher"""
        return {
            "candidate": {
                "profile": request.candidate,
                "questionnaire": request.candidate_questionnaire or {}
            },
            "jobs": [
                {
                    "id": str(i),
                    "data": offer,
                    "questionnaire": (
                        request.company_questionnaires[i] 
                        if request.company_questionnaires and i < len(request.company_questionnaires)
                        else {}
                    )
                }
                for i, offer in enumerate(request.offers)
            ],
            "algorithm": "advanced_ml"
        }
    
    @staticmethod
    def to_v1_format(request: MatchRequest) -> Dict[str, Any]:
        """Conversion vers format SuperSmartMatch V1"""
        return {
            "cv_data": request.candidate,
            "job_data": request.offers,
            "algorithm": request.algorithm if request.algorithm != "auto" else "smart-match",
            "config": request.config or {}
        }
    
    @staticmethod
    def from_nexten_response(response: Dict[str, Any]) -> List[MatchResult]:
        """Conversion depuis réponse Nexten"""
        matches = []
        results = response.get("matches", [])
        
        for result in results:
            matches.append(MatchResult(
                offer_id=str(result.get("job_id", result.get("id", "unknown"))),
                overall_score=result.get("compatibility_score", result.get("score", 0.0)),
                confidence=result.get("confidence", result.get("compatibility_score", 0.0)),
                skill_match_score=result.get("skills_match", 0.0),
                experience_match_score=result.get("experience_match", 0.0),
                location_match_score=result.get("location_match", 0.0),
                culture_match_score=result.get("culture_match", 0.0),
                insights=result.get("insights", []),
                explanation=result.get("explanation", "Match via Nexten ML Algorithm")
            ))
        
        return matches
    
    @staticmethod
    def from_v1_response(response: Dict[str, Any]) -> List[MatchResult]:
        """Conversion depuis réponse SuperSmartMatch V1"""
        matches = []
        results = response.get("matches", [])
        
        for result in results:
            matches.append(MatchResult(
                offer_id=str(result.get("offer_id", result.get("job_id", "unknown"))),
                overall_score=result.get("score", result.get("overall_score", 0.0)),
                confidence=result.get("confidence", result.get("score", 0.0)),
                skill_match_score=result.get("skill_match", result.get("details", {}).get("skill_match", 0.0)),
                experience_match_score=result.get("experience_match", result.get("details", {}).get("experience_match", 0.0)),
                location_match_score=result.get("location_match", result.get("details", {}).get("location_match", 0.0)),
                insights=result.get("insights", []),
                explanation=result.get("explanation", "Match via SuperSmartMatch V1")
            ))
        
        return matches

class SuperSmartMatchV2UnifiedService:
    """Service unifié SuperSmartMatch V2 - Port 5070"""
    
    def __init__(self, config: ServiceConfig = ServiceConfig()):
        self.config = config
        self.algorithm_selector = IntelligentAlgorithmSelector()
        self.circuit_breakers = {
            "nexten": CircuitBreaker(config.circuit_breaker_threshold, config.circuit_breaker_timeout),
            "v1": CircuitBreaker(config.circuit_breaker_threshold, config.circuit_breaker_timeout)
        }
        
        # Initialisation Redis pour cache
        self.redis_client: Optional[redis.Redis] = None
        
        # Statistiques globales
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time_ms": 0.0,
            "uptime_start": datetime.now()
        }
        
        logger.info("SuperSmartMatch V2 Unified Service initialized")
    
    async def initialize(self):
        """Initialisation asynchrone du service"""
        try:
            # Connexion Redis
            self.redis_client = redis.from_url(self.config.redis_url)
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e} - Cache disabled")
            self.redis_client = None
    
    async def match(self, request: MatchRequest) -> MatchResponse:
        """Point d'entrée principal pour le matching unifié"""
        start_time = time.time()
        
        try:
            self.stats["total_requests"] += 1
            
            # Vérification du cache
            cache_key = self._generate_cache_key(request)
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                logger.info("Cache hit - returning cached result")
                return cached_result
            
            # Sélection d'algorithme intelligent
            algorithm, selection_reason = self.algorithm_selector.select_algorithm(request)
            logger.info(f"Selected algorithm: {algorithm.value} - {selection_reason}")
            
            # Exécution avec fallback hiérarchique
            matches, algorithm_used = await self._execute_with_fallback(algorithm, request)
            
            # Construction de la réponse
            execution_time_ms = (time.time() - start_time) * 1000
            response = MatchResponse(
                success=True,
                matches=matches,
                algorithm_used=algorithm_used,
                execution_time_ms=execution_time_ms,
                selection_reason=selection_reason,
                metadata={
                    "context_analysis": self.algorithm_selector._analyze_context(request),
                    "cache_hit": False,
                    "fallback_used": algorithm_used != algorithm.value,
                    "circuit_breaker_states": {
                        name: cb.state for name, cb in self.circuit_breakers.items()
                    }
                }
            )
            
            # Mise à jour des métriques
            self.algorithm_selector.update_metrics(algorithm_used, True, execution_time_ms)
            self.stats["successful_requests"] += 1
            self._update_avg_response_time(execution_time_ms)
            
            # Cache du résultat
            await self._save_to_cache(cache_key, response)
            
            return response
            
        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Matching failed after {execution_time_ms:.2f}ms: {e}")
            
            self.stats["failed_requests"] += 1
            
            # Réponse d'erreur avec fallback basique
            return MatchResponse(
                success=False,
                matches=[],
                algorithm_used="error_fallback",
                execution_time_ms=execution_time_ms,
                selection_reason=f"Error occurred: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _execute_with_fallback(self, primary_algorithm: AlgorithmType, request: MatchRequest) -> Tuple[List[MatchResult], str]:
        """Exécution avec système de fallback hiérarchique"""
        
        # Définition de la hiérarchie de fallback
        fallback_hierarchy = [
            primary_algorithm,
            AlgorithmType.NEXTEN,
            AlgorithmType.ENHANCED,
            AlgorithmType.SMART_MATCH,
            AlgorithmType.SEMANTIC,
            AlgorithmType.BASIC
        ]
        
        # Supprimer les doublons tout en préservant l'ordre
        seen = set()
        unique_hierarchy = []
        for algo in fallback_hierarchy:
            if algo not in seen:
                unique_hierarchy.append(algo)
                seen.add(algo)
        
        last_error = None
        
        for algorithm in unique_hierarchy:
            try:
                matches = await self._execute_algorithm(algorithm, request)
                return matches, algorithm.value
            except Exception as e:
                last_error = e
                logger.warning(f"Algorithm {algorithm.value} failed: {e}")
                continue
        
        # Si tous les algorithmes échouent, retourner une réponse basique
        logger.error(f"All algorithms failed, last error: {last_error}")
        return [], "all_failed"
    
    async def _execute_algorithm(self, algorithm: AlgorithmType, request: MatchRequest) -> List[MatchResult]:
        """Exécution d'un algorithme spécifique avec circuit breaker"""
        
        if algorithm == AlgorithmType.NEXTEN:
            return await self._call_nexten_matcher(request)
        elif algorithm in [AlgorithmType.SMART_MATCH, AlgorithmType.ENHANCED, AlgorithmType.SEMANTIC]:
            return await self._call_supersmartmatch_v1(request, algorithm.value)
        elif algorithm == AlgorithmType.BASIC:
            return await self._call_basic_fallback(request)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    
    async def _call_nexten_matcher(self, request: MatchRequest) -> List[MatchResult]:
        """Appel au service Nexten Matcher avec circuit breaker"""
        
        async def nexten_call():
            data = DataAdapter.to_nexten_format(request)
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.nexten_url}/api/v1/match",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=5.0)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"Nexten service error: {response.status}")
                    
                    result = await response.json()
                    return DataAdapter.from_nexten_response(result)
        
        return await self.circuit_breakers["nexten"].call(nexten_call)
    
    async def _call_supersmartmatch_v1(self, request: MatchRequest, algorithm: str) -> List[MatchResult]:
        """Appel au service SuperSmartMatch V1 avec circuit breaker"""
        
        async def v1_call():
            data = DataAdapter.to_v1_format(request)
            data["algorithm"] = algorithm
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.supersmartmatch_v1_url}/api/v1/match",
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=3.0)
                ) as response:
                    if response.status != 200:
                        raise Exception(f"SuperSmartMatch V1 service error: {response.status}")
                    
                    result = await response.json()
                    return DataAdapter.from_v1_response(result)
        
        return await self.circuit_breakers["v1"].call(v1_call)
    
    async def _call_basic_fallback(self, request: MatchRequest) -> List[MatchResult]:
        """Algorithme de fallback basique en cas d'échec de tous les services"""
        
        matches = []
        candidate = request.candidate
        offers = request.offers
        
        # Matching basique par mots-clés
        candidate_skills = set()
        skills_sources = [
            candidate.get("technical_skills", []),
            candidate.get("competences", []),
            candidate.get("skills", [])
        ]
        
        for skills_list in skills_sources:
            if isinstance(skills_list, list):
                candidate_skills.update(str(skill).lower() for skill in skills_list)
        
        for i, offer in enumerate(offers):
            offer_skills = set()
            offer_skills_sources = [
                offer.get("required_skills", []),
                offer.get("competences", []),
                offer.get("skills", [])
            ]
            
            for skills_list in offer_skills_sources:
                if isinstance(skills_list, list):
                    offer_skills.update(str(skill).lower() for skill in skills_list)
            
            # Calcul de score basique
            if candidate_skills and offer_skills:
                intersection = candidate_skills & offer_skills
                union = candidate_skills | offer_skills
                score = len(intersection) / len(union) if union else 0.0
            else:
                score = 0.1  # Score minimal par défaut
            
            matches.append(MatchResult(
                offer_id=str(offer.get("id", i)),
                overall_score=score,
                confidence=score * 0.8,  # Confiance réduite pour fallback
                skill_match_score=score,
                explanation="Match basique par mots-clés (service de secours)"
            ))
        
        # Tri par score décroissant
        matches.sort(key=lambda x: x.overall_score, reverse=True)
        
        return matches[:10]  # Limiter à 10 résultats
    
    def _generate_cache_key(self, request: MatchRequest) -> str:
        """Génération de clé de cache basée sur le contenu de la requête"""
        # Créer un hash stable du contenu de la requête
        content = {
            "candidate": request.candidate,
            "offers": request.offers,
            "algorithm": request.algorithm,
            "questionnaire": request.candidate_questionnaire,
            "company_questionnaires": request.company_questionnaires
        }
        
        import hashlib
        content_str = json.dumps(content, sort_keys=True)
        hash_key = hashlib.md5(content_str.encode()).hexdigest()
        
        return f"supersmartmatch_v2:{hash_key}"
    
    async def _get_from_cache(self, cache_key: str) -> Optional[MatchResponse]:
        """Récupération depuis le cache Redis"""
        if not self.redis_client:
            return None
        
        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return MatchResponse(**data)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        
        return None
    
    async def _save_to_cache(self, cache_key: str, response: MatchResponse):
        """Sauvegarde dans le cache Redis"""
        if not self.redis_client:
            return
        
        try:
            # Conversion en dict pour sérialisation JSON
            data = response.dict()
            await self.redis_client.setex(
                cache_key, 
                self.config.cache_ttl,
                json.dumps(data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache save error: {e}")
    
    def _update_avg_response_time(self, response_time_ms: float):
        """Mise à jour du temps de réponse moyen"""
        if self.stats["avg_response_time_ms"] == 0:
            self.stats["avg_response_time_ms"] = response_time_ms
        else:
            # Moyenne mobile
            self.stats["avg_response_time_ms"] = (
                self.stats["avg_response_time_ms"] * 0.9 + response_time_ms * 0.1
            )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Status de santé du service unifié"""
        uptime = datetime.now() - self.stats["uptime_start"]
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "uptime_seconds": int(uptime.total_seconds()),
            "stats": self.stats,
            "algorithm_metrics": {
                name: asdict(metrics) 
                for name, metrics in self.algorithm_selector.metrics.items()
            },
            "circuit_breakers": {
                name: {
                    "state": cb.state,
                    "failure_count": cb.failure_count,
                    "last_failure": cb.last_failure.isoformat() if cb.last_failure else None
                }
                for name, cb in self.circuit_breakers.items()
            },
            "external_services": {
                "nexten_matcher": self.config.nexten_url,
                "supersmartmatch_v1": self.config.supersmartmatch_v1_url,
                "redis_cache": "connected" if self.redis_client else "disconnected"
            }
        }

# FastAPI Application
app = FastAPI(
    title="SuperSmartMatch V2 - Unified Service",
    description="🚀 Service intelligent unifié sur port 5070 - Intègre Nexten Matcher et SuperSmartMatch V1",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Instance globale du service
service: Optional[SuperSmartMatchV2UnifiedService] = None

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application"""
    global service
    service = SuperSmartMatchV2UnifiedService()
    await service.initialize()
    logger.info("🚀 SuperSmartMatch V2 Unified Service started on port 5070")

@app.get("/")
async def root():
    """Information sur le service unifié"""
    return {
        "service": "SuperSmartMatch V2 - Unified Service",
        "version": "2.0.0",
        "port": 5070,
        "description": "Service intelligent qui unifie Nexten Matcher et SuperSmartMatch V1",
        "features": {
            "intelligent_algorithm_selection": True,
            "nexten_matcher_integration": True,
            "supersmartmatch_v1_integration": True,
            "circuit_breakers": True,
            "hierarchical_fallback": True,
            "redis_caching": True,
            "real_time_monitoring": True
        },
        "endpoints": {
            "matching": "/api/v2/match",
            "legacy_compatibility": "/match",
            "health": "/health",
            "metrics": "/metrics",
            "documentation": "/api/docs"
        },
        "integrated_services": {
            "nexten_matcher": "http://localhost:5052",
            "supersmartmatch_v1": "http://localhost:5062"
        }
    }

@app.get("/health")
async def health_check():
    """Vérification de santé simple"""
    if service:
        return await service.get_health_status()
    else:
        return {"status": "initializing"}

@app.get("/metrics")
async def get_metrics():
    """Métriques détaillées du service"""
    if service:
        health = await service.get_health_status()
        return {
            "service_metrics": health["stats"],
            "algorithm_performance": health["algorithm_metrics"],
            "circuit_breaker_status": health["circuit_breakers"],
            "external_services_status": health["external_services"]
        }
    else:
        return {"status": "service not initialized"}

@app.post("/api/v2/match", response_model=MatchResponse)
async def match_v2(request: MatchRequest):
    """API V2 de matching avec sélection intelligente d'algorithme"""
    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = await service.match(request)
        return result
    except Exception as e:
        logger.error(f"Matching error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/match")
async def match_legacy(request_data: Dict[str, Any]):
    """API de compatibilité V1 - maintient l'interface existante"""
    if not service:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Conversion du format legacy vers V2
        match_request = MatchRequest(
            candidate=request_data.get("cv_data", request_data.get("candidate", {})),
            offers=request_data.get("job_data", request_data.get("offers", [])),
            algorithm=request_data.get("algorithm", "auto"),
            config=request_data.get("config")
        )
        
        result = await service.match(match_request)
        
        # Conversion vers format de réponse V1
        return {
            "matches": [
                {
                    "offer_id": match.offer_id,
                    "score": match.overall_score,
                    "confidence": match.confidence,
                    "details": {
                        "skill_match": match.skill_match_score,
                        "experience_match": match.experience_match_score,
                        "location_match": match.location_match_score
                    },
                    "insights": match.insights,
                    "explanation": match.explanation
                }
                for match in result.matches
            ],
            "algorithm_used": result.algorithm_used,
            "execution_time_ms": result.execution_time_ms,
            "version": "v2_unified_service"
        }
        
    except Exception as e:
        logger.error(f"Legacy matching error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/algorithms")
async def get_available_algorithms():
    """Liste des algorithmes disponibles et leur statut"""
    if service:
        health = await service.get_health_status()
        return {
            "available_algorithms": [algo.value for algo in AlgorithmType],
            "algorithm_metrics": health["algorithm_metrics"],
            "selection_rules": {
                "nexten": "Questionnaires complets (prioritaire)",
                "smart": "Contraintes géographiques + mobilité", 
                "enhanced": "Profils séniors (7+ ans d'expérience)",
                "semantic": "Compétences complexes NLP",
                "basic": "Fallback de secours",
                "auto": "Sélection intelligente automatique"
            }
        }
    else:
        return {"status": "service not initialized"}

if __name__ == "__main__":
    # Configuration et démarrage du service
    logger.info("🚀 Starting SuperSmartMatch V2 Unified Service on port 5070...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5070,
        log_level="info",
        access_log=True
    )
