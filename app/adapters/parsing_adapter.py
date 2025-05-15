#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Adaptateur pour convertir les données parsées au format attendu par SmartMatch."""

import logging
import requests
import json
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
    
    async def parse_cv(self, cv_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Version simplifiée: simulate parsing un CV.
        
        Args:
            cv_data (Dict): Données du CV à parser
            
        Returns:
            Dict: Données parsées simulées
        """
        logger.info("Simulation de parsing de CV")
        
        # Simuler un délai de traitement
        await asyncio.sleep(0.5)
        
        # Extraire certaines informations de base
        name = cv_data.get("name", "")
        if not name and "personal_info" in cv_data:
            name = cv_data["personal_info"].get("name", "")
        
        skills = cv_data.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",")]
        
        # Créer un profil parsé simulé
        parsed_data = {
            "id": cv_data.get("id", "cv_" + str(hash(name))[:8]),
            "name": name,
            "skills": skills,
            "work_experience": cv_data.get("experience", []),
            "address": cv_data.get("location", {}),
            "salary_expectation": cv_data.get("salary", 0),
            "preferences": {
                "remote_work": cv_data.get("remote", "hybrid")
            }
        }
        
        return parsed_data
    
    async def parse_job(self, job_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Version simplifiée: simulate parsing une fiche de poste.
        
        Args:
            job_data (Dict): Données de la fiche de poste à parser
            
        Returns:
            Dict: Données parsées simulées
        """
        logger.info("Simulation de parsing de fiche de poste")
        
        # Simuler un délai de traitement
        await asyncio.sleep(0.5)
        
        # Extraire certaines informations de base
        company_name = job_data.get("company_name", "")
        title = job_data.get("title", "")
        if not title and "job_info" in job_data:
            title = job_data["job_info"].get("title", "")
        
        skills = job_data.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",")]
        
        # Créer un profil parsé simulé
        parsed_data = {
            "id": job_data.get("id", "job_" + str(hash(title))[:8]),
            "title": title,
            "company": {"name": company_name},
            "required_skills": skills,
            "experience_required": job_data.get("experience", 0),
            "location": job_data.get("location", ""),
            "salary": {
                "min": job_data.get("salary_min", 0),
                "max": job_data.get("salary_max", 0)
            },
            "remote_work": job_data.get("remote", "hybrid")
        }
        
        return parsed_data
    
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
        if isinstance(experience_text, (int, float)):
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
