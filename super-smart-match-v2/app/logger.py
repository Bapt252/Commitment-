"""
Configuration du logging pour SuperSmartMatch V2
"""

import logging
import logging.config
import structlog
import sys
from typing import Any, Dict
from pathlib import Path

from .config import get_config

def setup_logging() -> None:
    """Configure le système de logging structuré"""
    config = get_config()
    
    # Configuration structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if config.log_format == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configuration logging standard
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            },
            "console": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": config.log_format if config.log_format in ["json", "console"] else "console",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": config.log_format if config.log_format in ["json", "console"] else "console",
                "filename": "logs/supersmartmatch_v2.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "app": {
                "level": config.log_level,
                "handlers": ["console", "file"],
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "httpx": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False
            }
        },
        "root": {
            "level": config.log_level,
            "handlers": ["console"]
        }
    }
    
    # Créer le dossier de logs si nécessaire
    Path("logs").mkdir(exist_ok=True)
    
    # Appliquer la configuration
    logging.config.dictConfig(logging_config)

def get_logger(name: str) -> structlog.BoundLogger:
    """Obtenir un logger structuré"""
    return structlog.get_logger(name)

class RequestLogger:
    """Logger pour les requêtes HTTP"""
    
    def __init__(self):
        self.logger = get_logger("request")
    
    def log_request(self, method: str, path: str, **kwargs: Any) -> None:
        """Logger une requête entrante"""
        self.logger.info(
            "incoming_request",
            method=method,
            path=path,
            **kwargs
        )
    
    def log_response(self, status_code: int, duration_ms: float, **kwargs: Any) -> None:
        """Logger une réponse"""
        self.logger.info(
            "outgoing_response",
            status_code=status_code,
            duration_ms=duration_ms,
            **kwargs
        )
    
    def log_error(self, error: Exception, **kwargs: Any) -> None:
        """Logger une erreur"""
        self.logger.error(
            "request_error",
            error=str(error),
            error_type=type(error).__name__,
            **kwargs
        )

class AlgorithmLogger:
    """Logger pour les algorithmes de matching"""
    
    def __init__(self):
        self.logger = get_logger("algorithm")
    
    def log_selection(self, algorithm: str, reason: str, context: Dict[str, Any]) -> None:
        """Logger la sélection d'un algorithme"""
        self.logger.info(
            "algorithm_selected",
            algorithm=algorithm,
            reason=reason,
            context=context
        )
    
    def log_execution(self, algorithm: str, duration_ms: float, success: bool, **kwargs: Any) -> None:
        """Logger l'exécution d'un algorithme"""
        self.logger.info(
            "algorithm_executed",
            algorithm=algorithm,
            duration_ms=duration_ms,
            success=success,
            **kwargs
        )
    
    def log_fallback(self, from_algorithm: str, to_algorithm: str, reason: str) -> None:
        """Logger un fallback d'algorithme"""
        self.logger.warning(
            "algorithm_fallback",
            from_algorithm=from_algorithm,
            to_algorithm=to_algorithm,
            reason=reason
        )