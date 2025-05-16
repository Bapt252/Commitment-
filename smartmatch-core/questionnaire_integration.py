# -*- coding: utf-8 -*-
"""
Module d'intégration entre les questionnaires web et l'algorithme SmartMatch
------------------------------------------------------------------
Ce module fournit des fonctions pour transformer les données des 
questionnaires HTML (candidat et client) en format compatible avec
l'algorithme SmartMatch, permettant une intégration complète.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======================================================================
# Fonctions utilitaires pour l'extraction et le traitement des données
# ======================================================================

def parse_salary_range(salary_text: str) -> int:
    """
    Extrait une valeur numérique à partir d'une chaîne de texte contenant une fourchette de salaire
    
    Args:
        salary_text: Texte représentant une fourchette salariale (ex: "35K€ - 45K€")
        
    Returns:
        La moyenne de la fourchette salariale, ou 0 si impossible à extraire
    """
    try:
        # Supprimer tous les caractères sauf les chiffres, K, k, € et -
        clean_text = re.sub(r'[^0-9Kk€\-]', '', salary_text)
        
        # Trouver toutes les valeurs numériques
        numbers = re.findall(r'\d+[Kk]?', clean_text)
        
        if not numbers:
            return 0
        
        # Convertir les valeurs en nombres
        values = []
        for num in numbers:
            if 'k' in num.lower():
                # Convertir les valeurs en K en milliers
                value = int(num.lower().replace('k', '')) * 1000
            else:
                value = int(num)
                # Si le nombre est petit, c'est probablement en milliers
                if value < 1000:
                    value *= 1000
            values.append(value)
        
        # Retourner la moyenne si plusieurs valeurs, sinon la valeur unique
        if len(values) > 1:
            return sum(values) // len(values)
        elif values:
            return values[0]
        else:
            return 0
    except Exception as e:
        logger.error(f"Erreur lors du parsing de la fourchette salariale '{salary_text}': {str(e)}")
        return 0

def extract_location_coordinates(questionnaire_data: Dict[str, Any]) -> str:
    """
    Extrait les coordonnées de localisation du questionnaire
    
    Args:
        questionnaire_data: Données du questionnaire
        
    Returns:
        Chaîne au format "latitude,longitude" ou chaîne vide si non disponible
    """
    lat = questionnaire_data.get('address-lat', '')
    lng = questionnaire_data.get('address-lng', '')
    
    if lat and lng:
        return f"{lat},{lng}"
    
    # Chercher dans un autre format possible
    lat = questionnaire_data.get('address_lat', '')
    lng = questionnaire_data.get('address_lng', '')
    
    if lat and lng:
        return f"{lat},{lng}"
    
    return ""

def get_primary_industry(questionnaire_data: Dict[str, Any]) -> str:
    """
    Détermine le secteur d'activité principal à partir des données du questionnaire
    
    Args:
        questionnaire_data: Données du questionnaire
        
    Returns:
        Le secteur d'activité principal ou chaîne vide si non disponible
    """
    # Vérifier si un secteur préféré est spécifié
    has_preference = questionnaire_data.get('has-sector-preference', 'no')
    
    if has_preference == 'yes':
        # Récupérer les secteurs sélectionnés
        sectors = questionnaire_data.get('sector-preference', [])
        if isinstance(sectors, list) and sectors:
            return sectors[0]  # Retourner le premier secteur
        elif isinstance(sectors, str):
            return sectors
    
    return ""

def get_alternative_industries(questionnaire_data: Dict[str, Any]) -> List[str]:
    """
    Récupère les secteurs d'activité alternatifs à partir des données du questionnaire
    
    Args:
        questionnaire_data: Données du questionnaire
        
    Returns:
        Liste des secteurs d'activité alternatifs
    """
    # Vérifier si un secteur préféré est spécifié
    has_preference = questionnaire_data.get('has-sector-preference', 'no')
    
    if has_preference == 'yes':
        # Récupérer les secteurs sélectionnés
        sectors = questionnaire_data.get('sector-preference', [])
        if isinstance(sectors, list) and len(sectors) > 1:
            return sectors[1:]  # Retourner tous les secteurs sauf le premier
        
    return []

def get_experience_years(questionnaire_data: Dict[str, Any]) -> int:
    """
    Estime le nombre d'années d'expérience à partir des données du questionnaire
    
    Args:
        questionnaire_data: Données du questionnaire
        
    Returns:
        Nombre estimé d'années d'expérience
    """
    # Cette fonction dépend de la structure du questionnaire
    # Nous devons estimer une valeur numérique à partir d'une sélection
    
    # Si l'information n'est pas disponible dans le questionnaire, 
    # nous pouvons essayer de l'extraire du CV via des champs cachés
    years = questionnaire_data.get('years_of_experience', 0)
    if years and isinstance(years, (int, float)):
        return int(years)
    
    return 0

def map_education_level(questionnaire_data: Dict[str, Any]) -> str:
    """
    Mappe le niveau d'éducation du questionnaire au format utilisé par SmartMatch
    
    Args:
        questionnaire_data: Données du questionnaire
        
    Returns:
        Niveau d'éducation au format SmartMatch (none, high_school, associate, bachelor, master, phd)
    """
    # Cette fonction dépend de la structure du questionnaire
    # Si l'information n'est pas disponible dans le questionnaire, 
    # nous pouvons essayer de l'extraire du CV via des champs cachés
    
    # Valeurs par défaut pour SmartMatch
    education_map = {
        "bac": "high_school",
        "bac+2": "associate",
        "bac+3": "bachelor",
        "licence": "bachelor",
        "bac+5": "master",
        "master": "master",
        "doctorat": "phd",
        "phd": "phd"
    }
    
    education = questionnaire_data.get('education_level', '').lower()
    
    return education_map.get(education, "bachelor")  # Par défaut, supposer un niveau licence

def get_transport_preferences(questionnaire_data: Dict[str, Any]) -> Dict[str, int]:
    """
    Extrait les préférences de transport et les temps de trajet maximaux
    
    Args:
        questionnaire_data: Données du questionnaire
        
    Returns:
        Dictionnaire associant chaque mode de transport à un temps maximum en minutes
    """
    transport_prefs = {}
    
    # Récupérer les modes de transport sélectionnés
    transport_methods = questionnaire_data.get('transport-method', [])
    if not isinstance(transport_methods, list):
        transport_methods = [transport_methods]
    
    # Pour chaque mode, récupérer le temps maximal
    for method in transport_methods:
        time_key = f'commute-time-{method}'
        max_time = questionnaire_data.get(time_key, 30)  # 30 minutes par défaut
        
        try:
            transport_prefs[method] = int(max_time)
        except (ValueError, TypeError):
            transport_prefs[method] = 30  # Valeur par défaut
    
    return transport_prefs

def extract_skills(skills_text: str) -> List[str]:
    """
    Extrait une liste de compétences à partir d'un texte
    
    Args:
        skills_text: Texte contenant des compétences
        
    Returns:
        Liste des compétences extraites
    """
    # Si le texte est déjà une liste, le retourner directement
    if isinstance(skills_text, list):
        return skills_text
    
    # Si le texte est "Non spécifié" ou vide, retourner une liste vide
    if not skills_text or skills_text.strip() == "Non spécifié":
        return []
    
    # Essayer de séparer les compétences (virgules, points-virgules, retours à la ligne)
    skills = re.split(r'[,;\n\r]+', skills_text)
    
    # Nettoyer les compétences
    cleaned_skills = []
    for skill in skills:
        # Supprimer les espaces et les tags HTML
        cleaned = re.sub(r'<[^>]+>', '', skill).strip()
        if cleaned and cleaned not in cleaned_skills:
            cleaned_skills.append(cleaned)
    
    return cleaned_skills

def get_job_location(questionnaire_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
    """
    Récupère la localisation du poste à partir des données du questionnaire et de la fiche de poste
    
    Args:
        questionnaire_data: Données du questionnaire
        job_data: Données de la fiche de poste
        
    Returns:
        Localisation du poste au format SmartMatch
    """
    # Essayer d'abord de récupérer depuis la fiche de poste
    job_location = job_data.get('job-location-value', '')
    
    # Si non disponible, utiliser l'adresse de l'entreprise
    if not job_location or job_location == "Non spécifié":
        # Essayer d'utiliser les coordonnées si disponibles
        location = extract_location_coordinates(questionnaire_data)
        if location:
            return location
        
        # Sinon utiliser l'adresse textuelle
        return questionnaire_data.get('company-address', '')
    
    return job_location

def is_remote_offered(job_data: Dict[str, Any]) -> bool:
    """
    Détermine si le travail à distance est proposé pour ce poste
    
    Args:
        job_data: Données de la fiche de poste
        
    Returns:
        True si le travail à distance est proposé, False sinon
    """
    # Analyser la description ou les avantages pour détecter la mention du télétravail
    benefits = job_data.get('job-benefits-value', '').lower()
    responsibilities = job_data.get('job-responsibilities-value', '').lower()
    contract = job_data.get('job-contract-value', '').lower()
    
    # Vérifier les mots-clés dans les différents champs
    remote_keywords = ["télétravail", "remote", "à distance", "home office", "travail à domicile"]
    
    for field in [benefits, responsibilities, contract]:
        for keyword in remote_keywords:
            if keyword in field:
                return True
    
    return False

def parse_min_salary(salary_text: str) -> int:
    """
    Extrait le salaire minimum d'une fourchette salariale
    
    Args:
        salary_text: Texte représentant une fourchette salariale
        
    Returns:
        Salaire minimum extrait ou 0 si impossible à extraire
    """
    try:
        # Nettoyer le texte
        clean_text = re.sub(r'[^0-9Kk€\-]', '', salary_text)
        
        # Trouver toutes les valeurs numériques
        numbers = re.findall(r'\d+[Kk]?', clean_text)
        
        if not numbers:
            return 0
        
        # Convertir la première valeur en nombre
        num = numbers[0]
        if 'k' in num.lower():
            value = int(num.lower().replace('k', '')) * 1000
        else:
            value = int(num)
            # Si le nombre est petit, c'est probablement en milliers
            if value < 1000:
                value *= 1000
        
        return value
    except Exception as e:
        logger.error(f"Erreur lors du parsing du salaire minimum '{salary_text}': {str(e)}")
        return 0

def parse_max_salary(salary_text: str) -> int:
    """
    Extrait le salaire maximum d'une fourchette salariale
    
    Args:
        salary_text: Texte représentant une fourchette salariale
        
    Returns:
        Salaire maximum extrait ou 0 si impossible à extraire
    """
    try:
        # Nettoyer le texte
        clean_text = re.sub(r'[^0-9Kk€\-]', '', salary_text)
        
        # Trouver toutes les valeurs numériques
        numbers = re.findall(r'\d+[Kk]?', clean_text)
        
        if not numbers:
            return 0
        
        # Si une seule valeur, la retourner (même min et max)
        if len(numbers) == 1:
            num = numbers[0]
            if 'k' in num.lower():
                return int(num.lower().replace('k', '')) * 1000
            else:
                value = int(num)
                # Si le nombre est petit, c'est probablement en milliers
                if value < 1000:
                    value *= 1000
                return value
        
        # Sinon, prendre la dernière valeur comme maximum
        num = numbers[-1]
        if 'k' in num.lower():
            value = int(num.lower().replace('k', '')) * 1000
        else:
            value = int(num)
            # Si le nombre est petit, c'est probablement en milliers
            if value < 1000:
                value *= 1000
        
        return value
    except Exception as e:
        logger.error(f"Erreur lors du parsing du salaire maximum '{salary_text}': {str(e)}")
        return 0

def get_min_experience(questionnaire_data: Dict[str, Any], job_data: Dict[str, Any]) -> int:
    """
    Détermine l'expérience minimale requise pour le poste
    
    Args:
        questionnaire_data: Données du questionnaire
        job_data: Données de la fiche de poste
        
    Returns:
        Nombre minimal d'années d'expérience requises
    """
    # Récupérer l'expérience depuis la fiche de poste
    experience_text = job_data.get('job-experience-value', '')
    if experience_text and experience_text != "Non spécifié":
        # Essayer d'extraire les années
        years = re.findall(r'\d+', experience_text)
        if years:
            return int(years[0])  # Retourner la première valeur numérique
    
    # Sinon, utiliser la sélection du questionnaire
    experience_required = questionnaire_data.get('experience-required', '')
    
    # Mapper les valeurs du questionnaire à des nombres d'années
    experience_map = {
        "junior": 0,
        "2-3": 2,
        "5-10": 5,
        "10plus": 10
    }
    
    return experience_map.get(experience_required, 0)

def get_max_experience(questionnaire_data: Dict[str, Any], job_data: Dict[str, Any]) -> int:
    """
    Détermine l'expérience maximale attendue pour le poste
    
    Args:
        questionnaire_data: Données du questionnaire
        job_data: Données de la fiche de poste
        
    Returns:
        Nombre maximal d'années d'expérience attendues (ou 100 si non spécifié)
    """
    # Récupérer l'expérience depuis la fiche de poste
    experience_text = job_data.get('job-experience-value', '')
    if experience_text and experience_text != "Non spécifié":
        # Essayer d'extraire plusieurs années
        years = re.findall(r'\d+', experience_text)
        if len(years) > 1:
            return int(years[1])  # Retourner la deuxième valeur numérique
    
    # Sinon, utiliser la sélection du questionnaire
    experience_required = questionnaire_data.get('experience-required', '')
    
    # Mapper les valeurs du questionnaire à des nombres d'années
    experience_map = {
        "junior": 2,
        "2-3": 3,
        "5-10": 10,
        "10plus": 100  # Pas de limite supérieure
    }
    
    return experience_map.get(experience_required, 100)

def map_job_education(education_text: str) -> str:
    """
    Mappe le niveau d'éducation de la fiche de poste au format utilisé par SmartMatch
    
    Args:
        education_text: Texte décrivant le niveau d'éducation requis
        
    Returns:
        Niveau d'éducation au format SmartMatch
    """
    education_text = education_text.lower() if education_text else ""
    
    # Mapper les mots-clés courants aux niveaux d'éducation
    if "doctorat" in education_text or "phd" in education_text or "docteur" in education_text:
        return "phd"
    elif "master" in education_text or "bac+5" in education_text or "bac +5" in education_text:
        return "master"
    elif "licence" in education_text or "bachelor" in education_text or "bac+3" in education_text:
        return "bachelor"
    elif "bts" in education_text or "dut" in education_text or "bac+2" in education_text:
        return "associate"
    elif "bac" in education_text or "high school" in education_text:
        return "high_school"
    else:
        return "none"

def get_contract_type(job_data: Dict[str, Any]) -> str:
    """
    Détermine le type de contrat à partir des données de la fiche de poste
    
    Args:
        job_data: Données de la fiche de poste
        
    Returns:
        Type de contrat au format SmartMatch (full_time, part_time, contract, internship)
    """
    contract_text = job_data.get('job-contract-value', '').lower()
    
    # Mapper les mots-clés courants aux types de contrat
    if "cdi" in contract_text or "permanent" in contract_text:
        return "full_time"
    elif "cdd" in contract_text or "durée déterminée" in contract_text:
        return "contract"
    elif "temps partiel" in contract_text or "part time" in contract_text:
        return "part_time"
    elif "stage" in contract_text or "internship" in contract_text:
        return "internship"
    elif "freelance" in contract_text or "indépendant" in contract_text:
        return "freelance"
    else:
        return "full_time"  # Par défaut

# ======================================================================
# Fonctions principales de transformation des données des questionnaires
# ======================================================================

def transform_candidate_questionnaire_to_smartmatch(questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convertit les données du questionnaire candidat au format compatible SmartMatch
    
    Args:
        questionnaire_data: Données du questionnaire candidat
        
    Returns:
        Dictionnaire au format compatible SmartMatch
    """
    # Récupérer les données de base
    candidate = {
        "id": questionnaire_data.get("id", "unknown"),
        "name": questionnaire_data.get("full-name", ""),
        "job_title": questionnaire_data.get("job-title", ""),
        
        # Localisation
        "location": extract_location_coordinates(questionnaire_data),
        
        # Préférences de travail
        "remote_work": questionnaire_data.get("remote-preference") in ["full", "hybrid"],
        "salary_expectation": parse_salary_range(questionnaire_data.get("salary-range", "")),
        
        # Secteurs d'intérêt
        "industry": get_primary_industry(questionnaire_data),
        "alternative_industries": get_alternative_industries(questionnaire_data),
        
        # Données de base (à extraire du CV si disponible)
        "years_of_experience": get_experience_years(questionnaire_data),
        "education_level": map_education_level(questionnaire_data),
        
        # Préférences supplémentaires pour SmartMatch étendu
        "office_preference": questionnaire_data.get("office-preference", ""),
        "motivation_priorities": questionnaire_data.get("motivation-order", "").split(","),
        "availability": questionnaire_data.get("availability", ""),
        "transport_preferences": get_transport_preferences(questionnaire_data),
        "structure_preference": questionnaire_data.get("structure-type", []),
        
        # Informations sur le statut actuel (pour les insights)
        "currently_employed": questionnaire_data.get("currently-employed", "no") == "yes"
    }
    
    return candidate

def transform_client_questionnaire_to_smartmatch(
    questionnaire_data: Dict[str, Any], 
    job_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convertit les données du questionnaire client et la fiche de poste au format compatible SmartMatch
    
    Args:
        questionnaire_data: Données du questionnaire client
        job_data: Données extraites de la fiche de poste
        
    Returns:
        Dictionnaire au format compatible SmartMatch
    """
    job = {
        "id": job_data.get("id", "unknown"),
        "title": job_data.get("job-title-value", ""),
        
        # Compétences extraites de la fiche de poste
        "required_skills": extract_skills(job_data.get("job-skills-value", "")),
        "preferred_skills": [],  # À extraire si différenciées
        
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
        
        # Données supplémentaires pour SmartMatch étendu
        "job_type": get_contract_type(job_data),
        "industry": questionnaire_data.get("sector-list", ""),
        "work_environment": questionnaire_data.get("work-environment", ""),
        "recruitment_delay": questionnaire_data.get("recruitment-delay", []),
        "sector_knowledge_required": questionnaire_data.get("sector-knowledge", "no") == "yes",
        "can_handle_notice": questionnaire_data.get("can-handle-notice", "no") == "yes",
        "notice_duration": questionnaire_data.get("notice-duration", ""),
        
        # Informations détaillées sur le poste (pour les insights)
        "team_composition": questionnaire_data.get("team-composition", ""),
        "evolution_perspectives": questionnaire_data.get("evolution-perspectives", ""),
        "benefits": questionnaire_data.get("benefits", ""),
        "recruitment_context": questionnaire_data.get("recruitment-context", "")
    }
    
    # Traitement spécial pour préparer les responsabilités et avantages
    responsibilities = job_data.get("job-responsibilities-value", "")
    if responsibilities and responsibilities != "Non spécifié":
        job["responsibilities"] = responsibilities
    
    benefits = job_data.get("job-benefits-value", "")
    if benefits and benefits != "Non spécifié":
        job["benefits_description"] = benefits
    
    return job

# ======================================================================
# Fonction d'extension de l'API SmartMatch pour l'intégration des questionnaires
# ======================================================================

def process_questionnaires(candidate_data, job_data, client_data):
    """
    Traite les données des questionnaires pour le matching SmartMatch
    
    Args:
        candidate_data: Données brutes du questionnaire candidat
        job_data: Données brutes de la fiche de poste
        client_data: Données brutes du questionnaire client
        
    Returns:
        Tuple (candidate, job) au format SmartMatch
    """
    try:
        # Transformer les données du candidat
        candidate = transform_candidate_questionnaire_to_smartmatch(candidate_data)
        
        # Transformer les données du poste
        job = transform_client_questionnaire_to_smartmatch(client_data, job_data)
        
        # Si des skills sont présentes dans le profil candidat, les utiliser
        if "skills" in candidate_data and candidate_data["skills"]:
            candidate["skills"] = candidate_data["skills"]
        
        # S'assurer que les skills sont au bon format
        if "skills" not in candidate:
            candidate["skills"] = []  # Valeur par défaut si non disponible
        
        return candidate, job
    except Exception as e:
        logger.error(f"Erreur lors du traitement des questionnaires: {str(e)}")
        # Retourner des structures minimales pour éviter les erreurs
        return {"id": "unknown", "skills": []}, {"id": "unknown", "required_skills": []}

# ======================================================================
# Tests unitaires et exemples d'utilisation
# ======================================================================

def test_salary_parsing():
    """
    Teste la fonction de parsing des salaires
    """
    test_cases = [
        ("35K€ - 45K€", 40000),
        ("35 000 € - 45 000 €", 40000),
        ("35000-45000", 40000),
        ("35K", 35000),
        ("35000€ annuel brut", 35000),
        ("Salaire: 35K à 45K", 40000)
    ]
    
    for text, expected in test_cases:
        result = parse_salary_range(text)
        print(f"Text: '{text}' -> {result} (expected {expected})")
        assert abs(result - expected) < 1000, f"Expected {expected}, got {result}"

def example_candidate_transformation():
    """
    Exemple de transformation des données d'un candidat
    """
    # Exemple de données de questionnaire
    candidate_data = {
        "full-name": "Jean Dupont",
        "job-title": "Développeur Full Stack",
        "address-lat": "48.8566",
        "address-lng": "2.3522",
        "office-preference": "open-space",
        "transport-method": ["public-transport", "bike"],
        "commute-time-public-transport": "45",
        "commute-time-bike": "30",
        "salary-range": "45K€ - 55K€",
        "has-sector-preference": "yes",
        "sector-preference": ["tech", "consulting"],
        "motivation-order": "evolution,remuneration,flexibility,location,other",
        "availability": "1month",
        "currently-employed": "yes",
        "skills": ["JavaScript", "React", "Node.js", "Python", "Django"]
    }
    
    # Transformer les données
    smart_candidate = transform_candidate_questionnaire_to_smartmatch(candidate_data)
    
    # Afficher le résultat
    print(json.dumps(smart_candidate, indent=2))

def example_job_transformation():
    """
    Exemple de transformation des données d'un poste
    """
    # Exemple de données de questionnaire client
    client_data = {
        "company-name": "TechStartup SAS",
        "company-address": "123 Avenue de la République, 75011 Paris",
        "sector-list": "tech",
        "work-environment": "open-space",
        "experience-required": "5-10",
        "sector-knowledge": "no",
        "can-handle-notice": "yes",
        "notice-duration": "2months"
    }
    
    # Exemple de données de fiche de poste
    job_data = {
        "job-title-value": "Développeur Full Stack JavaScript",
        "job-contract-value": "CDI",
        "job-location-value": "Paris",
        "job-experience-value": "Au moins 3 ans d'expérience",
        "job-education-value": "Bac+5 ou équivalent",
        "job-salary-value": "Entre 50K€ et 65K€ selon expérience",
        "job-skills-value": "React, Node.js, Express, MongoDB, TypeScript, Git",
        "job-responsibilities-value": "Développer de nouvelles fonctionnalités, Travailler en équipe agile, Possibilité de télétravail 2 jours par semaine",
        "job-benefits-value": "Tickets restaurant, Mutuelle, RTT, Télétravail partiel"
    }
    
    # Transformer les données
    smart_job = transform_client_questionnaire_to_smartmatch(client_data, job_data)
    
    # Afficher le résultat
    print(json.dumps(smart_job, indent=2))

# Point d'entrée pour les tests
if __name__ == "__main__":
    print("\n=== Test de parsing des salaires ===\n")
    test_salary_parsing()
    
    print("\n=== Exemple de transformation des données d'un candidat ===\n")
    example_candidate_transformation()
    
    print("\n=== Exemple de transformation des données d'un poste ===\n")
    example_job_transformation()