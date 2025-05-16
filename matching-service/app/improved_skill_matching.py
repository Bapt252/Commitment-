"""
Module d'amélioration du calcul des scores de compétences pour SmartMatch
-------------------------------------------------------------------------
Ce module implémente une approche avancée pour le calcul des scores de compétences
utilisant des embeddings de texte et la prise en compte des niveaux d'expertise.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import logging
import os
from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SkillMatchEnhanced:
    """
    Classe pour le calcul amélioré des scores de compétences
    en utilisant une approche sémantique et pondérée.
    """
    
    def __init__(self, embedding_model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2', 
                 cache_size: int = 1000):
        """
        Initialise le calculateur de score de compétences amélioré
        
        Args:
            embedding_model_name (str): Nom du modèle d'embeddings à utiliser
            cache_size (int): Taille du cache pour les embeddings
        """
        self.cache_size = cache_size
        self.embedding_model_name = embedding_model_name
        self.embedding_model = None
        self._initialize_embedding_model()
        
        # Mapping des niveaux d'expertise en valeurs numériques
        self.expertise_levels = {
            "débutant": 0.5,
            "junior": 0.6,
            "intermédiaire": 0.8,
            "avancé": 0.9,
            "expert": 1.0,
            "beginner": 0.5,
            "intermediate": 0.8,
            "advanced": 0.9,
            "expert": 1.0
        }
        
        # Pondération par type de compétence
        self.skill_type_weights = {
            "technical": 1.0,     # Compétences techniques/programmation
            "domain": 0.9,        # Compétences spécifiques au domaine
            "soft": 0.7,          # Compétences relationnelles
            "language": 0.8,      # Compétences linguistiques
            "tool": 0.85,         # Compétences outils/logiciels
            "certification": 0.95 # Certifications
        }
        
        # Taxonomie des compétences (hiérarchie et relations)
        self.skill_taxonomy = self._initialize_skill_taxonomy()
        
        logger.info("SkillMatchEnhanced initialisé avec succès")
    
    def _initialize_embedding_model(self):
        """
        Initialise le modèle d'embeddings pour la comparaison sémantique
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"Modèle d'embeddings {self.embedding_model_name} chargé avec succès")
        except ImportError:
            logger.warning("sentence-transformers non installé. L'analyse sémantique avancée sera désactivée.")
            self.embedding_model = None
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle d'embeddings: {str(e)}")
            self.embedding_model = None
    
    def _initialize_skill_taxonomy(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialise une taxonomie hiérarchique des compétences
        
        Returns:
            Dict: Taxonomie des compétences avec leurs relations
        """
        # Exemple de taxonomie simplifiée - à enrichir avec plus de données
        taxonomy = {
            # Programmation
            "programming": {
                "type": "category",
                "related": ["development", "coding", "software engineering"],
                "children": ["python", "javascript", "java", "c++", "ruby", "php", "go", "rust"]
            },
            "python": {
                "type": "technical",
                "parent": "programming",
                "related": ["django", "flask", "fastapi", "data science", "machine learning"],
                "children": ["django", "flask", "fastapi", "pandas", "numpy", "pytorch", "tensorflow"]
            },
            "javascript": {
                "type": "technical",
                "parent": "programming",
                "related": ["frontend", "web development", "nodejs"],
                "children": ["react", "vue", "angular", "node.js", "express", "nextjs"]
            },
            
            # Data Science
            "data science": {
                "type": "category",
                "related": ["machine learning", "statistics", "data analysis"],
                "children": ["machine learning", "deep learning", "data analysis", "data visualization"]
            },
            "machine learning": {
                "type": "technical",
                "parent": "data science",
                "related": ["artificial intelligence", "deep learning", "neural networks"],
                "children": ["supervised learning", "unsupervised learning", "reinforcement learning"]
            },
            
            # DevOps
            "devops": {
                "type": "category",
                "related": ["cloud", "ci/cd", "infrastructure", "automation"],
                "children": ["docker", "kubernetes", "jenkins", "terraform", "aws", "azure", "gcp"]
            }
        }
        
        logger.info(f"Taxonomie des compétences initialisée avec {len(taxonomy)} entrées")
        return taxonomy
    
    @lru_cache(maxsize=1000)
    def compute_skill_embedding(self, skill_name: str) -> np.ndarray:
        """
        Calcule l'embedding d'une compétence
        
        Args:
            skill_name (str): Nom de la compétence
            
        Returns:
            np.ndarray: Vecteur d'embedding
        """
        if self.embedding_model is None:
            logger.warning("Modèle d'embeddings non disponible, embeddings non calculés")
            return np.zeros(384)  # Vecteur zéro de dimension 384 (taille par défaut)
            
        try:
            embedding = self.embedding_model.encode(skill_name)
            return embedding
        except Exception as e:
            logger.error(f"Erreur lors du calcul de l'embedding pour '{skill_name}': {str(e)}")
            return np.zeros(384)
    
    def find_related_skills(self, skill_name: str) -> List[str]:
        """
        Trouve les compétences reliées à une compétence donnée
        
        Args:
            skill_name (str): Nom de la compétence
            
        Returns:
            List[str]: Liste des compétences reliées
        """
        skill_lower = skill_name.lower()
        
        # Vérifier si la compétence est directement dans la taxonomie
        if skill_lower in self.skill_taxonomy:
            skill_info = self.skill_taxonomy[skill_lower]
            return skill_info.get("related", []) + skill_info.get("children", [])
        
        # Chercher si c'est un enfant d'une catégorie
        for category, info in self.skill_taxonomy.items():
            if "children" in info and skill_lower in info["children"]:
                # Retourner le parent et les frères/sœurs
                siblings = [child for child in info["children"] if child != skill_lower]
                return [category] + siblings + info.get("related", [])
        
        # Si non trouvé, retourner une liste vide
        return []
    
    def get_skill_weight(self, skill_name: str, is_project_skill: bool = False) -> float:
        """
        Détermine le poids d'une compétence en fonction de son type
        
        Args:
            skill_name (str): Nom de la compétence
            is_project_skill (bool): Si la compétence vient du projet (priorité plus élevée)
            
        Returns:
            float: Poids de la compétence
        """
        skill_lower = skill_name.lower()
        
        # Chercher le type de compétence dans la taxonomie
        skill_type = "technical"  # Type par défaut
        
        if skill_lower in self.skill_taxonomy:
            skill_type = self.skill_taxonomy[skill_lower].get("type", "technical")
        else:
            # Chercher dans les enfants
            for category, info in self.skill_taxonomy.items():
                if "children" in info and skill_lower in info["children"]:
                    skill_type = info.get("type", "technical")
                    break
        
        # Poids de base selon le type
        base_weight = self.skill_type_weights.get(skill_type, 0.8)
        
        # Augmenter le poids si c'est une compétence requise par le projet
        if is_project_skill:
            base_weight *= 1.2
            
        return min(1.0, base_weight)  # Plafonner à 1.0
    
    def evaluate_expertise_match(self, candidate_level: str, project_level: str) -> float:
        """
        Évalue la correspondance entre les niveaux d'expertise
        
        Args:
            candidate_level (str): Niveau d'expertise du candidat
            project_level (str): Niveau d'expertise requis par le projet
            
        Returns:
            float: Score de correspondance d'expertise entre 0 et 1
        """
        # Convertir en valeurs numériques
        candidate_value = self.expertise_levels.get(candidate_level.lower(), 0.7)
        project_value = self.expertise_levels.get(project_level.lower(), 0.7)
        
        # Si le candidat a un niveau supérieur ou égal au requis, parfait
        if candidate_value >= project_value:
            return 1.0
        
        # Sinon, calculer le ratio
        ratio = candidate_value / project_value
        return max(0.3, ratio)  # Minimum de 0.3 pour ne pas trop pénaliser
    
    def calculate_skill_match_score(self, 
                                  candidate_skills: List[Dict[str, Any]], 
                                  project_skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcule un score de correspondance entre les compétences du candidat et celles requises par le projet
        en utilisant une approche sémantique et pondérée.
        
        Args:
            candidate_skills (List[Dict]): Liste des compétences du candidat avec niveau et type
            project_skills (List[Dict]): Liste des compétences requises par le projet avec niveau et type
            
        Returns:
            Dict: Score global et détails des correspondances
        """
        if not candidate_skills or not project_skills:
            logger.warning("Liste de compétences vide, score par défaut retourné")
            return {
                "score": 0.0,
                "matches": [],
                "missing": [],
                "details": {}
            }
        
        matches = []
        missing = []
        total_score = 0.0
        max_score_possible = 0.0
        
        # Pour chaque compétence requise par le projet
        for proj_skill in project_skills:
            # Extraire les informations
            proj_skill_name = proj_skill.get("name", "")
            if not proj_skill_name:
                continue
                
            proj_skill_level = proj_skill.get("level", "intermédiaire")
            proj_skill_required = proj_skill.get("required", True)
            
            # Pondération basée sur l'importance de la compétence
            skill_weight = proj_skill.get("weight", 1.0)
            if proj_skill_required:
                skill_weight *= 1.5  # Augmenter le poids des compétences requises
            
            # Pondération par type de compétence
            skill_weight *= self.get_skill_weight(proj_skill_name, True)
            
            max_score_possible += skill_weight
            
            # Calculer le meilleur match parmi les compétences du candidat
            best_match_score = 0.0
            best_match_skill = None
            
            for cand_skill in candidate_skills:
                cand_skill_name = cand_skill.get("name", "")
                if not cand_skill_name:
                    continue
                    
                cand_skill_level = cand_skill.get("level", "intermédiaire")
                
                # Calculer la similarité sémantique
                if self.embedding_model is not None:
                    # Utiliser les embeddings pour la similarité
                    proj_embedding = self.compute_skill_embedding(proj_skill_name)
                    cand_embedding = self.compute_skill_embedding(cand_skill_name)
                    semantic_similarity = cosine_similarity([proj_embedding], [cand_embedding])[0][0]
                else:
                    # Méthode de secours si pas d'embeddings
                    semantic_similarity = 1.0 if proj_skill_name.lower() == cand_skill_name.lower() else 0.2
                    
                    # Vérifier si compétence reliée dans la taxonomie
                    related_skills = self.find_related_skills(proj_skill_name)
                    if cand_skill_name.lower() in [s.lower() for s in related_skills]:
                        semantic_similarity = max(semantic_similarity, 0.7)
                
                # Considérer seulement si similarité significative
                if semantic_similarity > 0.6:
                    # Évaluer le niveau d'expertise
                    expertise_factor = self.evaluate_expertise_match(cand_skill_level, proj_skill_level)
                    
                    # Score final pour cette compétence
                    match_score = semantic_similarity * expertise_factor
                    
                    if match_score > best_match_score:
                        best_match_score = match_score
                        best_match_skill = cand_skill
            
            # Ajouter le résultat
            skill_score = best_match_score * skill_weight
            total_score += skill_score
            
            if best_match_skill:
                matches.append({
                    "project_skill": proj_skill_name,
                    "candidate_skill": best_match_skill.get("name", ""),
                    "similarity": best_match_score,
                    "required": proj_skill_required,
                    "weight": skill_weight,
                    "score": skill_score
                })
            else:
                missing.append({
                    "skill": proj_skill_name,
                    "required": proj_skill_required,
                    "level": proj_skill_level
                })
        
        # Calculer le score final normalisé
        normalized_score = total_score / max_score_possible if max_score_possible > 0 else 0.0
        
        # Bonus pour les compétences supplémentaires pertinentes non demandées
        # Identifier les compétences du candidat non appariées
        matched_candidate_skills = [match["candidate_skill"] for match in matches]
        extra_skills = [
            skill for skill in candidate_skills 
            if skill.get("name", "") and skill.get("name", "") not in matched_candidate_skills
        ]
        
        # Calculer un bonus basé sur ces compétences supplémentaires
        bonus = 0.0
        relevant_extras = []
        
        for skill in extra_skills:
            skill_name = skill.get("name", "")
            if not skill_name:
                continue
                
            # Vérifier si la compétence est pertinente pour le projet
            is_relevant = False
            relevance_score = 0.0
            
            for proj_skill in project_skills:
                proj_skill_name = proj_skill.get("name", "")
                if not proj_skill_name:
                    continue
                
                # Vérifier si reliée dans la taxonomie
                if skill_name.lower() in [s.lower() for s in self.find_related_skills(proj_skill_name)]:
                    is_relevant = True
                    relevance_score = 0.5
                    break
            
            if is_relevant:
                bonus += 0.01 * relevance_score  # Petit bonus pour chaque compétence pertinente
                relevant_extras.append(skill_name)
        
        # Appliquer le bonus (plafonné)
        final_score = min(1.0, normalized_score + bonus)
        
        return {
            "score": final_score,
            "raw_score": normalized_score,
            "bonus": bonus,
            "matches": matches,
            "missing": missing,
            "relevant_extras": relevant_extras,
            "details": {
                "total_score": total_score,
                "max_score_possible": max_score_possible,
                "matched_skills_count": len(matches),
                "missing_skills_count": len(missing),
                "extra_skills_count": len(extra_skills),
                "relevant_extra_skills_count": len(relevant_extras)
            }
        }

# Fonction utilitaire pour la conversion des structures de données
def convert_skills_format(skills_list: List[Union[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Convertit une liste de compétences en format standard pour l'algorithme de matching
    
    Args:
        skills_list (List[Union[str, Dict]]): Liste de compétences (strings ou dicts)
        
    Returns:
        List[Dict]: Liste de compétences au format standard
    """
    result = []
    
    for skill in skills_list:
        if isinstance(skill, str):
            # Conversion simple string -> dict
            result.append({
                "name": skill,
                "level": "intermédiaire",
                "weight": 1.0,
                "required": True
            })
        elif isinstance(skill, dict):
            # Assurer que tous les champs nécessaires sont présents
            processed_skill = {
                "name": skill.get("name", ""),
                "level": skill.get("level", "intermédiaire"),
                "weight": skill.get("weight", 1.0),
                "required": skill.get("required", True)
            }
            result.append(processed_skill)
    
    return result
