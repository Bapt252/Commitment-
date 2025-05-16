"""
SmartMatch Data Adapter - Module d'adaptation de données pour SmartMatch
-----------------------------------------------------------------------
Ce module permet d'adapter les données entre les formats de sortie du CV Parser
et du Job Parser vers le format attendu par l'algorithme SmartMatch.

Auteur: Claude
Date: 16/05/2025
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Union
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
