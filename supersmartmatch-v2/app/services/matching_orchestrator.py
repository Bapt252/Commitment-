"""
Orchestre les appels vers les services de matching externes

Coordonne les appels vers Nexten Matcher (port 5052) et SuperSmartMatch V1 (port 5062)
avec gestion des circuit breakers, fallbacks et monitoring.
"""

import asyncio
import logging
import aiohttp
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from ..models.matching_models import (
    CVData, JobData, MatchingOptions, MatchingResponse, MatchResult
)
from ..models.algorithm_models import AlgorithmType, AlgorithmSelection
from ..adapters.nexten_adapter import NextenMatcherAdapter
from ..adapters.supersmartmatch_v1_adapter import SuperSmartMatchV1Adapter
from ..services.circuit_breaker import CircuitBreakerManager
from ..services.cache_manager import CacheManager
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MatchingOrchestrator:
    """
    Orchestrateur principal des services de matching
    
    Coordonne les appels vers les différents algorithmes de matching
    avec gestion intégrée des circuit breakers et fallbacks.
    """
    
    def __init__(self):
        # Adapters pour services externes
        self.nexten_adapter = NextenMatcherAdapter()
        self.v1_adapter = SuperSmartMatchV1Adapter()
        
        # Gestionnaires
        self.circuit_breaker_manager = CircuitBreakerManager()
        self.cache_manager = CacheManager()
        
        # Session HTTP réutilisable
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Métriques
        self.execution_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "fallback_usage": 0,
            "cache_hits": 0
        }
        
        logger.info("🎼 MatchingOrchestrator initialisé")
    
    async def initialize(self):
        """Initialise l'orchestrateur et ses dépendances"""
        logger.info("🛠️ Initialisation MatchingOrchestrator...")
        
        # Création session HTTP
        timeout = aiohttp.ClientTimeout(total=settings.request_timeout)
        connector = aiohttp.TCPConnector(
            limit=settings.max_concurrent_requests,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                "User-Agent": "SuperSmartMatch-V2/2.0.0",
                "Content-Type": "application/json"
            }
        )
        
        # Initialisation des composants
        await self.nexten_adapter.initialize(self.session)
        await self.v1_adapter.initialize(self.session)
        await self.circuit_breaker_manager.initialize()
        await self.cache_manager.initialize()
        
        logger.info("✅ MatchingOrchestrator prêt")
    
    async def cleanup(self):
        """Nettoie les ressources"""
        logger.info("🧹 Nettoyage MatchingOrchestrator...")
        
        if self.session:
            await self.session.close()
        
        await self.circuit_breaker_manager.cleanup()
        await self.cache_manager.cleanup()
        
        logger.info("✅ MatchingOrchestrator nettoyé")
    
    async def execute_matching(
        self,
        algorithm: AlgorithmSelection,
        cv_data: CVData,
        jobs: List[JobData],
        options: Optional[MatchingOptions] = None
    ) -> MatchingResponse:
        """
        Exécute le matching avec l'algorithme sélectionné
        
        Args:
            algorithm: Algorithme sélectionné
            cv_data: Données CV
            jobs: Liste des jobs
            options: Options de matching
            
        Returns:
            MatchingResponse avec résultats
        """
        start_time = datetime.now()
        self.execution_stats["total_requests"] += 1
        
        try:
            # Vérification cache
            if options and options.enable_caching:
                cached_result = await self._check_cache(algorithm, cv_data, jobs, options)
                if cached_result:
                    self.execution_stats["cache_hits"] += 1
                    logger.info("📀 Résultat depuis cache")
                    return cached_result
            
            # Exécution avec circuit breaker
            result = await self._execute_with_circuit_breaker(
                algorithm.selected_algorithm, cv_data, jobs, options
            )
            
            # Mise en cache du résultat
            if options and options.enable_caching:
                await self._cache_result(algorithm, cv_data, jobs, options, result)
            
            # Mise à jour des métriques
            self.execution_stats["successful_requests"] += 1
            
            # Calcul du temps de traitement
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result.temps_traitement_ms = int(processing_time)
            
            logger.info(
                f"✅ Matching terminé: {len(result.matches)} résultats "
                f"en {processing_time:.1f}ms"
            )
            
            return result
            
        except Exception as e:
            self.execution_stats["failed_requests"] += 1
            logger.error(f"❌ Erreur lors du matching: {e}", exc_info=True)
            
            # Tentative de fallback
            if settings.enable_fallback:
                return await self._execute_fallback(cv_data, jobs, options, str(e))
            
            raise
    
    async def _execute_with_circuit_breaker(
        self,
        algorithm: AlgorithmType,
        cv_data: CVData,
        jobs: List[JobData],
        options: Optional[MatchingOptions]
    ) -> MatchingResponse:
        """Exécute le matching avec protection circuit breaker"""
        
        circuit_breaker = self.circuit_breaker_manager.get_circuit_breaker(algorithm)
        
        if not circuit_breaker.can_execute():
            logger.warning(f"⚠️ Circuit breaker ouvert pour {algorithm}, utilisation fallback")
            return await self._execute_fallback(cv_data, jobs, options, 
                                              f"Circuit breaker ouvert pour {algorithm}")
        
        try:
            # Exécution selon l'algorithme
            result = await self._execute_algorithm(algorithm, cv_data, jobs, options)
            
            # Succès, réinitialiser le circuit breaker
            circuit_breaker.record_success()
            
            return result
            
        except Exception as e:
            # Échec, enregistrer dans le circuit breaker
            circuit_breaker.record_failure()
            
            logger.error(f"❌ Échec algorithme {algorithm}: {e}")
            raise
    
    async def _execute_algorithm(
        self,
        algorithm: AlgorithmType,
        cv_data: CVData,
        jobs: List[JobData],
        options: Optional[MatchingOptions]
    ) -> MatchingResponse:
        """Exécute l'algorithme spécifique"""
        
        logger.debug(f"Exécution algorithme: {algorithm}")
        
        if algorithm == AlgorithmType.NEXTEN:
            return await self.nexten_adapter.execute_matching(cv_data, jobs, options)
        
        elif algorithm in [AlgorithmType.SMART_MATCH, AlgorithmType.ENHANCED, 
                          AlgorithmType.SEMANTIC, AlgorithmType.HYBRID, AlgorithmType.BASIC]:
            # Utiliser SuperSmartMatch V1 avec l'algorithme spécifique
            return await self.v1_adapter.execute_matching(cv_data, jobs, algorithm, options)
        
        else:
            raise ValueError(f"Algorithme non supporté: {algorithm}")
    
    async def _execute_fallback(
        self,
        cv_data: CVData,
        jobs: List[JobData],
        options: Optional[MatchingOptions],
        error_reason: str
    ) -> MatchingResponse:
        """Exécute la séquence de fallback"""
        
        self.execution_stats["fallback_usage"] += 1
        logger.warning(f"🔄 Exécution fallback: {error_reason}")
        
        # Essayer chaque algorithme dans l'ordre de fallback
        for algorithm_name in settings.fallback_algorithm_order:
            algorithm = AlgorithmType(algorithm_name)
            
            circuit_breaker = self.circuit_breaker_manager.get_circuit_breaker(algorithm)
            if not circuit_breaker.can_execute():
                logger.debug(f"Circuit breaker ouvert pour {algorithm}, passage au suivant")
                continue
            
            try:
                logger.info(f"🔄 Tentative fallback avec {algorithm}")
                result = await self._execute_algorithm(algorithm, cv_data, jobs, options)
                
                # Marquer comme utilisant le fallback
                result.fallback_utilise = True
                result.services_externes_utilises.append(f"fallback-{algorithm}")
                result.recommandations_generales.append(
                    f"Résultat obtenu via fallback ({algorithm}) en raison de: {error_reason}"
                )
                
                circuit_breaker.record_success()
                logger.info(f"✅ Fallback réussi avec {algorithm}")
                
                return result
                
            except Exception as e:
                circuit_breaker.record_failure()
                logger.warning(f"⚠️ Échec fallback {algorithm}: {e}")
                continue
        
        # Tous les fallbacks ont échoué, retourner réponse vide
        logger.error("❌ Tous les fallbacks ont échoué")
        
        return MatchingResponse(
            matches=[],
            algorithme_utilise="fallback-failed",
            total_jobs_analyses=len(jobs),
            jobs_matches=0,
            fallback_utilise=True,
            recommandations_generales=[
                "Aucun algorithme n'a pu traiter la requête",
                f"Raison initiale: {error_reason}",
                "Veuillez vérifier la configuration et les services externes"
            ]
        )
    
    async def _check_cache(
        self,
        algorithm: AlgorithmSelection,
        cv_data: CVData,
        jobs: List[JobData],
        options: MatchingOptions
    ) -> Optional[MatchingResponse]:
        """Vérifie si le résultat est en cache"""
        return await self.cache_manager.get_matching_result(
            algorithm, cv_data, jobs, options
        )
    
    async def _cache_result(
        self,
        algorithm: AlgorithmSelection,
        cv_data: CVData,
        jobs: List[JobData],
        options: MatchingOptions,
        result: MatchingResponse
    ):
        """Met en cache le résultat"""
        await self.cache_manager.cache_matching_result(
            algorithm, cv_data, jobs, options, result
        )
    
    async def validate_external_services(self):
        """Valide que les services externes sont accessibles"""
        logger.info("🔍 Validation des services externes...")
        
        # Validation Nexten Matcher
        try:
            await self.nexten_adapter.health_check()
            logger.info("✅ Nexten Matcher accessible")
        except Exception as e:
            logger.error(f"❌ Nexten Matcher inaccessible: {e}")
        
        # Validation SuperSmartMatch V1
        try:
            await self.v1_adapter.health_check()
            logger.info("✅ SuperSmartMatch V1 accessible")
        except Exception as e:
            logger.error(f"❌ SuperSmartMatch V1 inaccessible: {e}")
    
    async def check_external_services_health(self) -> Dict[str, Dict[str, Any]]:
        """Vérifie la santé des services externes"""
        health_status = {}
        
        # Vérification Nexten Matcher
        try:
            nexten_health = await self.nexten_adapter.health_check()
            health_status["nexten_matcher"] = {
                "status": "healthy",
                "url": settings.nexten_matcher_url,
                "details": nexten_health
            }
        except Exception as e:
            health_status["nexten_matcher"] = {
                "status": "unhealthy",
                "url": settings.nexten_matcher_url,
                "error": str(e)
            }
        
        # Vérification SuperSmartMatch V1
        try:
            v1_health = await self.v1_adapter.health_check()
            health_status["supersmartmatch_v1"] = {
                "status": "healthy",
                "url": settings.supersmartmatch_v1_url,
                "details": v1_health
            }
        except Exception as e:
            health_status["supersmartmatch_v1"] = {
                "status": "unhealthy",
                "url": settings.supersmartmatch_v1_url,
                "error": str(e)
            }
        
        return health_status
    
    async def get_algorithms_status(self) -> Dict[str, Any]:
        """Retourne le statut de tous les algorithmes"""
        return {
            "circuit_breakers": self.circuit_breaker_manager.get_all_status(),
            "execution_stats": self.execution_stats,
            "cache_stats": await self.cache_manager.get_stats()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques d'exécution"""
        return self.execution_stats.copy()
