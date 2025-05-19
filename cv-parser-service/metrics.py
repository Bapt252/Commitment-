# Middleware Prometheus pour FastAPI - Service CV Parser
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
import time
import psutil
import os

# Métriques HTTP
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

# Métriques business spécifiques au CV parser
cv_parsing_requests_total = Counter(
    'cv_parsing_requests_total',
    'Total CV parsing requests',
    ['status', 'file_type']
)

cv_parsing_duration_seconds = Histogram(
    'cv_parsing_duration_seconds',
    'CV parsing duration in seconds',
    ['file_type']
)

cv_files_processed_total = Counter(
    'cv_files_processed_total',
    'Total CV files processed successfully'
)

# Métriques système
system_cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

system_memory_usage = Gauge(
    'system_memory_usage_percent',
    'System memory usage percentage'
)

# Métriques de file d'attente Redis
redis_queue_size = Gauge(
    'redis_queue_size',
    'Redis queue size',
    ['queue_name']
)

# Métriques OpenAI
openai_requests_total = Counter(
    'openai_requests_total',
    'Total requests to OpenAI API',
    ['model', 'status']
)

openai_tokens_used_total = Counter(
    'openai_tokens_used_total',
    'Total tokens used with OpenAI',
    ['model', 'type']  # type: prompt, completion
)

openai_request_duration_seconds = Histogram(
    'openai_request_duration_seconds',
    'OpenAI request duration in seconds',
    ['model']
)

# Middleware FastAPI pour les métriques
class PrometheusMiddleware:
    def __init__(self, app: FastAPI):
        self.app = app
        self.update_system_metrics()

    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        # Extraire l'endpoint (sans les paramètres)
        endpoint = request.url.path
        method = request.method
        
        # Traiter la requête
        response = await call_next(request)
        
        # Calculer la durée
        duration = time.time() - start_time
        
        # Enregistrer les métriques
        status = str(response.status_code)
        http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
        
        return response

    def update_system_metrics(self):
        """Met à jour les métriques système"""
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        system_cpu_usage.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        system_memory_usage.set(memory.percent)

# Fonctions helpers pour enregistrer les métriques métier
def record_cv_parsing_request(status: str, file_type: str):
    """Enregistre une demande de parsing de CV"""
    cv_parsing_requests_total.labels(status=status, file_type=file_type).inc()

def record_cv_parsing_duration(duration: float, file_type: str):
    """Enregistre la durée de parsing d'un CV"""
    cv_parsing_duration_seconds.labels(file_type=file_type).observe(duration)

def record_cv_processed():
    """Enregistre un CV traité avec succès"""
    cv_files_processed_total.inc()

def record_openai_request(model: str, status: str, duration: float):
    """Enregistre une requête OpenAI"""
    openai_requests_total.labels(model=model, status=status).inc()
    openai_request_duration_seconds.labels(model=model).observe(duration)

def record_openai_tokens(model: str, prompt_tokens: int, completion_tokens: int):
    """Enregistre l'utilisation de tokens OpenAI"""
    openai_tokens_used_total.labels(model=model, type='prompt').inc(prompt_tokens)
    openai_tokens_used_total.labels(model=model, type='completion').inc(completion_tokens)

def update_redis_queue_metrics(queue_name: str, size: int):
    """Met à jour les métriques de file d'attente Redis"""
    redis_queue_size.labels(queue_name=queue_name).set(size)

# Endpoint pour exposer les métriques
async def metrics_endpoint():
    """Endpoint pour Prometheus"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Configuration FastAPI
def setup_metrics(app: FastAPI):
    """Configure les métriques Prometheus pour l'application FastAPI"""
    # Ajouter le middleware
    middleware = PrometheusMiddleware(app)
    app.middleware("http")(middleware)
    
    # Ajouter l'endpoint des métriques
    app.get("/metrics")(metrics_endpoint)
    
    # Planifier la mise à jour des métriques système
    import asyncio
    
    async def update_metrics_periodically():
        while True:
            middleware.update_system_metrics()
            await asyncio.sleep(30)  # Mise à jour toutes les 30 secondes
    
    # Démarrer la tâche de mise à jour en arrière-plan
    @app.on_event("startup")
    async def startup_event():
        asyncio.create_task(update_metrics_periodically())

# Exemple d'utilisation dans le code métier
"""
# Dans votre fonction de parsing de CV:
import time
from .metrics import record_cv_parsing_request, record_cv_parsing_duration, record_cv_processed

async def parse_cv(file_path: str, file_type: str):
    start_time = time.time()
    
    try:
        # Votre logique de parsing ici
        result = await your_parsing_logic(file_path)
        
        # Enregistrer le succès
        record_cv_parsing_request("success", file_type)
        record_cv_processed()
        
        return result
        
    except Exception as e:
        # Enregistrer l'échec
        record_cv_parsing_request("error", file_type)
        raise
        
    finally:
        # Enregistrer la durée
        duration = time.time() - start_time
        record_cv_parsing_duration(duration, file_type)

# Dans votre client OpenAI:
async def call_openai(prompt: str, model: str = "gpt-4o-mini"):
    start_time = time.time()
    
    try:
        response = await openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Enregistrer le succès et les tokens
        duration = time.time() - start_time
        record_openai_request(model, "success", duration)
        record_openai_tokens(
            model,
            response.usage.prompt_tokens,
            response.usage.completion_tokens
        )
        
        return response
        
    except Exception as e:
        # Enregistrer l'échec
        duration = time.time() - start_time
        record_openai_request(model, "error", duration)
        raise
"""