# Worker tasks pour le parsing de fiches de poste

import os
import time
import logging
import json
import requests
from typing import Dict, Any, Optional, List
import traceback
import hashlib
import hmac

from app.core.config import settings
from app.services.parser import parse_job
from app.services.storage import get_file_from_storage, store_result

# Créer le logger spécifique pour ce module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def parse_job_task(
    job_id: str,
    file_path: str,
    file_name: str,
    file_format: str,
    max_retries: int = 3,
    webhook_url: Optional[str] = None,
    webhook_secret: Optional[str] = None
) -> Dict[str, Any]:
    """Tâche asynchrone pour parser une fiche de poste
    
    Args:
        job_id: ID unique du job
        file_path: Chemin vers le fichier à parser
        file_name: Nom original du fichier
        file_format: Format du fichier (.pdf, .docx, etc.)
        max_retries: Nombre maximal de tentatives
        webhook_url: URL pour la notification webhook
        webhook_secret: Secret pour signer le webhook
        
    Returns:
        Dict[str, Any]: Résultat du parsing
    """
    start_time = time.time()
    logger.info(f"Démarrage du parsing de la fiche de poste pour le job {job_id}")
    
    try:
        # Charger le contenu du fichier depuis le stockage si nécessaire
        if file_path.startswith("minio://"):
            # Le fichier est dans MinIO, on doit créer un fichier temporaire
            logger.info(f"Récupération du fichier depuis MinIO: {file_path}")
            file_content = await get_file_from_storage(file_path)
            
            if not file_content:
                raise FileNotFoundError(f"Fichier non trouvé dans MinIO: {file_path}")
            
            # Créer un fichier temporaire local
            temp_dir = settings.TEMP_DIR
            os.makedirs(temp_dir, exist_ok=True)
            
            temp_file_path = os.path.join(temp_dir, f"temp_{job_id}{file_format}")
            with open(temp_file_path, "wb") as f:
                f.write(file_content)
            
            # Utiliser ce fichier temporaire
            file_path = temp_file_path
            logger.info(f"Fichier temporaire créé: {file_path}")
        
        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        # Parser la fiche de poste
        result = parse_job(file_path, file_format)
        
        # Ajouter des métadonnées
        result["job_id"] = job_id
        result["file_name"] = file_name
        result["completed_at"] = time.time()
        result["duration"] = time.time() - start_time
        
        # Stocker le résultat dans Redis
        await store_result(job_id, result)
        
        # Nettoyer le fichier temporaire si nécessaire
        if file_path.startswith(settings.TEMP_DIR) and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Fichier temporaire supprimé: {file_path}")
            except Exception as e:
                logger.warning(f"Erreur lors de la suppression du fichier temporaire: {str(e)}")
        
        # Notifier le service de matching si configuré
        if settings.MATCHING_API_URL:
            try:
                matching_result = notify_matching_service(job_id, result)
                logger.info(f"Service de matching notifié pour le job {job_id}: {matching_result}")
            except Exception as e:
                logger.error(f"Erreur lors de la notification du service de matching: {str(e)}")
        
        # Envoyer le webhook si configuré
        if webhook_url:
            try:
                webhook_result = send_webhook(webhook_url, job_id, result, webhook_secret)
                logger.info(f"Webhook envoyé pour le job {job_id}: {webhook_result}")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du webhook: {str(e)}")
        
        logger.info(f"Parsing de la fiche de poste terminé pour le job {job_id} en {result['duration']:.2f}s")
        return result
        
    except Exception as e:
        error_message = f"Erreur lors du parsing de la fiche de poste pour le job {job_id}: {str(e)}"
        logger.error(error_message)
        logger.error(traceback.format_exc())
        
        # En cas d'erreur, envoyer quand même un webhook si configuré
        if webhook_url:
            try:
                error_result = {
                    "job_id": job_id,
                    "status": "error",
                    "error": str(e),
                    "completed_at": time.time(),
                    "duration": time.time() - start_time
                }
                webhook_result = send_webhook(webhook_url, job_id, error_result, webhook_secret)
                logger.info(f"Webhook d'erreur envoyé pour le job {job_id}: {webhook_result}")
            except Exception as webhook_err:
                logger.error(f"Erreur lors de l'envoi du webhook d'erreur: {str(webhook_err)}")
        
        # Re-lever l'exception pour que RQ puisse la gérer
        raise

def notify_matching_service(job_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """Notifie le service de matching d'un nouveau parsing de fiche de poste
    
    Args:
        job_id: ID du job
        result: Résultat du parsing
        
    Returns:
        Dict[str, Any]: Réponse du service de matching
    """
    try:
        # Préparer les données à envoyer
        matching_data = {
            "job_id": job_id,
            "job_data": result.get("data", {}),
            "source": "job-parser",
            "timestamp": time.time()
        }
        
        # Envoyer la requête au service de matching
        response = requests.post(
            f"{settings.MATCHING_API_URL}/api/jobs",
            json=matching_data,
            headers={
                "Content-Type": "application/json",
                "X-Source": "job-parser"
            },
            timeout=10  # 10 secondes de timeout
        )
        
        # Vérifier la réponse
        response.raise_for_status()
        
        # Retourner la réponse
        return response.json()
    except Exception as e:
        logger.error(f"Erreur lors de la notification du service de matching: {str(e)}")
        raise

def send_webhook(url: str, job_id: str, result: Dict[str, Any], secret: Optional[str] = None) -> bool:
    """Envoie un webhook pour notifier de la fin du parsing
    
    Args:
        url: URL du webhook
        job_id: ID du job
        result: Résultat du parsing
        secret: Secret pour signer le webhook
        
    Returns:
        bool: True si succès, False sinon
    """
    try:
        # Préparer les données à envoyer
        webhook_data = {
            "job_id": job_id,
            "status": "error" if "error" in result else "success",
            "timestamp": time.time(),
            "result": result
        }
        
        # Convertir en JSON
        payload = json.dumps(webhook_data)
        
        # Préparer les headers
        headers = {
            "Content-Type": "application/json",
            "X-Job-Parser-Event": "job.parsed",
            "X-Job-ID": job_id
        }
        
        # Signer le payload si un secret est fourni
        if secret:
            signature = hmac.new(
                secret.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            headers["X-Job-Parser-Signature"] = signature
        
        # Envoyer la requête
        response = requests.post(
            url,
            data=payload,
            headers=headers,
            timeout=10  # 10 secondes de timeout
        )
        
        # Vérifier la réponse
        response.raise_for_status()
        
        logger.info(f"Webhook envoyé avec succès: {response.status_code}")
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du webhook: {str(e)}")
        return False
