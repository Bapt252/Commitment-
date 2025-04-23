import os
import redis
import json
import functools
from typing import Any, Optional, Callable, TypeVar, cast

# Type générique pour la valeur de retour de la fonction mise en cache
T = TypeVar('T')

def get_redis_client():
    """Obtient un client Redis configuré avec les paramètres d'environnement"""
    host = os.environ.get("REDIS_HOST", "redis")
    port = int(os.environ.get("REDIS_PORT", "6379"))
    db = int(os.environ.get("REDIS_DB", "0"))
    password = os.environ.get("REDIS_PASSWORD", None)
    
    return redis.Redis(
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=True
    )

def cache(expire: int = 300, prefix: str = ""):
    """Décorateur pour mettre en cache les résultats de fonction dans Redis
    
    Args:
        expire: Durée en secondes avant expiration du cache (défaut: 300s)
        prefix: Préfixe pour la clé de cache (généralement le nom du service)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Connexion Redis
            redis_client = get_redis_client()
            
            # Générer une clé basée sur la fonction et ses arguments
            cache_key = f"{prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Essayer de récupérer la valeur depuis le cache
            cached_value = redis_client.get(cache_key)
            if cached_value:
                try:
                    return cast(T, json.loads(cached_value))
                except (json.JSONDecodeError, TypeError):
                    pass  # En cas d'erreur, continuer et recalculer la valeur
            
            # Exécuter la fonction originale
            result = func(*args, **kwargs)
            
            # Mettre en cache le résultat
            try:
                redis_client.setex(cache_key, expire, json.dumps(result))
            except (TypeError, json.JSONDecodeError):
                # Certains objets ne peuvent pas être sérialisés en JSON
                pass
            
            return result
        return wrapper
    return decorator

def invalidate_cache(pattern: str):
    """Invalide toutes les clés de cache correspondant au motif"""
    redis_client = get_redis_client()
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)
        return len(keys)
    return 0

def store_object(key: str, data: Any, expire: Optional[int] = None):
    """Stocke un objet sérialisable dans Redis"""
    redis_client = get_redis_client()
    serialized = json.dumps(data)
    if expire:
        redis_client.setex(key, expire, serialized)
    else:
        redis_client.set(key, serialized)

def get_object(key: str) -> Optional[Any]:
    """Récupère un objet depuis Redis"""
    redis_client = get_redis_client()
    data = redis_client.get(key)
    if data:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None
    return None