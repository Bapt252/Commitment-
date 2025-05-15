#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de diagnostic pour l'analyseur sémantique.
Ce script permet de voir en détail ce qui se passe dans les tests.
"""

import os
import sys
import difflib
from typing import List, Dict, Any, Tuple

class SemanticAnalyzer:
    """Version simplifiée de l'analyseur sémantique pour le diagnostic"""
    
    def __init__(self):
        self.skills_relationships = self._load_skills_relationships()
    
    def _load_skills_relationships(self) -> Dict[str, List[str]]:
        relationships = {
            # Frameworks/Bibliothèques frontend
            "react": ["reactjs", "react.js", "react native", "frontend"],
            "angular": ["angularjs", "angular.js", "angular 2+", "frontend"],
            "vue": ["vuejs", "vue.js", "vuex", "frontend"],
            
            # Langages de programmation
            "python": ["django", "flask", "fastapi", "pandas", "numpy", "scikit-learn"],
            "javascript": ["js", "typescript", "ts", "node.js", "nodejs", "frontend"],
            "java": ["spring", "spring boot", "j2ee", "jakarta ee"],
            
            # Bases de données
            "sql": ["mysql", "postgresql", "postgres", "oracle", "sql server"],
            "nosql": ["mongodb", "cassandra", "couchdb", "firebase"],
            
            # DevOps
            "devops": ["ci/cd", "jenkins", "docker", "kubernetes", "k8s"],
            
            # Méthodologies
            "agile": ["scrum", "kanban", "lean", "xp", "extreme programming"],
            
            # Catégories plus générales
            "frontend": ["react", "angular", "vue", "javascript", "typescript", "html", "css"],
            "backend": ["python", "java", "nodejs", "django", "flask", "spring"],
            "database": ["sql", "mysql", "postgresql", "mongodb", "nosql"],
        }
        return relationships
    
    def calculate_skills_similarity(self, cv_skills: List[str], job_skills: List[str]) -> float:
        """Calcule la similarité entre deux ensembles de compétences avec débogage"""
        # Normaliser les compétences
        cv_skills_normalized = [skill.lower() for skill in cv_skills]
        job_skills_normalized = [skill.lower() for skill in job_skills]
        
        print(f"CV Skills (normalized): {cv_skills_normalized}")
        print(f"Job Skills (normalized): {job_skills_normalized}")
        
        # Si pas de compétences dans l'un des deux, retourner 0
        if not cv_skills_normalized or not job_skills_normalized:
            return 0.0
        
        # Correspondance directe
        matched_skills = set(cv_skills_normalized).intersection(set(job_skills_normalized))
        direct_match_score = len(matched_skills) / len(job_skills_normalized)
        
        print(f"Direct matches: {matched_skills}")
        print(f"Direct match score: {direct_match_score}")
        
        # Si on a une correspondance parfaite, on retourne 1.0 directement
        if direct_match_score == 1.0:
            return 1.0
        
        # Correspondance avec expansion sémantique
        expanded_matches = self._get_expanded_matches(cv_skills_normalized, job_skills_normalized)
        semantic_match_score = min(1.0, len(expanded_matches) / len(job_skills_normalized))
        
        print(f"Expanded matches: {expanded_matches}")
        print(f"Semantic match score: {semantic_match_score}")
        
        # Combiner les scores
        combined_score = (direct_match_score * 0.7) + (semantic_match_score * 0.3)
        
        print(f"Combined score: {combined_score}")
        
        return combined_score
    
    def _get_expanded_matches(self, cv_skills: List[str], job_skills: List[str]) -> List[Tuple[str, str, float]]:
        """Trouve les correspondances élargies entre les compétences"""
        matches = []
        
        # 1. Utiliser notre dictionnaire de relations
        for job_skill in job_skills:
            if job_skill in cv_skills:
                continue
                
            for cv_skill in cv_skills:
                if self._are_skills_related(cv_skill, job_skill):
                    print(f"RELATION FOUND: {cv_skill} is related to {job_skill}")
                    matches.append((cv_skill, job_skill, 0.9))
        
        # 2. Utiliser la similarité de chaîne pour les cas non couverts
        if not matches:
            for job_skill in job_skills:
                if job_skill in cv_skills:
                    continue
                
                for cv_skill in cv_skills:
                    similarity = difflib.SequenceMatcher(None, cv_skill, job_skill).ratio()
                    if similarity > 0.8:
                        matches.append((cv_skill, job_skill, similarity * 0.7))
        
        return matches
    
    def _are_skills_related(self, skill1: str, skill2: str) -> bool:
        """Vérifie si deux compétences sont liées selon notre dictionnaire"""
        # Vérifier dans les deux sens
        for base_skill, related_skills in self.skills_relationships.items():
            if skill1 == base_skill and skill2 in related_skills:
                return True
            if skill2 == base_skill and skill1 in related_skills:
                return True
            if skill1 in related_skills and skill2 in related_skills:
                return True
                
        return False

# Test avec l'exemple problématique
def run_diagnostic_test():
    """Exécute un test de diagnostic sur l'exemple problématique"""
    analyzer = SemanticAnalyzer()
    
    print("=== TEST DE DIAGNOSTIC DES CORRESPONDANCES SÉMANTIQUES ===")
    cv_skills = ["React", "MySQL", "TypeScript"]
    job_skills = ["JavaScript", "SQL", "Frontend"]
    
    print("\n1. Vérification des relations:")
    print(f"React is related to Frontend: {analyzer._are_skills_related('react', 'frontend')}")
    print(f"TypeScript is related to JavaScript: {analyzer._are_skills_related('typescript', 'javascript')}")
    print(f"MySQL is related to SQL: {analyzer._are_skills_related('mysql', 'sql')}")
    
    print("\n2. Calcul du score de similarité:")
    similarity = analyzer.calculate_skills_similarity(cv_skills, job_skills)
    
    print(f"\nRÉSULTAT: Score de similarité final = {similarity}")
    print(f"Test attendu: 0.5 <= {similarity} <= 0.7")
    print(f"Test réussi: {0.5 <= similarity <= 0.7}")

if __name__ == "__main__":
    run_diagnostic_test()
