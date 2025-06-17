#!/usr/bin/env python3
"""API Gateway for SuperSmartMatch V3.0 Enhanced"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import httpx
import asyncio
from datetime import datetime
from typing import Dict, Any

app = FastAPI(
    title="SuperSmartMatch V3.0 Enhanced - API Gateway",
    description="Gateway central pour tous les services SuperSmartMatch",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration des services
SERVICES = {
    "cv_parser": "http://localhost:5051",
    "job_parser": "http://localhost:5053", 
    "supersmartmatch": "http://localhost:5067",
    "dashboard": "http://localhost:5070",
    "data_adapter": "http://localhost:8000"
}

@app.get("/health")
async def health():
    """Point de contrôle de santé de l'API Gateway"""
    return {
        "status": "healthy",
        "service": "api_gateway", 
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """Page d'accueil de l'API Gateway"""
    return {
        "message": "🎯 SuperSmartMatch V3.0 Enhanced API Gateway",
        "description": "Gateway central pour tous les services SuperSmartMatch",
        "version": "3.0.0",
        "performance": {
            "accuracy": "98.6%",
            "response_time": "6.9-35ms",
            "algorithms": 7
        },
        "services": SERVICES,
        "endpoints": {
            "health_check": "/services/health",
            "service_status": "/services/status",
            "routing": "/services/{service_name}/{path:path}"
        },
        "documentation": "/docs"
    }

@app.get("/services/health")
async def check_all_services_health():
    """Vérifie la santé de tous les services"""
    health_status = {}
    overall_healthy = True
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health")
                if response.status_code == 200:
                    health_status[service_name] = {
                        "status": "healthy",
                        "url": service_url,
                        "response_time": response.elapsed.total_seconds() * 1000
                    }
                else:
                    health_status[service_name] = {
                        "status": "unhealthy",
                        "url": service_url,
                        "error": f"HTTP {response.status_code}"
                    }
                    overall_healthy = False
            except Exception as e:
                health_status[service_name] = {
                    "status": "offline",
                    "url": service_url,
                    "error": str(e)
                }
                overall_healthy = False
    
    return {
        "overall_status": "healthy" if overall_healthy else "degraded",
        "timestamp": datetime.now().isoformat(),
        "services": health_status,
        "summary": {
            "total": len(SERVICES),
            "healthy": len([s for s in health_status.values() if s["status"] == "healthy"]),
            "unhealthy": len([s for s in health_status.values() if s["status"] != "healthy"])
        }
    }

@app.get("/services/status")
async def get_services_status():
    """Statut détaillé de tous les services SuperSmartMatch"""
    return {
        "platform": "SuperSmartMatch V3.0 Enhanced",
        "gateway_version": "3.0.0",
        "timestamp": datetime.now().isoformat(),
        "services_configuration": {
            "cv_parser": {
                "url": SERVICES["cv_parser"],
                "port": 5051,
                "description": "Service de parsing de CV multi-formats",
                "formats": ["PDF", "DOCX", "DOC", "TXT", "PNG", "JPG", "JPEG"]
            },
            "job_parser": {
                "url": SERVICES["job_parser"],
                "port": 5053,
                "description": "Service de parsing de descriptions de poste",
                "capabilities": ["Skills extraction", "Experience parsing", "Salary detection"]
            },
            "supersmartmatch": {
                "url": SERVICES["supersmartmatch"],
                "port": 5067,
                "description": "Moteur de matching Enhanced V3.0",
                "performance": {
                    "accuracy": "98.6%",
                    "response_time": "6.9-35ms"
                },
                "algorithms": [
                    "Enhanced_V3.0", "Semantic_V2.1", "Weighted_Skills",
                    "Experience_Based", "Hybrid_ML", "Fuzzy_Logic", "Neural_Network"
                ]
            },
            "dashboard": {
                "url": SERVICES["dashboard"],
                "port": 5070,
                "description": "Interface web Streamlit",
                "features": ["Real-time matching", "Performance metrics", "Multi-format upload"]
            },
            "data_adapter": {
                "url": SERVICES["data_adapter"],
                "port": 8000,
                "description": "API de matching complète",
                "endpoints": ["/api/matching/complete", "/api/matching/single", "/api/matching/batch"]
            }
        },
        "architecture": {
            "microservices": True,
            "load_balancing": "Gateway routing",
            "monitoring": "Health checks",
            "caching": "In-memory + Redis ready"
        }
    }

@app.api_route("/services/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_service(service_name: str, path: str, request):
    """Route les requêtes vers les services appropriés"""
    
    if service_name not in SERVICES:
        raise HTTPException(
            status_code=404, 
            detail=f"Service '{service_name}' non trouvé. Services disponibles: {list(SERVICES.keys())}"
        )
    
    service_url = SERVICES[service_name]
    target_url = f"{service_url}/{path}"
    
    # Lire le body de la requête
    body = await request.body()
    
    # Copier les headers (en excluant ceux problématiques)
    headers = dict(request.headers)
    excluded_headers = {'host', 'content-length', 'connection'}
    headers = {k: v for k, v in headers.items() if k.lower() not in excluded_headers}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=dict(request.query_params)
            )
            
            # Retourner la réponse du service
            return JSONResponse(
                content=response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail=f"Timeout lors de la communication avec le service {service_name}"
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail=f"Impossible de se connecter au service {service_name} sur {service_url}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la communication avec {service_name}: {str(e)}"
        )

@app.get("/docs-all")
async def get_all_docs():
    """Liens vers la documentation de tous les services"""
    return {
        "message": "Documentation de tous les services SuperSmartMatch V3.0 Enhanced",
        "docs_links": {
            "api_gateway": "/docs",
            "cv_parser": f"{SERVICES['cv_parser']}/docs",
            "job_parser": f"{SERVICES['job_parser']}/docs",
            "supersmartmatch": f"{SERVICES['supersmartmatch']}/docs",
            "data_adapter": f"{SERVICES['data_adapter']}/docs",
            "dashboard": SERVICES['dashboard']
        },
        "quick_tests": {
            "health_all": "/services/health",
            "cv_parser_health": "/services/cv_parser/health",
            "job_parser_health": "/services/job_parser/health",
            "supersmartmatch_health": "/services/supersmartmatch/health"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "api_gateway:app",
        host="0.0.0.0",
        port=5065,
        reload=True,
        log_level="info"
    )