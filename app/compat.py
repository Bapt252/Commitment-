"""
Module de compatibilité pour OpenAI 0.28.1

Ce module patche l'API OpenAI 0.28.1 pour assurer la compatibilité entre les différentes 
versions et gérer spécifiquement les problèmes liés au paramètre 'proxies'.
"""
import logging
import os
import sys
import functools

# Configuration du logging
logger = logging.getLogger(__name__)

def patch_openai():
    """
    Applique des patchs de compatibilité à la bibliothèque OpenAI
    pour assurer le fonctionnement avec la version 0.28.1
    """
    try:
        import openai
        logger.info(f"OpenAI version: {openai.__version__}")
        
        # 1. Gérer le paramètre 'proxies' qui n'est plus supporté dans le client
        if hasattr(openai, 'ChatCompletion'):
            # Version 0.28.1 qui a déjà ChatCompletion, mais patche la méthode create
            original_create = openai.ChatCompletion.create
            
            @functools.wraps(original_create)
            def patched_create_chat(*args, **kwargs):
                # Supprimer l'argument 'proxies' s'il est présent
                if 'proxies' in kwargs:
                    logger.warning("Removing 'proxies' argument incompatible with OpenAI v0.28.1")
                    kwargs.pop('proxies')
                
                # Traiter d'autres paramètres incompatibles potentiels
                if 'timeout' in kwargs and isinstance(kwargs['timeout'], (list, tuple)):
                    logger.warning("Converting tuple 'timeout' to float (using first value)")
                    kwargs['timeout'] = kwargs['timeout'][0]
                
                # Convertir les nouveaux noms de modèles si nécessaire
                if 'model' in kwargs:
                    model_mapping = {
                        'gpt-4o': 'gpt-4',
                        'gpt-4-turbo': 'gpt-4',
                        'gpt-3.5-turbo-0125': 'gpt-3.5-turbo'
                    }
                    if kwargs['model'] in model_mapping:
                        logger.warning(f"Converting model '{kwargs['model']}' to '{model_mapping[kwargs['model']]}'")
                        kwargs['model'] = model_mapping[kwargs['model']]
                
                return original_create(*args, **kwargs)
            
            # Remplacer la méthode originale
            openai.ChatCompletion.create = patched_create_chat
            logger.info("Patched openai.ChatCompletion.create to handle incompatible arguments")
            
        # 2. Compatibilité pour les versions plus récentes (rarement utile, mais au cas où)
        elif hasattr(openai, 'chat') and hasattr(openai.chat, 'completions'):
            logger.warning("Detected newer OpenAI version, creating ChatCompletion compatibility layer")
            
            class ChatCompletion:
                @staticmethod
                def create(*args, **kwargs):
                    # Supprimer l'argument 'proxies' s'il est présent
                    if 'proxies' in kwargs:
                        logger.warning("Removing 'proxies' argument")
                        kwargs.pop('proxies')
                    
                    # Autres adaptations potentielles pour la rétrocompatibilité
                    return openai.chat.completions.create(*args, **kwargs)
            
            # Ajouter la classe au module openai
            openai.ChatCompletion = ChatCompletion
            logger.info("Added ChatCompletion compatibility class to OpenAI")
        
        # 3. Configuration de l'API key à partir des variables d'environnement
        if not openai.api_key:
            for env_var in ['OPENAI_API_KEY', 'OPENAI']:
                if env_var in os.environ:
                    openai.api_key = os.environ[env_var]
                    logger.info(f"Set OpenAI API key from {env_var}")
                    break
        
        logger.info("OpenAI compatibility patches applied successfully")
        return True
    
    except ImportError:
        logger.warning("OpenAI not installed, skipping patches")
        return False
    except Exception as e:
        logger.error(f"Error applying OpenAI patches: {e}")
        return False

# Appliquer les patchs automatiquement lors de l'import du module
patch_success = patch_openai()
