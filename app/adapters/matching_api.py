"""
Matching API Module

This module provides the REST API for the SmartMatch service.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, Body, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.adapters.parsing_adapter import ParsingAdapter
from app.adapters.matching_pipeline import MatchingPipeline

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Model definitions
class MatchRequest(BaseModel):
    """Request model for matching."""
    job_description: Optional[str] = None
    
class MultiMatchConfig(BaseModel):
    """Configuration for multi-CV matching."""
    sort_by: str = "score"  # score, name, experience
    sort_order: str = "desc"  # asc, desc
    min_score: Optional[float] = None
    max_results: Optional[int] = None

class MultiMatchResponse(BaseModel):
    """Response model for multi-CV matching."""
    matches: List[Dict[str, Any]]
    job_info: Dict[str, Any]
    config: MultiMatchConfig

# Create FastAPI app
app = FastAPI(
    title="SmartMatch API",
    description="API for the SmartMatch service, providing CV and job matching capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create instances (can be replaced with dependency injection)
parsing_adapter = ParsingAdapter()
matching_pipeline = MatchingPipeline(parsing_adapter)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "smartmatch"}

@app.post("/api/match/cv-to-job")
async def match_cv_to_job(
    cv_file: UploadFile = File(...),
    job_description: Optional[str] = Form(None),
    job_file: Optional[UploadFile] = File(None)
):
    """
    Match a CV to a job.
    
    Either job_description or job_file must be provided.
    """
    try:
        # Read the CV file
        cv_content = await cv_file.read()
        
        # Handle job data
        job_content = None
        job_filename = None
        
        if job_file:
            job_content = await job_file.read()
            job_filename = job_file.filename
        
        if not job_description and not job_content:
            raise HTTPException(status_code=400, detail="Either job_description or job_file must be provided")
        
        # Process the match
        result = await matching_pipeline.match_cv_to_job(
            cv_file=cv_content,
            cv_filename=cv_file.filename,
            job_description=job_description,
            job_file=job_content,
            job_filename=job_filename
        )
        
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in match_cv_to_job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match/job-to-cv")
async def match_job_to_cv(
    job_description: Optional[str] = Form(None),
    cv_file: UploadFile = File(...),
    job_file: Optional[UploadFile] = File(None)
):
    """
    Match a job to a CV.
    
    Either job_description or job_file must be provided.
    """
    try:
        # Read the CV file
        cv_content = await cv_file.read()
        
        # Handle job data
        job_content = None
        job_filename = None
        
        if job_file:
            job_content = await job_file.read()
            job_filename = job_file.filename
        
        if not job_description and not job_content:
            raise HTTPException(status_code=400, detail="Either job_description or job_file must be provided")
        
        # Process the match
        result = await matching_pipeline.match_job_to_cv(
            job_description=job_description,
            cv_file=cv_content,
            cv_filename=cv_file.filename,
            job_file=job_content,
            job_filename=job_filename
        )
        
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error in match_job_to_cv: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match/multi-cv")
async def match_multiple_cvs(
    cv_files: List[UploadFile] = File(...),
    job_description: Optional[str] = Form(None),
    job_file: Optional[UploadFile] = File(None),
    config: MultiMatchConfig = Body(MultiMatchConfig())
):
    """
    Match multiple CVs to a job.
    
    Either job_description or job_file must be provided.
    """
    try:
        # Handle job data
        job_content = None
        job_filename = None
        
        if job_file:
            job_content = await job_file.read()
            job_filename = job_file.filename
        
        if not job_description and not job_content:
            raise HTTPException(status_code=400, detail="Either job_description or job_file must be provided")
        
        # Read all CV files
        cv_data = []
        for cv_file in cv_files:
            cv_content = await cv_file.read()
            cv_data.append({
                "content": cv_content,
                "filename": cv_file.filename
            })
        
        # Process the matches
        results = await matching_pipeline.match_multiple_cvs_to_job(
            cv_files=cv_data,
            job_description=job_description,
            job_file=job_content,
            job_filename=job_filename
        )
        
        # Apply configuration filters
        if config.min_score is not None:
            results = [r for r in results if r.get("match_score", 0) >= config.min_score]
        
        if config.max_results is not None and config.max_results > 0:
            results = results[:config.max_results]
        
        # Extract job info from the first result (all have the same job info)
        job_info = {}
        if results:
            job_info = results[0].get("job_info", {})
        
        response = {
            "matches": results,
            "job_info": job_info,
            "config": config.dict()
        }
        
        return JSONResponse(content=response)
    except Exception as e:
        logger.error(f"Error in match_multiple_cvs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/match/job-to-multi-cv")
async def match_job_to_multiple_cvs(
    job_description: Optional[str] = Form(None),
    cv_files: List[UploadFile] = File(...),
    job_file: Optional[UploadFile] = File(None),
    config: MultiMatchConfig = Body(MultiMatchConfig())
):
    """
    Match a job to multiple CVs.
    
    Either job_description or job_file must be provided.
    """
    # This is functionally the same as match_multiple_cvs
    return await match_multiple_cvs(
        cv_files=cv_files,
        job_description=job_description,
        job_file=job_file,
        config=config
    )

@app.get("/api/match/score-explanation")
async def get_score_explanation():
    """
    Get explanation of the matching score components.
    """
    return {
        "score_components": {
            "skills": "Matches required skills from the job with skills listed in the CV",
            "experience": "Compares the years of experience with the job requirements",
            "education": "Matches education level and field with job requirements",
            "title_relevance": "Compares job title with past roles listed in the CV",
            "location": "Compares job location with candidate location or considers remote work"
        },
        "weights": {
            "skills": 0.40,
            "experience": 0.25,
            "education": 0.15,
            "title_relevance": 0.10,
            "location": 0.10
        },
        "score_interpretation": {
            "90-100": "Excellent match - The candidate meets or exceeds all major requirements",
            "75-89": "Strong match - The candidate meets most major requirements",
            "60-74": "Good match - The candidate meets many requirements, with some gaps",
            "40-59": "Moderate match - The candidate meets some requirements, with significant gaps",
            "20-39": "Weak match - The candidate meets few requirements",
            "0-19": "Poor match - The candidate meets very few or no requirements"
        }
    }
