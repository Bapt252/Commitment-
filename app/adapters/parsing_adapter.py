"""
Parsing Adapter Module

This module provides adapters for connecting various parsing services to the 
SmartMatch system.
"""

import os
import logging
import json
import aiohttp
from typing import Dict, Any, Optional, List, Union
import tempfile

# Configure logging
logger = logging.getLogger(__name__)

class ParsingAdapter:
    """
    Adapter that handles parsing of CVs and job descriptions by connecting
    to various parsing services.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the ParsingAdapter with configuration.
        
        Args:
            config (dict, optional): Configuration parameters
        """
        self.config = config or {}
        self.cv_parser_url = self.config.get('cv_parser_url', os.environ.get('CV_PARSER_URL', 'http://localhost:5051'))
        self.job_parser_url = self.config.get('job_parser_url', os.environ.get('JOB_PARSER_URL', 'http://localhost:5055'))
        
        # Use environment variables as default if not provided in config
        self.endpoints = {
            'cv_parse': self.config.get('cv_parse_endpoint', '/api/parse-cv'),
            'job_parse': self.config.get('job_parse_endpoint', '/api/analyze'),
            'job_parse_file': self.config.get('job_parse_file_endpoint', '/api/analyze-file')
        }
        
        # Cache for parsed documents to avoid redundant API calls
        self._cache = {}
        
        logger.info(f"ParsingAdapter initialized with CV parser at {self.cv_parser_url} and Job parser at {self.job_parser_url}")

    async def parse_cv(self, file_content: bytes, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse a CV file and return structured data.
        
        Args:
            file_content (bytes): The CV file content
            file_name (str, optional): The CV file name
            
        Returns:
            dict: Structured CV data
        """
        # Check cache first using hash of file_content as key
        cache_key = f"cv_{hash(file_content)}"
        if cache_key in self._cache:
            logger.info(f"Using cached CV parsing result for {file_name or 'unnamed file'}")
            return self._cache[cache_key]
        
        logger.info(f"Parsing CV: {file_name or 'unnamed file'}")
        
        try:
            # Prepare request to CV parser service
            url = f"{self.cv_parser_url}{self.endpoints['cv_parse']}"
            
            # Create form data with file
            form_data = aiohttp.FormData()
            form_data.add_field(
                'file',
                file_content,
                filename=file_name or 'cv.pdf',
                content_type='application/octet-stream'
            )
            form_data.add_field('force_refresh', 'false')
            
            # Send request to CV parser service
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form_data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"CV parsing error: {error_text}")
                        raise Exception(f"Failed to parse CV: {error_text}")
                    
                    # Parse the response
                    result = await response.json()
                    
                    # Cache the result
                    self._cache[cache_key] = result
                    
                    return result
                    
        except Exception as e:
            logger.error(f"Error in parse_cv: {str(e)}")
            # Return a minimal structure so the system can continue to function
            return {
                "personal_info": {
                    "name": file_name or "Unknown",
                    "email": "",
                    "phone": "",
                    "location": ""
                },
                "skills": [],
                "experience": [],
                "education": [],
                "summary": f"Failed to parse CV: {str(e)}"
            }
    
    async def parse_job(self, job_description: str) -> Dict[str, Any]:
        """
        Parse a job description and return structured data.
        
        Args:
            job_description (str): The job description text
            
        Returns:
            dict: Structured job data
        """
        # Check cache first using hash of job_description as key
        cache_key = f"job_{hash(job_description)}"
        if cache_key in self._cache:
            logger.info("Using cached job parsing result")
            return self._cache[cache_key]
        
        logger.info(f"Parsing job description: {job_description[:50]}...")
        
        try:
            # Prepare request to job parser service
            url = f"{self.job_parser_url}{self.endpoints['job_parse']}"
            
            # Send request to job parser service
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, 
                    json={"text": job_description}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Job parsing error: {error_text}")
                        raise Exception(f"Failed to parse job description: {error_text}")
                    
                    # Parse the response
                    result = await response.json()
                    
                    # Cache the result
                    self._cache[cache_key] = result
                    
                    return result
                    
        except Exception as e:
            logger.error(f"Error in parse_job: {str(e)}")
            # Return a minimal structure so the system can continue to function
            return {
                "title": "Unknown Position",
                "company": "",
                "location": "",
                "skills": [],
                "experience_required": 0,
                "education_required": "",
                "description": job_description,
                "error": str(e)
            }
    
    async def parse_job_file(self, file_content: bytes, file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse a job description file and return structured data.
        
        Args:
            file_content (bytes): The job description file content
            file_name (str, optional): The job description file name
            
        Returns:
            dict: Structured job data
        """
        # Check cache first using hash of file_content as key
        cache_key = f"job_file_{hash(file_content)}"
        if cache_key in self._cache:
            logger.info(f"Using cached job file parsing result for {file_name or 'unnamed file'}")
            return self._cache[cache_key]
        
        logger.info(f"Parsing job file: {file_name or 'unnamed file'}")
        
        try:
            # Prepare request to job parser service
            url = f"{self.job_parser_url}{self.endpoints['job_parse_file']}"
            
            # Create form data with file
            form_data = aiohttp.FormData()
            form_data.add_field(
                'file',
                file_content,
                filename=file_name or 'job.pdf',
                content_type='application/octet-stream'
            )
            
            # Send request to job parser service
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form_data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Job file parsing error: {error_text}")
                        raise Exception(f"Failed to parse job file: {error_text}")
                    
                    # Parse the response
                    result = await response.json()
                    
                    # Cache the result
                    self._cache[cache_key] = result
                    
                    return result
                    
        except Exception as e:
            logger.error(f"Error in parse_job_file: {str(e)}")
            # Return a minimal structure so the system can continue to function
            return {
                "title": file_name or "Unknown Position",
                "company": "",
                "location": "",
                "skills": [],
                "experience_required": 0,
                "education_required": "",
                "description": "",
                "error": str(e)
            }
    
    def prepare_for_matching(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """
        Prepare parsed data for matching.
        
        Args:
            data (dict): The data to prepare
            data_type (str): The type of data ('cv' or 'job')
            
        Returns:
            dict: Prepared data ready for matching
        """
        if data_type == "cv":
            return self._prepare_cv_for_matching(data)
        elif data_type == "job":
            return self._prepare_job_for_matching(data)
        else:
            raise ValueError(f"Unknown data type: {data_type}")
    
    def _prepare_cv_for_matching(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform parsed CV data into format suitable for matching.
        
        Args:
            cv_data (dict): Parsed CV data
            
        Returns:
            dict: CV data prepared for matching
        """
        # Extract skills, ensuring we have a list of strings
        skills = cv_data.get("skills", [])
        if isinstance(skills, list):
            # Handle different possible skill formats
            processed_skills = []
            for skill in skills:
                if isinstance(skill, str):
                    processed_skills.append(skill)
                elif isinstance(skill, dict) and "name" in skill:
                    processed_skills.append(skill["name"])
            skills = processed_skills
        else:
            skills = []
        
        # Extract location from personal info
        personal_info = cv_data.get("personal_info", {})
        location = personal_info.get("location", "")
        
        # Extract experience information
        experience = []
        for exp in cv_data.get("experience", []):
            if isinstance(exp, dict):
                experience.append({
                    "title": exp.get("title", ""),
                    "description": exp.get("description", ""),
                    "company": exp.get("company", ""),
                    "duration": self._calculate_duration(exp.get("start_date", ""), exp.get("end_date", "")),
                })
        
        # Calculate total years of experience
        total_experience = sum(exp.get("duration", 0) for exp in experience)
        
        # Extract education information
        education = []
        for edu in cv_data.get("education", []):
            if isinstance(edu, dict):
                education.append({
                    "degree": edu.get("degree", ""),
                    "field": edu.get("field_of_study", ""),
                    "institution": edu.get("institution", ""),
                })
        
        # Extract languages
        languages = cv_data.get("languages", [])
        
        return {
            "personal_info": personal_info,
            "skills": skills,
            "location": location,
            "total_experience": total_experience,
            "experience_details": experience,
            "education": education,
            "languages": languages,
            "summary": cv_data.get("summary", ""),
        }
    
    def _prepare_job_for_matching(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform parsed job data into format suitable for matching.
        
        Args:
            job_data (dict): Parsed job data
            
        Returns:
            dict: Job data prepared for matching
        """
        # Extract skills, ensuring we have a list of strings
        skills = job_data.get("skills", [])
        if isinstance(skills, list):
            # Handle different possible skill formats
            processed_skills = []
            for skill in skills:
                if isinstance(skill, str):
                    processed_skills.append(skill)
                elif isinstance(skill, dict) and "name" in skill:
                    processed_skills.append(skill["name"])
            skills = processed_skills
        else:
            skills = []
        
        # Extract and normalize experience requirement
        experience_required = job_data.get("experience_required", 0)
        if isinstance(experience_required, str):
            try:
                # Try to extract years from string (e.g., "5 years" -> 5)
                import re
                years_match = re.search(r'(\d+).*?(?:year|yr|an)', experience_required.lower())
                if years_match:
                    experience_required = int(years_match.group(1))
                else:
                    experience_required = 0
            except:
                experience_required = 0
        
        # Convert to remote boolean if it's a string
        remote = job_data.get("remote", False)
        if isinstance(remote, str):
            remote = remote.lower() in ["true", "yes", "1", "remote", "télétravail", "teletravail"]
            
        # Process and extract the job's contract type
        contract_type = job_data.get("contract_type", "")
        if isinstance(contract_type, str):
            contract_type = contract_type.upper()
            
            # Normalize contract type
            if "CDI" in contract_type:
                contract_type = "CDI"
            elif "CDD" in contract_type:
                contract_type = "CDD"
            elif "FREELANCE" in contract_type or "INDEPENDANT" in contract_type:
                contract_type = "FREELANCE"
            elif "STAGE" in contract_type or "INTERNSHIP" in contract_type:
                contract_type = "INTERNSHIP"
            elif "APPRENTISSAGE" in contract_type or "ALTERNANCE" in contract_type:
                contract_type = "APPRENTICESHIP"
        
        return {
            "title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "location": job_data.get("location", ""),
            "skills": skills,
            "experience_required": experience_required,
            "education_required": job_data.get("education", ""),
            "description": job_data.get("description", "") or job_data.get("job_description", ""),
            "job_type": job_data.get("job_type", ""),
            "contract_type": contract_type,
            "remote": remote,
            "responsibilities": job_data.get("responsibilities", []),
            "benefits": job_data.get("benefits", []),
        }
    
    def _calculate_duration(self, start_date: str, end_date: str) -> float:
        """
        Calculate duration in years between two dates.
        
        Args:
            start_date (str): Start date string
            end_date (str): End date string
            
        Returns:
            float: Duration in years
        """
        if not start_date:
            return 0
        
        # If end_date is empty, it means "present", so use current date
        if not end_date:
            import datetime
            end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        try:
            import datetime
            
            # Handle different date formats
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%B %Y", "%b %Y"]:
                try:
                    start = datetime.datetime.strptime(start_date[:10], fmt)
                    break
                except ValueError:
                    continue
            else:
                # If no format worked, try to extract just the year
                import re
                year_match = re.search(r'(\d{4})', start_date)
                if year_match:
                    start = datetime.datetime(int(year_match.group(1)), 1, 1)
                else:
                    return 0
            
            # Same for end date
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%B %Y", "%b %Y"]:
                try:
                    end = datetime.datetime.strptime(end_date[:10], fmt)
                    break
                except ValueError:
                    continue
            else:
                # If no format worked, try to extract just the year
                import re
                year_match = re.search(r'(\d{4})', end_date)
                if year_match:
                    end = datetime.datetime(int(year_match.group(1)), 1, 1)
                else:
                    return 0
            
            duration = (end - start).days / 365.25  # Approximate years
            return max(0, duration)  # Ensure non-negative
        except Exception as e:
            logger.warning(f"Error calculating duration: {str(e)}")
            return 0
