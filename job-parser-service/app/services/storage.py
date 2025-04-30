# Service de stockage pour les fichiers et résultats

import os
import io
import json
import logging
import tempfile
from typing import Dict, Any, Optional, BinaryIO, Union
from fastapi import UploadFile
import time
import redis

# Import MinIO si utilisé
try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Setup Redis connection
redis_conn = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True  # Important pour stocker/récupérer du JSON
)

# Setup MinIO client si nécessaire
minio_client = None
if settings.USE_MINIO_FOR_FILES and MINIO_AVAILABLE:
    try:
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        
        # Créer le bucket s'il n'existe pas
        if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
            minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
            logger.info(f"Bucket {settings.MINIO_BUCKET_NAME} créé")
        
        logger.info(f"Client MinIO configuré pour {settings.MINIO_ENDPOINT}")
    except Exception as e:
        logger.error(f"Erreur lors de la configuration du client MinIO: {str(e)}")
        minio_client = None

async def save_temp_file(file: UploadFile, job_id: str) -> str:
    """Sauvegarde un fichier temporaire (MinIO ou local)
    
    Args:
        file: Fichier à sauvegarder
        job_id: ID du job associé
        
    Returns:
        str: Chemin ou identifiant du fichier sauvegardé
    """
    try:
        # Générer un nom unique pour le fichier
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_name = f"{job_id}{file_extension}"
        
        # Reset du curseur pour lire depuis le début
        await file.seek(0)
        file_content = await file.read()
        
        # Utiliser MinIO si configuré
        if settings.USE_MINIO_FOR_FILES and minio_client:
            try:
                # Utiliser un buffer mémoire pour éviter d'écrire sur disque
                file_data = io.BytesIO(file_content)
                
                # Upload vers MinIO
                minio_client.put_object(
                    bucket_name=settings.MINIO_BUCKET_NAME,
                    object_name=file_name,
                    data=file_data,
                    length=len(file_content),
                    content_type=file.content_type
                )
                
                logger.info(f"Fichier {file_name} uploadé dans MinIO (bucket: {settings.MINIO_BUCKET_NAME})")
                
                # Retourner l'identificateur MinIO
                return f"minio://{settings.MINIO_BUCKET_NAME}/{file_name}"
            except Exception as e:
                logger.error(f"Erreur lors de l'upload vers MinIO: {str(e)}")
                # Fallback au stockage local
        
        # Stockage local si MinIO non configuré ou en échec
        temp_dir = settings.TEMP_DIR
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_path = os.path.join(temp_dir, file_name)
        
        with open(temp_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"Fichier {file_name} sauvegardé localement dans {temp_path}")
        return temp_path
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde du fichier: {str(e)}")
        raise

async def get_file_from_storage(file_path: str) -> Optional[bytes]:
    """Récupère un fichier depuis le stockage (MinIO ou local)
    
    Args:
        file_path: Chemin ou identifiant du fichier à récupérer
        
    Returns:
        Optional[bytes]: Contenu du fichier ou None si non trouvé
    """
    try:
        # Vérifier si c'est un fichier MinIO
        if file_path.startswith("minio://") and minio_client:
            try:
                # Extraire le bucket et le nom de l'objet
                path_parts = file_path.replace("minio://", "").split("/", 1)
                bucket_name = path_parts[0]
                object_name = path_parts[1]
                
                # Récupérer depuis MinIO
                response = minio_client.get_object(bucket_name, object_name)
                
                # Lire le contenu
                content = response.read()
                response.close()
                
                logger.info(f"Fichier {object_name} récupéré depuis MinIO (bucket: {bucket_name})")
                return content
            except Exception as e:
                logger.error(f"Erreur lors de la récupération depuis MinIO: {str(e)}")
                return None
        
        # Fichier local
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                content = f.read()
            
            logger.info(f"Fichier récupéré depuis le stockage local: {file_path}")
            return content
        else:
            logger.warning(f"Fichier non trouvé: {file_path}")
            return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du fichier: {str(e)}")
        return None

async def store_result(job_id: str, result: Dict[str, Any]) -> bool:
    """Stocke le résultat d'un job dans Redis
    
    Args:
        job_id: ID du job
        result: Résultat à stocker
        
    Returns:
        bool: True si succès, False sinon
    """
    try:
        if not settings.STORE_RESULTS_IN_REDIS:
            logger.info(f"Stockage des résultats dans Redis désactivé, ignoré pour {job_id}")
            return False
        
        # Convertir le résultat en JSON
        result_json = json.dumps(result)
        
        # Stocker dans Redis avec TTL
        redis_key = f"job:result:{job_id}"
        success = redis_conn.set(
            redis_key,
            result_json,
            ex=settings.REDIS_RESULT_TTL
        )
        
        if success:
            logger.info(f"Résultat stocké dans Redis pour le job {job_id} (TTL: {settings.REDIS_RESULT_TTL}s)")
        else:
            logger.warning(f"Échec du stockage dans Redis pour le job {job_id}")
        
        return bool(success)
    except Exception as e:
        logger.error(f"Erreur lors du stockage du résultat dans Redis: {str(e)}")
        return False

async def get_result_multi_tier(job_id: str) -> Optional[Dict[str, Any]]:
    """Récupère le résultat d'un job depuis Redis
    
    Args:
        job_id: ID du job
        
    Returns:
        Optional[Dict[str, Any]]: Résultat ou None si non trouvé
    """
    try:
        # Essayer de récupérer depuis Redis
        redis_key = f"job:result:{job_id}"
        result_json = redis_conn.get(redis_key)
        
        if result_json:
            logger.info(f"Résultat récupéré depuis Redis pour le job {job_id}")
            return json.loads(result_json)
        
        # TODO: Implémenter d'autres tiers de stockage (S3, DB, etc.)
        
        logger.warning(f"Aucun résultat trouvé pour le job {job_id}")
        return None
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du résultat: {str(e)}")
        return None
