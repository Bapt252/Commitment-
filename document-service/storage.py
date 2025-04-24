import io
import tempfile
import os
from typing import Optional, BinaryIO, List
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from minio.commonconfig import Tags
from fastapi import UploadFile
from config import settings
from loguru import logger


class StorageClient:
    """
    Client pour interagir avec MinIO/S3
    """
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE
        )
        # S'assurer que les buckets existent
        self._ensure_buckets_exist()

    def _ensure_buckets_exist(self):
        """
        Vérifie que les buckets nécessaires existent, sinon les crée
        """
        try:
            if not self.client.bucket_exists(settings.DOCUMENT_BUCKET):
                self.client.make_bucket(settings.DOCUMENT_BUCKET)
                logger.info(f"Bucket {settings.DOCUMENT_BUCKET} créé")
            
            if not self.client.bucket_exists(settings.ARCHIVE_BUCKET):
                self.client.make_bucket(settings.ARCHIVE_BUCKET)
                logger.info(f"Bucket {settings.ARCHIVE_BUCKET} créé")
        except S3Error as e:
            logger.error(f"Erreur lors de la vérification/création des buckets: {str(e)}")
            raise

    async def upload_file(self, file: UploadFile, object_key: str, bucket_name: Optional[str] = None) -> dict:
        """
        Télécharge un fichier sur MinIO
        """
        if bucket_name is None:
            bucket_name = settings.DOCUMENT_BUCKET
        
        try:
            content = await file.read()
            file_size = len(content)
            
            result = self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_key,
                data=io.BytesIO(content),
                length=file_size,
                content_type=file.content_type
            )
            
            logger.info(f"Fichier téléchargé: {bucket_name}/{object_key}, etag: {result.etag}")
            return {
                "bucket": bucket_name,
                "object_key": object_key,
                "etag": result.etag,
                "size": file_size
            }
        
        except S3Error as e:
            logger.error(f"Erreur lors du téléchargement du fichier: {str(e)}")
            raise
        
        finally:
            await file.seek(0)  # Réinitialiser le curseur du fichier

    def download_file(self, object_key: str, bucket_name: Optional[str] = None) -> BinaryIO:
        """
        Télécharge un fichier depuis MinIO et le retourne sous forme de stream
        """
        if bucket_name is None:
            bucket_name = settings.DOCUMENT_BUCKET
        
        try:
            response = self.client.get_object(
                bucket_name=bucket_name,
                object_name=object_key
            )
            
            return response
        
        except S3Error as e:
            logger.error(f"Erreur lors du téléchargement du fichier: {str(e)}")
            raise

    def download_file_to_temp(self, object_key: str, bucket_name: Optional[str] = None) -> str:
        """
        Télécharge un fichier depuis MinIO vers un fichier temporaire
        """
        if bucket_name is None:
            bucket_name = settings.DOCUMENT_BUCKET
        
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        
        try:
            response = self.client.get_object(
                bucket_name=bucket_name,
                object_name=object_key
            )
            
            for data in response.stream(32*1024):
                temp_file.write(data)
            
            temp_file.close()
            return temp_file.name
        
        except S3Error as e:
            logger.error(f"Erreur lors du téléchargement du fichier: {str(e)}")
            os.unlink(temp_file.name)
            raise
        
        except Exception as e:
            logger.error(f"Erreur inattendue: {str(e)}")
            os.unlink(temp_file.name)
            raise

    def delete_file(self, object_key: str, bucket_name: Optional[str] = None) -> bool:
        """
        Supprime un fichier de MinIO
        """
        if bucket_name is None:
            bucket_name = settings.DOCUMENT_BUCKET
        
        try:
            self.client.remove_object(
                bucket_name=bucket_name,
                object_name=object_key
            )
            
            logger.info(f"Fichier supprimé: {bucket_name}/{object_key}")
            return True
        
        except S3Error as e:
            logger.error(f"Erreur lors de la suppression du fichier: {str(e)}")
            raise

    def archive_file(self, object_key: str, source_bucket: Optional[str] = None, target_bucket: Optional[str] = None) -> str:
        """
        Déplace un fichier du bucket principal vers le bucket d'archivage
        """
        if source_bucket is None:
            source_bucket = settings.DOCUMENT_BUCKET
        
        if target_bucket is None:
            target_bucket = settings.ARCHIVE_BUCKET
        
        archive_key = f"archive_{object_key}"
        
        try:
            # Copier l'objet vers le bucket d'archivage
            self.client.copy_object(
                bucket_name=target_bucket,
                object_name=archive_key,
                source_object=f"{source_bucket}/{object_key}"
            )
            
            # Supprimer l'objet d'origine
            self.client.remove_object(
                bucket_name=source_bucket,
                object_name=object_key
            )
            
            logger.info(f"Fichier archivé: {source_bucket}/{object_key} -> {target_bucket}/{archive_key}")
            return archive_key
        
        except S3Error as e:
            logger.error(f"Erreur lors de l'archivage du fichier: {str(e)}")
            raise

    def generate_presigned_url(self, object_key: str, expires_in_seconds: int = 300, bucket_name: Optional[str] = None) -> str:
        """
        Génère une URL pré-signée pour accéder à un fichier
        """
        if bucket_name is None:
            bucket_name = settings.DOCUMENT_BUCKET
        
        try:
            url = self.client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_key,
                expires=expires_in_seconds
            )
            
            logger.info(f"URL pré-signée générée pour: {bucket_name}/{object_key}")
            return url
        
        except S3Error as e:
            logger.error(f"Erreur lors de la génération de l'URL pré-signée: {str(e)}")
            raise

    def set_file_tags(self, object_key: str, tags: dict, bucket_name: Optional[str] = None) -> bool:
        """
        Définit des tags sur un fichier
        """
        if bucket_name is None:
            bucket_name = settings.DOCUMENT_BUCKET
        
        try:
            self.client.set_object_tags(
                bucket_name=bucket_name,
                object_name=object_key,
                tags=Tags(tags)
            )
            
            logger.info(f"Tags définis pour: {bucket_name}/{object_key}")
            return True
        
        except S3Error as e:
            logger.error(f"Erreur lors de la définition des tags: {str(e)}")
            raise

    def check_file_exists(self, object_key: str, bucket_name: Optional[str] = None) -> bool:
        """
        Vérifie si un fichier existe
        """
        if bucket_name is None:
            bucket_name = settings.DOCUMENT_BUCKET
        
        try:
            self.client.stat_object(
                bucket_name=bucket_name,
                object_name=object_key
            )
            return True
        except S3Error:
            return False
        
    def list_files(self, prefix: str = "", recursive: bool = True, bucket_name: Optional[str] = None) -> List[dict]:
        """
        Liste les fichiers dans un bucket
        """
        if bucket_name is None:
            bucket_name = settings.DOCUMENT_BUCKET
        
        try:
            objects = []
            for obj in self.client.list_objects(
                bucket_name=bucket_name,
                prefix=prefix,
                recursive=recursive
            ):
                objects.append({
                    "name": obj.object_name,
                    "size": obj.size,
                    "last_modified": obj.last_modified,
                    "etag": obj.etag
                })
            
            return objects
        
        except S3Error as e:
            logger.error(f"Erreur lors de la liste des fichiers: {str(e)}")
            raise


# Instance singleton du client de stockage
storage_client = StorageClient()
