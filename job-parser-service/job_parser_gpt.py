"""
job_parser_gpt.py
API service for GPT-based job posting parsing

This module provides a FastAPI APIRouter endpoint for parsing job postings with the GPT model.
"""

import os
import json
import logging
import tempfile
from fastapi import APIRouter, HTTPException, Form, File, UploadFile, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import openai

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize APIRouter for job parser GPT API
job_parser_gpt_bp = APIRouter()

# Get API key from environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
GPT_MODEL = os.environ.get('GPT_MODEL', 'gpt-3.5-turbo')

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

# Pydantic models for response
class JobParsingResult(BaseModel):
    title: str
    company: str
    location: str
    contract_type: str
    skills: List[str]
    experience: str
    education: str
    salary: str
    responsibilities: List[str]
    benefits: List[str]

class HealthResponse(BaseModel):
    status: str
    message: str

@job_parser_gpt_bp.get('/health-check', response_model=HealthResponse)
async def health_check():
    """Health check endpoint to verify API availability"""
    return HealthResponse(status="ok", message="Job Parser GPT API is running")

@job_parser_gpt_bp.post('/parse-job-gpt')
async def parse_job_with_gpt(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None)
):
    """
    Parse job posting with GPT
    
    Accepts either file upload or text input
    Returns parsed job information in JSON format
    """
    try:
        job_text = ""
        
        # Check if request has file or text
        if file:
            content = await file.read()
            job_text = content.decode('utf-8', errors='ignore')
        elif text:
            job_text = text
        else:
            raise HTTPException(status_code=400, detail="No file or text provided")
        
        # Log info about the request
        logger.info(f"Received job parsing request: {len(job_text)} characters")
        
        # Call GPT API to parse the job posting
        result = await call_gpt_for_parsing(job_text)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        logger.error(f"Error in parse_job_with_gpt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def call_gpt_for_parsing(job_text: str) -> dict:
    """
    Call GPT API to parse job posting
    
    Args:
        job_text (str): The job posting text to parse
        
    Returns:
        dict: The parsed job information
    """
    try:
        # Create prompt for GPT
        prompt = f"""Extract key information from this job posting for automated parsing.
        For each field, find relevant information and return in the specified format.
        
        JOB POSTING:
        {job_text}
        
        Return the information in this JSON format:
        {{
            "title": "Job title",
            "company": "Company name",
            "location": "Job location",
            "contract_type": "Contract type (CDI, CDD, etc.)",
            "skills": ["Skill 1", "Skill 2", ...],
            "experience": "Required experience level",
            "education": "Required education",
            "salary": "Offered salary",
            "responsibilities": ["Responsibility 1", "Responsibility 2", ...],
            "benefits": ["Benefit 1", "Benefit 2", ...]
        }}
        
        If certain information is not found, use empty strings or empty arrays.
        Respond with ONLY the JSON, no additional text.
        """
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a specialized assistant that extracts job posting information into structured data. Respond only with JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2  # Lower temperature for more consistent results
        )
        
        # Extract the response content
        content = response.choices[0].message.content
        
        # Try to parse JSON from response
        try:
            # Look for JSON in the response
            json_start = content.find('{')
            json_end = content.rfind('}')
            
            if json_start >= 0 and json_end >= 0:
                json_str = content[json_start:json_end+1]
                parsed_result = json.loads(json_str)
            else:
                # If no JSON markers found, try to parse the entire content
                parsed_result = json.loads(content)
                
            # Log successful parsing
            logger.info(f"Successfully parsed job posting with GPT: {parsed_result.get('title', 'Unknown')}")
            
            return parsed_result
        
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from GPT response: {content[:100]}...")
            # Return a simplified structure with the raw response as a fallback
            return {
                "error": "Failed to parse JSON from GPT response",
                "raw_response": content,
                "title": "Parsing Error"
            }
    
    except Exception as e:
        logger.error(f"Error calling GPT API: {str(e)}")
        return {"error": str(e), "title": "API Error"}

# Check if API key is configured when module is imported
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not set. GPT parsing will not work.")
