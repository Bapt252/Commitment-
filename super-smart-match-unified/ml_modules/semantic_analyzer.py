"""
Analyseur sémantique pour SuperSmartMatch Unifié
Module optionnel utilisant Sentence Transformers
"""

import logging
from typing import List, Dict, Tuple
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

logger = logging.getLogger(__name__)

class SemanticAnalyzer:
    """
    Analyseur sémantique utilisant des embeddings pour calculer
    la similarité entre compétences CV et Job
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        if not ML_AVAILABLE:
            raise ImportError("Dépendances ML non disponibles. Installez : sentence-transformers, numpy, scikit-learn")
        
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Chargement du modèle Sentence Transformer"""
        try:
            logger.info(f"Chargement du modèle sémantique: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Modèle sémantique chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur chargement modèle sémantique: {e}")
            raise
    
    def calculate_similarity(self, cv_skills: List[str], job_skills: List[str]) -> float:
        """
        Calcule la similarité sémantique entre compétences CV et Job
        
        Args:
            cv_skills: Liste des compétences du CV
            job_skills: Liste des compétences requises pour le job
            
        Returns:
            Score de similarité entre 0 et 1
        """
        if not self.model:
            logger.warning("Modèle sémantique non disponible")
            return 0.0
        
        if not cv_skills or not job_skills:
            return 0.0
        
        try:
            # Nettoyage et préparation des compétences
            cv_skills_clean = [skill.strip().lower() for skill in cv_skills if skill.strip()]
            job_skills_clean = [skill.strip().lower() for skill in job_skills if skill.strip()]
            
            if not cv_skills_clean or not job_skills_clean:
                return 0.0
            
            # Génération des embeddings
            cv_embeddings = self.model.encode(cv_skills_clean)
            job_embeddings = self.model.encode(job_skills_clean)
            
            # Calcul de la matrice de similarité
            similarity_matrix = cosine_similarity(cv_embeddings, job_embeddings)
            
            # Stratégies de calcul du score final
            scores = {
                'max_similarity': self._max_similarity_strategy(similarity_matrix),
                'average_best_matches': self._average_best_matches_strategy(similarity_matrix),
                'weighted_coverage': self._weighted_coverage_strategy(similarity_matrix, len(job_skills_clean))
            }
            
            # Score final combiné
            final_score = (
                scores['max_similarity'] * 0.3 +
                scores['average_best_matches'] * 0.4 +
                scores['weighted_coverage'] * 0.3
            )
            
            logger.debug(f"Similarité sémantique calculée: {final_score:.3f}")
            return final_score
            
        except Exception as e:
            logger.error(f"Erreur calcul similarité sémantique: {e}")
            return 0.0
    
    def _max_similarity_strategy(self, similarity_matrix: np.ndarray) -> float:
        """Stratégie basée sur la similarité maximale"""
        return float(np.max(similarity_matrix))
    
    def _average_best_matches_strategy(self, similarity_matrix: np.ndarray) -> float:
        """Stratégie basée sur la moyenne des meilleures correspondances"""
        # Pour chaque compétence job, prendre la meilleure correspondance CV
        best_matches = np.max(similarity_matrix, axis=0)
        return float(np.mean(best_matches))
    
    def _weighted_coverage_strategy(self, similarity_matrix: np.ndarray, num_job_skills: int) -> float:
        """Stratégie pondérée par la couverture des compétences job"""
        # Seuil de similarité acceptable
        threshold = 0.7
        
        # Compter combien de compétences job ont une correspondance acceptable
        covered_skills = np.sum(np.max(similarity_matrix, axis=0) >= threshold)
        coverage_ratio = covered_skills / num_job_skills
        
        # Score moyen des compétences couvertes
        covered_scores = np.max(similarity_matrix, axis=0)
        covered_scores = covered_scores[covered_scores >= threshold]
        
        if len(covered_scores) > 0:
            average_covered_score = np.mean(covered_scores)
        else:
            average_covered_score = 0.0
        
        # Combinaison ratio de couverture et qualité des correspondances
        return float(coverage_ratio * 0.6 + average_covered_score * 0.4)
    
    def analyze_skill_matches(self, cv_skills: List[str], job_skills: List[str], threshold: float = 0.7) -> Dict:
        """
        Analyse détaillée des correspondances entre compétences
        
        Args:
            cv_skills: Compétences du CV
            job_skills: Compétences requises
            threshold: Seuil de similarité pour considérer une correspondance
            
        Returns:
            Analyse détaillée avec correspondances et suggestions
        """
        if not self.model or not cv_skills or not job_skills:
            return {"matches": [], "missing_skills": job_skills, "suggestions": []}
        
        try:
            cv_skills_clean = [skill.strip() for skill in cv_skills if skill.strip()]
            job_skills_clean = [skill.strip() for skill in job_skills if skill.strip()]
            
            cv_embeddings = self.model.encode(cv_skills_clean)
            job_embeddings = self.model.encode(job_skills_clean)
            
            similarity_matrix = cosine_similarity(cv_embeddings, job_embeddings)
            
            matches = []
            missing_skills = []
            suggestions = []
            
            for j, job_skill in enumerate(job_skills_clean):
                # Trouver la meilleure correspondance pour cette compétence job
                best_cv_idx = np.argmax(similarity_matrix[:, j])
                best_similarity = similarity_matrix[best_cv_idx, j]
                
                if best_similarity >= threshold:
                    matches.append({
                        "job_skill": job_skill,
                        "cv_skill": cv_skills_clean[best_cv_idx],
                        "similarity": float(best_similarity),
                        "match_quality": self._get_match_quality(best_similarity)
                    })
                else:
                    missing_skills.append(job_skill)
                    
                    # Suggestion d'amélioration
                    if best_similarity > 0.4:  # Correspondance partielle
                        suggestions.append({
                            "missing_skill": job_skill,
                            "closest_cv_skill": cv_skills_clean[best_cv_idx],
                            "similarity": float(best_similarity),
                            "suggestion": f"Développer '{job_skill}' (proche de '{cv_skills_clean[best_cv_idx]}')"
                        })
            
            return {
                "matches": matches,
                "missing_skills": missing_skills,
                "suggestions": suggestions,
                "coverage_ratio": len(matches) / len(job_skills_clean) if job_skills_clean else 0,
                "total_job_skills": len(job_skills_clean),
                "matched_skills": len(matches)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse des correspondances: {e}")
            return {"error": str(e)}
    
    def _get_match_quality(self, similarity: float) -> str:
        """Détermine la qualité de la correspondance"""
        if similarity >= 0.9:
            return "excellente"
        elif similarity >= 0.8:
            return "très_bonne"
        elif similarity >= 0.7:
            return "bonne"
        elif similarity >= 0.6:
            return "moyenne"
        else:
            return "faible"
    
    def get_model_info(self) -> Dict:
        """Informations sur le modèle chargé"""
        return {
            "model_name": self.model_name,
            "model_loaded": self.model is not None,
            "ml_available": ML_AVAILABLE,
            "embedding_dimension": self.model.get_sentence_embedding_dimension() if self.model else None
        }
