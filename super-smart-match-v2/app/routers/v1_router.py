"""
Router V1 - Compatibilité avec l'API SuperSmartMatch V1

Maintient 100% de compatibilité avec les clients existants
tout en utilisant le nouveau moteur intelligent V2
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Any, Dict
import time

from ..models import MatchRequestV1, MatchResponseV1
from ..dependencies import get_service_orchestrator
from ..logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/match", response_model=MatchResponseV1)
async def match_v1(request: Request, orchestrator = Depends(get_service_orchestrator)):
    """
    Endpoint de matching V1 - Compatible avec l'existant
    
    Maintient le format de réponse V1 tout en utilisant
    le moteur intelligent V2 en arrière-plan
    """
    start_time = time.time()
    
    try:
        # Parser la requête JSON
        body = await request.json()
        logger.info(f"V1 match request received", request_size=len(str(body)))
        
        # Valider avec le modèle Pydantic
        match_request = MatchRequestV1(**body)
        
        # Exécuter le matching via l'orchestrateur
        result = await orchestrator.execute_match_v1(match_request)
        
        execution_time = int((time.time() - start_time) * 1000)
        logger.info(
            "V1 match completed", 
            execution_time_ms=execution_time,
            algorithm_used=result.algorithm_used,
            matches_count=len(result.matches)
        )
        
        return result
        
    except ValueError as e:
        logger.error(f"V1 validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request format: {e}")
    
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        logger.error(f"V1 match error: {e}", execution_time_ms=execution_time, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal matching error")

@router.get("/algorithms")
async def get_available_algorithms() -> Dict[str, Any]:
    """
    Liste des algorithmes disponibles (compatibilité V1)
    """
    return {
        "algorithms": {
            "auto": {
                "name": "Automatic Selection",
                "description": "Sélection intelligente automatique",
                "precision": "91%",
                "recommended": True
            },
            "nexten_matcher": {
                "name": "Nexten Matcher", 
                "description": "Algorithme ML avancé (40K lignes)",
                "precision": "95%",
                "use_case": "Questionnaires complets"
            },
            "enhanced_match": {
                "name": "Enhanced Match",
                "description": "Matching avancé avec pondération expérience",
                "precision": "84%",
                "use_case": "Profils seniors"
            },
            "smart_match": {
                "name": "Smart Match",
                "description": "Matching intelligent avec optimisation géo",
                "precision": "87%",
                "use_case": "Contraintes géographiques"
            },
            "semantic_match": {
                "name": "Semantic Match",
                "description": "Analyse sémantique NLP des compétences",
                "precision": "81%",
                "use_case": "Compétences complexes"
            }
        },
        "default": "auto",
        "selection_rules": {
            "nexten_priority": "Questionnaires complets (>80%)",
            "smart_priority": "Contraintes géographiques + mobilité",
            "enhanced_priority": "Expérience senior (7+ ans)",
            "semantic_priority": "Compétences complexes + NLP"
        }
    }

@router.get("/health")
async def health_v1() -> Dict[str, Any]:
    """Health check V1 compatible"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "api_version": "v1_compatible",
        "timestamp": int(time.time())
    }

@router.get("/stats")
async def get_stats_v1(orchestrator = Depends(get_service_orchestrator)) -> Dict[str, Any]:
    """Statistiques de performance (format V1)"""
    try:
        stats = await orchestrator.get_performance_stats()
        
        # Format V1 compatible
        return {
            "total_requests": stats.get("total_requests", 0),
            "average_response_time": stats.get("avg_response_time_ms", 0),
            "success_rate": stats.get("success_rate", 1.0),
            "algorithms_usage": stats.get("algorithm_usage", {}),
            "uptime_seconds": stats.get("uptime_seconds", 0)
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve stats")