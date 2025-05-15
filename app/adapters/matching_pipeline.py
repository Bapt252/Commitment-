#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Pipeline d'intégration pour le matching entre CVs et fiches de poste."""

import logging
import json
import os
import time
from typing import Dict, List, Any, Optional, Union, Tuple

from app.smartmatch import SmartMatchEngine
from app.adapters.parsing_adapter import ParsingAdapter
from app.insight_generator import InsightGenerator

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
        self.matcher = SmartMatchEngine()
        self.insight_generator = InsightGenerator()
        self.results_dir = results_dir
        
        # Créer le répertoire des résultats s'il n'existe pas
        os.makedirs(results_dir, exist_ok=True)
        
        logger.info("Pipeline de matching initialisé avec succès")
    
    def run_full_pipeline(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Exécute le pipeline complet de matching.
        
        Returns:
            Tuple[List, List]: Résultats du matching et insights générés
        """
        logger.info("Démarrage du pipeline de matching complet")
        
        # Étape 1: Convertir les données des CVs et fiches de poste
        start_time = time.time()
        candidates = self.parsing_adapter.convert_all_cvs()
        companies = self.parsing_adapter.convert_all_jobs()
        conversion_time = time.time() - start_time
        logger.info(f"Conversion des données terminée en {conversion_time:.2f} secondes")
        
        # Étape 2: Exécuter le matching
        start_time = time.time()
        matching_results = self.matcher.match(candidates, companies)
        matching_time = time.time() - start_time
        logger.info(f"Matching terminé en {matching_time:.2f} secondes. {len(matching_results)} matchs trouvés.")
        
        # Étape 3: Générer des insights
        start_time = time.time()
        insights = self.insight_generator.generate_insights(matching_results)
        insights_time = time.time() - start_time
        logger.info(f"Génération des insights terminée en {insights_time:.2f} secondes. {len(insights)} insights générés.")
        
        # Étape 4: Sauvegarder les résultats
        self._save_results(matching_results, insights)
        
        return matching_results, insights
    
    def match_specific(self, cv_id: str, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Exécute un matching spécifique entre un CV et une fiche de poste.
        
        Args:
            cv_id (str): Identifiant du CV
            job_id (str): Identifiant de la fiche de poste
            
        Returns:
            Dict: Résultat du matching, ou None en cas d'erreur
        """
        logger.info(f"Démarrage du matching spécifique entre CV {cv_id} et fiche de poste {job_id}")
        
        # Récupérer et convertir les données
        cv_data = self.parsing_adapter.get_cv_data(cv_id)
        job_data = self.parsing_adapter.get_job_data(job_id)
        
        if not cv_data or not job_data:
            logger.error("Impossible de récupérer les données nécessaires")
            return None
        
        candidate = self.parsing_adapter.cv_to_candidate(cv_data)
        company = self.parsing_adapter.job_to_company(job_data)
        
        # Exécuter le matching
        results = self.matcher.match([candidate], [company])
        
        if not results:
            logger.warning("Aucun résultat de matching trouvé")
            return None
        
        # Générer des insights pour ce matching spécifique
        insights = self.insight_generator.generate_insights(results)
        
        # Enrichir le résultat avec les insights
        result = results[0]
        result["insights"] = insights
        
        # Sauvegarder le résultat
        self._save_specific_result(result, cv_id, job_id)
        
        return result
    
    def match_cv_with_all_jobs(self, cv_id: str) -> List[Dict[str, Any]]:
        """
        Exécute un matching entre un CV spécifique et toutes les fiches de poste.
        
        Args:
            cv_id (str): Identifiant du CV
            
        Returns:
            List[Dict]: Résultats du matching
        """
        logger.info(f"Démarrage du matching du CV {cv_id} avec toutes les fiches de poste")
        
        # Récupérer et convertir les données
        cv_data = self.parsing_adapter.get_cv_data(cv_id)
        if not cv_data:
            logger.error(f"Impossible de récupérer les données du CV {cv_id}")
            return []
        
        candidate = self.parsing_adapter.cv_to_candidate(cv_data)
        companies = self.parsing_adapter.convert_all_jobs()
        
        # Exécuter le matching
        results = self.matcher.match([candidate], companies)
        logger.info(f"Matching terminé. {len(results)} matchs trouvés pour le CV {cv_id}.")
        
        # Sauvegarder les résultats
        self._save_cv_results(results, cv_id)
        
        return results
    
    def match_job_with_all_cvs(self, job_id: str) -> List[Dict[str, Any]]:
        """
        Exécute un matching entre une fiche de poste spécifique et tous les CVs.
        
        Args:
            job_id (str): Identifiant de la fiche de poste
            
        Returns:
            List[Dict]: Résultats du matching
        """
        logger.info(f"Démarrage du matching de la fiche de poste {job_id} avec tous les CVs")
        
        # Récupérer et convertir les données
        job_data = self.parsing_adapter.get_job_data(job_id)
        if not job_data:
            logger.error(f"Impossible de récupérer les données de la fiche de poste {job_id}")
            return []
        
        company = self.parsing_adapter.job_to_company(job_data)
        candidates = self.parsing_adapter.convert_all_cvs()
        
        # Exécuter le matching
        results = self.matcher.match(candidates, [company])
        logger.info(f"Matching terminé. {len(results)} matchs trouvés pour la fiche de poste {job_id}.")
        
        # Sauvegarder les résultats
        self._save_job_results(results, job_id)
        
        return results
    
    def _save_results(self, matching_results: List[Dict[str, Any]], insights: List[Dict[str, Any]]) -> None:
        """
        Sauvegarde les résultats du matching dans des fichiers JSON.
        
        Args:
            matching_results (List[Dict]): Résultats du matching
            insights (List[Dict]): Insights générés
        """
        timestamp = int(time.time())
        
        # Sauvegarder les résultats du matching
        results_file = os.path.join(self.results_dir, f"matching_results_{timestamp}.json")
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(matching_results, f, ensure_ascii=False, indent=2)
        
        # Sauvegarder les insights
        insights_file = os.path.join(self.results_dir, f"insights_{timestamp}.json")
        with open(insights_file, "w", encoding="utf-8") as f:
            json.dump(insights, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Résultats du matching sauvegardés dans {results_file}")
        logger.info(f"Insights sauvegardés dans {insights_file}")
    
    def _save_specific_result(self, result: Dict[str, Any], cv_id: str, job_id: str) -> None:
        """
        Sauvegarde le résultat d'un matching spécifique.
        
        Args:
            result (Dict): Résultat du matching
            cv_id (str): Identifiant du CV
            job_id (str): Identifiant de la fiche de poste
        """
        timestamp = int(time.time())
        filename = os.path.join(self.results_dir, f"match_{cv_id}_{job_id}_{timestamp}.json")
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Résultat du matching spécifique sauvegardé dans {filename}")
    
    def _save_cv_results(self, results: List[Dict[str, Any]], cv_id: str) -> None:
        """
        Sauvegarde les résultats du matching pour un CV spécifique.
        
        Args:
            results (List[Dict]): Résultats du matching
            cv_id (str): Identifiant du CV
        """
        timestamp = int(time.time())
        filename = os.path.join(self.results_dir, f"cv_{cv_id}_matches_{timestamp}.json")
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Résultats du matching pour le CV {cv_id} sauvegardés dans {filename}")
    
    def _save_job_results(self, results: List[Dict[str, Any]], job_id: str) -> None:
        """
        Sauvegarde les résultats du matching pour une fiche de poste spécifique.
        
        Args:
            results (List[Dict]): Résultats du matching
            job_id (str): Identifiant de la fiche de poste
        """
        timestamp = int(time.time())
        filename = os.path.join(self.results_dir, f"job_{job_id}_matches_{timestamp}.json")
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Résultats du matching pour la fiche de poste {job_id} sauvegardés dans {filename}")
