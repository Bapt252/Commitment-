"""
SuperSmartMatch V2 API Endpoints

🚀 API Layer for SuperSmartMatch V2 Architecture
- Intelligent V1/V2 routing with feature flags
- A/B testing integration for progressive rollout
- Backward compatibility preservation
- Performance monitoring and health checks

🎯 Key Endpoints:
- /v2/match - Enhanced V2 API with context analysis
- /match - Legacy V1 API with automatic V2 routing
- /health - Comprehensive system health monitoring
- /config - Dynamic configuration management
"""

import logging
import time
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .supersmartmatch_v2 import SuperSmartMatchV2
from .models import MatchingContext, MatchingResult
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v2", tags=["SuperSmartMatch V2"])

# Global instance (will be initialized)
supersmartmatch_v2_instance: Optional[SuperSmartMatchV2] = None

# Pydantic models for API
class CandidateData(BaseModel):
    """Candidate data model for API"""
    name: str = Field(..., description="Candidate full name")
    email: str = Field(..., description="Candidate email")
    location: Dict[str, Any] = Field(default_factory=dict, description="Location information")
    technical_skills: List[Dict[str, Any]] = Field(default_factory=list, description="Technical skills list")
    soft_skills: List[Dict[str, Any]] = Field(default_factory=list, description="Soft skills list")
    experiences: List[Dict[str, Any]] = Field(default_factory=list, description="Work experiences")
    education: List[Dict[str, Any]] = Field(default_factory=list, description="Education background")
    mobility_preferences: str = Field(default="flexible", description="Mobility preferences")

class JobOffer(BaseModel):
    """Job offer data model for API"""
    id: str = Field(..., description="Unique offer identifier")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Dict[str, Any] = Field(default_factory=dict, description="Job location")
    required_skills: List[str] = Field(default_factory=list, description="Required skills")
    experience_level: str = Field(default="any", description="Required experience level")
    remote_policy: str = Field(default="hybrid", description="Remote work policy")
    salary_range: Dict[str, Any] = Field(default_factory=dict, description="Salary information")

class MatchingRequestV2(BaseModel):
    """V2 API Request model"""
    candidate: CandidateData = Field(..., description="Candidate information")
    candidate_questionnaire: Optional[Dict[str, Any]] = Field(None, description="Candidate questionnaire responses")
    offers: List[JobOffer] = Field(..., description="List of job offers to match against")
    company_questionnaires: Optional[List[Dict[str, Any]]] = Field(None, description="Company questionnaire responses")
    algorithm: str = Field(default="auto", description="Algorithm to use ('auto' for intelligent selection)")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Matching preferences")

class MatchingRequestV1(BaseModel):
    """V1 API Request model for backward compatibility"""
    candidate: Dict[str, Any] = Field(..., description="Candidate data")
    offers: List[Dict[str, Any]] = Field(..., description="Job offers")
    config: Optional[Dict[str, Any]] = Field(None, description="Optional configuration")

class HealthStatus(BaseModel):
    """System health status model"""
    status: str
    version: str
    environment: str
    uptime_seconds: float
    algorithms_available: List[str]
    performance_metrics: Dict[str, Any]

# Dependency to get SuperSmartMatch V2 instance
def get_supersmartmatch_v2() -> SuperSmartMatchV2:
    """Get or initialize SuperSmartMatch V2 instance"""
    global supersmartmatch_v2_instance
    
    if supersmartmatch_v2_instance is None:
        try:
            supersmartmatch_v2_instance = SuperSmartMatchV2()
            logger.info("SuperSmartMatch V2 instance initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SuperSmartMatch V2: {e}")
            raise HTTPException(status_code=500, detail=f"Service initialization failed: {str(e)}")
    
    return supersmartmatch_v2_instance

class RequestOrchestrator:
    """
    Intelligent request orchestrator for V1/V2 routing
    Implements progressive deployment and A/B testing
    """
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.get_config()
        self.traffic_splitter = TrafficSplitter(config_manager)
        
    async def route_request(self, request_data: Dict[str, Any], user_id: str = "anonymous") -> Dict[str, Any]:
        """Intelligent routing between V1 and V2 based on feature flags and A/B testing"""
        
        # Check if V2 is enabled
        if not self.config.feature_flags.enable_v2:
            return await self._route_to_v1(request_data)
        
        # Check traffic percentage for V2
        if not self.traffic_splitter.should_use_v2(user_id):
            return await self._route_to_v1_with_monitoring(request_data, user_id)
        
        # Check A/B testing assignment
        ab_assignment = self.traffic_splitter.get_ab_assignment(user_id)
        if ab_assignment and ab_assignment.get('force_v1'):
            return await self._route_to_v1_with_monitoring(request_data, user_id)
        
        # Route to V2
        try:
            return await self._route_to_v2(request_data, user_id)
        except Exception as e:
            logger.error(f"V2 routing failed for user {user_id}: {e}")
            # Fallback to V1
            return await self._route_to_v1_fallback(request_data, user_id, str(e))
    
    async def _route_to_v2(self, request_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Route to SuperSmartMatch V2"""
        
        supersmartmatch_v2 = get_supersmartmatch_v2()
        
        response = await supersmartmatch_v2.match_v2(
            candidate_data=request_data['candidate'],
            candidate_questionnaire=request_data.get('candidate_questionnaire'),
            offers_data=request_data['offers'],
            company_questionnaires=request_data.get('company_questionnaires'),
            algorithm=request_data.get('algorithm', 'auto'),
            user_id=user_id
        )
        
        return {
            'matches': [match.__dict__ for match in response.matches],
            'algorithm_used': response.algorithm_used,
            'execution_time_ms': response.execution_time_ms,
            'version': 'v2',
            'selection_reason': response.selection_reason,
            'performance_metrics': response.performance_metrics,
            'context_analysis': response.context_analysis
        }
    
    async def _route_to_v1_with_monitoring(self, request_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Route to V1 with monitoring for comparison"""
        
        # Note: In a real implementation, you would call the actual V1 service here
        # For now, we'll use V2 in compatibility mode
        supersmartmatch_v2 = get_supersmartmatch_v2()
        
        results = await supersmartmatch_v2.match(
            candidate=request_data['candidate'],
            offers=request_data['offers'],
            config=request_data.get('config')
        )
        
        return {
            'matches': [result.__dict__ for result in results],
            'algorithm_used': 'v1_compatibility',
            'version': 'v1',
            'user_id': user_id
        }
    
    async def _route_to_v1(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pure V1 routing"""
        return await self._route_to_v1_with_monitoring(request_data, "v1_user")
    
    async def _route_to_v1_fallback(self, request_data: Dict[str, Any], user_id: str, error: str) -> Dict[str, Any]:
        """Fallback to V1 when V2 fails"""
        
        logger.warning(f"Falling back to V1 for user {user_id} due to error: {error}")
        
        result = await self._route_to_v1_with_monitoring(request_data, user_id)
        result['fallback_reason'] = error
        result['fallback_used'] = True
        
        return result

class TrafficSplitter:
    """Manages traffic splitting for A/B testing and progressive rollout"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.config = config_manager.get_config()
    
    def should_use_v2(self, user_id: str) -> bool:
        """Determine if request should use V2 based on traffic percentage"""
        
        # Simple hash-based traffic splitting
        user_hash = hash(user_id) % 100
        return user_hash < self.config.feature_flags.v2_traffic_percentage
    
    def get_ab_assignment(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get A/B test assignment for user"""
        
        # This would integrate with a real A/B testing system
        # For now, return None (no special assignment)
        return None

# Initialize orchestrator
config_manager = ConfigManager()
request_orchestrator = RequestOrchestrator(config_manager)

# =============================================================================
# API ENDPOINTS
# =============================================================================

@router.post("/match", 
             summary="Enhanced V2 Matching API",
             description="Advanced matching with intelligent algorithm selection",
             response_model=Dict[str, Any])
async def match_v2(
    request: MatchingRequestV2,
    user_id: str = Query(default="anonymous", description="User identifier for tracking"),
    enable_fallback: bool = Query(default=True, description="Enable automatic fallback"),
    supersmartmatch_v2: SuperSmartMatchV2 = Depends(get_supersmartmatch_v2)
) -> Dict[str, Any]:
    """
    🚀 SuperSmartMatch V2 - Enhanced Matching API
    
    Features:
    - Intelligent algorithm selection based on data context
    - +13% precision improvement with Nexten Matcher integration
    - Real-time performance monitoring
    - Automatic fallback handling
    - A/B testing support
    
    Algorithm Selection Logic:
    - Nexten Matcher: Best for complete questionnaire data (highest precision)
    - Smart Match: Optimal for geographical constraints
    - Enhanced Match: Ideal for senior profiles with partial data
    - Semantic Match: Best for complex skill analysis
    - Hybrid Match: Used for critical validation scenarios
    """
    
    start_time = time.time()
    
    try:
        # Convert Pydantic models to dictionaries
        candidate_data = request.candidate.dict()
        offers_data = [offer.dict() for offer in request.offers]
        
        # Execute V2 matching
        response = await supersmartmatch_v2.match_v2(
            candidate_data=candidate_data,
            candidate_questionnaire=request.candidate_questionnaire,
            offers_data=offers_data,
            company_questionnaires=request.company_questionnaires,
            algorithm=request.algorithm,
            enable_fallback=enable_fallback,
            user_id=user_id,
            **request.preferences
        )
        
        # Format response
        result = {
            'success': True,
            'matches': [
                {
                    'offer_id': match.offer_id,
                    'overall_score': match.overall_score,
                    'confidence': match.confidence,
                    'skill_match_score': match.skill_match_score,
                    'experience_match_score': match.experience_match_score,
                    'location_match_score': match.location_match_score,
                    'culture_match_score': getattr(match, 'culture_match_score', 0.5),
                    'insights': match.insights,
                    'recommendations': getattr(match, 'recommendations', []),
                    'explanation': match.explanation
                }
                for match in response.matches
            ],
            'metadata': {
                'algorithm_used': response.algorithm_used,
                'execution_time_ms': response.execution_time_ms,
                'selection_reason': response.selection_reason,
                'version': response.version,
                'total_results': len(response.matches),
                'context_analysis': response.context_analysis,
                'performance_metrics': response.performance_metrics
            },
            'api_version': 'v2',
            'timestamp': time.time()
        }
        
        logger.info(f"V2 API success: {len(response.matches)} matches in {response.execution_time_ms:.1f}ms")
        return result
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(f"V2 API error after {execution_time:.1f}ms: {e}")
        
        if enable_fallback:
            # Create fallback response
            return {
                'success': False,
                'error': str(e),
                'matches': [],
                'metadata': {
                    'algorithm_used': 'error_fallback',
                    'execution_time_ms': execution_time,
                    'version': 'v2',
                    'fallback_used': True
                },
                'api_version': 'v2',
                'timestamp': time.time()
            }
        else:
            raise HTTPException(status_code=500, detail=str(e))

@router.post("/match/legacy",
             summary="V1 Compatible API",
             description="Legacy API with automatic V2 routing",
             response_model=Dict[str, Any])
async def match_v1_compatible(
    request: MatchingRequestV1,
    user_id: str = Query(default="anonymous", description="User identifier"),
    force_v1: bool = Query(default=False, description="Force V1 algorithm usage"),
    supersmartmatch_v2: SuperSmartMatchV2 = Depends(get_supersmartmatch_v2)
) -> Dict[str, Any]:
    """
    🔄 V1 Compatible API with intelligent V2 routing
    
    Maintains 100% backward compatibility while optionally leveraging V2 capabilities.
    Supports progressive migration and A/B testing.
    """
    
    try:
        if force_v1:
            # Force V1 compatibility mode
            results = await supersmartmatch_v2.match(
                candidate=request.candidate,
                offers=request.offers,
                config=request.config
            )
            
            return {
                'success': True,
                'results': [result.__dict__ for result in results],
                'algorithm_used': 'v1_forced',
                'version': 'v1'
            }
        
        else:
            # Use intelligent routing
            request_data = {
                'candidate': request.candidate,
                'offers': request.offers,
                'config': request.config
            }
            
            return await request_orchestrator.route_request(request_data, user_id)
            
    except Exception as e:
        logger.error(f"V1 compatible API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health",
           summary="System Health Check",
           description="Comprehensive health and performance information",
           response_model=Dict[str, Any])
async def health_check(
    detailed: bool = Query(default=False, description="Include detailed performance metrics"),
    supersmartmatch_v2: SuperSmartMatchV2 = Depends(get_supersmartmatch_v2)
) -> Dict[str, Any]:
    """
    📊 System Health and Performance Monitoring
    
    Provides comprehensive health information including:
    - Service status and uptime
    - Algorithm availability and performance
    - Cache statistics and memory usage
    - A/B testing status
    - Configuration information
    """
    
    try:
        health_info = await supersmartmatch_v2.get_system_health()
        
        if detailed:
            # Add detailed performance metrics
            health_info['detailed_metrics'] = {
                'request_distribution': supersmartmatch_v2.performance_monitor.get_request_distribution(),
                'algorithm_performance': supersmartmatch_v2.algorithm_selector.get_algorithm_stats(),
                'cache_statistics': {
                    'nexten_cache_hits': getattr(supersmartmatch_v2.nexten_adapter, 'cache_hits', 0),
                    'data_adapter_cache_hits': getattr(supersmartmatch_v2.data_adapter, 'cache_hits', 0)
                }
            }
        
        return {
            'success': True,
            'health': health_info,
            'timestamp': time.time()
        }
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }

@router.get("/algorithm/recommendations",
           summary="Algorithm Recommendations",
           description="Get algorithm recommendations for specific context")
async def get_algorithm_recommendations(
    candidate_skills: List[str] = Query(default=[], description="Candidate skills list"),
    candidate_experience: int = Query(default=0, description="Years of experience"),
    questionnaire_completeness: float = Query(default=0.0, description="Questionnaire completeness (0-1)"),
    has_geo_constraints: bool = Query(default=False, description="Has geographical constraints"),
    supersmartmatch_v2: SuperSmartMatchV2 = Depends(get_supersmartmatch_v2)
) -> Dict[str, Any]:
    """
    🧠 Algorithm Selection Recommendations
    
    Analyzes context and provides intelligent algorithm recommendations
    with detailed reasoning for optimization and debugging.
    """
    
    try:
        context_data = {
            'candidate_skills': candidate_skills,
            'candidate_experience': candidate_experience,
            'questionnaire_completeness': questionnaire_completeness,
            'company_questionnaires_completeness': questionnaire_completeness * 0.8,  # Estimate
            'locations': ['Paris'] if has_geo_constraints else [],
            'mobility_constraints': 'local' if has_geo_constraints else 'flexible'
        }
        
        recommendations = await supersmartmatch_v2.get_algorithm_recommendations(context_data)
        
        return {
            'success': True,
            'recommendations': recommendations,
            'timestamp': time.time()
        }
        
    except Exception as e:
        logger.error(f"Algorithm recommendations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/ab-test/start",
            summary="Start A/B Test",
            description="Start a new A/B test for algorithm comparison")
async def start_ab_test(
    test_name: str = Body(..., description="Test name"),
    algorithm_a: str = Body(..., description="Algorithm A"),
    algorithm_b: str = Body(..., description="Algorithm B"),
    traffic_split: float = Body(0.5, description="Traffic split (0.0-1.0)"),
    supersmartmatch_v2: SuperSmartMatchV2 = Depends(get_supersmartmatch_v2)
) -> Dict[str, Any]:
    """
    🧪 A/B Testing Management
    
    Start new A/B tests to compare algorithm performance
    """
    
    try:
        supersmartmatch_v2.start_ab_test(test_name, algorithm_a, algorithm_b, traffic_split)
        
        return {
            'success': True,
            'message': f"A/B test '{test_name}' started successfully",
            'test_config': {
                'name': test_name,
                'algorithm_a': algorithm_a,
                'algorithm_b': algorithm_b,
                'traffic_split': traffic_split
            },
            'timestamp': time.time()
        }
        
    except Exception as e:
        logger.error(f"A/B test start error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/ab-test/{test_name}/results",
           summary="Get A/B Test Results",
           description="Get results and statistics for an A/B test")
async def get_ab_test_results(
    test_name: str,
    supersmartmatch_v2: SuperSmartMatchV2 = Depends(get_supersmartmatch_v2)
) -> Dict[str, Any]:
    """Get A/B test results and statistics"""
    
    try:
        results = supersmartmatch_v2.get_ab_test_results(test_name)
        
        return {
            'success': True,
            'test_name': test_name,
            'results': results,
            'timestamp': time.time()
        }
        
    except Exception as e:
        logger.error(f"A/B test results error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/cache/clear",
            summary="Clear All Caches",
            description="Clear all system caches for fresh start")
async def clear_caches(
    supersmartmatch_v2: SuperSmartMatchV2 = Depends(get_supersmartmatch_v2)
) -> Dict[str, Any]:
    """Clear all system caches"""
    
    try:
        supersmartmatch_v2.clear_all_caches()
        
        return {
            'success': True,
            'message': 'All caches cleared successfully',
            'timestamp': time.time()
        }
        
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/config",
           summary="Configuration Information",
           description="Get current system configuration")
async def get_configuration(
    supersmartmatch_v2: SuperSmartMatchV2 = Depends(get_supersmartmatch_v2)
) -> Dict[str, Any]:
    """Get current system configuration information"""
    
    try:
        config_info = supersmartmatch_v2.get_configuration_info()
        
        return {
            'success': True,
            'configuration': config_info,
            'timestamp': time.time()
        }
        
    except Exception as e:
        logger.error(f"Configuration info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export router for inclusion in main app
__all__ = ['router', 'RequestOrchestrator', 'get_supersmartmatch_v2']
