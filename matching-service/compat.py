"""
Module de compatibilité pour l'API OpenAI
-----------------------------------------
Assure la compatibilité entre différentes versions de l'API OpenAI.

Auteur: Claude/Anthropic
Date: 14/05/2025
"""

import logging
import os
import sys
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Configuration de la compatibilité OpenAI
try:
    import openai
    
    # Déterminer la version d'OpenAI
    openai_version = getattr(openai, "__version__", "0.0.0")
    logger.info(f"Version d'OpenAI détectée : {openai_version}")
    
    # Compatibilité pour les versions >= 1.0.0
    if openai_version.startswith(("1.", "2.")):
        logger.info("Utilisation de la nouvelle API OpenAI (v1.x/v2.x)")
        
        # Configurer l'API key
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if openai_api_key:
            openai.api_key = openai_api_key
            
        # Configurer les méthodes de compatibilité
        original_completion_create = openai.Completion.create
        
        # Wrapper pour la compatibilité
        def completion_create_compat(*args, **kwargs):
            if "engine" in kwargs and "model" not in kwargs:
                kwargs["model"] = kwargs.pop("engine")
            return original_completion_create(*args, **kwargs)
        
        # Remplacer la méthode originale
        openai.Completion.create = completion_create_compat
        
    else:
        logger.info("Utilisation de l'ancienne API OpenAI (v0.x)")
        
        # Pas de modifications nécessaires pour la compatibilité
        
except ImportError:
    logger.warning("Module OpenAI non trouvé. La compatibilité OpenAI ne sera pas disponible.")
    
except Exception as e:
    logger.error(f"Erreur lors de la configuration de la compatibilité OpenAI: {str(e)}", exc_info=True)
