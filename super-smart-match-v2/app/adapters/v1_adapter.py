"""
Adaptateur SuperSmartMatch V1 - Intégration du service existant (port 5062)

Gère la communication avec SuperSmartMatch V1 (4 algorithmes)
Inclut :
- Routage vers algorithmes spécifiques
- Format de données compatible
- Circuit breaker et fallbacks
- Cache des résultats
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List
from circuitbreaker import CircuitBreaker
import time

from ..models import MatchRequestV1, MatchRequestV2, MatchResult, AlgorithmType
from ..config import get_config
from ..logger import get_logger
from .cache_adapter import CacheAdapter

config = get_config()
logger = get_logger(__name__)

class V1Adapter:
    """Adaptateur pour SuperSmartMatch V1"""
    
    def __init__(self, cache_adapter: Optional[CacheAdapter] = None):
        self.base_url = config.supersmartmatch_v1_url
        self.timeout = config.v1_timeout_ms / 1000
        self.cache_adapter = cache_adapter
        
        # Circuit breaker configuré
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_breaker_failure_threshold,
            recovery_timeout=config.circuit_breaker_recovery_timeout,
            expected_exception=Exception
        )
        
        # Client HTTP
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=50)
        )
        
        # Mapping des algorithmes V1
        self.algorithm_endpoints = {
            AlgorithmType.ENHANCED: "/api/v1/match/enhanced",
            AlgorithmType.SMART: "/api/v1/match/smart", 
            AlgorithmType.SEMANTIC: "/api/v1/match/semantic",
            AlgorithmType.BASIC: "/api/v1/match/basic"
        }
        
        logger.info("V1 adapter initialized", base_url=self.base_url, timeout=self.timeout)
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifier la santé du service V1"""
        try:
            start_time = time.time()
            response = await self.client.get(f"{self.base_url}/api/v1/health", timeout=5.0)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time_ms": response_time,
                    "last_check": int(time.time())
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time_ms": response_time,
                    "status_code": response.status_code,
                    "last_check": int(time.time())
                }
                
        except Exception as e:
            logger.error(f"V1 health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_check": int(time.time())
            }
    
    def _generate_cache_key(self, algorithm: AlgorithmType, request: MatchRequestV1) -> str:
        """Générer une clé de cache pour l'algorithme V1"""
        candidate_hash = hash((
            request.candidate.name,
            tuple(str(skill) for skill in request.candidate.technical_skills),
            tuple(exp.title for exp in request.candidate.experiences) if request.candidate.experiences else ()
        ))
        
        offers_hash = hash(tuple(
            (offer.id, offer.title, tuple(offer.required_skills))
            for offer in request.offers
        ))
        
        return f"v1_{algorithm.value}:{candidate_hash}:{offers_hash}"
    
    def _transform_request_for_v1(self, request: MatchRequestV1) -> Dict[str, Any]:
        """Transformer la requête au format V1"""
        
        # Le service V1 attend le format existant
        candidate_data = {
            "name": request.candidate.name,
            "email": request.candidate.email,
            "technical_skills": []
        }
        
        # Normaliser les compétences pour V1
        for skill in request.candidate.technical_skills:
            if isinstance(skill, str):
                candidate_data["technical_skills"].append(skill)
            else:
                candidate_data["technical_skills"].append(skill.name)
        
        # Ajouter les soft skills
        if request.candidate.soft_skills:
            candidate_data["soft_skills"] = request.candidate.soft_skills
        
        # Ajouter l'expérience
        if request.candidate.experiences:
            candidate_data["experiences"] = [
                {
                    "title": exp.title,
                    "company": exp.company,
                    "duration_months": exp.duration_months or 12,
                    "skills": exp.skills
                }
                for exp in request.candidate.experiences
            ]
        
        # Ajouter la localisation
        if request.candidate.location:
            candidate_data["location"] = {
                "city": request.candidate.location.city,
                "country": request.candidate.location.country
            }
        
        # Transformer les offres (V1 utilise "offers")
        offers_data = []
        for offer in request.offers:
            offer_data = {
                "id": offer.id,
                "title": offer.title,
                "company": offer.company,
                "required_skills": offer.required_skills,
                "preferred_skills": offer.preferred_skills or []
            }
            
            if offer.description:
                offer_data["description"] = offer.description
            
            if offer.location:
                offer_data["location"] = {
                    "city": offer.location.city,
                    "country": offer.location.country
                }
            
            if offer.salary_range:
                offer_data["salary_range"] = offer.salary_range
                
            if offer.experience_level:
                offer_data["experience_level"] = offer.experience_level
            
            offers_data.append(offer_data)
        
        return {
            "candidate": candidate_data,
            "offers": offers_data,  # V1 utilise "offers"
            "limit": getattr(request, 'limit', 10)
        }
    
    def _transform_response_from_v1(self, v1_response: Dict[str, Any], algorithm: AlgorithmType) -> List[MatchResult]:
        """Transformer la réponse V1 au format V2"""
        matches = []
        
        # V1 retourne les matches dans "matches"
        v1_matches = v1_response.get("matches", [])
        
        for match in v1_matches:
            # Le format V1 peut varier selon l'algorithme
            match_result = MatchResult(
                offer_id=match.get("offer_id", match.get("job_id", "unknown")),
                overall_score=float(match.get("score", match.get("overall_score", 0.0))),
                confidence=float(match.get("confidence", 0.7)),
                
                # Scores détaillés (si disponibles dans V1)
                skill_match_score=float(match.get("details", {}).get("skill_match", 
                                                  match.get("skill_score", 0.0))),
                experience_match_score=float(match.get("details", {}).get("experience_match", 
                                                       match.get("experience_score", 0.0))),
                location_match_score=float(match.get("details", {}).get("location_match", 1.0)),
                
                # Enrichissements pour compatibilité V2
                insights=self._generate_v1_insights(algorithm, match),
                explanation=self._generate_v1_explanation(algorithm, match),
                
                # Conserver les détails V1 pour compatibilité
                details=match.get("details", {})
            )
            
            matches.append(match_result)
        
        return matches
    
    def _generate_v1_insights(self, algorithm: AlgorithmType, match: Dict[str, Any]) -> List[str]:
        """Générer des insights basés sur l'algorithme V1 utilisé"""
        insights = []
        score = match.get("score", 0.0)
        
        if algorithm == AlgorithmType.ENHANCED:
            insights.append("Algorithme Enhanced : pondération avancée de l'expérience")
            if score > 0.8:
                insights.append("Excellent match basé sur l'expérience professionnelle")
        
        elif algorithm == AlgorithmType.SMART:
            insights.append("Algorithme Smart : optimisation géographique intelligente")
            if score > 0.8:
                insights.append("Très bon match avec optimisation de la localisation")
        
        elif algorithm == AlgorithmType.SEMANTIC:
            insights.append("Algorithme Semantic : analyse NLP des compétences")
            if score > 0.8:
                insights.append("Forte correspondance sémantique des compétences")
        
        elif algorithm == AlgorithmType.BASIC:
            insights.append("Algorithme Basic : matching rapide et fiable")
            if score > 0.7:
                insights.append("Bonne correspondance sur les critères de base")
        
        return insights
    
    def _generate_v1_explanation(self, algorithm: AlgorithmType, match: Dict[str, Any]) -> str:
        """Générer une explication basée sur l'algorithme V1"""
        score = match.get("score", 0.0)
        
        explanations = {
            AlgorithmType.ENHANCED: f"Match calculé via Enhanced algorithm (score: {score:.2f}) avec pondération expérience",
            AlgorithmType.SMART: f"Match calculé via Smart algorithm (score: {score:.2f}) avec optimisation géo", 
            AlgorithmType.SEMANTIC: f"Match calculé via Semantic algorithm (score: {score:.2f}) avec analyse NLP",
            AlgorithmType.BASIC: f"Match calculé via Basic algorithm (score: {score:.2f}) - critères standards"
        }
        
        return explanations.get(algorithm, f"Match calculé via {algorithm.value} (score: {score:.2f})")
    
    @CircuitBreaker(failure_threshold=5, recovery_timeout=60)
    async def execute_algorithm(self, algorithm: AlgorithmType, request: MatchRequestV1) -> List[MatchResult]:
        """Exécuter un algorithme V1 spécifique"""
        start_time = time.time()
        
        try:
            # Vérifier le cache
            cache_key = None
            if self.cache_adapter and config.enable_caching:
                cache_key = self._generate_cache_key(algorithm, request)
                cached_result = await self.cache_adapter.get(cache_key)
                if cached_result:
                    logger.info("V1 cache hit", algorithm=algorithm.value, cache_key=cache_key)
                    return [MatchResult(**result) for result in cached_result]
            
            # Transformer la requête
            v1_request = self._transform_request_for_v1(request)
            
            # Déterminer l'endpoint
            endpoint = self.algorithm_endpoints.get(algorithm, "/match")
            if algorithm == AlgorithmType.AUTO:
                # Pour auto, utiliser l'endpoint principal
                endpoint = "/match"
            
            logger.info(
                "V1 algorithm request",
                algorithm=algorithm.value,
                endpoint=endpoint,
                offers_count=len(v1_request["offers"])
            )
            
            # Appel API
            response = await self.client.post(
                f"{self.base_url}{endpoint}",
                json=v1_request,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "SuperSmartMatch-V2/2.0.0"
                }
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            if response.status_code != 200:
                logger.error(
                    "V1 API error",
                    algorithm=algorithm.value,
                    status_code=response.status_code,
                    response=response.text[:500]
                )
                raise Exception(f"V1 {algorithm.value} returned {response.status_code}: {response.text[:200]}")
            
            # Parser la réponse
            v1_response = response.json()
            matches = self._transform_response_from_v1(v1_response, algorithm)
            
            logger.info(
                "V1 algorithm completed",
                algorithm=algorithm.value,
                execution_time_ms=execution_time,
                matches_count=len(matches)
            )
            
            # Mettre en cache
            if self.cache_adapter and config.enable_caching and cache_key:
                cache_data = [match.dict() for match in matches]
                await self.cache_adapter.set(cache_key, cache_data, ttl=config.cache_ttl)
                logger.debug("V1 result cached", algorithm=algorithm.value, cache_key=cache_key)
            
            return matches
            
        except httpx.TimeoutException:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"V1 {algorithm.value} timeout after {execution_time}ms")
            raise Exception(f"V1 {algorithm.value} timeout ({self.timeout}s)")
        
        except httpx.ConnectError:
            logger.error("V1 connection error", algorithm=algorithm.value, base_url=self.base_url)
            raise Exception(f"Unable to connect to V1 service for {algorithm.value}")
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(
                f"V1 {algorithm.value} error: {e}", 
                execution_time_ms=execution_time, 
                exc_info=True
            )
            raise
    
    async def get_available_algorithms(self) -> List[str]:
        """Obtenir la liste des algorithmes disponibles"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/algorithms", timeout=5.0)
            if response.status_code == 200:
                data = response.json()
                return list(data.get("algorithms", {}).keys())
            else:
                # Fallback sur les algorithmes connus
                return ["enhanced", "smart", "semantic", "basic"]
        except Exception as e:
            logger.error(f"Failed to get V1 algorithms: {e}")
            return ["enhanced", "smart", "semantic", "basic"]
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Statut du circuit breaker V1"""
        return {
            "state": str(self.circuit_breaker.current_state),
            "failure_count": self.circuit_breaker.fail_counter,
            "last_failure": getattr(self.circuit_breaker, 'last_failure_time', None),
            "next_attempt": getattr(self.circuit_breaker, 'next_attempt_time', None)
        }
    
    async def reset_circuit_breaker(self) -> bool:
        """Réinitialiser le circuit breaker V1"""
        try:
            self.circuit_breaker.close()
            logger.info("V1 circuit breaker reset")
            return True
        except Exception as e:
            logger.error(f"Failed to reset V1 circuit breaker: {e}")
            return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()