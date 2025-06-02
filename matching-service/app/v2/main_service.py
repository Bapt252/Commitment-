"""
SuperSmartMatch V2 Main Application Integration

🚀 Main orchestrator that integrates SuperSmartMatch V2 into the existing service
- Seamless V1/V2 routing with feature flags
- Progressive deployment support
- A/B testing framework integration
- Health monitoring and performance tracking

🏗️ Architecture Integration:
- Maintains existing port 5062 for backward compatibility
- Adds V2 endpoints while preserving V1 API
- Intelligent request routing based on configuration
- Real-time performance monitoring and fallback handling
"""

import logging
import asyncio
import time
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# V2 imports
from .v2.api_endpoints import router as v2_router, get_supersmartmatch_v2
from .v2.supersmartmatch_v2 import SuperSmartMatchV2
from .v2.config_manager import ConfigManager

# Legacy imports (V1)
try:
    from ..main import app as legacy_app  # Import existing V1 app
except ImportError:
    legacy_app = None

logger = logging.getLogger(__name__)

class SuperSmartMatchV2Service:
    """
    Main service orchestrator for SuperSmartMatch V2
    
    Handles:
    - Service initialization and configuration
    - V1/V2 routing and feature flag management
    - Performance monitoring and health checks
    - Progressive deployment and A/B testing
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the V2 service with configuration"""
        
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_config()
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="SuperSmartMatch V2 Service",
            description="🚀 Unified Intelligent Matching Service - V2 Architecture",
            version=self.config.version,
            docs_url="/api/docs",
            redoc_url="/api/redoc"
        )
        
        # Setup middleware
        self._setup_middleware()
        
        # Setup routing
        self._setup_routing()
        
        # Initialize V2 instance
        self.supersmartmatch_v2: Optional[SuperSmartMatchV2] = None
        
        logger.info(f"SuperSmartMatch V2 Service initialized - Version: {self.config.version}")
    
    def _setup_middleware(self):
        """Setup FastAPI middleware for CORS, compression, etc."""
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        # Compression middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Custom performance monitoring middleware
        @self.app.middleware("http")
        async def performance_middleware(request: Request, call_next):
            start_time = time.time()
            
            # Add request ID for tracking
            request_id = request.headers.get("X-Request-ID", f"req_{int(time.time() * 1000)}")
            
            try:
                response = await call_next(request)
                
                # Calculate processing time
                process_time = time.time() - start_time
                response.headers["X-Process-Time"] = str(process_time)
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Service-Version"] = self.config.version
                
                # Log performance metrics
                logger.info(f"Request {request_id}: {request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
                
                return response
                
            except Exception as e:
                process_time = time.time() - start_time
                logger.error(f"Request {request_id} error after {process_time:.3f}s: {e}")
                
                return JSONResponse(
                    status_code=500,
                    content={
                        "error": "Internal server error",
                        "request_id": request_id,
                        "process_time": process_time
                    }
                )
    
    def _setup_routing(self):
        """Setup API routing for V1/V2 with intelligent switching"""
        
        # Include V2 router
        self.app.include_router(v2_router)
        
        # Root endpoint
        @self.app.get("/")
        async def root():
            """Service information endpoint"""
            return {
                "service": "SuperSmartMatch",
                "version": self.config.version,
                "architecture": "V2",
                "status": "operational",
                "features": {
                    "intelligent_algorithm_selection": True,
                    "nexten_matcher_integration": True,
                    "backward_compatibility": True,
                    "ab_testing": True,
                    "real_time_monitoring": True
                },
                "endpoints": {
                    "v2_api": "/api/v2/match",
                    "v1_compatible": "/api/v2/match/legacy",
                    "health": "/api/v2/health",
                    "docs": "/api/docs"
                }
            }
        
        # Health check endpoint (simplified)
        @self.app.get("/health")
        async def simple_health():
            """Simple health check for load balancers"""
            try:
                if self.supersmartmatch_v2 is None:
                    self.supersmartmatch_v2 = get_supersmartmatch_v2()
                
                return {
                    "status": "healthy",
                    "version": self.config.version,
                    "timestamp": time.time()
                }
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return JSONResponse(
                    status_code=503,
                    content={
                        "status": "unhealthy",
                        "error": str(e),
                        "timestamp": time.time()
                    }
                )
        
        # V1 API compatibility endpoints (main matching API)
        @self.app.post("/match")
        async def match_v1_endpoint(request_data: Dict[str, Any]):
            """
            Main matching endpoint with intelligent V1/V2 routing
            
            Maintains the existing /match endpoint while adding V2 capabilities.
            Routes intelligently based on feature flags and user assignment.
            """
            
            try:
                # Initialize V2 service if needed
                if self.supersmartmatch_v2 is None:
                    self.supersmartmatch_v2 = get_supersmartmatch_v2()
                
                # Extract user ID for routing decisions
                user_id = request_data.get('user_id', 'anonymous')
                
                # Check if V2 is enabled and user should get V2
                if (self.config.feature_flags.enable_v2 and 
                    self._should_use_v2(user_id)):
                    
                    logger.debug(f"Routing user {user_id} to V2")
                    
                    # Route to V2 with fallback to V1
                    try:
                        response = await self.supersmartmatch_v2.match_v2(
                            candidate_data=request_data.get('candidate', {}),
                            candidate_questionnaire=request_data.get('candidate_questionnaire'),
                            offers_data=request_data.get('offers', []),
                            company_questionnaires=request_data.get('company_questionnaires'),
                            algorithm=request_data.get('algorithm', 'auto'),
                            user_id=user_id
                        )
                        
                        # Return in V1 format for compatibility
                        return {
                            'matches': [
                                {
                                    'offer_id': match.offer_id,
                                    'score': match.overall_score,
                                    'confidence': match.confidence,
                                    'details': {
                                        'skill_match': match.skill_match_score,
                                        'experience_match': match.experience_match_score,
                                        'location_match': match.location_match_score
                                    },
                                    'insights': match.insights,
                                    'explanation': match.explanation
                                }
                                for match in response.matches
                            ],
                            'algorithm_used': response.algorithm_used,
                            'execution_time_ms': response.execution_time_ms,
                            'version': 'v2_routed'
                        }
                        
                    except Exception as e:
                        logger.error(f"V2 routing failed for user {user_id}, falling back to V1: {e}")
                        # Fall through to V1 processing
                
                # Use V1 compatibility mode
                logger.debug(f"Routing user {user_id} to V1 compatibility")
                
                results = await self.supersmartmatch_v2.match(
                    candidate=request_data.get('candidate', {}),
                    offers=request_data.get('offers', []),
                    config=request_data.get('config')
                )
                
                return {
                    'matches': [
                        {
                            'offer_id': result.offer_id,
                            'score': result.overall_score,
                            'confidence': result.confidence,
                            'details': {
                                'skill_match': result.skill_match_score,
                                'experience_match': result.experience_match_score,
                                'location_match': result.location_match_score
                            },
                            'insights': result.insights,
                            'explanation': result.explanation
                        }
                        for result in results
                    ],
                    'algorithm_used': 'v1_compatibility',
                    'version': 'v1'
                }
                
            except Exception as e:
                logger.error(f"Matching endpoint error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Additional legacy endpoints for backward compatibility
        @self.app.get("/stats")
        async def get_stats():
            """Service statistics endpoint"""
            try:
                if self.supersmartmatch_v2 is None:
                    self.supersmartmatch_v2 = get_supersmartmatch_v2()
                
                health_info = await self.supersmartmatch_v2.get_system_health()
                
                return {
                    'status': 'operational',
                    'requests_processed': health_info.get('uptime_requests', 0),
                    'avg_response_time_ms': health_info.get('avg_response_time_ms', 0),
                    'algorithms_available': health_info.get('algorithms', {}).get('available', []),
                    'version': self.config.version
                }
                
            except Exception as e:
                logger.error(f"Stats endpoint error: {e}")
                return {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Configuration endpoint
        @self.app.get("/config")
        async def get_service_config():
            """Service configuration endpoint"""
            return {
                'version': self.config.version,
                'environment': self.config.environment,
                'features': {
                    'v2_enabled': self.config.feature_flags.enable_v2,
                    'v2_traffic_percentage': self.config.feature_flags.v2_traffic_percentage,
                    'nexten_enabled': self.config.feature_flags.enable_nexten_algorithm,
                    'smart_selection': self.config.feature_flags.enable_smart_selection
                },
                'algorithms': {
                    'nexten_enabled': self.config_manager.is_algorithm_enabled('nexten'),
                    'smart_enabled': self.config_manager.is_algorithm_enabled('smart'),
                    'enhanced_enabled': self.config_manager.is_algorithm_enabled('enhanced'),
                    'semantic_enabled': self.config_manager.is_algorithm_enabled('semantic'),
                    'hybrid_enabled': self.config_manager.is_algorithm_enabled('hybrid')
                }
            }
    
    def _should_use_v2(self, user_id: str) -> bool:
        """Determine if a user should get V2 based on traffic percentage"""
        
        # Simple hash-based traffic splitting
        user_hash = hash(user_id) % 100
        return user_hash < self.config.feature_flags.v2_traffic_percentage
    
    async def start_service(self, host: str = "0.0.0.0", port: int = 5062):
        """Start the SuperSmartMatch V2 service"""
        
        logger.info(f"Starting SuperSmartMatch V2 Service on {host}:{port}")
        
        # Initialize V2 instance on startup
        try:
            self.supersmartmatch_v2 = get_supersmartmatch_v2()
            logger.info("SuperSmartMatch V2 initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize SuperSmartMatch V2: {e}")
            # Continue startup but service will be degraded
        
        # Configuration summary
        logger.info("=== SuperSmartMatch V2 Configuration ===")
        logger.info(f"Version: {self.config.version}")
        logger.info(f"Environment: {self.config.environment}")
        logger.info(f"V2 Enabled: {self.config.feature_flags.enable_v2}")
        logger.info(f"V2 Traffic %: {self.config.feature_flags.v2_traffic_percentage}%")
        logger.info(f"Nexten Algorithm: {self.config.feature_flags.enable_nexten_algorithm}")
        logger.info(f"Smart Selection: {self.config.feature_flags.enable_smart_selection}")
        logger.info("==========================================")
        
        # Start the server
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()

# Factory function for creating service instance
def create_supersmartmatch_v2_service(config_path: Optional[str] = None) -> SuperSmartMatchV2Service:
    """Create and configure SuperSmartMatch V2 service instance"""
    return SuperSmartMatchV2Service(config_path)

# Main entry point
async def main():
    """Main entry point for running SuperSmartMatch V2 service"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start service
    service = create_supersmartmatch_v2_service()
    await service.start_service()

if __name__ == "__main__":
    # Run the service
    asyncio.run(main())

# Export for use in other modules
__all__ = ['SuperSmartMatchV2Service', 'create_supersmartmatch_v2_service']
