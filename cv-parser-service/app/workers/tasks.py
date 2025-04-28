# CV Parser Service - Tâches asynchrones pour RQ

import os
import time
import logging
import json
import tempfile
import traceback
from typing import Dict, Any, Optional, BinaryIO, List
import redis

from app.core.config import settings
from app.services.storage import get_file_from_storage, delete_file_from_storage, store_result_multi_tier
from app.services.parser import parse_cv
from app.services.webhook import send_webhook

# Setup logging
logger = logging.getLogger(__name__)

# Connexion Redis
redis_conn = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True  # Important pour Redis HGET/HGETALL
)

def handle_failed_job(job_id: str, error_message: str, file_path: Optional[str] = None, 
                    original_queue: str = "cv_parsing") -> bool:
    """Traite un job qui a échoué définitivement
    
    Args:
        job_id: Identifiant unique du job
        error_message: Message d'erreur
        file_path: Chemin du fichier (optionnel)
        original_queue: Nom de la queue d'origine
        
    Returns:
        bool: True si le traitement a réussi
    """
    logger.error(f"Job {job_id} a échoué définitivement: {error_message}")
    
    # Stocker les informations d'échec dans Redis
    try:
        redis_conn.hset(
            f"cv:failed:{job_id}",
            mapping={
                "error": str(error_message),
                "file_path": file_path or "unknown",
                "failed_at": time.time(),
                "original_queue": original_queue
            }
        )
        
        # Garder l'information 7 jours
        redis_conn.expire(f"cv:failed:{job_id}", 604800)
    except Exception as e:
        logger.error(f"Erreur lors du stockage des informations d'échec dans Redis: {str(e)}")
    
    # Stocker le résultat d'échec dans le stockage multi-tier
    error_result = {
        "status": "failed",
        "error": str(error_message),
        "failed_at": time.time()
    }
    
    try:
        # Version asynchrone nécessite un event loop, utiliser la version sync dans RQ
        store_result_multi_tier_sync(
            job_id=job_id,
            result=error_result,
            status="failed",
            error=str(error_message)
        )
    except Exception as e:
        logger.error(f"Erreur lors du stockage du résultat d'échec: {str(e)}")
    
    # Notification webhook
    try:
        webhook_info = redis_conn.hgetall(f"cv:webhook:{job_id}")
        if webhook_info and "url" in webhook_info:
            send_webhook(
                job_id=job_id,
                url=webhook_info["url"],
                secret=webhook_info.get("secret", ""),
                data=error_result
            )
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du webhook d'échec: {str(e)}")
    
    return True

def move_to_dead_letter_queue(job_id: str, error: str, file_path: Optional[str] = None) -> bool:
    """Déplace un job dans la dead letter queue
    
    Args:
        job_id: Identifiant unique du job
        error: Message d'erreur
        file_path: Chemin du fichier (optionnel)
        
    Returns:
        bool: True si le déplacement a réussi
    """
    from rq import Queue, get_current_job
    
    current_job = get_current_job(connection=redis_conn)
    original_queue = current_job.origin if current_job else "cv_parsing"
    
    try:
        # Enregistrer dans la dead letter queue
        dlq = Queue("cv_parsing_failed", connection=redis_conn)
        dlq.enqueue(
            handle_failed_job,
            error_message=error,
            file_path=file_path,
            original_queue=original_queue,
            job_id=f"dlq:{job_id}"  # Préfixe pour éviter les collisions
        )
        
        logger.warning(f"Job {job_id} déplacé vers la dead letter queue")
        return True
    except Exception as e:
        logger.error(f"Erreur lors du déplacement vers la dead letter queue: {str(e)}")
        return False

# Version synchrone de store_result_multi_tier pour RQ
def store_result_multi_tier_sync(job_id: str, result: Dict[str, Any], status: str = "completed", 
                               error: Optional[str] = None, priority: Optional[str] = None, 
                               processing_time: Optional[float] = None) -> bool:
    """Version synchrone de store_result_multi_tier pour utilisation dans RQ"""
    # Similaire à store_result_multi_tier mais sans async/await
    # Utiliser directement les fonctions Redis et PostgreSQL synchrones
    # ...
    # Une implémentation complète nécessiterait de dupliquer la logique
    # Pour les besoins actuels, nous utilisons simplement le stockage Redis 
    try:
        # 1. Convertir en JSON
        result_json = json.dumps(result)
        
        # 2. Stocker dans Redis
        redis_conn.set(
            f"cv:result:{job_id}",
            result_json,
            ex=settings.REDIS_RESULT_TTL
        )
        
        # 3. Stocker les métadonnées
        redis_conn.hset(
            f"cv:meta:{job_id}",
            mapping={
                "status": status,
                "updated_at": time.time(),
                "processing_time": processing_time or 0
            }
        )
        
        if error:
            redis_conn.hset(f"cv:meta:{job_id}", "error", error)
            
        return True
    except Exception as e:
        logger.error(f"Erreur lors du stockage des résultats: {str(e)}")
        return False

# Modifié pour accepter job_id comme paramètre nommé obligatoire
def parse_cv_task(*, job_id: str = None, file_path: str = None, file_name: str = None, 
                file_format: str = None, max_retries: int = 3, webhook_url: Optional[str] = None,
                webhook_secret: Optional[str] = None) -> Dict[str, Any]:
    """Tâche RQ de parsing d'un CV
    
    Args:
        job_id: Identifiant unique du job (obligatoire, nommé)
        file_path: Chemin vers le fichier stocké
        file_name: Nom original du fichier
        file_format: Format du fichier (.pdf, .docx, etc.)
        max_retries: Nombre maximum de tentatives
        webhook_url: URL de callback (optionnel)
        webhook_secret: Secret pour la signature (optionnel)
        
    Returns:
        Dict[str, Any]: Résultat du parsing
    """
    # Vérifier que les paramètres obligatoires sont fournis
    if not job_id:
        raise ValueError("job_id est obligatoire")
    if not file_path:
        raise ValueError("file_path est obligatoire")
    if not file_name:
        raise ValueError("file_name est obligatoire") 
    if not file_format:
        raise ValueError("file_format est obligatoire")
        
    logger.info(f"Démarrage du parsing CV pour job: {job_id}, fichier: {file_name}")
    
    # Fichier temporaire si nécessaire
    temp_file = None
    retry_count = 0
    last_error = None
    
    try:
        # Récupérer les informations de webhook depuis Redis
        if not webhook_url:
            webhook_info = redis_conn.hgetall(f"cv:webhook:{job_id}")
            if webhook_info:
                webhook_url = webhook_info.get("url")
                webhook_secret = webhook_info.get("secret")
        
        # Traitement avec logique de retry
        while retry_count < max_retries:
            try:
                start_time = time.time()
                
                # Récupérer le fichier depuis le stockage
                file_obj = get_file_from_storage(file_path)
                
                # Pour MinIO ou objet file-like, enregistrer dans un fichier temporaire
                if hasattr(file_obj, 'read') and not isinstance(file_obj, str):
                    # Créer un fichier temporaire avec l'extension correcte
                    suffix = file_format if file_format.startswith('.') else f".{file_format}"
                    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                        tmp.write(file_obj.read())
                        temp_file = tmp.name
                    
                    # Fermer l'objet file-like si possible
                    if hasattr(file_obj, 'close'):
                        file_obj.close()
                    
                    # Utiliser le fichier temporaire pour le parsing
                    file_to_parse = temp_file
                else:
                    # Utiliser le chemin de fichier original
                    file_to_parse = file_path
                
                # Parser le CV
                parsing_result = parse_cv(file_to_parse, file_format)
                processing_time = time.time() - start_time
                
                # Préparer le résultat avec métadonnées
                result = {
                    "job_id": job_id,
                    "file_name": file_name,
                    "file_format": file_format,
                    "processing_time": processing_time,
                    "parsed_at": time.time(),
                    "status": "done",
                    "data": parsing_result.get("data", parsing_result)
                }
                
                # Stocker le résultat
                store_result_multi_tier_sync(
                    job_id=job_id,
                    result=result,
                    status="completed",
                    processing_time=processing_time
                )
                
                logger.info(f"Parsing CV réussi pour job: {job_id}, durée: {processing_time:.2f}s")
                
                # Envoyer la notification webhook si URL fournie
                if webhook_url:
                    send_webhook(webhook_url, job_id, result, webhook_secret or "")
                
                return result
                
            except Exception as e:
                # Incrémenter le compteur et enregistrer l'erreur
                retry_count += 1
                last_error = str(e)
                stack_trace = traceback.format_exc()
                
                logger.warning(
                    f"Tentative {retry_count}/{max_retries} échouée pour job {job_id}: {last_error}"
                )
                
                # Arrêter si nombre max de tentatives atteint
                if retry_count >= max_retries:
                    logger.error(f"Job {job_id} a échoué après {max_retries} tentatives")
                    logger.error(f"Stack trace: {stack_trace}")
                    break
                    
                # Backoff exponentiel: 2^retry_count secondes
                backoff = 2 ** retry_count
                logger.info(f"Attente de {backoff}s avant la prochaine tentative")
                time.sleep(backoff)
        
        # Si toutes les tentatives ont échoué
        if retry_count >= max_retries:
            error_result = {
                "job_id": job_id,
                "file_name": file_name,
                "status": "failed",
                "error": f"Échec après {max_retries} tentatives. Dernière erreur: {last_error}"
            }
            
            # Enregistrer l'échec
            move_to_dead_letter_queue(job_id, last_error, file_path)
            
            # Envoyer notification d'échec
            if webhook_url:
                send_webhook(webhook_url, job_id, error_result, webhook_secret or "")
            
            # Re-lever l'exception pour que RQ marque le job comme échoué
            raise Exception(f"Parsing CV échoué: {last_error}")
            
        return {"error": f"Échec après {max_retries} tentatives"}
        
    finally:
        # Nettoyer le fichier temporaire si créé
        if temp_file and os.path.exists(temp_file) and settings.CLEANUP_TEMP_FILES:
            try:
                os.unlink(temp_file)
            except Exception as e:
                logger.warning(f"Erreur lors de la suppression du fichier temporaire {temp_file}: {str(e)}")
        
        # Nettoyer le fichier original si configuré
        if settings.CLEANUP_TEMP_FILES:
            try:
                delete_file_from_storage(file_path)
            except Exception as e:
                logger.warning(f"Erreur lors de la suppression du fichier original {file_path}: {str(e)}")
