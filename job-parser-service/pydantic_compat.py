"""
Module de compatibilité pour Pydantic v1 et v2.
Permet d'utiliser le code avec les deux versions de Pydantic.
"""
import sys
import importlib.util
import logging

logger = logging.getLogger(__name__)

def is_pydantic_v2():
    """Vérifie si Pydantic v2 est installé"""
    import pydantic
    return pydantic.__version__.startswith('2')

# Classes et fonctions compatibles avec les deux versions
def get_base_settings():
    """Retourne la classe BaseSettings appropriée selon la version de Pydantic"""
    if is_pydantic_v2():
        try:
            from pydantic_settings import BaseSettings
            logger.info("Utilisation de BaseSettings depuis pydantic_settings (Pydantic v2)")
            return BaseSettings
        except ImportError:
            logger.warning("pydantic_settings non trouvé, utilisation de la classe BaseSettings de Pydantic v1")
            from pydantic import BaseSettings
            return BaseSettings
    else:
        from pydantic import BaseSettings
        logger.info("Utilisation de BaseSettings depuis pydantic (Pydantic v1)")
        return BaseSettings

# Exporter les classes et fonctions
BaseSettings = get_base_settings()
