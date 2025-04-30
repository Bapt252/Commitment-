"""
Module de compatibilité pour assurer le fonctionnement avec OpenAI 0.28.1

Ce module applique des patches pour maintenir la compatibilité entre les
différentes versions de l'API OpenAI. Il s'assure que le code écrit pour
des versions plus récentes fonctionne avec la version 0.28.1.
"""
import sys
import logging
import types

logger = logging.getLogger(__name__)

def patch_openai():
    """
    Patch pour assurer la compatibilité avec openai 0.28.1
    Crée des classes de compatibilité si nécessaire et gère les arguments problématiques
    """
    try:
        import openai
        
        logger.info(f"OpenAI version: {openai.__version__}")
        
        # Patch pour la compatibilité avec les versions plus récentes qui utilisent Client
        if not hasattr(openai, 'ChatCompletion') and hasattr(openai, 'chat'):
            logger.info("Patching OpenAI to add ChatCompletion compatibility")
            
            class ChatCompletion:
                @staticmethod
                def create(*args, **kwargs):
                    # Supprimer les arguments incompatibles
                    if 'proxies' in kwargs:
                        logger.warning("Removing 'proxies' argument incompatible with OpenAI v0.28.1")
                        del kwargs['proxies']
                    
                    # Convertir les nouveaux formats en anciens formats si nécessaire
                    if 'model' in kwargs and kwargs['model'] == 'gpt-4o':
                        logger.info("Converting 'gpt-4o' to 'gpt-4' for compatibility")
                        kwargs['model'] = 'gpt-4'
                    
                    # Si le code utilise la nouvelle API, rediriger vers l'ancienne
                    return openai.Completion.create(*args, **kwargs) if hasattr(openai, 'Completion') else None
            
            # Ajouter la classe au module openai
            openai.ChatCompletion = ChatCompletion
            logger.info("OpenAI patched successfully")
            
        # Si le code utilise déjà la version 0.28.1, pas besoin de patch
        elif hasattr(openai, 'ChatCompletion'):
            logger.info("OpenAI already in v0.28.1 mode - no patching needed")
            
            # Patch la méthode create si nécessaire pour gérer les arguments incompatibles
            original_create = openai.ChatCompletion.create
            
            def patched_create(*args, **kwargs):
                if 'proxies' in kwargs:
                    logger.warning("Removing 'proxies' argument incompatible with OpenAI v0.28.1")
                    del kwargs['proxies']
                return original_create(*args, **kwargs)
            
            # Remplacer la méthode d'origine par notre version patchée
            openai.ChatCompletion.create = patched_create
            
        # Assurer que l'API est correctement configurée
        if hasattr(openai, 'api_key') and not openai.api_key and 'OPENAI' in os.environ:
            openai.api_key = os.environ.get('OPENAI')
            logger.info("Set OpenAI API key from environment variable")
            
    except ImportError:
        logger.warning("OpenAI package not found - skipping compatibility patching")
    except Exception as e:
        logger.error(f"Error patching OpenAI: {e}")

# Importer os pour gérer les variables d'environnement
import os

# Appliquer les patchs au chargement du module
patch_openai()

logger.info("OpenAI compatibility patches applied")
