"""
Adaptateur Cache Redis pour SuperSmartMatch V2

Gère le cache intelligent :
- Mise en cache des résultats de matching
- Gestion TTL configurable
- Éviction intelligente
- Statistiques de performance
"""

import redis.asyncio as redis
import json
import pickle
import hashlib
from typing import Any, Optional, Dict, List, Union
import time
from datetime import datetime, timedelta

from ..config import get_config
from ..logger import get_logger

config = get_config()
logger = get_logger(__name__)

class CacheAdapter:
    """Adaptateur pour le cache Redis"""
    
    def __init__(self):
        self.redis_url = config.redis_url
        self.default_ttl = config.cache_ttl
        self.enabled = config.enable_caching
        
        # Connection pool Redis
        self.pool = redis.ConnectionPool.from_url(
            self.redis_url,
            decode_responses=False,  # Pour supporter pickle
            max_connections=20
        )
        self.redis_client = redis.Redis(connection_pool=self.pool)
        
        # Statistiques
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0
        }
        
        logger.info("Cache adapter initialized", redis_url=self.redis_url, enabled=self.enabled)
    
    def _generate_key(self, namespace: str, key: str) -> str:
        """Générer une clé Redis avec namespace"""
        return f"supersmartmatch_v2:{namespace}:{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Sérialiser une valeur pour Redis"""
        try:
            # Essayer JSON d'abord (plus lisible)
            if isinstance(value, (dict, list, str, int, float, bool)):
                return json.dumps(value, ensure_ascii=False).encode('utf-8')
            else:
                # Fallback sur pickle pour les objets complexes
                return pickle.dumps(value)
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Désérialiser une valeur depuis Redis"""
        try:
            # Essayer JSON d'abord
            return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                # Fallback sur pickle
                return pickle.loads(data)
            except Exception as e:
                logger.error(f"Deserialization error: {e}")
                return None
    
    async def get(self, key: str, namespace: str = "default") -> Optional[Any]:
        """Récupérer une valeur du cache"""
        if not self.enabled:
            return None
        
        try:
            redis_key = self._generate_key(namespace, key)
            data = await self.redis_client.get(redis_key)
            
            if data is not None:
                self.stats["hits"] += 1
                value = self._deserialize_value(data)
                logger.debug("Cache hit", key=redis_key)
                return value
            else:
                self.stats["misses"] += 1
                logger.debug("Cache miss", key=redis_key)
                return None
                
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Cache get error: {e}", key=key)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, namespace: str = "default") -> bool:
        """Stocker une valeur dans le cache"""
        if not self.enabled:
            return False
        
        try:
            redis_key = self._generate_key(namespace, key)
            serialized_value = self._serialize_value(value)
            
            ttl = ttl or self.default_ttl
            
            await self.redis_client.setex(redis_key, ttl, serialized_value)
            self.stats["sets"] += 1
            
            logger.debug("Cache set", key=redis_key, ttl=ttl)
            return True
            
        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Cache set error: {e}", key=key)
            return False
    
    async def delete(self, key: str, namespace: str = "default") -> bool:
        """Supprimer une valeur du cache"""
        if not self.enabled:
            return False
        
        try:
            redis_key = self._generate_key(namespace, key)
            result = await self.redis_client.delete(redis_key)
            
            logger.debug("Cache delete", key=redis_key, deleted=bool(result))
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}", key=key)
            return False
    
    async def exists(self, key: str, namespace: str = "default") -> bool:
        """Vérifier si une clé existe"""
        if not self.enabled:
            return False
        
        try:
            redis_key = self._generate_key(namespace, key)
            result = await self.redis_client.exists(redis_key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache exists error: {e}", key=key)
            return False
    
    async def clear_namespace(self, namespace: str) -> int:
        """Vider un namespace complet"""
        if not self.enabled:
            return 0
        
        try:
            pattern = self._generate_key(namespace, "*")
            keys = await self.redis_client.keys(pattern)
            
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"Namespace cleared", namespace=namespace, keys_deleted=deleted)
                return deleted
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Cache clear namespace error: {e}", namespace=namespace)
            return 0
    
    async def clear_all(self) -> int:
        """Vider tout le cache SuperSmartMatch V2"""
        if not self.enabled:
            return 0
        
        try:
            pattern = "supersmartmatch_v2:*"
            keys = await self.redis_client.keys(pattern)
            
            if keys:
                deleted = await self.redis_client.delete(*keys)
                logger.info(f"All cache cleared", keys_deleted=deleted)
                return deleted
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du cache"""
        try:
            # Statistiques Redis
            redis_info = await self.redis_client.info("memory")
            redis_stats = await self.redis_client.info("stats")
            
            # Compter les clés SuperSmartMatch V2
            pattern = "supersmartmatch_v2:*"
            keys = await self.redis_client.keys(pattern)
            
            # Calculer les taux
            total_requests = self.stats["hits"] + self.stats["misses"]
            hit_rate = (self.stats["hits"] / total_requests) if total_requests > 0 else 0
            miss_rate = (self.stats["misses"] / total_requests) if total_requests > 0 else 0
            
            return {
                "enabled": self.enabled,
                "total_keys": len(keys),
                "memory_usage_mb": redis_info.get("used_memory", 0) / 1024 / 1024,
                "hit_rate": hit_rate,
                "miss_rate": miss_rate,
                "total_requests": total_requests,
                "cache_hits": self.stats["hits"],
                "cache_misses": self.stats["misses"],
                "cache_sets": self.stats["sets"],
                "cache_errors": self.stats["errors"],
                "redis_stats": {
                    "keyspace_hits": redis_stats.get("keyspace_hits", 0),
                    "keyspace_misses": redis_stats.get("keyspace_misses", 0),
                    "total_commands_processed": redis_stats.get("total_commands_processed", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {
                "enabled": self.enabled,
                "error": str(e),
                "local_stats": self.stats
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Vérifier la santé de Redis"""
        try:
            start_time = time.time()
            
            # Test ping
            pong = await self.redis_client.ping()
            response_time = (time.time() - start_time) * 1000
            
            # Test set/get
            test_key = "health_check_test"
            test_value = {"timestamp": int(time.time()), "test": True}
            
            await self.set(test_key, test_value, ttl=60, namespace="health")
            retrieved = await self.get(test_key, namespace="health")
            
            await self.delete(test_key, namespace="health")
            
            return {
                "status": "healthy" if (pong and retrieved is not None) else "unhealthy",
                "ping": pong,
                "response_time_ms": response_time,
                "set_get_test": retrieved is not None,
                "last_check": int(time.time())
            }
            
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_check": int(time.time())
            }
    
    async def get_key_distribution(self) -> Dict[str, int]:
        """Analyser la distribution des clés par namespace"""
        try:
            pattern = "supersmartmatch_v2:*"
            keys = await self.redis_client.keys(pattern)
            
            distribution = {}
            for key in keys:
                key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                parts = key_str.split(":")
                if len(parts) >= 2:
                    namespace = parts[1]
                    distribution[namespace] = distribution.get(namespace, 0) + 1
            
            return distribution
            
        except Exception as e:
            logger.error(f"Key distribution error: {e}")
            return {}
    
    async def __aenter__(self):
        """Support du context manager"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage à la sortie"""
        await self.redis_client.close()