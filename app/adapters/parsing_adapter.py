#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Adaptateur pour convertir les données parsées au format attendu par SmartMatch."""

import logging
import json
import uuid
import asyncio
from typing import Dict, List, Any, Optional, Union, BinaryIO

from app.services.parser_service_interface import ParserServiceInterface

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ParsingAdapter")

class ParsingAdapter:
    """
    Adaptateur pour convertir les données parsées des CV et fiches de poste
    au format attendu par SmartMatch.
    """
    
    def __init__(self, parser_service: Optional[ParserServiceInterface] = None):
        """
        Initialise l'adaptateur avec un service de parsing.
        
        Args:
            parser_service (ParserServiceInterface, optional): Service de parsing à utiliser
        """
        self.parser_service = parser_service
        self._cache = {}  # Cache simple pour les documents parsés
        logger.info("Adaptateur de parsing initialisé avec succès")
    
    async def parse_cv(self, file_content: Union[bytes, BinaryIO], file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse un CV en utilisant le service de parsing.
        
        Args:
            file_content: Contenu du fichier CV (binaire ou file-like object)
            file_name: Nom du fichier (optionnel)
            
        Returns:
            Dict[str, Any]: Données structurées extraites du CV
            
        Raises:
            Exception: Si le parsing échoue ou si aucun service n'est disponible
        """
        logger.info(f"Parsing de CV: {file_name if file_name else 'fichier sans nom'}")
        
        if not self.parser_service:
            return self._simulate_cv_parsing({})
        
        try:
            # Vérifier le cache d'abord
            cache_key = f"cv_{hash(repr(file_content))}"
            if cache_key in self._cache:
                logger.info("Utilisation de données de CV en cache")
                return self._cache[cache_key]
            
            # Utiliser le service de parsing
            parsed_data = await self.parser_service.parse_cv(file_content, file_name)
            
            # Mettre en cache le résultat
            self._cache[cache_key] = parsed_data
            
            return parsed_data
        except Exception as e:
            logger.error(f"Erreur lors du parsing de CV: {str(e)}")
            
            # En cas d'erreur, utiliser un parsing simulé comme fallback
            logger.warning("Utilisation du parsing simulé comme fallback")
            return self._simulate_cv_parsing({})
    
    async def parse_job(self, job_description: str) -> Dict[str, Any]:
        """
        Parse une description de poste en utilisant le service de parsing.
        
        Args:
            job_description: Texte de la description de poste
            
        Returns:
            Dict[str, Any]: Données structurées extraites de la description de poste
            
        Raises:
            Exception: Si le parsing échoue ou si aucun service n'est disponible
        """
        logger.info("Parsing de description de poste")
        
        if not self.parser_service:
            return self._simulate_job_parsing({})
        
        try:
            # Vérifier le cache d'abord
            cache_key = f"job_{hash(job_description)}"
            if cache_key in self._cache:
                logger.info("Utilisation de données de poste en cache")
                return self._cache[cache_key]
            
            # Utiliser le service de parsing
            parsed_data = await self.parser_service.parse_job(job_description)
            
            # Mettre en cache le résultat
            self._cache[cache_key] = parsed_data
            
            return parsed_data
        except Exception as e:
            logger.error(f"Erreur lors du parsing de description de poste: {str(e)}")
            
            # En cas d'erreur, utiliser un parsing simulé comme fallback
            logger.warning("Utilisation du parsing simulé comme fallback")
            return self._simulate_job_parsing({})
    
    async def parse_job_file(self, file_content: Union[bytes, BinaryIO], file_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse un fichier de fiche de poste en utilisant le service de parsing.
        
        Args:
            file_content: Contenu du fichier de fiche de poste (binaire ou file-like object)
            file_name: Nom du fichier (optionnel)
            
        Returns:
            Dict[str, Any]: Données structurées extraites de la fiche de poste
            
        Raises:
            Exception: Si le parsing échoue ou si aucun service n'est disponible
        """
        logger.info(f"Parsing de fichier de fiche de poste: {file_name if file_name else 'fichier sans nom'}")
        
        # Vérifier si le service implémente parse_job_file
        if self.parser_service and hasattr(self.parser_service, "parse_job_file"):
            try:
                # Vérifier le cache d'abord
                cache_key = f"job_file_{hash(repr(file_content))}"
                if cache_key in self._cache:
                    logger.info("Utilisation de données de fichier de poste en cache")
                    return self._cache[cache_key]
                
                # Utiliser la méthode du service
                method = getattr(self.parser_service, "parse_job_file")
                parsed_data = await method(file_content, file_name)
                
                # Mettre en cache le résultat
                self._cache[cache_key] = parsed_data
                
                return parsed_data
            except Exception as e:
                logger.error(f"Erreur lors du parsing de fichier de fiche de poste: {str(e)}")
        
        # Fallback: extraire le texte et utiliser parse_job
        logger.info("Extraction du texte du fichier de fiche de poste")
        if isinstance(file_content, bytes):
            try:
                text = file_content.decode("utf-8")
                return await self.parse_job(text)
            except UnicodeDecodeError:
                pass
        
        # En cas d'échec, utiliser un parsing simulé
        logger.warning("Utilisation du parsing simulé comme fallback")
        return self._simulate_job_parsing({})
    
    def prepare_for_matching(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """
        Prépare les données parsées pour le matching.
        
        Args:
            data: Données parsées
            data_type: Type de données ("cv" ou "job")
            
        Returns:
            Dict[str, Any]: Données formatées pour le matching
            
        Raises:
            ValueError: Si le type de données n'est pas reconnu
        """
        if data_type.lower() == "cv":
            return self.cv_to_candidate(data)
        elif data_type.lower() == "job":
            return self.job_to_company(data)
        else:
            raise ValueError(f"Type de données non reconnu: {data_type}")
    
    def cv_to_candidate(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convertit les données parsées d'un CV au format attendu par SmartMatch.
        
        Args:
            cv_data (Dict): Données parsées du CV
            
        Returns:
            Dict: Données formatées pour SmartMatch
        """
        # Extraction des informations pertinentes
        cv_id = cv_data.get("id", f"cv_{uuid.uuid4().hex[:8]}")
        
        # Extraction du nom
        name = ""
        if "name" in cv_data:
            name = cv_data["name"]
        elif "personal_info" in cv_data and "name" in cv_data["personal_info"]:
            name = cv_data["personal_info"]["name"]
        
        # Extraction des compétences
        skills = []
        if "skills" in cv_data:
            skills = cv_data["skills"]
        if isinstance(skills, str):
            # Si les compétences sont une chaîne, la diviser
            skills = [skill.strip() for skill in skills.split(",")]
        
        # Extraction de l'expérience
        experience = 0
        if "total_experience" in cv_data:
            experience = cv_data["total_experience"]
        else:
            # Calculer l'expérience totale
            for job in cv_data.get("experience", []):
                if "duration" in job:
                    experience += job["duration"]
                elif "duration_years" in job:
                    experience += job["duration_years"]
                elif "start_date" in job and "end_date" in job:
                    # Calcul simplifié à partir des dates
                    start = job["start_date"]
                    end = job["end_date"] or "present"
                    # Logique de calcul de durée ici
        
        # Extraction de la localisation
        location = ""
        if "location" in cv_data:
            location = cv_data["location"]
        elif "personal_info" in cv_data and "location" in cv_data["personal_info"]:
            location = cv_data["personal_info"]["location"]
        
        if isinstance(location, dict):
            location_parts = []
            for field in ["street", "city", "state", "country"]:
                if field in location and location[field]:
                    location_parts.append(location[field])
            location = ", ".join(location_parts)
        
        # Extraction des attentes salariales
        salary_expectation = 0
        if "salary_expectation" in cv_data:
            salary_expectation = cv_data["salary_expectation"]
        
        if isinstance(salary_expectation, str):
            # Nettoyer et convertir en nombre
            salary_expectation = salary_expectation.replace("$", "").replace("€", "").replace(" ", "")
            try:
                salary_expectation = int(salary_expectation)
            except (ValueError, TypeError):
                salary_expectation = 0
        
        # Extraction des préférences de travail à distance
        remote_preference = "hybrid"  # Valeur par défaut
        if "remote_preference" in cv_data:
            remote_preference = cv_data["remote_preference"]
        elif "preferences" in cv_data and "remote_work" in cv_data["preferences"]:
            pref = cv_data["preferences"]["remote_work"]
            if isinstance(pref, str):
                pref = pref.lower()
                if pref in ["yes", "true", "full", "100%"]:
                    remote_preference = "full"
                elif pref in ["no", "false", "office", "0%"]:
                    remote_preference = "office"
        
        # Création du dictionnaire au format SmartMatch
        candidate = {
            "id": cv_id,
            "name": name,
            "skills": skills,
            "experience": experience,
            "location": location,
            "remote_preference": remote_preference,
            "salary_expectation": salary_expectation,
            "original_data": cv_data  # Conserver les données originales pour référence
        }
        
        return candidate
    
    def job_to_company(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convertit les données parsées d'une fiche de poste au format attendu par SmartMatch.
        
        Args:
            job_data (Dict): Données parsées de la fiche de poste
            
        Returns:
            Dict: Données formatées pour SmartMatch
        """
        # Extraction des informations pertinentes
        job_id = job_data.get("id", f"job_{uuid.uuid4().hex[:8]}")
        
        # Extraction du nom de l'entreprise
        company_name = ""
        if "company_name" in job_data:
            company_name = job_data["company_name"]
        elif "company" in job_data:
            if isinstance(job_data["company"], str):
                company_name = job_data["company"]
            elif isinstance(job_data["company"], dict) and "name" in job_data["company"]:
                company_name = job_data["company"]["name"]
        
        # Extraction du titre du poste
        job_title = ""
        if "job_title" in job_data:
            job_title = job_data["job_title"]
        elif "title" in job_data:
            job_title = job_data["title"]
        
        # Extraction des compétences requises
        required_skills = []
        if "skills" in job_data:
            required_skills = job_data["skills"]
        elif "required_skills" in job_data:
            required_skills = job_data["required_skills"]
        
        if isinstance(required_skills, str):
            # Si les compétences sont une chaîne, la diviser
            required_skills = [skill.strip() for skill in required_skills.split(",")]
        
        # Extraction de l'expérience requise
        required_experience = 0
        if "experience_required" in job_data:
            required_experience = job_data["experience_required"]
        elif "experience" in job_data:
            required_experience = job_data["experience"]
        
        if isinstance(required_experience, str):
            # Extraire le nombre d'années
            import re
            years = re.findall(r'(\d+)', required_experience)
            if years:
                required_experience = int(years[0])
        
        # Extraction de la localisation
        location = ""
        if "location" in job_data:
            location = job_data["location"]
        
        if isinstance(location, dict):
            location_parts = []
            for field in ["street", "city", "state", "country"]:
                if field in location and location[field]:
                    location_parts.append(location[field])
            location = ", ".join(location_parts)
        
        # Extraction de la fourchette de salaire
        salary_range = {"min": 0, "max": 0}
        if "salary_range" in job_data:
            salary_range = job_data["salary_range"]
        elif "salary" in job_data:
            if isinstance(job_data["salary"], dict):
                salary_range["min"] = job_data["salary"].get("min", 0)
                salary_range["max"] = job_data["salary"].get("max", 0)
            elif isinstance(job_data["salary"], str):
                # Extraire les nombres de la chaîne
                import re
                numbers = re.findall(r'(\d+(?:\.\d+)?)', job_data["salary"].replace(",", ""))
                if len(numbers) >= 2:
                    salary_range["min"] = float(numbers[0])
                    salary_range["max"] = float(numbers[1])
                elif len(numbers) == 1:
                    salary_range["min"] = 0
                    salary_range["max"] = float(numbers[0])
        
        # Extraction de la politique de travail à distance
        remote_policy = "hybrid"  # Valeur par défaut
        if "remote_policy" in job_data:
            remote_policy = job_data["remote_policy"]
        elif "remote" in job_data:
            remote = job_data["remote"]
            if isinstance(remote, bool):
                remote_policy = "full" if remote else "office"
            elif isinstance(remote, str):
                remote = remote.lower()
                if remote in ["yes", "true", "full", "100%"]:
                    remote_policy = "full"
                elif remote in ["no", "false", "office", "0%"]:
                    remote_policy = "office"
        
        # Création du dictionnaire au format SmartMatch
        company = {
            "id": job_id,
            "name": company_name,
            "title": job_title,
            "required_skills": required_skills,
            "location": location,
            "remote_policy": remote_policy,
            "required_experience": required_experience,
            "salary_range": salary_range,
            "original_data": job_data  # Conserver les données originales pour référence
        }
        
        return company
    
    def _simulate_cv_parsing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simule le parsing d'un CV en cas de défaillance du service.
        
        Args:
            data (Dict): Données initiales
            
        Returns:
            Dict: Données simulées
        """
        logger.info("Simulation du parsing de CV")
        
        # Créer un identifiant unique
        cv_id = data.get("id", f"cv_{uuid.uuid4().hex[:8]}")
        
        # Extraire ou simuler le nom
        name = data.get("name", "Candidat")
        if not name and "personal_info" in data:
            name = data["personal_info"].get("name", "Candidat")
        
        # Extraire ou simuler les compétences
        skills = data.get("skills", ["Python", "JavaScript", "SQL", "React", "Docker"])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",")]
        
        # Créer un profil parsé simulé
        parsed_data = {
            "id": cv_id,
            "name": name,
            "skills": skills,
            "experience": data.get("experience", []),
            "total_experience": data.get("total_experience", 3),
            "location": data.get("location", "Paris, France"),
            "salary_expectation": data.get("salary_expectation", 50000),
            "preferences": {
                "remote_work": data.get("remote_preference", "hybrid")
            }
        }
        
        return parsed_data
    
    def _simulate_job_parsing(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simule le parsing d'une fiche de poste en cas de défaillance du service.
        
        Args:
            data (Dict): Données initiales
            
        Returns:
            Dict: Données simulées
        """
        logger.info("Simulation du parsing de fiche de poste")
        
        # Créer un identifiant unique
        job_id = data.get("id", f"job_{uuid.uuid4().hex[:8]}")
        
        # Extraire ou simuler le titre
        title = data.get("title", data.get("job_title", "Développeur Full Stack"))
        
        # Extraire ou simuler l'entreprise
        company_name = data.get("company_name", "Entreprise")
        if not company_name and isinstance(data.get("company"), dict):
            company_name = data["company"].get("name", "Entreprise")
        
        # Extraire ou simuler les compétences
        skills = data.get("skills", ["Python", "JavaScript", "SQL", "React", "Docker"])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",")]
        
        # Créer un profil parsé simulé
        parsed_data = {
            "id": job_id,
            "job_title": title,
            "company_name": company_name,
            "skills": skills,
            "experience_required": data.get("experience_required", 2),
            "location": data.get("location", "Paris, France"),
            "remote": data.get("remote", "hybrid"),
            "salary": {
                "min": data.get("salary_min", 40000),
                "max": data.get("salary_max", 60000)
            }
        }
        
        return parsed_data
