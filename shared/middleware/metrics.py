"""
Middleware de métriques Prometheus pour les APIs FastAPI
"""
import time
from typing import Callable
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import logging

# Métriques Prometheus
REQUEST_COUNT = Counter(
    'fastapi_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status_code', 'service']
)

REQUEST_DURATION = Histogram(
    'fastapi_request_duration_seconds', 
    'HTTP request duration in seconds', 
    ['method', 'endpoint', 'service'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

REQUEST_IN_PROGRESS = Gauge(
    'fastapi_requests_in_progress', 
    'HTTP requests currently being processed', 
    ['method', 'endpoint', 'service']
)

# Métriques business pour le ML
ML_INFERENCE_DURATION = Histogram(
    'ml_inference_duration_seconds',
    'ML inference duration in seconds',
    ['model_type', 'service'],
    buckets=(0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0)
)

ML_INFERENCE_COUNT = Counter(
    'ml_inference_total',
    'Total ML inferences',
    ['model_type', 'service', 'status']
)

PARSING_ACCURACY = Histogram(
    'parsing_accuracy_score',
    'Parsing accuracy score',
    ['parser_type', 'file_type'],
    buckets=(0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.99, 1.0)
)

MATCHING_SCORE = Histogram(
    'matching_score_distribution',
    'Distribution of matching scores',
    ['matching_algorithm'],
    buckets=(0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
)

FILE_PROCESSING_SIZE = Histogram(
    'file_processing_size_bytes',
    'Size of processed files in bytes',
    ['file_type', 'service'],
    buckets=(1024, 10240, 102400, 1048576, 10485760, 104857600)  # 1KB à 100MB
)

logger = logging.getLogger(__name__)

class PrometheusMiddleware:
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Exclure le endpoint de métriques pour éviter la récursion
        if request.url.path == "/metrics":
            return await call_next(request)
        
        method = request.method
        endpoint = request.url.path
        
        # Normaliser l'endpoint pour les métriques (remplacer les IDs par des placeholders)
        endpoint_normalized = self._normalize_endpoint(endpoint)
        
        # Incrémenter les requêtes en cours
        REQUEST_IN_PROGRESS.labels(
            method=method, 
            endpoint=endpoint_normalized, 
            service=self.service_name
        ).inc()
        
        start_time = time.time()
        
        try:
            # Traiter la requête
            response = await call_next(request)
            
            # Calculer la durée
            duration = time.time() - start_time
            
            # Enregistrer les métriques
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint_normalized,
                status_code=response.status_code,
                service=self.service_name
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint_normalized,
                service=self.service_name
            ).observe(duration)
            
            # Log des requêtes lentes
            if duration > 5.0:  # Plus de 5 secondes
                logger.warning(
                    f"Slow request detected: {method} {endpoint} took {duration:.2f}s",
                    extra={
                        'method': method,
                        'endpoint': endpoint,
                        'duration': duration,
                        'status_code': response.status_code,
                        'service': self.service_name
                    }
                )
            
            return response
            
        except Exception as e:
            # En cas d'erreur, enregistrer avec status 500
            duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=endpoint_normalized,
                status_code=500,
                service=self.service_name
            ).inc()
            
            REQUEST_DURATION.labels(
                method=method,
                endpoint=endpoint_normalized,
                service=self.service_name
            ).observe(duration)
            
            logger.error(
                f"Request error: {method} {endpoint}",
                extra={
                    'method': method,
                    'endpoint': endpoint,
                    'duration': duration,
                    'error': str(e),
                    'service': self.service_name
                },
                exc_info=True
            )
            
            raise
            
        finally:
            # Décrémenter les requêtes en cours
            REQUEST_IN_PROGRESS.labels(
                method=method,
                endpoint=endpoint_normalized,
                service=self.service_name
            ).dec()
    
    def _normalize_endpoint(self, endpoint: str) -> str:
        """Normalise les endpoints pour les métriques"""
        # Remplacer les UUIDs et IDs numériques par des placeholders
        import re
        
        # UUID pattern
        endpoint = re.sub(r'/[0-9a-f-]{36}', '/{uuid}', endpoint)
        # Numeric ID pattern
        endpoint = re.sub(r'/\d+', '/{id}', endpoint)
        # File names
        endpoint = re.sub(r'/[^/]+\.(pdf|docx?|txt|json)$', '/{filename}', endpoint)
        
        return endpoint

# Fonctions helper pour les métriques business
def track_ml_inference(model_type: str, service: str, duration: float, success: bool = True):
    """Track ML inference metrics"""
    status = "success" if success else "error"
    ML_INFERENCE_COUNT.labels(model_type=model_type, service=service, status=status).inc()
    if success:
        ML_INFERENCE_DURATION.labels(model_type=model_type, service=service).observe(duration)

def track_parsing_accuracy(parser_type: str, file_type: str, accuracy: float):
    """Track parsing accuracy metrics"""
    PARSING_ACCURACY.labels(parser_type=parser_type, file_type=file_type).observe(accuracy)

def track_matching_score(algorithm: str, score: float):
    """Track matching score metrics"""
    MATCHING_SCORE.labels(matching_algorithm=algorithm).observe(score)

def track_file_processing(file_type: str, service: str, file_size: int):
    """Track file processing metrics"""
    FILE_PROCESSING_SIZE.labels(file_type=file_type, service=service).observe(file_size)

async def metrics_endpoint():
    """Endpoint pour exposer les métriques Prometheus"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
