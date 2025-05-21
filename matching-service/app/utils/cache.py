"""
Module d'utilitaires pour la mise en cache des résultats.

Ce module fournit des fonctions pour mettre en cache des résultats
de calculs coûteux, afin d'éviter de les recalculer à chaque fois.
"""

import functools
import time
import hashlib
import json
import logging
from typing import Any, Callable, Dict, Optional, Tuple

# Configuration du logger
logger = logging.getLogger(__name__)

# Cache en mémoire simple (pour les environnements sans Redis)
_memory_cache = {}

def cache_key(func_name: str, args: Tuple, kwargs: Dict) -> str:
    """
    Génère une clé de cache unique basée sur la fonction et ses arguments.
    
    Args:
        func_name: Nom de la fonction
        args: Arguments positionnels
        kwargs: Arguments nommés
        
    Returns:
        Clé de cache
    """
    # Convertir les arguments en chaîne JSON pour la sérialisation
    serialized = json.dumps({
        'func': func_name,
        'args': args,
        'kwargs': {k: v for k, v in kwargs.items() if isinstance(v, (str, int, float, bool, list, dict, tuple))}
    }, sort_keys=True)
    
    # Générer un hash pour créer une clé courte mais unique
    return hashlib.md5(serialized.encode()).hexdigest()

def cache_result(ttl: int = 300):
    """
    Décorateur pour mettre en cache les résultats d'une fonction.
    
    Args:
        ttl: Durée de vie du cache en secondes
    
    Returns:
        Fonction décorée
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Générer la clé de cache
            key = cache_key(func.__name__, args, kwargs)
            
            # Vérifier si le résultat est déjà en cache
            if key in _memory_cache:
                entry = _memory_cache[key]
                # Vérifier si l'entrée n'a pas expiré
                if time.time() < entry['expires']:
                    logger.debug(f"Résultat trouvé en cache pour {func.__name__}")
                    return entry['result']
            
            # Exécuter la fonction et mettre en cache le résultat
            result = func(*args, **kwargs)
            
            # Stocker le résultat en cache avec un timestamp d'expiration
            _memory_cache[key] = {
                'result': result,
                'expires': time.time() + ttl
            }
            
            return result
        return wrapper
    return decorator

def clear_cache():
    """Vide le cache en mémoire."""
    global _memory_cache
    _memory_cache = {}
    logger.info("Cache en mémoire vidé")

def get_cached_value(key: str) -> Optional[Any]:
    """
    Récupère une valeur depuis le cache.
    
    Args:
        key: Clé du cache
        
    Returns:
        Valeur en cache ou None si la clé n'existe pas ou a expiré
    """
    if key in _memory_cache:
        entry = _memory_cache[key]
        if time.time() < entry['expires']:
            return entry['result']
    return None

def set_cached_value(key: str, value: Any, ttl: int = 300):
    """
    Stocke une valeur dans le cache.
    
    Args:
        key: Clé du cache
        value: Valeur à stocker
        ttl: Durée de vie en secondes
    """
    _memory_cache[key] = {
        'result': value,
        'expires': time.time() + ttl
    }
