"""Module pour analyser et extraire les informations des fiches de poste."""
import re

# Catégories d'informations à extraire d'une fiche de poste
JOB_CATEGORIES = {
    "JOB_TITLE": ["titre", "poste", "intitulé"],
    "EXPERIENCE": ["expérience", "années d'expérience", "exp", "senior", "junior", "confirmé"],
    "SKILLS": ["compétences", "skills", "tech", "technologies", "outils", "langages", "framework"],
    "EDUCATION": ["formation", "diplôme", "études", "diplômé", "bac+", "ingénieur", "master"],
    "CONTRACT": ["contrat", "cdd", "cdi", "freelance", "stage", "alternance", "temps", "partiel", "plein"],
    "LOCATION": ["lieu", "localisation", "ville", "site", "adresse", "remote", "télétravail", "région", "pays"],
    "SALARY": ["salaire", "rémunération", "k€", "keur", "package", "avantages", "benefits"]
}

# Expressions régulières pour identifier certains patterns spécifiques
REGEX_PATTERNS = {
    "EXPERIENCE_YEARS": r"(\d+)[\s-]*(ans?|années?|an d['']expérience|années? d['']expérience)",
    "SALARY_RANGE": r"([\d\s]+[k€KE])[^\d]+([\d\s]+[k€KE])",
    "EDUCATION_LEVEL": r"bac\s*\+\s*(\d+)",
    "CONTRACT_TYPE": r"cdi|cdd|stage|alternance|freelance|consultant|temps (plein|partiel)",
    "REMOTE_WORK": r"(full remote|télétravail|remote|à distance)(\s*\d+\s*j(ours?)?)?"
}

def parse_job_description(job_description):
    """
    Parse une fiche de poste et extrait les informations pertinentes
    
    Args:
        job_description (str): Le texte de la fiche de poste
        
    Returns:
        dict: Un dictionnaire avec les informations extraites et les scores de confiance
    """
    # Résultat de l'analyse
    result = {
        "doc_type": "job",
        "extracted_data": {
            "titre": "",
            "experience": "",
            "competences": [],
            "formation": "",
            "contrat": "",
            "localisation": "",
            "remuneration": ""
        },
        "confidence_scores": {
            "global": 0.0,
            "titre": 0.0,
            "experience": 0.0,
            "competences": 0.0,
            "formation": 0.0,
            "contrat": 0.0,
            "localisation": 0.0,
            "remuneration": 0.0
        }
    }
    
    # Analyse du texte
    text = job_description.lower()
    
    # Diviser le texte en paragraphes et lignes
    paragraphs = job_description.split('\n\n')
    lines = job_description.split('\n')
    
    # Extraire le titre du poste
    result["extracted_data"]["titre"] = extract_job_title(paragraphs, lines)
    result["confidence_scores"]["titre"] = calculate_confidence(result["extracted_data"]["titre"])
    
    # Extraire l'expérience requise
    result["extracted_data"]["experience"] = extract_experience(job_description)
    result["confidence_scores"]["experience"] = calculate_confidence(result["extracted_data"]["experience"])
    
    # Extraire les compétences techniques
    result["extracted_data"]["competences"] = extract_skills(job_description)
    result["confidence_scores"]["competences"] = 0.8 if result["extracted_data"]["competences"] else 0.3
    
    # Extraire le niveau d'études
    result["extracted_data"]["formation"] = extract_education(job_description)
    result["confidence_scores"]["formation"] = calculate_confidence(result["extracted_data"]["formation"])
    
    # Extraire le type de contrat
    result["extracted_data"]["contrat"] = extract_contract(job_description)
    result["confidence_scores"]["contrat"] = calculate_confidence(result["extracted_data"]["contrat"])
    
    # Extraire le lieu de travail
    result["extracted_data"]["localisation"] = extract_location(job_description)
    result["confidence_scores"]["localisation"] = calculate_confidence(result["extracted_data"]["localisation"])
    
    # Extraire la rémunération proposée
    result["extracted_data"]["remuneration"] = extract_salary(job_description)
    result["confidence_scores"]["remuneration"] = calculate_confidence(result["extracted_data"]["remuneration"])
    
    # Calculer le score de confiance global
    scores = [score for field, score in result["confidence_scores"].items() if field != "global"]
    result["confidence_scores"]["global"] = sum(scores) / len(scores) if scores else 0.0
    
    return result

def extract_job_title(paragraphs, lines):
    """Extrait le titre du poste de la fiche."""
    # Stratégie 1: Première ligne courte qui ne commence pas par des mots courants à éviter
    for i in range(min(5, len(lines))):
        line = lines[i].strip()
        if line and len(line) < 80 and not any(line.lower().startswith(word) for word in ["nous", "notre", "recherch"]):
            return line
    
    # Stratégie 2: Chercher un titre probable dans les premiers paragraphes
    for i in range(min(3, len(paragraphs))):
        paragraph = paragraphs[i].strip()
        if ":" in paragraph:
            parts = paragraph.split(":")
            if any(keyword in parts[0].lower() for keyword in ["poste", "titre", "intitulé"]):
                return parts[1].strip()
    
    # Stratégie 3: Première ligne non vide comme dernier recours
    for line in lines:
        if line.strip():
            return line.strip()
    
    return "Non spécifié"

def extract_experience(text):
    """Extrait les informations d'expérience requise."""
    # Recherche d'un pattern d'années d'expérience
    exp_match = re.search(REGEX_PATTERNS["EXPERIENCE_YEARS"], text, re.IGNORECASE)
    if exp_match:
        return f"{exp_match.group(1)} {exp_match.group(2)}"
    
    # Recherche par mots-clés
    lower_text = text.lower()
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        lower_sentence = sentence.lower()
        if any(keyword in lower_sentence for keyword in JOB_CATEGORIES["EXPERIENCE"]):
            if "junior" in lower_sentence:
                return "Junior"
            if "senior" in lower_sentence:
                return "Senior"
            if "confirmé" in lower_sentence:
                return "Profil confirmé"
            if "débutant" in lower_sentence:
                return "Débutant accepté"
            
            # Si on trouve une phrase avec le mot expérience, on la retourne
            return sentence.strip()
    
    return "Non spécifié"

def extract_skills(text):
    """Extrait les compétences techniques mentionnées."""
    skills = []
    lower_text = text.lower()
    
    # Liste de technologies et langages couramment recherchés
    tech_keywords = [
        'java', 'python', 'javascript', 'js', 'typescript', 'ts', 'c#', 'c++', 'ruby', 'php', 'swift', 'kotlin',
        'react', 'angular', 'vue', 'node', 'express', 'django', 'flask', 'spring', 'asp.net', 'laravel', 'symfony',
        'sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'nosql', 'redis', 'elasticsearch',
        'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'devops', 'ci/cd', 'jenkins', 'git',
        'html', 'css', 'sass', 'less', 'bootstrap', 'tailwind',
        'agile', 'scrum', 'kanban', 'jira', 'confluence',
        'machine learning', 'ml', 'ai', 'deep learning', 'nlp', 'data science',
        'linux', 'unix', 'windows', 'macos',
        'rest', 'graphql', 'api', 'soap', 'microservices'
    ]
    
    # Rechercher les technologies dans le texte
    for keyword in tech_keywords:
        # Recherche avec délimiteurs de mots pour éviter les faux positifs
        pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(pattern, lower_text, re.IGNORECASE):
            skills.append(keyword)
    
    # Rechercher des listes de compétences dans le texte
    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences:
        lower_sentence = sentence.lower()
        if any(keyword in lower_sentence for keyword in JOB_CATEGORIES["SKILLS"]):
            # Si on trouve une liste avec des puces ou des virgules
            list_items = re.findall(r'[•\-*]\s*([^•\-*\n]+)', sentence) or []
            for item in list_items:
                clean_item = item.strip()
                if clean_item and clean_item not in skills:
                    skills.append(clean_item)
            
            # Ajouter les éléments séparés par des virgules
            if ',' in sentence:
                parts = sentence.split(',')
                for part in parts:
                    clean_part = part.strip()
                    if clean_part and clean_part not in skills and len(clean_part) < 30:
                        skills.append(clean_part)
    
    return list(set(skills))  # Dédupliquer

def extract_education(text):
    """Extrait les informations de formation/éducation requise."""
    lower_text = text.lower()
    
    # Recherche de pattern Bac+X
    educ_match = re.search(REGEX_PATTERNS["EDUCATION_LEVEL"], text, re.IGNORECASE)
    if educ_match:
        return f"Bac+{educ_match.group(1)}"
    
    # Recherche par mots-clés
    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences:
        lower_sentence = sentence.lower()
        if any(keyword in lower_sentence for keyword in JOB_CATEGORIES["EDUCATION"]):
            if "ingénieur" in lower_sentence:
                return "École d'ingénieur"
            if "master" in lower_sentence:
                return "Master"
            if "licence" in lower_sentence:
                return "Licence"
            if "bts" in lower_sentence:
                return "BTS"
            if "dut" in lower_sentence:
                return "DUT"
            
            # Si on trouve une phrase avec le mot formation, on la retourne
            return sentence.strip()
    
    return "Non spécifié"

def extract_contract(text):
    """Extrait le type de contrat proposé."""
    lower_text = text.lower()
    
    # Recherche d'un pattern de type de contrat
    contract_match = re.search(REGEX_PATTERNS["CONTRACT_TYPE"], text, re.IGNORECASE)
    if contract_match:
        contract = contract_match.group(0).upper()
        
        # Vérifier télétravail
        remote_match = re.search(REGEX_PATTERNS["REMOTE_WORK"], text, re.IGNORECASE)
        if remote_match:
            return f"{contract} - {remote_match.group(0)}"
        
        return contract
    
    # Recherche par mots-clés
    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences:
        lower_sentence = sentence.lower()
        if any(keyword in lower_sentence for keyword in JOB_CATEGORIES["CONTRACT"]):
            return sentence.strip()
    
    return "Non spécifié"

def extract_location(text):
    """Extrait la localisation du poste."""
    lower_text = text.lower()
    
    # Recherche par mots-clés
    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences:
        lower_sentence = sentence.lower()
        if any(keyword in lower_sentence for keyword in JOB_CATEGORIES["LOCATION"]):
            # Recherche télétravail
            remote_match = re.search(REGEX_PATTERNS["REMOTE_WORK"], lower_sentence, re.IGNORECASE)
            if remote_match:
                return remote_match.group(0)
            
            # Sinon retourner la phrase entière
            return sentence.strip()
    
    return "Non spécifié"

def extract_salary(text):
    """Extrait les informations de salaire proposé."""
    lower_text = text.lower()
    
    # Recherche d'un pattern de fourchette de salaire
    salary_match = re.search(REGEX_PATTERNS["SALARY_RANGE"], text, re.IGNORECASE)
    if salary_match:
        return f"{salary_match.group(1)} - {salary_match.group(2)}"
    
    # Recherche par mots-clés
    sentences = re.split(r'[.!?]+', text)
    for sentence in sentences:
        lower_sentence = sentence.lower()
        if any(keyword in lower_sentence for keyword in JOB_CATEGORIES["SALARY"]):
            # Rechercher tout pattern qui ressemble à un salaire
            keuros_pattern = r'\d+\s*[k€KE]'
            matches = re.findall(keuros_pattern, lower_sentence, re.IGNORECASE)
            if matches:
                if len(matches) >= 2:
                    return f"{matches[0]} - {matches[1]}"
                else:
                    return matches[0]
            
            # Sinon retourner la phrase entière
            return sentence.strip()
    
    return "Non spécifié"

def calculate_confidence(value):
    """Calcule le niveau de confiance pour un champ extrait."""
    if not value or value.strip() == "" or value == "Non spécifié":
        return 0.0
    if len(value) < 5:
        return 0.3
    if len(value) < 15:
        return 0.6
    return 0.8