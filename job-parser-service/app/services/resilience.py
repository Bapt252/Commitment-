"""
Service de résilience pour les appels à l'API OpenAI
Implémente des mécanismes de circuit breaker et de retry
"""

import logging
import time
import random
from typing import Dict, Any, Optional
import traceback

from app.core.config import settings
import openai

# Setup logging
logger = logging.getLogger(__name__)

# État du circuit breaker
CIRCUIT_STATE = {
    "is_open": False,
    "failure_count": 0,
    "last_failure_time": 0,
    "recovery_timeout": 30,  # Temps en secondes avant de réessayer après ouverture du circuit
    "failure_threshold": 3   # Nombre d'échecs consécutifs avant d'ouvrir le circuit
}

def resilient_openai_call(
    prompt: str, 
    model: Optional[str] = None,
    temperature: float = 0.1, 
    max_tokens: int = 4000,
    retry_count: int = 3,
    base_wait_time: float = 2.0
) -> str:
    """
    Effectue un appel résilient à l'API OpenAI avec circuit breaker et retry
    
    Args:
        prompt: Le prompt à envoyer à l'API
        model: Le modèle à utiliser (par défaut: settings.OPENAI_MODEL)
        temperature: Paramètre de température (défaut: 0.1)
        max_tokens: Nombre maximum de tokens en réponse (défaut: 4000)
        retry_count: Nombre de tentatives en cas d'échec (défaut: 3)
        base_wait_time: Temps d'attente de base en secondes entre les tentatives (défaut: 2.0)
        
    Returns:
        str: La réponse générée par l'API
        
    Raises:
        Exception: Si toutes les tentatives échouent ou si le circuit est ouvert
    """
    # Vérifier l'état du circuit breaker
    if CIRCUIT_STATE["is_open"]:
        current_time = time.time()
        if current_time - CIRCUIT_STATE["last_failure_time"] < CIRCUIT_STATE["recovery_timeout"]:
            logger.warning(f"Circuit breaker ouvert, API temporairement indisponible. Réessayez dans {CIRCUIT_STATE['recovery_timeout'] - (current_time - CIRCUIT_STATE['last_failure_time']):.1f}s")
            raise Exception("Service temporairement indisponible (circuit breaker ouvert)")
        else:
            # Réinitialiser l'état semi-ouvert pour tenter une nouvelle connexion
            logger.info("Tentative de refermer le circuit breaker après timeout")
            CIRCUIT_STATE["is_open"] = False
            CIRCUIT_STATE["failure_count"] = 0
    
    # Modèle à utiliser (priorité à celui passé en paramètre, sinon celui des settings)
    model_to_use = model or settings.OPENAI_MODEL
    
    # Initialiser les API keys
    openai.api_key = settings.OPENAI_API_KEY
    
    attempt = 0
    last_exception = None
    
    while attempt < retry_count:
        try:
            # Logs pour le debugging
            logger.info(f"Appel à l'API OpenAI (tentative {attempt+1}/{retry_count})")
            logger.debug(f"Modèle: {model_to_use}, Temperature: {temperature}, Max tokens: {max_tokens}")
            logger.debug(f"Longueur du prompt: {len(prompt)} caractères")
            
            # Effectuer l'appel à l'API
            response = openai.chat.completions.create(
                model=model_to_use,
                messages=[
                    {"role": "system", "content": "Tu es un expert en analyse de documents et extraction de données."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Extraire le texte de la réponse
            response_text = response.choices[0].message.content.strip()
            
            # Réinitialiser le compteur d'échecs si l'appel réussit
            CIRCUIT_STATE["failure_count"] = 0
            
            logger.info(f"Appel à l'API OpenAI réussi, réponse reçue ({len(response_text)} caractères)")
            return response_text
            
        except Exception as e:
            attempt += 1
            last_exception = e
            
            # Incrémenter le compteur d'échecs
            CIRCUIT_STATE["failure_count"] += 1
            CIRCUIT_STATE["last_failure_time"] = time.time()
            
            # Vérifier si le seuil d'échecs est atteint pour ouvrir le circuit
            if CIRCUIT_STATE["failure_count"] >= CIRCUIT_STATE["failure_threshold"]:
                CIRCUIT_STATE["is_open"] = True
                logger.error(f"Circuit breaker ouvert après {CIRCUIT_STATE['failure_count']} échecs consécutifs")
                
                # Si le circuit est ouvert, on arrête immédiatement les tentatives
                raise Exception(f"Circuit breaker ouvert après {CIRCUIT_STATE['failure_count']} échecs. Erreur: {str(e)}")
            
            # Attente exponentielle (backoff) entre les tentatives
            wait_time = base_wait_time * (2 ** (attempt - 1)) + random.uniform(0, 1)
            logger.warning(f"Échec de l'appel à l'API OpenAI: {str(e)}. Nouvelle tentative dans {wait_time:.2f}s ({attempt}/{retry_count})")
            logger.debug(f"Stacktrace: {traceback.format_exc()}")
            
            # Attendre avant la prochaine tentative
            time.sleep(wait_time)
    
    # Si toutes les tentatives ont échoué
    logger.error(f"Échec de toutes les tentatives d'appel à l'API OpenAI: {str(last_exception)}")
    raise last_exception or Exception("Erreur inconnue lors de l'appel à l'API OpenAI")
