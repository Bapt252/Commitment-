"""Configuration du logging structuré avec structlog."""
import logging
import logging.config
import structlog
from datetime import datetime
import json
import os
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """Formatter JSON personnalisé pour les logs."""

    def format(self, record: logging.LogRecord) -> str:
        # Informations de base du log
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread,
        }

        # Ajouter des champs personnalisés s'ils existent
        custom_fields = [
            "user_id", "request_id", "service", "operation",
            "duration_ms", "status_code", "method", "path",
            "error_type", "error_message", "traceback"
        ]
        
        for field in custom_fields:
            if hasattr(record, field):
                log_entry[field] = getattr(record, field)

        # Ajouter l'exception si présente
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info)
            }

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(service_name: str = "nexten", log_level: str = "INFO"):
    """Configuration du logging structuré."""
    
    # Configuration du niveau de log
    log_level = os.getenv("LOG_LEVEL", log_level).upper()
    
    # Configuration de structlog
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
            structlog.processors.CallsiteParameterAdder(
                parameters=[structlog.processors.CallsiteParameter.FILENAME,
                           structlog.processors.CallsiteParameter.FUNC_NAME,
                           structlog.processors.CallsiteParameter.LINENO]
            ),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configuration du logging standard
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json" if os.getenv("LOG_FORMAT", "json") == "json" else "simple",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "json",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "level": "ERROR",
            }
        },
        "loggers": {
            service_name: {
                "level": log_level,
                "handlers": ["console", "file", "error_file"],
                "propagate": False,
            },
            "fastapi": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console", "error_file"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
    }

    # Créer le répertoire logs s'il n'existe pas
    os.makedirs("logs", exist_ok=True)
    
    # Appliquer la configuration
    logging.config.dictConfig(logging_config)
    
    # Retourner un logger structuré
    return structlog.get_logger(service_name)


class CorrelationIDProcessor:
    """Processeur pour ajouter un ID de corrélation aux logs."""
    
    def __init__(self, correlation_id_key: str = "correlation_id"):
        self.correlation_id_key = correlation_id_key
    
    def __call__(self, logger, method_name, event_dict):
        # Ajouter l'ID de corrélation s'il est disponible dans le contexte
        if hasattr(logger, "_context") and self.correlation_id_key in logger._context:
            event_dict[self.correlation_id_key] = logger._context[self.correlation_id_key]
        return event_dict


def get_logger(name: str = "") -> structlog.BoundLogger:
    """Obtenir un logger structuré."""
    return structlog.get_logger(name)


def setup_request_logging_middleware(app):
    """Middleware pour ajouter un ID de corrélation à chaque requête."""
    import uuid
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    
    class RequestLoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # Générer un ID de corrélation
            correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
            
            # Ajouter au contexte de la requête
            request.state.correlation_id = correlation_id
            
            # Logger la requête
            logger = get_logger("request")
            logger = logger.bind(correlation_id=correlation_id)
            
            logger.info(
                "Request started",
                method=request.method,
                path=request.url.path,
                query_params=dict(request.query_params),
                headers=dict(request.headers),
                client_ip=request.client.host if request.client else None
            )
            
            try:
                response = await call_next(request)
                
                logger.info(
                    "Request completed",
                    status_code=response.status_code,
                    response_headers=dict(response.headers)
                )
                
                # Ajouter l'ID de corrélation à la réponse
                response.headers["X-Correlation-ID"] = correlation_id
                
                return response
                
            except Exception as e:
                logger.error(
                    "Request failed",
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise
    
    app.add_middleware(RequestLoggingMiddleware)


# Configuration pour différents environnements
LOGGING_CONFIGS = {
    "development": {
        "level": "DEBUG",
        "format": "simple",
        "console_output": True,
        "file_output": True,
    },
    "testing": {
        "level": "WARNING",
        "format": "simple",
        "console_output": False,
        "file_output": False,
    },
    "staging": {
        "level": "INFO",
        "format": "json",
        "console_output": True,
        "file_output": True,
    },
    "production": {
        "level": "WARNING",
        "format": "json",
        "console_output": True,
        "file_output": True,
    }
}


def get_logging_config(environment: str = "development") -> Dict[str, Any]:
    """Obtenir la configuration de logging pour un environnement donné."""
    return LOGGING_CONFIGS.get(environment, LOGGING_CONFIGS["development"])