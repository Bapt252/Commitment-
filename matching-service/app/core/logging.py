"""
Configuration du logging pour le service de matching.
"""
import logging
import json
import sys
import time
import uuid
from typing import Dict, Any, Optional
from app.core.config import settings

class JSONFormatter(logging.Formatter):
    """
    Formateur de logs au format JSON pour une meilleure intégration avec
    les outils de monitoring et d'analyse de logs.
    """
    def format(self, record: logging.LogRecord) -> str:
        """Formate un enregistrement de log en JSON"""
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread,
            "service": settings.SERVICE_NAME,
        }
        
        # Ajout des attributs supplémentaires
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_data.update(record.extra)
            
        # Ajout d'information sur l'exception si présente
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
            
        return json.dumps(log_data)

class StandardFormatter(logging.Formatter):
    """
    Formateur de logs standard pour la lisibilité humaine.
    Utilisé en mode développement.
    """
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

def get_request_id() -> str:
    """Génère un ID de requête unique pour le suivi des logs"""
    return str(uuid.uuid4())

def setup_logging() -> logging.Logger:
    """
    Configure le système de logging global
    
    Returns:
        Logger: Logger racine configuré
    """
    # Obtention du logger racine
    root_logger = logging.getLogger()
    
    # Suppression des handlers existants
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configuration du niveau de log
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Création du handler pour stdout
    handler = logging.StreamHandler(sys.stdout)
    
    # Choix du formateur selon le format configuré
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = StandardFormatter()
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # Création d'un logger spécifique pour le service
    logger = logging.getLogger(settings.SERVICE_NAME)
    logger.info(f"Logging configuré au niveau {settings.LOG_LEVEL}")
    
    return logger

class LoggerAdapter(logging.LoggerAdapter):
    """
    Adaptateur de logger pour ajouter automatiquement des métadonnées 
    contextuelles à chaque message de log.
    """
    def __init__(self, logger, extra=None):
        super().__init__(logger, extra or {})
        
    def process(self, msg, kwargs):
        """Ajoute les attributs supplémentaires aux logs"""
        kwargs.setdefault("extra", {}).update(self.extra)
        return msg, kwargs

def get_logger(name: str, request_id: Optional[str] = None, **extra) -> LoggerAdapter:
    """
    Obtient un logger avec des métadonnées contextuelles
    
    Args:
        name: Nom du logger
        request_id: ID de requête pour le suivi (généré si None)
        **extra: Métadonnées supplémentaires à inclure
        
    Returns:
        LoggerAdapter: Logger adapté avec contexte
    """
    logger = logging.getLogger(name)
    
    # Contexte à ajouter aux logs
    context = {
        "request_id": request_id or get_request_id(),
        "service": settings.SERVICE_NAME,
        "timestamp": time.time()
    }
    
    # Ajout des métadonnées supplémentaires
    if extra:
        context.update(extra)
        
    return LoggerAdapter(logger, context)
