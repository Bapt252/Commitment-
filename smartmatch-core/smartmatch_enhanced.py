# -*- coding: utf-8 -*-
"""
Version étendue de SmartMatch prenant en compte toutes les données des questionnaires
-----------------------------------------------------------------------------------
Cette classe étend SmartMatcher avec des fonctionnalités supplémentaires pour 
intégrer complètement les données des questionnaires web et générer des insights
plus détaillés.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import logging
from typing import Dict, List, Any, Optional, Union

from smartmatch import SmartMatcher

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartMatcherEnhanced(SmartMatcher):
    """
    Version étendue de SmartMatcher intégrant des critères supplémentaires 
    des questionnaires candidat et client.
    """
    
    def __init__(self, api_key: str = None, use_cache: bool = True, cache_size: int = 1000):
        """
        Initialisation du SmartMatcherEnhanced
        
        Args:
            api_key (str): Clé API Google Maps pour les calculs de distance
            use_cache (bool): Activer le cache pour les calculs de distance
            cache_size (int): Taille du cache pour les calculs de distance
        """
        # Initialiser la classe parente
        super().__init__(api_key, use_cache, cache_size)
        
        # Facteurs de pondération ajustés pour inclure les critères supplémentaires
        self.weights = {
            "skills": 0.35,            # Réduction du poids des compétences pour intégrer les nouveaux critères
            "location": 0.20,          # Réduction du poids de la localisation
            "experience": 0.15,        # Maintien du poids de l'expérience
            "education": 0.10,         # Maintien du poids de l'éducation
            "preferences": 0.10,       # Maintien du poids des préférences de base
            "environment": 0.05,       # Nouvel axe pour l'environnement de travail
            "motivation": 0.05         # Nouvel axe pour l'alignement des motivations
        }
        
        logger.info("SmartMatcherEnhanced initialisé avec succès")
    
    def calculate_environment_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule la correspondance entre l'environnement de travail préféré et celui proposé
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
        
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Récupérer les préférences
        candidate_preference = candidate.get("office_preference", "no-preference")
        job_environment = job.get("work_environment", "")
        
        # Si pas de préférence explicite, score neutre
        if candidate_preference == "no-preference" or not job_environment:
            return 0.8  # Score légèrement positif par défaut
        
        # Si correspondance parfaite
        if candidate_preference == job_environment:
            return 1.0
        
        # Si non correspondance
        return 0.3
    
    def calculate_motivation_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule la correspondance entre les motivations du candidat et les atouts du poste
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Récupérer les priorités de motivation
        motivation_priorities = candidate.get("motivation_priorities", [])
        if not motivation_priorities:
            return 0.5  # Score neutre si pas d'information
        
        score = 0.5  # Score de base
        alignments = 0  # Nombre d'alignements trouvés
        
        # Vérifier si les principales motivations sont satisfaites par le poste
        # Prioriser les 3 premières motivations
        top_motivations = motivation_priorities[:3] if len(motivation_priorities) >= 3 else motivation_priorities
        
        for motivation in top_motivations:
            if motivation == "remuneration":
                # Vérifier si le salaire répond aux attentes
                if "salary_expectation" in candidate and "salary_range" in job:
                    candidate_salary = candidate["salary_expectation"]
                    job_min = job["salary_range"].get("min", 0)
                    job_max = job["salary_range"].get("max", 0)
                    
                    if job_min <= candidate_salary <= job_max:
                        score += 0.2
                        alignments += 1
            
            elif motivation == "evolution":
                # Vérifier si des perspectives d'évolution sont mentionnées
                if "evolution_perspectives" in job and job["evolution_perspectives"]:
                    score += 0.2
                    alignments += 1
            
            elif motivation == "flexibility":
                # Vérifier si le télétravail est mentionné ou d'autres flexibilités
                if job.get("offers_remote", False):
                    score += 0.2
                    alignments += 1
                elif "benefits_description" in job and any(keyword in job["benefits_description"].lower() 
                                                      for keyword in ["flex", "souple", "horaires"]):
                    score += 0.15
                    alignments += 1
            
            elif motivation == "location":
                # Vérifier si le temps de trajet est bon
                if "location_score" in self.temp_scores and self.temp_scores["location_score"] >= 0.7:
                    score += 0.2
                    alignments += 1
        
        # Normalisation du score
        if alignments > 0:
            return min(1.0, score)
        else:
            return score
    
    def calculate_transport_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule un score de matching plus précis pour le transport en tenant compte 
        des préférences de temps de trajet
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Si les deux proposent le travail à distance, le score est parfait
        if candidate.get("remote_work", False) and job.get("offers_remote", False):
            return 1.0
        
        # Récupérer les préférences de transport
        transport_preferences = candidate.get("transport_preferences", {})
        if not transport_preferences:
            # Si pas de préférences, utiliser le calcul standard
            return super().calculate_location_match(candidate, job)
        
        # Récupérer les localisations
        candidate_location = candidate.get("location", "")
        job_location = job.get("location", "")
        
        if not candidate_location or not job_location:
            logger.warning("Information de localisation manquante")
            return 0.5  # Score neutre si pas de localisation disponible
        
        # Calculer le temps de trajet
        travel_time = self.calculate_travel_time(candidate_location, job_location)
        
        # Vérifier le temps de trajet par rapport aux préférences
        best_match_score = 0.0
        
        for mode, max_time in transport_preferences.items():
            # Calculer le score pour ce mode de transport
            if travel_time <= max_time:
                score = 1.0  # Temps de trajet inférieur au maximum accepté
            else:
                # Pénalité proportionnelle au dépassement
                ratio = max_time / travel_time
                score = max(0.2, ratio)  # Minimum de 0.2 pour ne pas trop pénaliser
            
            # Garder le meilleur score parmi tous les modes de transport
            best_match_score = max(best_match_score, score)
        
        return best_match_score if best_match_score > 0.0 else super().calculate_location_match(candidate, job)
    
    def calculate_company_size_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule la correspondance entre les préférences de taille d'entreprise et la structure
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Récupérer les préférences du candidat
        structure_preferences = candidate.get("structure_preference", [])
        if not structure_preferences or "no-preference" in structure_preferences:
            return 0.8  # Score légèrement positif si pas de préférence spécifique
        
        # Récupérer la taille de l'entreprise
        company_size = job.get("company_size", "")
        if not company_size:
            return 0.5  # Score neutre si pas d'information
        
        # Vérifier la correspondance
        if company_size in structure_preferences:
            return 1.0  # Correspondance parfaite
        
        # Mappings de similarité pour les différentes structures
        structure_similarity = {
            "startup": {"pme": 0.6, "groupe": 0.3},
            "pme": {"startup": 0.6, "groupe": 0.6},
            "groupe": {"pme": 0.6, "startup": 0.3}
        }
        
        # Trouver la meilleure correspondance approximative
        best_score = 0.0
        for preference in structure_preferences:
            if preference in structure_similarity and company_size in structure_similarity[preference]:
                score = structure_similarity[preference][company_size]
                best_score = max(best_score, score)
        
        return best_score if best_score > 0.0 else 0.4  # Score par défaut si pas de correspondance
    
    def calculate_sector_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule la correspondance entre les préférences de secteur et le secteur du poste,
        en tenant compte des secteurs rédhibitoires.
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Récupérer les préférences de secteur
        industry = candidate.get("industry", "")
        alternative_industries = candidate.get("alternative_industries", [])
        prohibited_sectors = candidate.get("prohibited_sectors", [])
        
        # Récupérer le secteur du poste
        job_industry = job.get("industry", "")
        
        # Vérifier si le secteur est rédhibitoire
        if job_industry and job_industry in prohibited_sectors:
            return 0.1  # Score très bas pour un secteur explicitement rejeté
        
        # Si pas de préférence ou pas de secteur de poste, score neutre
        if not industry or not job_industry:
            return 0.5
        
        # Si correspondance parfaite
        if industry == job_industry:
            return 1.0
        
        # Si dans les alternatives
        if job_industry in alternative_industries:
            return 0.8
        
        # Sinon, score modéré
        return 0.4
    
    def calculate_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule le score global de correspondance entre un candidat et une offre d'emploi
        en prenant en compte les critères supplémentaires des questionnaires
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            Dict: Résultat du matching avec scores et insights
        """
        # Stocker les résultats intermédiaires pour les utiliser dans d'autres calculs
        self.temp_scores = {}
        
        # Calculer les scores de base
        skill_score = self.calculate_skill_match(candidate, job)
        location_score = self.calculate_transport_match(candidate, job)  # Utilise la version améliorée
        self.temp_scores["location_score"] = location_score  # Pour l'utiliser dans d'autres calculs
        
        experience_score = self.calculate_experience_match(candidate, job)
        education_score = self.calculate_education_match(candidate, job)
        preference_score = self.calculate_preference_match(candidate, job)
        
        # Calculer les scores supplémentaires
        environment_score = self.calculate_environment_match(candidate, job)
        motivation_score = self.calculate_motivation_match(candidate, job)
        
        # Intégrer les scores de taille d'entreprise et de secteur dans le score de préférences
        company_size_score = self.calculate_company_size_match(candidate, job)
        sector_score = self.calculate_sector_match(candidate, job)
        
        # Ajuster le score de préférences
        adjusted_preference_score = (preference_score * 0.6 + 
                                   company_size_score * 0.2 + 
                                   sector_score * 0.2)
        
        # Calculer le score global pondéré
        overall_score = (
            skill_score * self.weights["skills"] +
            location_score * self.weights["location"] +
            experience_score * self.weights["experience"] +
            education_score * self.weights["education"] +
            adjusted_preference_score * self.weights["preferences"] +
            environment_score * self.weights["environment"] +
            motivation_score * self.weights["motivation"]
        )
        
        # Générer des insights étendus
        insights = self.generate_enhanced_insights(
            candidate, job,
            skill_score, location_score, experience_score, 
            education_score, adjusted_preference_score,
            environment_score, motivation_score,
            company_size_score, sector_score
        )
        
        # Nettoyer les données temporaires
        del self.temp_scores
        
        # Retourner le résultat complet
        return {
            "candidate_id": candidate.get("id", ""),
            "job_id": job.get("id", ""),
            "overall_score": round(overall_score, 2),
            "category_scores": {
                "skills": round(skill_score, 2),
                "location": round(location_score, 2),
                "experience": round(experience_score, 2),
                "education": round(education_score, 2),
                "preferences": round(adjusted_preference_score, 2),
                "environment": round(environment_score, 2),
                "motivation": round(motivation_score, 2)
            },
            "additional_scores": {
                "company_size": round(company_size_score, 2),
                "sector": round(sector_score, 2)
            },
            "insights": insights
        }
    
    def generate_enhanced_insights(self, 
                               candidate: Dict[str, Any], 
                               job: Dict[str, Any],
                               skill_score: float,
                               location_score: float,
                               experience_score: float,
                               education_score: float,
                               preference_score: float,
                               environment_score: float,
                               motivation_score: float,
                               company_size_score: float,
                               sector_score: float) -> List[Dict[str, Any]]:
        """
        Génère des insights détaillés et enrichis sur le match entre un candidat et une offre d'emploi
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            skill_score (float): Score de compétences
            location_score (float): Score de localisation
            experience_score (float): Score d'expérience
            education_score (float): Score d'éducation
            preference_score (float): Score de préférences
            environment_score (float): Score d'environnement
            motivation_score (float): Score de motivation
            company_size_score (float): Score de taille d'entreprise
            sector_score (float): Score de secteur
            
        Returns:
            List[Dict]: Liste d'insights avec type, message et score
        """
        # Obtenir les insights standard
        insights = super().generate_insights(
            candidate, job, skill_score, location_score, 
            experience_score, education_score, preference_score
        )
        
        # Ajouter les insights sur l'environnement de travail
        if environment_score >= 0.9:
            insights.append({
                "type": "environment_match",
                "message": "Environnement de travail parfaitement adapté aux préférences",
                "score": environment_score,
                "category": "strength"
            })
        elif environment_score <= 0.4:
            insights.append({
                "type": "environment_mismatch",
                "message": "L'environnement de travail ne correspond pas aux préférences",
                "score": environment_score,
                "category": "weakness"
            })
        
        # Ajouter les insights sur les motivations
        if motivation_score >= 0.8:
            # Identifier les principales motivations
            motivation_priorities = candidate.get("motivation_priorities", [])
            top_motivations = motivation_priorities[:2] if len(motivation_priorities) >= 2 else motivation_priorities
            
            # Traduire les codes en texte lisible
            motivation_names = {
                "remuneration": "rémunération",
                "evolution": "évolution de carrière",
                "flexibility": "flexibilité",
                "location": "proximité géographique"
            }
            
            # Construire le message
            motivation_text = ", ".join([motivation_names.get(m, m) for m in top_motivations if m in motivation_names])
            
            if motivation_text:
                insights.append({
                    "type": "motivation_match",
                    "message": f"Les priorités du candidat ({motivation_text}) sont satisfaites par ce poste",
                    "score": motivation_score,
                    "category": "strength"
                })
            else:
                insights.append({
                    "type": "motivation_match",
                    "message": "Ce poste répond bien aux attentes importantes du candidat",
                    "score": motivation_score,
                    "category": "strength"
                })
        elif motivation_score <= 0.4:
            insights.append({
                "type": "motivation_mismatch",
                "message": "Ce poste ne semble pas répondre aux motivations principales du candidat",
                "score": motivation_score,
                "category": "weakness"
            })
        
        # Ajouter les insights sur la taille d'entreprise
        if company_size_score >= 0.9:
            structure_preferences = candidate.get("structure_preference", [])
            if isinstance(structure_preferences, list) and len(structure_preferences) > 0 and \
               structure_preferences[0] != "no-preference":
                insights.append({
                    "type": "company_size_match",
                    "message": f"La taille de l'entreprise correspond parfaitement aux préférences",
                    "score": company_size_score,
                    "category": "strength"
                })
        elif company_size_score <= 0.4:
            insights.append({
                "type": "company_size_mismatch",
                "message": "La taille de l'entreprise ne correspond pas aux préférences",
                "score": company_size_score,
                "category": "weakness"
            })
        
        # Ajouter les insights sur le secteur d'activité
        if sector_score <= 0.2:
            insights.append({
                "type": "prohibited_sector",
                "message": "Ce poste est dans un secteur que le candidat souhaite éviter",
                "score": sector_score,
                "category": "dealbreaker"  # Nouvelle catégorie pour les éléments rédhibitoires
            })
        
        # Ajouter des insights sur la disponibilité et le préavis si pertinent
        candidate_availability = candidate.get("availability", "")
        job_delay = job.get("recruitment_delay", [])
        
        if candidate.get("currently_employed", False) and not job.get("can_handle_notice", True):
            insights.append({
                "type": "notice_period_issue",
                "message": "Le recruteur ne peut pas gérer de préavis et le candidat est actuellement en poste",
                "score": 0.3,
                "category": "weakness"
            })
        
        # Ajouter des insights sur l'adéquation générale
        if len([i for i in insights if i.get("category") == "strength"]) >= 3 and len([i for i in insights if i.get("category") in ["weakness", "dealbreaker"]]) == 0:
            insights.append({
                "type": "overall_match",
                "message": "Excellente adéquation globale entre le candidat et le poste",
                "score": 0.9,
                "category": "strength"
            })
        
        return insights

# Fonction utilitaire pour obtenir une instance de SmartMatcherEnhanced
def get_enhanced_matcher(api_key: str = None) -> SmartMatcherEnhanced:
    """
    Obtient une instance de SmartMatcherEnhanced
    
    Args:
        api_key (str): Clé API Google Maps pour les calculs de distance
        
    Returns:
        SmartMatcherEnhanced: Instance prête à l'emploi
    """
    return SmartMatcherEnhanced(api_key=api_key)

# Point d'entrée pour les tests
if __name__ == "__main__":
    # Créer une instance
    matcher = get_enhanced_matcher()
    
    # Exemple de matching
    candidate = {
        "id": "c1",
        "name": "Jean Dupont",
        "skills": ["Python", "Django", "JavaScript", "React"],
        "location": "48.8566,2.3522",  # Paris
        "years_of_experience": 5,
        "education_level": "master",
        "remote_work": True,
        "salary_expectation": 65000,
        "job_type": "full_time",
        "industry": "tech",
        "office_preference": "open-space",
        "motivation_priorities": ["evolution", "remuneration", "flexibility"],
        "structure_preference": ["startup", "pme"],
        "transport_preferences": {"public-transport": 45, "bike": 30},
        "currently_employed": True,
        "availability": "1month"
    }
    
    job = {
        "id": "j1",
        "title": "Développeur Python Senior",
        "required_skills": ["Python", "Django", "SQL"],
        "preferred_skills": ["React", "Docker"],
        "location": "48.8847,2.2967",  # Levallois-Perret
        "min_years_of_experience": 4,
        "max_years_of_experience": 8,
        "required_education": "bachelor",
        "offers_remote": True,
        "salary_range": {"min": 55000, "max": 75000},
        "job_type": "full_time",
        "industry": "tech",
        "work_environment": "open-space",
        "company_size": "startup",
        "evolution_perspectives": "Possibilité d'évoluer vers un poste de lead developer",
        "can_handle_notice": True
    }
    
    # Calculer le match
    result = matcher.calculate_match(candidate, job)
    
    # Afficher les résultats
    print("\n=== RÉSULTAT DU MATCHING AVANCÉ ===\n")
    print(f"Score global: {result['overall_score']}")
    print("\nScores par catégorie:")
    for category, score in result['category_scores'].items():
        print(f"  - {category}: {score}")
    
    print("\nInsights générés:")
    for insight in result['insights']:
        print(f"  - [{insight['category']}] {insight['message']} ({insight['score']:.2f})")