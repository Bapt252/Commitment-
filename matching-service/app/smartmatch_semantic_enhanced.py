"""
Module SmartMatcher amélioré avec analyse sémantique avancée des compétences
-------------------------------------------------------------------------
Ce module étend SmartMatcher avec l'intégration du nouvel analyseur sémantique 
des compétences pour des résultats de matching plus précis.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import logging
from typing import Dict, List, Any, Optional, Union
import os
import json
import time

# Importer les modules du projet
from app.smartmatch import SmartMatcher
from app.semantic_skills_analyzer import SemanticSkillsAnalyzer

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartMatcherSemanticEnhanced(SmartMatcher):
    """
    Version améliorée de SmartMatcher avec analyse sémantique avancée des compétences
    """
    
    def __init__(self, api_key: str = None, use_cache: bool = True, cache_size: int = 1000,
                embedding_model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2',
                taxonomy_file: str = None,
                use_threading: bool = True,
                max_workers: int = 4):
        """
        Initialisation du SmartMatcherSemanticEnhanced
        
        Args:
            api_key (str): Clé API Google Maps pour les calculs de distance
            use_cache (bool): Activer le cache pour les calculs de distance
            cache_size (int): Taille du cache pour les calculs de distance
            embedding_model_name (str): Nom du modèle d'embeddings à utiliser
            taxonomy_file (str): Fichier de taxonomie des compétences
            use_threading (bool): Utiliser le multithreading pour les calculs
            max_workers (int): Nombre maximum de workers pour le multithreading
        """
        # Initialiser la classe parent
        super().__init__(api_key, use_cache, cache_size)
        
        # Initialiser l'analyseur sémantique
        self.skills_analyzer = SemanticSkillsAnalyzer(
            embedding_model_name=embedding_model_name,
            taxonomy_file=taxonomy_file,
            cache_size=cache_size,
            use_threading=use_threading,
            max_workers=max_workers
        )
        
        # Stocker l'état de l'analyseur
        self.semantic_analysis_available = self.skills_analyzer.semantic_analysis_available
        
        # Ajuster les pondérations si nécessaire
        self.weights = {
            "skills": 0.45,      # Augmenter légèrement le poids des compétences
            "location": 0.25,
            "experience": 0.12,
            "education": 0.08,
            "preferences": 0.10
        }
        
        logger.info("SmartMatcherSemanticEnhanced initialisé avec succès")
        
        if self.semantic_analysis_available:
            logger.info("Analyse sémantique des compétences active")
        else:
            logger.info("Analyse sémantique des compétences limitée (mode de secours)")
    
    def calculate_skill_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule le score de correspondance des compétences entre un candidat et une offre d'emploi
        en utilisant l'analyseur sémantique avancé.
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Extraire les compétences
        candidate_skills_raw = candidate.get("skills", [])
        job_required_skills = job.get("required_skills", [])
        job_preferred_skills = job.get("preferred_skills", [])
        
        # Vérifier si les compétences sont disponibles
        if not candidate_skills_raw or (not job_required_skills and not job_preferred_skills):
            logger.warning("Compétences manquantes pour le candidat ou l'offre")
            return 0.5  # Score neutre si pas de compétences disponibles
        
        # Combiner les compétences requises et préférées
        job_skills_raw = []
        
        # Ajouter les compétences requises
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
        
        # Ajouter les compétences préférées
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
        
        # Analyser la correspondance des compétences
        try:
            result = self.skills_analyzer.analyze_skills_match(
                candidate_skills=candidate_skills_raw,
                job_skills=job_skills_raw
            )
            
            # Stocker le résultat détaillé pour une analyse ultérieure
            if not hasattr(self, "matching_details"):
                self.matching_details = {}
            
            candidate_id = candidate.get("id", "unknown")
            job_id = job.get("id", "unknown")
            key = f"{candidate_id}_{job_id}"
            
            if key not in self.matching_details:
                self.matching_details[key] = {}
            
            self.matching_details[key]["skills_analysis"] = result
            
            # Retourner le score global
            return result["score"]
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse sémantique des compétences: {str(e)}")
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
        avec des informations plus précises sur les compétences.
        
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
        candidate_id = candidate.get("id", "unknown")
        job_id = job.get("id", "unknown")
        key = f"{candidate_id}_{job_id}"
        
        if hasattr(self, "matching_details") and key in self.matching_details:
            details = self.matching_details[key].get("skills_analysis", {})
            
            if details:
                # Informations sur les compétences manquantes critiques
                missing_required = [
                    skill for skill in details.get("missing", []) 
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
                        "category": "weakness",
                        "importance": "high"
                    })
                
                # Informations sur les compétences bonus du candidat
                relevant_extras = details.get("relevant_extras", [])
                if relevant_extras:
                    extras_str = ", ".join(relevant_extras[:3])
                    if len(relevant_extras) > 3:
                        extras_str += f" et {len(relevant_extras) - 3} autres"
                        
                    insights.append({
                        "type": "relevant_extra_skills",
                        "message": f"Compétences supplémentaires pertinentes: {extras_str}",
                        "score": 0.8,
                        "category": "strength",
                        "importance": "medium"
                    })
                
                # Ajouter des informations sur la qualité des correspondances
                matches = details.get("matches", [])
                if matches:
                    high_quality_matches = [
                        match for match in matches 
                        if match.get("semantic_similarity", 0) > 0.8 and match.get("required", True)
                    ]
                    
                    if high_quality_matches and len(high_quality_matches) >= 3:
                        insights.append({
                            "type": "strong_skill_alignment",
                            "message": f"Forte correspondance sur {len(high_quality_matches)} compétences clés",
                            "score": 0.9,
                            "category": "strength",
                            "importance": "high"
                        })
        
        return insights

def get_semantic_enhanced_matcher(api_key: str = None, 
                               embedding_model: str = None,
                               taxonomy_file: str = None) -> SmartMatcherSemanticEnhanced:
    """
    Fonction utilitaire pour obtenir une instance de SmartMatcherSemanticEnhanced
    
    Args:
        api_key (str): Clé API Google Maps
        embedding_model (str): Nom du modèle d'embeddings
        taxonomy_file (str): Fichier de taxonomie des compétences
        
    Returns:
        SmartMatcherSemanticEnhanced: Instance du matcher amélioré
    """
    # Utiliser le modèle d'embeddings spécifié ou un par défaut
    model_name = embedding_model or 'paraphrase-multilingual-MiniLM-L12-v2'
    
    # Déterminer le chemin du fichier de taxonomie si non spécifié
    if not taxonomy_file:
        default_paths = [
            "app/data/skills_taxonomy.json",
            "data/skills_taxonomy.json",
            "skills_taxonomy.json"
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                taxonomy_file = path
                break
    
    # Créer et retourner l'instance
    return SmartMatcherSemanticEnhanced(
        api_key=api_key,
        embedding_model_name=model_name,
        taxonomy_file=taxonomy_file
    )

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer une instance du SmartMatcherSemanticEnhanced
    matcher = get_semantic_enhanced_matcher()
    
    # Charger des données de test
    test_data = matcher.load_test_data()
    
    # Exécuter le matching
    results = matcher.batch_match(test_data["candidates"], test_data["jobs"])
    
    # Afficher les résultats
    for result in results:
        print(f"Match score: {result['overall_score']}")
        print(f"Skills score: {result['category_scores']['skills']}")
        
        # Afficher les insights
        print("Insights:")
        for insight in result['insights']:
            print(f"- {insight['message']} ({insight['category']})")
        
        print("---")
