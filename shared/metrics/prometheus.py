"""Configuration et métriques Prometheus pour FastAPI."""
import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry
)
import psutil
import asyncio
from contextlib import asynccontextmanager

# Métriques globales Prometheus
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code', 'service']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'service'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Number of active HTTP requests',
    ['service']
)

REQUEST_SIZE = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint', 'service']
)

RESPONSE_SIZE = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint', 'status_code', 'service']
)

# Métriques spécifiques à l'application
ML_PROCESSING_TIME = Histogram(
    'ml_processing_duration_seconds',
    'ML processing duration in seconds',
    ['service', 'operation', 'model_type']
)

ML_REQUESTS_TOTAL = Counter(
    'ml_requests_total',
    'Total ML processing requests',
    ['service', 'operation', 'status']
)

ML_ERRORS_TOTAL = Counter(
    'ml_errors_total',
    'Total ML processing errors',
    ['service', 'operation', 'error_type']
)

# Métriques système
SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage',
    ['service']
)

SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'System memory usage in bytes',
    ['service', 'type']
)

OPENAI_API_CALLS = Counter(
    'openai_api_calls_total',
    'Total OpenAI API calls',
    ['service', 'model', 'status']
)

OPENAI_TOKENS_USED = Counter(
    'openai_tokens_total',
    'Total OpenAI tokens used',
    ['service', 'model', 'type']
)

# Métriques de base de données
DB_CONNECTIONS_ACTIVE = Gauge(
    'db_connections_active',
    'Active database connections',
    ['service', 'database']
)

DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['service', 'operation', 'table']
)

# Métriques Redis
REDIS_OPERATIONS = Counter(
    'redis_operations_total',
    'Total Redis operations',
    ['service', 'operation', 'status']
)

REDIS_OPERATION_DURATION = Histogram(
    'redis_operation_duration_seconds',
    'Redis operation duration in seconds',
    ['service', 'operation']
)


class PrometheusMiddleware:
    """Middleware Prometheus pour FastAPI."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.process = psutil.Process()

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Ignorer les métriques pour /metrics
        if request.url.path == "/metrics":
            return await call_next(request)

        # Mesurer la taille de la requête
        request_size = len(await request.body()) if hasattr(request, "body") else 0
        
        # Incrémenter les requêtes actives
        ACTIVE_REQUESTS.labels(service=self.service_name).inc()
        
        # Enregistrer la taille de la requête
        REQUEST_SIZE.labels(
            method=request.method,
            endpoint=request.url.path,
            service=self.service_name
        ).observe(request_size)
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Mesurer la durée
            duration = time.time() - start_time
            
            # Enregistrer les métriques
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                service=self.service_name
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path,
                service=self.service_name
            ).observe(duration)
            
            # Mesurer la taille de la réponse
            response_size = len(getattr(response, "body", b""))
            RESPONSE_SIZE.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code,
                service=self.service_name
            ).observe(response_size)
            
            return response
            
        except Exception as e:
            # Compter les erreurs
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=500,
                service=self.service_name
            ).inc()
            raise
            
        finally:
            # Décrémenter les requêtes actives
            ACTIVE_REQUESTS.labels(service=self.service_name).dec()


class SystemMetricsCollector:
    """Collecteur de métriques système."""

    def __init__(self, service_name: str, interval: int = 10):
        self.service_name = service_name
        self.interval = interval
        self.process = psutil.Process()
        self.running = False

    async def start(self):
        """Démarrer la collecte de métriques système."""
        self.running = True
        asyncio.create_task(self._collect_system_metrics())

    async def stop(self):
        """Arrêter la collecte de métriques système."""
        self.running = False

    async def _collect_system_metrics(self):
        """Collecter les métriques système périodiquement."""
        while self.running:
            try:
                # CPU
                cpu_percent = self.process.cpu_percent()
                SYSTEM_CPU_USAGE.labels(service=self.service_name).set(cpu_percent)
                
                # Mémoire
                memory_info = self.process.memory_info()
                SYSTEM_MEMORY_USAGE.labels(
                    service=self.service_name,
                    type="rss"
                ).set(memory_info.rss)
                SYSTEM_MEMORY_USAGE.labels(
                    service=self.service_name,
                    type="vms"
                ).set(memory_info.vms)
                
                await asyncio.sleep(self.interval)
                
            except Exception as e:
                print(f"Error collecting system metrics: {e}")
                await asyncio.sleep(self.interval)


@asynccontextmanager
async def setup_metrics(service_name: str):
    """Context manager pour configurer les métriques."""
    collector = SystemMetricsCollector(service_name)
    await collector.start()
    try:
        yield
    finally:
        await collector.stop()


def setup_prometheus_middleware(app: FastAPI, service_name: str):
    """Configurer le middleware Prometheus pour FastAPI."""
    # Ajouter le middleware
    app.middleware("http")(PrometheusMiddleware(service_name))
    
    # Endpoint pour les métriques
    @app.get("/metrics")
    async def metrics():
        """Endpoint pour exposer les métriques Prometheus."""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    
    # Démarrer le collecteur de métriques système
    @app.on_event("startup")
    async def startup_event():
        collector = SystemMetricsCollector(service_name)
        await collector.start()
        app.state.metrics_collector = collector
    
    @app.on_event("shutdown")
    async def shutdown_event():
        if hasattr(app.state, "metrics_collector"):
            await app.state.metrics_collector.stop()


# Fonctions utilitaires pour les métriques métiers
def track_ml_operation(service: str, operation: str, model_type: str = ""):
    """Décorateur pour mesurer les opérations ML."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                ML_REQUESTS_TOTAL.labels(
                    service=service,
                    operation=operation,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                ML_REQUESTS_TOTAL.labels(
                    service=service,
                    operation=operation,
                    status="error"
                ).inc()
                ML_ERRORS_TOTAL.labels(
                    service=service,
                    operation=operation,
                    error_type=type(e).__name__
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                ML_PROCESSING_TIME.labels(
                    service=service,
                    operation=operation,
                    model_type=model_type
                ).observe(duration)
        
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                ML_REQUESTS_TOTAL.labels(
                    service=service,
                    operation=operation,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                ML_REQUESTS_TOTAL.labels(
                    service=service,
                    operation=operation,
                    status="error"
                ).inc()
                ML_ERRORS_TOTAL.labels(
                    service=service,
                    operation=operation,
                    error_type=type(e).__name__
                ).inc()
                raise
            finally:
                duration = time.time() - start_time
                ML_PROCESSING_TIME.labels(
                    service=service,
                    operation=operation,
                    model_type=model_type
                ).observe(duration)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def track_openai_call(service: str, model: str):
    """Décorateur pour mesurer les appels OpenAI."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                OPENAI_API_CALLS.labels(
                    service=service,
                    model=model,
                    status="success"
                ).inc()
                
                # Compter les tokens si disponibles
                if hasattr(result, "usage"):
                    if hasattr(result.usage, "prompt_tokens"):
                        OPENAI_TOKENS_USED.labels(
                            service=service,
                            model=model,
                            type="prompt"
                        ).inc(result.usage.prompt_tokens)
                    if hasattr(result.usage, "completion_tokens"):
                        OPENAI_TOKENS_USED.labels(
                            service=service,
                            model=model,
                            type="completion"
                        ).inc(result.usage.completion_tokens)
                
                return result
            except Exception as e:
                OPENAI_API_CALLS.labels(
                    service=service,
                    model=model,
                    status="error"
                ).inc()
                raise
        
        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                OPENAI_API_CALLS.labels(
                    service=service,
                    model=model,
                    status="success"
                ).inc()
                
                # Compter les tokens si disponibles
                if hasattr(result, "usage"):
                    if hasattr(result.usage, "prompt_tokens"):
                        OPENAI_TOKENS_USED.labels(
                            service=service,
                            model=model,
                            type="prompt"
                        ).inc(result.usage.prompt_tokens)
                    if hasattr(result.usage, "completion_tokens"):
                        OPENAI_TOKENS_USED.labels(
                            service=service,
                            model=model,
                            type="completion"
                        ).inc(result.usage.completion_tokens)
                
                return result
            except Exception as e:
                OPENAI_API_CALLS.labels(
                    service=service,
                    model=model,
                    status="error"
                ).inc()
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator