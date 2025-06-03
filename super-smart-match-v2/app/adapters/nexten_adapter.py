"""
Adaptateur Nexten Matcher - Intégration du service ML avancé (port 5052)

Gère la communication avec le service Nexten Matcher (40K lignes ML)
Inclut :
- Transformation de format de données
- Circuit breaker
- Cache intelligent
- Gestion des timeouts
"""

import httpx
import asyncio
from typing import Dict, Any, Optional, List
from circuitbreaker import CircuitBreaker
import time
import json

from ..models import MatchRequestV1, MatchRequestV2, MatchResult, Candidate, JobOffer
from ..config import get_config
from ..logger import get_logger
from .cache_adapter import CacheAdapter

config = get_config()
logger = get_logger(__name__)

class NextenAdapter:
    """Adaptateur pour le service Nexten Matcher"""
    
    def __init__(self, cache_adapter: Optional[CacheAdapter] = None):
        self.base_url = config.nexten_matcher_url
        self.timeout = config.nexten_timeout_ms / 1000  # Convertir en secondes
        self.cache_adapter = cache_adapter
        
        # Configuration du circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_breaker_failure_threshold,
            recovery_timeout=config.circuit_breaker_recovery_timeout,
            expected_exception=Exception
        )
        
        # Client HTTP configuré
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=100)
        )
        
        logger.info("Nexten adapter initialized", base_url=self.base_url, timeout=self.timeout)
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifier la santé du service Nexten"""
        try:
            start_time = time.time()
            response = await self.client.get(f"{self.base_url}/health", timeout=5.0)
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
            logger.error(f"Nexten health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_check": int(time.time())
            }
    
    def _generate_cache_key(self, candidate: Candidate, offers: List[JobOffer]) -> str:
        """Générer une clé de cache pour la requête"""
        # Créer un hash basé sur les données importantes
        candidate_hash = hash((
            candidate.name,
            tuple(candidate.technical_skills) if candidate.technical_skills else (),
            tuple(exp.title for exp in candidate.experiences) if candidate.experiences else ()
        ))
        
        offers_hash = hash(tuple(
            (offer.id, offer.title, tuple(offer.required_skills))
            for offer in offers
        ))
        
        return f"nexten_match:{candidate_hash}:{offers_hash}"
    
    def _transform_request_for_nexten(self, request: MatchRequestV1) -> Dict[str, Any]:
        """Transformer la requête V1/V2 au format attendu par Nexten"""
        
        # Transformer le candidat
        candidate_data = {
            "id": request.candidate.id or f"candidate_{int(time.time())}",
            "name": request.candidate.name,
            "email": request.candidate.email,
            "skills": []
        }
        
        # Normaliser les compétences
        for skill in request.candidate.technical_skills:
            if isinstance(skill, str):
                candidate_data["skills"].append({"name": skill, "level": "intermediate"})
            else:
                candidate_data["skills"].append({
                    "name": skill.name,
                    "level": skill.level or "intermediate",
                    "years": skill.years or 1
                })
        
        # Ajouter l'expérience
        if request.candidate.experiences:
            candidate_data["experience"] = [
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
        
        # Transformer les offres (format "jobs" pour Nexten)
        jobs_data = []
        for offer in request.offers:
            job_data = {
                "id": offer.id,
                "title": offer.title,
                "company": offer.company,
                "description": offer.description or f"{offer.title} at {offer.company}",
                "required_skills": offer.required_skills,
                "preferred_skills": offer.preferred_skills or [],
                "experience_level": offer.experience_level or "intermediate"
            }
            
            if offer.location:
                job_data["location"] = {
                    "city": offer.location.city,
                    "country": offer.location.country
                }
            
            if offer.salary_range:
                job_data["salary_range"] = offer.salary_range
            
            jobs_data.append(job_data)
        
        return {
            "candidate": candidate_data,
            "jobs": jobs_data,  # Nexten utilise "jobs" pas "offers"
            "algorithm": "nexten_advanced",
            "limit": getattr(request, 'limit', 10)
        }
    
    def _transform_response_from_nexten(self, nexten_response: Dict[str, Any]) -> List[MatchResult]:
        """Transformer la réponse Nexten au format V2"""
        matches = []
        
        # Nexten retourne les matches dans "matches" ou "results"
        nexten_matches = nexten_response.get("matches", nexten_response.get("results", []))
        
        for match in nexten_matches:
            # Adapter selon le format de réponse Nexten
            match_result = MatchResult(
                offer_id=match.get("job_id", match.get("offer_id", "unknown")),
                overall_score=float(match.get("score", match.get("overall_score", 0.0))),
                confidence=float(match.get("confidence", 0.8)),
                skill_match_score=float(match.get("skill_match", match.get("skills_score", 0.0))),
                experience_match_score=float(match.get("experience_match", match.get("experience_score", 0.0))),
                location_match_score=float(match.get("location_match", match.get("location_score", 1.0))),
                culture_match_score=float(match.get("culture_match", match.get("culture_score", 0.8))),
                
                # Enrichissements V2
                insights=match.get("insights", ["Matching via Nexten ML avancé"]),
                explanation=match.get("explanation", "Algorithme ML avec 40K lignes de code avancé"),
                strengths=match.get("strengths", []),
                weaknesses=match.get("weaknesses", []),
                recommendations=match.get("recommendations", [])
            )
            
            matches.append(match_result)
        
        return matches
    
    @CircuitBreaker(failure_threshold=5, recovery_timeout=60)
    async def execute_matching(self, request: MatchRequestV1) -> List[MatchResult]:
        """Exécuter le matching via Nexten avec circuit breaker"""
        start_time = time.time()
        
        try:
            # Vérifier le cache si activé
            cache_key = None
            if self.cache_adapter and config.enable_caching:
                cache_key = self._generate_cache_key(request.candidate, request.offers)
                cached_result = await self.cache_adapter.get(cache_key)
                if cached_result:
                    logger.info("Nexten cache hit", cache_key=cache_key)
                    return [MatchResult(**result) for result in cached_result]
            
            # Transformer la requête
            nexten_request = self._transform_request_for_nexten(request)
            
            logger.info(
                "Nexten matching request", 
                candidate_id=nexten_request["candidate"].get("id"),
                jobs_count=len(nexten_request["jobs"])
            )
            
            # Appel API vers Nexten
            response = await self.client.post(
                f"{self.base_url}/match",
                json=nexten_request,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "SuperSmartMatch-V2/2.0.0"
                }
            )
            
            execution_time = (time.time() - start_time) * 1000
            
            if response.status_code != 200:
                logger.error(
                    "Nexten API error",
                    status_code=response.status_code,
                    response=response.text[:500]
                )
                raise Exception(f"Nexten API returned {response.status_code}: {response.text[:200]}")
            
            # Parser la réponse
            nexten_response = response.json()
            matches = self._transform_response_from_nexten(nexten_response)
            
            logger.info(
                "Nexten matching completed",
                execution_time_ms=execution_time,
                matches_count=len(matches),
                cache_key=cache_key is not None
            )
            
            # Mettre en cache si activé
            if self.cache_adapter and config.enable_caching and cache_key:
                cache_data = [match.dict() for match in matches]
                await self.cache_adapter.set(cache_key, cache_data, ttl=config.cache_ttl)
                logger.debug("Nexten result cached", cache_key=cache_key)
            
            return matches
            
        except httpx.TimeoutException:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Nexten timeout after {execution_time}ms")
            raise Exception(f"Nexten service timeout ({self.timeout}s)")
        
        except httpx.ConnectError:
            logger.error("Nexten connection error", base_url=self.base_url)
            raise Exception("Unable to connect to Nexten service")
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.error(f"Nexten execution error: {e}", execution_time_ms=execution_time, exc_info=True)
            raise
    
    async def execute_matching_v2(self, request: MatchRequestV2) -> List[MatchResult]:
        """Exécuter le matching V2 avec données enrichies"""
        # Convertir V2 vers V1 pour compatibilité
        v1_request = MatchRequestV1(
            candidate=request.candidate,
            offers=request.offers,
            algorithm=request.algorithm,
            limit=request.limit
        )
        
        # Si on a des questionnaires, enrichir la requête
        if request.candidate_questionnaire or request.company_questionnaires:
            # TODO: Adapter le format Nexten pour supporter les questionnaires
            logger.info("V2 questionnaire data available for Nexten", 
                       has_candidate_q=request.candidate_questionnaire is not None,
                       company_q_count=len(request.company_questionnaires or []))
        
        return await self.execute_matching(v1_request)
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Obtenir le statut du circuit breaker"""
        return {
            "state": str(self.circuit_breaker.current_state),
            "failure_count": self.circuit_breaker.fail_counter,
            "last_failure": getattr(self.circuit_breaker, 'last_failure_time', None),
            "next_attempt": getattr(self.circuit_breaker, 'next_attempt_time', None)
        }
    
    async def reset_circuit_breaker(self) -> bool:
        """Réinitialiser le circuit breaker"""
        try:
            self.circuit_breaker.close()
            logger.info("Nexten circuit breaker reset")
            return True
        except Exception as e:
            logger.error(f"Failed to reset Nexten circuit breaker: {e}")
            return False
    
    async def __aenter__(self):
        """Support du context manager"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage à la sortie"""
        await self.client.aclose()