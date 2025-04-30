import logging
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any

from app.core.config import settings

class JsonFormatter(logging.Formatter):
    """Formateur de logs en JSON pour une meilleure intégration avec des outils comme ELK"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formate l'enregistrement de log en JSON"""
        # Dictionnaire de base
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "service": settings.SERVICE_NAME
        }
        
        # Ajouter les attributs supplémentaires s'ils existent
        if hasattr(record, "job_id"):
            log_data["job_id"] = record.job_id
            
        if hasattr(record, "duration"):
            log_data["duration"] = record.duration
            
        # Ajouter l'exception si elle existe
        if record.exc_info:
            log_data["exception"] = {
                "type": str(record.exc_info[0].__name__),
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }
        
        return json.dumps(log_data)

def setup_logging() -> logging.Logger:
    """Configure le système de logging et retourne le logger racine"""
    # Créer le répertoire de logs s'il n'existe pas
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    
    # Configurer le niveau de log
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Configurer le logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Supprimer les handlers existants
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
    
    # Créer et configurer les handlers
    handlers = []
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    handlers.append(console_handler)
    
    # Handler pour les fichiers de log
    file_handler = logging.FileHandler(
        os.path.join(settings.LOG_DIR, f"{settings.SERVICE_NAME}.log")
    )
    file_handler.setLevel(log_level)
    handlers.append(file_handler)
    
    # Appliquer le formateur selon la configuration
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    # Appliquer le formateur à tous les handlers
    for handler in handlers:
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    
    # Créer et retourner un logger spécifique au service
    service_logger = logging.getLogger(settings.SERVICE_NAME)
    service_logger.setLevel(log_level)
    
    return service_logger
