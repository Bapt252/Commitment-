# Service de résilience pour les appels API externes

import logging
import time
from typing import Dict, Any, Optional, List, Callable
import os
import json
import traceback
import time

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import pybreaker

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Configuration du circuit breaker
circuit_breaker = pybreaker.CircuitBreaker(
    fail_max=5,
    reset_timeout=30
)

def resilient_openai_call(
    prompt: str,
    model: str = settings.OPENAI_MODEL,
    temperature: float = 0.1,
    max_tokens: int = 4000
) -> str:
    """Appel résilient à l'API OpenAI avec circuit breaker et retry
    
    Args:
        prompt: Prompt à envoyer à l'API
        model: Modèle à utiliser
        temperature: Température pour la génération
        max_tokens: Nombre maximal de tokens pour la réponse
        
    Returns:
        str: Réponse de l'API OpenAI
    """
    
    # Fonction d'appel à l'API OpenAI
    def _call_openai() -> str:
        try:
            # Import déplacé à l'intérieur de la fonction pour permettre le mock en test
            import openai
            
            # S'assurer que la clé API est configurée
            if not openai.api_key and settings.OPENAI:
                openai.api_key = settings.OPENAI
            
            if not openai.api_key:
                raise ValueError("Clé API OpenAI non configurée")
            
            # Appel à l'API avec un système de messages pour plus de contrôle
            start_time = time.time()
            logger.info(f"Appel à OpenAI avec le modèle {model} et {len(prompt)} caractères")
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Tu es un expert en analyse de documents qui extrait avec précision les informations demandées."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                n=1,
                stop=None
            )
            
            # Extraction de la réponse
            response_text = response.choices[0].message.content.strip()
            
            # Logging du temps d'exécution et du coût approximatif
            duration = time.time() - start_time
            logger.info(f"Réponse d'OpenAI reçue en {duration:.2f} secondes")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à OpenAI: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    
    # Fonction de retry avec tenacity
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def _retry_call_openai() -> str:
        return _call_openai()
    
    # Utiliser le circuit breaker si activé, sinon appel direct avec retry
    if settings.CIRCUIT_BREAKER_ENABLED:
        try:
            return circuit_breaker(_retry_call_openai)
        except Exception as e:
            logger.error(f"Circuit ouvert ou erreur après tous les retries: {str(e)}")
            # Dernier recours: message d'erreur formaté comme une réponse vide
            return json.dumps({
                "error": f"Erreur de service OpenAI: {str(e)}",
                "message": "Le service est temporairement indisponible. Veuillez réessayer plus tard."
            })
    else:
        try:
            return _retry_call_openai()
        except Exception as e:
            logger.error(f"Erreur après tous les retries: {str(e)}")
            return json.dumps({
                "error": f"Erreur de service OpenAI: {str(e)}",
                "message": "Le service est temporairement indisponible. Veuillez réessayer plus tard."
            })
