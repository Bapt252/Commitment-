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
        
        # Pondérations par défaut
        self.weights = {
            "skills": 0.35,
            "location": 0.25,
            "remote_policy": 0.15,
            "experience": 0.15,
            "salary": 0.10
        }
    
    def set_weights(self, weights: Dict[str, float]):
        """
        Définit les pondérations pour les différents critères de matching.
        
        Args:
            weights (dict): Dictionnaire des pondérations
        """
        # Vérifier si la méthode set_weights existe dans le moteur
        if hasattr(self.match_engine, 'set_weights') and callable(getattr(self.match_engine, 'set_weights')):
            self.match_engine.set_weights(weights)
            logger.info(f"Pondérations mises à jour via le moteur: {weights}")
        else:
            # La méthode n'existe pas, nous stockons simplement les poids localement
            # Vérifier que les pondérations sont valides
            total = sum(weights.values())
            if abs(total - 1.0) > 0.01:
                logger.warning(f"La somme des pondérations ({total}) n'est pas égale à 1. Normalisation automatique.")
                weights = {k: v / total for k, v in weights.items()}
            
            # Directement modifier les poids dans le moteur si possible
            if hasattr(self.match_engine, 'weights'):
                self.match_engine.weights = weights
                logger.info(f"Pondérations mises à jour directement: {weights}")
            else:
                # Si même l'attribut weights n'existe pas, on stocke localement
                self.weights = weights
                logger.warning("Le moteur ne supporte pas la modification des pondérations. Stockage local uniquement.")
    
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
            # Essayer d'appeler la méthode match si elle existe
            if hasattr(self.match_engine, 'match') and callable(getattr(self.match_engine, 'match')):
                match_results = self.match_engine.match(candidates, companies)
            else:
                # Version de secours pour le demo - simuler des matches
                logger.warning("La méthode 'match' n'existe pas dans le moteur. Utilisation de la version de démonstration.")
                match_results = self._demo_matching(candidates, companies)
            
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
    
    def _demo_matching(self, candidates, companies):
        """
        Version de démo du matching qui génère des résultats factices.
        
        Args:
            candidates (list): Liste des candidats
            companies (list): Liste des entreprises
            
        Returns:
            list: Résultats de matching simulés
        """
        import random
        
        results = []
        min_score_threshold = 0.6
        
        for candidate in candidates:
            candidate_id = candidate.get("id", "unknown")
            candidate_skills = set(candidate.get("skills", []))
            
            for company in companies:
                company_id = company.get("id", "unknown")
                company_skills = set(company.get("required_skills", []))
                
                # Calculer des scores aléatoires mais réalistes
                skills_score = len(candidate_skills.intersection(company_skills)) / max(1, len(company_skills))
                skills_score = min(1.0, skills_score + random.uniform(0, 0.3))
                
                location_score = random.uniform(0.3, 1.0)
                remote_score = random.uniform(0.3, 1.0)
                experience_score = random.uniform(0.3, 1.0)
                salary_score = random.uniform(0.3, 1.0)
                
                # Calcul du score global avec les pondérations
                final_score = (
                    self.weights.get("skills", 0.35) * skills_score +
                    self.weights.get("location", 0.25) * location_score +
                    self.weights.get("remote_policy", 0.15) * remote_score +
                    self.weights.get("experience", 0.15) * experience_score +
                    self.weights.get("salary", 0.10) * salary_score
                )
                
                # Arrondir le score
                final_score = round(final_score, 2)
                
                # Ajouter aux résultats si le score est au-dessus du seuil
                if final_score >= min_score_threshold:
                    missing_skills = list(company_skills - candidate_skills)
                    
                    result = {
                        "candidate_id": candidate_id,
                        "company_id": company_id,
                        "score": final_score,
                        "details": {
                            "skills_score": round(skills_score, 2),
                            "location_score": round(location_score, 2),
                            "remote_score": round(remote_score, 2),
                            "experience_score": round(experience_score, 2),
                            "salary_score": round(salary_score, 2),
                            "missing_skills": missing_skills,
                            "travel_time_minutes": int(random.uniform(15, 90)) if location_score < 0.9 else "N/A"
                        }
                    }
                    results.append(result)
        
        # Trier par score décroissant
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
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
        explanation += f"Score global: {match_result['score']:.2f} (seuil minimum: 0.6)\n\n"
        
        details = match_result.get("details", {})
        weights = self.weights if hasattr(self.match_engine, 'weights') else self.weights
        
        # Expliquer chaque composante
        explanation += "Détail des scores par critère:\n"
        explanation += f"- Compétences: {details.get('skills_score', 0):.2f} (pondération: {weights.get('skills', 0.35):.2f})\n"
        explanation += f"- Localisation: {details.get('location_score', 0):.2f} (pondération: {weights.get('location', 0.25):.2f})\n"
        explanation += f"- Politique de télétravail: {details.get('remote_score', 0):.2f} (pondération: {weights.get('remote_policy', 0.15):.2f})\n"
        explanation += f"- Expérience: {details.get('experience_score', 0):.2f} (pondération: {weights.get('experience', 0.15):.2f})\n"
        explanation += f"- Salaire: {details.get('salary_score', 0):.2f} (pondération: {weights.get('salary', 0.10):.2f})\n\n"
        
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
