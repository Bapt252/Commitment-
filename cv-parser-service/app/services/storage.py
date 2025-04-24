# CV Parser Service - Service de stockage des fichiers et résultats

import os
import logging
import json
import io
import time
from typing import Optional, Dict, Any, BinaryIO, Union

import aiofiles
import redis
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException
from sqlalchemy import create_engine, Column, String, Integer, Text, Float, DateTime, func, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Setup logging
logger = logging.getLogger(__name__)

# Initialisation Redis
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD or None,
    decode_responses=True  # Important pour le stockage JSON
)

# Initialisation MinIO
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)

# Initialisation SQLAlchemy (si configuré)
Base = declarative_base()

class CVParsingResult(Base):
    """Modèle SQLAlchemy pour les résultats de parsing CV"""
    __tablename__ = "cv_parsing_results"
    
    job_id = Column(String(36), primary_key=True)
    status = Column(String(20), nullable=False, index=True)
    result_json = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    priority = Column(String(20), nullable=True)
    processing_time = Column(Float, nullable=True)
    error = Column(Text, nullable=True)
    
    def to_dict(self):
        return {
            "job_id": self.job_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "priority": self.priority,
            "processing_time": self.processing_time,
            "result": json.loads(self.result_json) if self.result_json else None,
            "error": self.error
        }

# Connexion PostgreSQL si configurée
db_engine = None
SessionLocal = None

if settings.STORE_RESULTS_IN_POSTGRES and settings.DATABASE_URL:
    try:
        db_engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
        Base.metadata.create_all(bind=db_engine)
        logger.info("PostgreSQL connecté pour le stockage de résultats")
    except Exception as e:
        logger.error(f"Erreur de connexion à PostgreSQL: {str(e)}")

# Fonctions pour assurer l'existence des buckets MinIO
def ensure_bucket_exists():
    """S'assure que le bucket MinIO existe, le crée sinon"""
    try:
        if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
            minio_client.make_bucket(settings.MINIO_BUCKET_NAME)
            logger.info(f"Bucket MinIO créé: {settings.MINIO_BUCKET_NAME}")
    except S3Error as e:
        logger.error(f"Erreur d'accès ou de création du bucket MinIO: {str(e)}")
        raise

# Fonction de sauvegarde de fichier temporaire
async def save_temp_file(file: UploadFile, job_id: str) -> str:
    """Sauvegarde un fichier téléchargé dans le stockage temporaire
    
    Args:
        file: Le fichier téléchargé
        job_id: Identifiant unique du job
        
    Returns:
        str: Chemin vers le fichier stocké
    """
    if settings.USE_MINIO_FOR_FILES:
        # Sauvegarde dans MinIO
        try:
            ensure_bucket_exists()
            
            # Lire le contenu du fichier
            content = await file.read()
            file_obj = io.BytesIO(content)
            
            # Réinitialiser le pointeur pour les lectures futures
            await file.seek(0)
            
            # Générer le nom de l'objet
            file_extension = os.path.splitext(file.filename)[1].lower()
            object_name = f"temp/{job_id}{file_extension}"
            
            # Upload dans MinIO
            minio_client.put_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=object_name,
                data=file_obj,
                length=len(content),
                content_type=file.content_type
            )
            
            logger.info(f"Fichier sauvegardé dans MinIO: {object_name}")
            return object_name
            
        except Exception as e:
            logger.error(f"Erreur de sauvegarde du fichier dans MinIO: {str(e)}")
            raise
    else:
        # Sauvegarde dans le répertoire temporaire local
        temp_dir = os.path.join(settings.TEMP_DIR, "cv_parser")
        os.makedirs(temp_dir, exist_ok=True)
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_path = os.path.join(temp_dir, f"{job_id}{file_extension}")
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        
        logger.info(f"Fichier sauvegardé en local: {file_path}")
        return file_path

# Fonction pour récupérer un fichier du stockage
def get_file_from_storage(file_path: str) -> BinaryIO:
    """Récupère un fichier depuis le stockage
    
    Args:
        file_path: Chemin vers le fichier stocké
        
    Returns:
        BinaryIO: Objet de type fichier
    """
    if settings.USE_MINIO_FOR_FILES and not file_path.startswith('/'):
        # Récupération depuis MinIO
        try:
            response = minio_client.get_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=file_path
            )
            return response
        except Exception as e:
            logger.error(f"Erreur de récupération du fichier depuis MinIO: {str(e)}")
            raise
    else:
        # Récupération depuis le stockage local
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Fichier non trouvé: {file_path}")
        
        return open(file_path, 'rb')

# Fonction pour supprimer un fichier du stockage
def delete_file_from_storage(file_path: str) -> bool:
    """Supprime un fichier du stockage
    
    Args:
        file_path: Chemin vers le fichier stocké
        
    Returns:
        bool: True si la suppression a réussi
    """
    if settings.USE_MINIO_FOR_FILES and not file_path.startswith('/'):
        # Suppression depuis MinIO
        try:
            minio_client.remove_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=file_path
            )
            logger.info(f"Fichier supprimé de MinIO: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur de suppression du fichier depuis MinIO: {str(e)}")
            return False
    else:
        # Suppression depuis le stockage local
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Fichier supprimé du stockage local: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur de suppression du fichier local: {str(e)}")
            return False

# Fonction de stockage multi-tier
async def store_result_multi_tier(job_id: str, result: Dict[str, Any], status: str = "completed", 
                               error: Optional[str] = None, priority: Optional[str] = None, 
                               processing_time: Optional[float] = None) -> bool:
    """Stocke le résultat dans plusieurs niveaux (Redis, PostgreSQL, MinIO)
    selon la taille et les besoins
    
    Args:
        job_id: Identifiant unique du job
        result: Résultat du parsing
        status: Statut du job
        error: Message d'erreur éventuel
        priority: Priorité du job
        processing_time: Temps de traitement en secondes
        
    Returns:
        bool: True si le stockage a réussi
    """
    success = False
    
    # 1. Déterminer si le résultat est volumineux
    result_json = json.dumps(result)
    is_large = len(result_json) > settings.LARGE_RESULT_THRESHOLD
    
    # 2. Stocker dans Redis (court terme, accès rapide)
    if settings.STORE_RESULTS_IN_REDIS:
        try:
            redis_client.set(
                f"cv:result:{job_id}",
                result_json,
                ex=settings.REDIS_RESULT_TTL
            )
            success = True
            logger.debug(f"Résultat stocké dans Redis pour job: {job_id}")
        except Exception as e:
            logger.error(f"Erreur de stockage Redis pour job {job_id}: {str(e)}")
    
    # 3. Stocker dans PostgreSQL (persistance longue durée)
    if settings.STORE_RESULTS_IN_POSTGRES and SessionLocal:
        try:
            db = SessionLocal()
            
            try:
                # Vérifier si l'enregistrement existe déjà
                existing = db.query(CVParsingResult).filter(CVParsingResult.job_id == job_id).first()
                
                if existing:
                    # Mettre à jour les champs
                    existing.status = status
                    existing.result_json = None if is_large else result_json
                    existing.priority = priority or existing.priority
                    existing.processing_time = processing_time or existing.processing_time
                    existing.error = error or existing.error
                    existing.updated_at = func.now()
                else:
                    # Nouvel enregistrement
                    db_record = CVParsingResult(
                        job_id=job_id,
                        status=status,
                        result_json=None if is_large else result_json,
                        file_path=None,
                        priority=priority,
                        processing_time=processing_time,
                        error=error
                    )
                    db.add(db_record)
                
                db.commit()
                success = True
                logger.info(f"Résultat stocké dans PostgreSQL pour job {job_id}")
            except Exception as e:
                logger.error(f"Erreur lors du stockage PostgreSQL pour job {job_id}: {str(e)}")
                db.rollback()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Erreur de connexion PostgreSQL pour job {job_id}: {str(e)}")
    
    # 4. Si volumineux, stocker dans MinIO
    if is_large and settings.USE_MINIO_FOR_FILES:
        try:
            ensure_bucket_exists()
            
            # Stocker le JSON dans MinIO
            object_name = f"results/{job_id}.json"
            minio_client.put_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=object_name,
                data=io.BytesIO(result_json.encode('utf-8')),
                length=len(result_json.encode('utf-8')),
                content_type="application/json"
            )
            
            # Mettre à jour le chemin dans PostgreSQL si configuré
            if settings.STORE_RESULTS_IN_POSTGRES and SessionLocal:
                try:
                    db = SessionLocal()
                    result_record = db.query(CVParsingResult).filter(CVParsingResult.job_id == job_id).first()
                    if result_record:
                        result_record.file_path = object_name
                        db.commit()
                    db.close()
                except Exception as e:
                    logger.error(f"Erreur de mise à jour du chemin MinIO dans PostgreSQL: {str(e)}")
            
            logger.info(f"Résultat volumineux stocké dans MinIO pour job {job_id}")
            success = True
        except Exception as e:
            logger.error(f"Erreur lors du stockage MinIO pour job {job_id}: {str(e)}")
    
    return success

# Fonction de récupération multi-tier
async def get_result_multi_tier(job_id: str) -> Optional[Dict[str, Any]]:
    """Récupère le résultat à partir du stockage multi-tier
    
    Recherche d'abord dans Redis, puis PostgreSQL, puis MinIO si nécessaire
    
    Args:
        job_id: Identifiant unique du job
        
    Returns:
        Optional[Dict[str, Any]]: Résultat ou None si non trouvé
    """
    # 1. Chercher dans Redis (plus rapide)
    if settings.STORE_RESULTS_IN_REDIS:
        try:
            redis_result = redis_client.get(f"cv:result:{job_id}")
            if redis_result:
                try:
                    return json.loads(redis_result)
                except json.JSONDecodeError:
                    logger.error(f"Erreur de décodage JSON pour job {job_id} dans Redis")
        except Exception as e:
            logger.error(f"Erreur de récupération Redis pour job {job_id}: {str(e)}")
    
    # 2. Chercher dans PostgreSQL
    if settings.STORE_RESULTS_IN_POSTGRES and SessionLocal:
        try:
            db = SessionLocal()
            
            try:
                db_record = db.query(CVParsingResult).filter(CVParsingResult.job_id == job_id).first()
                
                if not db_record:
                    db.close()
                    return None
                    
                # Si le résultat est directement disponible dans PostgreSQL
                if db_record.result_json:
                    try:
                        result = json.loads(db_record.result_json)
                        db.close()
                        return result
                    except json.JSONDecodeError:
                        logger.error(f"Erreur de décodage JSON pour job {job_id} dans PostgreSQL")
                
                # 3. Si le résultat est dans MinIO
                if db_record.file_path and settings.USE_MINIO_FOR_FILES:
                    file_path = db_record.file_path
                    db.close()
                    
                    try:
                        response = minio_client.get_object(
                            bucket_name=settings.MINIO_BUCKET_NAME,
                            object_name=file_path
                        )
                        
                        result_json = response.read().decode('utf-8')
                        response.close()
                        
                        # Mettre en cache dans Redis pour les prochains accès
                        if settings.STORE_RESULTS_IN_REDIS:
                            redis_client.set(
                                f"cv:result:{job_id}",
                                result_json,
                                ex=settings.REDIS_RESULT_TTL
                            )
                        
                        return json.loads(result_json)
                    except Exception as e:
                        logger.error(f"Erreur lors de la récupération MinIO pour job {job_id}: {str(e)}")
                
                # Si le statut est complété mais pas de résultat, c'est une anomalie
                if db_record.status == "completed" and not db_record.error:
                    logger.error(f"Anomalie: job {job_id} marqué comme complété mais aucun résultat trouvé")
                
                # Retourner les métadonnées disponibles
                metadata = {
                    "job_id": job_id,
                    "status": db_record.status,
                    "error": db_record.error,
                    "created_at": db_record.created_at.isoformat() if db_record.created_at else None,
                    "updated_at": db_record.updated_at.isoformat() if db_record.updated_at else None
                }
                
                db.close()
                return metadata
                
            except Exception as e:
                logger.error(f"Erreur de requête PostgreSQL pour job {job_id}: {str(e)}")
                db.close()
        except Exception as e:
            logger.error(f"Erreur de connexion PostgreSQL pour job {job_id}: {str(e)}")
    
    # Aucun résultat trouvé
    return None
