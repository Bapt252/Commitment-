#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Adapter pour le service de parsing de CV existant."""

import os
import json
import logging
import aiohttp
from typing import Dict, Any, Optional, Union, BinaryIO

from app.services.parser_service_interface import ParserServiceInterface

logger = logging.getLogger(__name__)

class ExistingCVParserAdapter(ParserServiceInterface):
    """Adapter pour le service de parsing de CV existant.
    
    Cette classe adapte le service de parsing de CV existant pour
    l'interface ParserServiceInterface.
    """
    
    def __init__(self, api_url: Optional[str] = None):
        """Initialise l'adaptateur pour le service de parsing de CV.
        
        Args:
            api_url: URL de l'API de parsing de CV (défaut: valeur de CV_PARSER_URL dans l'environnement)
        """
        self.api_url = api_url or os.environ.get("CV_PARSER_URL", "http://localhost:5051")
        logger.info(f"Initialisation de l'adaptateur de parsing CV avec URL: {self.api_url}")
    
    async def parse_cv(self, file_content: Union[bytes, BinaryIO], file_name: Optional[str] = None) -> Dict[str, Any]:
        """Parse un CV en utilisant le service existant.
        
        Args:
            file_content: Contenu du fichier CV (binaire ou file-like object)
            file_name: Nom du fichier (optionnel)
            
        Returns:
            Dict[str, Any]: Données structurées extraites du CV
            
        Raises:
            Exception: Si le parsing échoue
        """
        logger.info(f"Parsing de CV: {file_name if file_name else 'fichier sans nom'}")
        
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
                           filename=file_name or 'resume.pdf',
                           content_type='application/octet-stream')
            
            data.add_field('force_refresh', 'false')
            
            # Appeler l'API existante
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/api/parse-cv/", data=data) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Erreur de parsing CV: {error_text}")
                        raise Exception(f"Échec du parsing de CV: {error_text}")
                    
                    result = await response.json()
                    logger.info(f"Parsing de CV réussi. ID: {result.get('id', 'non spécifié')}")
                    
                    # Standardiser le format de réponse pour SmartMatch
                    return self._standardize_cv_data(result)
        
        except Exception as e:
            logger.exception(f"Exception lors du parsing de CV: {str(e)}")
            raise
    
    async def parse_job(self, job_description: str) -> Dict[str, Any]:
        """Non implémenté pour cet adaptateur qui est spécifique aux CV.
        
        Args:
            job_description: Texte de la description de poste
            
        Raises:
            NotImplementedError: Cette méthode n'est pas implémentée
        """
        raise NotImplementedError("Cet adaptateur ne supporte que le parsing de CV")
    
    def _standardize_cv_data(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Standardise les données de CV pour le format attendu par SmartMatch.
        
        Args:
            parsed_data: Données brutes du service de parsing
            
        Returns:
            Dict[str, Any]: Données standardisées
        """
        logger.debug("Standardisation des données de CV")
        
        # Exemple de standardisation basé sur le format de sortie connu du service existant
        # Adapter cette méthode selon le format réel du service de parsing
        try:
            parsed_content = parsed_data.get("parsed_content", {})
            
            return {
                "personal_info": {
                    "name": parsed_content.get("name", ""),
                    "email": parsed_content.get("email", ""),
                    "phone": parsed_content.get("phone", ""),
                    "location": parsed_content.get("location", {}).get("text", ""),
                },
                "summary": parsed_content.get("summary", ""),
                "skills": parsed_content.get("skills", []),
                "experience": [
                    {
                        "title": exp.get("title", ""),
                        "company": exp.get("company", ""),
                        "start_date": exp.get("start_date", ""),
                        "end_date": exp.get("end_date", ""),
                        "description": exp.get("description", ""),
                    }
                    for exp in parsed_content.get("experience", [])
                ],
                "education": [
                    {
                        "degree": edu.get("degree", ""),
                        "field_of_study": edu.get("field", ""),
                        "institution": edu.get("institution", ""),
                        "start_date": edu.get("start_date", ""),
                        "end_date": edu.get("end_date", ""),
                    }
                    for edu in parsed_content.get("education", [])
                ],
                "languages": parsed_content.get("languages", []),
                "certifications": parsed_content.get("certifications", []),
                "links": parsed_content.get("links", []),
                "original_id": parsed_data.get("id", ""),
                "original_data": parsed_data,  # Conserver les données d'origine
            }
        except Exception as e:
            logger.exception(f"Erreur lors de la standardisation des données CV: {str(e)}")
            # En cas d'erreur, retourner les données d'origine
            return {
                "original_data": parsed_data,
                "error": str(e)
            }
