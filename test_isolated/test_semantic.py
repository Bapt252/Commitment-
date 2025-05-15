#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test indépendant pour l'analyseur sémantique de compétences.
Ce script est conçu pour fonctionner sans dépendances complexes.
"""

import os
import sys
import unittest
import logging
import difflib
from typing import List, Dict, Any, Tuple

# Désactiver les logs pour les tests
logging.basicConfig(level=logging.ERROR)

# Classe SemanticAnalyzer simplifiée pour les tests
class SemanticAnalyzer:
    """Version simplifiée de l'analyseur sémantique pour les tests"""
    
    def __init__(self):
        self.skills_relationships = self._load_skills_relationships()
    
    def _load_skills_relationships(self) -> Dict[str, List[str]]:
        relationships = {
            "react": ["reactjs", "react.js", "react native"],
            "angular": ["angularjs", "angular.js", "angular 2+"],
            "vue": ["vuejs", "vue.js", "vuex"],
            "python": ["django", "flask", "fastapi", "pandas", "numpy", "scikit-learn"],
            "javascript": ["js", "typescript", "ts", "node.js", "nodejs"],
            "java": ["spring", "spring boot", "j2ee", "jakarta ee"],
            "sql": ["mysql", "postgresql", "postgres", "oracle", "sql server"],
            "nosql": ["mongodb", "cassandra", "couchdb", "firebase"],
            "devops": ["ci/cd", "jenkins", "docker", "kubernetes", "k8s"],
            "agile": ["scrum", "kanban", "lean", "xp", "extreme programming"],
        }
        return relationships
    
    def calculate_skills_similarity(self, cv_skills: List[str], job_skills: List[str]) -> float:
        # Normaliser les compétences
        cv_skills_normalized = [skill.lower() for skill in cv_skills]
        job_skills_normalized = [skill.lower() for skill in job_skills]
        
        # Si pas de compétences dans l'un des deux, retourner 0
        if not cv_skills_normalized or not job_skills_normalized:
            return 0.0
        
        # Correspondance directe
        matched_skills = set(cv_skills_normalized).intersection(set(job_skills_normalized))
        direct_match_score = len(matched_skills) / len(job_skills_normalized)
        
        # Si on a une correspondance parfaite, on retourne 1.0 directement
        if direct_match_score == 1.0:
            return 1.0
        
        # Correspondance avec expansion sémantique
        expanded_matches = self._get_expanded_matches(cv_skills_normalized, job_skills_normalized)
        semantic_match_score = min(1.0, len(expanded_matches) / len(job_skills_normalized))
        
        # Combiner les scores
        combined_score = (direct_match_score * 0.7) + (semantic_match_score * 0.3)
        
        return combined_score
    
    def _get_expanded_matches(self, cv_skills: List[str], job_skills: List[str]) -> List[Tuple[str, str, float]]:
        matches = []
        
        # 1. Utiliser notre dictionnaire de relations
        for job_skill in job_skills:
            if job_skill in cv_skills:
                continue
                
            for cv_skill in cv_skills:
                if self._are_skills_related(cv_skill, job_skill):
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
        for base_skill, related_skills in self.skills_relationships.items():
            if skill1 == base_skill and skill2 in related_skills:
                return True
            if skill2 == base_skill and skill1 in related_skills:
                return True
            if skill1 in related_skills and skill2 in related_skills:
                return True
                
        return False

# Test unitaires
class TestSemanticAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = SemanticAnalyzer()
    
    def test_exact_matches(self):
        """Test lorsque toutes les compétences du poste sont dans le CV"""
        cv_skills = ["Python", "JavaScript", "React", "SQL"]
        job_skills = ["Python", "JavaScript", "React"]
        similarity = self.analyzer.calculate_skills_similarity(cv_skills, job_skills)
        self.assertEqual(similarity, 1.0)
        print("✓ Test des correspondances exactes réussi")
    
    def test_partial_matches(self):
        """Test lorsque certaines compétences du poste sont dans le CV"""
        cv_skills = ["Python", "JavaScript", "Angular"]
        job_skills = ["Python", "JavaScript", "React", "SQL"]
        similarity = self.analyzer.calculate_skills_similarity(cv_skills, job_skills)
        # Pour 2/4 compétences exactes, on attend 0.5*0.7 = 0.35
        self.assertAlmostEqual(similarity, 0.35, delta=0.05)
        print("✓ Test des correspondances partielles réussi")
    
    def test_semantic_matches(self):
        """Test lorsque des compétences liées sont présentes"""
        cv_skills = ["React", "MySQL", "TypeScript"]
        job_skills = ["JavaScript", "SQL", "Frontend"]
        similarity = self.analyzer.calculate_skills_similarity(cv_skills, job_skills)
        # On s'attend à ce que TypeScript soit lié à JavaScript, et MySQL à SQL
        self.assertTrue(0.5 <= similarity <= 0.7)
        print("✓ Test des correspondances sémantiques réussi")
    
    def test_no_matches(self):
        """Test sans correspondances"""
        cv_skills = ["Python", "Django", "Flask"]
        job_skills = ["Java", "Spring", "Hibernate"]
        similarity = self.analyzer.calculate_skills_similarity(cv_skills, job_skills)
        # Pas de correspondances directes, mais peut-être sémantiques
        self.assertTrue(similarity < 0.3)
        print("✓ Test sans correspondances réussi")
        
    def test_skills_relationship(self):
        """Test des relations entre compétences"""
        self.assertTrue(self.analyzer._are_skills_related("python", "django"))
        self.assertTrue(self.analyzer._are_skills_related("django", "flask"))
        self.assertFalse(self.analyzer._are_skills_related("python", "java"))
        print("✓ Test des relations entre compétences réussi")

if __name__ == "__main__":
    print("Exécution des tests indépendants de l'analyseur sémantique...")
    unittest.main()
