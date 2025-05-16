"""
SmartMatch Extended - Version étendue de SmartMatch avec prise en compte des questionnaires
------------------------------------------------------------------------------------
Cette version de SmartMatch intègre des fonctionnalités supplémentaires pour
prendre en compte les données des questionnaires candidat et client.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple

from smartmatch import SmartMatcher

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartMatcherExtended(SmartMatcher):
    """
    Version étendue de SmartMatcher avec prise en compte des questionnaires
    """
    
    def __init__(self, api_key: str = None, use_cache: bool = True, cache_size: int = 1000):
        """
        Initialisation de SmartMatcherExtended
        
        Args:
            api_key (str): Clé API Google Maps pour les calculs de distance
            use_cache (bool): Activer le cache pour les calculs de distance
            cache_size (int): Taille du cache pour les calculs de distance
        """
        # Initialisation de la classe parent
        super().__init__(api_key, use_cache, cache_size)
        
        # Facteurs de pondération étendus
        self.extended_weights = {
            "skills": 0.35,            # Légèrement réduit pour donner de la place aux nouveaux critères
            "location": 0.20,          # Légèrement réduit
            "experience": 0.15,        # Maintenu
            "education": 0.10,         # Maintenu
            "preferences": 0.10,       # Maintenu
            "environment": 0.05,       # Nouveau facteur pour l'environnement de travail
            "commute_preference": 0.05 # Nouveau facteur pour les préférences de trajet
        }
        
        logger.info("SmartMatcherExtended initialisé avec succès")
    
    def calculate_environment_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule la correspondance entre les préférences d'environnement de travail
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Si les informations sont manquantes, score neutre
        if "office_preference" not in candidate or "work_environment" not in job:
            return 0.5
        
        candidate_preference = candidate["office_preference"]
        job_environment = job["work_environment"]
        
        # Si le candidat n'a pas de préférence, c'est bon
        if candidate_preference == "no-preference":
            return 0.8
        
        # Si les préférences correspondent exactement
        if candidate_preference == job_environment:
            return 1.0
        
        # Sinon, le score est faible
        return 0.3
    
    def calculate_commute_preference_match(self, candidate: Dict[str, Any], job: Dict[str, Any], travel_time: int = None) -> float:
        """
        Calcule la correspondance entre les préférences de temps de trajet et le temps réel
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            travel_time (int, optional): Temps de trajet calculé en minutes
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Si le travail est à distance, score parfait
        if candidate.get("remote_work", False) and job.get("offers_remote", False):
            return 1.0
        
        # Si le temps de trajet n'est pas fourni, le calculer
        if travel_time is None:
            candidate_location = candidate.get("location", "")
            job_location = job.get("location", "")
            
            if not candidate_location or not job_location:
                return 0.5  # Score neutre si pas de localisation
            
            travel_time = self.calculate_travel_time(candidate_location, job_location)
        
        # Récupérer les préférences de temps de trajet
        transport_preferences = candidate.get("transport_preferences", {})
        
        # Si aucune préférence définie, utiliser le calcul standard du temps de trajet
        if not transport_preferences:
            # Convertir le temps de trajet en score comme dans la méthode parent
            if travel_time <= 30:
                return 1.0
            elif travel_time <= 60:
                return 0.8
            elif travel_time <= 90:
                return 0.6
            elif travel_time <= 120:
                return 0.4
            else:
                return 0.2
        
        # Déterminer le temps maximum acceptable pour les modes de transport disponibles
        max_acceptable_time = None
        
        # Vérifier d'abord le mode de transport véhicule personnel
        if "vehicle" in transport_preferences:
            max_acceptable_time = transport_preferences["vehicle"]
        
        # Puis le transport en commun (priorité plus basse)
        elif "public-transport" in transport_preferences:
            max_acceptable_time = transport_preferences["public-transport"]
        
        # Puis le vélo (priorité encore plus basse)
        elif "bike" in transport_preferences:
            max_acceptable_time = transport_preferences["bike"]
        
        # Enfin, la marche (priorité la plus basse)
        elif "walking" in transport_preferences:
            max_acceptable_time = transport_preferences["walking"]
        
        # Si aucun temps maximum défini, utiliser le calcul standard
        if not max_acceptable_time:
            return super().calculate_location_match(candidate, job)
        
        # Calculer le score en fonction du temps de trajet et du maximum acceptable
        if travel_time <= max_acceptable_time:
            # Dans les limites acceptables, score proportionnel
            ratio = 1 - (travel_time / max_acceptable_time)
            return 0.7 + (0.3 * ratio)  # Entre 0.7 et 1.0
        else:
            # Au-delà des limites acceptables, score dégressif
            ratio = max_acceptable_time / travel_time
            return max(0.2, ratio * 0.7)  # Entre 0.2 et 0.7
    
    def calculate_motivation_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule la correspondance entre les motivations du candidat et les caractéristiques du poste
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        motivation_priorities = candidate.get("motivation_priorities", [])
        if not motivation_priorities:
            return 0.5  # Score neutre si pas de priorités
        
        scores = []
        
        # Analyser chaque motivation prioritaire
        for i, motivation in enumerate(motivation_priorities[:3]):  # Considérer seulement les 3 premières
            priority_weight = 1.0 - (i * 0.2)  # Poids dégressif: 1.0, 0.8, 0.6
            
            if motivation == "remuneration":
                # Vérifier si le salaire proposé correspond aux attentes
                if "salary_expectation" in candidate and "salary_range" in job:
                    candidate_salary = candidate["salary_expectation"]
                    job_min = job["salary_range"].get("min", 0)
                    job_max = job["salary_range"].get("max", 0)
                    
                    if job_min <= candidate_salary <= job_max:
                        scores.append(1.0 * priority_weight)
                    elif candidate_salary < job_min:
                        # Le candidat demande moins que le minimum (bonne situation)
                        scores.append(0.9 * priority_weight)
                    else:
                        # Le candidat demande plus que le maximum
                        ratio = min(1.0, job_max / candidate_salary if candidate_salary > 0 else 0)
                        scores.append(ratio * priority_weight)
            
            elif motivation == "evolution":
                # Vérifier si des perspectives d'évolution sont mentionnées
                if job.get("evolution_perspectives"):
                    scores.append(1.0 * priority_weight)
                else:
                    scores.append(0.5 * priority_weight)
            
            elif motivation == "flexibility":
                # Vérifier si le poste offre de la flexibilité (télétravail, etc.)
                if job.get("offers_remote"):
                    scores.append(1.0 * priority_weight)
                else:
                    # Vérifier dans les avantages
                    benefits = job.get("job-benefits-value", "").lower()
                    if "flexib" in benefits or "horaire" in benefits or "temps" in benefits:
                        scores.append(0.8 * priority_weight)
                    else:
                        scores.append(0.3 * priority_weight)
            
            elif motivation == "location":
                # Utiliser le score de localisation/trajet
                location_score = self.calculate_location_match(candidate, job)
                scores.append(location_score * priority_weight)
            
            elif motivation == "other":
                # Utiliser la valeur spécifiée dans other_motivation
                # Cette partie serait à personnaliser selon les besoins
                scores.append(0.5 * priority_weight)  # Score neutre par défaut
        
        # Calculer le score moyen
        if scores:
            return sum(scores) / sum(1.0 - (i * 0.2) for i in range(min(3, len(motivation_priorities))))
        else:
            return 0.5  # Score neutre si aucun score calculé
    
    def calculate_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule le score global de correspondance entre un candidat et une offre d'emploi
        avec prise en compte des fonctionnalités étendues
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            Dict: Résultat du matching avec scores et insights
        """
        # Calculer les scores des catégories de base
        skill_score = self.calculate_skill_match(candidate, job)
        location_score = self.calculate_location_match(candidate, job)
        experience_score = self.calculate_experience_match(candidate, job)
        education_score = self.calculate_education_match(candidate, job)
        preference_score = self.calculate_preference_match(candidate, job)
        
        # Calculer les scores des nouvelles catégories
        environment_score = self.calculate_environment_match(candidate, job)
        
        # Pour le score de préférence de trajet, réutiliser le temps de trajet calculé
        candidate_location = candidate.get("location", "")
        job_location = job.get("location", "")
        travel_time = None
        
        if candidate_location and job_location and not (candidate.get("remote_work", False) and job.get("offers_remote", False)):
            travel_time = self.calculate_travel_time(candidate_location, job_location)
        
        commute_preference_score = self.calculate_commute_preference_match(candidate, job, travel_time)
        
        # Calculer le score de motivation si les données sont disponibles
        motivation_score = self.calculate_motivation_match(candidate, job)
        
        # Si les facteurs de motivation sont pris en compte, ajuster les pondérations
        if "motivation_priorities" in candidate and candidate["motivation_priorities"]:
            extended_weights = self.extended_weights.copy()
            extended_weights["preferences"] = 0.05  # Réduire pour faire de la place
            extended_weights["motivation"] = 0.05  # Ajouter le nouveau facteur
        else:
            extended_weights = self.extended_weights.copy()
            extended_weights["motivation"] = 0.0  # Pas de pondération pour les motivations
        
        # Normaliser les pondérations
        total_weight = sum(extended_weights.values())
        normalized_weights = {k: v / total_weight for k, v in extended_weights.items()}
        
        # Calculer le score global pondéré avec les poids étendus
        overall_score = (
            skill_score * normalized_weights["skills"] +
            location_score * normalized_weights["location"] +
            experience_score * normalized_weights["experience"] +
            education_score * normalized_weights["education"] +
            preference_score * normalized_weights["preferences"] +
            environment_score * normalized_weights["environment"] +
            commute_preference_score * normalized_weights["commute_preference"]
        )
        
        # Ajouter le score de motivation si applicable
        if "motivation" in normalized_weights and normalized_weights["motivation"] > 0:
            overall_score += motivation_score * normalized_weights["motivation"]
        
        # Générer des insights (étendus avec les nouveaux critères)
        insights = self.generate_extended_insights(
            candidate, job,
            skill_score, location_score, experience_score, 
            education_score, preference_score,
            environment_score, commute_preference_score,
            motivation_score if "motivation_priorities" in candidate else None
        )
        
        # Construire le résultat avec les scores étendus
        result = {
            "candidate_id": candidate.get("id", ""),
            "job_id": job.get("id", ""),
            "overall_score": round(overall_score, 2),
            "category_scores": {
                "skills": round(skill_score, 2),
                "location": round(location_score, 2),
                "experience": round(experience_score, 2),
                "education": round(education_score, 2),
                "preferences": round(preference_score, 2),
                "environment": round(environment_score, 2),
                "commute_preference": round(commute_preference_score, 2)
            },
            "insights": insights
        }
        
        # Ajouter le score de motivation si applicable
        if "motivation_priorities" in candidate and candidate["motivation_priorities"]:
            result["category_scores"]["motivation"] = round(motivation_score, 2)
        
        return result
    
    def generate_extended_insights(self, 
                                  candidate: Dict[str, Any], 
                                  job: Dict[str, Any],
                                  skill_score: float,
                                  location_score: float,
                                  experience_score: float,
                                  education_score: float,
                                  preference_score: float,
                                  environment_score: float,
                                  commute_preference_score: float,
                                  motivation_score: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Génère des insights détaillés sur le match entre un candidat et une offre d'emploi,
        incluant les nouveaux critères
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            skill_score (float): Score de compétences
            location_score (float): Score de localisation
            experience_score (float): Score d'expérience
            education_score (float): Score d'éducation
            preference_score (float): Score de préférences
            environment_score (float): Score d'environnement de travail
            commute_preference_score (float): Score de préférence de trajet
            motivation_score (float, optional): Score de motivation
            
        Returns:
            List[Dict]: Liste d'insights avec type, message et score
        """
        # Récupérer les insights de base
        insights = super().generate_insights(
            candidate, job,
            skill_score, location_score, experience_score, 
            education_score, preference_score
        )
        
        # Ajouter des insights pour l'environnement de travail
        if "office_preference" in candidate and "work_environment" in job:
            candidate_preference = candidate["office_preference"]
            job_environment = job["work_environment"]
            
            if candidate_preference == job_environment:
                insights.append({
                    "type": "environment_match",
                    "message": f"Environnement de travail {job_environment} correspondant aux préférences",
                    "score": environment_score,
                    "category": "strength"
                })
            elif candidate_preference != "no-preference" and candidate_preference != job_environment:
                insights.append({
                    "type": "environment_mismatch",
                    "message": f"Préférence pour un environnement {candidate_preference} mais le poste propose {job_environment}",
                    "score": environment_score,
                    "category": "mismatch"
                })
        
        # Ajouter des insights pour les préférences de trajet
        if "transport_preferences" in candidate and candidate["transport_preferences"]:
            # Si travail à distance, tout va bien
            if candidate.get("remote_work", False) and job.get("offers_remote", False):
                pass  # Déjà couvert par les insights de base
            else:
                # Calculer le temps de trajet
                candidate_location = candidate.get("location", "")
                job_location = job.get("location", "")
                
                if candidate_location and job_location:
                    travel_time = self.calculate_travel_time(candidate_location, job_location)
                    
                    # Trouver le temps maximum acceptable pour les modes de transport disponibles
                    transport_preferences = candidate["transport_preferences"]
                    max_time = 0
                    max_mode = ""
                    
                    for mode, time in transport_preferences.items():
                        if int(time) > max_time:
                            max_time = int(time)
                            max_mode = mode
                    
                    if max_time > 0:
                        if travel_time <= max_time:
                            insights.append({
                                "type": "commute_preference_match",
                                "message": f"Temps de trajet de {travel_time} minutes, dans la limite acceptable de {max_time} minutes",
                                "score": commute_preference_score,
                                "category": "strength"
                            })
                        else:
                            insights.append({
                                "type": "commute_preference_mismatch",
                                "message": f"Temps de trajet de {travel_time} minutes, supérieur à la limite acceptable de {max_time} minutes",
                                "score": commute_preference_score,
                                "category": "weakness"
                            })
        
        # Ajouter des insights pour les motivations
        if motivation_score is not None and "motivation_priorities" in candidate:
            motivation_priorities = candidate["motivation_priorities"]
            
            if motivation_priorities and len(motivation_priorities) >= 1:
                top_motivation = motivation_priorities[0]
                
                motivation_names = {
                    "remuneration": "la rémunération",
                    "evolution": "les perspectives d'évolution",
                    "flexibility": "la flexibilité",
                    "location": "la localisation",
                    "other": "d'autres facteurs"
                }
                
                motivation_name = motivation_names.get(top_motivation, top_motivation)
                
                if top_motivation == "remuneration" and "salary_expectation" in candidate and "salary_range" in job:
                    candidate_salary = candidate["salary_expectation"]
                    job_min = job["salary_range"].get("min", 0)
                    job_max = job["salary_range"].get("max", 0)
                    
                    if job_min <= candidate_salary <= job_max:
                        insights.append({
                            "type": "motivation_match",
                            "message": f"La rémunération proposée ({job_min} - {job_max}) correspond aux attentes ({candidate_salary})",
                            "score": 1.0,
                            "category": "strength"
                        })
                    elif candidate_salary > job_max:
                        insights.append({
                            "type": "motivation_mismatch",
                            "message": f"La rémunération proposée (max {job_max}) est inférieure aux attentes ({candidate_salary})",
                            "score": 0.3,
                            "category": "weakness"
                        })
                
                elif top_motivation == "evolution" and not job.get("evolution_perspectives"):
                    insights.append({
                        "type": "motivation_mismatch",
                        "message": "Les perspectives d'évolution sont importantes pour le candidat mais ne sont pas détaillées dans l'offre",
                        "score": 0.4,
                        "category": "weakness"
                    })
                
                elif top_motivation == "flexibility" and not job.get("offers_remote"):
                    insights.append({
                        "type": "motivation_mismatch",
                        "message": "La flexibilité est importante pour le candidat mais le poste n'offre pas de télétravail",
                        "score": 0.4,
                        "category": "weakness"
                    })
                
                elif top_motivation == "other" and candidate.get("other_motivation"):
                    insights.append({
                        "type": "motivation_other",
                        "message": f"Motivation principale: {candidate['other_motivation']}",
                        "score": 0.5,  # Score neutre, car difficile à évaluer automatiquement
                        "category": "info"
                    })
        
        return insights

# Fonction utilitaire pour créer une instance de SmartMatcherExtended
def create_extended_matcher(api_key: str = None, use_cache: bool = True, cache_size: int = 1000) -> SmartMatcherExtended:
    """
    Crée une instance de SmartMatcherExtended avec les paramètres spécifiés
    
    Args:
        api_key (str, optional): Clé API Google Maps
        use_cache (bool, optional): Activer le cache
        cache_size (int, optional): Taille du cache
        
    Returns:
        SmartMatcherExtended: Instance configurée
    """
    return SmartMatcherExtended(api_key=api_key, use_cache=use_cache, cache_size=cache_size)
