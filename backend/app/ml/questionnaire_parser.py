"""
Module pour le parsing et la structuration des données de questionnaire.
Ce module permet d'extraire et de transformer les données des questionnaires frontend
en structure de données utilisable par l'algorithme de matching.
"""

from typing import Dict, Any, List, Union, Optional
import re
import logging
import json

# Configuration du logging
logger = logging.getLogger(__name__)

def parse_candidate_questionnaire(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse et structure les données du questionnaire candidat.
    
    Args:
        raw_data: Données brutes du questionnaire candidat
        
    Returns:
        Données structurées pour l'algorithme de matching
    """
    try:
        structured_data = {}
        
        # 1. Environnement de travail préféré
        if "work_environment" in raw_data:
            structured_data["environment_preference"] = map_environment_value(raw_data["work_environment"])
        
        # 2. Mode de travail préféré
        if "work_mode" in raw_data:
            structured_data["work_mode_preference"] = map_work_mode_value(raw_data["work_mode"])
        
        # 3. Taille d'équipe préférée
        if "team_size" in raw_data:
            structured_data["team_size_preference"] = map_team_size_value(raw_data["team_size"])
        
        # 4. Valeurs importantes
        if "values" in raw_data:
            structured_data["values_important"] = extract_values(raw_data["values"])
        
        # 5. Objectifs de carrière
        if "career_goals" in raw_data:
            structured_data["career_goals"] = extract_career_goals(raw_data["career_goals"])
        
        # 6. Compétences techniques (si présentes)
        if "skills" in raw_data:
            structured_data["technical_skills"] = extract_skills(raw_data["skills"])
        
        # 7. Localisation et mobilité
        if "location" in raw_data and "mobility" in raw_data:
            structured_data["location_mobility"] = {
                "location": raw_data["location"],
                "mobility_distance": extract_mobility_distance(raw_data["mobility"])
            }
        
        # 8. Attentes salariales
        if "salary_expectation" in raw_data:
            structured_data["salary_expectation"] = extract_salary_range(raw_data["salary_expectation"])
        
        # 9. Disponibilité
        if "availability" in raw_data:
            structured_data["availability"] = extract_availability(raw_data["availability"])
        
        # 10. Préférences sectorielles
        if "sector_preference" in raw_data:
            structured_data["sector_preference"] = extract_sectors(raw_data["sector_preference"])
        
        return structured_data
    
    except Exception as e:
        logger.error(f"Erreur lors du parsing du questionnaire candidat: {str(e)}")
        # Retourner un dict minimal pour éviter les erreurs en aval
        return {
            "environment_preference": "calme et silencieux",
            "work_mode_preference": "hybride (3j bureau / 2j remote)",
            "values_important": ["collaboration", "respect", "innovation"]
        }

def parse_company_questionnaire(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse et structure les données du questionnaire entreprise.
    
    Args:
        raw_data: Données brutes du questionnaire entreprise
        
    Returns:
        Données structurées pour l'algorithme de matching
    """
    try:
        structured_data = {}
        
        # 1. Environnement de travail offert
        if "work_environment" in raw_data:
            structured_data["environment_offered"] = map_environment_value(raw_data["work_environment"])
        
        # 2. Mode de travail offert
        if "work_mode" in raw_data:
            structured_data["work_mode_offered"] = map_work_mode_value(raw_data["work_mode"])
        
        # 3. Taille d'équipe
        if "team_size" in raw_data:
            structured_data["team_size"] = map_team_size_value(raw_data["team_size"])
        
        # 4. Valeurs de l'entreprise
        if "company_values" in raw_data:
            structured_data["company_values"] = extract_values(raw_data["company_values"])
        
        # 5. Opportunités de croissance
        if "growth_opportunities" in raw_data:
            structured_data["growth_opportunities"] = extract_growth_opportunities(raw_data["growth_opportunities"])
        
        # 6. Compétences requises
        if "required_skills" in raw_data:
            structured_data["required_skills"] = extract_skills(raw_data["required_skills"])
        
        # 7. Localisation
        if "location" in raw_data:
            structured_data["location"] = raw_data["location"]
        
        # 8. Plage salariale
        if "salary_range" in raw_data:
            structured_data["salary_range"] = extract_salary_range(raw_data["salary_range"])
        
        # 9. Date de début souhaitée
        if "start_date" in raw_data:
            structured_data["desired_start_date"] = raw_data["start_date"]
        
        # 10. Secteur d'activité
        if "sector" in raw_data:
            structured_data["sector"] = raw_data["sector"]
        
        return structured_data
    
    except Exception as e:
        logger.error(f"Erreur lors du parsing du questionnaire entreprise: {str(e)}")
        # Retourner un dict minimal pour éviter les erreurs en aval
        return {
            "environment_offered": "open space collaboratif",
            "work_mode_offered": "hybride (3j bureau / 2j remote)",
            "company_values": ["excellence", "innovation", "collaboration"]
        }

def map_environment_value(value: Union[str, int]) -> str:
    """
    Mappe les valeurs numériques ou textuelles d'environnement de travail à des chaînes standardisées.
    
    Args:
        value: Valeur d'environnement de travail (peut être un entier ou une chaîne)
        
    Returns:
        Chaîne standardisée représentant l'environnement
    """
    environment_mapping = {
        0: "calme et silencieux",
        1: "calme et silencieux",
        2: "dynamique avec espaces calmes",
        3: "open space collaboratif",
        4: "très dynamique et animé",
        5: "très dynamique et animé",
        "calme": "calme et silencieux",
        "silencieux": "calme et silencieux",
        "dynamique": "dynamique avec espaces calmes",
        "équilibre": "dynamique avec espaces calmes",
        "open space": "open space collaboratif",
        "collaboratif": "open space collaboratif",
        "animé": "très dynamique et animé",
        "startup": "très dynamique et animé"
    }
    
    # Si la valeur est une chaîne, la convertir en minuscules pour la recherche
    if isinstance(value, str):
        value_lower = value.lower()
        
        # Recherche directe
        if value_lower in environment_mapping:
            return environment_mapping[value_lower]
        
        # Recherche de sous-chaînes
        for key, mapped_value in environment_mapping.items():
            if isinstance(key, str) and key in value_lower:
                return mapped_value
    
    # Si la valeur est un entier ou un entier sous forme de chaîne
    try:
        int_value = int(value)
        if int_value in environment_mapping:
            return environment_mapping[int_value]
    except (ValueError, TypeError):
        pass
    
    # Valeur par défaut
    return "dynamique avec espaces calmes"

def map_work_mode_value(value: Union[str, int]) -> str:
    """
    Mappe les valeurs de mode de travail à des chaînes standardisées.
    
    Args:
        value: Valeur du mode de travail (peut être un entier ou une chaîne)
        
    Returns:
        Chaîne standardisée représentant le mode de travail
    """
    work_mode_mapping = {
        0: "100% présentiel",
        1: "100% présentiel",
        2: "hybride (3j bureau / 2j remote)",
        3: "hybride (2j bureau / 3j remote)",
        4: "100% télétravail",
        5: "100% télétravail",
        "présentiel": "100% présentiel",
        "bureau": "100% présentiel",
        "hybride": "hybride (3j bureau / 2j remote)",
        "mixte": "hybride (3j bureau / 2j remote)",
        "flexible": "hybride (2j bureau / 3j remote)",
        "télétravail": "100% télétravail",
        "remote": "100% télétravail",
        "à distance": "100% télétravail"
    }
    
    # Si la valeur est une chaîne, la convertir en minuscules pour la recherche
    if isinstance(value, str):
        value_lower = value.lower()
        
        # Recherche directe
        if value_lower in work_mode_mapping:
            return work_mode_mapping[value_lower]
        
        # Recherche de sous-chaînes
        for key, mapped_value in work_mode_mapping.items():
            if isinstance(key, str) and key in value_lower:
                return mapped_value
    
    # Si la valeur est un entier ou un entier sous forme de chaîne
    try:
        int_value = int(value)
        if int_value in work_mode_mapping:
            return work_mode_mapping[int_value]
    except (ValueError, TypeError):
        pass
    
    # Valeur par défaut
    return "hybride (3j bureau / 2j remote)"

def map_team_size_value(value: Union[str, int]) -> str:
    """
    Mappe les valeurs de taille d'équipe à des chaînes standardisées.
    
    Args:
        value: Valeur de la taille d'équipe (peut être un entier ou une chaîne)
        
    Returns:
        Chaîne standardisée représentant la taille d'équipe
    """
    team_size_mapping = {
        0: "startup (<20 personnes)",
        1: "startup (<20 personnes)",
        2: "petite entreprise (20-100)",
        3: "entreprise moyenne (100-500)",
        4: "grande entreprise (500+)",
        5: "grande entreprise (500+)",
        "startup": "startup (<20 personnes)",
        "petite": "petite entreprise (20-100)",
        "pme": "petite entreprise (20-100)",
        "moyenne": "entreprise moyenne (100-500)",
        "eti": "entreprise moyenne (100-500)",
        "grande": "grande entreprise (500+)",
        "international": "grande entreprise (500+)"
    }
    
    # Si la valeur est une chaîne, la convertir en minuscules pour la recherche
    if isinstance(value, str):
        value_lower = value.lower()
        
        # Recherche directe
        if value_lower in team_size_mapping:
            return team_size_mapping[value_lower]
        
        # Recherche de sous-chaînes
        for key, mapped_value in team_size_mapping.items():
            if isinstance(key, str) and key in value_lower:
                return mapped_value
        
        # Recherche de nombres
        numbers = re.findall(r'\d+', value_lower)
        if numbers:
            size = int(numbers[0])
            if size < 20:
                return "startup (<20 personnes)"
            elif size < 100:
                return "petite entreprise (20-100)"
            elif size < 500:
                return "entreprise moyenne (100-500)"
            else:
                return "grande entreprise (500+)"
    
    # Si la valeur est un entier ou un entier sous forme de chaîne
    try:
        int_value = int(value)
        if int_value in team_size_mapping:
            return team_size_mapping[int_value]
    except (ValueError, TypeError):
        pass
    
    # Valeur par défaut
    return "entreprise moyenne (100-500)"

def extract_values(values_data: Union[str, List, Dict]) -> List[str]:
    """
    Extrait une liste de valeurs à partir de différents formats possibles.
    
    Args:
        values_data: Données de valeurs dans différents formats possibles
        
    Returns:
        Liste de valeurs normalisées
    """
    standard_values = [
        "innovation", "collaboration", "excellence", "agilité", "diversité",
        "responsabilité", "transparence", "respect", "confiance", "créativité",
        "efficacité", "qualité", "intégrité", "leadership", "passion"
    ]
    
    # Si c'est déjà une liste
    if isinstance(values_data, list):
        # Si c'est une liste de dictionnaires (e.g. [{name: "value1"}, ...])
        if values_data and isinstance(values_data[0], dict):
            return [item.get("name", "").lower() for item in values_data if "name" in item]
        # Si c'est une liste de chaînes
        return [str(item).lower() for item in values_data]
    
    # Si c'est une chaîne
    if isinstance(values_data, str):
        # Si c'est du JSON
        if values_data.startswith("[") or values_data.startswith("{"):
            try:
                json_data = json.loads(values_data)
                return extract_values(json_data)
            except json.JSONDecodeError:
                pass
        
        # Essayer de séparer par des délimiteurs communs
        if "," in values_data:
            return [item.strip().lower() for item in values_data.split(",")]
        if ";" in values_data:
            return [item.strip().lower() for item in values_data.split(";")]
        
        # Si une seule valeur, chercher les correspondances
        value_lower = values_data.lower()
        matched_values = []
        for std_value in standard_values:
            if std_value in value_lower:
                matched_values.append(std_value)
        
        # Si des correspondances trouvées, les retourner
        if matched_values:
            return matched_values
        
        # Sinon, retourner la chaîne entière
        return [value_lower]
    
    # Si c'est un dictionnaire
    if isinstance(values_data, dict):
        # Format {value1: true, value2: false, ...}
        if all(isinstance(v, bool) for v in values_data.values()):
            return [k.lower() for k, v in values_data.items() if v]
        
        # Format {1: "value1", 2: "value2", ...}
        if all(isinstance(k, (int, float)) for k in values_data.keys()):
            return [str(v).lower() for v in values_data.values()]
    
    # Valeur par défaut
    return ["collaboration", "innovation", "respect"]

def extract_career_goals(goals_data: Union[str, List, Dict]) -> List[str]:
    """
    Extrait les objectifs de carrière à partir de différents formats possibles.
    
    Args:
        goals_data: Données d'objectifs de carrière dans différents formats
        
    Returns:
        Liste d'objectifs de carrière normalisés
    """
    # Réutiliser la logique d'extraction des valeurs
    return extract_values(goals_data)

def extract_growth_opportunities(opps_data: Union[str, List, Dict]) -> List[str]:
    """
    Extrait les opportunités de croissance à partir de différents formats possibles.
    
    Args:
        opps_data: Données d'opportunités de croissance dans différents formats
        
    Returns:
        Liste d'opportunités de croissance normalisées
    """
    # Réutiliser la logique d'extraction des valeurs
    return extract_values(opps_data)

def extract_skills(skills_data: Union[str, List, Dict]) -> List[Dict[str, Any]]:
    """
    Extrait les compétences à partir de différents formats possibles.
    
    Args:
        skills_data: Données de compétences dans différents formats
        
    Returns:
        Liste de compétences normalisées avec niveau
    """
    skills = []
    
    # Si c'est déjà une liste
    if isinstance(skills_data, list):
        # Si c'est une liste de dictionnaires
        if skills_data and isinstance(skills_data[0], dict):
            for skill_item in skills_data:
                skill = {
                    "name": skill_item.get("name", "").lower(),
                    "level": skill_item.get("level", 3)
                }
                if "years" in skill_item:
                    skill["years"] = skill_item["years"]
                skills.append(skill)
            return skills
        
        # Si c'est une liste de chaînes
        return [{"name": str(item).lower(), "level": 3} for item in skills_data]
    
    # Si c'est une chaîne
    if isinstance(skills_data, str):
        # Si c'est du JSON
        if skills_data.startswith("[") or skills_data.startswith("{"):
            try:
                json_data = json.loads(skills_data)
                return extract_skills(json_data)
            except json.JSONDecodeError:
                pass
        
        # Essayer de séparer par des délimiteurs communs
        skill_items = []
        if "," in skills_data:
            skill_items = [item.strip() for item in skills_data.split(",")]
        elif ";" in skills_data:
            skill_items = [item.strip() for item in skills_data.split(";")]
        else:
            skill_items = [skills_data.strip()]
        
        for item in skill_items:
            # Essayer d'extraire le niveau
            level_match = re.search(r'(\d+)/\d+', item)
            if level_match:
                level = int(level_match.group(1))
                name = re.sub(r'\d+/\d+', '', item).strip()
                skills.append({"name": name.lower(), "level": level})
            else:
                skills.append({"name": item.lower(), "level": 3})
        
        return skills
    
    # Si c'est un dictionnaire
    if isinstance(skills_data, dict):
        # Format {skill1: level1, skill2: level2, ...}
        for skill_name, value in skills_data.items():
            if isinstance(value, (int, float)):
                skills.append({"name": skill_name.lower(), "level": value})
            else:
                skills.append({"name": skill_name.lower(), "level": 3})
        return skills
    
    # Valeur par défaut
    return [{"name": "compétence générale", "level": 3}]

def extract_mobility_distance(mobility_data: Union[str, int, Dict]) -> int:
    """
    Extrait la distance de mobilité en kilomètres.
    
    Args:
        mobility_data: Données de mobilité dans différents formats
        
    Returns:
        Distance de mobilité en kilomètres
    """
    # Si c'est déjà un entier
    if isinstance(mobility_data, int):
        return mobility_data
    
    # Si c'est une chaîne
    if isinstance(mobility_data, str):
        # Rechercher des nombres
        numbers = re.findall(r'\d+', mobility_data)
        if numbers:
            return int(numbers[0])
        
        # Rechercher des mots-clés
        mobility_lower = mobility_data.lower()
        if "international" in mobility_lower or "pays" in mobility_lower:
            return 10000
        if "national" in mobility_lower or "france" in mobility_lower:
            return 1000
        if "région" in mobility_lower:
            return 200
        if "département" in mobility_lower:
            return 100
        if "ville" in mobility_lower or "local" in mobility_lower:
            return 30
    
    # Si c'est un dictionnaire
    if isinstance(mobility_data, dict):
        if "distance" in mobility_data:
            return extract_mobility_distance(mobility_data["distance"])
    
    # Valeur par défaut
    return 50  # 50 km par défaut

def extract_salary_range(salary_data: Union[str, int, Dict]) -> Dict[str, int]:
    """
    Extrait la plage salariale.
    
    Args:
        salary_data: Données de salaire dans différents formats
        
    Returns:
        Dictionnaire avec min et max
    """
    # Valeur par défaut
    salary_range = {"min": 35000, "max": 45000}
    
    # Si c'est un entier
    if isinstance(salary_data, int):
        salary_range["min"] = salary_data - 5000
        salary_range["max"] = salary_data + 5000
        return salary_range
    
    # Si c'est une chaîne
    if isinstance(salary_data, str):
        # Rechercher des plages de type "40K-50K" ou "40000-50000"
        range_match = re.search(r'(\d+)[kK]?[-–—](\d+)[kK]?', salary_data)
        if range_match:
            min_val = int(range_match.group(1))
            max_val = int(range_match.group(2))
            
            # Convertir K en milliers si nécessaire
            if "k" in salary_data.lower() and min_val < 1000:
                min_val *= 1000
                max_val *= 1000
            
            salary_range["min"] = min_val
            salary_range["max"] = max_val
            return salary_range
        
        # Rechercher un nombre unique
        number_match = re.search(r'(\d+)[kK]?', salary_data)
        if number_match:
            val = int(number_match.group(1))
            
            # Convertir K en milliers si nécessaire
            if "k" in salary_data.lower() and val < 1000:
                val *= 1000
            
            salary_range["min"] = val - 5000
            salary_range["max"] = val + 5000
            return salary_range
    
    # Si c'est un dictionnaire
    if isinstance(salary_data, dict):
        if "min" in salary_data:
            salary_range["min"] = int(salary_data["min"])
        if "max" in salary_data:
            salary_range["max"] = int(salary_data["max"])
        return salary_range
    
    return salary_range

def extract_availability(availability_data: Union[str, Dict]) -> str:
    """
    Extrait la disponibilité.
    
    Args:
        availability_data: Données de disponibilité dans différents formats
        
    Returns:
        Chaîne normalisée de disponibilité
    """
    # Si c'est une chaîne
    if isinstance(availability_data, str):
        availability_lower = availability_data.lower()
        
        if "immédiate" in availability_lower or "dès maintenant" in availability_lower:
            return "immediate"
        
        # Rechercher des dates au format DD/MM/YYYY ou similaire
        date_match = re.search(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})', availability_lower)
        if date_match:
            day = date_match.group(1).zfill(2)
            month = date_match.group(2).zfill(2)
            year = date_match.group(3)
            if len(year) == 2:
                year = "20" + year
            
            return f"{year}-{month}-{day}"
        
        # Rechercher du texte comme "dans X mois" ou "X semaines"
        if "mois" in availability_lower:
            numbers = re.findall(r'\d+', availability_lower)
            if numbers:
                return f"in_{numbers[0]}_months"
        
        if "semaine" in availability_lower:
            numbers = re.findall(r'\d+', availability_lower)
            if numbers:
                return f"in_{numbers[0]}_weeks"
    
    # Si c'est un dictionnaire
    if isinstance(availability_data, dict):
        if "date" in availability_data:
            return availability_data["date"]
        if "text" in availability_data:
            return extract_availability(availability_data["text"])
    
    # Valeur par défaut
    return "in_1_month"

def extract_sectors(sectors_data: Union[str, List, Dict]) -> List[str]:
    """
    Extrait les secteurs d'activité préférés.
    
    Args:
        sectors_data: Données de secteurs dans différents formats
        
    Returns:
        Liste de secteurs normalisés
    """
    # Réutiliser la logique d'extraction des valeurs
    return extract_values(sectors_data)

def extract_questionnaire_data_from_form(form_data: Dict[str, Any], is_company: bool = False) -> Dict[str, Any]:
    """
    Extrait les données de questionnaire à partir des données de formulaire HTML.
    
    Args:
        form_data: Données du formulaire
        is_company: True si c'est un formulaire entreprise, False pour candidat
        
    Returns:
        Données structurées du questionnaire
    """
    try:
        # Normaliser les noms de champs
        normalized_data = {}
        
        # Mapper les noms de champs du formulaire aux noms de champs internes
        field_mapping = {
            # Mappings communs
            "environment": "work_environment",
            "workEnvironment": "work_environment",
            "workMode": "work_mode",
            "teamSize": "team_size",
            "values": "values",
            "location": "location",
            
            # Mappings spécifiques au candidat
            "careerGoals": "career_goals",
            "skills": "skills",
            "mobility": "mobility",
            "salaryExpectation": "salary_expectation",
            "availability": "availability",
            "sectorPreference": "sector_preference",
            
            # Mappings spécifiques à l'entreprise
            "companyValues": "company_values",
            "growthOpportunities": "growth_opportunities",
            "requiredSkills": "required_skills",
            "salaryRange": "salary_range",
            "startDate": "start_date",
            "sector": "sector"
        }
        
        # Traiter chaque champ du formulaire
        for field_name, value in form_data.items():
            # Vérifier si le champ est dans notre mapping
            normalized_name = None
            for original, mapped in field_mapping.items():
                if original.lower() in field_name.lower():
                    normalized_name = mapped
                    break
            
            # Si pas trouvé, utiliser le nom original
            if normalized_name is None:
                normalized_name = field_name
            
            # Stocker la valeur avec le nom normalisé
            normalized_data[normalized_name] = value
        
        # Analyser les données
        if is_company:
            return parse_company_questionnaire(normalized_data)
        else:
            return parse_candidate_questionnaire(normalized_data)
    
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des données de formulaire: {str(e)}")
        # Retourner un dict minimal pour éviter les erreurs en aval
        if is_company:
            return {
                "environment_offered": "open space collaboratif",
                "work_mode_offered": "hybride (3j bureau / 2j remote)",
                "company_values": ["excellence", "innovation", "collaboration"]
            }
        else:
            return {
                "environment_preference": "calme et silencieux",
                "work_mode_preference": "hybride (3j bureau / 2j remote)",
                "values_important": ["collaboration", "respect", "innovation"]
            }
