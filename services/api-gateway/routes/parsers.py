"""
Routes pour les parsers CV et Job
Redirection intelligente vers les microservices avec authentification
"""

from fastapi import APIRouter, Depends, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from typing import Optional
import logging

from routes.auth import get_current_user
from utils.proxy import forward_to_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Routes CV Parser
@router.post("/parse-cv")
async def parse_cv(
    request: Request,
    file: UploadFile = File(...),
    extract_skills: bool = Form(True),
    extract_experience: bool = Form(True),
    extract_education: bool = Form(True),
    extract_languages: bool = Form(True),
    current_user: dict = Depends(get_current_user)
):
    """
    Parser un CV en utilisant le service CV Parser
    Supporte 8 formats : PDF, DOCX, DOC, Images (OCR), TXT, CSV, HTML, RTF, ODT
    """
    try:
        logger.info(f"Parsing CV pour utilisateur {current_user['email']}")
        
        # Lire le contenu du fichier
        file_content = await file.read()
        
        # Préparer les données pour le service CV Parser
        files = {
            "file": (file.filename, file_content, file.content_type)
        }
        
        data = {
            "extract_skills": str(extract_skills).lower(),
            "extract_experience": str(extract_experience).lower(),
            "extract_education": str(extract_education).lower(),
            "extract_languages": str(extract_languages).lower()
        }
        
        # Créer une nouvelle requête pour le proxy
        from fastapi import Request as FastAPIRequest
        from starlette.datastructures import QueryParams, Headers
        
        # Simuler une requête POST pour le proxy
        proxy_request = type('Request', (), {
            'method': 'POST',
            'headers': dict(request.headers),
            'query_params': QueryParams(),
            'url': type('URL', (), {'path': '/api/parse-cv/'})()
        })()
        
        # Rediriger vers le service CV Parser
        response = await forward_to_service_with_files(
            service_name="cv_parser",
            path="api/parse-cv/",
            request=proxy_request,
            files=files,
            data=data
        )
        
        logger.info(f"CV parsé avec succès pour {current_user['email']}")
        return response
        
    except Exception as e:
        logger.error(f"Erreur parsing CV: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du parsing du CV: {str(e)}")

@router.get("/parse-cv/formats")
async def get_supported_cv_formats(current_user: dict = Depends(get_current_user)):
    """Obtenir la liste des formats supportés pour les CV"""
    try:
        response = await forward_to_service(
            service_name="cv_parser",
            path="api/formats",
            request=Request(scope={"type": "http", "method": "GET"})
        )
        return response
    except Exception as e:
        logger.error(f"Erreur récupération formats CV: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des formats")

# Routes Job Parser  
@router.post("/parse-job")
async def parse_job(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Parser une offre d'emploi en utilisant le service Job Parser
    Accepte du JSON avec les détails de l'offre
    """
    try:
        logger.info(f"Parsing job pour utilisateur {current_user['email']}")
        
        # Lire le body de la requête
        body = await request.body()
        
        # Rediriger vers le service Job Parser
        response = await forward_to_service(
            service_name="job_parser",
            path="api/parse-job",
            request=request,
            body=body
        )
        
        logger.info(f"Job parsé avec succès pour {current_user['email']}")
        return response
        
    except Exception as e:
        logger.error(f"Erreur parsing job: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du parsing du job: {str(e)}")

@router.post("/parse-job/url")
async def parse_job_from_url(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Parser une offre d'emploi depuis une URL"""
    try:
        logger.info(f"Parsing job depuis URL pour utilisateur {current_user['email']}")
        
        body = await request.body()
        
        response = await forward_to_service(
            service_name="job_parser",
            path="api/parse-job/url",
            request=request,
            body=body
        )
        
        logger.info(f"Job depuis URL parsé avec succès pour {current_user['email']}")
        return response
        
    except Exception as e:
        logger.error(f"Erreur parsing job depuis URL: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du parsing du job depuis URL: {str(e)}")

@router.post("/parse-job/batch")
async def parse_job_batch(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Parser plusieurs offres d'emploi en lot"""
    try:
        logger.info(f"Parsing batch jobs pour utilisateur {current_user['email']}")
        
        # Vérifier le rôle (seuls recruteurs et admins peuvent faire du batch)
        if current_user.get("role") not in ["recruteur", "admin"]:
            raise HTTPException(
                status_code=403, 
                detail="Seuls les recruteurs et admins peuvent faire du parsing en lot"
            )
        
        body = await request.body()
        
        response = await forward_to_service(
            service_name="job_parser",
            path="api/parse-job/batch",
            request=request,
            body=body
        )
        
        logger.info(f"Batch jobs parsé avec succès pour {current_user['email']}")
        return response
        
    except Exception as e:
        logger.error(f"Erreur parsing batch jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lors du parsing batch: {str(e)}")

# Routes de statistiques et monitoring
@router.get("/parsers/stats")
async def get_parsers_stats(current_user: dict = Depends(get_current_user)):
    """Obtenir les statistiques des parsers"""
    try:
        # Vérifier le rôle admin
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Accès admin requis")
        
        # Récupérer les stats des deux services
        cv_request = Request(scope={"type": "http", "method": "GET"})
        job_request = Request(scope={"type": "http", "method": "GET"})
        
        cv_stats_response = await forward_to_service(
            service_name="cv_parser",
            path="api/stats",
            request=cv_request
        )
        
        job_stats_response = await forward_to_service(
            service_name="job_parser", 
            path="api/stats",
            request=job_request
        )
        
        return {
            "cv_parser": cv_stats_response,
            "job_parser": job_stats_response
        }
        
    except Exception as e:
        logger.error(f"Erreur récupération stats parsers: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des stats")

# Fonction utilitaire pour gérer les uploads de fichiers
async def forward_to_service_with_files(
    service_name: str,
    path: str,
    request: Request,
    files: dict = None,
    data: dict = None
) -> Response:
    """
    Fonction spécialisée pour rediriger des requêtes avec fichiers
    """
    from utils.proxy import proxy_manager
    import httpx
    
    proxy = proxy_manager.get_proxy(service_name)
    url = proxy.get_next_url()
    
    if not url:
        raise HTTPException(status_code=503, detail=f"Service {service_name} indisponible")
    
    full_url = f"{url.rstrip('/')}/{path.lstrip('/')}"
    
    try:
        # Préparer les headers (sans content-length et host)
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
        
        # Faire la requête avec fichiers
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url=full_url,
                headers=headers,
                files=files,
                data=data
            )
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
        
    except Exception as e:
        logger.error(f"Erreur proxy avec fichiers vers {full_url}: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur communication service: {str(e)}")
