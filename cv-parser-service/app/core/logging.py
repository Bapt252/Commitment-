# CV Parser Service - Configuration Logging

import logging
import json
import time
import socket
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Optional

from app.core.config import settings

class JsonFormatter(logging.Formatter):
    """Formateur de logs au format JSON structuré"""
    
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
            "process": record.process,
            "thread": record.thread,
            "hostname": socket.gethostname(),
            "service": "cv-parser-service"
        }
        
        # Ajouter les attributs contextuels
        for key, value in record.__dict__.items():
            if key.startswith('ctx_') and key != 'ctx_args':
                log_record[key[4:]] = value
                
        # Ajouter l'exception si présente
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

def setup_logging() -> logging.Logger:
    """Configure le logging avec format JSON et rotation"""
    
    # Déterminer le niveau de log
    log_level_name = settings.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Créer le logger root
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Supprimer tous les handlers existants
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Handler pour console (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Formateur selon la configuration
    if settings.LOG_FORMAT.lower() == "json":
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler pour fichier avec rotation si spécifié
    if settings.LOG_FILE:
        # Créer le répertoire si nécessaire
        log_dir = os.path.dirname(settings.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = RotatingFileHandler(
            settings.LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Configurer les loggers spécifiques
    # Réduire le niveau des logs pour les librairies tierces
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("rq").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.INFO)  # Garder INFO pour OpenAI
    
    # Logger de démarrage
    logger.info("Logging initialized", extra={"ctx_log_level": log_level_name})
    
    return logger
