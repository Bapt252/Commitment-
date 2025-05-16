#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module de cache pour les appels à l'API Google Maps.

Ce module fournit une fonctionnalité de cache pour réduire les appels API
et respecter les quotas, tout en optimisant les performances.
"""

import os
import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timedelta
import redis

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MapsCache:
    """
    Gestionnaire de cache pour les requêtes Google Maps avec support Redis et fallback fichier.
    """
    
    def __init__(self, redis_url: str = None, cache_file: str = 'maps_cache.json', 
                 ttl: int = 604800):  # 7 jours par défaut
        """
        Initialise le gestionnaire de cache.
        
        Args:
            redis_url: URL de connexion Redis (optionnel)
            cache_file: Chemin du fichier de cache local (fallback)
            ttl: Durée de vie des entrées en secondes
        """
        self.ttl = ttl
        self.cache_file = cache_file
        self.redis_client = None
        self.file_cache = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "saved_calls": 0,
            "usage": {
                "travel_time": 0,
                "geocode": 0,
                "distance_matrix": 0
            },
            "last_cleanup": time.time()
        }
        
        # Essayer d'initialiser Redis si une URL est fournie
        if redis_url:
            try:
                import redis as redis_module
                self.redis_client = redis_module.from_url(redis_url)
                logger.info("Cache Redis initialisé avec succès")
            except (ImportError, Exception) as e:
                logger.warning(f"⚠️ Impossible d'initialiser Redis: {e}")
                logger.info("Utilisation du cache fichier uniquement")
        
        # Charger le cache fichier comme fallback
        self._load_file_cache()
    
    def _load_file_cache(self):
        """Charge le cache depuis le fichier."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.file_cache = cache_data.get('cache', {})
                    self.stats = cache_data.get('stats', self.stats)
                logger.info(f"Cache chargé depuis {self.cache_file}")
            else:
                logger.info(f"Fichier de cache {self.cache_file} non trouvé, création d'un nouveau cache")
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement du cache: {e}")
            self.file_cache = {}
    
    def _save_file_cache(self):
        """Enregistre le cache dans le fichier."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'cache': self.file_cache,
                    'stats': self.stats
                }, f, indent=2)
            logger.debug(f"Cache sauvegardé dans {self.cache_file}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde du cache: {e}")
    
    def _generate_key(self, request_type: str, **params) -> str:
        """Génère une clé de cache unique basée sur les paramètres."""
        # Trier les paramètres pour garantir une clé cohérente
        sorted_params = sorted(params.items())
        params_str = f"{request_type}:{json.dumps(sorted_params)}"
        return hashlib.md5(params_str.encode()).hexdigest()
    
    def get(self, request_type: str, **params) -> Optional[Dict[str, Any]]:
        """
        Récupère une entrée du cache.
        
        Args:
            request_type: Type de requête (travel_time, geocode, distance_matrix)
            **params: Paramètres de la requête
            
        Returns:
            Valeur en cache ou None si non trouvée
        """
        key = self._generate_key(request_type, **params)
        now = time.time()
        
        # Essayer d'abord Redis si disponible
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    data = json.loads(cached_data)
                    if data.get('expires_at', 0) > now:
                        self.stats["hits"] += 1
                        self.stats["saved_calls"] += 1
                        self.stats["usage"][request_type] += 1
                        return data.get('value')
            except Exception as e:
                logger.warning(f"⚠️ Erreur Redis, fallback sur cache fichier: {e}")
        
        # Fallback sur le cache fichier
        if key in self.file_cache:
            data = self.file_cache[key]
            if data.get('expires_at', 0) > now:
                self.stats["hits"] += 1
                self.stats["saved_calls"] += 1
                self.stats["usage"][request_type] += 1
                return data.get('value')
        
        self.stats["misses"] += 1
        return None
    
    def set(self, request_type: str, value: Any, **params):
        """
        Ajoute ou met à jour une entrée dans le cache.
        
        Args:
            request_type: Type de requête
            value: Valeur à mettre en cache
            **params: Paramètres de la requête
        """
        key = self._generate_key(request_type, **params)
        now = time.time()
        expires_at = now + self.ttl
        
        cache_data = {
            'value': value,
            'created_at': now,
            'expires_at': expires_at
        }
        
        # Essayer d'abord Redis si disponible
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key, 
                    self.ttl, 
                    json.dumps(cache_data)
                )
            except Exception as e:
                logger.warning(f"⚠️ Erreur Redis, fallback sur cache fichier: {e}")
        
        # Toujours mettre à jour le cache fichier comme fallback
        self.file_cache[key] = cache_data
        
        # Périodiquement nettoyer et sauvegarder le cache fichier
        if now - self.stats["last_cleanup"] > 3600:  # toutes les heures
            self._cleanup_file_cache()
            self.stats["last_cleanup"] = now
        else:
            # Sauvegarde périodique moins fréquente (tous les 10 appels)
            if (self.stats["hits"] + self.stats["misses"]) % 10 == 0:
                self._save_file_cache()
    
    def _cleanup_file_cache(self):
        """Nettoie les entrées expirées du cache fichier."""
        now = time.time()
        expired_keys = [
            key for key, data in self.file_cache.items() 
            if data.get('expires_at', 0) < now
        ]
        
        for key in expired_keys:
            del self.file_cache[key]
        
        logger.info(f"Cache nettoyé: {len(expired_keys)} entrées expirées supprimées")
        self._save_file_cache()
    
    def get_stats(self) -> Dict[str, Any]:
        """Renvoie les statistiques d'utilisation du cache."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate": round(hit_rate, 2),
            "size": len(self.file_cache)
        }

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer une instance du cache
    maps_cache = MapsCache()
    
    # Exemple de mise en cache d'un temps de trajet
    maps_cache.set(
        "travel_time", 
        {"duration": 3600, "distance": 50000},
        origin="Paris", 
        destination="Lyon", 
        mode="driving"
    )
    
    # Récupérer depuis le cache
    result = maps_cache.get(
        "travel_time",
        origin="Paris", 
        destination="Lyon", 
        mode="driving"
    )
    print(f"Résultat mis en cache: {result}")
    
    # Afficher les statistiques
    print(f"Statistiques du cache: {maps_cache.get_stats()}")
