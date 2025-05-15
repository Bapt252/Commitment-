"""
Matching Pipeline Module

This module provides the orchestration pipeline for the matching process, connecting
parsers and the SmartMatch engine.
"""

import logging
from typing import Dict, Any, Optional, List, Union

from app.adapters.parsing_adapter import ParsingAdapter
from app.core.smart_match import SmartMatcher

# Configure logging
logger = logging.getLogger(__name__)

class MatchingPipeline:
    """
    Orchestrates the entire matching process, from parsing to matching.
    """
    
    def __init__(self, parsing_adapter: ParsingAdapter, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the MatchingPipeline with adapters and optional configuration.
        
        Args:
            parsing_adapter (ParsingAdapter): The parsing adapter
            config (dict, optional): Configuration parameters
        """
        self.parsing_adapter = parsing_adapter
        self.config = config or {}
        
        # Initialize the matcher with config
        matcher_config = self.config.get("matcher", {})
        self.matcher = SmartMatcher(matcher_config)
        
        logger.info("MatchingPipeline initialized")
    
    async def match_cv_to_job(
        self,
        cv_file: bytes,
        cv_filename: Optional[str] = None,
        job_description: Optional[str] = None,
        job_file: Optional[bytes] = None,
        job_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Match a CV to a job posting.
        
        Args:
            cv_file (bytes): The CV file content
            cv_filename (str, optional): The CV file name
            job_description (str, optional): The job description text
            job_file (bytes, optional): The job description file content
            job_filename (str, optional): The job description file name
            
        Returns:
            dict: Match results
        """
        logger.info(f"Starting CV to job matching for {cv_filename or 'unnamed CV'}")
        
        # Parse CV
        cv_data = await self.parsing_adapter.parse_cv(cv_file, cv_filename)
        prepared_cv = self.parsing_adapter.prepare_for_matching(cv_data, "cv")
        
        # Parse job - either from text or file
        if job_description:
            job_data = await self.parsing_adapter.parse_job(job_description)
        elif job_file:
            job_data = await self.parsing_adapter.parse_job_file(job_file, job_filename)
        else:
            raise ValueError("Either job_description or job_file must be provided")
        
        prepared_job = self.parsing_adapter.prepare_for_matching(job_data, "job")
        
        # Match
        match_result = self.matcher.match_cv_to_job(prepared_cv, prepared_job)
        
        # Return results
        return {
            "cv_info": {
                "name": cv_data.get("personal_info", {}).get("name", cv_filename or "Unnamed CV"),
                "skills": prepared_cv.get("skills", []),
                "experience": prepared_cv.get("total_experience", 0),
                "location": prepared_cv.get("location", "")
            },
            "job_info": {
                "title": job_data.get("title", job_filename or "Unnamed Job"),
                "company": job_data.get("company", ""),
                "skills": prepared_job.get("skills", []),
                "location": prepared_job.get("location", "")
            },
            "match_score": match_result["match_score"],
            "match_details": match_result["match_details"]
        }
    
    async def match_job_to_cv(
        self,
        job_description: Optional[str] = None,
        cv_file: bytes = None,
        cv_filename: Optional[str] = None,
        job_file: Optional[bytes] = None,
        job_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Match a job posting to a CV.
        
        Args:
            job_description (str, optional): The job description text
            cv_file (bytes): The CV file content
            cv_filename (str, optional): The CV file name
            job_file (bytes, optional): The job description file content
            job_filename (str, optional): The job description file name
            
        Returns:
            dict: Match results
        """
        logger.info(f"Starting job to CV matching")
        
        # Parse job - either from text or file
        if job_description:
            job_data = await self.parsing_adapter.parse_job(job_description)
        elif job_file:
            job_data = await self.parsing_adapter.parse_job_file(job_file, job_filename)
        else:
            raise ValueError("Either job_description or job_file must be provided")
            
        prepared_job = self.parsing_adapter.prepare_for_matching(job_data, "job")
        
        # Parse CV
        cv_data = await self.parsing_adapter.parse_cv(cv_file, cv_filename)
        prepared_cv = self.parsing_adapter.prepare_for_matching(cv_data, "cv")
        
        # Match
        match_result = self.matcher.match_job_to_cv(prepared_job, prepared_cv)
        
        # Return results
        return {
            "job_info": {
                "title": job_data.get("title", job_filename or "Unnamed Job"),
                "company": job_data.get("company", ""),
                "skills": prepared_job.get("skills", []),
                "location": prepared_job.get("location", "")
            },
            "cv_info": {
                "name": cv_data.get("personal_info", {}).get("name", cv_filename or "Unnamed CV"),
                "skills": prepared_cv.get("skills", []),
                "experience": prepared_cv.get("total_experience", 0),
                "location": prepared_cv.get("location", "")
            },
            "match_score": match_result["match_score"],
            "match_details": match_result["match_details"]
        }
    
    async def match_multiple_cvs_to_job(
        self,
        cv_files: List[Dict[str, Union[bytes, str]]],
        job_description: Optional[str] = None,
        job_file: Optional[bytes] = None,
        job_filename: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Match multiple CVs to a job posting.
        
        Args:
            cv_files (list): List of dicts with 'content' (bytes) and 'filename' (str) keys
            job_description (str, optional): The job description text
            job_file (bytes, optional): The job description file content
            job_filename (str, optional): The job description file name
            
        Returns:
            list: Sorted list of match results
        """
        # Parse job once - either from text or file
        if job_description:
            job_data = await self.parsing_adapter.parse_job(job_description)
        elif job_file:
            job_data = await self.parsing_adapter.parse_job_file(job_file, job_filename)
        else:
            raise ValueError("Either job_description or job_file must be provided")
            
        prepared_job = self.parsing_adapter.prepare_for_matching(job_data, "job")
        
        # Match each CV
        results = []
        for cv in cv_files:
            cv_content = cv.get('content')
            cv_filename = cv.get('filename')
            
            try:
                # Parse CV
                cv_data = await self.parsing_adapter.parse_cv(cv_content, cv_filename)
                prepared_cv = self.parsing_adapter.prepare_for_matching(cv_data, "cv")
                
                # Match
                match_result = self.matcher.match_cv_to_job(prepared_cv, prepared_job)
                
                # Add to results
                results.append({
                    "cv_filename": cv_filename,
                    "cv_info": {
                        "name": cv_data.get("personal_info", {}).get("name", cv_filename or "Unnamed CV"),
                        "skills": prepared_cv.get("skills", []),
                        "experience": prepared_cv.get("total_experience", 0),
                        "location": prepared_cv.get("location", "")
                    },
                    "job_info": {
                        "title": job_data.get("title", job_filename or "Unnamed Job"),
                        "company": job_data.get("company", ""),
                        "skills": prepared_job.get("skills", []),
                        "location": prepared_job.get("location", "")
                    },
                    "match_score": match_result["match_score"],
                    "match_details": match_result["match_details"]
                })
            except Exception as e:
                logger.error(f"Error matching CV '{cv_filename}': {str(e)}")
                # Add error result
                results.append({
                    "cv_filename": cv_filename,
                    "error": str(e),
                    "match_score": 0
                })
        
        # Sort by match score (descending)
        results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        
        return results
    
    async def match_job_to_multiple_cvs(
        self,
        job_description: Optional[str] = None,
        cv_files: List[Dict[str, Union[bytes, str]]] = None,
        job_file: Optional[bytes] = None,
        job_filename: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Match a job posting to multiple CVs.
        
        Args:
            job_description (str, optional): The job description text
            cv_files (list): List of dicts with 'content' (bytes) and 'filename' (str) keys
            job_file (bytes, optional): The job description file content
            job_filename (str, optional): The job description file name
            
        Returns:
            list: Sorted list of match results
        """
        # Use the same implementation as match_multiple_cvs_to_job
        # Results will be the same, just with a different perspective
        return await self.match_multiple_cvs_to_job(
            cv_files=cv_files,
            job_description=job_description,
            job_file=job_file,
            job_filename=job_filename
        )
