"""
Module d'intégration de l'algorithme amélioré de matching de compétences au SmartMatcher
---------------------------------------------------------------------------------------
Ce module montre comment intégrer la classe SkillMatchEnhanced au SmartMatcher existant
pour améliorer les scores de matching de compétences.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import os
import logging
from typing import Dict, List, Any, Optional
import json

# Importer les modules nécessaires
from app.smartmatch import SmartMatcher
from app.improved_skill_matching import SkillMatchEnhanced, convert_skills_format

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartMatcherEnhanced(SmartMatcher):
    """
    Version améliorée du SmartMatcher qui intègre le nouveau calculateur de scores de compétences
    """
    
    def __init__(self, api_key: str = None, use_cache: bool = True, cache_size: int = 1000,
                embedding_model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Initialisation du SmartMatcherEnhanced
        
        Args:
            api_key (str): Clé API Google Maps pour les calculs de distance
            use_cache (bool): Activer le cache pour les calculs de distance
            cache_size (int): Taille du cache pour les calculs de distance
            embedding_model_name (str): Nom du modèle d'embeddings à utiliser
        """
        # Initialiser la classe parent
        super().__init__(api_key, use_cache, cache_size)
        
        # Initialiser le calculateur amélioré de score de compétences
        self.skill_matcher = SkillMatchEnhanced(
            embedding_model_name=embedding_model_name,
            cache_size=cache_size
        )
        
        # Mettre à jour les facteurs de pondération
        self.weights = {
            "skills": 0.40,  # Maintenir le même poids pour les compétences
            "location": 0.25,
            "experience": 0.15,
            "education": 0.10,
            "preferences": 0.10
        }
        
        logger.info("SmartMatcherEnhanced initialisé avec succès")
    
    def calculate_skill_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule le score de correspondance des compétences entre un candidat et une offre d'emploi
        en utilisant l'algorithme amélioré.
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Extraire les compétences dans le format approprié
        candidate_skills_raw = candidate.get("skills", [])
        job_required_skills = job.get("required_skills", [])
        job_preferred_skills = job.get("preferred_skills", [])
        
        # Combiner les compétences requises et préférées du job
        job_skills_raw = []
        
        # Ajouter les compétences requises avec un poids plus élevé
        for skill in job_required_skills:
            if isinstance(skill, str):
                job_skills_raw.append({
                    "name": skill,
                    "required": True,
                    "weight": 1.5
                })
            elif isinstance(skill, dict):
                skill_dict = skill.copy()
                skill_dict["required"] = True
                skill_dict["weight"] = skill.get("weight", 1.0) * 1.5
                job_skills_raw.append(skill_dict)
        
        # Ajouter les compétences préférées avec un poids normal
        for skill in job_preferred_skills:
            if isinstance(skill, str):
                job_skills_raw.append({
                    "name": skill,
                    "required": False,
                    "weight": 1.0
                })
            elif isinstance(skill, dict):
                skill_dict = skill.copy()
                skill_dict["required"] = False
                skill_dict["weight"] = skill.get("weight", 1.0)
                job_skills_raw.append(skill_dict)
        
        # Si les deux listes sont vides, retourner le score par défaut
        if not candidate_skills_raw or not job_skills_raw:
            logger.warning("Compétences manquantes pour le candidat ou l'offre")
            return 0.5  # Score neutre si pas de compétences disponibles
        
        # Convertir les listes en format standard
        candidate_skills = convert_skills_format(candidate_skills_raw)
        job_skills = convert_skills_format(job_skills_raw)
        
        # Calculer le score de correspondance avec l'algorithme amélioré
        try:
            result = self.skill_matcher.calculate_skill_match_score(
                candidate_skills=candidate_skills,
                project_skills=job_skills
            )
            
            # Stocker les détails dans job pour analyse ultérieure si nécessaire
            if hasattr(job, "skill_match_details"):
                job["skill_match_details"] = result
            
            # Retourner le score global
            return result["score"]
        except Exception as e:
            logger.error(f"Erreur lors du calcul amélioré de la similarité des compétences: {str(e)}")
            # En cas d'erreur, revenir à l'algorithme de base
            return super().calculate_skill_match(candidate, job)
    
    def generate_insights(self, 
                         candidate: Dict[str, Any], 
                         job: Dict[str, Any],
                         skill_score: float,
                         location_score: float,
                         experience_score: float,
                         education_score: float,
                         preference_score: float) -> List[Dict[str, Any]]:
        """
        Génère des insights détaillés sur le match entre un candidat et une offre d'emploi
        avec des informations supplémentaires sur les compétences
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            skill_score (float): Score de compétences
            location_score (float): Score de localisation
            experience_score (float): Score d'expérience
            education_score (float): Score d'éducation
            preference_score (float): Score de préférences
            
        Returns:
            List[Dict]: Liste d'insights avec type, message et score
        """
        # Récupérer les insights de base
        insights = super().generate_insights(
            candidate, job, skill_score, location_score, 
            experience_score, education_score, preference_score
        )
        
        # Ajouter des insights spécifiques aux compétences si disponibles
        if hasattr(job, "skill_match_details") and "missing" in job["skill_match_details"]:
            # Informations sur les compétences manquantes critiques
            missing_required = [
                skill for skill in job["skill_match_details"]["missing"] 
                if skill.get("required", True)
            ]
            
            if missing_required:
                skill_names = ", ".join([skill["skill"] for skill in missing_required[:3]])
                if len(missing_required) > 3:
                    skill_names += f" et {len(missing_required) - 3} autres"
                    
                insights.append({
                    "type": "missing_critical_skills",
                    "message": f"Compétences requises manquantes: {skill_names}",
                    "score": 0.3,
                    "category": "weakness"
                })
            
            # Informations sur les compétences bonus du candidat
            if "relevant_extras" in job["skill_match_details"] and job["skill_match_details"]["relevant_extras"]:
                extras = job["skill_match_details"]["relevant_extras"]
                extras_str = ", ".join(extras[:3])
                if len(extras) > 3:
                    extras_str += f" et {len(extras) - 3} autres"
                    
                insights.append({
                    "type": "relevant_extra_skills",
                    "message": f"Compétences supplémentaires pertinentes: {extras_str}",
                    "score": 0.8,
                    "category": "strength"
                })
        
        return insights


def get_enhanced_matcher(api_key: str = None, embedding_model: str = None) -> SmartMatcherEnhanced:
    """
    Fonction utilitaire pour obtenir une instance de SmartMatcherEnhanced
    
    Args:
        api_key (str): Clé API Google Maps
        embedding_model (str): Nom du modèle d'embeddings
        
    Returns:
        SmartMatcherEnhanced: Instance du matcher amélioré
    """
    # Utiliser le modèle d'embeddings spécifié ou un par défaut
    model_name = embedding_model or 'paraphrase-multilingual-MiniLM-L12-v2'
    
    # Créer et retourner l'instance
    return SmartMatcherEnhanced(
        api_key=api_key,
        embedding_model_name=model_name
    )


# Exemple d'utilisation
if __name__ == "__main__":
    # Créer une instance du SmartMatcherEnhanced
    matcher = get_enhanced_matcher()
    
    # Charger des données de test
    test_data = matcher.load_test_data()
    
    # Exécuter le matching
    results = matcher.batch_match(test_data["candidates"], test_data["jobs"])
    
    # Afficher les résultats
    for result in results:
        print(f"Match score: {result['overall_score']}")
        print(f"Skills score: {result['category_scores']['skills']}")
        print("---")