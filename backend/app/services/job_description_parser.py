from typing import Dict, Any, List, Optional
import re

def parse_job_description(text: str) -> Dict[str, Any]:
    """
    Analyse une fiche de poste pour en extraire les informations clés.
    
    Args:
        text: Le texte de la fiche de poste à analyser
        
    Returns:
        Un dictionnaire contenant les informations extraites
    """
    # Initialiser le dictionnaire de résultats
    result = {
        "title": "",
        "description": "",
        "requirements": "",
        "salary_min": None,
        "salary_max": None,
        "location": "",
        "job_type": "",
        "experience_level": "",
        "skills": []
    }
    
    # Extraction du titre
    title_patterns = [
        r"\b(?:poste|offre|emploi)\s*:?\s*([\w\s\-\(\)]+)\b",
        r"^([\w\s\-\(\)]+)\n"
    ]
    for pattern in title_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["title"] = match.group(1).strip()
            break
    
    # Extraction de la localisation
    location_patterns = [
        r"\blieu\s*:?\s*([\w\s\-]+)\b",
        r"\blocalisation\s*:?\s*([\w\s\-]+)\b",
        r"\bsite\s*:?\s*([\w\s\-]+)\b",
        r"\b(?:à|a)\s+([\w\s\-]+)\b"
    ]
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            result["location"] = match.group(1).strip()
            break
    
    # Extraction du type de poste
    job_type_patterns = {
        "CDI": r"\bCDI\b",
        "CDD": r"\bCDD\b",
        "Stage": r"\bstage\b",
        "Alternance": r"\balternance\b",
        "Freelance": r"\bfreelance\b",
        "Temps partiel": r"\btemps partiel\b",
        "Temps plein": r"\btemps plein\b",
    }
    for job_type, pattern in job_type_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            result["job_type"] = job_type
            break
    
    # Extraction du niveau d'expérience
    experience_patterns = [
        r"\bexp[ée]rience\s*:?\s*([\d\-\+]+)\s*an",
        r"\bexp[ée]rience\s*de\s*([\d\-\+]+)\s*an",
        r"\b([\d\-\+]+)\s*an\w*\s*d'exp[ée]rience"
    ]
    for pattern in experience_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            exp_value = match.group(1).strip()
            # Conversion en niveau
            if "+" in exp_value or int(exp_value.replace("+", "")) >= 5:
                result["experience_level"] = "Senior"
            elif int(exp_value) >= 2:
                result["experience_level"] = "Mid-level"
            else:
                result["experience_level"] = "Junior"
            break
    
    # Extraction du salaire
    salary_patterns = [
        r"\bsalaire\s*:?\s*([\d\s\-\à\,\.\€\k]+)\b",
        r"\br[ée]mun[ée]ration\s*:?\s*([\d\s\-\à\,\.\€\k]+)\b"
    ]
    for pattern in salary_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            salary_text = match.group(1).strip().lower()
            # Extraire les chiffres
            numbers = re.findall(r'\d+(?:[\.,]\d+)?', salary_text)
            if len(numbers) >= 2:
                try:
                    result["salary_min"] = float(numbers[0].replace(',', '.'))
                    result["salary_max"] = float(numbers[1].replace(',', '.'))
                    
                    # Ajuster si K€ est utilisé
                    if 'k' in salary_text or 'k€' in salary_text:
                        result["salary_min"] *= 1000
                        result["salary_max"] *= 1000
                except ValueError:
                    pass
            elif len(numbers) == 1:
                try:
                    value = float(numbers[0].replace(',', '.'))
                    # Ajuster si K€ est utilisé
                    if 'k' in salary_text or 'k€' in salary_text:
                        value *= 1000
                    
                    if '-' in salary_text or 'à' in salary_text:
                        # Estimation d'une fourchette si on a seulement un chiffre
                        result["salary_min"] = value * 0.9
                        result["salary_max"] = value * 1.1
                    else:
                        result["salary_min"] = value
                        result["salary_max"] = value
                except ValueError:
                    pass
            break
    
    # Extraction des compétences techniques
    # Liste de compétences techniques courantes
    common_skills = [
        "Python", "Java", "JavaScript", "C++", "C#", "PHP", "Ruby", "Swift", "Kotlin",
        "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", "Spring", "Laravel",
        "SQL", "MySQL", "PostgreSQL", "MongoDB", "Oracle", "Redis", "Docker", "Kubernetes",
        "AWS", "Azure", "GCP", "Linux", "Git", "CI/CD", "Agile", "Scrum", "DevOps",
        "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "NLP", "Data Science",
        "Power BI", "Tableau", "Excel", "HTML", "CSS", "SEO", "SEM", "Marketing", "Sales",
        "CRM", "Salesforce", "Communication", "Leadership", "Gestion de projet", "Product Management"
    ]
    
    skills_found = []
    for skill in common_skills:
        if re.search(r"\b" + re.escape(skill) + r"\b", text, re.IGNORECASE):
            skills_found.append(skill)
    
    # Extraire la section compétences
    skills_section = re.search(r"\b(?:comp[ée]tences|skills)\s*:?[^\n]*\n+([^#]+?)(?:\n\n|\n\w|$)", text, re.IGNORECASE)
    if skills_section:
        # Chercher des compétences listées avec des puces
        additional_skills = re.findall(r"[\-\*•]\s*([\w\s\-\.\+\#]+)\b", skills_section.group(1))
        for skill in additional_skills:
            skill = skill.strip()
            if len(skill) > 2 and skill not in skills_found:  # Éviter les initiales ou caractères isolés
                skills_found.append(skill)
    
    result["skills"] = skills_found
    
    # Extraction de la description et des exigences
    # Recherche des sections clés
    sections = {
        "description": re.search(r"\b(?:description|poste|role|missions|responsabilit[ée]s)\s*:?[^\n]*\n+([^#]+?)(?:\n\n|\n\w|$)", text, re.IGNORECASE),
        "requirements": re.search(r"\b(?:exigences|profil|requirements|qualifications|pr[ée]requis)\s*:?[^\n]*\n+([^#]+?)(?:\n\n|\n\w|$)", text, re.IGNORECASE)
    }
    
    # Extraire le texte correspondant
    for key, match in sections.items():
        if match:
            result[key] = match.group(1).strip()
    
    # Si pas de description mais du texte, utiliser les premiers paragraphes
    if not result["description"] and len(text) > 100:
        paragraphs = re.split(r"\n\s*\n", text)
        if len(paragraphs) > 1:
            result["description"] = paragraphs[1].strip()
        else:
            result["description"] = paragraphs[0].strip()
    
    return result