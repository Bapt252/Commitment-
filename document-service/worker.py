import os
import time
import redis
import tempfile
import httpx
import uuid
from rq import Worker, Queue, Connection
from rq.job import Job
from datetime import datetime, timedelta
from loguru import logger
import json

# Configuration et imports locaux
from config import settings
from database import get_db_context
from models import Document
from storage import storage_client
from security import antivirus_scanner
from expiration import setup_document_expiration_scheduler

# Configuration du logger
logger.add(
    f"logs/worker_{uuid.uuid4()}.log",
    rotation="10 MB",
    level=settings.LOG_LEVEL,
    format="{time} {level} {message}",
    serialize=settings.LOG_FORMAT == "json"
)

# Connexion Redis
redis_conn = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)

# Définir les files d'attente
default_queue = Queue('document_default', connection=redis_conn)
security_queue = Queue('document_security', connection=redis_conn)
processing_queue = Queue('document_processing', connection=redis_conn)
notification_queue = Queue('document_notification', connection=redis_conn)


# Définition des tâches de traitement
def security_scan_job(document_id, object_key, bucket_name):
    """
    Worker pour l'analyse anti-virus avec ClamAV
    """
    logger.info(f"Démarrage de l'analyse de sécurité pour le document: {document_id}")
    
    # Initialisation des connexions
    try:
        with get_db_context() as db:
            # Récupérer les informations du document
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.error(f"Document non trouvé: {document_id}")
                return {
                    "status": "error",
                    "message": "Document non trouvé",
                    "document_id": str(document_id)
                }
            
            try:
                # Télécharger le fichier depuis MinIO
                temp_file_path = storage_client.download_file_to_temp(
                    object_key=object_key,
                    bucket_name=bucket_name
                )
                
                # Scanner avec ClamAV
                result = antivirus_scanner.scan_file(temp_file_path)
                
                # Mettre à jour le statut dans la base de données
                if result["infected"]:
                    document.status = "quarantined"
                    document.metadata = {
                        **(document.metadata or {}),
                        "security_scan": {
                            "status": "infected",
                            "threat": result["threat_name"],
                            "timestamp": result["timestamp"]
                        }
                    }
                    
                    # Déplacer vers un bucket de quarantaine si nécessaire
                    # Cette étape est optionnelle selon votre politique de sécurité
                    
                    # Notifier l'équipe de sécurité
                    notification_queue.enqueue(
                        'notify_security_team',
                        document_id=str(document_id),
                        threat_name=result["threat_name"]
                    )
                    
                else:
                    document.status = "active"
                    document.metadata = {
                        **(document.metadata or {}),
                        "security_scan": {
                            "status": "clean",
                            "timestamp": result["timestamp"]
                        }
                    }
                
                document.updated_at = datetime.utcnow()
                db.commit()
                
                # Nettoyage du fichier temporaire
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
                logger.info(f"Analyse de sécurité terminée pour le document: {document_id}, statut: {document.status}")
                
                # Lancer le traitement de parsing si applicable et si le document est propre
                if not result["infected"] and document.document_type == "cv":
                    # Envoyer à la file d'attente de parsing
                    notify_parsing_service(document_id, object_key, bucket_name)
                
                return {
                    "status": "success",
                    "infected": result["infected"],
                    "threat_name": result.get("threat_name"),
                    "document_id": str(document_id)
                }
            
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse de sécurité: {str(e)}")
                
                # Mettre à jour le statut en erreur
                document.status = "error"
                document.metadata = {
                    **(document.metadata or {}),
                    "security_scan_error": str(e),
                    "error_timestamp": datetime.utcnow().isoformat()
                }
                document.updated_at = datetime.utcnow()
                db.commit()
                
                # Nettoyage en cas d'erreur
                if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
                return {
                    "status": "error",
                    "message": str(e),
                    "document_id": str(document_id)
                }
    
    except Exception as e:
        logger.error(f"Erreur globale dans security_scan_job: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "document_id": str(document_id)
        }


def notify_parsing_service(document_id, object_key, bucket_name):
    """
    Notifie le service de parsing qu'un nouveau CV est disponible
    """
    logger.info(f"Notification du service de parsing pour le document: {document_id}")
    
    try:
        # Option 1: Appel direct à l'API du service de parsing
        if settings.CV_PARSER_SERVICE_URL:
            payload = {
                "document_id": str(document_id),
                "bucket_name": bucket_name,
                "object_key": object_key
            }
            
            # Appel asynchrone au service de parsing
            notification_queue.enqueue(
                'send_cv_to_parser',
                payload=payload,
                service_url=settings.CV_PARSER_SERVICE_URL
            )
        
        return {
            "status": "success",
            "message": "Service de parsing notifié",
            "document_id": str(document_id)
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la notification du service de parsing: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "document_id": str(document_id)
        }


async def send_cv_to_parser(payload, service_url):
    """
    Envoie un CV au service de parsing via une requête HTTP
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{service_url}/parse-document",
                json=payload,
                timeout=10.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"CV envoyé au service de parsing: {payload['document_id']}, résultat: {result}")
            return result
    
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du CV au service de parsing: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "document_id": payload['document_id']
        }


def notify_security_team(document_id, threat_name):
    """
    Notifie l'équipe de sécurité en cas de menace détectée
    """
    logger.warning(f"ALERTE SÉCURITÉ: Document {document_id} infecté par {threat_name}")
    
    # Implémentation à personnaliser selon vos besoins (email, Slack, etc.)
    # Par exemple, envoi d'un email à l'équipe de sécurité
    try:
        # Code d'envoi d'email ou d'alerte
        # ...
        
        return {
            "status": "success",
            "message": "Équipe de sécurité notifiée",
            "document_id": document_id
        }
    
    except Exception as e:
        logger.error(f"Erreur lors de la notification de l'équipe de sécurité: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "document_id": document_id
        }


def process_document_expiration():
    """
    Traite l'expiration des documents (RGPD)
    """
    logger.info("Traitement de l'expiration des documents")
    
    try:
        with get_db_context() as db:
            # Récupérer les documents expirés
            expired_docs = db.query(Document).filter(
                Document.expires_at < datetime.utcnow(),
                Document.status.in_(["active", "pending"])
            ).all()
            
            processed_count = 0
            for doc in expired_docs:
                try:
                    # Archiver ou supprimer selon la configuration
                    if settings.ARCHIVE_EXPIRED_DOCUMENTS:
                        # Archiver le document
                        archive_key = storage_client.archive_file(
                            object_key=doc.object_key,
                            source_bucket=doc.bucket_name,
                            target_bucket=settings.ARCHIVE_BUCKET
                        )
                        
                        # Mettre à jour les métadonnées
                        doc.status = "archived"
                        doc.metadata = {
                            **(doc.metadata or {}),
                            "archived": {
                                "timestamp": datetime.utcnow().isoformat(),
                                "reason": "RGPD expiration",
                                "archive_key": archive_key
                            }
                        }
                    else:
                        # Supprimer complètement
                        storage_client.delete_file(
                            object_key=doc.object_key,
                            bucket_name=doc.bucket_name
                        )
                        
                        # Marquer comme supprimé
                        doc.status = "deleted"
                        doc.metadata = {
                            **(doc.metadata or {}),
                            "deleted": {
                                "timestamp": datetime.utcnow().isoformat(),
                                "reason": "RGPD expiration"
                            }
                        }
                    
                    doc.updated_at = datetime.utcnow()
                    processed_count += 1
                
                except Exception as e:
                    logger.error(f"Erreur lors du traitement de l'expiration du document {doc.id}: {str(e)}")
            
            db.commit()
            logger.info(f"Traitement terminé: {processed_count} documents expirés traités")
            
            return {
                "status": "success",
                "processed_count": processed_count,
                "total_count": len(expired_docs)
            }
    
    except Exception as e:
        logger.error(f"Erreur globale dans process_document_expiration: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


def send_expiration_notifications():
    """
    Envoie des notifications pour les documents qui expirent bientôt
    """
    logger.info("Envoi des notifications d'expiration")
    
    try:
        with get_db_context() as db:
            # Documents qui expirent dans 30 jours
            expiring_soon = db.query(Document).filter(
                Document.expires_at.between(
                    datetime.utcnow(),
                    datetime.utcnow() + timedelta(days=30)
                ),
                Document.status == "active"
            ).all()
            
            notification_count = 0
            for doc in expiring_soon:
                try:
                    # Récupérer les propriétaires/responsables du document
                    # Logique à adapter selon votre modèle de données et vos règles métier
                    
                    # Envoyer notification (à personnaliser)
                    notification_queue.enqueue(
                        'send_expiration_notification',
                        document_id=str(doc.id),
                        expiry_date=doc.expires_at.isoformat()
                    )
                    
                    notification_count += 1
                
                except Exception as e:
                    logger.error(f"Erreur lors de l'envoi de notification pour le document {doc.id}: {str(e)}")
            
            logger.info(f"Notifications envoyées: {notification_count} sur {len(expiring_soon)} documents")
            
            return {
                "status": "success",
                "notification_count": notification_count,
                "total_count": len(expiring_soon)
            }
    
    except Exception as e:
        logger.error(f"Erreur globale dans send_expiration_notifications: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == '__main__':
    # Configuration du scheduler pour les tâches planifiées
    setup_document_expiration_scheduler()
    
    # Définir les files d'attente à surveiller
    queues = [
        security_queue,
        processing_queue,
        notification_queue,
        default_queue  # File par défaut en dernier
    ]
    
    # Information de démarrage
    logger.info(f"Démarrage du worker avec {len(queues)} files d'attente")
    
    # Démarrer le worker
    with Connection(redis_conn):
        worker = Worker(queues)
        worker.work(with_scheduler=True)
