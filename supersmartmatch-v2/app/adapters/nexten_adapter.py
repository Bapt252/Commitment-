"""
Adaptateur pour Nexten Matcher (port 5052)

Adapte les requêtes SuperSmartMatch V2 vers le format Nexten Matcher
et traduit les réponses vers le format unifié.

Nexten Matcher : Service ML avancé avec 40K lignes de code
"""

import logging
import aiohttp
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..models.matching_models import (
    CVData, JobData, MatchingOptions, MatchingResponse, MatchResult
)
from ..config import get_settings, AlgorithmConfig

logger = logging.getLogger(__name__)
settings = get_settings()
algorithm_config = AlgorithmConfig()


class NextenMatcherAdapter:
    """
    Adaptateur pour Nexten Matcher
    
    Traduit les requêtes V2 vers le format Nexten et adapte les réponses
    vers le format unifié SuperSmartMatch V2.
    """
    
    def __init__(self):
        self.base_url = settings.nexten_matcher_url
        self.endpoint = algorithm_config.NEXTEN_ENDPOINT
        self.timeout = algorithm_config.NEXTEN_TIMEOUT
        self.retry_attempts = algorithm_config.NEXTEN_RETRY_ATTEMPTS
        
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Métriques
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time": 0.0
        }
        
        logger.info(f"🤖 NextenMatcherAdapter initialisé - URL: {self.base_url}")
    
    async def initialize(self, session: aiohttp.ClientSession):
        """Initialise l'adaptateur avec une session HTTP"""
        self.session = session
        logger.info("✅ NextenMatcherAdapter prêt")
    
    async def execute_matching(
        self,
        cv_data: CVData,
        jobs: List[JobData],
        options: Optional[MatchingOptions] = None
    ) -> MatchingResponse:
        """
        Exécute le matching via Nexten Matcher
        
        Args:
            cv_data: Données CV
            jobs: Liste des jobs
            options: Options de matching
            
        Returns:
            MatchingResponse formatée
        """
        start_time = datetime.now()
        self.stats["total_requests"] += 1
        
        try:
            logger.debug(f"Appel Nexten Matcher: {len(jobs)} jobs")
            
            # Préparation de la requête
            request_payload = self._prepare_nexten_request(cv_data, jobs, options)
            
            # Appel avec retry
            response_data = await self._call_nexten_with_retry(request_payload)
            
            # Adaptation de la réponse
            result = self._adapt_nexten_response(response_data, jobs)
            
            # Métriques de succès
            response_time = (datetime.now() - start_time).total_seconds()
            self.stats["successful_requests"] += 1
            self.stats["total_response_time"] += response_time
            
            logger.info(
                f"✅ Nexten Matcher: {len(result.matches)} résultats "
                f"en {response_time*1000:.1f}ms"
            )
            
            return result
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"❌ Erreur Nexten Matcher: {e}", exc_info=True)
            raise
    
    def _prepare_nexten_request(
        self,
        cv_data: CVData,
        jobs: List[JobData],
        options: Optional[MatchingOptions]
    ) -> Dict[str, Any]:
        """
        Prépare la requête au format Nexten Matcher
        
        Le format Nexten attendu (basé sur l'architecture existante) :
        {
          "candidate": {...},
          "jobs": [...],
          "matching_options": {...}
        }
        """
        # Conversion CV vers format Nexten "candidate"
        candidate_data = {
            "id": f"temp-{hash(str(cv_data.dict()))}",
            "profile": {
                "skills": cv_data.competences,
                "experience_years": cv_data.experience or 0,
                "education_level": cv_data.niveau_etudes,
                "certifications": cv_data.certifications,
                "location": cv_data.localisation,
                "salary_expectation": cv_data.salaire_souhaite,
                "contract_type_preference": cv_data.type_contrat_souhaite,
                "mobility_km": cv_data.mobilite_km,
                "remote_work_accepted": cv_data.teletravail_accepte
            },
            "questionnaire": {
                "completed": cv_data.questionnaire_complete,
                "behavioral_profile": cv_data.profil_comportemental or {},
                "detailed_preferences": cv_data.preferences_detaillees or {},
                "completeness_score": cv_data.score_completude or 0
            },
            "metadata": {
                "last_updated": cv_data.derniere_mise_a_jour.isoformat() if cv_data.derniere_mise_a_jour else None,
                "age": cv_data.age
            }
        }
        
        # Conversion jobs vers format Nexten
        nexten_jobs = []
        for job in jobs:
            nexten_job = {
                "id": job.id,
                "title": job.titre,
                "company": job.entreprise,
                "location": job.localisation,
                "description": job.description,
                "requirements": {
                    "skills": job.competences,
                    "experience_years": job.experience_requise or 0,
                    "education_level": job.niveau_etudes_requis,
                    "certifications": job.certifications_requises
                },
                "conditions": {
                    "salary_min": job.salaire_min,
                    "salary_max": job.salaire_max,
                    "contract_type": job.type_contrat,
                    "remote_work_possible": job.teletravail_possible
                },
                "metadata": {
                    "sector": job.secteur,
                    "company_size": job.taille_entreprise,
                    "publication_date": job.date_publication.isoformat() if job.date_publication else None,
                    "urgency": job.urgence,
                    "attractiveness_score": job.score_attractivite,
                    "priority": job.priorite
                }
            }
            nexten_jobs.append(nexten_job)
        
        # Options de matching
        matching_options = {
            "max_results": options.max_results if options else 10,
            "min_score": options.min_score if options else 0.0,
            "include_travel_time": options.include_travel_time if options else False,
            "max_distance_km": options.max_distance_km if options else None,
            "user_id": options.user_id if options else None,
            "context": options.context if options and options.context else {}
        }
        
        return {
            "candidate": candidate_data,
            "jobs": nexten_jobs,
            "matching_options": matching_options,
            "algorithm": "nexten_ml_advanced",  # Algorithme spécifique Nexten
            "version": "2.0"
        }
    
    async def _call_nexten_with_retry(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appelle Nexten Matcher avec retry automatique
        """
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(f"Tentative {attempt + 1}/{self.retry_attempts} vers Nexten")
                
                async with self.session.post(
                    f"{self.base_url}{self.endpoint}",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.debug("Réponse Nexten reçue avec succès")
                        return data
                    
                    elif response.status == 429:  # Rate limiting
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limit Nexten, attente {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    else:
                        error_text = await response.text()
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"Erreur Nexten: {error_text}"
                        )
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                wait_time = 2 ** attempt
                logger.warning(f"Erreur tentative {attempt + 1}: {e}, retry dans {wait_time}s")
                
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(wait_time)
                continue
        
        # Toutes les tentatives ont échoué
        raise Exception(f"Nexten Matcher inaccessible après {self.retry_attempts} tentatives: {last_exception}")
    
    def _adapt_nexten_response(
        self,
        nexten_data: Dict[str, Any],
        original_jobs: List[JobData]
    ) -> MatchingResponse:
        """
        Adapte la réponse Nexten vers le format SuperSmartMatch V2
        
        Format Nexten attendu :
        {
          "matches": [...],
          "metadata": {...},
          "statistics": {...}
        }
        """
        try:
            # Extraction des matches
            nexten_matches = nexten_data.get("matches", [])
            
            # Conversion vers MatchResult
            matches = []
            for match in nexten_matches:
                match_result = MatchResult(
                    job_id=match.get("job_id"),
                    score_global=match.get("overall_score", 0.0),
                    score_competences=match.get("skills_score"),
                    score_experience=match.get("experience_score"),
                    score_localisation=match.get("location_score"),
                    score_salaire=match.get("salary_score"),
                    competences_matchees=match.get("matched_skills", []),
                    competences_manquantes=match.get("missing_skills", []),
                    distance_km=match.get("distance_km"),
                    temps_trajet_minutes=match.get("travel_time_minutes"),
                    moyen_transport=match.get("transport_mode"),
                    raisons_match=match.get("match_reasons", []),
                    recommandations=match.get("recommendations", []),
                    algorithme_utilise="nexten",
                    confiance=match.get("confidence_score")
                )
                matches.append(match_result)
            
            # Tri par score décroissant
            matches.sort(key=lambda x: x.score_global, reverse=True)
            
            # Métadonnées
            metadata = nexten_data.get("metadata", {})
            statistics = nexten_data.get("statistics", {})
            
            # Score moyen
            score_moyen = None
            if matches:
                score_moyen = sum(m.score_global for m in matches) / len(matches)
            
            return MatchingResponse(
                matches=matches,
                algorithme_utilise="nexten",
                total_jobs_analyses=len(original_jobs),
                jobs_matches=len(matches),
                score_moyen=score_moyen,
                services_externes_utilises=["nexten_matcher"],
                recommandations_generales=metadata.get("global_recommendations", []),
                ameliorations_possibles=metadata.get("improvement_suggestions", [])
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur adaptation réponse Nexten: {e}", exc_info=True)
            
            # Réponse de fallback
            return MatchingResponse(
                matches=[],
                algorithme_utilise="nexten",
                total_jobs_analyses=len(original_jobs),
                jobs_matches=0,
                services_externes_utilises=["nexten_matcher"],
                recommandations_generales=[f"Erreur lors du traitement Nexten: {str(e)}"]
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Vérifie la santé de Nexten Matcher
        """
        try:
            async with self.session.get(
                f"{self.base_url}/health",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    health_data = await response.json()
                    return {
                        "status": "healthy",
                        "response_time_ms": response.headers.get("X-Response-Time"),
                        "version": health_data.get("version"),
                        "details": health_data
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "http_status": response.status,
                        "error": await response.text()
                    }
        
        except Exception as e:
            return {
                "status": "unreachable",
                "error": str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de l'adaptateur"""
        avg_response_time = 0.0
        if self.stats["successful_requests"] > 0:
            avg_response_time = self.stats["total_response_time"] / self.stats["successful_requests"]
        
        return {
            **self.stats,
            "success_rate": (
                self.stats["successful_requests"] / max(self.stats["total_requests"], 1)
            ),
            "average_response_time_seconds": avg_response_time,
            "service_url": self.base_url
        }
