"""
Router V2 - API enrichie SuperSmartMatch V2

Nouvelles fonctionnalités avancées :
- Questionnaires candidat/entreprise
- Analyse contextuelle détaillée
- Explications et insights
- Métadonnées de performance
"""

from fastapi import APIRouter, HTTPException, Request, Depends, Query
from typing import Any, Dict, Optional
import time

from ..models import MatchRequestV2, MatchResponseV2, AlgorithmType
from ..dependencies import get_service_orchestrator, get_context_analyzer
from ..logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/match", response_model=MatchResponseV2)
async def match_v2(
    match_request: MatchRequestV2, 
    orchestrator = Depends(get_service_orchestrator),
    context_analyzer = Depends(get_context_analyzer)
):
    """
    Endpoint de matching V2 - Fonctionnalités enrichies
    
    Nouvelles capacités :
    - Questionnaires candidat/entreprise
    - Sélection d'algorithme contextualisée
    - Explications détaillées des résultats
    - Métadonnées de performance complètes
    """
    start_time = time.time()
    
    try:
        logger.info(
            "V2 match request received", 
            candidate_id=match_request.candidate.id,
            offers_count=len(match_request.offers),
            algorithm=match_request.algorithm,
            has_questionnaire=match_request.candidate_questionnaire is not None
        )
        
        # Analyser le contexte pour la sélection d'algorithme
        context = await context_analyzer.analyze_request_context(match_request)
        
        # Exécuter le matching avec contexte enrichi
        result = await orchestrator.execute_match_v2(match_request, context)
        
        execution_time = int((time.time() - start_time) * 1000)
        logger.info(
            "V2 match completed",
            execution_time_ms=execution_time,
            algorithm_used=result.metadata.algorithm_used,
            matches_count=len(result.matches),
            cache_hit=result.metadata.performance_metrics.cache_hit
        )
        
        return result
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        logger.error(f"V2 match error: {e}", execution_time_ms=execution_time, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Matching error: {str(e)}")

@router.post("/analyze-context")
async def analyze_context(
    match_request: MatchRequestV2,
    context_analyzer = Depends(get_context_analyzer)
) -> Dict[str, Any]:
    """
    Analyser le contexte d'une requête sans exécuter le matching
    
    Utile pour comprendre quelle logique de sélection sera appliquée
    """
    try:
        context = await context_analyzer.analyze_request_context(match_request)
        algorithm_recommendation = await context_analyzer.recommend_algorithm(context)
        
        return {
            "context_analysis": context.dict(),
            "recommended_algorithm": algorithm_recommendation,
            "selection_reasoning": await context_analyzer.get_selection_reasoning(context),
            "estimated_performance": await context_analyzer.estimate_performance(context)
        }
        
    except Exception as e:
        logger.error(f"Context analysis error: {e}")
        raise HTTPException(status_code=500, detail="Context analysis failed")

@router.get("/algorithms/detailed")
async def get_algorithms_detailed() -> Dict[str, Any]:
    """
    Information détaillée sur les algorithmes disponibles
    """
    return {
        "algorithms": {
            "nexten_matcher": {
                "name": "Nexten Matcher",
                "type": "machine_learning",
                "precision": 0.95,
                "typical_response_time_ms": 75,
                "strengths": [
                    "Précision maximale avec questionnaires complets",
                    "Apprentissage continu et adaptation",
                    "Analyse comportementale avancée"
                ],
                "optimal_conditions": {
                    "questionnaire_completeness": ">= 0.8",
                    "data_richness": "high",
                    "use_cases": ["matching_premium", "enterprise_clients"]
                },
                "limitations": [
                    "Temps de réponse plus élevé",
                    "Nécessite des données riches"
                ]
            },
            "enhanced_match": {
                "name": "Enhanced Match",
                "type": "rule_based_advanced",
                "precision": 0.84,
                "typical_response_time_ms": 25,
                "strengths": [
                    "Optimisé pour les profils seniors",
                    "Pondération intelligente de l'expérience",
                    "Rapide et fiable"
                ],
                "optimal_conditions": {
                    "experience_years": ">= 7",
                    "profile_completeness": ">= 0.6",
                    "use_cases": ["senior_matching", "executive_search"]
                }
            },
            "smart_match": {
                "name": "Smart Match",
                "type": "geo_optimized",
                "precision": 0.87,
                "typical_response_time_ms": 20,
                "strengths": [
                    "Optimisation géographique avancée",
                    "Calcul de temps de trajet",
                    "Très rapide"
                ],
                "optimal_conditions": {
                    "has_location_data": True,
                    "mobility_constraints": True,
                    "use_cases": ["local_matching", "commute_optimization"]
                }
            },
            "semantic_match": {
                "name": "Semantic Match", 
                "type": "nlp_semantic",
                "precision": 0.81,
                "typical_response_time_ms": 45,
                "strengths": [
                    "Analyse sémantique des compétences",
                    "Compréhension du contexte métier",
                    "Détection de synonymes et compétences liées"
                ],
                "optimal_conditions": {
                    "skills_complexity": ">= 0.6",
                    "text_analysis_needed": True,
                    "use_cases": ["complex_skills", "emerging_technologies"]
                }
            }
        },
        "selection_matrix": {
            "high_precision_needed": "nexten_matcher",
            "geographic_constraints": "smart_match",
            "senior_profiles": "enhanced_match",
            "complex_skills": "semantic_match",
            "fast_response_needed": "smart_match",
            "rich_questionnaire_data": "nexten_matcher"
        },
        "performance_targets": {
            "overall_precision": 0.91,
            "max_response_time_ms": 100,
            "availability_target": 0.999
        }
    }

@router.get("/performance/metrics")
async def get_performance_metrics(
    time_range: Optional[str] = Query("1h", description="Plage temporelle: 1h, 6h, 24h, 7d"),
    orchestrator = Depends(get_service_orchestrator)
) -> Dict[str, Any]:
    """
    Métriques de performance détaillées
    """
    try:
        metrics = await orchestrator.get_detailed_metrics(time_range)
        
        return {
            "time_range": time_range,
            "overview": {
                "total_requests": metrics.get("total_requests", 0),
                "success_rate": metrics.get("success_rate", 1.0),
                "average_precision": metrics.get("avg_precision", 0.91),
                "p95_response_time_ms": metrics.get("p95_response_time", 0)
            },
            "algorithm_performance": metrics.get("algorithm_stats", {}),
            "error_analysis": metrics.get("error_breakdown", {}),
            "cache_performance": {
                "hit_rate": metrics.get("cache_hit_rate", 0),
                "miss_rate": metrics.get("cache_miss_rate", 0),
                "eviction_rate": metrics.get("cache_eviction_rate", 0)
            },
            "circuit_breaker_status": metrics.get("circuit_breaker_stats", {})
        }
        
    except Exception as e:
        logger.error(f"Performance metrics error: {e}")
        raise HTTPException(status_code=500, detail="Unable to retrieve performance metrics")

@router.post("/test-algorithm")
async def test_algorithm(
    algorithm: AlgorithmType,
    match_request: MatchRequestV2,
    orchestrator = Depends(get_service_orchestrator)
) -> Dict[str, Any]:
    """
    Tester un algorithme spécifique (mode debug)
    
    Permet de forcer l'utilisation d'un algorithme particulier
    pour des tests et comparaisons
    """
    try:
        # Forcer l'algorithme spécifié
        match_request.algorithm = algorithm
        
        start_time = time.time()
        result = await orchestrator.execute_algorithm_directly(algorithm, match_request)
        execution_time = int((time.time() - start_time) * 1000)
        
        return {
            "algorithm_tested": algorithm,
            "execution_time_ms": execution_time,
            "matches_count": len(result.get("matches", [])),
            "success": True,
            "results": result,
            "performance_note": "Test mode - circuit breakers and fallbacks disabled"
        }
        
    except Exception as e:
        logger.error(f"Algorithm test error: {e}")
        raise HTTPException(status_code=500, detail=f"Algorithm test failed: {str(e)}")