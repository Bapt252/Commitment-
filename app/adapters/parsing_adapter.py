#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Adaptateur pour convertir les données parsées au format attendu par SmartMatch."""

import logging
import requests
import json
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional, Union

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ParsingAdapter")

class ParsingAdapter:
    """
    Adaptateur pour convertir les données parsées des CV et fiches de poste
    au format attendu par SmartMatch.
    """
    
    def __init__(self, cv_parser_url: str = "http://localhost:5051", 
                 job_parser_url: str = "http://localhost:5055"):
        """
        Initialise l'adaptateur avec les URLs des services de parsing.
        
        Args:
            cv_parser_url (str): URL du service de parsing de CV
            job_parser_url (str): URL du service de parsing de fiches de poste
        """
        self.cv_parser_url = cv_parser_url
        self.job_parser_url = job_parser_url
        logger.info("Adaptateur de parsing initialisé avec succès")
    
    def get_cv_data(self, cv_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les données parsées d'un CV depuis le service de parsing.
        
        Args:
            cv_id (str): Identifiant du CV
            
        Returns:
            Dict: Données parsées du CV, ou None en cas d'erreur
        """
        try:
            url = f"{self.cv_parser_url}/api/cv/{cv_id}"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur lors de la récupération du CV {cv_id}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Exception lors de la récupération du CV {cv_id}: {e}")
            return None
    
    def get_job_data(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère les données parsées d'une fiche de poste depuis le service de parsing.
        
        Args:
            job_id (str): Identifiant de la fiche de poste
            
        Returns:
            Dict: Données parsées de la fiche de poste, ou None en cas d'erreur
        """
        try:
            url = f"{self.job_parser_url}/api/job/{job_id}"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur lors de la récupération de la fiche de poste {job_id}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Exception lors de la récupération de la fiche de poste {job_id}: {e}")
            return None
    
    def get_all_cvs(self) -> List[Dict[str, Any]]:
        """
        Récupère tous les CVs parsés depuis le service de parsing.
        
        Returns:
            List[Dict]: Liste des données parsées des CVs
        """
        try:
            url = f"{self.cv_parser_url}/api/cvs"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur lors de la récupération des CVs: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Exception lors de la récupération des CVs: {e}")
            return []
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Récupère toutes les fiches de poste parsées depuis le service de parsing.
        
        Returns:
            List[Dict]: Liste des données parsées des fiches de poste
        """
        try:
            url = f"{self.job_parser_url}/api/jobs"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur lors de la récupération des fiches de poste: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Exception lors de la récupération des fiches de poste: {e}")
            return []
    
    async def parse_cv(self, cv_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Envoie un CV au service de parsing et retourne le profil structuré.
        
        Args:
            cv_data (Dict): Données du CV à parser
            
        Returns:
            Dict: Données parsées du CV, ou None en cas d'erreur
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.cv_parser_url}/parse", json=cv_data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Erreur lors du parsing du CV: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Exception lors du parsing du CV: {e}")
            return None
    
    async def parse_job(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Envoie une fiche de poste au service de parsing et retourne le profil de poste structuré.
        
        Args:
            job_data (Dict): Données de la fiche de poste à parser
            
        Returns:
            Dict: Données parsées de la fiche de poste, ou None en cas d'erreur
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.job_parser_url}/parse", json=job_data) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Erreur lors du parsing de la fiche de poste: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Exception lors du parsing de la fiche de poste: {e}")
            return None
    
    async def get_cv_data_async(self, cv_id: str) -> Optional[Dict[str, Any]]:
        """
        Version asynchrone de get_cv_data.
        
        Args:
            cv_id (str): Identifiant du CV
            
        Returns:
            Dict: Données parsées du CV, ou None en cas d'erreur
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.cv_parser_url}/api/cv/{cv_id}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Erreur lors de la récupération du CV {cv_id}: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Exception lors de la récupération du CV {cv_id}: {e}")
            return None
    
    async def get_job_data_async(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Version asynchrone de get_job_data.
        
        Args:
            job_id (str): Identifiant de la fiche de poste
            
        Returns:
            Dict: Données parsées de la fiche de poste, ou None en cas d'erreur
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.job_parser_url}/api/job/{job_id}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Erreur lors de la récupération de la fiche de poste {job_id}: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Exception lors de la récupération de la fiche de poste {job_id}: {e}")
            return None
    
    def cv_to_candidate(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convertit les données parsées d'un CV au format attendu par SmartMatch.
        
        Args:
            cv_data (Dict): Données parsées du CV
            
        Returns:
            Dict: Données formatées pour SmartMatch
        """
        # Extraction des informations pertinentes
        cv_id = cv_data.get("id", "")
        name = cv_data.get("name", "")
        
        # Extraction des compétences
        skills = cv_data.get("skills", [])
        if isinstance(skills, str):
            # Si les compétences sont une chaîne, la diviser
            skills = [skill.strip() for skill in skills.split(",")]
        
        # Extraction de l'expérience
        experience = 0
        for job in cv_data.get("work_experience", []):
            experience += job.get("duration_years", 0)
        
        # Extraction de la localisation
        location = ""
        if "address" in cv_data:
            address_parts = []
            if "city" in cv_data["address"]:
                address_parts.append(cv_data["address"]["city"])
            if "country" in cv_data["address"]:
                address_parts.append(cv_data["address"]["country"])
            location = ", ".join(address_parts)
        
        # Extraction des attentes salariales
        salary_expectation = cv_data.get("salary_expectation", 0)
        if isinstance(salary_expectation, str):
            # Nettoyer et convertir en nombre
            salary_expectation = salary_expectation.replace("$", "").replace("€", "").replace(" ", "")
            try:
                salary_expectation = int(salary_expectation)
            except ValueError:
                salary_expectation = 0
        
        # Extraction des préférences de travail à distance
        remote_preference = "hybrid"  # Valeur par défaut
        preferences = cv_data.get("preferences", {})
        if preferences:
            if preferences.get("remote_work", "").lower() == "yes":
                remote_preference = "full"
            elif preferences.get("remote_work", "").lower() == "no":
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
        job_id = job_data.get("id", "")
        company_name = job_data.get("company", {}).get("name", "")
        job_title = job_data.get("title", "")
        
        # Extraction des compétences requises
        required_skills = job_data.get("required_skills", [])
        if isinstance(required_skills, str):
            # Si les compétences sont une chaîne, la diviser
            required_skills = [skill.strip() for skill in required_skills.split(",")]
        
        # Extraction de l'expérience requise
        required_experience = 0
        experience_text = job_data.get("experience_required", "")
        if isinstance(experience_text, str):
            # Extraire le nombre d'années d'expérience
            import re
            experience_match = re.search(r'(\d+)\s*(?:an|year)', experience_text, re.IGNORECASE)
            if experience_match:
                required_experience = int(experience_match.group(1))
        elif isinstance(experience_text, (int, float)):
            required_experience = experience_text
        
        # Extraction de la localisation
        location = job_data.get("location", "")
        if isinstance(location, dict):
            location_parts = []
            if "city" in location:
                location_parts.append(location["city"])
            if "country" in location:
                location_parts.append(location["country"])
            location = ", ".join(location_parts)
        
        # Extraction de la fourchette de salaire
        salary_range = {"min": 0, "max": 0}
        salary_data = job_data.get("salary", {})
        if isinstance(salary_data, dict):
            salary_range["min"] = salary_data.get("min", 0)
            salary_range["max"] = salary_data.get("max", 0)
        
        # Extraction de la politique de travail à distance
        remote_policy = "hybrid"  # Valeur par défaut
        remote_info = job_data.get("remote_work", "")
        if isinstance(remote_info, str):
            remote_info = remote_info.lower()
            if "full" in remote_info or "100%" in remote_info:
                remote_policy = "full"
            elif "no" in remote_info or "office only" in remote_info:
                remote_policy = "office_only"
        
        # Création du dictionnaire au format SmartMatch
        company = {
            "id": job_id,
            "name": f"{company_name} - {job_title}",
            "required_skills": required_skills,
            "location": location,
            "remote_policy": remote_policy,
            "required_experience": required_experience,
            "salary_range": salary_range,
            "original_data": job_data  # Conserver les données originales pour référence
        }
        
        return company
    
    def convert_all_cvs(self) -> List[Dict[str, Any]]:
        """
        Convertit tous les CVs disponibles au format SmartMatch.
        
        Returns:
            List[Dict]: Liste des candidats au format SmartMatch
        """
        cvs = self.get_all_cvs()
        candidates = [self.cv_to_candidate(cv) for cv in cvs]
        logger.info(f"Conversion de {len(candidates)} CVs au format SmartMatch")
        return candidates
    
    def convert_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Convertit toutes les fiches de poste disponibles au format SmartMatch.
        
        Returns:
            List[Dict]: Liste des entreprises au format SmartMatch
        """
        jobs = self.get_all_jobs()
        companies = [self.job_to_company(job) for job in jobs]
        logger.info(f"Conversion de {len(companies)} fiches de poste au format SmartMatch")
        return companies
