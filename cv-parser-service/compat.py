"""
Module de compatibilité pour assurer le fonctionnement avec OpenAI 0.28.1

Ce module applique des patches pour maintenir la compatibilité entre les
différentes versions de l'API OpenAI. Il s'assure que le code écrit pour
des versions plus récentes fonctionne avec la version 0.28.1.
"""
import sys
import logging

logger = logging.getLogger(__name__)

def patch_openai():
    """
    Patch pour assurer la compatibilité avec openai 0.28.1
    Crée des classes de compatibilité si nécessaire
    """
    try:
        import openai
        
        logger.info(f"OpenAI version: {openai.__version__}")
        
        # Pour OpenAI 0.28.1 - ajouter ChatCompletion si manquant
        if hasattr(openai, 'chat') and not hasattr(openai, 'ChatCompletion'):
            logger.info("Patching OpenAI to add ChatCompletion compatibility")
            
            class ChatCompletion:
                @staticmethod
                def create(*args, **kwargs):
                    # Utiliser l'API maintenant en chat.completions
                    return openai.chat.completions.create(*args, **kwargs)
            
            # Ajouter la classe à openai
            openai.ChatCompletion = ChatCompletion
            logger.info("OpenAI patched successfully")
            
        # Pour versions plus anciennes - ajouter chat.completions si manquant
        if not hasattr(openai, 'chat') and hasattr(openai, 'ChatCompletion'):
            logger.info("OpenAI in 0.28.1 mode - no patching needed")
        
    except ImportError:
        logger.warning("OpenAI package not found - skipping compatibility patching")
    except Exception as e:
        logger.error(f"Error patching OpenAI: {e}")

# Appliquer les patchs au chargement du module
patch_openai()
