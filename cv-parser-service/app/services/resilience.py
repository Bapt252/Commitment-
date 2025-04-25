# CV Parser Service - Service de résilience pour les appels API

import time
import random
import logging
from functools import wraps
from typing import Dict, Any, Optional, Callable
import openai

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Configurer la clé API OpenAI
openai.api_key = settings.OPENAI_API_KEY

# État du circuit breaker
class CircuitBreakerState:
    def __init__(self):
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF-OPEN
        self.threshold = settings.CIRCUIT_BREAKER_THRESHOLD
        self.timeout = settings.CIRCUIT_BREAKER_TIMEOUT  # secondes
        self.successes_needed = 2
        self.success_count = 0

circuit_state = CircuitBreakerState()

def circuit_breaker(func):
    """Décorateur de circuit breaker pour protéger contre les appels à des services défaillants"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Désactiver le circuit breaker si configuré ainsi
        if not settings.CIRCUIT_BREAKER_ENABLED:
            return func(*args, **kwargs)
            
        current_time = time.time()
        
        # Circuit est OUVERT (en échec)
        if circuit_state.state == "OPEN":
            # Vérifier si le temps d'attente est passé
            if current_time - circuit_state.last_failure_time > circuit_state.timeout:
                logger.info("Circuit breaker passant de OPEN à HALF-OPEN")
                circuit_state.state = "HALF-OPEN"
                circuit_state.success_count = 0
            else:
                # Circuit toujours ouvert, rejeter immédiatement
                wait_time = circuit_state.timeout - (current_time - circuit_state.last_failure_time)
                logger.warning(f"Circuit ouvert, appel rejeté. Réessayez dans {wait_time:.1f}s")
                raise Exception(f"Service temporairement indisponible (circuit ouvert). Réessayez dans {int(wait_time)}s")
        
        try:
            result = func(*args, **kwargs)
            
            # Succès, réinitialiser en mode HALF-OPEN ou fermer en mode CLOSED
            if circuit_state.state == "HALF-OPEN":
                circuit_state.success_count += 1
                if circuit_state.success_count >= circuit_state.successes_needed:
                    logger.info("Circuit breaker passant de HALF-OPEN à CLOSED")
                    circuit_state.state = "CLOSED"
                    circuit_state.failure_count = 0
            elif circuit_state.state == "CLOSED":
                # Tout va bien, réinitialiser les compteurs par sécurité
                circuit_state.failure_count = 0
                
            return result
            
        except Exception as e:
            # Échec, incrémenter compteur ou ouvrir le circuit
            circuit_state.failure_count += 1
            circuit_state.last_failure_time = current_time
            
            if circuit_state.state == "CLOSED" and circuit_state.failure_count >= circuit_state.threshold:
                logger.error(f"Seuil d'erreurs atteint ({circuit_state.threshold}), circuit passant à OPEN")
                circuit_state.state = "OPEN"
            elif circuit_state.state == "HALF-OPEN":
                logger.error("Echec en mode HALF-OPEN, revenant à l'état OPEN")
                circuit_state.state = "OPEN"
                
            raise e
            
    return wrapper

def exponential_backoff(attempt: int, base: float = 1.0, max_backoff: float = 60.0, jitter: bool = True) -> float:
    """Calcule le temps d'attente pour un backoff exponentiel
    
    Args:
        attempt: Numéro de la tentative (commence à 0)
        base: Temps de base en secondes
        max_backoff: Temps d'attente maximum en secondes
        jitter: Ajouter du bruit aléatoire
        
    Returns:
        float: Temps d'attente en secondes
    """
    # Formule: base * 2^attempt
    backoff = base * (2 ** attempt)
    
    # Appliquer la limite maximum
    backoff = min(backoff, max_backoff)
    
    # Ajouter du jitter (± 10%)
    if jitter:
        backoff = backoff * (0.9 + random.random() * 0.2)  # Entre 90% et 110%
    
    return backoff

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0,
                       retryable_errors = (openai.error.APIError, openai.error.APIConnectionError, openai.error.RateLimitError)):
    """Décorateur de réessai avec backoff exponentiel"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_error = None
            
            while attempt <= max_retries:
                try:
                    return func(*args, **kwargs)
                except retryable_errors as e:
                    attempt += 1
                    last_error = e
                    
                    if attempt > max_retries:
                        logger.error(f"Echec après {max_retries} tentatives: {str(e)}")
                        raise
                    
                    # Calculer le temps d'attente avec backoff exponentiel
                    delay = exponential_backoff(
                        attempt=attempt-1,  # -1 car on compte à partir de 0
                        base=base_delay,
                        max_backoff=max_delay,
                        jitter=True
                    )
                    
                    # Déterminer le message selon le type d'erreur
                    if isinstance(e, openai.error.RateLimitError):
                        logger.warning(f"Rate limit atteint, attente de {delay:.2f}s avant réessai {attempt}/{max_retries}")
                    elif isinstance(e, openai.error.APIConnectionError):
                        logger.warning(f"Erreur de connexion, attente de {delay:.2f}s avant réessai {attempt}/{max_retries}")
                    else:
                        logger.warning(f"Erreur API, attente de {delay:.2f}s avant réessai {attempt}/{max_retries}: {str(e)}")
                    
                    time.sleep(delay)
                    
                except Exception as e:
                    # Erreur non récupérable
                    logger.error(f"Erreur non récupérable: {str(e)}")
                    raise
            
            # Ne devrait jamais arriver, mais par sécurité
            raise last_error or Exception(f"Echec après {max_retries} tentatives")
            
        return wrapper
    return decorator

# Utilisation combinée du circuit breaker et du retry avec backoff
@circuit_breaker
@retry_with_backoff(max_retries=3, base_delay=2.0, max_delay=30.0)
def resilient_openai_call(prompt: str, model: str = "gpt-4o-mini", temperature: float = 0.1, max_tokens: int = 4000) -> str:
    """Appel résilient à l'API OpenAI avec circuit breaker et retry
    
    Args:
        prompt: Prompt à envoyer à OpenAI
        model: Modèle GPT à utiliser
        temperature: Température (créativité)
        max_tokens: Nombre maximum de tokens en réponse
        
    Returns:
        str: Réponse du modèle
    """
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "Tu es un assistant spécialisé dans l'extraction d'informations à partir de CV."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except openai.error.RateLimitError as e:
        logger.warning(f"Rate limit atteint: {str(e)}")
        raise
    except openai.error.APIConnectionError as e:
        logger.error(f"Erreur de connexion OpenAI: {str(e)}")
        raise
    except openai.error.APIError as e:
        logger.error(f"Erreur API OpenAI: {str(e)}")
        raise
    except Exception as e:
        logger.exception(f"Erreur inattendue lors de l'appel OpenAI: {str(e)}")
        raise
