"""
SuperSmartMatch V2 - API Gateway (Version connectée)
Point d'entrée unifié pour orchestrer tous les microservices
Port: 5055
"""

from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
import asyncio
import httpx
import json
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
import time
import os

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Variables d'environnement
JWT_SECRET = os.getenv("JWT_SECRET", "supersecure-jwt-secret-change-in-production")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# URLs des services
SERVICE_URLS = {
    "cv_parser": os.getenv("CV_PARSER_URL", "http://cv-parser:5051"),
    "job_parser": os.getenv("JOB_PARSER_URL", "http://job-parser:5053"),
    "matching_service": os.getenv("MATCHING_SERVICE_URL", "http://matching-service:5060"),
    "nexten_api": os.getenv("NEXTEN_API_URL", "http://nexten-api:5000"),
    "nexten_data_adapter": os.getenv("NEXTEN_DATA_ADAPTER_URL", "http://nexten-data-adapter:5052"),
}

# Variables globales pour le monitoring
service_health_status = {}
request_count = 0
start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application"""
    logger.info("🚀 SuperSmartMatch V2 API Gateway démarrage...")
    logger.info(f"🔧 Mode: {ENVIRONMENT}")
    logger.info(f"🔧 Debug: {DEBUG}")
    logger.info(f"🔧 Services configurés: {list(SERVICE_URLS.keys())}")
    
    # Vérification initiale des services
    await check_all_services_health()
    
    yield
    
    logger.info("🛑 SuperSmartMatch V2 API Gateway arrêt...")

async def check_service_health(service_name: str, url: str) -> Dict[str, Any]:
    """Vérifie la santé d'un service spécifique"""
    try:
        timeout = httpx.Timeout(5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            start = time.time()
            response = await client.get(f"{url}/health")
            duration = time.time() - start
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time": round(duration, 3),
                    "status_code": response.status_code
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time": round(duration, 3),
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}"
                }
    except Exception as e:
        return {
            "status": "unreachable",
            "response_time": 0,
            "error": str(e)
        }

async def check_all_services_health():
    """Vérifie la santé de tous les services"""
    global service_health_status
    
    tasks = []
    for service_name, url in SERVICE_URLS.items():
        tasks.append(check_service_health(service_name, url))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, (service_name, _) in enumerate(SERVICE_URLS.items()):
        if isinstance(results[i], Exception):
            service_health_status[service_name] = {
                "status": "error",
                "error": str(results[i])
            }
        else:
            service_health_status[service_name] = results[i]

async def proxy_request(service_url: str, path: str, method: str = "GET", 
                       data: Any = None, files: Any = None) -> Dict[str, Any]:
    """Fonction générique pour proxifier les requêtes vers les services"""
    try:
        timeout = httpx.Timeout(30.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            url = f"{service_url}{path}"
            
            if method.upper() == "GET":
                response = await client.get(url)
            elif method.upper() == "POST":
                if files:
                    response = await client.post(url, files=files)
                elif data:
                    response = await client.post(url, json=data)
                else:
                    response = await client.post(url)
            else:
                raise HTTPException(status_code=405, detail="Method not allowed")
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                "headers": dict(response.headers)
            }
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Service timeout")
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Service unreachable: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy error: {str(e)}")

# Création de l'application FastAPI
app = FastAPI(
    title="SuperSmartMatch V2 API Gateway",
    description="Point d'entrée unifié pour la plateforme de recrutement IA",
    version="2.1.0",
    docs_url="/api/gateway/docs",
    redoc_url="/api/gateway/redoc",
    openapi_url="/api/gateway/openapi.json",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Middleware de logging et monitoring"""
    global request_count
    request_count += 1
    
    start_time_req = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time_req
    
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Gestionnaire d'exceptions HTTP personnalisé"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path),
            "timestamp": time.time()
        }
    )

@app.get("/api/gateway")
async def root():
    """Endpoint racine avec informations sur l'API Gateway"""
    await check_all_services_health()
    
    healthy_services = sum(1 for status in service_health_status.values() 
                          if status.get("status") == "healthy")
    total_services = len(service_health_status)
    
    return {
        "service": "SuperSmartMatch V2 API Gateway",
        "version": "2.1.0",
        "status": "operational",
        "mode": ENVIRONMENT,
        "uptime": round(time.time() - start_time, 2),
        "services_health": f"{healthy_services}/{total_services}",
        "endpoints": {
            "health": "/api/gateway/health",
            "status": "/api/gateway/status",
            "metrics": "/api/gateway/metrics",
            "parse_cv": "/api/gateway/parse-cv",
            "parse_job": "/api/gateway/parse-job",
            "match": "/api/gateway/match",
            "nexten": "/api/gateway/nexten",
            "docs": "/api/gateway/docs"
        },
        "message": "🌟 API Gateway unifié opérationnel avec connectivité réseau !"
    }

@app.get("/api/gateway/status")
async def simple_status():
    """Status simple pour vérifications rapides"""
    return {
        "status": "ok",
        "service": "SuperSmartMatch V2 API Gateway",
        "version": "2.1.0",
        "environment": ENVIRONMENT,
        "port": 5055,
        "timestamp": time.time(),
        "request_count": request_count
    }

@app.get("/api/gateway/health")
async def health_check():
    """Health check complet avec vérification des services"""
    await check_all_services_health()
    
    healthy_services = sum(1 for status in service_health_status.values() 
                          if status.get("status") == "healthy")
    total_services = len(service_health_status)
    health_ratio = healthy_services / total_services if total_services > 0 else 0
    
    overall_status = "healthy" if health_ratio >= 0.5 else "degraded" if health_ratio > 0 else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": time.time(),
        "uptime": round(time.time() - start_time, 2),
        "services": service_health_status,
        "gateway_info": {
            "name": "SuperSmartMatch V2 API Gateway",
            "version": "2.1.0",
            "environment": ENVIRONMENT,
            "debug_mode": DEBUG,
            "port": 5055
        },
        "performance_metrics": {
            "request_count": request_count,
            "healthy_services_ratio": round(health_ratio, 2),
            "healthy_services_count": f"{healthy_services}/{total_services}"
        }
    }

@app.get("/api/gateway/metrics")
async def get_metrics():
    """Métriques format Prometheus"""
    await check_all_services_health()
    
    healthy_services = sum(1 for status in service_health_status.values() 
                          if status.get("status") == "healthy")
    total_services = len(service_health_status)
    uptime = time.time() - start_time
    
    metrics = [
        "# HELP supersmartmatch_gateway_up Gateway availability",
        "# TYPE supersmartmatch_gateway_up gauge",
        "supersmartmatch_gateway_up 1",
        "",
        "# HELP supersmartmatch_gateway_requests_total Total requests",
        "# TYPE supersmartmatch_gateway_requests_total counter", 
        f"supersmartmatch_gateway_requests_total {request_count}",
        "",
        "# HELP supersmartmatch_gateway_uptime_seconds Gateway uptime",
        "# TYPE supersmartmatch_gateway_uptime_seconds gauge",
        f"supersmartmatch_gateway_uptime_seconds {uptime}",
        "",
        "# HELP supersmartmatch_services_healthy_total Healthy services count",
        "# TYPE supersmartmatch_services_healthy_total gauge",
        f"supersmartmatch_services_healthy_total {healthy_services}",
        "",
        "# HELP supersmartmatch_services_total Total services count",
        "# TYPE supersmartmatch_services_total gauge",
        f"supersmartmatch_services_total {total_services}"
    ]
    
    return "\n".join(metrics)

# ===== ROUTES DE PARSING =====

@app.post("/api/gateway/parse-cv")
async def parse_cv(file: UploadFile = File(...)):
    """Parser CV via le CV Parser Service"""
    try:
        service_url = SERVICE_URLS["cv_parser"]
        
        # Préparation du fichier pour envoi
        file_content = await file.read()
        files = {"file": (file.filename, file_content, file.content_type)}
        
        result = await proxy_request(service_url, "/parse", method="POST", files=files)
        
        if result["status_code"] == 200:
            return {
                "success": True,
                "data": result["data"],
                "service": "cv_parser",
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=result["status_code"], 
                              detail=f"CV Parser error: {result['data']}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Parse CV error: {e}")
        raise HTTPException(status_code=500, detail=f"Parse CV failed: {str(e)}")

@app.post("/api/gateway/parse-job")
async def parse_job(job_data: dict):
    """Parser Job via le Job Parser Service"""
    try:
        service_url = SERVICE_URLS["job_parser"]
        
        result = await proxy_request(service_url, "/parse", method="POST", data=job_data)
        
        if result["status_code"] == 200:
            return {
                "success": True,
                "data": result["data"],
                "service": "job_parser",
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=result["status_code"], 
                              detail=f"Job Parser error: {result['data']}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Parse Job error: {e}")
        raise HTTPException(status_code=500, detail=f"Parse Job failed: {str(e)}")

# ===== ROUTES DE MATCHING =====

@app.post("/api/gateway/match")
async def match_candidates(match_data: dict):
    """Matching IA via le Matching Service"""
    try:
        service_url = SERVICE_URLS["matching_service"]
        
        result = await proxy_request(service_url, "/api/v1/match", method="POST", data=match_data)
        
        if result["status_code"] == 200:
            return {
                "success": True,
                "data": result["data"],
                "service": "matching_service",
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=result["status_code"], 
                              detail=f"Matching Service error: {result['data']}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Matching error: {e}")
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")

@app.get("/api/gateway/match/algorithms")
async def get_algorithms():
    """Liste des algorithmes de matching"""
    try:
        service_url = SERVICE_URLS["matching_service"]
        
        result = await proxy_request(service_url, "/api/v1/algorithms", method="GET")
        
        if result["status_code"] == 200:
            return result["data"]
        else:
            # Fallback si le service n'est pas disponible
            return {
                "algorithms": [
                    "cosine_similarity",
                    "tfidf_matching", 
                    "bert_semantic",
                    "skills_exact_match",
                    "experience_weighted",
                    "education_match",
                    "location_proximity",
                    "hybrid_ensemble",
                    "neural_network"
                ],
                "status": "fallback_data"
            }
    
    except Exception as e:
        logger.warning(f"Could not fetch algorithms: {e}")
        # Retour des données par défaut
        return {
            "algorithms": [
                "cosine_similarity",
                "tfidf_matching", 
                "bert_semantic",
                "skills_exact_match",
                "experience_weighted",
                "education_match",
                "location_proximity",
                "hybrid_ensemble",
                "neural_network"
            ],
            "status": "fallback_data",
            "note": "Service temporarily unavailable"
        }

# ===== ROUTES NEXTEN =====

@app.get("/api/gateway/nexten/health")
async def nexten_health():
    """Health check des services Nexten"""
    try:
        nexten_api_health = await check_service_health("nexten_api", SERVICE_URLS["nexten_api"])
        nexten_adapter_health = await check_service_health("nexten_data_adapter", SERVICE_URLS["nexten_data_adapter"])
        
        return {
            "nexten_api": nexten_api_health,
            "nexten_data_adapter": nexten_adapter_health,
            "timestamp": time.time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nexten health check failed: {str(e)}")

@app.get("/api/gateway/nexten/{path:path}")
async def nexten_proxy_get(path: str):
    """Proxy GET pour Nexten API"""
    try:
        service_url = SERVICE_URLS["nexten_api"]
        result = await proxy_request(service_url, f"/{path}", method="GET")
        
        if result["status_code"] == 200:
            return result["data"]
        else:
            raise HTTPException(status_code=result["status_code"], detail=result["data"])
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nexten proxy error: {str(e)}")

@app.post("/api/gateway/nexten/{path:path}")
async def nexten_proxy_post(path: str, data: dict = None):
    """Proxy POST pour Nexten API"""
    try:
        service_url = SERVICE_URLS["nexten_api"]
        result = await proxy_request(service_url, f"/{path}", method="POST", data=data)
        
        if result["status_code"] in [200, 201]:
            return result["data"]
        else:
            raise HTTPException(status_code=result["status_code"], detail=result["data"])
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nexten proxy error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "app_simple:app",
        host="0.0.0.0",
        port=5055,
        reload=DEBUG,
        log_level="info"
    )
