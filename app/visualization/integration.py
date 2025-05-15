"""
Intégration du visualiseur de matching avec le moteur SmartMatch.
Ce module permet de générer facilement des visualisations à partir des résultats du matching.
"""

import os
import logging
from typing import List, Dict, Any
from app.smartmatch import SmartMatchEngine
from app.visualization.match_visualizer import MatchVisualizer

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartMatchVisualization")

class SmartMatchWithVisualization:
    """
    Classe qui intègre le moteur SmartMatch avec des capacités de visualisation.
    Permet de facilement générer des tableaux de bord et des rapports.
    """
    
    def __init__(self, output_dir: str = "output/dashboard"):
        """
        Initialise un système de matching avec visualisation.
        
        Args:
            output_dir (str): Répertoire où les visualisations seront générées
        """
        try:
            self.match_engine = SmartMatchEngine()
            logger.info("Moteur SmartMatch initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du moteur SmartMatch: {e}")
            raise
            
        self.visualizer = MatchVisualizer(output_dir=output_dir)
    
    def set_weights(self, weights: Dict[str, float]):
        """
        Définit les pondérations pour les différents critères de matching.
        
        Args:
            weights (dict): Dictionnaire des pondérations
        """
        self.match_engine.set_weights(weights)
    
    def match_and_visualize(self, candidates: List[Dict[str, Any]], companies: List[Dict[str, Any]], 
                           generate_html: bool = True, export_json: bool = True) -> Dict[str, Any]:
        """
        Exécute le matching et génère des visualisations des résultats.
        
        Args:
            candidates (list): Liste des candidats
            companies (list): Liste des entreprises
            generate_html (bool): Si True, génère un tableau de bord HTML
            export_json (bool): Si True, exporte les résultats au format JSON
            
        Returns:
            dict: Informations sur les chemins des visualisations générées
        """
        # Vérifier que les données d'entrée sont valides
        if not candidates or not companies:
            logger.warning("Données d'entrée vides: aucun candidat ou aucune entreprise")
            return {
                "match_results": [],
                "output_paths": {},
                "report": {}
            }
        
        # Effectuer le matching
        logger.info(f"Exécution du matching bidirectionnel entre {len(candidates)} candidats et {len(companies)} entreprises")
        try:
            match_results = self.match_engine.match(candidates, companies)
            logger.info(f"{len(match_results)} matches trouvés")
        except Exception as e:
            logger.error(f"Erreur lors du matching: {e}")
            raise
        
        # Enrichir les résultats avec les informations de localisation pour la visualisation
        for match in match_results:
            # Trouver le candidat et l'entreprise correspondants
            candidate = next((c for c in candidates if c.get("id") == match["candidate_id"]), {})
            company = next((c for c in companies if c.get("id") == match["company_id"]), {})
            
            # Ajouter les informations de localisation
            match["candidate_location"] = candidate.get("location", "Non spécifié")
            match["company_location"] = company.get("location", "Non spécifié")
            
            # S'assurer que les détails contiennent des compétences communes
            if "details" in match and "missing_skills" in match["details"]:
                candidate_skills = set(candidate.get("skills", []))
                company_skills = set(company.get("required_skills", []))
                match["details"]["matched_skills"] = list(candidate_skills.intersection(company_skills))
        
        # Générer les visualisations
        output_paths = {}
        
        if generate_html:
            dashboard_path = self.visualizer.generate_dashboard(match_results)
            output_paths["dashboard"] = dashboard_path
            logger.info(f"Tableau de bord HTML généré: {dashboard_path}")
        
        if export_json:
            json_path = self.visualizer.export_json(match_results)
            output_paths["json"] = json_path
            logger.info(f"Données JSON exportées: {json_path}")
        
        # Générer le rapport statistique
        report = self.visualizer.generate_report(match_results)
        output_paths["report"] = report
        
        return {
            "match_results": match_results,
            "output_paths": output_paths,
            "report": report
        }
    
    def explain_match(self, match_result: Dict[str, Any]) -> str:
        """
        Génère une explication détaillée d'un résultat de matching spécifique.
        
        Args:
            match_result (dict): Un résultat de matching individuel
            
        Returns:
            str: Explication détaillée du matching
        """
        if not match_result:
            return "Aucun résultat de matching à expliquer."
        
        explanation = f"Analyse du match entre Candidat {match_result['candidate_id']} et Entreprise {match_result['company_id']}\n"
        explanation += f"Score global: {match_result['score']:.2f} (seuil minimum: {self.match_engine.min_score_threshold})\n\n"
        
        details = match_result.get("details", {})
        weights = self.match_engine.weights
        
        # Expliquer chaque composante
        explanation += "Détail des scores par critère:\n"
        explanation += f"- Compétences: {details.get('skills_score', 'N/A'):.2f} (pondération: {weights['skills']:.2f})\n"
        explanation += f"- Localisation: {details.get('location_score', 'N/A'):.2f} (pondération: {weights['location']:.2f})\n"
        explanation += f"- Politique de télétravail: {details.get('remote_score', 'N/A'):.2f} (pondération: {weights['remote_policy']:.2f})\n"
        explanation += f"- Expérience: {details.get('experience_score', 'N/A'):.2f} (pondération: {weights['experience']:.2f})\n"
        explanation += f"- Salaire: {details.get('salary_score', 'N/A'):.2f} (pondération: {weights['salary']:.2f})\n\n"
        
        # Compétences manquantes
        missing_skills = details.get("missing_skills", [])
        if missing_skills:
            explanation += "Compétences requises manquantes:\n"
            for skill in missing_skills:
                explanation += f"- {skill}\n"
        else:
            explanation += "Aucune compétence requise manquante.\n"
        
        # Compétences communes
        matched_skills = details.get("matched_skills", [])
        if matched_skills:
            explanation += "\nCompétences communes:\n"
            for skill in matched_skills:
                explanation += f"- {skill}\n"
        
        # Temps de trajet
        travel_time = details.get("travel_time_minutes", "N/A")
        if travel_time != "N/A":
            explanation += f"\nTemps de trajet estimé: {travel_time} minutes\n"
            if travel_time < 30:
                explanation += "Trajet court, très favorable.\n"
            elif travel_time < 60:
                explanation += "Trajet raisonnable.\n"
            else:
                explanation += "Trajet long, potentiellement problématique.\n"
        
        return explanation
