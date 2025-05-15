#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Interface pour les services de parsing."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, BinaryIO

class ParserServiceInterface(ABC):
    """Interface pour les services de parsing.
    
    Cette interface définit les méthodes qui doivent être implémentées
    par tout service de parsing utilisé dans le système SmartMatch.
    """
    
    @abstractmethod
    async def parse_cv(self, file_content: Union[bytes, BinaryIO], file_name: Optional[str] = None) -> Dict[str, Any]:
        """Parse un CV et retourne les données structurées.
        
        Args:
            file_content: Contenu du fichier CV (binaire ou file-like object)
            file_name: Nom du fichier (optionnel)
            
        Returns:
            Dict[str, Any]: Données structurées extraites du CV
        """
        pass
    
    @abstractmethod
    async def parse_job(self, job_description: str) -> Dict[str, Any]:
        """Parse une description de poste et retourne les données structurées.
        
        Args:
            job_description: Texte de la description de poste
            
        Returns:
            Dict[str, Any]: Données structurées extraites de la description de poste
        """
        pass
