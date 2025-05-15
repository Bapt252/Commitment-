#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Adapter pour le service de parsing de fiches de poste existant."""

import os
import json
import logging
import aiohttp
from typing import Dict, Any, Optional, Union, BinaryIO

from app.services.parser_service_interface import ParserServiceInterface

logger = logging.getLogger(__name__)

class ExistingJobParserAdapter(ParserServiceInterface):
    """Adapter pour le service de parsing de fiches de poste existant.
    
    Cette classe adapte le service de parsing de fiches de poste existant pour
    l'interface ParserServiceInterface.
    """
    
    def __init__(self, api_url: Optional[str] = None):
        """Initialise l'adaptateur pour le service de parsing de fiches de poste.
        
        Args:
            api_url: URL de l'API de parsing de fiches de poste (défaut: valeur de JOB_PARSER_URL dans l'environnement)
        """
        self.api_url = api_url or os.environ.get("JOB_PARSER_URL", "http://localhost:5055")
        logger.info(f"Initialisation de l'adaptateur de parsing de fiches de poste avec URL: {self.api_url}")
    
    async def parse_job(self, job_description: str) -> Dict[str, Any]:
        """Parse une description de poste en utilisant le service existant.
        
        Args:
            job_description: Texte de la description de poste
            
        Returns:
            Dict[str, Any]: Données structurées extraites de la description de poste
            
        Raises:
            Exception: Si le parsing échoue
        """
        logger.info("Parsing de fiche de poste")
        
        try:
            # Préparer les données pour l'API existante
            data = {
                "text": job_description
            }
            
            # Appeler l'API existante
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/analyze", json=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Erreur de parsing de fiche de poste: {error_text}")
                        raise Exception(f"Échec du parsing de fiche de poste: {error_text}")
                    
                    result = await response.json()
                    logger.info("Parsing de fiche de poste réussi")
                    
                    # Standardiser le format de réponse pour SmartMatch
                    return self._standardize_job_data(result)
        
        except Exception as e:
            logger.exception(f"Exception lors du parsing de fiche de poste: {str(e)}")
            raise
    
    async def parse_cv(self, file_content: Union[bytes, BinaryIO], file_name: Optional[str] = None) -> Dict[str, Any]:
        """Non implémenté pour cet adaptateur qui est spécifique aux fiches de poste.
        
        Args:
            file_content: Contenu du fichier CV (binaire ou file-like object)
            file_name: Nom du fichier (optionnel)
            
        Raises:
            NotImplementedError: Cette méthode n'est pas implémentée
        """
        raise NotImplementedError("Cet adaptateur ne supporte que le parsing de fiches de poste")
    
    async def parse_job_file(self, file_content: Union[bytes, BinaryIO], file_name: Optional[str] = None) -> Dict[str, Any]:
        """Parse un fichier de fiche de poste en utilisant le service existant.
        
        Note: Cette méthode est une extension de l'interface et n'est pas requise
        par ParserServiceInterface, mais elle est utile pour les fichiers de poste.
        
        Args:
            file_content: Contenu du fichier de fiche de poste (binaire ou file-like object)
            file_name: Nom du fichier (optionnel)
            
        Returns:
            Dict[str, Any]: Données structurées extraites de la fiche de poste
            
        Raises:
            Exception: Si le parsing échoue
        """
        logger.info(f"Parsing de fichier de fiche de poste: {file_name if file_name else 'fichier sans nom'}")
        
        try:
            # Préparer les données pour l'API existante
            data = aiohttp.FormData()
            
            # Si file_content est un file-like object, le lire en bytes
            if hasattr(file_content, 'read'):
                content = file_content.read()
                if isinstance(content, str):
                    content = content.encode('utf-8')
                file_content = content
            
            data.add_field('file', 
                           file_content,
                           filename=file_name or 'job_description.pdf',
                           content_type='application/octet-stream')
            
            # Appeler l'API existante
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/analyze-file", data=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Erreur de parsing de fichier de fiche de poste: {error_text}")
                        raise Exception(f"Échec du parsing de fichier de fiche de poste: {error_text}")
                    
                    result = await response.json()
                    logger.info("Parsing de fichier de fiche de poste réussi")
                    
                    # Standardiser le format de réponse pour SmartMatch
                    return self._standardize_job_data(result)
        
        except Exception as e:
            logger.exception(f"Exception lors du parsing de fichier de fiche de poste: {str(e)}")
            raise
    
    def _standardize_job_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardise les données de fiche de poste pour le format attendu par SmartMatch.
        
        Args:
            parsed_data: Données brutes du service de parsing
            
        Returns:
            Dict[str, Any]: Données standardisées
        """
        logger.debug("Standardisation des données de fiche de poste")
        
        # Exemple de standardisation basé sur le format de sortie connu du service existant
        # Adapter cette méthode selon le format réel du service de parsing
        try:
            # Extraire les champs pertinents du résultat du parsing
            # Le format exact dépendra de votre service existant
            job_data = parsed_data.get("content", {})
            
            # Standardisation des compétences
            skills = []
            if isinstance(job_data.get("skills"), list):
                skills = job_data.get("skills", [])
            elif isinstance(job_data.get("skills"), dict):
                for skill_type, skill_list in job_data.get("skills", {}).items():
                    if isinstance(skill_list, list):
                        skills.extend(skill_list)
            
            # Création du format standardisé
            return {
                "job_title": job_data.get("job_title", ""),
                "company_name": job_data.get("company_name", ""),
                "location": job_data.get("location", ""),
                "skills": skills,
                "experience_required": job_data.get("experience_years", 0),
                "education_required": job_data.get("education_level", ""),
                "job_description": job_data.get("job_description", ""),
                "job_type": job_data.get("job_type", ""),
                "remote": job_data.get("remote", False),
                "salary_range": job_data.get("salary", {}).get("range", ""),
                "benefits": job_data.get("benefits", []),
                "responsibilities": job_data.get("responsibilities", []),
                "requirements": job_data.get("requirements", []),
                "original_data": parsed_data,  # Conserver les données d'origine
            }
        except Exception as e:
            logger.exception(f"Erreur lors de la standardisation des données de fiche de poste: {str(e)}")
            # En cas d'erreur, retourner les données d'origine
            return {
                "original_data": parsed_data,
                "error": str(e)
            }
