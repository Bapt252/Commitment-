import PyPDF2
import re
import logging

logger = logging.getLogger(__name__)

def parse_pdf(file_path):
    """
    Parse a PDF CV to extract structured information
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        dict: Structured CV data
    """
    try:
        # Open the PDF file
        with open(file_path, 'rb') as file:
            # Create a PDF reader object
            reader = PyPDF2.PdfReader(file)
            
            # Get the number of pages
            num_pages = len(reader.pages)
            
            # Extract text from all pages
            text = ""
            for page_num in range(num_pages):
                text += reader.pages[page_num].extract_text()
        
        # Process the extracted text to find relevant information
        result = extract_cv_data(text)
        return result
    
    except Exception as e:
        logger.error(f"Error parsing PDF: {str(e)}")
        raise

def extract_cv_data(text):
    """
    Extract structured data from CV text
    
    Args:
        text: Text content of the CV
        
    Returns:
        dict: Structured CV data
    """
    # Basic CV structure to fill
    cv_data = {
        "personal_info": {},
        "education": [],
        "experience": [],
        "skills": [],
        "languages": [],
        "raw_text": text
    }
    
    # Extract name (assuming it's at the beginning of the CV)
    name_match = re.search(r'^([A-Za-z\s]{2,50})', text.strip(), re.MULTILINE)
    if name_match:
        cv_data["personal_info"]["name"] = name_match.group(1).strip()
    
    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        cv_data["personal_info"]["email"] = email_match.group(0)
    
    # Extract phone number (various formats)
    phone_match = re.search(r'(\+\d{1,3}[\s\-]?)?(\(?\d{1,4}\)?[\s\-]?)?(\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{1,9})', text)
    if phone_match:
        cv_data["personal_info"]["phone"] = phone_match.group(0)
    
    # Extract skills (assuming they are listed after "Skills" or "Competences" keywords)
    skills_section = re.search(r'(?:Skills|Competences|Expertise)[:\s]*(.*?)(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if skills_section:
        skills_text = skills_section.group(1)
        # Split skills by commas, bullets, or newlines
        skills = re.split(r'[,•\n]+', skills_text)
        cv_data["skills"] = [skill.strip() for skill in skills if skill.strip()]
    
    # Extract education information
    education_section = re.search(r'(?:Education|Formation)[:\s]*(.*?)(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if education_section:
        education_text = education_section.group(1)
        # Look for patterns like "Year - Year Institution Degree"
        education_entries = re.findall(r'(\d{4})\s*[-–]\s*(\d{4}|\w+)\s+([^,\n]+),?\s*([^\n]*)', education_text)
        
        for entry in education_entries:
            cv_data["education"].append({
                "start_year": entry[0],
                "end_year": entry[1] if entry[1].isdigit() else "Present",
                "institution": entry[2].strip(),
                "degree": entry[3].strip()
            })
    
    # Extract work experience
    experience_section = re.search(r'(?:Experience|Employment|Work)[:\s]*(.*?)(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
    if experience_section:
        experience_text = experience_section.group(1)
        # Look for patterns like "Year - Year Company Position"
        experience_entries = re.findall(r'(\d{4})\s*[-–]\s*(\d{4}|\w+)\s+([^,\n]+),?\s*([^\n]*)', experience_text)
        
        for entry in experience_entries:
            cv_data["experience"].append({
                "start_year": entry[0],
                "end_year": entry[1] if entry[1].isdigit() else "Present",
                "company": entry[2].strip(),
                "position": entry[3].strip()
            })
    
    return cv_data
