"""
Point d'entrée principal du service de matching.
Lance le serveur FastAPI avec uvicorn.
"""
# Module de compatibilité pour l'API OpenAI directement intégré
import logging
import os
import sys

# Configuration de la compatibilité OpenAI
try:
    import openai
    
    # Déterminer la version d'OpenAI
    openai_version = getattr(openai, "__version__", "0.0.0")
    print(f"Version d'OpenAI détectée : {openai_version}")
    
    # Compatibilité pour les versions >= 1.0.0
    if openai_version.startswith(("1.", "2.")):
        print("Utilisation de la nouvelle API OpenAI (v1.x/v2.x)")
        
        # Configurer l'API key
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if openai_api_key:
            openai.api_key = openai_api_key
            
        # Configurer les méthodes de compatibilité
        if hasattr(openai, "Completion") and hasattr(openai.Completion, "create"):
            original_completion_create = openai.Completion.create
            
            # Wrapper pour la compatibilité
            def completion_create_compat(*args, **kwargs):
                if "engine" in kwargs and "model" not in kwargs:
                    kwargs["model"] = kwargs.pop("engine")
                return original_completion_create(*args, **kwargs)
            
            # Remplacer la méthode originale
            openai.Completion.create = completion_create_compat
        
    else:
        print("Utilisation de l'ancienne API OpenAI (v0.x)")
        
except ImportError:
    print("Module OpenAI non trouvé. La compatibilité OpenAI ne sera pas disponible.")
    
except Exception as e:
    print(f"Erreur lors de la configuration de la compatibilité OpenAI: {str(e)}")

# Imports normaux
import uvicorn
import logging
from app.core.config import settings
from app.core.logging import setup_logging

if __name__ == "__main__":
    # Configuration du logging
    setup_logging()
    logger = logging.getLogger("matching-service")
    
    logger.info(f"Démarrage du serveur FastAPI sur le port {settings.PORT}")
    
    # Démarrage du serveur FastAPI
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
