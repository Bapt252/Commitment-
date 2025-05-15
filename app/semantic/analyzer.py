"""
Module d'analyse sémantique pour la comparaison de compétences.
Ce module fournit des outils pour une analyse avancée des correspondances entre compétences,
allant au-delà de la simple correspondance exacte.
"""

import os
import logging
from typing import List, Dict, Any, Tuple
import difflib  # Pour la comparaison de chaînes simple

# Importations conditionnelles pour les fonctionnalités avancées
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import nltk
    from nltk.corpus import wordnet
    HAS_NLTK = True
    # Télécharger les ressources NLTK nécessaires
    nltk.download('wordnet', quiet=True)
except ImportError:
    HAS_NLTK = False

logger = logging.getLogger(__name__)

class SemanticAnalyzer:
    """Analyseur sémantique pour la comparaison de compétences"""
    
    def __init__(self):
        # Dictionnaire de synonymes et de compétences liées
        self.skills_relationships = self._load_skills_relationships()
    
    def _load_skills_relationships(self) -> Dict[str, List[str]]:
        """Charge les relations entre compétences depuis un dictionnaire prédéfini"""
        # Dictionnaire de base avec des groupes de compétences similaires
        relationships = {
            # Frameworks/Bibliothèques frontend
            "react": ["reactjs", "react.js", "react native"],
            "angular": ["angularjs", "angular.js", "angular 2+"],
            "vue": ["vuejs", "vue.js", "vuex"],
            
            # Langages de programmation
            "python": ["django", "flask", "fastapi", "pandas", "numpy", "scikit-learn"],
            "javascript": ["js", "typescript", "ts", "node.js", "nodejs"],
            "java": ["spring", "spring boot", "j2ee", "jakarta ee"],
            
            # Bases de données
            "sql": ["mysql", "postgresql", "postgres", "oracle", "sql server"],
            "nosql": ["mongodb", "cassandra", "couchdb", "firebase"],
            
            # DevOps
            "devops": ["ci/cd", "jenkins", "docker", "kubernetes", "k8s"],
            
            # Méthodologies
            "agile": ["scrum", "kanban", "lean", "xp", "extreme programming"],
        }
        
        return relationships
    
    def calculate_skills_similarity(self, cv_skills: List[str], job_skills: List[str]) -> float:
        """
        Calcule la similarité entre deux ensembles de compétences
        
        Args:
            cv_skills: Liste des compétences du CV
            job_skills: Liste des compétences requises pour le poste
            
        Returns:
            Score de similarité entre 0 et 1
        """
        # Normaliser les compétences (minuscules)
        cv_skills_normalized = [skill.lower() for skill in cv_skills]
        job_skills_normalized = [skill.lower() for skill in job_skills]
        
        # Si pas de compétences dans l'un des deux, retourner 0
        if not cv_skills_normalized or not job_skills_normalized:
            return 0.0
        
        # Approche 1: Correspondance directe (stricte)
        matched_skills = set(cv_skills_normalized).intersection(set(job_skills_normalized))
        direct_match_score = len(matched_skills) / len(job_skills_normalized)
        
        # Approche 2: Correspondance avec expansion sémantique
        expanded_matches = self._get_expanded_matches(cv_skills_normalized, job_skills_normalized)
        semantic_match_score = min(1.0, len(expanded_matches) / len(job_skills_normalized))
        
        # Combiner les scores (donner plus de poids à la correspondance directe)
        combined_score = (direct_match_score * 0.7) + (semantic_match_score * 0.3)
        
        return combined_score
    
    def _get_expanded_matches(self, cv_skills: List[str], job_skills: List[str]) -> List[Tuple[str, str, float]]:
        """
        Trouve les correspondances élargies entre les compétences
        
        Args:
            cv_skills: Liste normalisée des compétences du CV
            job_skills: Liste normalisée des compétences du poste
            
        Returns:
            Liste de tuples (compétence_cv, compétence_job, score)
        """
        matches = []
        
        # 1. Utiliser notre dictionnaire de relations
        for job_skill in job_skills:
            # Correspondances directes déjà comptées ailleurs
            if job_skill in cv_skills:
                continue
                
            # Chercher des compétences liées
            for cv_skill in cv_skills:
                # Vérifier si l'une est liée à l'autre
                if self._are_skills_related(cv_skill, job_skill):
                    matches.append((cv_skill, job_skill, 0.9))  # Score élevé pour les relations connues
        
        # 2. Utiliser la similarité de chaîne pour les cas non couverts
        if not matches:
            for job_skill in job_skills:
                if job_skill in cv_skills:
                    continue
                
                for cv_skill in cv_skills:
                    # Calculer la similarité de chaîne (ratio de difflib)
                    similarity = difflib.SequenceMatcher(None, cv_skill, job_skill).ratio()
                    if similarity > 0.8:  # Seuil arbitraire pour les correspondances
                        matches.append((cv_skill, job_skill, similarity * 0.7))  # Pondération plus faible
        
        # 3. Utiliser WordNet si disponible pour trouver des synonymes
        if HAS_NLTK and not matches:
            for job_skill in job_skills:
                if job_skill in cv_skills:
                    continue
                
                job_synsets = wordnet.synsets(job_skill)
                
                for cv_skill in cv_skills:
                    cv_synsets = wordnet.synsets(cv_skill)
                    
                    # Calculer la similarité maximale entre les synsets
                    max_similarity = 0
                    for job_synset in job_synsets:
                        for cv_synset in cv_synsets:
                            similarity = job_synset.path_similarity(cv_synset)
                            if similarity and similarity > max_similarity:
                                max_similarity = similarity
                    
                    if max_similarity > 0.5:  # Seuil pour les synonymes
                        matches.append((cv_skill, job_skill, max_similarity * 0.6))  # Pondération plus faible
        
        return matches
    
    def _are_skills_related(self, skill1: str, skill2: str) -> bool:
        """
        Vérifie si deux compétences sont liées selon notre dictionnaire
        
        Args:
            skill1: Première compétence
            skill2: Deuxième compétence
            
        Returns:
            True si les compétences sont liées, False sinon
        """
        # Vérifier dans les deux sens
        for base_skill, related_skills in self.skills_relationships.items():
            if skill1 == base_skill and skill2 in related_skills:
                return True
            if skill2 == base_skill and skill1 in related_skills:
                return True
            if skill1 in related_skills and skill2 in related_skills:
                return True
                
        return False
