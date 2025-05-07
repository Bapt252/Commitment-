def extract_job_info_custom(text):
    """Fonction d'extraction adaptée au format observé sur la capture d'écran"""
    import re
    import logging
    
    logger = logging.getLogger(__name__)
    logger.debug("Utilisation de l'extracteur personnalisé")
    
    # Dictionnaire pour stocker les informations extraites
    job_info = {
        "title": "",
        "skills": [],
        "contract_type": "",
        "location": "",
        "experience": "",
        "education": "",
        "salary": "",
        "company": ""
    }
    
    # Log du texte complet pour déboguer
    logger.debug("Texte complet du PDF:\n" + text)
    
    # Recherche du titre du poste après "Poste"
    title_match = re.search(r"(?:^|\n)[\s•]*Poste[\s:]*(.+?)(?:\n|$)", text, re.IGNORECASE)
    if title_match:
        job_info["title"] = title_match.group(1).strip()
        logger.debug(f"Titre du poste trouvé: {job_info['title']}")
    
    # Recherche des compétences après "Compétences requises"
    skills_match = re.search(r"(?:^|\n)[\s•]*Compétences requises[\s:]*(.+?)(?:\n|$)", text, re.IGNORECASE | re.DOTALL)
    if skills_match:
        skills_text = skills_match.group(1).strip()
        # Si les compétences sont séparées par des espaces, on les divise
        skills = re.split(r"\s+", skills_text)
        # Filtrer les compétences vides
        job_info["skills"] = [skill.strip() for skill in skills if skill.strip()]
        logger.debug(f"Compétences trouvées: {job_info['skills']}")
    
    # Recherche de l'expérience après "Expérience"
    experience_match = re.search(r"(?:^|\n)[\s•]*Expérience[\s:]*(.+?)(?:\n|$)", text, re.IGNORECASE)
    if experience_match:
        job_info["experience"] = experience_match.group(1).strip()
        logger.debug(f"Expérience trouvée: {job_info['experience']}")
    
    # Recherche du type de contrat après "Type de contrat"
    contract_match = re.search(r"(?:^|\n)[\s•]*Type de contrat[\s:]*(.+?)(?:\n|$)", text, re.IGNORECASE)
    if contract_match:
        job_info["contract_type"] = contract_match.group(1).strip()
        logger.debug(f"Type de contrat trouvé: {job_info['contract_type']}")
    
    # Recherche directe de termes spécifiques
    if "CDI" in text:
        job_info["contract_type"] = "CDI"
    elif "CDD" in text:
        job_info["contract_type"] = "CDD"
    
    # Extraction de compétences techniques courantes si aucune n'a été trouvée
    if not job_info["skills"]:
        tech_skills = ["JavaScript", "React", "Node.js", "Python", "MongoDB", "SQL", "HTML", "CSS", "Java", "PHP"]
        found_skills = []
        for skill in tech_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found_skills.append(skill)
        
        if found_skills:
            job_info["skills"] = found_skills
            logger.debug(f"Compétences détectées par recherche de mots-clés: {job_info['skills']}")
    
    logger.debug(f"Informations extraites par l'extracteur personnalisé: {job_info}")
    return job_info
