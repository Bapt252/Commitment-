"""
Module d'intégration des questionnaires candidat et client pour SmartMatch
---------------------------------------------------------------------
Ce module fournit les fonctions nécessaires pour transformer les données
des questionnaires HTML en structures de données compatibles avec SmartMatch.
"""

import re
import json
from typing import Dict, List, Any, Optional, Union

# Fonctions utilitaires d'extraction et de conversion

def parse_salary_range(salary_str: str) -> int:
    """
    Extrait un montant salarial moyen à partir d'une chaîne de fourchette salariale
    
    Args:
        salary_str: Chaîne contenant la fourchette salariale (ex: "35K€ - 45K€ brut annuel")
        
    Returns:
        int: Montant moyen en euros (ex: 40000)
    """
    # Extraire tous les nombres
    numbers = re.findall(r'\d+', salary_str)
    numbers = [int(n) for n in numbers]
    
    if not numbers:
        return 0
    
    # Vérifier si les valeurs sont en milliers (K)
    if 'K' in salary_str or 'k' in salary_str:
        numbers = [n * 1000 if n < 1000 else n for n in numbers]
    
    # Calculer la moyenne si c'est une fourchette
    if len(numbers) >= 2:
        return sum(numbers[:2]) // 2
    elif len(numbers) == 1:
        return numbers[0]
    
    return 0

def parse_min_salary(salary_str: str) -> int:
    """
    Extrait le montant salarial minimum à partir d'une chaîne de fourchette salariale
    
    Args:
        salary_str: Chaîne contenant la fourchette salariale (ex: "35K€ - 45K€ brut annuel")
        
    Returns:
        int: Montant minimum en euros (ex: 35000)
    """
    # Extraire tous les nombres
    numbers = re.findall(r'\d+', salary_str)
    numbers = [int(n) for n in numbers if n]
    
    if not numbers:
        return 0
    
    # Vérifier si les valeurs sont en milliers (K)
    if 'K' in salary_str or 'k' in salary_str:
        numbers = [n * 1000 if n < 1000 else n for n in numbers]
    
    # Retourner la valeur minimale
    return min(numbers)

def parse_max_salary(salary_str: str) -> int:
    """
    Extrait le montant salarial maximum à partir d'une chaîne de fourchette salariale
    
    Args:
        salary_str: Chaîne contenant la fourchette salariale (ex: "35K€ - 45K€ brut annuel")
        
    Returns:
        int: Montant maximum en euros (ex: 45000)
    """
    # Extraire tous les nombres
    numbers = re.findall(r'\d+', salary_str)
    numbers = [int(n) for n in numbers if n]
    
    if not numbers:
        return 0
    
    # Vérifier si les valeurs sont en milliers (K)
    if 'K' in salary_str or 'k' in salary_str:
        numbers = [n * 1000 if n < 1000 else n for n in numbers]
    
    # Retourner la valeur maximale
    return max(numbers)

def extract_skills(skills_html: str) -> List[str]:
    """
    Extrait les compétences à partir du HTML des compétences du job parser
    
    Args:
        skills_html: Chaîne HTML contenant les compétences sous forme de tags
        
    Returns:
        List[str]: Liste des compétences extraites
    """
    # Supprimer les balises HTML et extraire les compétences
    # Exemple de format: <div class="tag">Python</div><div class="tag">Django</div>
    skills = re.findall(r'<div class="tag">(.*?)</div>', skills_html)
    
    # Si aucune balise trouvée, essayer de diviser la chaîne par virgule ou espace
    if not skills and skills_html and skills_html != "Non spécifié":
        skills = [s.strip() for s in re.split(r'[,;]\s*', skills_html) if s.strip()]
    
    return skills

def get_experience_years(questionnaire_data: Dict[str, Any]) -> int:
    """
    Détermine le nombre d'années d'expérience à partir des données du questionnaire
    
    Args:
        questionnaire_data: Données du questionnaire candidat
        
    Returns:
        int: Nombre d'années d'expérience estimé
    """
    # Cette fonction serait à adapter en fonction de la structure exacte du questionnaire
    # Comme le questionnaire candidat ne contient pas directement cette information,
    # on pourrait la récupérer du CV ou définir une valeur par défaut
    return 0

def get_primary_industry(questionnaire_data: Dict[str, Any]) -> str:
    """
    Extrait le secteur d'activité principal à partir des données du questionnaire
    
    Args:
        questionnaire_data: Données du questionnaire candidat
        
    Returns:
        str: Secteur d'activité principal
    """
    # Vérifier si le candidat a une préférence pour un secteur
    if questionnaire_data.get("has-sector-preference") == "yes":
        # Récupérer le premier secteur de la liste (si format tableau)
        sectors = questionnaire_data.get("sector-preference", [])
        if isinstance(sectors, list) and sectors:
            return sectors[0]
        elif isinstance(sectors, str):
            return sectors
    
    return ""

def get_alternative_industries(questionnaire_data: Dict[str, Any]) -> List[str]:
    """
    Extrait les secteurs d'activité alternatifs à partir des données du questionnaire
    
    Args:
        questionnaire_data: Données du questionnaire candidat
        
    Returns:
        List[str]: Liste des secteurs d'activité alternatifs
    """
    # Vérifier si le candidat a une préférence pour un secteur
    if questionnaire_data.get("has-sector-preference") == "yes":
        # Récupérer tous les secteurs sauf le premier (déjà considéré comme principal)
        sectors = questionnaire_data.get("sector-preference", [])
        if isinstance(sectors, list) and len(sectors) > 1:
            return sectors[1:]
    
    return []

def map_education_level(questionnaire_data: Dict[str, Any]) -> str:
    """
    Mappe le niveau d'éducation du questionnaire au format attendu par SmartMatch
    
    Args:
        questionnaire_data: Données du questionnaire candidat
        
    Returns:
        str: Niveau d'éducation au format SmartMatch (none, high_school, associate, bachelor, master, phd)
    """
    # Cette fonction serait à adapter en fonction de la structure exacte du questionnaire
    # Comme le questionnaire candidat ne contient pas directement cette information,
    # on pourrait la récupérer du CV ou définir une valeur par défaut
    return "bachelor"

def get_transport_preferences(questionnaire_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Extrait les préférences de transport et les temps de trajet maximum
    
    Args:
        questionnaire_data: Données du questionnaire candidat
        
    Returns:
        Dict[str, int]: Dictionnaire des modes de transport avec temps maximum en minutes
    """
    preferences = {}
    
    # Récupérer les modes de transport cochés
    transport_methods = questionnaire_data.get("transport-method", [])
    if not isinstance(transport_methods, list):
        transport_methods = [transport_methods]
    
    # Pour chaque mode de transport, récupérer le temps de trajet maximum
    for method in transport_methods:
        time_key = f"commute-time-{method}"
        if time_key in questionnaire_data:
            try:
                time_value = int(questionnaire_data[time_key])
                preferences[method] = time_value
            except (ValueError, TypeError):
                pass
    
    return preferences

def get_job_location(questionnaire_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
    """
    Extrait la localisation du poste à partir des données du questionnaire et des données de job
    
    Args:
        questionnaire_data: Données du questionnaire client
        job_data: Données de la fiche de poste
        
    Returns:
        str: Localisation au format "latitude,longitude" ou texte
    """
    # Essayer d'abord de récupérer depuis les coordonnées cachées
    if questionnaire_data.get("address_lat") and questionnaire_data.get("address_lng"):
        return f"{questionnaire_data['address_lat']},{questionnaire_data['address_lng']}"
    
    # Sinon, récupérer depuis l'adresse de l'entreprise
    company_address = questionnaire_data.get("company-address", "")
    if company_address:
        return company_address
    
    # En dernier recours, utiliser la localisation de la fiche de poste
    job_location = job_data.get("job-location-value", "")
    return job_location

def is_remote_offered(job_data: Dict[str, Any]) -> bool:
    """
    Détermine si le travail à distance est offert
    
    Args:
        job_data: Données de la fiche de poste
        
    Returns:
        bool: True si le travail à distance est offert
    """
    # Vérifier si le texte de localisation ou des avantages mentionne le remote
    location = job_data.get("job-location-value", "").lower()
    benefits = job_data.get("job-benefits-value", "").lower()
    
    remote_keywords = ["remote", "télétravail", "à distance", "home office", "distanciel"]
    
    for keyword in remote_keywords:
        if keyword in location or keyword in benefits:
            return True
    
    return False

def get_contract_type(job_data: Dict[str, Any]) -> str:
    """
    Extrait le type de contrat à partir des données de la fiche de poste
    
    Args:
        job_data: Données de la fiche de poste
        
    Returns:
        str: Type de contrat (full_time, part_time, contract, intern, etc.)
    """
    contract = job_data.get("job-contract-value", "").lower()
    
    if "cdi" in contract:
        return "full_time"
    elif "cdd" in contract:
        return "contract"
    elif "stage" in contract or "intern" in contract:
        return "intern"
    elif "freelance" in contract or "indépendant" in contract:
        return "freelance"
    elif "temps partiel" in contract or "part time" in contract:
        return "part_time"
    
    # Par défaut
    return "full_time"

def get_min_experience(questionnaire_data: Dict[str, Any], job_data: Dict[str, Any]) -> int:
    """
    Détermine l'expérience minimale requise
    
    Args:
        questionnaire_data: Données du questionnaire client
        job_data: Données de la fiche de poste
        
    Returns:
        int: Nombre d'années d'expérience minimale
    """
    # Vérifier d'abord dans les données du questionnaire
    experience_required = questionnaire_data.get("experience-required", "")
    
    if experience_required == "junior":
        return 0
    elif experience_required == "2-3":
        return 2
    elif experience_required == "5-10":
        return 5
    elif experience_required == "10plus":
        return 10
    
    # Sinon, essayer d'extraire de la fiche de poste
    experience_text = job_data.get("job-experience-value", "")
    years = re.findall(r'(\d+)\s*(?:an|année|years)', experience_text)
    if years:
        return int(years[0])
    
    return 0

def get_max_experience(questionnaire_data: Dict[str, Any], job_data: Dict[str, Any]) -> int:
    """
    Détermine l'expérience maximale souhaitée
    
    Args:
        questionnaire_data: Données du questionnaire client
        job_data: Données de la fiche de poste
        
    Returns:
        int: Nombre d'années d'expérience maximale
    """
    # Vérifier d'abord dans les données du questionnaire
    experience_required = questionnaire_data.get("experience-required", "")
    
    if experience_required == "junior":
        return 2
    elif experience_required == "2-3":
        return 4
    elif experience_required == "5-10":
        return 10
    elif experience_required == "10plus":
        return 100  # Pas de limite supérieure spécifique
    
    # Sinon, essayer d'extraire de la fiche de poste
    experience_text = job_data.get("job-experience-value", "")
    
    # Chercher un pattern comme "5-10 ans"
    range_pattern = re.search(r'(\d+)\s*-\s*(\d+)\s*(?:an|année|years)', experience_text)
    if range_pattern:
        return int(range_pattern.group(2))
    
    return 100  # Valeur par défaut très élevée

def map_job_education(education_text: str) -> str:
    """
    Mappe le texte du niveau d'éducation au format attendu par SmartMatch
    
    Args:
        education_text: Texte décrivant le niveau d'éducation requis
        
    Returns:
        str: Niveau d'éducation au format SmartMatch (none, high_school, associate, bachelor, master, phd)
    """
    education_text = education_text.lower()
    
    if "bac+5" in education_text or "master" in education_text or "ingénieur" in education_text:
        return "master"
    elif "bac+3" in education_text or "licence" in education_text or "bachelor" in education_text:
        return "bachelor"
    elif "bac+2" in education_text or "dut" in education_text or "bts" in education_text:
        return "associate"
    elif "bac" in education_text or "high school" in education_text:
        return "high_school"
    elif "phd" in education_text or "doctorat" in education_text:
        return "phd"
    
    return "none"

# Fonctions principales de transformation

def transform_candidate_questionnaire_to_smartmatch(questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convertit les données du questionnaire candidat au format compatible SmartMatch
    
    Args:
        questionnaire_data: Données du questionnaire candidat
        
    Returns:
        Dict[str, Any]: Données au format SmartMatch
    """
    # Identifier si les questions sur le transport ont été répondues
    transport_modes = questionnaire_data.get("transport-method", [])
    if not isinstance(transport_modes, list):
        transport_modes = [transport_modes]
    
    # Récupérer les préférences de transport avec temps max
    transport_preferences = get_transport_preferences(questionnaire_data)
    
    # Traiter la liste des motivations
    motivations = questionnaire_data.get("motivation-order", "")
    if motivations and isinstance(motivations, str):
        motivations = motivations.split(",")
    elif not isinstance(motivations, list):
        motivations = []
    
    # Valeur other_motivation
    other_motivation = ""
    if "other" in motivations and motivations.index("other") < 3:
        other_motivation = questionnaire_data.get("other-motivation", "")
    
    # Structure des données candidat
    candidate = {
        "id": questionnaire_data.get("id", f"candidate-{hash(questionnaire_data.get('full-name', 'unknown'))}"),
        "name": questionnaire_data.get("full-name", ""),
        "skills": [],  # À remplir depuis le CV
        "location": "",  # À extraire des coordonnées d'adresse
        
        # Extraire depuis l'adresse si disponible
        "location_coordinates": {
            "lat": questionnaire_data.get("address-lat", ""),
            "lng": questionnaire_data.get("address-lng", ""),
            "place_id": questionnaire_data.get("address-place-id", "")
        },
        
        # Préférences de travail
        "remote_work": questionnaire_data.get("remote-preference", "") in ["full", "hybrid"],
        "salary_expectation": parse_salary_range(questionnaire_data.get("salary-range", "")),
        "job_type": "full_time",  # À déterminer selon le questionnaire
        
        # Secteurs d'intérêt
        "industry": get_primary_industry(questionnaire_data),
        "alternative_industries": get_alternative_industries(questionnaire_data),
        
        # Préférences supplémentaires
        "office_preference": questionnaire_data.get("office-preference", ""),
        "availability": questionnaire_data.get("availability", ""),
        "transport_modes": transport_modes,
        "transport_preferences": transport_preferences,
        "motivation_priorities": motivations,
        "other_motivation": other_motivation,
        
        # Statistiques sur l'emploi actuel
        "currently_employed": questionnaire_data.get("currently-employed", "") == "yes",
        "notice_period": questionnaire_data.get("notice-period", "") if questionnaire_data.get("currently-employed") == "yes" else "",
        "notice_negotiable": questionnaire_data.get("notice-negotiable", "") == "yes" if questionnaire_data.get("currently-employed") == "yes" else False,
        "recruitment_status": questionnaire_data.get("recruitment-status", "")
    }
    
    # Formatage final de la localisation
    if candidate["location_coordinates"]["lat"] and candidate["location_coordinates"]["lng"]:
        candidate["location"] = f"{candidate['location_coordinates']['lat']},{candidate['location_coordinates']['lng']}"
    
    # Valeurs par défaut pour les champs requis par SmartMatch
    if not candidate["skills"]:
        candidate["skills"] = []
    
    if not candidate["years_of_experience"]:
        candidate["years_of_experience"] = 0
    
    if not candidate["education_level"]:
        candidate["education_level"] = "bachelor"
    
    return candidate

def transform_client_questionnaire_to_smartmatch(questionnaire_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convertit les données du questionnaire client et la fiche de poste au format compatible SmartMatch
    
    Args:
        questionnaire_data: Données du questionnaire client
        job_data: Données de la fiche de poste extraites
        
    Returns:
        Dict[str, Any]: Données au format SmartMatch
    """
    # Extraire les compétences depuis la valeur HTML
    skills = extract_skills(job_data.get("job-skills-value", ""))
    
    # Séparer les compétences requises et préférées (si possible)
    # Par défaut, toutes les compétences sont considérées comme requises
    required_skills = skills
    preferred_skills = []
    
    # Structure des données de l'offre d'emploi
    job = {
        "id": job_data.get("id", f"job-{hash(job_data.get('job-title-value', 'unknown'))}"),
        "title": job_data.get("job-title-value", ""),
        
        # Compétences
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        
        # Localisation
        "location": get_job_location(questionnaire_data, job_data),
        
        # Conditions
        "offers_remote": is_remote_offered(job_data),
        "salary_range": {
            "min": parse_min_salary(job_data.get("job-salary-value", "")),
            "max": parse_max_salary(job_data.get("job-salary-value", ""))
        },
        
        # Exigences
        "min_years_of_experience": get_min_experience(questionnaire_data, job_data),
        "max_years_of_experience": get_max_experience(questionnaire_data, job_data),
        "required_education": map_job_education(job_data.get("job-education-value", "")),
        
        # Données supplémentaires
        "job_type": get_contract_type(job_data),
        "industry": questionnaire_data.get("sector-list", ""),
        "work_environment": questionnaire_data.get("work-environment", ""),
        "recruitment_delay": questionnaire_data.get("recruitment-delay", []),
        "can_handle_notice": questionnaire_data.get("can-handle-notice", "") == "yes",
        "notice_duration": questionnaire_data.get("notice-duration", "") if questionnaire_data.get("can-handle-notice") == "yes" else "",
        "recruitment_context": questionnaire_data.get("recruitment-context", ""),
        "sector_knowledge_required": questionnaire_data.get("sector-knowledge", "") == "yes",
        "team_composition": questionnaire_data.get("team-composition", ""),
        "evolution_perspectives": questionnaire_data.get("evolution-perspectives", "")
    }
    
    return job

# Fonction utilitaire pour charger les données depuis le stockage de session
def load_questionnaire_data_from_session(session_storage_key: str) -> Dict[str, Any]:
    """
    Cette fonction simule le chargement des données depuis le stockage de session
    En pratique, cette fonction devrait être implémentée côté client ou serveur
    selon l'architecture de l'application.
    
    Args:
        session_storage_key: Clé du stockage de session
        
    Returns:
        Dict[str, Any]: Données du questionnaire
    """
    # Ceci est une fonction dummy pour simulation
    # En réalité, cette fonction serait implémentée dans le frontend ou backend
    return {}

# Fonction de test/exemple
def example_integration():
    """
    Exemple d'utilisation des fonctions d'intégration
    """
    # Exemple de données de questionnaire candidat
    candidate_data = {
        "full-name": "Jean Dupont",
        "job-title": "Développeur Python",
        "transport-method": ["public-transport", "vehicle"],
        "commute-time-public-transport": "45",
        "commute-time-vehicle": "30",
        "address": "123 Rue de Paris, 75001 Paris",
        "address-lat": "48.8566",
        "address-lng": "2.3522",
        "office-preference": "no-preference",
        "motivation-order": "remuneration,evolution,flexibility,location,other",
        "structure-type": ["startup", "pme"],
        "has-sector-preference": "yes",
        "sector-preference": ["tech", "finance"],
        "salary-range": "40K€ - 50K€ brut annuel",
        "availability": "1month",
        "currently-employed": "yes",
        "listening-reason": "no-evolution",
        "notice-period": "2months",
        "notice-negotiable": "yes",
        "recruitment-status": "in-progress"
    }
    
    # Exemple de données de questionnaire client
    client_data = {
        "company-name": "TechSolutions",
        "company-address": "456 Avenue de la République, 75011 Paris",
        "experience-required": "5-10",
        "sector-knowledge": "yes",
        "sector-list": "tech",
        "work-environment": "openspace",
        "recruitment-delay": ["1month"],
        "can-handle-notice": "yes",
        "notice-duration": "2months"
    }
    
    # Exemple de données de fiche de poste extraites
    job_extracted_data = {
        "job-title-value": "Développeur Python Senior",
        "job-contract-value": "CDI",
        "job-location-value": "Paris, France (Télétravail possible 2j/semaine)",
        "job-experience-value": "5 ans minimum sur des technologies similaires",
        "job-education-value": "Bac+5 ingénieur ou équivalent",
        "job-salary-value": "45K€ - 55K€ selon profil",
        "job-skills-value": "<div class=\"tag\">Python</div><div class=\"tag\">Django</div><div class=\"tag\">PostgreSQL</div><div class=\"tag\">Docker</div>",
        "job-responsibilities-value": "Développement de nouvelles fonctionnalités, maintenance...",
        "job-benefits-value": "Télétravail 2j/semaine, RTT, tickets restaurant"
    }
    
    # Transformation des données
    candidate = transform_candidate_questionnaire_to_smartmatch(candidate_data)
    job = transform_client_questionnaire_to_smartmatch(client_data, job_extracted_data)
    
    # Imprimer les résultats
    print("\n=== Données candidat transformées ===")
    print(json.dumps(candidate, indent=2))
    
    print("\n=== Données job transformées ===")
    print(json.dumps(job, indent=2))
    
    return candidate, job

# Code d'exécution directe
if __name__ == "__main__":
    example_integration()
