"""
Utilitaires pour la résilience des services.
Implémente le circuit breaker pattern et les mécanismes de retry.
"""
import time
import logging
import functools
import random
from typing import Callable, Any, Optional, Dict, List

logger = logging.getLogger(__name__)

class CircuitBreaker:
    """
    Implémentation du pattern Circuit Breaker
    
    Empêche les appels répétés à des services défaillants et implémente
    une récupération automatique après un délai.
    """
    
    states = {
        'CLOSED': 'CLOSED',       # Circuit fermé (normal)
        'OPEN': 'OPEN',           # Circuit ouvert (échecs détectés)
        'HALF_OPEN': 'HALF_OPEN'  # Circuit en test de récupération
    }
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30, name: str = 'default'):
        """
        Initialise le circuit breaker
        
        Args:
            failure_threshold: Nombre d'échecs avant ouverture du circuit
            recovery_timeout: Délai en secondes avant tentative de récupération
            name: Nom du circuit pour l'identification dans les logs
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        self.state = self.states['CLOSED']
        self.failure_count = 0
        self.last_failure_time = 0
        
    def __enter__(self):
        """
        Vérification de l'état au début du bloc with
        Lève une exception si le circuit est ouvert
        """
        if self.state == self.states['OPEN']:
            # Vérifier si le délai de récupération est écoulé
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                logger.info(f"Circuit {self.name} passe de OPEN à HALF_OPEN")
                self.state = self.states['HALF_OPEN']
            else:
                # Toujours ouvert, rejeter l'appel
                logger.warning(f"Circuit {self.name} est OPEN, appel rejeté")
                raise CircuitBreakerError(f"Circuit {self.name} est ouvert")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Gestion de l'état à la fin du bloc with
        Met à jour le compteur d'échecs et l'état du circuit
        """
        if exc_type is not None:
            # L'appel a échoué
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == self.states['HALF_OPEN'] or self.failure_count >= self.failure_threshold:
                logger.warning(f"Circuit {self.name} passe à OPEN suite à un échec")
                self.state = self.states['OPEN']
                
            return False  # Relève l'exception
        else:
            # L'appel a réussi
            if self.state == self.states['HALF_OPEN']:
                logger.info(f"Circuit {self.name} passe de HALF_OPEN à CLOSED")
                self.state = self.states['CLOSED']
                self.failure_count = 0
            
            return True

class CircuitBreakerError(Exception):
    """Exception levée lorsque le circuit breaker est ouvert"""
    pass

def retry_with_backoff(max_retries: int = 3, delay: int = 1, backoff: int = 2, 
                      exceptions: tuple = (Exception,), logger_name: str = None):
    """
    Décorateur pour les retries avec backoff exponentiel
    
    Args:
        max_retries: Nombre maximum de tentatives
        delay: Délai initial en secondes
        backoff: Multiplicateur de backoff
        exceptions: Tuple d'exceptions à capturer
        logger_name: Nom du logger
        
    Returns:
        Callable: Fonction décorée
    """
    retry_logger = logging.getLogger(logger_name or __name__)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mtries, mdelay = max_retries, delay
            
            while mtries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    msg = f"{str(e)}, nouvelle tentative dans {mdelay} secondes..."
                    retry_logger.warning(msg)
                    
                    # Ajout de jitter pour éviter le problème du "thundering herd"
                    jitter = random.uniform(0, 0.3) * mdelay
                    time.sleep(mdelay + jitter)
                    
                    mtries -= 1
                    mdelay *= backoff
            
            # Dernière tentative
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator
