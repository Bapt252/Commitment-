#!/usr/bin/env python3
"""CV Parser Service - Compatible SuperSmartMatch V3.0"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import re
from typing import Dict, Any

app = FastAPI(title="CV Parser Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "cv_parser", "version": "1.0.0"}

@app.post("/api/parse-cv/")
async def parse_cv(file: UploadFile = File(...), force_refresh: str = Form("false")):
    """Parse un CV uploadé"""
    try:
        # Lire le contenu du fichier
        content = await file.read()
        
        # Si c'est un fichier texte, décoder
        if file.content_type and 'text' in file.content_type:
            text_content = content.decode('utf-8')
        else:
            # Pour PDF/Word, simulation extraction (à remplacer par vraie lib)
            text_content = f"Contenu simulé de {file.filename}"
        
        # Parsing basique du CV
        parsed_content = parse_cv_content(text_content)
        
        return {
            "id": f"cv_{hash(file.filename)}",
            "filename": file.filename,
            "parsed_content": parsed_content,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def parse_cv_content(text: str) -> Dict[str, Any]:
    """Parse le contenu d'un CV"""
    
    # Extraction nom/email/téléphone
    name = extract_name(text)
    email = extract_email(text) 
    phone = extract_phone(text)
    
    # Extraction compétences
    skills = extract_skills(text)
    
    # Extraction expérience
    experience = extract_experience(text)
    
    # Extraction formation
    education = extract_education(text)
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "location": {"text": extract_location(text)},
        "summary": extract_summary(text),
        "skills": skills,
        "experience": experience,
        "education": education,
        "languages": extract_languages(text),
        "certifications": []
    }

def extract_name(text: str) -> str:
    """Extrait le nom du CV"""
    lines = text.split('\n')[:5]  # Chercher dans les 5 premières lignes
    for line in lines:
        line = line.strip()
        if len(line) > 5 and len(line) < 50 and ' ' in line:
            # Simple heuristique pour détecter un nom
            words = line.split()
            if len(words) >= 2 and all(word.isalpha() or word.isupper() for word in words):
                return line
    return "Non spécifié"

def extract_email(text: str) -> str:
    """Extrait l'email"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else ""

def extract_phone(text: str) -> str:
    """Extrait le téléphone"""
    phone_pattern = r'(?:\+33|0)[1-9](?:[.\s-]?\d{2}){4}'
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else ""

def extract_location(text: str) -> str:
    """Extrait la localisation"""
    location_patterns = [
        r"(?:Paris|Lyon|Marseille|Lille|Toulouse|Nice|Nantes|Bordeaux)",
        r"\d{5}\s+\w+",  # Code postal + ville
    ]
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
    return ""

def extract_summary(text: str) -> str:
    """Extrait le résumé/profil"""
    summary_keywords = ["profil", "résumé", "objectif", "présentation"]
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in summary_keywords):
            # Prendre les 3 lignes suivantes
            summary_lines = lines[i+1:i+4]
            return ' '.join(summary_lines).strip()
    return ""

def extract_skills(text: str) -> list:
    """Extrait les compétences"""
    # Compétences techniques communes
    common_skills = [
        # Langages
        "python", "java", "javascript", "typescript", "php", "c++", "c#", "go", "rust", "scala",
        # Frameworks/Libs
        "django", "flask", "fastapi", "react", "angular", "vue", "spring", "laravel", "express",
        # Bases de données
        "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "sql",
        # DevOps/Cloud
        "docker", "kubernetes", "aws", "gcp", "azure", "jenkins", "gitlab", "github", "ci/cd",
        # Outils
        "git", "linux", "windows", "macos", "nginx", "apache", "terraform"
    ]
    
    skills = []
    text_lower = text.lower()
    
    for skill in common_skills:
        if skill in text_lower:
            skills.append(skill)
    
    return skills

def extract_experience(text: str) -> list:
    """Extrait l'expérience professionnelle"""
    experience = []
    
    # Recherche de patterns d'expérience
    exp_patterns = [
        r"(\d{4})\s*[-–]\s*(\d{4}|\w+)\s*[:\-]\s*(.{10,100})",
        r"(.{10,50})\s*[-–]\s*(.{10,50})\s*\((\d{4})\s*[-–]\s*(\d{4}|\w+)\)"
    ]
    
    for pattern in exp_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches[:5]:  # Limiter à 5 expériences
            if len(match) >= 3:
                experience.append({
                    "title": match[2] if len(match) > 2 else "Non spécifié",
                    "company": "Non spécifié",
                    "start_date": match[0] if match[0].isdigit() else "",
                    "end_date": match[1] if len(match) > 1 else "",
                    "description": ""
                })
    
    return experience

def extract_education(text: str) -> list:
    """Extrait la formation"""
    education = []
    
    # Mots-clés de formation
    education_keywords = ["master", "licence", "bac", "école", "université", "formation", "diplôme"]
    
    lines = text.split('\n')
    for line in lines:
        if any(keyword in line.lower() for keyword in education_keywords):
            education.append({
                "degree": line.strip(),
                "field": "",
                "institution": "",
                "start_date": "",
                "end_date": ""
            })
    
    return education[:3]  # Limiter à 3 formations

def extract_languages(text: str) -> list:
    """Extrait les langues"""
    languages = []
    common_languages = ["français", "anglais", "espagnol", "allemand", "italien", "chinois", "japanese"]
    
    text_lower = text.lower()
    for lang in common_languages:
        if lang in text_lower:
            languages.append(lang.capitalize())
    
    return languages

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5051)