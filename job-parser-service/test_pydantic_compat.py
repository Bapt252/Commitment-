#!/usr/bin/env python3
"""
Script de test pour vérifier la compatibilité avec les différentes versions de Pydantic.
Permet de valider que le module pydantic_compat fonctionne correctement.
"""

import os
import sys
import logging
import importlib
from typing import Optional

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def check_pydantic_version():
    """Vérifie la version de Pydantic installée"""
    try:
        import pydantic
        version = pydantic.__version__
        logger.info(f"Version de Pydantic installée: {version}")
        is_v2 = version.startswith('2')
        logger.info(f"Pydantic v2: {'Oui' if is_v2 else 'Non'}")
        return is_v2, version
    except ImportError:
        logger.error("Pydantic n'est pas installé")
        return False, None

def check_pydantic_settings():
    """Vérifie si pydantic_settings est disponible"""
    try:
        import pydantic_settings
        logger.info(f"pydantic_settings est installé (version: {pydantic_settings.__version__})")
        return True
    except ImportError:
        logger.info("pydantic_settings n'est pas installé")
        return False

def test_compat_module():
    """Teste le module de compatibilité pydantic_compat"""
    logger.info("Test du module de compatibilité pydantic_compat")
    
    try:
        from pydantic_compat import BaseSettings
        logger.info("Module pydantic_compat importé avec succès")
        
        # Créer une classe de test
        class TestSettings(BaseSettings):
            test_value: str = "default"
            optional_value: Optional[int] = None
            
            class Config:
                env_prefix = "TEST_"
        
        # Instancier la classe
        settings = TestSettings()
        logger.info(f"Instance de TestSettings créée: {settings.dict() if hasattr(settings, 'dict') else settings.model_dump()}")
        
        # Tester avec une variable d'environnement
        os.environ["TEST_TEST_VALUE"] = "from_env"
        settings = TestSettings()
        
        # Vérifier si la valeur a été chargée depuis l'environnement
        env_value = settings.test_value
        logger.info(f"Valeur depuis l'environnement: {env_value}")
        assert env_value == "from_env", "La valeur n'a pas été chargée depuis l'environnement"
        
        logger.info("✅ Le module pydantic_compat fonctionne correctement!")
        return True
        
    except ImportError as e:
        logger.error(f"Impossible d'importer pydantic_compat: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur lors du test du module pydantic_compat: {e}")
        return False

def main():
    """Fonction principale"""
    logger.info("Démarrage des tests de compatibilité Pydantic")
    
    # Vérifier la version de Pydantic
    is_v2, version = check_pydantic_version()
    
    # Vérifier pydantic_settings
    has_settings = check_pydantic_settings()
    
    # Tester le module de compatibilité
    compat_works = test_compat_module()
    
    # Résumé
    logger.info("\n=== RÉSUMÉ ===")
    logger.info(f"Pydantic version: {'v2 (' + version + ')' if is_v2 else 'v1 (' + str(version) + ')'}")
    logger.info(f"pydantic_settings: {'Disponible' if has_settings else 'Non disponible'}")
    logger.info(f"Module de compatibilité: {'Fonctionnel' if compat_works else 'Non fonctionnel'}")
    
    # Statut global
    if compat_works:
        logger.info("✅ Configuration compatible")
        return 0
    else:
        logger.error("❌ Configuration incompatible")
        return 1

if __name__ == "__main__":
    sys.exit(main())
