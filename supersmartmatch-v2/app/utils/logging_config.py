"""
SuperSmartMatch V2 - Configuration du logging
===========================================

Configuration centralisée du système de logging avec support pour
différents formats et niveaux selon l'environnement.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
import structlog
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO", log_format: str = "json") -> None:
    """
    Configure le système de logging pour SuperSmartMatch V2
    
    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format des logs ("json" ou "text")
    """
    
    # Configuration du niveau
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Niveau de log invalide: {log_level}')
    
    # Formatters
    if log_format.lower() == "json":
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(numeric_level)
    
    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Configuration spécifique pour SuperSmartMatch V2
    app_logger = logging.getLogger('app')
    app_logger.setLevel(numeric_level)
    
    # Réduction du bruit des librairies externes
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    # Configuration structlog si JSON
    if log_format.lower() == "json":
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
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


def setup_file_logging(
    log_file: Optional[str] = None,
    max_size: str = "100MB",
    backup_count: int = 5
) -> None:
    """
    Configure le logging vers fichier avec rotation
    
    Args:
        log_file: Chemin du fichier de log
        max_size: Taille maximale avant rotation
        backup_count: Nombre de fichiers de backup à conserver
    """
    
    if not log_file:
        return
    
    # Création du dossier si nécessaire
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Conversion de la taille
    size_map = {
        'KB': 1024,
        'MB': 1024 * 1024,
        'GB': 1024 * 1024 * 1024
    }
    
    size_value = max_size.rstrip('KMGB')
    size_unit = max_size[len(size_value):]
    max_bytes = int(size_value) * size_map.get(size_unit, 1)
    
    # Handler pour fichier avec rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    
    # Format JSON pour les fichiers
    json_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(json_formatter)
    
    # Ajout au logger racine
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Récupère un logger configuré pour SuperSmartMatch V2
    
    Args:
        name: Nom du logger (généralement __name__)
        
    Returns:
        Logger configuré
    """
    return logging.getLogger(name)


def setup_correlation_id_logging():
    """
    Configure le logging avec correlation ID pour tracer les requêtes
    """
    
    class CorrelationIdFilter(logging.Filter):
        """Filtre pour ajouter correlation_id aux logs"""
        
        def filter(self, record):
            # Récupération du correlation_id depuis le contexte
            # (nécessite middleware FastAPI pour le contexte)
            correlation_id = getattr(record, 'correlation_id', None)
            if not correlation_id:
                import uuid
                correlation_id = str(uuid.uuid4())[:8]
            
            record.correlation_id = correlation_id
            return True
    
    # Ajout du filtre à tous les handlers
    for handler in logging.getLogger().handlers:
        handler.addFilter(CorrelationIdFilter())


class RequestLogger:
    """
    Logger spécialisé pour les requêtes HTTP avec métriques
    """
    
    def __init__(self, name: str = "supersmartmatch.requests"):
        self.logger = logging.getLogger(name)
    
    def log_request_start(self, method: str, path: str, client_ip: str = None):
        """Log du début d'une requête"""
        self.logger.info(
            "Request started",
            extra={
                "event": "request_start",
                "method": method,
                "path": path,
                "client_ip": client_ip
            }
        )
    
    def log_request_end(
        self,
        method: str,
        path: str,
        status_code: int,
        duration: float,
        algorithm: str = None
    ):
        """Log de la fin d'une requête"""
        self.logger.info(
            "Request completed",
            extra={
                "event": "request_end",
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": duration * 1000,
                "algorithm": algorithm
            }
        )
    
    def log_algorithm_selection(self, algorithm: str, reason: str, score: float = None):
        """Log de la sélection d'algorithme"""
        self.logger.info(
            "Algorithm selected",
            extra={
                "event": "algorithm_selection",
                "algorithm": algorithm,
                "reason": reason,
                "score": score
            }
        )
    
    def log_external_service_call(
        self,
        service: str,
        method: str,
        url: str,
        duration: float,
        success: bool,
        status_code: int = None
    ):
        """Log d'appel à un service externe"""
        level = logging.INFO if success else logging.WARNING
        self.logger.log(
            level,
            f"External service call: {service}",
            extra={
                "event": "external_service_call",
                "service": service,
                "method": method,
                "url": url,
                "duration_ms": duration * 1000,
                "success": success,
                "status_code": status_code
            }
        )
    
    def log_circuit_breaker_event(self, service: str, state: str, reason: str = None):
        """Log d'événement circuit breaker"""
        self.logger.warning(
            f"Circuit breaker {state}: {service}",
            extra={
                "event": "circuit_breaker",
                "service": service,
                "state": state,
                "reason": reason
            }
        )


class PerformanceLogger:
    """
    Logger spécialisé pour les métriques de performance
    """
    
    def __init__(self, name: str = "supersmartmatch.performance"):
        self.logger = logging.getLogger(name)
    
    def log_algorithm_performance(
        self,
        algorithm: str,
        duration: float,
        num_jobs: int,
        num_results: int,
        success: bool
    ):
        """Log des performances d'un algorithme"""
        self.logger.info(
            f"Algorithm performance: {algorithm}",
            extra={
                "event": "algorithm_performance",
                "algorithm": algorithm,
                "duration_ms": duration * 1000,
                "num_jobs": num_jobs,
                "num_results": num_results,
                "success": success,
                "jobs_per_second": num_jobs / duration if duration > 0 else 0
            }
        )
    
    def log_cache_operation(self, operation: str, hit: bool, key: str = None):
        """Log des opérations de cache"""
        self.logger.debug(
            f"Cache {operation}: {'HIT' if hit else 'MISS'}",
            extra={
                "event": "cache_operation",
                "operation": operation,
                "hit": hit,
                "key": key
            }
        )
    
    def log_memory_usage(self, usage_mb: float, threshold_mb: float = None):
        """Log de l'utilisation mémoire"""
        level = logging.WARNING if threshold_mb and usage_mb > threshold_mb else logging.DEBUG
        self.logger.log(
            level,
            f"Memory usage: {usage_mb:.1f}MB",
            extra={
                "event": "memory_usage",
                "usage_mb": usage_mb,
                "threshold_mb": threshold_mb
            }
        )


# Loggers préconfigurés pour faciliter l'usage
request_logger = RequestLogger()
performance_logger = PerformanceLogger()
