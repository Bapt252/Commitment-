import re
import pandas as pd
import spacy
from typing import Dict, Any, List, Optional
import io
import logging
import os
import docx2txt
from pdfminer.high_level import extract_text

# Configurer le logging
logger = logging.getLogger(__name__)

# Chargement du modèle spaCy (lazy loading)
nlp = None

def load_nlp_model():
    """Charge le modèle spaCy de manière paresseuse"""
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("fr_core_news_lg")
            logger.info("Modèle spaCy fr_core_news_lg chargé avec succès")
        except:
            try:
                # Fallback sur le modèle anglais si le modèle français n'est pas disponible
                nlp = spacy.load("en_core_web_lg")
                logger.info("Modèle spaCy en_core_web_lg chargé avec succès (fallback)")
            except:
                # Fallback sur le petit modèle si les grands modèles ne sont pas disponibles
                nlp = spacy.load("fr_core_news_sm")
                logger.warning("Modèle spaCy fr_core_news_sm chargé (fallback). Les performances peuvent être réduites.")

    return nlp

async def parse_job_post(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Parse une fiche de poste à partir d'un fichier.
    Extrait les informations structurées comme le titre, la description, les compétences, etc.
    """
    # Détecter le type de fichier
    file_extension = filename.split('.')[-1].lower()
    
    # Extraction du texte selon le type de fichier
    if file_extension == 'pdf':
        text = extract_text_from_pdf(file_content)
    elif file_extension in ['docx', 'doc']:
        text = extract_text_from_docx(file_content)
    elif file_extension in ['txt', 'text']:
        text = file_content.decode('utf-8')
    else:
        raise ValueError(f"Format de fichier non supporté: {file_extension}")
    
    # Charger le modèle NLP
    nlp_model = load_nlp_model()
    
    # Traitement NLP avec spaCy
    doc = nlp_model(text)
    
    # Extraction des informations
    job_data = {
        "title": extract_job_title(doc, text),
        "description": extract_job_description(doc, text),
        "company": extract_company_name(doc, text),
        "location": extract_location(doc, text),
        "contract_type": extract_contract_type(doc, text),
        "salary_range": extract_salary(doc, text),
        "skills": extract_skills(doc, text)
    }
    
    return job_data

def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extrait le texte d'un fichier PDF.
    """
    try:
        # Utiliser un fichier temporaire en mémoire
        with io.BytesIO(file_content) as pdf_file:
            text = extract_text(pdf_file)
        return text
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte du PDF: {str(e)}")
        return ""

def extract_text_from_docx(file_content: bytes) -> str:
    """
    Extrait le texte d'un fichier DOCX.
    """
    try:
        # Utiliser un fichier temporaire en mémoire
        with io.BytesIO(file_content) as docx_file:
            text = docx2txt.process(docx_file)
        return text
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction du texte du DOCX: {str(e)}")
        return ""

def extract_job_title(doc, text: str) -> str:
    """
    Extrait le titre du poste à partir du document spaCy et du texte brut.
    """
    # Approche 1: Rechercher les titres typiques en début de document
    title_patterns = [
        r"(?i)^.*(?:recherche|embauche|recrute)\s+(?:un|une|des)?\s+(.*?)(?:\n|$)",
        r"(?i)^.*(?:poste|offre)\s*:\s*(.*?)(?:\n|$)",
        r"(?i)^.*(?:intitulé du poste)\s*:\s*(.*?)(?:\n|$)",
        r"(?i)^job title\s*:\s*(.*?)(?:\n|$)"
    ]
    
    for pattern in title_patterns:
        match = re.search(pattern, text[:500])
        if match:
            return match.group(1).strip()
    
    # Approche 2: Utiliser NER pour les titres professionnels
    for ent in doc.ents:
        if ent.label_ in ["PROFESSION", "ROLE", "WORK_OF_ART"] and len(ent.text) < 50:
            # Vérifier si c'est probablement un titre de poste
            if any(term in ent.text.lower() for term in ["développeur", "ingénieur", "manager", "directeur", "consultant", "analyst"]):
                return ent.text.strip()
    
    # Approche 3: Rechercher les titres communs dans le texte
    common_job_titles = [
        "développeur", "ingénieur", "architecte", "chef de projet", "project manager",
        "data scientist", "analyste", "consultant", "technicien", "responsable"
    ]
    
    for title in common_job_titles:
        pattern = rf"(?i)\b{title}\s+(\w+(?:\s+\w+){{0,3}})"
        match = re.search(pattern, text[:1000])
        if match:
            return f"{title} {match.group(1)}".strip()
    
    # Fallback: retourner les premiers mots du document
    first_lines = text.split('\n')[0:2]
    return first_lines[0].strip() if first_lines else "Titre inconnu"

def extract_job_description(doc, text: str) -> str:
    """
    Extrait la description du poste.
    """
    # Rechercher des sections typiques de description
    description_patterns = [
        r"(?i)(?:description|détails|présentation)\s+(?:du poste|de la mission)\s*:\s*(.*?)(?:(?:compétences|profil|qualifications|expérience|nous recherchons)|\Z)",
        r"(?i)(?:missions|responsabilités)\s*:\s*(.*?)(?:(?:compétences|profil|qualifications|expérience|nous recherchons)|\Z)",
        r"(?i)(?:à propos du poste)\s*:\s*(.*?)(?:(?:compétences|profil|qualifications|expérience|nous recherchons)|\Z)"
    ]
    
    for pattern in description_patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # Nettoyer la description (supprimer les espaces multiples, etc.)
            desc = match.group(1).strip()
            desc = re.sub(r'\s+', ' ', desc)
            return desc
    
    # Fallback: prendre les premiers paragraphes (exclus le titre)
    paragraphs = [p.strip() for p in text.split('\n\n')]
    if len(paragraphs) > 1:
        return '\n\n'.join(paragraphs[1:4])  # Prendre quelques paragraphes
    
    return text[:500] + "..."  # Si tout échoue, prendre les 500 premiers caractères

def extract_company_name(doc, text: str) -> str:
    """
    Extrait le nom de l'entreprise.
    """
    # Rechercher des patterns d'entreprise
    company_patterns = [
        r"(?i)(?:entreprise|société|company|à propos de)\s*:\s*([\w\s'-]+(?:SAS|SARL|SA|Inc\.?|LLC|GmbH)?)",
        r"(?i)(?:nous rejoindre chez|postuler chez|travailler chez|travailler pour)\s+([\w\s'-]+(?:SAS|SARL|SA|Inc\.?|LLC|GmbH)?)",
        r"(?i)([\w\s'-]+(?:SAS|SARL|SA|Inc\.?|LLC|GmbH))\s+(?:recherche|recrute|embauche)"
    ]
    
    for pattern in company_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    # Rechercher des entités d'organisation
    for ent in doc.ents:
        if ent.label_ == "ORG":
            # Vérifier que ce n'est pas un terme générique ou une technologie
            if not any(tech in ent.text.lower() for tech in ["python", "java", "javascript", "react", "angular", "vue"]):
                return ent.text
    
    return "Non spécifié"

def extract_location(doc, text: str) -> str:
    """
    Extrait la localisation du poste.
    """
    # Rechercher des patterns de localisation
    location_patterns = [
        r"(?i)(?:lieu|location|localisation|ville|basé à|based in)\s*:\s*([\w\s,'-]+)",
        r"(?i)(?:poste basé à|poste situé à|travail à)\s+([\w\s,'-]+)",
        r"(?i)(?:télétravail|remote|à distance)"
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text)
        if match:
            # Le dernier pattern est pour le télétravail sans groupe de capture
            if "télétravail" in pattern or "remote" in pattern:
                return "Télétravail / Remote"
            return match.group(1).strip()
    
    # Rechercher des entités de lieu
    for ent in doc.ents:
        if ent.label_ in ["LOC", "GPE"]:
            return ent.text
    
    return "Non spécifié"

def extract_contract_type(doc, text: str) -> str:
    """
    Extrait le type de contrat.
    """
    # Rechercher des patterns de type de contrat
    contract_patterns = [
        r"(?i)(?:type de contrat|contract type)\s*:\s*(CDI|CDD|Stage|Apprentissage|Freelance|Intérim|Full-time|Part-time)",
        r"(?i)\b(CDI|CDD|Stage|Apprentissage|Freelance|Intérim|Full-time|Part-time)\b"
    ]
    
    for pattern in contract_patterns:
        match = re.search(pattern, text)
        if match:
            if "type de contrat" in pattern or "contract type" in pattern:
                return match.group(1).strip()
            else:
                return match.group(0).strip()
    
    return "Non spécifié"

def extract_salary(doc, text: str) -> str:
    """
    Extrait la fourchette de salaire.
    """
    # Rechercher des patterns de salaire
    salary_patterns = [
        r"(?i)(?:salaire|rémunération|salary|compensation)\s*:\s*([^.]*?€[^.]*)",
        r"(?i)(?:salaire|rémunération|salary|compensation)\s*(?:de|entre|from|between)?\s*(\d+[k]?[€$]?\s*[-à]\s*\d+[k]?[€$]?)",
        r"(?i)(\d+[k]?[€$]?\s*[-à]\s*\d+[k]?[€$]?)",
        r"(?i)(?:jusqu'à|up to)\s*(\d+[k]?[€$]?)"
    ]
    
    for pattern in salary_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    
    return "Non spécifié"

def extract_skills(doc, text: str) -> List[Dict[str, Any]]:
    """
    Extrait les compétences requises.
    """
    skills = []
    
    # Liste de compétences techniques courantes
    tech_skills = [
        "Python", "Java", "JavaScript", "TypeScript", "C#", "C++", "PHP", "Ruby", "Go", "Rust",
        "React", "Angular", "Vue.js", "Node.js", "Express", "Django", "Flask", "Spring", "ASP.NET",
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "Redis", "Elasticsearch",
        "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "Git", "GitHub", "GitLab",
        "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy", "NLTK", "spaCy", "Hadoop", "Spark",
        "HTML", "CSS", "SASS", "LESS", "Bootstrap", "Tailwind",
        "Agile", "Scrum", "Kanban", "Jira", "Confluence",
        "Linux", "Unix", "Windows", "MacOS",
        "REST", "GraphQL", "gRPC", "Microservices", "API", "SOAP",
        "CI/CD", "DevOps", "MLOps", "DataOps"
    ]
    
    # Rechercher des sections de compétences
    skills_sections = []
    skills_patterns = [
        r"(?i)(?:compétences|skills|requirements|qualifications)\s*(?:requises|techniques|required|techniques)?\s*:([^:]*?)(?:(?:\n\n|\n\s*\n)|(?:expérience|profil|éducation|formation|langues|experience|profile|education|languages):|\Z)",
        r"(?i)(?:profil recherché|candidate profile)\s*:([^:]*?)(?:(?:\n\n|\n\s*\n)|(?:expérience|compétences|éducation|formation|langues|experience|skills|education|languages):|\Z)"
    ]
    
    for pattern in skills_patterns:
        matches = re.finditer(pattern, text, re.DOTALL)
        for match in matches:
            skills_sections.append(match.group(1).strip())
    
    # Si des sections ont été trouvées, les analyser
    parsed_skills = set()
    if skills_sections:
        for section in skills_sections:
            # Chercher des listes à puces ou numérotées
            bullet_items = re.findall(r"(?:^|\n)[\s•\-*✓➢➤→⁃◦▪▸]+\s*([^\n]+)", section)
            if bullet_items:
                for item in bullet_items:
                    # Vérifier si l'item contient des compétences techniques connues
                    for skill in tech_skills:
                        if re.search(rf"\b{re.escape(skill)}\b", item, re.IGNORECASE):
                            parsed_skills.add(skill)
            
            # Chercher également dans le texte complet de la section
            for skill in tech_skills:
                if re.search(rf"\b{re.escape(skill)}\b", section, re.IGNORECASE):
                    parsed_skills.add(skill)
    else:
        # Si aucune section spécifique n'a été trouvée, chercher dans tout le texte
        for skill in tech_skills:
            if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
                parsed_skills.add(skill)
    
    # Convertir en format de sortie
    for skill in sorted(parsed_skills):
        skills.append({
            "name": skill,
            "level": None,
            "description": None
        })
    
    return skills
