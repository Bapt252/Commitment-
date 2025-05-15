#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Factory pour la création des services de parsing."""

import os
import logging
from typing import Optional

from app.services.parser_service_interface import ParserServiceInterface
from app.services.existing_cv_parser_adapter import ExistingCVParserAdapter
from app.services.existing_job_parser_adapter import ExistingJobParserAdapter
from app.services.combined_parser_service import CombinedParserService
from app.adapters.parsing_adapter import ParsingAdapter

logger = logging.getLogger(__name__)

class ServiceFactory:
    """Factory pour la création des services.
    
    Cette classe fournit des méthodes statiques pour créer les différents
    services nécessaires au système SmartMatch.
    """
    
    @staticmethod
    def create_parser_service(service_type: str = "combined", 
                             cv_parser_url: Optional[str] = None,
                             job_parser_url: Optional[str] = None) -> ParserServiceInterface:
        """Crée un service de parsing selon le type spécifié.
        
        Args:
            service_type: Type de service à créer ('combined', 'cv', 'job')
            cv_parser_url: URL de l'API de parsing de CV (optionnel)
            job_parser_url: URL de l'API de parsing de fiches de poste (optionnel)
            
        Returns:
            ParserServiceInterface: Instance du service de parsing
            
        Raises:
            ValueError: Si le type de service n'est pas reconnu
        """
        if service_type.lower() == "combined":
            logger.info("Création d'un service de parsing combiné")
            return CombinedParserService(cv_parser_url, job_parser_url)
        elif service_type.lower() == "cv":
            logger.info("Création d'un service de parsing CV")
            return ExistingCVParserAdapter(cv_parser_url)
        elif service_type.lower() == "job":
            logger.info("Création d'un service de parsing de fiches de poste")
            return ExistingJobParserAdapter(job_parser_url)
        else:
            msg = f"Type de service de parsing non reconnu: {service_type}"
            logger.error(msg)
            raise ValueError(msg)
    
    @staticmethod
    def create_parsing_adapter(parser_service: Optional[ParserServiceInterface] = None,
                              cv_parser_url: Optional[str] = None,
                              job_parser_url: Optional[str] = None) -> ParsingAdapter:
        """Crée un adaptateur de parsing.
        
        Args:
            parser_service: Service de parsing à utiliser (optionnel)
            cv_parser_url: URL de l'API de parsing de CV (optionnel)
            job_parser_url: URL de l'API de parsing de fiches de poste (optionnel)
            
        Returns:
            ParsingAdapter: Instance de l'adaptateur de parsing
        """
        logger.info("Création d'un adaptateur de parsing")
        
        # Si aucun service n'est fourni, en créer un par défaut
        if parser_service is None:
            # Déterminer le type de service à partir des variables d'environnement
            service_type = os.environ.get("DEFAULT_PARSER_SERVICE", "combined")
            parser_service = ServiceFactory.create_parser_service(
                service_type, cv_parser_url, job_parser_url
            )
        
        return ParsingAdapter(parser_service)
