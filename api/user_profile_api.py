"""
API for User Profiles and Behavioral Analysis

This module provides API endpoints for accessing enriched user profiles,
behavioral insights, and user segments for the Commitment platform.

Part of the Session 8 implementation: Behavioral Analysis and User Profiling.
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Body, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
import logging
import json
import asyncio
from datetime import datetime, timedelta
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import behavioral analysis modules
from analysis.behavioral_analysis.user_clustering import UserClusteringEngine
from analysis.behavioral_analysis.pattern_detection import PatternDetectionEngine
from analysis.behavioral_analysis.preference_scoring import PreferenceScoringEngine

# Database connection
from database.connection import get_db_connection

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Commitment User Profiling API",
    description="API for accessing user behavioral analysis and profiling data",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
user_clustering_engine = None
pattern_detection_engine = None
preference_scoring_engine = None

# Pydantic models for request/response
class UserProfileResponse(BaseModel):
    user_id: str
    profile_status: str = "active"
    cluster: Dict[str, Any] = None
    behavioral_patterns: Dict[str, Any] = None
    preferences: Dict[str, Any] = None
    profile_completeness: float = 0.0
    last_updated: str = None
    
class ClusterResponse(BaseModel):
    cluster_id: int
    name: str
    size: int
    percentage: float
    features: Dict[str, Any]
    
class PatternResponse(BaseModel):
    pattern_id: str
    pattern_type: str
    description: str
    support: float
    details: Dict[str, Any]
    
class PreferenceScoreRequest(BaseModel):
    user_id: str
    match_attributes: Dict[str, Any]
    recalculate: bool = False

class PreferenceScoreResponse(BaseModel):
    user_id: str
    status: str
    overall_score: float
    category_scores: Dict[str, float] = None
    timestamp: str = None
    error: Optional[str] = None

class SegmentListResponse(BaseModel):
    total_segments: int
    segments: List[Dict[str, Any]]
    
class ErrorResponse(BaseModel):
    error: str
    details: Optional[Dict[str, Any]] = None

# Background task to initialize engines
@app.on_event("startup")
async def startup_event():
    global user_clustering_engine, pattern_detection_engine, preference_scoring_engine
    
    # Get database connection
    try:
        db_connection = get_db_connection()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        db_connection = None
    
    # Initialize engines with config
    config = {
        'clustering': {
            'n_clusters': 5,
            'random_state': 42,
            'pca_components': 3,
            'min_events_threshold': 10
        },
        'pattern_detection': {
            'min_pattern_support': 0.05,
            'min_pattern_length': 2,
            'max_pattern_length': 10,
            'time_window': 30
        },
        'preference_scoring': {
            'explicit_weight': 0.7,
            'implicit_weight': 0.3,
            'recency_decay_factor': 0.1,
            'min_interactions': 5,
            'preference_categories': [
                'skills', 'industry', 'job_type', 'location', 'company_size'
            ]
        }
    }
    
    user_clustering_engine = UserClusteringEngine(db_connection, config['clustering'])
    pattern_detection_engine = PatternDetectionEngine(db_connection, config['pattern_detection'])
    preference_scoring_engine = PreferenceScoringEngine(db_connection, config['preference_scoring'])
    
    logger.info("Behavioral analysis engines initialized")
    
    # Pre-calculate clusters and patterns in background
    asyncio.create_task(precalculate_analysis())

async def precalculate_analysis():
    """Background task to precalculate clusters and patterns"""
    try:
        # Wait a bit to ensure everything is initialized
        await asyncio.sleep(5)
        
        # Run clustering
        if user_clustering_engine:
            logger.info("Starting background clustering task")
            await asyncio.to_thread(user_clustering_engine.cluster_users, 90, 'kmeans', True)
            logger.info("Background clustering task completed")
        
        # Run pattern detection
        if pattern_detection_engine:
            logger.info("Starting background pattern detection task")
            await asyncio.to_thread(pattern_detection_engine.detect_all_patterns, 90)
            logger.info("Background pattern detection task completed")
            
    except Exception as e:
        logger.error(f"Error in background analysis task: {e}")

# Dependency for checking API readiness
async def check_engines_ready():
    if not all([user_clustering_engine, pattern_detection_engine, preference_scoring_engine]):
        raise HTTPException(
            status_code=503, 
            detail="Behavioral analysis engines not fully initialized yet"
        )
    return True

# API Routes

@app.get("/", tags=["General"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Commitment User Profiling API",
        "version": "1.0.0",
        "status": "running",
        "engines_initialized": all([
            user_clustering_engine, 
            pattern_detection_engine, 
            preference_scoring_engine
        ])
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint"""
    engines_status = {
        "clustering_engine": user_clustering_engine is not None,
        "pattern_engine": pattern_detection_engine is not None,
        "preference_engine": preference_scoring_engine is not None
    }
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engines": engines_status
    }

@app.get("/profile/{user_id}", response_model=UserProfileResponse, tags=["User Profiles"])
async def get_user_profile(
    user_id: str = Path(..., description="User ID to retrieve profile for"),
    recalculate: bool = Query(False, description="Force recalculation of the profile"),
    include_patterns: bool = Query(True, description="Include behavioral patterns"),
    include_preferences: bool = Query(True, description="Include preference model"),
    _: bool = Depends(check_engines_ready)
):
    """
    Get a complete user profile with behavioral analysis results.
    
    This endpoint combines clustering, pattern detection, and preference scoring
    to build a comprehensive user profile with behavioral insights.
    """
    try:
        profile = {"user_id": user_id, "profile_status": "active"}
        completeness_factors = []
        
        # Get user cluster
        try:
            cluster_info = await asyncio.to_thread(
                user_clustering_engine.get_user_cluster, user_id, 'kmeans'
            )
            profile["cluster"] = cluster_info
            completeness_factors.append(1.0 if "cluster_id" in cluster_info else 0.0)
        except Exception as e:
            logger.warning(f"Error getting cluster for user {user_id}: {e}")
            profile["cluster"] = {"status": "error", "message": str(e)}
            completeness_factors.append(0.0)
        
        # Get behavioral patterns
        if include_patterns:
            try:
                patterns = await asyncio.to_thread(
                    pattern_detection_engine.analyze_user_patterns, user_id
                )
                profile["behavioral_patterns"] = patterns
                completeness_factors.append(1.0 if "error" not in patterns else 0.0)
            except Exception as e:
                logger.warning(f"Error analyzing patterns for user {user_id}: {e}")
                profile["behavioral_patterns"] = {"status": "error", "message": str(e)}
                completeness_factors.append(0.0)
        
        # Get preference model
        if include_preferences:
            try:
                preferences = await asyncio.to_thread(
                    preference_scoring_engine.get_user_preferences, user_id, recalculate
                )
                profile["preferences"] = preferences
                completeness_factors.append(1.0 if preferences.get("status") == "success" else 0.0)
            except Exception as e:
                logger.warning(f"Error getting preferences for user {user_id}: {e}")
                profile["preferences"] = {"status": "error", "message": str(e)}
                completeness_factors.append(0.0)
        
        # Calculate profile completeness
        if completeness_factors:
            profile["profile_completeness"] = sum(completeness_factors) / len(completeness_factors)
        
        profile["last_updated"] = datetime.now().isoformat()
        
        return profile
        
    except Exception as e:
        logger.error(f"Error generating user profile: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating user profile: {str(e)}")

@app.get("/segments", response_model=SegmentListResponse, tags=["Segmentation"])
async def list_user_segments(
    algorithm: str = Query("kmeans", description="Clustering algorithm (kmeans or dbscan)"),
    refresh: bool = Query(False, description="Force refresh of segments"),
    _: bool = Depends(check_engines_ready)
):
    """
    List all user segments/clusters with their characteristics.
    """
    try:
        # If refresh requested, run clustering
        if refresh:
            await asyncio.to_thread(
                user_clustering_engine.cluster_users, 90, algorithm, True
            )
        
        # Get cluster profiles
        if algorithm not in user_clustering_engine.cluster_profiles:
            # Run clustering if profiles not available
            await asyncio.to_thread(
                user_clustering_engine.cluster_users, 90, algorithm, True
            )
        
        profiles = user_clustering_engine.cluster_profiles.get(algorithm, {})
        
        if not profiles:
            raise HTTPException(
                status_code=404, 
                detail=f"No clusters found for algorithm: {algorithm}"
            )
        
        segments = []
        for cluster_id, profile in profiles.items():
            segments.append({
                "id": cluster_id,
                "name": profile.get("name", f"Cluster {cluster_id}"),
                "size": profile.get("size", 0),
                "percentage": profile.get("percentage", 0),
                "key_characteristics": _extract_key_characteristics(profile)
            })
        
        return {
            "total_segments": len(segments),
            "segments": segments
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing user segments: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing user segments: {str(e)}")

@app.get("/segments/{cluster_id}", response_model=ClusterResponse, tags=["Segmentation"])
async def get_segment_details(
    cluster_id: int = Path(..., description="Cluster ID to get details for"),
    algorithm: str = Query("kmeans", description="Clustering algorithm (kmeans or dbscan)"),
    _: bool = Depends(check_engines_ready)
):
    """
    Get detailed information about a specific user segment/cluster.
    """
    try:
        profiles = user_clustering_engine.cluster_profiles.get(algorithm, {})
        
        if not profiles:
            raise HTTPException(
                status_code=404, 
                detail=f"No clusters found for algorithm: {algorithm}"
            )
        
        profile = profiles.get(cluster_id)
        
        if not profile:
            raise HTTPException(
                status_code=404, 
                detail=f"Cluster {cluster_id} not found"
            )
        
        return {
            "cluster_id": cluster_id,
            "name": profile.get("name", f"Cluster {cluster_id}"),
            "size": profile.get("size", 0),
            "percentage": profile.get("percentage", 0),
            "features": profile.get("features", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting segment details: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting segment details: {str(e)}")

@app.get("/patterns", tags=["Behavioral Patterns"])
async def list_behavioral_patterns(
    pattern_type: str = Query(None, description="Type of patterns to retrieve (sequential, time_based, anomalies)"),
    min_support: float = Query(0.05, description="Minimum pattern support"),
    _: bool = Depends(check_engines_ready)
):
    """
    List detected behavioral patterns across all users.
    """
    try:
        # Make sure patterns are detected
        if not pattern_detection_engine.detected_patterns:
            await asyncio.to_thread(
                pattern_detection_engine.detect_all_patterns, 90
            )
        
        patterns = pattern_detection_engine.detected_patterns
        
        # Filter by pattern type if specified
        if pattern_type:
            if pattern_type not in patterns:
                raise HTTPException(
                    status_code=404, 
                    detail=f"No patterns found for type: {pattern_type}"
                )
            
            return {
                "pattern_type": pattern_type,
                "patterns": patterns[pattern_type]
            }
        
        # Return summary of all pattern types
        result = {}
        for p_type, p_data in patterns.items():
            if isinstance(p_data, list):
                # Filter by support for list-based patterns
                filtered_patterns = [p for p in p_data if p.get('support', 0) >= min_support]
                result[p_type] = {
                    "count": len(filtered_patterns),
                    "patterns": filtered_patterns[:10]  # Return top 10
                }
            elif isinstance(p_data, dict):
                result[p_type] = {
                    "count": len(p_data),
                    "summary": _summarize_dict_patterns(p_data, 5)
                }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing behavioral patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing behavioral patterns: {str(e)}")

@app.get("/patterns/{user_id}", tags=["Behavioral Patterns"])
async def get_user_patterns(
    user_id: str = Path(..., description="User ID to get patterns for"),
    _: bool = Depends(check_engines_ready)
):
    """
    Get behavioral patterns for a specific user.
    """
    try:
        patterns = await asyncio.to_thread(
            pattern_detection_engine.analyze_user_patterns, user_id
        )
        
        if "error" in patterns:
            raise HTTPException(
                status_code=404, 
                detail=patterns["error"]
            )
        
        return patterns
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting user patterns: {str(e)}")

@app.get("/preferences/{user_id}", tags=["Preferences"])
async def get_user_preferences(
    user_id: str = Path(..., description="User ID to get preferences for"),
    recalculate: bool = Query(False, description="Force recalculation of preferences"),
    _: bool = Depends(check_engines_ready)
):
    """
    Get preference model for a specific user.
    """
    try:
        preferences = await asyncio.to_thread(
            preference_scoring_engine.get_user_preferences, user_id, recalculate
        )
        
        if "error" in preferences:
            raise HTTPException(
                status_code=404, 
                detail=preferences["error"]
            )
        
        return preferences
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting user preferences: {str(e)}")

@app.post("/preferences/score", response_model=PreferenceScoreResponse, tags=["Preferences"])
async def score_match_preferences(
    request: PreferenceScoreRequest,
    _: bool = Depends(check_engines_ready)
):
    """
    Score a potential match against a user's preference model.
    """
    try:
        score_result = await asyncio.to_thread(
            preference_scoring_engine.score_match_for_user,
            request.user_id,
            request.match_attributes,
            request.recalculate
        )
        
        return score_result
        
    except Exception as e:
        logger.error(f"Error scoring match preferences: {e}")
        raise HTTPException(status_code=500, detail=f"Error scoring match preferences: {str(e)}")

@app.post("/analysis/run", tags=["Administration"])
async def run_analysis(
    days_lookback: int = Query(90, description="Days of data to analyze"),
    _: bool = Depends(check_engines_ready)
):
    """
    Manually trigger a full analysis run (clustering, pattern detection).
    This is an administrative endpoint for running analysis outside the 
    automatic schedule.
    """
    try:
        # Run analysis tasks in background
        asyncio.create_task(run_full_analysis(days_lookback))
        
        return {
            "status": "analysis_started",
            "message": "Full analysis process has been started in the background",
            "days_lookback": days_lookback
        }
        
    except Exception as e:
        logger.error(f"Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting analysis: {str(e)}")

async def run_full_analysis(days_lookback: int):
    """Background task to run full analysis"""
    try:
        # Run clustering
        if user_clustering_engine:
            logger.info(f"Starting clustering analysis with {days_lookback} days lookback")
            await asyncio.to_thread(user_clustering_engine.cluster_users, days_lookback, 'kmeans', True)
            logger.info("Clustering analysis completed")
        
        # Run pattern detection
        if pattern_detection_engine:
            logger.info(f"Starting pattern detection with {days_lookback} days lookback")
            await asyncio.to_thread(pattern_detection_engine.detect_all_patterns, days_lookback)
            logger.info("Pattern detection completed")
            
    except Exception as e:
        logger.error(f"Error in full analysis task: {e}")

# Helper functions

def _extract_key_characteristics(profile: Dict) -> List[Dict]:
    """Extract key characteristics from a cluster profile"""
    key_chars = []
    
    if "features" not in profile:
        return key_chars
    
    # Get top 5 most distinctive features
    features = profile["features"]
    
    for feature_name, feature_stats in features.items():
        if isinstance(feature_stats, dict) and "mean" in feature_stats:
            key_chars.append({
                "feature": feature_name,
                "value": feature_stats["mean"],
                "percentile": None  # Would calculate if we had global stats
            })
    
    # Sort by presumed importance and take top 5
    key_chars.sort(key=lambda x: abs(x["value"]), reverse=True)
    return key_chars[:5]

def _summarize_dict_patterns(patterns: Dict, limit: int) -> List[Dict]:
    """Summarize dictionary-based patterns"""
    summary = []
    
    # Take a sample of patterns
    for key, value in list(patterns.items())[:limit]:
        if isinstance(value, dict):
            summary.append({
                "id": key,
                "type": "dict_pattern",
                "details": {k: v for k, v in value.items() if not isinstance(v, (dict, list))}
            })
        else:
            summary.append({
                "id": key,
                "value": str(value)[:100]  # Truncate long values
            })
    
    return summary

# Run app with uvicorn when module is called directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5060)
