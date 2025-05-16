"""
Module amélioré d'analyse sémantique des compétences pour Nexten SmartMatch
--------------------------------------------------------------------------
Ce module implémente une approche avancée pour l'analyse sémantique des compétences
en utilisant des embeddings de texte, une taxonomie enrichie et des techniques
d'optimisation pour améliorer la précision et les performances.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import os
import logging
import json
import time
from typing import Dict, List, Any, Set, Tuple, Optional, Union
import numpy as np
from functools import lru_cache
from sklearn.metrics.pairwise import cosine_similarity
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Importer la taxonomie des compétences
from app.skills_taxonomy import SkillsTaxonomy

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticSkillsAnalyzer:
    """
    Classe pour l'analyse sémantique avancée des compétences
    """
    
    def __init__(self, embedding_model_name: str = 'paraphrase-multilingual-MiniLM-L12-v2',
                taxonomy_file: str = None, 
                cache_size: int = 2000,
                similarity_threshold: float = 0.6,
                use_threading: bool = True,
                max_workers: int = 4):
        """
        Initialise l'analyseur sémantique des compétences
        
        Args:
            embedding_model_name: Nom du modèle d'embeddings à utiliser
            taxonomy_file: Fichier contenant la taxonomie des compétences
            cache_size: Taille du cache pour les embeddings
            similarity_threshold: Seuil de similarité pour considérer deux compétences comme similaires
            use_threading: Utiliser le multithreading pour les calculs d'embeddings
            max_workers: Nombre maximum de threads pour les calculs parallèles
        """
        self.embedding_model_name = embedding_model_name
        self.cache_size = cache_size
        self.similarity_threshold = similarity_threshold
        self.use_threading = use_threading
        self.max_workers = max_workers
        
        # Initialiser l'embedding model
        self.embedding_model = self._initialize_embedding_model()
        
        # Initialiser la taxonomie des compétences
        self.taxonomy = SkillsTaxonomy(taxonomy_file)
        
        # Cache pour les embeddings
        self._embeddings_cache = {}
        self._embeddings_lock = threading.Lock()
        
        # Évaluer la disponibilité de l'analyse sémantique
        self.semantic_analysis_available = self.embedding_model is not None
        
        if self.semantic_analysis_available:
            logger.info("Analyse sémantique des compétences initialisée avec succès")
        else:
            logger.warning("Analyse sémantique des compétences désactivée (modèle d'embeddings non disponible)")
            logger.info("Utilisation du mode de secours basé sur la taxonomie uniquement")
    
    def _initialize_embedding_model(self):
        """
        Initialise le modèle d'embeddings
        
        Returns:
            Object: Modèle d'embeddings initialisé ou None si non disponible
        """
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer(self.embedding_model_name)
            logger.info(f"Modèle d'embeddings {self.embedding_model_name} chargé avec succès")
            return model
        except ImportError:
            logger.warning("Module sentence-transformers non installé, analyse sémantique désactivée")
            logger.info("Utilisez 'pip install sentence-transformers' pour activer l'analyse sémantique")
            return None
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du modèle d'embeddings: {str(e)}")
            return None
    
    def get_skill_embedding(self, skill_name: str) -> np.ndarray:
        """
        Calcule l'embedding d'une compétence avec mise en cache
        
        Args:
            skill_name: Nom de la compétence
            
        Returns:
            np.ndarray: Vecteur d'embedding
        """
        # Normaliser le nom de la compétence
        skill_name = skill_name.lower().strip()
        
        # Vérifier si l'embedding est déjà dans le cache
        with self._embeddings_lock:
            if skill_name in self._embeddings_cache:
                return self._embeddings_cache[skill_name]
        
        # Si le modèle n'est pas disponible, retourner un vecteur nul
        if not self.embedding_model:
            return np.zeros(384)  # Taille standard pour les embeddings
        
        try:
            # Calculer l'embedding
            embedding = self.embedding_model.encode(skill_name)
            
            # Mettre à jour le cache (avec gestion de la taille maximale)
            with self._embeddings_lock:
                if len(self._embeddings_cache) >= self.cache_size:
                    # Supprimer une entrée aléatoire si le cache est plein
                    if self._embeddings_cache:
                        key_to_remove = next(iter(self._embeddings_cache))
                        del self._embeddings_cache[key_to_remove]
                
                self._embeddings_cache[skill_name] = embedding
            
            return embedding
        except Exception as e:
            logger.error(f"Erreur lors du calcul de l'embedding pour '{skill_name}': {str(e)}")
            return np.zeros(384)
    
    def batch_compute_embeddings(self, skills: List[str]) -> Dict[str, np.ndarray]:
        """
        Calcule les embeddings pour une liste de compétences en batch
        
        Args:
            skills: Liste des noms de compétences
            
        Returns:
            Dict[str, np.ndarray]: Dictionnaire des embeddings par compétence
        """
        if not self.embedding_model:
            return {skill: np.zeros(384) for skill in skills}
        
        result = {}
        skills_to_compute = []
        
        # Vérifier d'abord le cache
        with self._embeddings_lock:
            for skill in skills:
                skill_lower = skill.lower().strip()
                if skill_lower in self._embeddings_cache:
                    result[skill] = self._embeddings_cache[skill_lower]
                else:
                    skills_to_compute.append(skill)
        
        if not skills_to_compute:
            return result
        
        try:
            # Utiliser l'encodage par batch du modèle
            embeddings = self.embedding_model.encode(skills_to_compute)
            
            for i, skill in enumerate(skills_to_compute):
                skill_lower = skill.lower().strip()
                result[skill] = embeddings[i]
                
                # Mettre à jour le cache
                with self._embeddings_lock:
                    if len(self._embeddings_cache) >= self.cache_size:
                        # Supprimer une entrée aléatoire si le cache est plein
                        if self._embeddings_cache:
                            key_to_remove = next(iter(self._embeddings_cache))
                            del self._embeddings_cache[key_to_remove]
                    
                    self._embeddings_cache[skill_lower] = embeddings[i]
        
        except Exception as e:
            logger.error(f"Erreur lors du calcul des embeddings par batch: {str(e)}")
            for skill in skills_to_compute:
                result[skill] = np.zeros(384)
        
        return result
    
    def semantic_similarity(self, skill1: str, skill2: str) -> float:
        """
        Calcule la similarité sémantique entre deux compétences
        
        Args:
            skill1: Première compétence
            skill2: Deuxième compétence
            
        Returns:
            float: Score de similarité entre 0 et 1
        """
        # Si les noms sont identiques, retourner une similarité parfaite
        if skill1.lower() == skill2.lower():
            return 1.0
        
        # Vérifier si l'un est un synonyme ou une variante de l'autre
        canonical1 = self.taxonomy.get_canonical_skill_name(skill1)
        canonical2 = self.taxonomy.get_canonical_skill_name(skill2)
        
        if canonical1.lower() == canonical2.lower():
            return 1.0
        
        # Si l'analyse sémantique n'est pas disponible, utiliser la taxonomie
        if not self.semantic_analysis_available:
            return self._fallback_similarity(canonical1, canonical2)
        
        # Calculer les embeddings
        embedding1 = self.get_skill_embedding(skill1)
        embedding2 = self.get_skill_embedding(skill2)
        
        # Calculer la similarité cosinus
        try:
            similarity = cosine_similarity([embedding1], [embedding2])[0][0]
            
            # Combiner avec l'information de la taxonomie
            taxonomy_similarity = self._fallback_similarity(canonical1, canonical2)
            
            # Donner plus de poids à la similarité sémantique, mais considérer aussi la taxonomie
            combined_similarity = similarity * 0.7 + taxonomy_similarity * 0.3
            
            return float(combined_similarity)
        except Exception as e:
            logger.error(f"Erreur lors du calcul de similarité entre '{skill1}' et '{skill2}': {str(e)}")
            return self._fallback_similarity(canonical1, canonical2)
    
    def _fallback_similarity(self, skill1: str, skill2: str) -> float:
        """
        Calcule la similarité basée sur la taxonomie (mode de secours)
        
        Args:
            skill1: Première compétence
            skill2: Deuxième compétence
            
        Returns:
            float: Score de similarité entre 0 et 1
        """
        # Si les noms sont identiques, retourner une similarité parfaite
        if skill1.lower() == skill2.lower():
            return 1.0
        
        # Obtenir les informations depuis la taxonomie
        related_skills1 = set(self.taxonomy.get_related_skills(skill1))
        
        # Si la seconde compétence est reliée à la première, similarité élevée
        if skill2 in related_skills1:
            return 0.8
        
        # Vérifier si elles ont un parent commun
        skill1_info = self.taxonomy.get_skill_info(skill1)
        skill2_info = self.taxonomy.get_skill_info(skill2)
        
        if skill1_info and skill2_info:
            parent1 = skill1_info.get('parent')
            parent2 = skill2_info.get('parent')
            
            if parent1 and parent2 and parent1 == parent2:
                return 0.7
        
        # Vérifier s'il y a des compétences reliées communes
        related_skills2 = set(self.taxonomy.get_related_skills(skill2))
        common_related = related_skills1.intersection(related_skills2)
        
        if common_related:
            return 0.5 + min(0.2, len(common_related) * 0.05)
        
        # Par défaut, faible similarité
        return 0.1
    
    def find_best_skill_match(self, skill: str, skill_candidates: List[str]) -> Tuple[str, float]:
        """
        Trouve la meilleure correspondance pour une compétence parmi une liste de candidats
        
        Args:
            skill: Compétence à chercher
            skill_candidates: Liste des compétences candidates
            
        Returns:
            Tuple[str, float]: Meilleure correspondance et score de similarité
        """
        best_match = None
        best_score = 0.0
        
        if not skill_candidates:
            return None, 0.0
        
        # Si un seul candidat, calcul direct
        if len(skill_candidates) == 1:
            similarity = self.semantic_similarity(skill, skill_candidates[0])
            if similarity >= self.similarity_threshold:
                return skill_candidates[0], similarity
            else:
                return None, 0.0
        
        # Multithreading pour les gros ensembles de données si activé
        if self.use_threading and len(skill_candidates) > 10:
            return self._threaded_find_best_match(skill, skill_candidates)
        
        # Traitement séquentiel pour les petits ensembles
        for candidate in skill_candidates:
            similarity = self.semantic_similarity(skill, candidate)
            
            if similarity > best_score:
                best_score = similarity
                best_match = candidate
        
        if best_score >= self.similarity_threshold:
            return best_match, best_score
        else:
            return None, 0.0
    
    def _threaded_find_best_match(self, skill: str, skill_candidates: List[str]) -> Tuple[str, float]:
        """
        Version multithreadée de find_best_skill_match
        
        Args:
            skill: Compétence à chercher
            skill_candidates: Liste des compétences candidates
            
        Returns:
            Tuple[str, float]: Meilleure correspondance et score de similarité
        """
        best_match = None
        best_score = 0.0
        
        # Calculer l'embedding de la compétence principale à l'avance
        self.get_skill_embedding(skill)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Créer des tâches pour calculer les similarités
            future_to_candidate = {
                executor.submit(self.semantic_similarity, skill, candidate): candidate
                for candidate in skill_candidates
            }
            
            # Collecter les résultats à mesure qu'ils sont prêts
            for future in as_completed(future_to_candidate):
                candidate = future_to_candidate[future]
                try:
                    similarity = future.result()
                    if similarity > best_score:
                        best_score = similarity
                        best_match = candidate
                except Exception as e:
                    logger.error(f"Erreur lors du calcul de similarité pour '{candidate}': {str(e)}")
        
        if best_score >= self.similarity_threshold:
            return best_match, best_score
        else:
            return None, 0.0
    
    def analyze_skills_match(self, 
                           candidate_skills: List[Union[str, Dict[str, Any]]], 
                           job_skills: List[Union[str, Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Analyse la correspondance entre les compétences d'un candidat et celles requises pour un poste
        
        Args:
            candidate_skills: Liste des compétences du candidat (strings ou dicts)
            job_skills: Liste des compétences requises pour le poste (strings ou dicts)
            
        Returns:
            Dict: Résultat de l'analyse avec scores et détails
        """
        # Normaliser les formats d'entrée
        normalized_candidate_skills = self._normalize_skills_format(candidate_skills)
        normalized_job_skills = self._normalize_skills_format(job_skills)
        
        # Extraire les noms de compétences
        candidate_skill_names = [skill["name"] for skill in normalized_candidate_skills]
        job_skill_names = [skill["name"] for skill in normalized_job_skills]
        
        # Précalculer les embeddings en batch pour améliorer les performances
        if self.semantic_analysis_available:
            all_skills = list(set(candidate_skill_names + job_skill_names))
            self.batch_compute_embeddings(all_skills)
        
        # Analyser les correspondances pour chaque compétence requise
        matches = []
        missing = []
        
        for job_skill in normalized_job_skills:
            job_skill_name = job_skill["name"]
            best_match, score = self.find_best_skill_match(job_skill_name, candidate_skill_names)
            
            if best_match and score >= self.similarity_threshold:
                # Trouver les détails de la compétence correspondante
                candidate_skill_details = next((skill for skill in normalized_candidate_skills 
                                              if skill["name"] == best_match), {})
                
                # Évaluer la correspondance des niveaux d'expertise
                expertise_score = self._evaluate_expertise_match(
                    candidate_skill_details.get("level", "intermédiaire"),
                    job_skill.get("level", "intermédiaire")
                )
                
                # Calculer le score final pour cette compétence
                skill_weight = job_skill.get("weight", 1.0)
                if job_skill.get("required", True):
                    skill_weight *= 1.5  # Augmenter le poids des compétences requises
                
                final_score = score * expertise_score * skill_weight
                
                matches.append({
                    "job_skill": job_skill_name,
                    "candidate_skill": best_match,
                    "semantic_similarity": score,
                    "expertise_match": expertise_score,
                    "required": job_skill.get("required", True),
                    "weight": skill_weight,
                    "final_score": final_score
                })
            else:
                # Compétence manquante
                missing.append({
                    "skill": job_skill_name,
                    "required": job_skill.get("required", True),
                    "level": job_skill.get("level", "intermédiaire")
                })
        
        # Identifier les compétences supplémentaires pertinentes
        extra_skills = []
        relevant_extras = []
        
        matched_skills = [match["candidate_skill"] for match in matches]
        for skill in normalized_candidate_skills:
            if skill["name"] not in matched_skills:
                extra_skills.append(skill["name"])
                
                # Vérifier si la compétence est pertinente pour le poste
                is_relevant = False
                for job_skill in normalized_job_skills:
                    # Calculer la similarité
                    similarity = self.semantic_similarity(skill["name"], job_skill["name"])
                    if similarity > 0.4:  # Seuil plus bas pour les compétences supplémentaires
                        is_relevant = True
                        break
                
                if is_relevant:
                    relevant_extras.append(skill["name"])
        
        # Calculer le score global
        total_score = sum(match["final_score"] for match in matches)
        max_possible_score = sum(skill.get("weight", 1.0) * (1.5 if skill.get("required", True) else 1.0) 
                                for skill in normalized_job_skills)
        
        normalized_score = total_score / max_possible_score if max_possible_score > 0 else 0.0
        
        # Appliquer un bonus pour les compétences supplémentaires pertinentes
        bonus = min(0.1, len(relevant_extras) * 0.02)
        final_score = min(1.0, normalized_score + bonus)
        
        return {
            "score": final_score,
            "raw_score": normalized_score,
            "bonus_score": bonus,
            "matches": matches,
            "missing": missing,
            "extra_skills": extra_skills,
            "relevant_extras": relevant_extras,
            "details": {
                "total_score": total_score,
                "max_possible_score": max_possible_score,
                "matched_count": len(matches),
                "missing_count": len(missing),
                "extra_count": len(extra_skills),
                "relevant_extra_count": len(relevant_extras),
                "semantic_analysis_used": self.semantic_analysis_available
            }
        }
    
    def _normalize_skills_format(self, skills: List[Union[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Normalise le format des compétences pour l'analyse
        
        Args:
            skills: Liste de compétences au format string ou dict
            
        Returns:
            List[Dict]: Liste normalisée de compétences
        """
        normalized = []
        
        for skill in skills:
            if isinstance(skill, str):
                normalized.append({
                    "name": skill,
                    "level": "intermédiaire",
                    "weight": 1.0,
                    "required": True
                })
            elif isinstance(skill, dict):
                # Assurer que tous les champs nécessaires sont présents
                normalized.append({
                    "name": skill.get("name", ""),
                    "level": skill.get("level", "intermédiaire"),
                    "weight": skill.get("weight", 1.0),
                    "required": skill.get("required", True)
                })
        
        return normalized
    
    def _evaluate_expertise_match(self, candidate_level: str, job_level: str) -> float:
        """
        Évalue la correspondance entre les niveaux d'expertise
        
        Args:
            candidate_level: Niveau d'expertise du candidat
            job_level: Niveau d'expertise requis pour le poste
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Mapping des niveaux d'expertise
        expertise_levels = {
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
        
        # Obtenir les valeurs numériques
        candidate_value = expertise_levels.get(candidate_level.lower(), 0.7)
        job_value = expertise_levels.get(job_level.lower(), 0.7)
        
        # Si le candidat a un niveau supérieur ou égal au requis, parfait
        if candidate_value >= job_value:
            return 1.0
        
        # Sinon, calculer le ratio
        ratio = candidate_value / job_value
        return max(0.3, ratio)  # Minimum de 0.3 pour ne pas trop pénaliser

# Fonction utilitaire pour la conversion des structures de données
def normalize_skills_format(skills_list: List[Union[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Convertit une liste de compétences en format standard pour l'analyse
    
    Args:
        skills_list: Liste de compétences (strings ou dicts)
        
    Returns:
        List[Dict]: Liste de compétences au format standard
    """
    analyzer = SemanticSkillsAnalyzer()
    return analyzer._normalize_skills_format(skills_list)

# Pour compatibilité avec le code existant
def convert_skills_format(skills_list: List[Union[str, Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Alias pour normalize_skills_format, pour compatibilité
    
    Args:
        skills_list: Liste de compétences (strings ou dicts)
        
    Returns:
        List[Dict]: Liste de compétences au format standard
    """
    return normalize_skills_format(skills_list)

# Exemple d'utilisation
if __name__ == "__main__":
    # Créer une instance de l'analyseur
    analyzer = SemanticSkillsAnalyzer()
    
    # Tester les similarités
    test_skills = [
        ("Python", "Python programming"),
        ("JavaScript", "JS"),
        ("React", "ReactJS"),
        ("Java", "JavaScript"),
        ("Machine Learning", "ML"),
        ("C++", "C#"),
        ("NodeJS", "Node.js"),
        ("Data Science", "Machine Learning")
    ]
    
    print("=== Test de similarité sémantique ===")
    for skill1, skill2 in test_skills:
        similarity = analyzer.semantic_similarity(skill1, skill2)
        print(f"{skill1} <-> {skill2}: {similarity:.4f}")
    
    # Tester l'analyse de matching
    candidate_skills = [
        "Python", "Django", "JavaScript", "React", "SQL", "Git"
    ]
    
    job_skills = [
        {"name": "Python", "level": "avancé", "required": True},
        {"name": "Flask", "level": "intermédiaire", "required": True},
        {"name": "JavaScript", "level": "intermédiaire", "required": False},
        {"name": "Docker", "level": "débutant", "required": False}
    ]
    
    result = analyzer.analyze_skills_match(candidate_skills, job_skills)
    
    print("\n=== Résultat de l'analyse ===")
    print(f"Score: {result['score']:.4f}")
    print(f"Score brut: {result['raw_score']:.4f}")
    print(f"Bonus: {result['bonus_score']:.4f}")
    print(f"Compétences correspondantes: {len(result['matches'])}")
    print(f"Compétences manquantes: {len(result['missing'])}")
    print(f"Compétences supplémentaires pertinentes: {result['relevant_extras']}")
