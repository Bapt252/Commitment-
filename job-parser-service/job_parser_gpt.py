"""
job_parser_gpt.py
API service for GPT-based job posting parsing

This module provides a Flask API endpoint for parsing job postings with the GPT model.
"""

import os
import json
import logging
import tempfile
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import openai

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Blueprint for job parser GPT API
job_parser_gpt_bp = Blueprint('job_parser_gpt', __name__)

# Get API key from environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
GPT_MODEL = os.environ.get('GPT_MODEL', 'gpt-3.5-turbo')

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

@job_parser_gpt_bp.route('/health-check', methods=['GET'])
def health_check():
    """Health check endpoint to verify API availability"""
    return jsonify({"status": "ok", "message": "Job Parser GPT API is running"}), 200

@job_parser_gpt_bp.route('/parse-job-gpt', methods=['POST'])
def parse_job_with_gpt():
    """
    Parse job posting with GPT
    
    Accepts either file upload or text input
    Returns parsed job information in JSON format
    """
    try:
        job_text = ""
        
        # Check if request has file or text
        if 'file' in request.files:
            file = request.files['file']
            # Create temporary file to store uploaded content
            with tempfile.NamedTemporaryFile(delete=False) as temp:
                file.save(temp.name)
                with open(temp.name, 'r', encoding='utf-8', errors='ignore') as f:
                    job_text = f.read()
                os.unlink(temp.name)  # Clean up temp file
        elif 'text' in request.form:
            job_text = request.form['text']
        else:
            return jsonify({"error": "No file or text provided"}), 400
        
        # Log info about the request
        logger.info(f"Received job parsing request: {len(job_text)} characters")
        
        # Call GPT API to parse the job posting
        result = call_gpt_for_parsing(job_text)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error in parse_job_with_gpt: {str(e)}")
        return jsonify({"error": str(e)}), 500

def call_gpt_for_parsing(job_text):
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

def register_job_parser_gpt(app):
    """Register the job parser GPT blueprint with the app"""
    app.register_blueprint(job_parser_gpt_bp, url_prefix='/api')
    CORS(app)  # Enable CORS for all routes
    logger.info("Registered Job Parser GPT API endpoints")
    
    # Check if API key is configured
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set. GPT parsing will not work.")

# For direct execution testing
if __name__ == "__main__":
    app = Flask(__name__)
    register_job_parser_gpt(app)
    app.run(debug=True, port=5055)
