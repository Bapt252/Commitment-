#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptateur de données pour SuperSmartMatch
Standardise les formats de données entre les différents algorithmes
"""

import logging
from typing import Dict, List, Any, Optional
import re

logger = logging.getLogger(__name__)

class DataAdapter:
    """
    Adaptateur pour standardiser les formats de données
    entre votre front-end et les algorithmes de matching
    """
    
    def __init__(self):
        self.field_mappings = self._initialize_field_mappings()
        self.validation_rules = self._initialize_validation_rules()
    
    def _initialize_field_mappings(self) -> Dict[str, Dict[str, str]]:
        """Initialise les mappings de champs pour différents formats"""
        return {
            "candidate": {
                # Front-end → Standard
                "nom": "name",
                "prenom": "first_name", 
                "email": "email",
                "telephone": "phone",
                "adresse": "location",
                "localisation": "location",
                "competences": "skills",
                "skills": "skills",
                "annees_experience": "years_experience",
                "experience": "years_experience",
                "formation": "education",
                "diplome": "education",
                "salaire_souhaite": "salary_expectation",
                "salaire_min": "salary_expectation",
                "contrats_recherches": "contract_types",
                "type_contrat_recherche": "contract_types",
                "disponibilite": "availability",
                "date_disponibilite": "availability",
                "mobilite": "remote_preference",
                "remote_preference": "remote_preference",
                "soft_skills": "soft_skills",
                "competences_comportementales": "soft_skills",
                "langues": "languages",
                "niveau_etudes": "education_level",
                "secteur_activite": "industry_preference",
                "preferences_culture": "culture_preferences",
                "valeurs_importantes": "important_values",
                "criteres_importants": "important_criteria"
            },
            "job": {
                # Front-end → Standard
                "titre": "title",
                "title": "title",
                "poste": "title",
                "entreprise": "company",
                "company": "company",
                "societe": "company",
                "competences": "required_skills",
                "skills": "required_skills",
                "competences_requises": "required_skills",
                "localisation": "location",
                "lieu": "location",
                "adresse": "location",
                "type_contrat": "contract_type",
                "contrat": "contract_type",
                "salaire": "salary_range",
                "remuneration": "salary_range",
                "experience_requise": "required_experience",
                "experience_minimum": "required_experience",
                "annees_experience": "required_experience",
                "description": "description",
                "mission": "description",
                "responsabilites": "responsibilities",
                "avantages": "benefits",
                "politique_remote": "remote_policy",
                "teletravail": "remote_policy",
                "remote_policy": "remote_policy",
                "soft_skills": "desired_soft_skills",
                "competences_comportementales": "desired_soft_skills",
                "culture_entreprise": "company_culture",
                "valeurs": "company_values",
                "taille_entreprise": "company_size",
                "secteur": "industry",
                "date_publication": "published_date",
                "date_limite": "deadline"
            }
        }
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialise les règles de validation"""
        return {
            "candidate": {
                "required_fields": ["skills"],
                "optional_fields": ["name", "location", "years_experience", "salary_expectation"],
                "field_types": {
                    "skills": list,
                    "years_experience": (int, float),
                    "salary_expectation": (int, float),
                    "contract_types": list,
                    "soft_skills": list
                }
            },
            "job": {
                "required_fields": ["title", "required_skills"],
                "optional_fields": ["company", "location", "salary_range", "contract_type"],
                "field_types": {
                    "required_skills": list,
                    "required_experience": (int, float),
                    "desired_soft_skills": list
                }
            }
        }
    
    def adapt_candidate(self, candidate_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapte les données candidat au format standard
        
        Args:
            candidate_data: Données candidat du front-end
            
        Returns:
            Données candidat standardisées
        """
        if not candidate_data:
            raise ValueError("Données candidat vides")
        
        # Mapping des champs
        adapted = self._map_fields(candidate_data, "candidate")
        
        # Nettoyage et normalisation
        adapted = self._normalize_candidate_data(adapted)
        
        # Validation
        self._validate_data(adapted, "candidate")
        
        logger.debug(f"Candidat adapté: {len(adapted)} champs")
        
        return adapted
    
    def adapt_jobs(self, jobs_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Adapte les données d'offres au format standard
        
        Args:
            jobs_data: Liste des offres du front-end
            
        Returns:
            Liste des offres standardisées
        """
        if not jobs_data:
            raise ValueError("Liste d'offres vide")
        
        adapted_jobs = []
        
        for i, job in enumerate(jobs_data):
            try:
                # Mapping des champs
                adapted = self._map_fields(job, "job")
                
                # Nettoyage et normalisation
                adapted = self._normalize_job_data(adapted)
                
                # Validation
                self._validate_data(adapted, "job")
                
                # Ajouter un ID si manquant
                if 'id' not in adapted:
                    adapted['id'] = job.get('id', f'job_{i}')
                
                adapted_jobs.append(adapted)
                
            except Exception as e:
                logger.warning(f"Erreur adaptation offre {i}: {e}")
                # Continuer avec les autres offres
                continue
        
        logger.debug(f"{len(adapted_jobs)} offres adaptées sur {len(jobs_data)}")
        
        return adapted_jobs
    
    def _map_fields(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """
        Mappe les champs selon les règles définies
        
        Args:
            data: Données à mapper
            data_type: Type de données ("candidate" ou "job")
            
        Returns:
            Données avec champs mappés
        """
        mappings = self.field_mappings.get(data_type, {})
        mapped_data = {}
        
        for original_field, value in data.items():
            # Utiliser le mapping si disponible, sinon garder le nom original
            standard_field = mappings.get(original_field, original_field)
            mapped_data[standard_field] = value
        
        return mapped_data
    
    def _normalize_candidate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalise les données candidat
        
        Args:
            data: Données candidat mappées
            
        Returns:
            Données normalisées
        """
        normalized = data.copy()
        
        # Normaliser les compétences
        if 'skills' in normalized:
            normalized['skills'] = self._normalize_skills(normalized['skills'])
        
        # Normaliser l'expérience
        if 'years_experience' in normalized:
            normalized['years_experience'] = self._normalize_experience(normalized['years_experience'])
        
        # Normaliser le salaire
        if 'salary_expectation' in normalized:
            normalized['salary_expectation'] = self._normalize_salary(normalized['salary_expectation'])
        
        # Normaliser les types de contrat
        if 'contract_types' in normalized:
            normalized['contract_types'] = self._normalize_contract_types(normalized['contract_types'])
        
        # Normaliser la localisation
        if 'location' in normalized:
            normalized['location'] = self._normalize_location(normalized['location'])
        
        # Normaliser la mobilité/remote
        if 'remote_preference' in normalized:
            normalized['remote_preference'] = self._normalize_remote_preference(normalized['remote_preference'])
        
        # Normaliser les soft skills
        if 'soft_skills' in normalized:
            normalized['soft_skills'] = self._normalize_skills(normalized['soft_skills'])
        
        return normalized
    
    def _normalize_job_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalise les données d'offre
        
        Args:
            data: Données offre mappées
            
        Returns:
            Données normalisées
        """
        normalized = data.copy()
        
        # Normaliser les compétences requises
        if 'required_skills' in normalized:
            normalized['required_skills'] = self._normalize_skills(normalized['required_skills'])
        
        # Normaliser l'expérience requise
        if 'required_experience' in normalized:
            normalized['required_experience'] = self._normalize_experience(normalized['required_experience'])
        
        # Normaliser le salaire
        if 'salary_range' in normalized:
            normalized['salary_range'] = self._normalize_salary_range(normalized['salary_range'])
        
        # Normaliser le type de contrat
        if 'contract_type' in normalized:
            normalized['contract_type'] = self._normalize_contract_type(normalized['contract_type'])
        
        # Normaliser la localisation
        if 'location' in normalized:
            normalized['location'] = self._normalize_location(normalized['location'])
        
        # Normaliser la politique remote
        if 'remote_policy' in normalized:
            normalized['remote_policy'] = self._normalize_remote_preference(normalized['remote_policy'])
        
        # Normaliser les soft skills désirés
        if 'desired_soft_skills' in normalized:
            normalized['desired_soft_skills'] = self._normalize_skills(normalized['desired_soft_skills'])
        
        return normalized
    
    def _normalize_skills(self, skills: Any) -> List[str]:
        """Normalise une liste de compétences"""
        if not skills:
            return []
        
        if isinstance(skills, str):
            # Diviser les compétences séparées par des virgules ou points-virgules
            skills = re.split(r'[,;]', skills)
        
        if not isinstance(skills, list):
            return []
        
        # Nettoyer et normaliser chaque compétence
        normalized_skills = []
        for skill in skills:
            if isinstance(skill, str):
                skill = skill.strip().title()
                if skill and len(skill) > 1:  # Éviter les compétences trop courtes
                    normalized_skills.append(skill)
        
        return normalized_skills
    
    def _normalize_experience(self, experience: Any) -> float:
        """Normalise l'expérience en années"""
        if experience is None:
            return 0.0
        
        if isinstance(experience, str):
            # Extraire les nombres de la chaîne
            numbers = re.findall(r'\d+', experience)
            if numbers:
                return float(numbers[0])
            return 0.0
        
        try:
            return max(0.0, float(experience))
        except (ValueError, TypeError):
            return 0.0
    
    def _normalize_salary(self, salary: Any) -> float:
        """Normalise un salaire"""
        if salary is None:
            return 0.0
        
        if isinstance(salary, str):
            # Extraire les nombres et convertir en salaire annuel
            numbers = re.findall(r'\d+', salary.replace(' ', ''))
            if numbers:
                value = float(numbers[0])
                # Si c'est en format "45K", multiplier par 1000
                if 'k' in salary.lower():
                    value *= 1000
                return value
            return 0.0
        
        try:
            return max(0.0, float(salary))
        except (ValueError, TypeError):
            return 0.0
    
    def _normalize_salary_range(self, salary_range: Any) -> Dict[str, float]:
        """Normalise une fourchette salariale"""
        if isinstance(salary_range, dict):
            return {
                'min': self._normalize_salary(salary_range.get('min', 0)),
                'max': self._normalize_salary(salary_range.get('max', 0))
            }
        
        if isinstance(salary_range, str):
            # Parser des formats comme "45K-55K€" ou "45000-55000"
            range_pattern = r'(\d+)(?:k)?.*?(\d+)(?:k)?'
            match = re.search(range_pattern, salary_range.lower())
            
            if match:
                min_val = float(match.group(1))
                max_val = float(match.group(2))
                
                # Convertir en milliers si nécessaire
                if 'k' in salary_range.lower():
                    min_val *= 1000
                    max_val *= 1000
                
                return {'min': min_val, 'max': max_val}
        
        # Si c'est un nombre unique, créer une fourchette
        normalized_salary = self._normalize_salary(salary_range)
        return {
            'min': normalized_salary * 0.9,  # -10%
            'max': normalized_salary * 1.1   # +10%
        }
    
    def _normalize_contract_types(self, contract_types: Any) -> List[str]:
        """Normalise les types de contrat recherchés"""
        if not contract_types:
            return []
        
        if isinstance(contract_types, str):
            contract_types = [contract_types]
        
        if not isinstance(contract_types, list):
            return []
        
        normalized = []
        contract_mapping = {
            'cdi': 'CDI',
            'cdd': 'CDD',
            'freelance': 'Freelance',
            'stage': 'Stage',
            'alternance': 'Alternance',
            'consultant': 'Freelance',
            'contrat pro': 'Alternance'
        }
        
        for contract in contract_types:
            if isinstance(contract, str):
                contract_lower = contract.lower().strip()
                normalized_contract = contract_mapping.get(contract_lower, contract.strip().upper())
                if normalized_contract not in normalized:
                    normalized.append(normalized_contract)
        
        return normalized
    
    def _normalize_contract_type(self, contract_type: Any) -> str:
        """Normalise un type de contrat unique"""
        if not contract_type:
            return ""
        
        contract_types = self._normalize_contract_types([contract_type])
        return contract_types[0] if contract_types else ""
    
    def _normalize_location(self, location: Any) -> str:
        """Normalise une localisation"""
        if not location:
            return ""
        
        if not isinstance(location, str):
            return str(location)
        
        # Nettoyer et capitaliser
        location = location.strip()
        
        # Normaliser les villes françaises communes
        city_mappings = {
            'paris': 'Paris',
            'lyon': 'Lyon', 
            'marseille': 'Marseille',
            'toulouse': 'Toulouse',
            'nice': 'Nice',
            'bordeaux': 'Bordeaux',
            'lille': 'Lille',
            'nantes': 'Nantes',
            'strasbourg': 'Strasbourg',
            'montpellier': 'Montpellier'
        }
        
        location_lower = location.lower()
        for city_key, city_proper in city_mappings.items():
            if city_key in location_lower:
                return city_proper
        
        return location.title()
    
    def _normalize_remote_preference(self, remote_pref: Any) -> str:
        """Normalise les préférences de télétravail"""
        if not remote_pref:
            return ""
        
        if not isinstance(remote_pref, str):
            return str(remote_pref)
        
        pref_lower = remote_pref.lower().strip()
        
        # Mapping des préférences communes
        remote_mappings = {
            'remote': 'remote',
            'full remote': 'remote',
            'télétravail': 'remote',
            'totalement': 'remote',
            'hybrid': 'hybrid',
            'hybride': 'hybrid',
            'mixte': 'hybrid',
            'partiel': 'hybrid',
            'onsite': 'onsite',
            'présentiel': 'onsite',
            'bureau': 'onsite',
            'sur site': 'onsite'
        }
        
        for key, value in remote_mappings.items():
            if key in pref_lower:
                return value
        
        return remote_pref
    
    def _validate_data(self, data: Dict[str, Any], data_type: str):
        """
        Valide les données selon les règles définies
        
        Args:
            data: Données à valider
            data_type: Type de données ("candidate" ou "job")
        """
        rules = self.validation_rules.get(data_type, {})
        
        # Vérifier les champs requis
        required_fields = rules.get('required_fields', [])
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Champ requis manquant: {field}")
        
        # Vérifier les types de données
        field_types = rules.get('field_types', {})
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    logger.warning(f"Type incorrect pour {field}: attendu {expected_type}, reçu {type(data[field])}")
    
    def reverse_adapt_candidate(self, standard_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convertit les données standard vers le format front-end
        
        Args:
            standard_data: Données au format standard
            
        Returns:
            Données au format front-end
        """
        reverse_mappings = {v: k for k, v in self.field_mappings["candidate"].items()}
        
        adapted = {}
        for standard_field, value in standard_data.items():
            frontend_field = reverse_mappings.get(standard_field, standard_field)
            adapted[frontend_field] = value
        
        return adapted
    
    def reverse_adapt_job(self, standard_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convertit les données standard vers le format front-end
        
        Args:
            standard_data: Données au format standard
            
        Returns:
            Données au format front-end
        """
        reverse_mappings = {v: k for k, v in self.field_mappings["job"].items()}
        
        adapted = {}
        for standard_field, value in standard_data.items():
            frontend_field = reverse_mappings.get(standard_field, standard_field)
            adapted[frontend_field] = value
        
        return adapted
    
    def get_supported_fields(self, data_type: str) -> Dict[str, List[str]]:
        """
        Retourne les champs supportés pour un type de données
        
        Args:
            data_type: Type de données ("candidate" ou "job")
            
        Returns:
            Dictionnaire avec les champs requis et optionnels
        """
        rules = self.validation_rules.get(data_type, {})
        mappings = self.field_mappings.get(data_type, {})
        
        return {
            "required_fields": rules.get('required_fields', []),
            "optional_fields": rules.get('optional_fields', []),
            "frontend_fields": list(mappings.keys()),
            "standard_fields": list(mappings.values())
        }
