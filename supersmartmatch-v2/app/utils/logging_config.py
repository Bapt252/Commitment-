"""
Configuration du logging pour SuperSmartMatch V2

Configure le système de logging avec :
- Niveaux de log configurables
- Formatage JSON structuré
- Rotation des logs
- Métriques intégrées
"""

import logging
import logging.handlers
import sys
import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """
    Formateur JSON pour les logs structurés
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Formate un enregistrement de log en JSON"""
        
        # Données de base
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Ajouter des champs spéciaux s'ils existent
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        if hasattr(record, 'algorithm'):
            log_data['algorithm'] = record.algorithm
        
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        
        if hasattr(record, 'service'):
            log_data['service'] = record.service
        
        # Exception si présente
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Données additionnelles
        if hasattr(record, 'extra_data'):
            log_data.update(record.extra_data)
        
        return json.dumps(log_data, ensure_ascii=False)


class SuperSmartMatchFilter(logging.Filter):
    """
    Filtre personnalisé pour les logs SuperSmartMatch
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filtre les logs selon les critères"""
        
        # Ajouter des métadonnées standard
        record.service = "supersmartmatch-v2"
        record.version = "2.0.0"
        
        # Filtrer les logs de sanity check trop verbeux
        if record.levelno == logging.DEBUG and "health" in record.getMessage().lower():
            return False
        
        return True


def setup_logging(log_level: str = "INFO", enable_json: bool = True, log_file: str = None):
    """
    Configure le système de logging
    
    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_json: Activer le formatage JSON
        log_file: Fichier de log (optionnel)
    """
    
    # Configuration de base
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Supprimer les handlers existants
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    # Formateur
    if enable_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    
    # Filtre personnalisé
    supersmartmatch_filter = SuperSmartMatchFilter()
    console_handler.addFilter(supersmartmatch_filter)
    
    root_logger.addHandler(console_handler)
    
    # Handler fichier avec rotation (si spécifié)
    if log_file:
        # Créer le répertoire si nécessaire
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        file_handler.addFilter(supersmartmatch_filter)
        
        root_logger.addHandler(file_handler)
    
    # Configuration spécifique pour certains loggers
    _configure_specific_loggers(log_level)
    
    # Log initial
    logger = logging.getLogger(__name__)
    logger.info(
        f"🔧 Logging configuré - Niveau: {log_level}, JSON: {enable_json}, Fichier: {log_file or 'Non'}"
    )


def _configure_specific_loggers(log_level: str):
    """Configure des loggers spécifiques"""
    
    # Logger aiohttp moins verbeux
    aiohttp_logger = logging.getLogger('aiohttp')
    aiohttp_logger.setLevel(logging.WARNING)
    
    # Logger Redis moins verbeux
    redis_logger = logging.getLogger('aioredis')
    redis_logger.setLevel(logging.WARNING)
    
    # Logger uvicorn personnalisé
    uvicorn_logger = logging.getLogger('uvicorn')
    if log_level.upper() == 'DEBUG':
        uvicorn_logger.setLevel(logging.DEBUG)
    else:
        uvicorn_logger.setLevel(logging.INFO)
    
    # Logger pour les accès HTTP
    access_logger = logging.getLogger('uvicorn.access')
    access_logger.setLevel(logging.INFO)


def get_logger_with_context(name: str, **context) -> logging.LoggerAdapter:
    """
    Crée un logger avec contexte additionnel
    
    Args:
        name: Nom du logger
        **context: Contexte additionnel (request_id, user_id, etc.)
    
    Returns:
        LoggerAdapter avec contexte
    """
    logger = logging.getLogger(name)
    return logging.LoggerAdapter(logger, context)


class MetricsLogHandler(logging.Handler):
    """
    Handler spécialisé pour les métriques
    
    Extrait et envoie les métriques depuis les logs vers un système de monitoring
    """
    
    def __init__(self, metrics_callback=None):
        super().__init__()
        self.metrics_callback = metrics_callback
        self.metrics_buffer = []
    
    def emit(self, record: logging.LogRecord):
        """Traite un enregistrement de log pour extraire les métriques"""
        try:
            # Extraire les métriques depuis les logs
            if hasattr(record, 'duration_ms'):
                metric = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'duration',
                    'value': record.duration_ms,
                    'tags': {
                        'service': getattr(record, 'service', 'unknown'),
                        'algorithm': getattr(record, 'algorithm', 'unknown'),
                        'level': record.levelname
                    }
                }
                
                if self.metrics_callback:
                    self.metrics_callback(metric)
                else:
                    self.metrics_buffer.append(metric)
        
        except Exception:
            # Ne pas faire échouer le logging si les métriques posent problème
            pass
    
    def get_buffered_metrics(self) -> list:
        """Récupère et vide le buffer de métriques"""
        metrics = self.metrics_buffer.copy()
        self.metrics_buffer.clear()
        return metrics


# Helpers pour logging structuré
def log_matching_request(logger: logging.Logger, algorithm: str, num_jobs: int, duration_ms: float, success: bool):
    """Log structuré pour les requêtes de matching"""
    logger.info(
        f"{'✅' if success else '❌'} Matching request completed",
        extra={
            'algorithm': algorithm,
            'num_jobs': num_jobs,
            'duration_ms': duration_ms,
            'success': success,
            'event_type': 'matching_request'
        }
    )


def log_algorithm_selection(logger: logging.Logger, selected: str, score: float, reasons: list):
    """Log structuré pour la sélection d'algorithme"""
    logger.info(
        f"🧠 Algorithm selected: {selected}",
        extra={
            'selected_algorithm': selected,
            'selection_score': score,
            'selection_reasons': reasons,
            'event_type': 'algorithm_selection'
        }
    )


def log_service_health(logger: logging.Logger, service: str, status: str, details: dict):
    """Log structuré pour la santé des services"""
    status_emoji = {
        'healthy': '✅',
        'unhealthy': '❌', 
        'degraded': '⚠️',
        'unknown': '❓'
    }
    
    logger.info(
        f"{status_emoji.get(status, '❓')} Service {service}: {status}",
        extra={
            'service_name': service,
            'health_status': status,
            'health_details': details,
            'event_type': 'service_health'
        }
    )


def log_circuit_breaker_event(logger: logging.Logger, service: str, old_state: str, new_state: str, failure_count: int):
    """Log structuré pour les événements circuit breaker"""
    state_emoji = {
        'closed': '🟢',
        'open': '🔴',
        'half_open': '🟡'
    }
    
    logger.warning(
        f"{state_emoji.get(new_state, '❓')} Circuit breaker {service}: {old_state} → {new_state}",
        extra={
            'service_name': service,
            'old_state': old_state,
            'new_state': new_state,
            'failure_count': failure_count,
            'event_type': 'circuit_breaker_transition'
        }
    )
