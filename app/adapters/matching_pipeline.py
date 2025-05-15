#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Pipeline d'intégration pour le matching entre CVs et fiches de poste."""

import logging
import json
import os
import time
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple

from app.core.smart_match import SmartMatcher
from app.adapters.parsing_adapter import ParsingAdapter

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MatchingPipeline")

class MatchingPipeline:
    """
    Pipeline d'intégration pour le matching entre CVs et fiches de poste.
    """
    
    def __init__(self, cv_parser_url: str = "http://localhost:5051", 
                 job_parser_url: str = "http://localhost:5055",
                 results_dir: str = "matching_results"):
        """
        Initialise le pipeline de matching.
        
        Args:
            cv_parser_url (str): URL du service de parsing de CV
            job_parser_url (str): URL du service de parsing de fiches de poste
            results_dir (str): Répertoire pour stocker les résultats
        """
        self.parsing_adapter = ParsingAdapter(cv_parser_url, job_parser_url)
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
            # Parser les données de façon asynchrone
            parsed_cv_task = self.parsing_adapter.parse_cv(cv_data)
            parsed_job_task = self.parsing_adapter.parse_job(job_data)
            
            parsed_cv, parsed_job = await asyncio.gather(parsed_cv_task, parsed_job_task)
            
            if not parsed_cv or not parsed_job:
                logger.error("Erreur lors du parsing des données")
                return {"status": "error", "message": "Erreur lors du parsing des données"}
            
            # Convertir au format SmartMatch
            candidate = self.parsing_adapter.cv_to_candidate(parsed_cv)
            company = self.parsing_adapter.job_to_company(parsed_job)
            
            # Exécuter le matching
            score, details = self.matcher.calculate_match(candidate, company)
            
            # Préparer le résultat
            result = {
                "status": "success",
                "candidate": {
                    "id": candidate["id"],
                    "name": candidate["name"]
                },
                "job": {
                    "id": company["id"],
                    "name": company["name"]
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
