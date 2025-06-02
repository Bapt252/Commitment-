"""
Gestionnaire de cache Redis pour SuperSmartMatch V2

Gère la mise en cache des résultats de matching, sélections d'algorithmes,
et métriques pour optimiser les performances.
"""

import asyncio
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

import aioredis
from aioredis import Redis

from ..models.matching_models import (
    CVData, JobData, MatchingOptions, MatchingResponse
)
from ..models.algorithm_models import AlgorithmSelection
from ..config import get_settings, CacheConfig

logger = logging.getLogger(__name__)
settings = get_settings()
cache_config = CacheConfig()


class CacheManager:
    """
    Gestionnaire de cache Redis
    
    Gère la mise en cache intelligente des résultats de matching,
    sélections d'algorithmes et métriques pour optimiser les performances.
    """
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.cache_config = cache_config
        
        # Statistiques du cache
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_sets": 0,
            "cache_errors": 0
        }
        
        logger.info("🗄️ CacheManager initialisé")
    
    async def initialize(self):
        """Initialise la connexion Redis"""
        try:
            logger.info(f"📡 Connexion à Redis: {settings.redis_url}")
            
            self.redis = await aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                **cache_config.REDIS_CONFIG
            )
            
            # Test de connexion
            await self.redis.ping()
            
            logger.info("✅ Cache Redis connecté")
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion Redis: {e}")
            self.redis = None
            raise
    
    async def cleanup(self):
        """Ferme la connexion Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("🔌 Connexion Redis fermée")
    
    async def get_matching_result(
        self,
        algorithm: AlgorithmSelection,
        cv_data: CVData,
        jobs: List[JobData],
        options: Optional[MatchingOptions]
    ) -> Optional[MatchingResponse]:
        """
        Récupère un résultat de matching depuis le cache
        
        Args:
            algorithm: Sélection d'algorithme
            cv_data: Données CV
            jobs: Liste des jobs
            options: Options de matching
            
        Returns:
            MatchingResponse si trouvé dans le cache, None sinon
        """
        if not self.redis or not settings.enable_caching:
            return None
        
        try:
            cache_key = self._generate_matching_cache_key(algorithm, cv_data, jobs, options)
            
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                self.stats["cache_hits"] += 1
                logger.debug(f"💾 Cache hit: {cache_key[:20]}...")
                
                # Désérialisation
                result_dict = json.loads(cached_data)
                result = MatchingResponse(**result_dict)
                result.depuis_cache = True
                
                return result
            else:
                self.stats["cache_misses"] += 1
                logger.debug(f"🔍 Cache miss: {cache_key[:20]}...")
                return None
                
        except Exception as e:
            self.stats["cache_errors"] += 1
            logger.error(f"❌ Erreur lecture cache: {e}")
            return None
    
    async def cache_matching_result(
        self,
        algorithm: AlgorithmSelection,
        cv_data: CVData,
        jobs: List[JobData],
        options: Optional[MatchingOptions],
        result: MatchingResponse
    ):
        """
        Met en cache un résultat de matching
        
        Args:
            algorithm: Sélection d'algorithme
            cv_data: Données CV
            jobs: Liste des jobs
            options: Options de matching
            result: Résultat à mettre en cache
        """
        if not self.redis or not settings.enable_caching:
            return
        
        try:
            cache_key = self._generate_matching_cache_key(algorithm, cv_data, jobs, options)
            
            # Sérialisation
            result_dict = result.dict()
            cached_data = json.dumps(result_dict, default=str)
            
            # Mise en cache avec TTL
            ttl = cache_config.CACHE_TTL["matching_result"]
            await self.redis.setex(cache_key, ttl, cached_data)
            
            self.stats["cache_sets"] += 1
            logger.debug(f"💾 Résultat mis en cache: {cache_key[:20]}... (TTL: {ttl}s)")
            
        except Exception as e:
            self.stats["cache_errors"] += 1
            logger.error(f"❌ Erreur écriture cache: {e}")
    
    async def get_algorithm_selection(
        self,
        cv_data: CVData,
        jobs: List[JobData]
    ) -> Optional[AlgorithmSelection]:
        """
        Récupère une sélection d'algorithme depuis le cache
        """
        if not self.redis or not settings.enable_caching:
            return None
        
        try:
            cache_key = self._generate_algorithm_cache_key(cv_data, jobs)
            
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                self.stats["cache_hits"] += 1
                selection_dict = json.loads(cached_data)
                return AlgorithmSelection(**selection_dict)
            else:
                self.stats["cache_misses"] += 1
                return None
                
        except Exception as e:
            self.stats["cache_errors"] += 1
            logger.error(f"❌ Erreur lecture cache algorithme: {e}")
            return None
    
    async def cache_algorithm_selection(
        self,
        cv_data: CVData,
        jobs: List[JobData],
        selection: AlgorithmSelection
    ):
        """
        Met en cache une sélection d'algorithme
        """
        if not self.redis or not settings.enable_caching:
            return
        
        try:
            cache_key = self._generate_algorithm_cache_key(cv_data, jobs)
            
            # Sérialisation
            selection_dict = selection.dict()
            cached_data = json.dumps(selection_dict, default=str)
            
            # Mise en cache avec TTL
            ttl = cache_config.CACHE_TTL["algorithm_selection"]
            await self.redis.setex(cache_key, ttl, cached_data)
            
            self.stats["cache_sets"] += 1
            logger.debug(f"💾 Sélection algorithme mise en cache: {cache_key[:20]}...")
            
        except Exception as e:
            self.stats["cache_errors"] += 1
            logger.error(f"❌ Erreur écriture cache algorithme: {e}")
    
    async def cache_service_health(
        self,
        service_name: str,
        health_data: Dict[str, Any]
    ):
        """
        Met en cache l'état de santé d'un service
        """
        if not self.redis:
            return
        
        try:
            cache_key = cache_config.CACHE_KEYS["service_health"].format(service=service_name)
            
            cached_data = json.dumps({
                "health_data": health_data,
                "timestamp": datetime.now().isoformat()
            })
            
            ttl = cache_config.CACHE_TTL["service_health"]
            await self.redis.setex(cache_key, ttl, cached_data)
            
            logger.debug(f"💾 Santé service {service_name} mise en cache")
            
        except Exception as e:
            logger.error(f"❌ Erreur cache santé service: {e}")
    
    async def get_service_health(
        self,
        service_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Récupère l'état de santé d'un service depuis le cache
        """
        if not self.redis:
            return None
        
        try:
            cache_key = cache_config.CACHE_KEYS["service_health"].format(service=service_name)
            
            cached_data = await self.redis.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                return data["health_data"]
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur lecture cache santé: {e}")
            return None
    
    async def cache_metrics(
        self,
        metrics_type: str,
        metrics_data: Dict[str, Any]
    ):
        """
        Met en cache des métriques
        """
        if not self.redis:
            return
        
        try:
            timestamp = int(datetime.now().timestamp())
            cache_key = cache_config.CACHE_KEYS["metrics"].format(
                type=metrics_type,
                timestamp=timestamp
            )
            
            cached_data = json.dumps({
                "metrics": metrics_data,
                "timestamp": timestamp
            })
            
            ttl = cache_config.CACHE_TTL["metrics"]
            await self.redis.setex(cache_key, ttl, cached_data)
            
            logger.debug(f"💾 Métriques {metrics_type} mises en cache")
            
        except Exception as e:
            logger.error(f"❌ Erreur cache métriques: {e}")
    
    async def get_recent_metrics(
        self,
        metrics_type: str,
        hours: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Récupère les métriques récentes
        """
        if not self.redis:
            return []
        
        try:
            # Pattern pour rechercher les clés de métriques
            pattern = cache_config.CACHE_KEYS["metrics"].format(
                type=metrics_type,
                timestamp="*"
            )
            
            keys = await self.redis.keys(pattern)
            
            # Filtrer par période
            cutoff_time = datetime.now() - timedelta(hours=hours)
            cutoff_timestamp = int(cutoff_time.timestamp())
            
            recent_metrics = []
            
            for key in keys:
                cached_data = await self.redis.get(key)
                if cached_data:
                    data = json.loads(cached_data)
                    if data["timestamp"] >= cutoff_timestamp:
                        recent_metrics.append(data)
            
            # Trier par timestamp
            recent_metrics.sort(key=lambda x: x["timestamp"])
            
            return recent_metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur lecture métriques récentes: {e}")
            return []
    
    async def clear_cache(self, pattern: Optional[str] = None):
        """
        Vide le cache (tout ou selon un pattern)
        
        Args:
            pattern: Pattern de clés à supprimer (None = tout)
        """
        if not self.redis:
            return
        
        try:
            if pattern:
                keys = await self.redis.keys(pattern)
                if keys:
                    deleted = await self.redis.delete(*keys)
                    logger.info(f"🗑️ {deleted} clés supprimées (pattern: {pattern})")
            else:
                await self.redis.flushdb()
                logger.info("🗑️ Cache vidé complètement")
                
        except Exception as e:
            logger.error(f"❌ Erreur vidage cache: {e}")
    
    def _generate_matching_cache_key(
        self,
        algorithm: AlgorithmSelection,
        cv_data: CVData,
        jobs: List[JobData],
        options: Optional[MatchingOptions]
    ) -> str:
        """
        Génère une clé de cache pour un résultat de matching
        """
        # Données pertinentes pour le hash
        cache_data = {
            "algorithm": algorithm.selected_algorithm.value,
            "cv_competences": sorted(cv_data.competences),
            "cv_experience": cv_data.experience,
            "cv_localisation": cv_data.localisation,
            "jobs": [
                {
                    "id": job.id,
                    "competences": sorted(job.competences),
                    "localisation": job.localisation
                }
                for job in jobs
            ],
            "options": options.dict() if options else None
        }
        
        # Génération du hash
        cache_str = json.dumps(cache_data, sort_keys=True)
        hash_obj = hashlib.md5(cache_str.encode())
        
        return cache_config.CACHE_KEYS["matching_result"].format(hash=hash_obj.hexdigest())
    
    def _generate_algorithm_cache_key(
        self,
        cv_data: CVData,
        jobs: List[JobData]
    ) -> str:
        """
        Génère une clé de cache pour une sélection d'algorithme
        """
        cache_data = {
            "cv_competences": sorted(cv_data.competences),
            "cv_experience": cv_data.experience,
            "cv_localisation": cv_data.localisation,
            "cv_questionnaire_complete": cv_data.questionnaire_complete,
            "jobs_count": len(jobs),
            "jobs_locations": sorted(set(
                job.localisation for job in jobs if job.localisation
            ))
        }
        
        cache_str = json.dumps(cache_data, sort_keys=True)
        hash_obj = hashlib.md5(cache_str.encode())
        
        return cache_config.CACHE_KEYS["algorithm_selection"].format(hash=hash_obj.hexdigest())
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du cache
        """
        stats = self.stats.copy()
        
        # Calcul du taux de succès
        total_requests = stats["cache_hits"] + stats["cache_misses"]
        if total_requests > 0:
            stats["hit_rate"] = stats["cache_hits"] / total_requests
        else:
            stats["hit_rate"] = 0.0
        
        # Informations Redis
        if self.redis:
            try:
                info = await self.redis.info()
                stats["redis_info"] = {
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory", 0),
                    "used_memory_human": info.get("used_memory_human", "0B"),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                }
            except Exception as e:
                stats["redis_info"] = {"error": str(e)}
        
        return stats
