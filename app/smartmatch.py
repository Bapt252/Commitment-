"""Module principal du moteur de matching bidirectionnel SmartMatch.
Ce module implémente l'algorithme de matching entre candidats et entreprises.
"""

import logging
import numpy as np
from app.compat import GoogleMapsClient
from app.semantic_analysis import SemanticAnalyzer

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartMatchEngine")

class SmartMatchEngine:
    """
    Moteur de matching bidirectionnel entre candidats et entreprises.
    Prend en compte:
    - Similarité sémantique des compétences
    - Temps de trajet (via Google Maps)
    - Préférences de travail à distance
    - Expérience professionnelle
    - Attentes salariales
    """
    
    def __init__(self):
        """
        Initialise le moteur de matching avec ses composants et pondérations par défaut.
        """
        # Composants
        self.maps_client = GoogleMapsClient()
        self.semantic_analyzer = SemanticAnalyzer()
        
        # Pondérations par défaut
        self.weights = {
            "skills": 0.35,
            "location": 0.25,
            "remote_policy": 0.15,
            "experience": 0.15,
            "salary": 0.10
        }
        
        # Seuils
        self.min_score_threshold = 0.6  # Score minimum pour considérer un match
        
        logger.info("Moteur SmartMatch initialisé avec succès")
    
    def set_weights(self, weights):
        """
        Définit les pondérations pour les différents critères de matching.
        
        Args:
            weights (dict): Dictionnaire des pondérations
        """
        # Vérifier que les pondérations sont valides
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            logger.warning(f"La somme des pondérations ({total}) n'est pas égale à 1. Normalisation automatique.")
            weights = {k: v / total for k, v in weights.items()}
        
        self.weights = weights
        logger.info(f"Pondérations mises à jour: {self.weights}")
    
    def match(self, candidates, companies):
        """
        Exécute l'algorithme de matching bidirectionnel.
        
        Args:
            candidates (list): Liste des candidats
            companies (list): Liste des entreprises
            
        Returns:
            list: Résultats de matching triés par score
        """
        logger.info(f"Début du matching entre {len(candidates)} candidats et {len(companies)} entreprises")
        
        results = []
        
        # Calculer tous les scores de matching
        for candidate in candidates:
            candidate_id = candidate.get("id", "unknown")
            logger.info(f"Évaluation du candidat {candidate_id}")
            
            for company in companies:
                company_id = company.get("id", "unknown")
                
                # Calculer le score de matching
                score, details = self._calculate_match_score(candidate, company)
                
                # Vérifier si le score est au-dessus du seuil
                if score >= self.min_score_threshold:
                    results.append({
                        "candidate_id": candidate_id,
                        "company_id": company_id,
                        "score": score,
                        "details": details
                    })
        
        # Trier les résultats par score décroissant
        results.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"Matching terminé. {len(results)} matches trouvés.")
        return results
    
    def _calculate_match_score(self, candidate, company):
        """
        Calcule le score de matching entre un candidat et une entreprise.
        
        Args:
            candidate (dict): Données du candidat
            company (dict): Données de l'entreprise
            
        Returns:
            tuple: (score global, détails des scores)
        """
        # Extraire les données
        candidate_skills = candidate.get("skills", [])
        company_skills = company.get("required_skills", [])
        candidate_location = candidate.get("location", "")
        company_location = company.get("location", "")
        candidate_remote = candidate.get("remote_preference", "hybrid")
        company_remote = company.get("remote_policy", "hybrid")
        candidate_experience = candidate.get("experience", 0)
        company_required_exp = company.get("required_experience", 0)
        candidate_salary = candidate.get("salary_expectation", 0)
        company_salary_min = company.get("salary_range", {}).get("min", 0)
        company_salary_max = company.get("salary_range", {}).get("max", 0)
        
        # 1. Score de compétences par analyse sémantique
        skills_score = self.semantic_analyzer.calculate_similarity(candidate_skills, company_skills)
        
        # 2. Score de localisation basé sur le temps de trajet
        location_score = 0.0
        
        # Règles pour le score de localisation basé sur les préférences de remote
        if candidate_remote == "full" and company_remote in ["full", "hybrid"]:
            # Si le candidat veut full remote et l'entreprise l'accepte
            location_score = 1.0
        elif company_remote == "office_only" and candidate_remote == "full":
            # Si l'entreprise exige présentiel et candidat veut full remote
            location_score = 0.0
        elif candidate_remote == "office" and company_remote == "office_only":
            # Si le candidat préfère le bureau et l'entreprise l'exige
            # Calculer score basé sur temps de trajet
            travel_time = self.maps_client.get_travel_time(candidate_location, company_location)
            if travel_time >= 0:
                # Pénaliser les longs trajets: score=1 pour 0min, score=0 pour >=90min
                location_score = max(0, 1 - (travel_time / 90))
            else:
                # Si impossible de calculer le temps de trajet
                location_score = 0.5
        elif candidate_remote == "hybrid" or company_remote == "hybrid":
            # Pour les configurations hybrides
            # Calculer un score mixte
            travel_time = self.maps_client.get_travel_time(candidate_location, company_location)
            if travel_time >= 0:
                # Pénalité moins forte pour hybride: score=1 pour 0min, score=0 pour >=120min
                location_score = max(0, 1 - (travel_time / 120))
            else:
                location_score = 0.5
        else:
            # Autres cas
            travel_time = self.maps_client.get_travel_time(candidate_location, company_location)
            if travel_time >= 0:
                location_score = max(0, 1 - (travel_time / 90))
            else:
                location_score = 0.5
        
        # 3. Score de compatibilité travail à distance
        remote_score = 0.0
        
        if candidate_remote == company_remote:
            # Correspondance parfaite
            remote_score = 1.0
        elif candidate_remote == "hybrid":
            # Candidat flexible
            if company_remote == "full":
                remote_score = 0.9
            elif company_remote == "office_only":
                remote_score = 0.7
        elif company_remote == "hybrid":
            # Entreprise flexible
            if candidate_remote == "full":
                remote_score = 0.8
            elif candidate_remote == "office":
                remote_score = 0.9
        elif candidate_remote == "full" and company_remote == "office_only":
            # Incompatibilité forte
            remote_score = 0.1
        elif candidate_remote == "office" and company_remote == "full":
            # Incompatibilité modérée
            remote_score = 0.3
        else:
            # Autres cas
            remote_score = 0.5
        
        # 4. Score d'expérience
        experience_score = 0.0
        
        if candidate_experience >= company_required_exp:
            # Le candidat a assez d'expérience
            # Bonus pour expérience proche de l'exigence (pas trop surqualifié)
            over_experience = candidate_experience - company_required_exp
            if over_experience <= 2:
                experience_score = 1.0
            else:
                # Légère pénalité si trop surqualifié
                experience_score = max(0.7, 1.0 - (over_experience - 2) * 0.05)
        else:
            # Le candidat manque d'expérience
            experience_gap = company_required_exp - candidate_experience
            if experience_gap <= 1:
                # Tolérance pour 1 an de moins
                experience_score = 0.8
            else:
                # Forte pénalité si gap important
                experience_score = max(0.1, 0.8 - (experience_gap - 1) * 0.2)
        
        # 5. Score de salaire
        salary_score = 0.0
        
        if company_salary_min <= candidate_salary <= company_salary_max:
            # Dans la fourchette: score parfait
            salary_score = 1.0
        elif candidate_salary < company_salary_min:
            # En dessous: potentiellement avantageux pour l'entreprise mais pas idéal
            gap_ratio = candidate_salary / company_salary_min
            salary_score = max(0.5, gap_ratio)
        else:
            # Au-dessus: potentiellement problématique
            gap_ratio = company_salary_max / candidate_salary
            salary_score = max(0.1, gap_ratio * 0.9)
        
        # Calcul du score final pondéré
        final_score = (
            self.weights["skills"] * skills_score +
            self.weights["location"] * location_score +
            self.weights["remote_policy"] * remote_score +
            self.weights["experience"] * experience_score +
            self.weights["salary"] * salary_score
        )
        
        # Détails pour analyse
        details = {
            "skills_score": skills_score,
            "location_score": location_score,
            "remote_score": remote_score,
            "experience_score": experience_score,
            "salary_score": salary_score,
            "missing_skills": self.semantic_analyzer.get_skill_gaps(candidate_skills, company_skills),
            "travel_time_minutes": self.maps_client.get_travel_time(candidate_location, company_location) if location_score < 1 else "N/A"
        }
        
        return final_score, details