"""
SmartMatch Data Adapter - Module d'adaptation de données pour SmartMatch
-----------------------------------------------------------------------
Ce module permet d'adapter les données entre les formats de sortie du CV Parser
et du Job Parser vers le format attendu par l'algorithme SmartMatch.

Version: 2.0.0 - Intégration des questionnaires
Auteur: Claude
Date: 16/05/2025
"""

import re
import json
import logging
import math
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartMatchDataAdapter:
    """
    Adaptateur de données pour l'algorithme SmartMatch
    
    Cette classe permet de transformer les formats de sortie des parsers (CV et Job)
    en formats compatibles avec l'algorithme de matching SmartMatch.
    """
    
    def __init__(self, use_location_lookup: bool = True):
        """
        Initialisation de l'adaptateur
        
        Args:
            use_location_lookup (bool): Activer la recherche de coordonnées pour les adresses
        """
        self.use_location_lookup = use_location_lookup
        
        # Mapping des niveaux d'éducation
        self.education_mapping = {
            # Mots-clés français -> format SmartMatch
            "bac": "high_school",
            "lycée": "high_school",
            "bts": "associate",
            "dut": "associate",
            "licence": "bachelor",
            "bachelor": "bachelor",
            "master": "master",
            "ingénieur": "master",
            "doctorat": "phd",
            "thèse": "phd",
            "phd": "phd",
            "docteur": "phd",
            # Par défaut
            "default": "bachelor"
        }
        
        # Mapping des types de contrat
        self.contract_mapping = {
            "cdi": "full_time",
            "permanent": "full_time",
            "cdd": "contract",
            "contract": "contract",
            "stage": "internship",
            "internship": "internship",
            "alternance": "apprenticeship",
            "apprenticeship": "apprenticeship",
            "freelance": "freelance",
            "indépendant": "freelance",
            # Par défaut
            "default": "full_time"
        }
        
        logger.info("SmartMatchDataAdapter initialisé avec succès")
    
    def address_to_coordinates(self, address: str) -> str:
        """
        Convertit une adresse textuelle en coordonnées géographiques
        
        Args:
            address (str): Adresse au format texte
            
        Returns:
            str: Coordonnées au format "latitude,longitude"
        """
        # Dans une implémentation réelle, utiliser une API de géocodage comme Google Maps
        # Pour cette démo, nous utilisons des coordonnées fictives pour Paris
        if not address:
            return "48.8566,2.3522"  # Coordonnées de Paris par défaut
        
        # Simulation de géocodage - dans une implémentation réelle, appeler une API
        # Ici on détecte simplement quelques villes françaises courantes
        if re.search(r'\bparis\b', address.lower()):
            return "48.8566,2.3522"
        elif re.search(r'\blyon\b', address.lower()):
            return "45.7640,4.8357"
        elif re.search(r'\bmarseille\b', address.lower()):
            return "43.2965,5.3698"
        elif re.search(r'\btoulouse\b', address.lower()):
            return "43.6043,1.4437"
        elif re.search(r'\bnice\b', address.lower()):
            return "43.7034,7.2663"
        elif re.search(r'\bnantes\b', address.lower()):
            return "47.2173,1.5534"
        elif re.search(r'\bstrasbourg\b', address.lower()):
            return "48.5734,7.7521"
        elif re.search(r'\bmontpellier\b', address.lower()):
            return "43.6108,3.8767"
        elif re.search(r'\bbordeaux\b', address.lower()):
            return "44.8378,0.5792"
        elif re.search(r'\blille\b', address.lower()):
            return "50.6292,3.0573"
        else:
            # Coordonnées génériques pour la France si la ville n'est pas reconnue
            return "46.603354,1.8883335"  # Centre de la France
    
    def extract_education_level(self, text: str) -> str:
        """
        Extrait le niveau d'éducation à partir d'un texte
        
        Args:
            text (str): Texte contenant des informations sur l'éducation
            
        Returns:
            str: Niveau d'éducation au format SmartMatch
        """
        if not text:
            return self.education_mapping["default"]
        
        text_lower = text.lower()
        
        # Parcourir les mots-clés d'éducation
        for keyword, level in self.education_mapping.items():
            if keyword in text_lower:
                return level
        
        # Si aucun mot-clé n'est trouvé, retourner la valeur par défaut
        return self.education_mapping["default"]
    
    def extract_contract_type(self, text: str) -> str:
        """
        Extrait le type de contrat à partir d'un texte
        
        Args:
            text (str): Texte contenant des informations sur le contrat
            
        Returns:
            str: Type de contrat au format SmartMatch
        """
        if not text:
            return self.contract_mapping["default"]
        
        text_lower = text.lower()
        
        # Parcourir les mots-clés de contrat
        for keyword, contract_type in self.contract_mapping.items():
            if keyword in text_lower:
                return contract_type
        
        # Si aucun mot-clé n'est trouvé, retourner la valeur par défaut
        return self.contract_mapping["default"]
    
    def extract_salary_range(self, text: str) -> Dict[str, int]:
        """
        Extrait une fourchette de salaire à partir d'un texte
        
        Args:
            text (str): Texte contenant des informations sur le salaire
            
        Returns:
            Dict[str, int]: Fourchette de salaire {"min": X, "max": Y}
        """
        if not text:
            return {"min": 35000, "max": 50000}  # Valeurs par défaut
        
        # Recherche de patterns comme "40K-50K", "40 000 - 50 000 €", etc.
        # Supprimer les espaces dans les chiffres et les séparateurs de milliers
        text_clean = re.sub(r'\s+', '', text)
        text_clean = re.sub(r'[^\d\-.,€$kK]', '', text_clean)
        
        # Recherche de fourchettes
        range_match = re.search(r'(\d+[.,]?\d*)[kK€$]?[\-–à]+(\d+[.,]?\d*)[kK€$]?', text_clean)
        if range_match:
            min_val = float(range_match.group(1).replace(',', '.'))
            max_val = float(range_match.group(2).replace(',', '.'))
            
            # Si valeurs en K (milliers)
            if 'k' in text_clean.lower() or 'K' in text_clean:
                min_val *= 1000
                max_val *= 1000
            
            return {"min": int(min_val), "max": int(max_val)}
        
        # Recherche d'une valeur unique
        single_match = re.search(r'(\d+[.,]?\d*)[kK€$]?', text_clean)
        if single_match:
            value = float(single_match.group(1).replace(',', '.'))
            
            # Si valeur en K (milliers)
            if 'k' in text_clean.lower() or 'K' in text_clean:
                value *= 1000
            
            # Créer une fourchette autour de la valeur unique
            return {"min": int(value * 0.9), "max": int(value * 1.1)}
        
        # Valeur par défaut si rien n'est trouvé
        return {"min": 35000, "max": 50000}
    
    def extract_years_experience(self, text: str) -> int:
        """
        Extrait le nombre d'années d'expérience à partir d'un texte
        
        Args:
            text (str): Texte contenant des informations sur l'expérience
            
        Returns:
            int: Nombre d'années d'expérience
        """
        if not text:
            return 0
        
        # Recherche de patterns comme "5 ans", "5 years", "5+ ans", etc.
        text_lower = text.lower()
        
        # Recherche explicite d'années
        years_match = re.search(r'(\d+)[+]?\s*(ans|années|years|year)', text_lower)
        if years_match:
            return int(years_match.group(1))
        
        # Recherche d'un chiffre simple
        num_match = re.search(r'(\d+)[+]?', text_lower)
        if num_match:
            return int(num_match.group(1))
        
        # Recherche de mots-clés
        if "débutant" in text_lower or "junior" in text_lower:
            return 1
        elif "intermédiaire" in text_lower or "confirmé" in text_lower:
            return 3
        elif "senior" in text_lower or "expérimenté" in text_lower:
            return 5
        elif "expert" in text_lower:
            return 8
        
        # Valeur par défaut
        return 0
    
    def cv_to_smartmatch_format(self, cv_data: Dict[str, Any], cv_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Convertit les données du CV Parser au format attendu par SmartMatch
        
        Args:
            cv_data (Dict): Données issues du CV Parser
            cv_id (str, optional): Identifiant du CV
            
        Returns:
            Dict: Données au format SmartMatch
        """
        if not cv_data:
            logger.warning("Données CV vides")
            return {}
        
        # Générer un ID si non fourni
        if not cv_id:
            cv_id = f"cv_{int(datetime.now().timestamp())}"
        
        # Créer le nom complet
        full_name = f"{cv_data.get('prenom', '')} {cv_data.get('nom', '')}".strip()
        
        # Récupérer toutes les compétences et fusionner les listes
        all_skills = []
        if 'competences' in cv_data and cv_data['competences']:
            all_skills.extend(cv_data['competences'])
        if 'logiciels' in cv_data and cv_data['logiciels']:
            all_skills.extend(cv_data['logiciels'])
        
        # Coordonnées géographiques à partir de l'adresse
        location = cv_data.get('adresse', '')
        if self.use_location_lookup and location:
            location_coords = self.address_to_coordinates(location)
        else:
            location_coords = "48.8566,2.3522"  # Paris par défaut
        
        # Analyser le poste pour en extraire des informations supplémentaires
        job_title = cv_data.get('poste', '')
        
        # Le format final attendu par SmartMatch
        smartmatch_data = {
            "id": cv_id,
            "name": full_name,
            "skills": all_skills,
            "soft_skills": cv_data.get('soft_skills', []),
            "location": location_coords,
            "address": cv_data.get('adresse', ''),
            "contact": {
                "email": cv_data.get('email', ''),
                "phone": cv_data.get('telephone', '')
            },
            # Valeurs à affiner avec des extracteurs plus précis dans une mise en œuvre réelle
            "years_of_experience": 3,  # Valeur par défaut
            "education_level": "bachelor",  # Valeur par défaut
            "remote_work": True,  # Valeur par défaut
            "salary_expectation": 45000,  # Valeur par défaut
            "job_type": "full_time",  # Valeur par défaut
            "industry": "tech"  # Valeur par défaut
        }
        
        logger.info(f"CV converti avec succès pour {full_name}")
        return smartmatch_data
    
    def job_to_smartmatch_format(self, job_data: Dict[str, Any], job_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Convertit les données du Job Parser au format attendu par SmartMatch
        
        Args:
            job_data (Dict): Données issues du Job Parser
            job_id (str, optional): Identifiant de l'offre d'emploi
            
        Returns:
            Dict: Données au format SmartMatch
        """
        if not job_data:
            logger.warning("Données d'offre d'emploi vides")
            return {}
        
        # Générer un ID si non fourni
        if not job_id:
            job_id = f"job_{int(datetime.now().timestamp())}"
        
        # Extraire les compétences (séparation entre requises et préférées)
        skills = job_data.get('skills', [])
        required_skills = []
        preferred_skills = []
        
        # Dans une implémentation réelle, on pourrait analyser les textes pour déterminer
        # quelles compétences sont requises vs préférées. Ici on fait une répartition simple.
        if skills:
            # 2/3 des compétences sont considérées comme requises, le reste comme préférées
            split_index = max(1, len(skills) * 2 // 3)
            required_skills = skills[:split_index]
            preferred_skills = skills[split_index:]
        
        # Coordonnées géographiques à partir de l'adresse/localisation
        location = job_data.get('location', '')
        if self.use_location_lookup and location:
            location_coords = self.address_to_coordinates(location)
        else:
            location_coords = "48.8566,2.3522"  # Paris par défaut
        
        # Extraire le type de contrat
        contract_type = self.extract_contract_type(job_data.get('contract_type', ''))
        
        # Extraire l'expérience requise
        experience = self.extract_years_experience(job_data.get('experience', ''))
        
        # Extraire le niveau d'éducation requis
        education_level = self.extract_education_level(job_data.get('education', ''))
        
        # Extraire la fourchette de salaire
        salary_range = self.extract_salary_range(job_data.get('salary', ''))
        
        # Le format final attendu par SmartMatch
        smartmatch_data = {
            "id": job_id,
            "title": job_data.get('title', ''),
            "company": job_data.get('company', ''),
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "location": location_coords,
            "location_text": location,
            "min_years_of_experience": experience,
            "max_years_of_experience": experience + 3,  # Estimation
            "required_education": education_level,
            "offers_remote": "remote" in job_data.get('title', '').lower() or "télétravail" in job_data.get('title', '').lower(),
            "salary_range": salary_range,
            "job_type": contract_type,
            "industry": "tech",  # Valeur par défaut
            "responsibilities": job_data.get('responsibilities', []),
            "benefits": job_data.get('benefits', [])
        }
        
        logger.info(f"Offre d'emploi convertie avec succès: {job_data.get('title', '')}")
        return smartmatch_data
    
    def json_to_smartmatch(self, json_data: str, data_type: str, item_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Convertit des données JSON en format SmartMatch
        
        Args:
            json_data (str): Données JSON à convertir
            data_type (str): Type de données ('cv' ou 'job')
            item_id (str, optional): Identifiant de l'élément
            
        Returns:
            Dict: Données au format SmartMatch
        """
        try:
            data = json.loads(json_data)
            
            if data_type.lower() == 'cv':
                return self.cv_to_smartmatch_format(data, item_id)
            elif data_type.lower() == 'job':
                return self.job_to_smartmatch_format(data, item_id)
            else:
                logger.error(f"Type de données non supporté: {data_type}")
                return {}
                
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Erreur lors de la conversion: {str(e)}")
            return {}
    
    def file_to_smartmatch(self, file_path: str, data_type: str, item_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Convertit des données à partir d'un fichier en format SmartMatch
        
        Args:
            file_path (str): Chemin vers le fichier à convertir
            data_type (str): Type de données ('cv' ou 'job')
            item_id (str, optional): Identifiant de l'élément
            
        Returns:
            Dict: Données au format SmartMatch
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = f.read()
            
            return self.json_to_smartmatch(json_data, data_type, item_id)
                
        except FileNotFoundError:
            logger.error(f"Fichier non trouvé: {file_path}")
            return {}
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du fichier: {str(e)}")
            return {}
    
    def batch_convert(self, data_list: List[Dict[str, Any]], data_type: str) -> List[Dict[str, Any]]:
        """
        Convertit un lot de données au format SmartMatch
        
        Args:
            data_list (List[Dict]): Liste de données à convertir
            data_type (str): Type de données ('cv' ou 'job')
            
        Returns:
            List[Dict]: Liste de données au format SmartMatch
        """
        result = []
        
        for i, data in enumerate(data_list):
            item_id = f"{data_type}_{i}_{int(datetime.now().timestamp())}"
            
            if data_type.lower() == 'cv':
                converted = self.cv_to_smartmatch_format(data, item_id)
            elif data_type.lower() == 'job':
                converted = self.job_to_smartmatch_format(data, item_id)
            else:
                logger.error(f"Type de données non supporté: {data_type}")
                continue
            
            if converted:
                result.append(converted)
        
        logger.info(f"Lot de {len(result)} éléments {data_type} convertis avec succès")
        return result

    # Nouvelles méthodes pour intégrer les questionnaires

    def enrich_cv_data_with_questionnaire(self, cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any], cv_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Enrichit les données CV avec les réponses au questionnaire candidat
        
        Args:
            cv_data (Dict): Données du CV
            questionnaire_data (Dict): Réponses du questionnaire candidat
            cv_id (str, optional): Identifiant du CV
            
        Returns:
            Dict: Données CV enrichies
        """
        if not cv_data:
            logger.warning("Données CV vides")
            return {}
        
        if not questionnaire_data:
            logger.warning("Données de questionnaire vides, retour des données CV originales")
            return cv_data
        
        # Si les données ont déjà été converties au format SmartMatch
        if 'id' in cv_data and 'skills' in cv_data:
            enriched_data = cv_data.copy()
        else:
            # Sinon, convertir d'abord au format SmartMatch
            enriched_data = self.cv_to_smartmatch_format(cv_data, cv_id)
        
        # Enrichir avec les informations de mobilité
        if 'transport-method' in questionnaire_data:
            transport_methods = questionnaire_data.get('transport-method', [])
            if isinstance(transport_methods, str):
                transport_methods = [transport_methods]
            
            enriched_data['mobility'] = {
                'transport_methods': transport_methods,
                'commute_times': {}
            }
            
            # Ajouter les temps de trajet pour chaque moyen de transport
            for method in transport_methods:
                time_key = f'commute-time-{method}'
                if time_key in questionnaire_data:
                    enriched_data['mobility']['commute_times'][method] = int(questionnaire_data[time_key])
        
        # Ajouter l'adresse exacte et les coordonnées
        if 'address' in questionnaire_data:
            enriched_data['exact_address'] = questionnaire_data['address']
            
            # Si des coordonnées sont disponibles dans le questionnaire
            if 'address-lat' in questionnaire_data and 'address-lng' in questionnaire_data:
                lat = questionnaire_data['address-lat']
                lng = questionnaire_data['address-lng']
                enriched_data['location'] = f"{lat},{lng}"
        
        # Préférences d'environnement de travail
        if 'office-preference' in questionnaire_data:
            enriched_data['work_environment_preference'] = questionnaire_data['office-preference']
        
        # Leviers de motivation
        if 'motivation-order' in questionnaire_data:
            motivation_order = questionnaire_data['motivation-order']
            if isinstance(motivation_order, str):
                motivation_order = motivation_order.split(',')
            
            enriched_data['motivations'] = motivation_order
            
            # Si "other" est parmi les motivations et qu'un détail est fourni
            if 'other' in motivation_order and 'other-motivation' in questionnaire_data:
                enriched_data['other_motivation'] = questionnaire_data['other-motivation']
        
        # Préférences de structure
        if 'structure-type' in questionnaire_data:
            structure_types = questionnaire_data.get('structure-type', [])
            if isinstance(structure_types, str):
                structure_types = [structure_types]
            
            enriched_data['preferred_structure_types'] = structure_types
        
        # Préférences sectorielles
        if 'has-sector-preference' in questionnaire_data:
            has_preference = questionnaire_data['has-sector-preference'] == 'yes'
            enriched_data['has_sector_preference'] = has_preference
            
            if has_preference and 'sector-preference' in questionnaire_data:
                sectors = questionnaire_data.get('sector-preference', [])
                if isinstance(sectors, str):
                    sectors = [sectors]
                
                enriched_data['preferred_sectors'] = sectors
            
            # Secteurs à éviter
            if 'has-prohibited-sector' in questionnaire_data:
                has_prohibited = questionnaire_data['has-prohibited-sector'] == 'yes'
                
                if has_prohibited and 'prohibited-sector' in questionnaire_data:
                    prohibited_sectors = questionnaire_data.get('prohibited-sector', [])
                    if isinstance(prohibited_sectors, str):
                        prohibited_sectors = [prohibited_sectors]
                    
                    enriched_data['prohibited_sectors'] = prohibited_sectors
        
        # Fourchette de salaire
        if 'salary-range' in questionnaire_data:
            salary_range = questionnaire_data['salary-range']
            parsed_salary = self.extract_salary_range(salary_range)
            enriched_data['salary_expectation'] = {
                'min': parsed_salary['min'],
                'max': parsed_salary['max']
            }
        
        # Disponibilité
        if 'availability' in questionnaire_data:
            availability = questionnaire_data['availability']
            
            # Convertir en nombre de jours approximatif
            days_mapping = {
                'immediate': 0,
                '1month': 30,
                '2months': 60,
                '3months': 90
            }
            
            enriched_data['availability_days'] = days_mapping.get(availability, 0)
        
        # Situation actuelle
        if 'currently-employed' in questionnaire_data:
            is_employed = questionnaire_data['currently-employed'] == 'yes'
            enriched_data['currently_employed'] = is_employed
            
            # Raisons du changement
            if is_employed and 'listening-reason' in questionnaire_data:
                enriched_data['change_reason'] = questionnaire_data['listening-reason']
            elif not is_employed and 'contract-end-reason' in questionnaire_data:
                enriched_data['end_reason'] = questionnaire_data['contract-end-reason']
            
            # Préavis
            if is_employed and 'notice-period' in questionnaire_data:
                notice_period = questionnaire_data['notice-period']
                
                # Convertir en nombre de jours approximatif
                notice_days_mapping = {
                    'none': 0,
                    'trial': 15,
                    '1month': 30,
                    '2months': 60,
                    '3months': 90
                }
                
                enriched_data['notice_period_days'] = notice_days_mapping.get(notice_period, 0)
                
                # Négociabilité du préavis
                if 'notice-negotiable' in questionnaire_data:
                    enriched_data['notice_negotiable'] = questionnaire_data['notice-negotiable'] == 'yes'
        
        # Statut des recrutements en cours
        if 'recruitment-status' in questionnaire_data:
            enriched_data['recruitment_status'] = questionnaire_data['recruitment-status']
        
        logger.info(f"CV enrichi avec les données du questionnaire candidat pour {enriched_data.get('name', 'candidat inconnu')}")
        return enriched_data

    def enrich_job_data_with_questionnaire(self, job_data: Dict[str, Any], questionnaire_data: Dict[str, Any], job_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Enrichit les données d'offre d'emploi avec les réponses au questionnaire client
        
        Args:
            job_data (Dict): Données de l'offre d'emploi
            questionnaire_data (Dict): Réponses du questionnaire client
            job_id (str, optional): Identifiant de l'offre d'emploi
            
        Returns:
            Dict: Données d'offre d'emploi enrichies
        """
        if not job_data:
            logger.warning("Données d'offre d'emploi vides")
            return {}
        
        if not questionnaire_data:
            logger.warning("Données de questionnaire vides, retour des données d'offre originales")
            return job_data
        
        # Si les données ont déjà été converties au format SmartMatch
        if 'id' in job_data and 'required_skills' in job_data:
            enriched_data = job_data.copy()
        else:
            # Sinon, convertir d'abord au format SmartMatch
            enriched_data = self.job_to_smartmatch_format(job_data, job_id)
        
        # Enrichir avec les informations de structure
        if 'company-name' in questionnaire_data:
            enriched_data['company'] = questionnaire_data['company-name']
        
        # Adresse et localisation
        if 'company-address' in questionnaire_data:
            enriched_data['exact_location'] = questionnaire_data['company-address']
            
            # Si nous utilisons la recherche de coordonnées
            if self.use_location_lookup:
                location_coords = self.address_to_coordinates(questionnaire_data['company-address'])
                enriched_data['location'] = location_coords
        
        # Site internet
        if 'company-website' in questionnaire_data:
            enriched_data['company_website'] = questionnaire_data['company-website']
        
        # Description de l'entreprise
        if 'company-description' in questionnaire_data:
            enriched_data['company_description'] = questionnaire_data['company-description']
        
        # Taille de structure
        if 'company-size' in questionnaire_data:
            enriched_data['company_size'] = questionnaire_data['company-size']
        
        # Délai de recrutement
        if 'recruitment-delay' in questionnaire_data:
            delays = questionnaire_data.get('recruitment-delay', [])
            if isinstance(delays, str):
                delays = [delays]
            
            # Convertir en jours et prendre le délai le plus court
            delay_days_mapping = {
                'immediate': 0,
                '2weeks': 14,
                '1month': 30,
                '2months': 60,
                '3months': 90
            }
            
            if delays:
                min_delay = min(delay_days_mapping.get(delay, 90) for delay in delays)
                enriched_data['recruitment_delay_days'] = min_delay
        
        # Gestion des préavis
        if 'can-handle-notice' in questionnaire_data:
            enriched_data['can_handle_notice'] = questionnaire_data['can-handle-notice'] == 'yes'
            
            # Durée de préavis acceptable
            if enriched_data['can_handle_notice'] and 'notice-duration' in questionnaire_data:
                notice_duration = questionnaire_data['notice-duration']
                
                # Convertir en jours
                notice_days_mapping = {
                    '1month': 30,
                    '2months': 60,
                    '3months': 90
                }
                
                enriched_data['max_notice_period_days'] = notice_days_mapping.get(notice_duration, 30)
        
        # Contexte de recrutement
        if 'recruitment-context' in questionnaire_data:
            enriched_data['recruitment_context'] = questionnaire_data['recruitment-context']
        
        # Expérience requise
        if 'experience-required' in questionnaire_data:
            experience = questionnaire_data['experience-required']
            
            # Convertir en années
            experience_years_mapping = {
                'junior': 1,
                '2-3': 3,
                '5-10': 8,
                '10plus': 12
            }
            
            min_years = experience_years_mapping.get(experience, 3)
            max_years = min_years + 3  # Estimation pour la fourchette haute
            
            enriched_data['min_years_of_experience'] = min_years
            enriched_data['max_years_of_experience'] = max_years
        
        # Connaissance sectorielle
        if 'sector-knowledge' in questionnaire_data:
            enriched_data['requires_sector_knowledge'] = questionnaire_data['sector-knowledge'] == 'yes'
            
            # Secteur spécifique requis
            if enriched_data['requires_sector_knowledge'] and 'sector-list' in questionnaire_data:
                enriched_data['required_sector'] = questionnaire_data['sector-list']
        
        # Environnement de travail
        if 'work-environment' in questionnaire_data:
            enriched_data['work_environment'] = questionnaire_data['work-environment']
        
        # Composition de l'équipe
        if 'team-composition' in questionnaire_data:
            enriched_data['team_composition'] = questionnaire_data['team-composition']
        
        # Perspectives d'évolution
        if 'evolution-perspectives' in questionnaire_data:
            enriched_data['evolution_perspectives'] = questionnaire_data['evolution-perspectives']
        
        # Rémunération (si pas déjà extrait de la fiche de poste)
        if 'salary' in questionnaire_data and not enriched_data.get('salary_range'):
            salary_range = questionnaire_data['salary']
            parsed_salary = self.extract_salary_range(salary_range)
            enriched_data['salary_range'] = parsed_salary
        
        # Avantages (si pas déjà extrait de la fiche de poste)
        if 'benefits' in questionnaire_data and (not enriched_data.get('benefits') or len(enriched_data.get('benefits', [])) == 0):
            benefits_text = questionnaire_data['benefits']
            
            # Convertir le texte en liste d'avantages
            if benefits_text:
                benefits_list = [b.strip() for b in benefits_text.split(',')]
                enriched_data['benefits'] = benefits_list
        
        # Type de contrat
        if 'contract-type' in questionnaire_data:
            enriched_data['contract_details'] = questionnaire_data['contract-type']
        
        logger.info(f"Offre d'emploi enrichie avec les données du questionnaire client: {enriched_data.get('title', 'poste inconnu')}")
        return enriched_data

    def enhanced_match(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Réalise un matching avancé entre un CV et une offre d'emploi, en tenant compte
        des critères enrichis des questionnaires
        
        Args:
            cv_data (Dict): Données CV au format SmartMatch enrichi
            job_data (Dict): Données d'offre d'emploi au format SmartMatch enrichi
            
        Returns:
            Dict: Résultats du matching avancé
        """
        if not cv_data or not job_data:
            logger.warning("Données CV ou offre d'emploi vides")
            return {"error": "Données insuffisantes pour réaliser le matching"}
        
        # Initialiser les scores par catégorie
        category_scores = {
            "skills": 0.0,              # Compétences techniques
            "location": 0.0,            # Proximité géographique
            "experience": 0.0,          # Expérience professionnelle
            "education": 0.0,           # Formation et diplômes
            "work_environment": 0.0,    # Environnement de travail
            "structure_type": 0.0,      # Type de structure
            "sector": 0.0,              # Secteur d'activité
            "salary": 0.0,              # Rémunération
            "availability": 0.0,        # Disponibilité et préavis
            "motivation": 0.0           # Leviers de motivation
        }
        
        # Liste des insights à générer
        insights = []
        
        # 1. Compatibilité des compétences (reprendre le calcul existant)
        skills_score, skills_insights = self._calculate_skills_compatibility(cv_data, job_data)
        category_scores["skills"] = skills_score
        insights.extend(skills_insights)
        
        # 2. Compatibilité géographique avancée
        location_score, location_insights = self._calculate_location_compatibility(cv_data, job_data)
        category_scores["location"] = location_score
        insights.extend(location_insights)
        
        # 3. Expérience professionnelle
        experience_score, experience_insights = self._calculate_experience_compatibility(cv_data, job_data)
        category_scores["experience"] = experience_score
        insights.extend(experience_insights)
        
        # 4. Formation et diplômes
        education_score, education_insights = self._calculate_education_compatibility(cv_data, job_data)
        category_scores["education"] = education_score
        insights.extend(education_insights)
        
        # 5. Environnement de travail
        env_score, env_insights = self._calculate_work_environment_compatibility(cv_data, job_data)
        category_scores["work_environment"] = env_score
        insights.extend(env_insights)
        
        # 6. Type de structure
        structure_score, structure_insights = self._calculate_structure_compatibility(cv_data, job_data)
        category_scores["structure_type"] = structure_score
        insights.extend(structure_insights)
        
        # 7. Secteur d'activité
        sector_score, sector_insights = self._calculate_sector_compatibility(cv_data, job_data)
        category_scores["sector"] = sector_score
        insights.extend(sector_insights)
        
        # 8. Rémunération
        salary_score, salary_insights = self._calculate_salary_compatibility(cv_data, job_data)
        category_scores["salary"] = salary_score
        insights.extend(salary_insights)
        
        # 9. Disponibilité et préavis
        availability_score, availability_insights = self._calculate_availability_compatibility(cv_data, job_data)
        category_scores["availability"] = availability_score
        insights.extend(availability_insights)
        
        # 10. Leviers de motivation
        motivation_score, motivation_insights = self._calculate_motivation_compatibility(cv_data, job_data)
        category_scores["motivation"] = motivation_score
        insights.extend(motivation_insights)
        
        # Calculer le score global (moyenne pondérée des scores par catégorie)
        weights = {
            "skills": 0.3,              # 30% pour les compétences techniques
            "location": 0.15,           # 15% pour la proximité géographique
            "experience": 0.1,          # 10% pour l'expérience
            "education": 0.05,          # 5% pour la formation
            "work_environment": 0.1,    # 10% pour l'environnement de travail
            "structure_type": 0.05,     # 5% pour le type de structure
            "sector": 0.05,             # 5% pour le secteur d'activité
            "salary": 0.1,              # 10% pour la rémunération
            "availability": 0.05,       # 5% pour la disponibilité
            "motivation": 0.05          # 5% pour les leviers de motivation
        }
        
        weighted_sum = sum(category_scores[cat] * weights[cat] for cat in category_scores)
        total_weight = sum(weights.values())
        overall_score = weighted_sum / total_weight
        
        # Construire le résultat du matching
        result = {
            "candidate_id": cv_data.get("id", ""),
            "job_id": job_data.get("id", ""),
            "candidate_name": cv_data.get("name", ""),
            "job_title": job_data.get("title", ""),
            "company": job_data.get("company", ""),
            "overall_score": round(overall_score, 2),
            "category_scores": {cat: round(score, 2) for cat, score in category_scores.items()},
            "insights": insights
        }
        
        logger.info(f"Matching avancé effectué entre {cv_data.get('name', '')} et {job_data.get('title', '')} avec un score de {overall_score:.2f}")
        return result

    def _calculate_skills_compatibility(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calcule la compatibilité des compétences entre un CV et une offre d'emploi
        
        Args:
            cv_data (Dict): Données CV enrichies
            job_data (Dict): Données d'offre d'emploi enrichies
            
        Returns:
            tuple: (score de compatibilité, liste des insights)
        """
        cv_skills = set(cv_data.get('skills', []))
        required_skills = set(job_data.get('required_skills', []))
        preferred_skills = set(job_data.get('preferred_skills', []))
        
        # Si aucune compétence requise, retourner un score par défaut
        if not required_skills:
            return 0.75, [
                {
                    "type": "skills_match",
                    "message": "Impossible d'évaluer les compétences techniques (aucune compétence requise spécifiée)",
                    "score": 0.75,
                    "category": "neutral"
                }
            ]
        
        # Calcul des correspondances
        matched_required = cv_skills.intersection(required_skills)
        matched_preferred = cv_skills.intersection(preferred_skills)
        
        # Calcul des ratios
        required_ratio = len(matched_required) / len(required_skills) if required_skills else 1.0
        preferred_ratio = len(matched_preferred) / len(preferred_skills) if preferred_skills else 1.0
        
        # Score pondéré (les compétences requises ont plus de poids)
        score = (required_ratio * 0.7) + (preferred_ratio * 0.3)
        score = min(1.0, score)  # Plafonner à 1.0
        
        # Génération des insights
        insights = []
        
        if required_ratio >= 0.8:
            category = "strength"
            if required_ratio == 1.0:
                message = "Correspondance parfaite des compétences requises"
            else:
                message = "Excellente correspondance des compétences requises"
        elif required_ratio >= 0.6:
            category = "strength"
            message = "Bonne correspondance des compétences requises"
        elif required_ratio >= 0.4:
            category = "neutral"
            message = "Correspondance moyenne des compétences requises"
        else:
            category = "weakness"
            message = "Faible correspondance des compétences requises"
        
        insights.append({
            "type": "required_skills_match",
            "message": message,
            "score": round(required_ratio, 2),
            "category": category,
            "matched_skills": list(matched_required),
            "missing_skills": list(required_skills - cv_skills)
        })
        
        if preferred_skills:
            if preferred_ratio >= 0.5:
                category = "strength"
                message = "Bonne correspondance des compétences préférées"
            else:
                category = "neutral"
                message = "Correspondance partielle des compétences préférées"
                
            insights.append({
                "type": "preferred_skills_match",
                "message": message,
                "score": round(preferred_ratio, 2),
                "category": category,
                "matched_skills": list(matched_preferred)
            })
        
        return score, insights

    def _calculate_location_compatibility(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calcule la compatibilité géographique entre un CV et une offre d'emploi
        en tenant compte des modes de transport et temps de trajet
        
        Args:
            cv_data (Dict): Données CV enrichies
            job_data (Dict): Données d'offre d'emploi enrichies
            
        Returns:
            tuple: (score de compatibilité, liste des insights)
        """
        # Récupérer les coordonnées
        cv_location = cv_data.get('location', '')
        job_location = job_data.get('location', '')
        
        # Par défaut, score moyen si les coordonnées ne sont pas disponibles
        if not cv_location or not job_location:
            return 0.5, [
                {
                    "type": "location_match",
                    "message": "Impossible d'évaluer la distance (coordonnées manquantes)",
                    "score": 0.5,
                    "category": "neutral"
                }
            ]
        
        # Coordonnées au format "latitude,longitude"
        try:
            cv_lat, cv_lng = map(float, cv_location.split(','))
            job_lat, job_lng = map(float, job_location.split(','))
        except (ValueError, TypeError):
            return 0.5, [
                {
                    "type": "location_match",
                    "message": "Format de coordonnées invalide",
                    "score": 0.5,
                    "category": "neutral"
                }
            ]
        
        # Calculer la distance à vol d'oiseau (formule de Haversine)
        
        def haversine(lat1, lng1, lat2, lng2):
            """Calcule la distance en km entre deux points en utilisant la formule de Haversine"""
            # Convertir degrés en radians
            lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])
            
            # Formule de Haversine
            dlat = lat2 - lat1
            dlng = lng2 - lng1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
            c = 2 * math.asin(math.sqrt(a))
            r = 6371  # Rayon de la Terre en km
            return c * r
        
        distance_km = haversine(cv_lat, cv_lng, job_lat, job_lng)
        
        # Estimer les temps de trajet selon les modes de transport
        # En réalité, il faudrait utiliser une API comme Google Maps Direction
        # Ces valeurs sont des approximations
        transport_speeds = {
            'public-transport': 25,  # km/h (vitesse moyenne incluant les arrêts)
            'vehicle': 40,           # km/h (vitesse moyenne urbaine/périurbaine)
            'bike': 15,              # km/h
            'walking': 5             # km/h
        }
        
        # Obtenir les modes de transport du candidat
        mobility_data = cv_data.get('mobility', {})
        transport_methods = mobility_data.get('transport_methods', [])
        commute_times = mobility_data.get('commute_times', {})
        
        # Si aucun mode de transport spécifié, mode par défaut
        if not transport_methods:
            transport_methods = ['public-transport']
        
        # Calculer les temps de trajet estimés pour chaque mode et vérifier si acceptables
        transport_insights = []
        acceptable_methods = []
        acceptable_times = []
        
        for method in transport_methods:
            if method in transport_speeds:
                # Temps de trajet estimé en minutes
                est_time_minutes = (distance_km / transport_speeds[method]) * 60
                
                # Temps maximum acceptable pour ce mode de transport
                max_acceptable = commute_times.get(method, 45)  # 45 min par défaut
                
                is_acceptable = est_time_minutes <= max_acceptable
                
                if is_acceptable:
                    acceptable_methods.append(method)
                    acceptable_times.append(est_time_minutes)
                
                transport_insights.append({
                    "transport_method": method,
                    "estimated_time": round(est_time_minutes),
                    "max_acceptable": max_acceptable,
                    "is_acceptable": is_acceptable
                })
        
        # Vérifier si au moins un mode de transport est dans les limites acceptables
        if acceptable_methods:
            # Prendre le temps le plus court parmi les modes acceptables
            best_time = min(acceptable_times)
            
            # Score basé sur le rapport entre le meilleur temps et le temps maximum acceptable
            # Plus le trajet est court par rapport au maximum acceptable, meilleur est le score
            best_method_idx = acceptable_times.index(best_time)
            best_method = acceptable_methods[best_method_idx]
            max_time = commute_times.get(best_method, 45)
            
            # Plus le ratio est petit, meilleur est le score
            time_ratio = best_time / max_time
            score = 1.0 - min(1.0, time_ratio * 0.8)  # 1.0 si temps = 0, 0.2 si temps = max
            
            category = "strength" if score > 0.7 else "neutral"
            message = f"Trajet de {round(best_time)} min en {self._translate_transport_method(best_method)}"
            
        else:
            # Aucun mode de transport dans les limites acceptables
            score = 0.2
            category = "weakness"
            message = "Tous les temps de trajet dépassent les limites acceptables"
        
        # Synthèse pour l'insight principal
        location_insight = {
            "type": "location_match",
            "message": message,
            "score": round(score, 2),
            "category": category,
            "distance_km": round(distance_km, 1),
            "transport_details": transport_insights
        }
        
        return score, [location_insight]

    def _translate_transport_method(self, method):
        """Traduit le code du mode de transport en texte lisible"""
        translations = {
            'public-transport': 'transports en commun',
            'vehicle': 'véhicule personnel',
            'bike': 'vélo',
            'walking': 'marche à pied'
        }
        return translations.get(method, method)

    def _calculate_experience_compatibility(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calcule la compatibilité d'expérience entre un CV et une offre d'emploi
        
        Args:
            cv_data (Dict): Données CV enrichies
            job_data (Dict): Données d'offre d'emploi enrichies
            
        Returns:
            tuple: (score de compatibilité, liste des insights)
        """
        # Récupérer les années d'expérience
        cv_experience = cv_data.get('years_of_experience', 0)
        job_min_exp = job_data.get('min_years_of_experience', 0)
        job_max_exp = job_data.get('max_years_of_experience', job_min_exp + 5)
        
        # Si l'expérience du candidat est dans la fourchette demandée
        if cv_experience >= job_min_exp and cv_experience <= job_max_exp:
            # Score optimal
            score = 1.0
            category = "strength"
            
            if cv_experience == job_min_exp:
                message = f"Expérience correspondant exactement au minimum requis ({job_min_exp} ans)"
            elif cv_experience > job_min_exp and cv_experience < job_max_exp:
                message = f"Expérience parfaitement dans la fourchette requise ({job_min_exp}-{job_max_exp} ans)"
            else:
                message = f"Expérience correspondant au maximum requis ({job_max_exp} ans)"
        
        # Si l'expérience est légèrement en dessous du minimum
        elif cv_experience >= job_min_exp * 0.7:
            # Score proportionnel
            score = 0.7
            category = "neutral"
            message = f"Expérience légèrement inférieure au minimum requis ({cv_experience} ans vs {job_min_exp} ans)"
        
        # Si l'expérience est nettement en dessous du minimum
        elif cv_experience < job_min_exp * 0.7:
            # Score faible
            score = 0.3
            category = "weakness"
            message = f"Expérience significativement inférieure au minimum requis ({cv_experience} ans vs {job_min_exp} ans)"
        
        # Si l'expérience dépasse largement le maximum
        elif cv_experience > job_max_exp * 1.5:
            # Score moyen (peut être surqualifié)
            score = 0.5
            category = "neutral"
            message = f"Candidat potentiellement surqualifié ({cv_experience} ans vs max {job_max_exp} ans)"
        
        # Si l'expérience dépasse un peu le maximum
        else:
            # Score bon mais pas optimal
            score = 0.8
            category = "strength"
            message = f"Expérience supérieure au maximum requis ({cv_experience} ans vs max {job_max_exp} ans)"
        
        experience_insight = {
            "type": "experience_match",
            "message": message,
            "score": round(score, 2),
            "category": category,
            "candidate_experience": cv_experience,
            "job_required_min": job_min_exp,
            "job_required_max": job_max_exp
        }
        
        return score, [experience_insight]

    def _calculate_education_compatibility(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calcule la compatibilité du niveau d'éducation entre un CV et une offre d'emploi
        
        Args:
            cv_data (Dict): Données CV enrichies
            job_data (Dict): Données d'offre d'emploi enrichies
            
        Returns:
            tuple: (score de compatibilité, liste des insights)
        """
        # Récupérer les niveaux d'éducation
        cv_education = cv_data.get('education_level', 'bachelor')
        job_education = job_data.get('required_education', 'bachelor')
        
        # Définir une hiérarchie de niveaux d'éducation
        education_levels = {
            'high_school': 1,
            'associate': 2,
            'bachelor': 3,
            'master': 4,
            'phd': 5
        }
        
        # Si le niveau d'éducation n'est pas reconnu, utiliser "bachelor" par défaut
        cv_level = education_levels.get(cv_education, 3)
        job_level = education_levels.get(job_education, 3)
        
        # Si le candidat a un niveau supérieur ou égal au niveau requis
        if cv_level >= job_level:
            # Score optimal
            score = 1.0
            category = "strength"
            
            if cv_level == job_level:
                message = f"Niveau d'éducation correspond exactement au niveau requis"
            else:
                message = f"Niveau d'éducation supérieur au niveau requis"
        
        # Si le candidat a un niveau inférieur d'un seul cran
        elif cv_level == job_level - 1:
            # Score moyen
            score = 0.6
            category = "neutral"
            message = f"Niveau d'éducation légèrement inférieur au niveau requis"
        
        # Si le candidat a un niveau nettement inférieur
        else:
            # Score faible
            score = 0.3
            category = "weakness"
            message = f"Niveau d'éducation significativement inférieur au niveau requis"
        
        education_insight = {
            "type": "education_match",
            "message": message,
            "score": round(score, 2),
            "category": category,
            "candidate_education": cv_education,
            "job_required_education": job_education
        }
        
        return score, [education_insight]

    def _calculate_work_environment_compatibility(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calcule la compatibilité de l'environnement de travail entre un CV et une offre d'emploi
        
        Args:
            cv_data (Dict): Données CV enrichies
            job_data (Dict): Données d'offre d'emploi enrichies
            
        Returns:
            tuple: (score de compatibilité, liste des insights)
        """
        # Récupérer les préférences d'environnement de travail
        cv_preference = cv_data.get('work_environment_preference', 'no-preference')
        job_environment = job_data.get('work_environment', 'office')
        
        # Si le candidat n'a pas de préférence
        if cv_preference == 'no-preference':
            score = 1.0
            category = "strength"
            message = "Pas de préférence particulière pour l'environnement de travail"
        
        # Si les préférences correspondent
        elif cv_preference == job_environment:
            score = 1.0
            category = "strength"
            message = f"Environnement de travail correspond parfaitement aux préférences ({job_environment})"
        
        # Si les préférences ne correspondent pas
        else:
            score = 0.4
            category = "weakness"
            message = f"Environnement de travail ({job_environment}) ne correspond pas aux préférences ({cv_preference})"
        
        # Vérifier le travail à distance
        cv_remote = cv_data.get('remote_work', False)
        job_remote = job_data.get('offers_remote', False)
        
        insights = [
            {
                "type": "work_environment_match",
                "message": message,
                "score": round(score, 2),
                "category": category,
                "candidate_preference": cv_preference,
                "job_environment": job_environment
            }
        ]
        
        # Ajouter un insight sur le travail à distance si pertinent
        if cv_remote and job_remote:
            insights.append({
                "type": "remote_work_match",
                "message": "Possibilité de travail à distance correspondant aux préférences",
                "score": 1.0,
                "category": "strength"
            })
        elif cv_remote and not job_remote:
            insights.append({
                "type": "remote_work_match",
                "message": "Pas de possibilité de travail à distance malgré la préférence",
                "score": 0.3,
                "category": "weakness"
            })
            # Impacte légèrement le score global
            score = max(0.3, score - 0.2)
        
        return score, insights

    def _calculate_structure_compatibility(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calcule la compatibilité du type de structure entre un CV et une offre d'emploi
        
        Args:
            cv_data (Dict): Données CV enrichies
            job_data (Dict): Données d'offre d'emploi enrichies
            
        Returns:
            tuple: (score de compatibilité, liste des insights)
        """
        # Récupérer les préférences de type de structure
        cv_structures = cv_data.get('preferred_structure_types', [])
        job_structure = job_data.get('company_size', 'pme')
        
        # Si le candidat a coché "pas d'importance" ou n'a pas de préférence
        if 'no-preference' in cv_structures or not cv_structures:
            score = 1.0
            category = "strength"
            message = "Pas de préférence particulière pour le type de structure"
        
        # Si le type de structure de l'offre correspond à une des préférences
        elif job_structure in cv_structures:
            score = 1.0
            category = "strength"
            message = f"Type de structure ({job_structure}) correspond parfaitement aux préférences"
        
        # Si le type de structure ne correspond pas aux préférences
        else:
            score = 0.4
            category = "weakness"
            message = f"Type de structure ({job_structure}) ne correspond pas aux préférences"
        
        structure_insight = {
            "type": "structure_match",
            "message": message,
            "score": round(score, 2),
            "category": category,
            "candidate_preferences": cv_structures,
            "job_structure": job_structure
        }
        
        return score, [structure_insight]

    def _calculate_sector_compatibility(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calcule la compatibilité du secteur d'activité entre un CV et une offre d'emploi
        
        Args:
            cv_data (Dict): Données CV enrichies
            job_data (Dict): Données d'offre d'emploi enrichies
            
        Returns:
            tuple: (score de compatibilité, liste des insights)
        """
        # Récupérer les préférences sectorielles
        has_sector_preference = cv_data.get('has_sector_preference', False)
        cv_sectors = cv_data.get('preferred_sectors', [])
        prohibited_sectors = cv_data.get('prohibited_sectors', [])
        
        # Récupérer le secteur de l'offre
        job_sector = job_data.get('industry', '')
        requires_knowledge = job_data.get('requires_sector_knowledge', False)
        
        # Initialiser les insights
        insights = []
        
        # Si le candidat n'a pas de préférence sectorielle
        if not has_sector_preference:
            sector_score = 1.0
            sector_category = "strength"
            sector_message = "Pas de préférence sectorielle particulière"
        
        # Si le secteur de l'offre correspond à une des préférences
        elif job_sector in cv_sectors:
            sector_score = 1.0
            sector_category = "strength"
            sector_message = f"Secteur d'activité ({job_sector}) correspond parfaitement aux préférences"
        
        # Si le secteur ne correspond pas aux préférences mais n'est pas prohibé
        elif job_sector not in prohibited_sectors:
            sector_score = 0.7
            sector_category = "neutral"
            sector_message = f"Secteur d'activité ({job_sector}) ne figure pas dans les préférences"
        
        # Si le secteur est prohibé
        else:
            sector_score = 0.0
            sector_category = "dealbreaker"
            sector_message = f"Secteur d'activité ({job_sector}) figure dans les secteurs à éviter"
        
        insights.append({
            "type": "sector_preference_match",
            "message": sector_message,
            "score": round(sector_score, 2),
            "category": sector_category,
            "candidate_preferred_sectors": cv_sectors,
            "job_sector": job_sector
        })
        
        # Vérifier si l'offre requiert une connaissance du secteur
        if requires_knowledge:
            # Le candidat a-t-il de l'expérience dans ce secteur ?
            sector_experience = job_sector in cv_sectors
            
            if sector_experience:
                knowledge_score = 1.0
                knowledge_category = "strength"
                knowledge_message = "Connaissance du secteur requise et présente"
            else:
                knowledge_score = 0.3
                knowledge_category = "weakness"
                knowledge_message = "Connaissance du secteur requise mais absente"
            
            insights.append({
                "type": "sector_knowledge_match",
                "message": knowledge_message,
                "score": round(knowledge_score, 2),
                "category": knowledge_category,
                "requires_knowledge": requires_knowledge,
                "has_experience": sector_experience
            })
            
            # Ajuster le score global en tenant compte des deux aspects
            score = (sector_score * 0.6) + (knowledge_score * 0.4)
        else:
            # Si la connaissance du secteur n'est pas requise, seule la préférence compte
            score = sector_score
        
        return score, insights

    def _calculate_salary_compatibility(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calcule la compatibilité salariale entre un CV et une offre d'emploi
        
        Args:
            cv_data (Dict): Données CV enrichies
            job_data (Dict): Données d'offre d'emploi enrichies
            
        Returns:
            tuple: (score de compatibilité, liste des insights)
        """
        # Récupérer les fourchettes de salaire
        cv_salary = cv_data.get('salary_expectation', 0)
        cv_range = cv_data.get('salary_expectation_range', {})
        
        if isinstance(cv_range, dict) and 'min' in cv_range and 'max' in cv_range:
            cv_min = cv_range.get('min', 0)
            cv_max = cv_range.get('max', 0)
        else:
            # Si pas de fourchette, utiliser ±10% autour de l'attente
            cv_min = int(cv_salary * 0.9) if cv_salary else 0
            cv_max = int(cv_salary * 1.1) if cv_salary else 0
        
        # Salaire de l'offre
        job_range = job_data.get('salary_range', {})
        
        if isinstance(job_range, dict) and 'min' in job_range and 'max' in job_range:
            job_min = job_range.get('min', 0)
            job_max = job_range.get('max', 0)
        else:
            job_min = 0
            job_max = 0
        
        # Si les informations de salaire ne sont pas disponibles
        if not cv_min or not job_min:
            return 0.5, [
                {
                    "type": "salary_match",
                    "message": "Informations salariales insuffisantes pour l'évaluation",
                    "score": 0.5,
                    "category": "neutral"
                }
            ]
        
        # Déterminer le chevauchement des fourchettes
        overlap_min = max(cv_min, job_min)
        overlap_max = min(cv_max, job_max)
        
        # S'il y a un chevauchement
        if overlap_min <= overlap_max:
            # Calculer le ratio de chevauchement par rapport à la fourchette du candidat
            cv_range_size = cv_max - cv_min
            overlap_size = overlap_max - overlap_min
            
            if cv_range_size > 0:
                overlap_ratio = overlap_size / cv_range_size
            else:
                overlap_ratio = 1.0 if overlap_size > 0 else 0.0
            
            # Score basé sur le chevauchement
            score = min(1.0, overlap_ratio * 1.5)  # Bonus pour le chevauchement
            
            # Message selon le niveau de chevauchement
            if overlap_ratio > 0.8:
                category = "strength"
                message = "Attentes salariales parfaitement alignées avec l'offre"
            elif overlap_ratio > 0.5:
                category = "strength"
                message = "Bonne correspondance des attentes salariales"
            else:
                category = "neutral"
                message = "Chevauchement partiel des attentes salariales"
        
        # Si l'attente min du candidat > max de l'offre
        elif cv_min > job_max:
            # Calculer l'écart en pourcentage
            gap_percent = (cv_min - job_max) / job_max
            
            # Score inverse à l'écart (plus l'écart est grand, plus le score est bas)
            score = max(0.0, 1.0 - (gap_percent * 2))
            
            # Message selon l'ampleur de l'écart
            if gap_percent < 0.1:
                category = "neutral"
                message = "Attentes salariales légèrement supérieures à l'offre"
            elif gap_percent < 0.2:
                category = "weakness"
                message = "Attentes salariales sensiblement supérieures à l'offre"
            else:
                category = "dealbreaker"
                message = "Attentes salariales significativement supérieures à l'offre"
        
        # Si le max du candidat < min de l'offre (candidat demanderait moins que le minimum offert)
        else:
            # C'est positif pour l'entreprise mais peut indiquer une sous-estimation du candidat
            gap_percent = (job_min - cv_max) / cv_max
            
            if gap_percent < 0.15:
                score = 0.9
                category = "strength"
                message = "Attentes salariales légèrement inférieures au minimum offert"
            else:
                score = 0.7
                category = "neutral"
                message = "Attentes salariales nettement inférieures au minimum offert"
        
        salary_insight = {
            "type": "salary_match",
            "message": message,
            "score": round(score, 2),
            "category": category,
            "candidate_range": {"min": cv_min, "max": cv_max},
            "job_range": {"min": job_min, "max": job_max}
        }
        
        return score, [salary_insight]

    def _calculate_availability_compatibility(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calcule la compatibilité des disponibilités entre un CV et une offre d'emploi
        
        Args:
            cv_data (Dict): Données CV enrichies
            job_data (Dict): Données d'offre d'emploi enrichies
            
        Returns:
            tuple: (score de compatibilité, liste des insights)
        """
        # Récupérer les informations de disponibilité
        cv_availability_days = cv_data.get('availability_days', 0)
        job_delay_days = job_data.get('recruitment_delay_days', 30)  # 30 jours par défaut
        
        # Récupérer les informations de préavis
        currently_employed = cv_data.get('currently_employed', False)
        notice_period_days = cv_data.get('notice_period_days', 0)
        notice_negotiable = cv_data.get('notice_negotiable', False)
        
        # L'entreprise peut-elle gérer un préavis ?
        job_can_handle_notice = job_data.get('can_handle_notice', True)
        job_max_notice = job_data.get('max_notice_period_days', 90)  # 90 jours par défaut
        
        # Si le candidat est disponible avant le délai de recrutement
        if cv_availability_days <= job_delay_days:
            availability_score = 1.0
            availability_category = "strength"
            availability_message = "Disponibilité idéale par rapport au délai de recrutement"
        
        # Si le candidat est disponible peu après le délai
        elif cv_availability_days <= job_delay_days * 1.5:
            availability_score = 0.8
            availability_category = "neutral"
            availability_message = "Disponibilité légèrement retardée par rapport au délai souhaité"
        
        # Si le candidat est disponible bien après le délai
        else:
            availability_score = 0.4
            availability_category = "weakness"
            availability_message = "Disponibilité significativement retardée par rapport au délai souhaité"
        
        insights = [
            {
                "type": "availability_match",
                "message": availability_message,
                "score": round(availability_score, 2),
                "category": availability_category,
                "candidate_availability_days": cv_availability_days,
                "job_delay_days": job_delay_days
            }
        ]
        
        # Si le candidat est en poste avec un préavis
        if currently_employed and notice_period_days > 0:
            # Si l'entreprise ne peut pas gérer de préavis
            if not job_can_handle_notice:
                notice_score = 0.0
                notice_category = "dealbreaker"
                notice_message = "L'entreprise ne peut pas gérer de préavis, mais le candidat en a un"
            
            # Si le préavis est trop long
            elif notice_period_days > job_max_notice:
                # Si le préavis est négociable
                if notice_negotiable:
                    notice_score = 0.5
                    notice_category = "neutral"
                    notice_message = "Préavis trop long mais négociable"
                else:
                    notice_score = 0.2
                    notice_category = "weakness"
                    notice_message = "Préavis trop long et non négociable"
            
            # Si le préavis est acceptable
            else:
                notice_score = 0.9
                notice_category = "neutral"
                notice_message = "Préavis dans les limites acceptables"
            
            insights.append({
                "type": "notice_period_match",
                "message": notice_message,
                "score": round(notice_score, 2),
                "category": notice_category,
                "candidate_notice_days": notice_period_days,
                "job_max_notice_days": job_max_notice,
                "notice_negotiable": notice_negotiable
            })
            
            # Score global combinant disponibilité et préavis
            score = (availability_score * 0.6) + (notice_score * 0.4)
        else:
            # Si pas de préavis à considérer, seule la disponibilité compte
            score = availability_score
        
        return score, insights

    def _calculate_motivation_compatibility(self, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calcule la compatibilité des leviers de motivation entre un CV et une offre d'emploi
        
        Args:
            cv_data (Dict): Données CV enrichies
            job_data (Dict): Données d'offre d'emploi enrichies
            
        Returns:
            tuple: (score de compatibilité, liste des insights)
        """
        # Récupérer les leviers de motivation du candidat
        motivations = cv_data.get('motivations', [])
        
        # Si aucune motivation n'est spécifiée
        if not motivations:
            return 0.5, [
                {
                    "type": "motivation_match",
                    "message": "Pas d'information sur les leviers de motivation",
                    "score": 0.5,
                    "category": "neutral"
                }
            ]
        
        # Identifier les points forts de l'offre qui peuvent correspondre aux motivations
        motivation_matches = {
            'remuneration': {
                'job_attribute': 'salary_range', 
                'job_attribute2': 'benefits',
                'strength': 0.0, 
                'message': ""
            },
            'evolution': {
                'job_attribute': 'evolution_perspectives', 
                'strength': 0.0, 
                'message': ""
            },
            'flexibility': {
                'job_attribute': 'offers_remote', 
                'job_attribute2': 'benefits',
                'strength': 0.0, 
                'message': ""
            },
            'location': {
                'job_attribute': 'location', 
                'strength': 0.0, 
                'message': ""
            },
            'other': {
                'job_attribute': '', 
                'strength': 0.0, 
                'message': ""
            }
        }
        
        # Analyser les points forts de l'offre pour chaque levier de motivation
        
        # Rémunération
        if 'salary_range' in job_data and job_data['salary_range'].get('min', 0) > 0:
            salary_min = job_data['salary_range'].get('min', 0)
            cv_expectation = cv_data.get('salary_expectation', 0)
            
            if cv_expectation > 0 and salary_min >= cv_expectation:
                motivation_matches['remuneration']['strength'] = 1.0
                motivation_matches['remuneration']['message'] = "Salaire proposé atteint ou dépasse les attentes"
            elif cv_expectation > 0 and salary_min >= cv_expectation * 0.9:
                motivation_matches['remuneration']['strength'] = 0.8
                motivation_matches['remuneration']['message'] = "Salaire proposé proche des attentes"
            else:
                motivation_matches['remuneration']['strength'] = 0.5
                motivation_matches['remuneration']['message'] = "Fourchette de salaire disponible"
        
        # Vérifier les avantages pour la rémunération et la flexibilité
        if 'benefits' in job_data and job_data['benefits']:
            benefits = job_data['benefits']
            
            # Avantages liés à la rémunération
            remuneration_keywords = ['13e mois', 'prime', 'bonus', 'intéressement', 'participation', 'mutuelle']
            for keyword in remuneration_keywords:
                if any(keyword.lower() in benefit.lower() for benefit in benefits):
                    motivation_matches['remuneration']['strength'] = max(motivation_matches['remuneration']['strength'], 0.7)
                    motivation_matches['remuneration']['message'] = "Avantages financiers inclus dans le package"
            
            # Avantages liés à la flexibilité
            flexibility_keywords = ['télétravail', 'remote', 'horaires flexibles', 'rtt', 'flexible']
            for keyword in flexibility_keywords:
                if any(keyword.lower() in benefit.lower() for benefit in benefits):
                    motivation_matches['flexibility']['strength'] = max(motivation_matches['flexibility']['strength'], 0.9)
                    motivation_matches['flexibility']['message'] = "Flexibilité de travail mentionnée dans les avantages"
        
        # Évolution
        if 'evolution_perspectives' in job_data and job_data['evolution_perspectives']:
            motivation_matches['evolution']['strength'] = 0.9
            motivation_matches['evolution']['message'] = "Perspectives d'évolution mentionnées dans l'offre"
        
        # Flexibilité
        if 'offers_remote' in job_data and job_data['offers_remote']:
            motivation_matches['flexibility']['strength'] = max(motivation_matches['flexibility']['strength'], 0.8)
            motivation_matches['flexibility']['message'] = "Possibilité de télétravail mentionnée"
        
        # Localisation (déjà évaluée dans _calculate_location_compatibility)
        location_score, _ = self._calculate_location_compatibility(cv_data, job_data)
        motivation_matches['location']['strength'] = location_score
        
        if location_score > 0.8:
            motivation_matches['location']['message'] = "Localisation idéale par rapport aux préférences"
        elif location_score > 0.6:
            motivation_matches['location']['message'] = "Bonne localisation par rapport aux préférences"
        else:
            motivation_matches['location']['message'] = "Localisation correcte par rapport aux préférences"
        
        # Calculer le score en fonction des priorités du candidat
        weighted_scores = []
        insights = []
        
        # Attribuer des poids en fonction de l'ordre des motivations
        for idx, motivation in enumerate(motivations[:3]):  # Ne considérer que les 3 premières motivations
            weight = 1.0 - (idx * 0.25)  # 1.0, 0.75, 0.5 pour les 3 premières
            
            if motivation in motivation_matches:
                match_data = motivation_matches[motivation]
                strength = match_data['strength']
                weighted_score = strength * weight
                
                # Préparer l'insight pour cette motivation
                motivation_display = motivation
                if motivation == 'other' and 'other_motivation' in cv_data:
                    motivation_display = cv_data['other_motivation']
                
                if strength > 0.7:
                    category = "strength"
                elif strength > 0.4:
                    category = "neutral"
                else:
                    category = "weakness"
                
                insights.append({
                    "type": f"motivation_{motivation}_match",
                    "message": match_data['message'] or f"Levier de motivation : {motivation_display}",
                    "score": round(strength, 2),
                    "category": category,
                    "priority": idx + 1
                })
                
                weighted_scores.append(weighted_score)
        
        # Calculer le score global (moyenne des scores pondérés)
        if weighted_scores:
            score = sum(weighted_scores) / sum(1.0 - (i * 0.25) for i in range(min(3, len(motivations))))
        else:
            score = 0.5
        
        # Ajouter un insight de synthèse
        if score > 0.8:
            main_message = "Excellente correspondance avec les leviers de motivation prioritaires"
        elif score > 0.6:
            main_message = "Bonne correspondance avec les leviers de motivation prioritaires"
        elif score > 0.4:
            main_message = "Correspondance moyenne avec les leviers de motivation"
        else:
            main_message = "Faible correspondance avec les leviers de motivation prioritaires"
        
        main_category = "strength" if score > 0.6 else "neutral" if score > 0.4 else "weakness"
        
        insights.insert(0, {
            "type": "motivation_match_summary",
            "message": main_message,
            "score": round(score, 2),
            "category": main_category,
            "top_motivations": motivations[:3]
        })
        
        return score, insights


# Exemple d'utilisation
if __name__ == "__main__":
    # Créer l'adaptateur
    adapter = SmartMatchDataAdapter()
    
    # Exemple de données CV issues du CV Parser
    cv_data = {
        "nom": "Dupont",
        "prenom": "Jean",
        "poste": "Développeur Python Senior",
        "competences": ["Python", "Django", "Flask", "REST API"],
        "logiciels": ["Git", "Docker", "VS Code", "PyCharm"],
        "soft_skills": ["Communication", "Travail d'équipe", "Autonomie"],
        "email": "jean.dupont@example.com",
        "telephone": "06 12 34 56 78",
        "adresse": "123 rue de Paris, 75001 Paris"
    }
    
    # Exemple de données Job issues du Job Parser
    job_data = {
        "title": "Développeur Python Senior",
        "company": "Acme Inc.",
        "location": "Paris",
        "contract_type": "CDI",
        "skills": ["Python", "Django", "Flask", "SQL", "Git", "Docker"],
        "experience": "5 ans d'expérience en développement Python",
        "education": "Diplôme d'ingénieur ou équivalent",
        "salary": "45K - 55K",
        "responsibilities": [
            "Développer des applications web avec Django",
            "Maintenir les API REST existantes",
            "Participer à la conception technique"
        ],
        "benefits": [
            "Télétravail partiel",
            "Mutuelle d'entreprise",
            "Tickets restaurant"
        ]
    }
    
    # Convertir au format SmartMatch
    cv_smartmatch = adapter.cv_to_smartmatch_format(cv_data, "cv_123")
    job_smartmatch = adapter.job_to_smartmatch_format(job_data, "job_456")
    
    # Afficher les résultats
    print("CV au format SmartMatch:")
    print(json.dumps(cv_smartmatch, indent=2, ensure_ascii=False))
    
    print("\nJob au format SmartMatch:")
    print(json.dumps(job_smartmatch, indent=2, ensure_ascii=False))
