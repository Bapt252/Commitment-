from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger
import redis
from config import settings


def setup_document_expiration_scheduler():
    """
    Configure le scheduler pour gérer l'expiration des documents RGPD
    """
    scheduler = BackgroundScheduler()
    
    # Tâche quotidienne pour vérifier les documents expirés (3h du matin)
    scheduler.add_job(
        trigger_document_expiration_check,
        CronTrigger(hour=3, minute=0),
        id='check_expired_documents',
        replace_existing=True
    )
    
    # Tâche pour envoyer des notifications avant expiration (9h du matin)
    scheduler.add_job(
        trigger_expiration_notifications,
        CronTrigger(hour=9, minute=0),
        id='send_expiration_notifications',
        replace_existing=True
    )
    
    # Démarrer le scheduler
    scheduler.start()
    logger.info("Scheduler d'expiration des documents démarré")
    
    return scheduler


def trigger_document_expiration_check():
    """
    Déclenche la tâche de vérification des documents expirés dans Redis Queue
    """
    try:
        # Connexion Redis
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
        
        # Importer Queue ici pour éviter les dépendances circulaires
        from rq import Queue
        
        # Créer la file d'attente
        queue = Queue('document_default', connection=redis_conn)
        
        # Envoyer la tâche
        job = queue.enqueue(
            'process_document_expiration',
            job_timeout=settings.REDIS_JOB_TIMEOUT,
            ttl=settings.REDIS_JOB_TTL,
            result_ttl=3600  # Garder le résultat pendant 1 heure
        )
        
        logger.info(f"Tâche de vérification des documents expirés programmée: {job.id}")
        return job.id
    
    except Exception as e:
        logger.error(f"Erreur lors de la programmation de la tâche d'expiration: {str(e)}")
        return None


def trigger_expiration_notifications():
    """
    Déclenche la tâche d'envoi des notifications d'expiration dans Redis Queue
    """
    try:
        # Connexion Redis
        redis_conn = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB
        )
        
        # Importer Queue ici pour éviter les dépendances circulaires
        from rq import Queue
        
        # Créer la file d'attente
        queue = Queue('document_notification', connection=redis_conn)
        
        # Envoyer la tâche
        job = queue.enqueue(
            'send_expiration_notifications',
            job_timeout=settings.REDIS_JOB_TIMEOUT,
            ttl=settings.REDIS_JOB_TTL,
            result_ttl=3600  # Garder le résultat pendant 1 heure
        )
        
        logger.info(f"Tâche d'envoi des notifications d'expiration programmée: {job.id}")
        return job.id
    
    except Exception as e:
        logger.error(f"Erreur lors de la programmation des notifications d'expiration: {str(e)}")
        return None


def calculate_expiry_date(days=None):
    """
    Calcule la date d'expiration à partir du nombre de jours fourni
    ou utilise la valeur par défaut des paramètres
    """
    if days is None:
        days = settings.DEFAULT_DOCUMENT_EXPIRY_DAYS
    
    return datetime.utcnow() + timedelta(days=days)


def is_document_expired(expires_at):
    """
    Vérifie si un document est expiré
    """
    if expires_at is None:
        return False
    
    return expires_at < datetime.utcnow()


def days_until_expiry(expires_at):
    """
    Calcule le nombre de jours avant expiration
    """
    if expires_at is None:
        return None
    
    delta = expires_at - datetime.utcnow()
    return max(0, delta.days)
