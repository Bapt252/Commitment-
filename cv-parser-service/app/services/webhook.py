# CV Parser Service - Service de callback webhook

import hmac
import hashlib
import json
import time
import logging
import random
from typing import Dict, Any, Optional
import requests

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

def generate_signature(payload: Dict[str, Any], secret: str) -> str:
    """Génère une signature HMAC-SHA256 pour un payload
    
    Args:
        payload: Données à signer
        secret: Secret partagé
        
    Returns:
        str: Signature hexadécimale
    """
    if not secret:
        return ""
        
    # Trier les clés pour une signature cohérente
    payload_str = json.dumps(payload, sort_keys=True)
    
    # Générer la signature HMAC-SHA256
    signature = hmac.new(
        secret.encode(),
        payload_str.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return signature

def send_webhook(job_id: str, url: str, data: Dict[str, Any], secret: str = "", 
                max_retries: int = 3, timeout: int = 10) -> bool:
    """Envoie une notification webhook avec signature HMAC
    
    Args:
        job_id: ID du job
        url: URL du webhook
        data: Données à envoyer
        secret: Secret partagé pour la signature
        max_retries: Nombre maximum de tentatives
        timeout: Timeout de la requête en secondes
        
    Returns:
        bool: True si succès, False sinon
    """
    if not url:
        logger.warning(f"Pas d'URL de webhook configurée pour le job {job_id}")
        return False
        
    # Paramètres par défaut depuis la configuration
    if max_retries == 3 and hasattr(settings, 'WEBHOOK_MAX_RETRIES'):
        max_retries = settings.WEBHOOK_MAX_RETRIES
        
    if timeout == 10 and hasattr(settings, 'WEBHOOK_TIMEOUT'):
        timeout = settings.WEBHOOK_TIMEOUT
    
    # Préparer le payload
    payload = {
        "job_id": job_id,
        "status": data.get("status", "unknown"),
        "timestamp": int(time.time()),
        "data": data
    }
    
    # Générer la signature si secret fourni
    signature = generate_signature(payload, secret)
    
    # Préparer les headers
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "CV-Parser-Service/1.0",
    }
    
    if signature:
        headers["X-Signature"] = signature
    
    # Envoyer avec retry et backoff exponentiel
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Webhook réussi pour le job {job_id}")
                return True
                
            logger.warning(
                f"Webhook échoué pour le job {job_id}: status {response.status_code}, "  
                f"attempt {attempt+1}/{max_retries}"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du webhook pour job {job_id}: {str(e)}")
        
        # Attente exponentielle entre les tentatives
        if attempt < max_retries - 1:
            # Backoff exponentiel: 2^attempt secondes avec jitter
            backoff = (2 ** attempt) + random.uniform(0, 1)  # Jitter pour éviter les tempêtes
            logger.info(f"Attente de {backoff:.2f}s avant la prochaine tentative de webhook")
            time.sleep(backoff)
    
    # Échec après toutes les tentatives
    logger.error(f"Webhook définitivement échoué pour job {job_id} après {max_retries} tentatives")
    return False
