#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Pipeline d'intégration pour le matching entre CVs et fiches de poste."""

import logging
import json
import os
import time
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple, BinaryIO

from app.core.smart_match import SmartMatcher
from app.adapters.parsing_adapter import ParsingAdapter
from app.factories import ServiceFactory

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MatchingPipeline")

class MatchingPipeline:
    """
    Pipeline d'intégration pour le matching entre CVs et fiches de poste.
    """
    
    def __init__(self, parsing_adapter: Optional[ParsingAdapter] = None,
                 results_dir: str = "matching_results"):
        """
        Initialise le pipeline de matching.
        
        Args:
            parsing_adapter (ParsingAdapter, optional): Adaptateur de parsing
            results_dir (str): Répertoire pour stocker les résultats
        """
        # Si aucun adaptateur n'est fourni, en créer un par défaut
        self.parsing_adapter = parsing_adapter or ServiceFactory.create_parsing_adapter()
        self.matcher = SmartMatcher()
        self.results_dir = results_dir
        
        # Créer le répertoire des résultats s'il n'existe pas
        os.makedirs(results_dir, exist_ok=True)
        
        logger.info("Pipeline de matching initialisé avec succès")
    
    async def parse_and_match_cv_job(self, cv_data: Dict[str, Any], 
                                     job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse et match directement un CV et une fiche de poste à partir de leurs données brutes.
        
        Args:
            cv_data (Dict): Données brutes du CV
            job_data (Dict): Données brutes de la fiche de poste
            
        Returns:
            Dict: Résultat du matching
        """
        logger.info("Démarrage du parsing et matching direct de CV et fiche de poste")
        
        try:
            # Préparer les données pour le matching
            candidate = self.parsing_adapter.prepare_for_matching(cv_data, "cv")
            job = self.parsing_adapter.prepare_for_matching(job_data, "job")
            
            # Exécuter le matching
            score, details = self.matcher.calculate_match(candidate, job)
            
            # Préparer le résultat
            result = {
                "status": "success",
                "candidate": {
                    "id": candidate.get("id", "unknown"),
                    "name": candidate.get("name", "Candidat")
                },
                "job": {
                    "id": job.get("id", "unknown"),
                    "title": job.get("title", "Poste")
                },
                "score": score,
                "details": details
            }
            
            # Sauvegarder le résultat
            self._save_result(result)
            
            return result
        except Exception as e:
            logger.error(f"Erreur lors du matching direct: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def match_cv_to_job(self, cv_content: Union[bytes, BinaryIO], 
                             cv_filename: Optional[str], 
                             job_description: str) -> Dict[str, Any]:
        """
        Match un CV (fichier) avec une description de poste (texte).
        
        Args:
            cv_content: Contenu du fichier CV
            cv_filename: Nom du fichier CV
            job_description: Description du poste
            
        Returns:
            Dict: Résultat du matching
        """
        logger.info(f"Matching CV ({cv_filename}) avec description de poste")
        
        try:
            # Parser le CV et la fiche de poste de façon asynchrone
            parsed_cv_task = self.parsing_adapter.parse_cv(cv_content, cv_filename)
            parsed_job_task = self.parsing_adapter.parse_job(job_description)
            
            parsed_cv, parsed_job = await asyncio.gather(parsed_cv_task, parsed_job_task)
            
            # Préparer les données pour le matching
            candidate = self.parsing_adapter.prepare_for_matching(parsed_cv, "cv")
            job = self.parsing_adapter.prepare_for_matching(parsed_job, "job")
            
            # Exécuter le matching
            score, details = self.matcher.calculate_match(candidate, job)
            
            # Préparer le résultat
            result = {
                "status": "success",
                "candidate": {
                    "id": candidate.get("id", "unknown"),
                    "name": candidate.get("name", "Candidat")
                },
                "job": {
                    "id": job.get("id", "unknown"),
                    "title": job.get("title", "Poste")
                },
                "score": score,
                "details": details
            }
            
            # Sauvegarder le résultat
            self._save_result(result)
            
            return result
        except Exception as e:
            logger.error(f"Erreur lors du matching CV vers Job: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def match_job_to_cv(self, job_description: str, 
                             cv_content: Union[bytes, BinaryIO],
                             cv_filename: Optional[str]) -> Dict[str, Any]:
        """
        Match une description de poste (texte) avec un CV (fichier).
        
        Args:
            job_description: Description du poste
            cv_content: Contenu du fichier CV
            cv_filename: Nom du fichier CV
            
        Returns:
            Dict: Résultat du matching
        """
        logger.info(f"Matching description de poste avec CV ({cv_filename})")
        
        try:
            # Parser le CV et la fiche de poste de façon asynchrone
            parsed_job_task = self.parsing_adapter.parse_job(job_description)
            parsed_cv_task = self.parsing_adapter.parse_cv(cv_content, cv_filename)
            
            parsed_job, parsed_cv = await asyncio.gather(parsed_job_task, parsed_cv_task)
            
            # Préparer les données pour le matching
            job = self.parsing_adapter.prepare_for_matching(parsed_job, "job")
            candidate = self.parsing_adapter.prepare_for_matching(parsed_cv, "cv")
            
            # Exécuter le matching
            score, details = self.matcher.calculate_match(candidate, job)
            
            # Préparer le résultat
            result = {
                "status": "success",
                "candidate": {
                    "id": candidate.get("id", "unknown"),
                    "name": candidate.get("name", "Candidat")
                },
                "job": {
                    "id": job.get("id", "unknown"),
                    "title": job.get("title", "Poste")
                },
                "score": score,
                "details": details
            }
            
            # Sauvegarder le résultat
            self._save_result(result)
            
            return result
        except Exception as e:
            logger.error(f"Erreur lors du matching Job vers CV: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def match_job_file_to_cv(self, job_content: Union[bytes, BinaryIO],
                                  job_filename: Optional[str],
                                  cv_content: Union[bytes, BinaryIO],
                                  cv_filename: Optional[str]) -> Dict[str, Any]:
        """
        Match une fiche de poste (fichier) avec un CV (fichier).
        
        Args:
            job_content: Contenu du fichier de fiche de poste
            job_filename: Nom du fichier de fiche de poste
            cv_content: Contenu du fichier CV
            cv_filename: Nom du fichier CV
            
        Returns:
            Dict: Résultat du matching
        """
        logger.info(f"Matching fiche de poste ({job_filename}) avec CV ({cv_filename})")
        
        try:
            # Vérifier si l'adaptateur supporte le parsing de fichiers de poste
            if hasattr(self.parsing_adapter, "parse_job_file"):
                # Parser le fichier de fiche de poste et le CV de façon asynchrone
                parsed_job_task = self.parsing_adapter.parse_job_file(job_content, job_filename)
                parsed_cv_task = self.parsing_adapter.parse_cv(cv_content, cv_filename)
                
                parsed_job, parsed_cv = await asyncio.gather(parsed_job_task, parsed_cv_task)
            else:
                # Fallback: extraire le texte du fichier et utiliser parse_job
                # Note: Cette méthode est moins précise car elle ne traite pas les spécificités du format
                job_text = await self._extract_text_from_file(job_content)
                
                # Parser le texte de la fiche de poste et le CV de façon asynchrone
                parsed_job_task = self.parsing_adapter.parse_job(job_text)
                parsed_cv_task = self.parsing_adapter.parse_cv(cv_content, cv_filename)
                
                parsed_job, parsed_cv = await asyncio.gather(parsed_job_task, parsed_cv_task)
            
            # Préparer les données pour le matching
            job = self.parsing_adapter.prepare_for_matching(parsed_job, "job")
            candidate = self.parsing_adapter.prepare_for_matching(parsed_cv, "cv")
            
            # Exécuter le matching
            score, details = self.matcher.calculate_match(candidate, job)
            
            # Préparer le résultat
            result = {
                "status": "success",
                "candidate": {
                    "id": candidate.get("id", "unknown"),
                    "name": candidate.get("name", "Candidat")
                },
                "job": {
                    "id": job.get("id", "unknown"),
                    "title": job.get("title", "Poste")
                },
                "score": score,
                "details": details
            }
            
            # Sauvegarder le résultat
            self._save_result(result)
            
            return result
        except Exception as e:
            logger.error(f"Erreur lors du matching Job file vers CV: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _extract_text_from_file(self, file_content: Union[bytes, BinaryIO]) -> str:
        """
        Extrait le texte d'un fichier (PDF, DOCX, etc.).
        
        Args:
            file_content: Contenu du fichier
            
        Returns:
            str: Texte extrait du fichier
        """
        # TODO: Implémenter l'extraction de texte pour différents formats
        # Pour l'instant, convertir simplement en texte si c'est du binaire
        if isinstance(file_content, bytes):
            try:
                return file_content.decode("utf-8")
            except UnicodeDecodeError:
                # Si ce n'est pas un fichier texte, utiliser un extracteur approprié
                return "Texte non extrait du fichier binaire"
        
        # Si c'est un file-like object, le lire
        if hasattr(file_content, "read"):
            content = file_content.read()
            if isinstance(content, bytes):
                try:
                    return content.decode("utf-8")
                except UnicodeDecodeError:
                    return "Texte non extrait du fichier binaire"
            return str(content)
        
        return "Texte non extrait"
    
    def _save_result(self, result: Dict[str, Any]) -> None:
        """
        Sauvegarde un résultat de matching dans un fichier JSON.
        
        Args:
            result (Dict): Résultat du matching
        """
        timestamp = int(time.time())
        candidate_id = result.get("candidate", {}).get("id", "unknown")
        job_id = result.get("job", {}).get("id", "unknown")
        
        filename = os.path.join(self.results_dir, f"match_{candidate_id}_{job_id}_{timestamp}.json")
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Résultat du matching sauvegardé dans {filename}")
