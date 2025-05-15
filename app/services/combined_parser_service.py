#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Service combiné pour le parsing de CV et de fiches de poste."""

import logging
from typing import Dict, Any, Optional, Union, BinaryIO

from app.services.parser_service_interface import ParserServiceInterface
from app.services.existing_cv_parser_adapter import ExistingCVParserAdapter
from app.services.existing_job_parser_adapter import ExistingJobParserAdapter

logger = logging.getLogger(__name__)

class CombinedParserService(ParserServiceInterface):
    """Service combiné qui utilise les adaptateurs existants pour le parsing de CV et de fiches de poste.
    
    Cette classe implémente l'interface ParserServiceInterface en déléguant
    les appels aux adaptateurs spécifiques à chaque type de document.
    """
    
    def __init__(self, cv_parser_url: Optional[str] = None, job_parser_url: Optional[str] = None):
        """Initialise le service combiné avec les URLs des services de parsing.
        
        Args:
            cv_parser_url: URL du service de parsing de CV
            job_parser_url: URL du service de parsing de fiches de poste
        """
        self.cv_parser = ExistingCVParserAdapter(cv_parser_url)
        self.job_parser = ExistingJobParserAdapter(job_parser_url)
        logger.info("Initialisation du service de parsing combiné")
    
    async def parse_cv(self, file_content: Union[bytes, BinaryIO], file_name: Optional[str] = None) -> Dict[str, Any]:
        """Parse un CV en utilisant l'adaptateur de CV.
        
        Args:
            file_content: Contenu du fichier CV (binaire ou file-like object)
            file_name: Nom du fichier (optionnel)
            
        Returns:
            Dict[str, Any]: Données structurées extraites du CV
        """
        return await self.cv_parser.parse_cv(file_content, file_name)
    
    async def parse_job(self, job_description: str) -> Dict[str, Any]:
        """Parse une description de poste en utilisant l'adaptateur de fiches de poste.
        
        Args:
            job_description: Texte de la description de poste
            
        Returns:
            Dict[str, Any]: Données structurées extraites de la description de poste
        """
        return await self.job_parser.parse_job(job_description)
    
    async def parse_job_file(self, file_content: Union[bytes, BinaryIO], file_name: Optional[str] = None) -> Dict[str, Any]:
        """Parse un fichier de fiche de poste en utilisant l'adaptateur de fiches de poste.
        
        Note: Cette méthode est une extension de l'interface et n'est pas requise
        par ParserServiceInterface, mais elle est utile pour les fichiers de poste.
        
        Args:
            file_content: Contenu du fichier de fiche de poste (binaire ou file-like object)
            file_name: Nom du fichier (optionnel)
            
        Returns:
            Dict[str, Any]: Données structurées extraites de la fiche de poste
        """
        return await self.job_parser.parse_job_file(file_content, file_name)
