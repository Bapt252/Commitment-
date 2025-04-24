"""
Service pour la gestion des notifications, notamment les webhooks.
"""
import requests
import logging
import hmac
import hashlib
import json
import time
from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.resilience import retry_with_backoff

logger = logging.getLogger(__name__)

class NotificationService:
    """Service pour la gestion des notifications telles que les webhooks"""
    
    def __init__(self):
        self.webhook_secret = settings.WEBHOOK_SECRET
    
    def _generate_signature(self, payload: Dict[str, Any]) -> str:
        """
        Génère une signature HMAC pour le payload du webhook
        
        Args:
            payload: Payload du webhook
            
        Returns:
            str: Signature HMAC
        """
        payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        return hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
    
    @retry_with_backoff(
        max_retries=settings.WEBHOOK_RETRY_COUNT,
        delay=settings.WEBHOOK_RETRY_DELAY,
        exceptions=(requests.RequestException,)
    )
    def send_webhook(self, webhook_url: str, payload: Dict[str, Any]) -> bool:
        """
        Envoie une notification webhook
        
        Args:
            webhook_url: URL du webhook
            payload: Payload du webhook
            
        Returns:
            bool: Indicateur de succès
        """
        try:
            # Ajout du timestamp
            payload["timestamp"] = int(time.time())
            
            # Génération de la signature
            signature = self._generate_signature(payload)
            
            # Envoi du webhook
            response = requests.post(
                webhook_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Signature": signature,
                    "User-Agent": f"Nexten/{settings.SERVICE_NAME}"
                },
                timeout=10
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Webhook envoyé avec succès à {webhook_url}")
                return True
            else:
                logger.warning(f"Échec du webhook avec le statut {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du webhook à {webhook_url}: {str(e)}")
            raise
