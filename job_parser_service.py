#!/usr/bin/env python3
"""Job Parser Service - Compatible SuperSmartMatch V3.0"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import re
from typing import Dict, Any

app = FastAPI(title="Job Parser Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobRequest(BaseModel):
    text: str

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "job_parser", "version": "1.0.0"}

@app.post("/analyze")
async def analyze_job(job_request: JobRequest):
    """Parse une description de poste en texte"""
    try:
        text = job_request.text
        
        result = {
            "content": {
                "job_title": extract_job_title(text),
                "company_name": extract_company(text),
                "location": extract_location(text),
                "skills": extract_skills(text),
                "experience_years": extract_experience_years(text),
                "education_level": extract_education_level(text),
                "job_description": text,
                "job_type": extract_job_type(text),
                "remote": "remote" in text.lower() or "télétravail" in text.lower(),
                "salary": extract_salary(text),
                "benefits": extract_benefits(text),
                "responsibilities": extract_responsibilities(text),
                "requirements": extract_requirements(text)
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-file")
async def analyze_job_file(file: UploadFile = File(...)):
    """Parse un fichier de description de poste"""
    try:
        content = await file.read()
        
        if file.content_type and 'text' in file.content_type:
            text = content.decode('utf-8')
        else:
            text = f"Contenu extrait de {file.filename}"
        
        # Réutiliser la logique d'analyse
        job_request = JobRequest(text=text)
        return await analyze_job(job_request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def extract_job_title(text: str) -> str:
    """Extrait le titre du poste"""
    patterns = [
        r"(?:poste|titre|position)[\s:]*([^\n]{10,80})",
        r"(lead|senior|junior|développeur|developer|ingénieur|chef|directeur|manager)[\s\w]{5,50}",
        r"recherche\s+(?:un|une)\s+([^\n]{10,60})",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            if len(title) > 5:
                return title
    
    # Chercher dans les premières lignes
    lines = text.split('\n')[:5]
    for line in lines:
        line = line.strip()
        if 10 <= len(line) <= 80 and any(word in line.lower() for word in ['developer', 'développeur', 'engineer', 'lead', 'manager']):
            return line
    
    return "Non spécifié"

def extract_company(text: str) -> str:
    """Extrait le nom de l'entreprise"""
    patterns = [
        r"(?:entreprise|société|company|chez)[\s:]*([^\n]{3,40})",
        r"(?:^|\n)([A-Z][a-zA-Z\s&]{5,30})(?:\s+recherche|\s+recrute)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            company = match.group(1).strip()
            if len(company) > 2:
                return company
    
    return "Non spécifié"

def extract_location(text: str) -> str:
    """Extrait la localisation"""
    patterns = [
        r"(?:localisation|lieu|location|adresse)[\s:]*([^\n]{5,50})",
        r"(Paris|Lyon|Marseille|Lille|Toulouse|Nice|Nantes|Bordeaux|Remote|Télétravail)",
        r"(\d{5}\s+[A-Za-z\s]+)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "Non spécifié"

def extract_skills(text: str) -> list:
    """Extrait les compétences requises"""
    # Compétences techniques étendues
    all_skills = [
        # Langages de programmation
        "python", "java", "javascript", "typescript", "php", "c++", "c#", "go", "rust", "scala", "ruby", "swift", "kotlin",
        # Frameworks web
        "django", "flask", "fastapi", "react", "angular", "vue", "svelte", "spring", "laravel", "express", "next.js",
        # Bases de données
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "oracle", "sql server", "cassandra", "dynamodb",
        # DevOps/Cloud
        "docker", "kubernetes", "aws", "gcp", "azure", "jenkins", "gitlab", "github", "ci/cd", "terraform", "ansible",
        # Outils de développement
        "git", "linux", "nginx", "apache", "jira", "confluence", "slack", "figma",
        # Compétences business
        "management", "leadership", "agile", "scrum", "product owner", "chef de projet", "communication"
    ]
    
    skills = []
    text_lower = text.lower()
    
    for skill in all_skills:
        if skill in text_lower:
            skills.append(skill)
    
    return skills

def extract_experience_years(text: str) -> int:
    """Extrait le nombre d'années d'expérience requis"""
    patterns = [
        r"(\d+)\+?\s*(?:ans?|années?|years?)\s*(?:d'|de\s*)?(?:expérience|experience)",
        r"(?:expérience|experience)[\s\w]*?(\d+)\+?\s*(?:ans?|années?|years?)",
        r"minimum\s+(\d+)\s*(?:ans?|années?)"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    
    return 0

def extract_education_level(text: str) -> str:
    """Extrait le niveau d'éducation requis"""
    education_levels = {
        "doctorat": "Doctorat",
        "phd": "Doctorat", 
        "master": "Master",
        "licence": "Licence",
        "bachelor": "Licence",
        "bac+5": "Master",
        "bac+3": "Licence",
        "bac+2": "BTS/DUT",
        "bts": "BTS/DUT",
        "dut": "BTS/DUT"
    }
    
    text_lower = text.lower()
    for level_key, level_value in education_levels.items():
        if level_key in text_lower:
            return level_value
    
    return "Non spécifié"

def extract_job_type(text: str) -> str:
    """Extrait le type de contrat"""
    contract_types = {
        "cdi": "CDI",
        "cdd": "CDD", 
        "stage": "Stage",
        "alternance": "Alternance",
        "freelance": "Freelance",
        "temps partiel": "Temps partiel",
        "temps plein": "Temps plein"
    }
    
    text_lower = text.lower()
    for contract_key, contract_value in contract_types.items():
        if contract_key in text_lower:
            return contract_value
    
    return "CDI"  # Par défaut

def extract_salary(text: str) -> Dict[str, str]:
    """Extrait la fourchette de salaire"""
    patterns = [
        r"(\d{2,3})[-–]\s*(\d{2,3})\s*k?\s*€",
        r"(\d{30,80})\s*[-–]\s*(\d{30,80})\s*€",
        r"salaire[\s:]*(\d{2,3})[-–](\d{2,3})k"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {"range": f"{match.group(1)}-{match.group(2)}K€"}
    
    return {"range": "Non spécifié"}

def extract_benefits(text: str) -> list:
    """Extrait les avantages"""
    benefits_keywords = [
        "télétravail", "remote", "tickets restaurant", "mutuelle", "rtt", "13ème mois",
        "stock options", "formation", "conférences", "flex office", "congés payés"
    ]
    
    benefits = []
    text_lower = text.lower()
    
    for benefit in benefits_keywords:
        if benefit in text_lower:
            benefits.append(benefit.title())
    
    return benefits

def extract_responsibilities(text: str) -> list:
    """Extrait les responsabilités"""
    resp_section = extract_section(text, ["responsabilités", "missions", "tâches", "rôle"])
    return [resp.strip() for resp in resp_section.split('\n') if len(resp.strip()) > 10][:5]

def extract_requirements(text: str) -> list:
    """Extrait les exigences"""
    req_section = extract_section(text, ["exigences", "requis", "profil", "compétences"])
    return [req.strip() for req in req_section.split('\n') if len(req.strip()) > 10][:5]

def extract_section(text: str, keywords: list) -> str:
    """Extrait une section basée sur des mots-clés"""
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in keywords):
            # Prendre les 5 lignes suivantes
            section_lines = lines[i+1:i+6]
            return '\n'.join(section_lines)
    
    return ""

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5053)