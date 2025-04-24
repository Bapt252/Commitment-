import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class ParsingService:
    """Client service to interact with the CV Parser microservice"""
    
    def __init__(self, base_url=None):
        self.base_url = base_url or current_app.config.get('CV_PARSER_SERVICE_URL')
        if not self.base_url:
            raise ValueError("CV Parser service URL is not configured")
    
    def parse_cv(self, file_path=None, file_content=None, file_type=None):
        """
        Parse a CV by sending it to the parser service
        
        Args:
            file_path: Path to the CV file
            file_content: Content of the CV file
            file_type: Type of file ('pdf', 'docx', etc.)
            
        Returns:
            dict: Parsed CV data
        """
        try:
            url = f"{self.base_url}/api/v1/parse"
            
            if file_path:
                with open(file_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post(url, files=files)
            elif file_content:
                files = {'file': (f'cv.{file_type}', file_content, f'application/{file_type}')}
                response = requests.post(url, files=files)
            else:
                raise ValueError("Either file_path or file_content must be provided")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"CV parsing failed: {response.text}")
                return {'error': 'Parsing failed', 'details': response.text}
        
        except Exception as e:
            logger.exception("Error in parse_cv")
            return {'error': str(e)}
    
    def get_parser_status(self):
        """Check the status of the parsing service"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            logger.exception("Error checking parser service status")
            return False

# Instantiate a global service client
cv_parser = ParsingService()
