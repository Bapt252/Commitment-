"""
Adaptateur pour SuperSmartMatch V1 (port 5062)

Adapte les requêtes SuperSmartMatch V2 vers le format V1
et utilise les 4 algorithmes existants (smart-match, enhanced, semantic, basic).
"""

import logging
import aiohttp
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any

from ..models.matching_models import (
    CVData, JobData, MatchingOptions, MatchingResponse, MatchResult
)
from ..models.algorithm_models import AlgorithmType
from ..config import get_settings, AlgorithmConfig

logger = logging.getLogger(__name__)
settings = get_settings()
algorithm_config = AlgorithmConfig()


class SuperSmartMatchV1Adapter:
    """
    Adaptateur pour SuperSmartMatch V1
    
    Utilise l'API existante de SuperSmartMatch V1 avec ses 4 algorithmes :
    - smart-match : Géolocalisation avec Google Maps
    - enhanced : Pondération adaptative intelligente
    - semantic : Analyse sémantique des compétences
    - basic : Algorithme de base
    """
    
    def __init__(self):
        self.base_url = settings.supersmartmatch_v1_url
        self.endpoint = algorithm_config.V1_ENDPOINT
        self.timeout = algorithm_config.V1_TIMEOUT
        self.retry_attempts = algorithm_config.V1_RETRY_ATTEMPTS
        
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Mapping des algorithmes V2 vers V1
        self.algorithm_mapping = algorithm_config.V1_ALGORITHMS
        
        # Métriques par algorithme
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_response_time": 0.0,
            "algorithm_usage": {}
        }
        
        logger.info(f"🚀 SuperSmartMatchV1Adapter initialisé - URL: {self.base_url}")
    
    async def initialize(self, session: aiohttp.ClientSession):
        """Initialise l'adaptateur avec une session HTTP"""
        self.session = session
        logger.info("✅ SuperSmartMatchV1Adapter prêt")
    
    async def execute_matching(
        self,
        cv_data: CVData,
        jobs: List[JobData],
        algorithm: AlgorithmType,
        options: Optional[MatchingOptions] = None
    ) -> MatchingResponse:
        """
        Exécute le matching via SuperSmartMatch V1
        
        Args:
            cv_data: Données CV
            jobs: Liste des jobs
            algorithm: Algorithme V1 à utiliser
            options: Options de matching
            
        Returns:
            MatchingResponse formatée
        """
        start_time = datetime.now()
        self.stats["total_requests"] += 1
        
        # Suivi d'utilisation par algorithme
        algo_key = algorithm.value
        if algo_key not in self.stats["algorithm_usage"]:
            self.stats["algorithm_usage"][algo_key] = 0
        self.stats["algorithm_usage"][algo_key] += 1
        
        try:
            logger.debug(f"Appel SuperSmartMatch V1: {algorithm} pour {len(jobs)} jobs")
            
            # Préparation de la requête V1
            request_payload = self._prepare_v1_request(cv_data, jobs, algorithm, options)
            
            # Appel avec retry
            response_data = await self._call_v1_with_retry(request_payload)
            
            # Adaptation de la réponse
            result = self._adapt_v1_response(response_data, algorithm, jobs)
            
            # Métriques de succès
            response_time = (datetime.now() - start_time).total_seconds()
            self.stats["successful_requests"] += 1
            self.stats["total_response_time"] += response_time
            
            logger.info(
                f"✅ SuperSmartMatch V1 ({algorithm}): {len(result.matches)} résultats "
                f"en {response_time*1000:.1f}ms"
            )
            
            return result
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"❌ Erreur SuperSmartMatch V1 ({algorithm}): {e}", exc_info=True)
            raise
    
    def _prepare_v1_request(
        self,
        cv_data: CVData,
        jobs: List[JobData],
        algorithm: AlgorithmType,
        options: Optional[MatchingOptions]
    ) -> Dict[str, Any]:
        """
        Prépare la requête au format SuperSmartMatch V1
        
        Format V1 attendu :
        {
          "cv_data": {...},
          "job_data": [...],  # V1 utilise 'job_data'
          "algorithm": "smart-match",
          "options": {...}
        }
        """
        # Conversion CV vers format V1
        cv_v1 = {
            "competences": cv_data.competences,
            "experience": cv_data.experience,
            "localisation": cv_data.localisation,
            "niveau_etudes": cv_data.niveau_etudes,
            "certifications": cv_data.certifications,
            "salaire_souhaite": cv_data.salaire_souhaite,
            "type_contrat_souhaite": cv_data.type_contrat_souhaite,
            "mobilite_km": cv_data.mobilite_km,
            "teletravail_accepte": cv_data.teletravail_accepte,
            "age": cv_data.age,
            "nom": cv_data.nom,
            "prenom": cv_data.prenom
        }
        
        # Conversion jobs vers format V1
        jobs_v1 = []
        for job in jobs:
            job_v1 = {
                "id": job.id,
                "titre": job.titre,
                "entreprise": job.entreprise,
                "localisation": job.localisation,
                "description": job.description,
                "competences": job.competences,
                "experience_requise": job.experience_requise,
                "niveau_etudes_requis": job.niveau_etudes_requis,
                "certifications_requises": job.certifications_requises,
                "salaire_min": job.salaire_min,
                "salaire_max": job.salaire_max,
                "type_contrat": job.type_contrat,
                "teletravail_possible": job.teletravail_possible,
                "secteur": job.secteur,
                "taille_entreprise": job.taille_entreprise
            }
            jobs_v1.append(job_v1)
        
        # Algorithme V1
        v1_algorithm = self.algorithm_mapping.get(algorithm.value, "basic")
        
        # Options V1
        v1_options = {}
        if options:
            v1_options = {
                "max_results": options.max_results,
                "min_score": options.min_score,
                "include_travel_time": options.include_travel_time,
                "max_distance_km": options.max_distance_km
            }
        
        return {
            "cv_data": cv_v1,
            "job_data": jobs_v1,  # V1 utilise 'job_data' au lieu de 'jobs'
            "algorithm": v1_algorithm,
            "options": v1_options
        }
    
    async def _call_v1_with_retry(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Appelle SuperSmartMatch V1 avec retry automatique
        """
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                logger.debug(f"Tentative {attempt + 1}/{self.retry_attempts} vers V1")
                
                async with self.session.post(
                    f"{self.base_url}{self.endpoint}",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.debug("Réponse SuperSmartMatch V1 reçue avec succès")
                        return data
                    
                    elif response.status == 429:  # Rate limiting
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limit V1, attente {wait_time}s")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    else:
                        error_text = await response.text()
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=f"Erreur SuperSmartMatch V1: {error_text}"
                        )
            
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                wait_time = 2 ** attempt
                logger.warning(f"Erreur tentative {attempt + 1}: {e}, retry dans {wait_time}s")
                
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(wait_time)
                continue
        
        # Toutes les tentatives ont échoué
        raise Exception(f"SuperSmartMatch V1 inaccessible après {self.retry_attempts} tentatives: {last_exception}")
    
    def _adapt_v1_response(
        self,
        v1_data: Dict[str, Any],
        algorithm: AlgorithmType,
        original_jobs: List[JobData]
    ) -> MatchingResponse:
        """
        Adapte la réponse SuperSmartMatch V1 vers le format V2
        
        Format V1 attendu :
        {
          "results": [...],
          "algorithm_used": "smart-match",
          "total_jobs": 10,
          "matched_jobs": 5,
          "processing_time_ms": 150
        }
        """
        try:
            # Extraction des résultats V1
            v1_results = v1_data.get("results", [])
            
            # Conversion vers MatchResult
            matches = []
            for result in v1_results:
                match_result = MatchResult(
                    job_id=result.get("job_id"),
                    score_global=result.get("score", 0.0),
                    score_competences=result.get("skills_score"),
                    score_experience=result.get("experience_score"),
                    score_localisation=result.get("location_score"),
                    score_salaire=result.get("salary_score"),
                    competences_matchees=result.get("matched_skills", []),
                    competences_manquantes=result.get("missing_skills", []),
                    distance_km=result.get("distance_km"),
                    temps_trajet_minutes=result.get("travel_time_minutes"),
                    moyen_transport=result.get("transport_mode"),
                    raisons_match=result.get("reasons", []),
                    recommandations=result.get("recommendations", []),
                    algorithme_utilise=f"v1-{algorithm.value}",
                    confiance=result.get("confidence")
                )
                matches.append(match_result)
            
            # Tri par score décroissant
            matches.sort(key=lambda x: x.score_global, reverse=True)
            
            # Score moyen
            score_moyen = None
            if matches:
                score_moyen = sum(m.score_global for m in matches) / len(matches)
            
            return MatchingResponse(
                matches=matches,
                algorithme_utilise=f"v1-{algorithm.value}",
                temps_traitement_ms=v1_data.get("processing_time_ms"),
                total_jobs_analyses=v1_data.get("total_jobs", len(original_jobs)),
                jobs_matches=v1_data.get("matched_jobs", len(matches)),
                score_moyen=score_moyen,
                services_externes_utilises=[f"supersmartmatch_v1_{algorithm.value}"],
                recommandations_generales=v1_data.get("global_recommendations", []),
                ameliorations_possibles=v1_data.get("suggestions", [])
            )
            
        except Exception as e:
            logger.error(f"❌ Erreur adaptation réponse V1: {e}", exc_info=True)
            
            # Réponse de fallback
            return MatchingResponse(
                matches=[],
                algorithme_utilise=f"v1-{algorithm.value}",
                total_jobs_analyses=len(original_jobs),
                jobs_matches=0,
                services_externes_utilises=[f"supersmartmatch_v1_{algorithm.value}"],
                recommandations_generales=[f"Erreur lors du traitement V1: {str(e)}"]
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Vérifie la santé de SuperSmartMatch V1
        """
        try:
            async with self.session.get(
                f"{self.base_url}/api/v1/health",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    health_data = await response.json()
                    return {
                        "status": "healthy",
                        "response_time_ms": response.headers.get("X-Response-Time"),
                        "version": health_data.get("version"),
                        "algorithms": health_data.get("algorithms_available", []),
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
            "service_url": self.base_url,
            "supported_algorithms": list(self.algorithm_mapping.keys())
        }
