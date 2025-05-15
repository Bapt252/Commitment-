#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tests unitaires pour l'analyseur sémantique de compétences.
"""

import unittest
import sys
import os

# Ajouter le répertoire du projet au chemin
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer l'analyseur sémantique
from app.semantic.analyzer import SemanticAnalyzer

class TestSemanticAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = SemanticAnalyzer()
    
    def test_exact_matches(self):
        """Test avec des correspondances exactes"""
        cv_skills = ["Python", "JavaScript", "React", "SQL"]
        job_skills = ["Python", "JavaScript", "React"]
        similarity = self.analyzer.calculate_skills_similarity(cv_skills, job_skills)
        self.assertEqual(similarity, 1.0)  # Correspondance parfaite
    
    def test_partial_matches(self):
        """Test avec des correspondances partielles"""
        cv_skills = ["Python", "JavaScript", "Angular"]
        job_skills = ["Python", "JavaScript", "React", "SQL"]
        similarity = self.analyzer.calculate_skills_similarity(cv_skills, job_skills)
        self.assertTrue(0.4 <= similarity <= 0.6)  # Correspondance partielle
    
    def test_semantic_matches(self):
        """Test avec des correspondances sémantiques"""
        cv_skills = ["React", "MySQL", "TypeScript"]
        job_skills = ["JavaScript", "SQL", "Frontend"]
        similarity = self.analyzer.calculate_skills_similarity(cv_skills, job_skills)
        self.assertTrue(similarity > 0.5)  # Devrait reconnaître les relations sémantiques
    
    def test_no_matches(self):
        """Test sans correspondances"""
        cv_skills = ["Python", "Django", "Flask"]
        job_skills = ["Java", "Spring", "Hibernate"]
        similarity = self.analyzer.calculate_skills_similarity(cv_skills, job_skills)
        self.assertTrue(similarity < 0.3)  # Peu ou pas de correspondances
    
    def test_empty_skills(self):
        """Test avec des listes vides"""
        cv_skills = []
        job_skills = ["Python", "JavaScript"]
        similarity = self.analyzer.calculate_skills_similarity(cv_skills, job_skills)
        self.assertEqual(similarity, 0.0)  # Pas de correspondance
        
        cv_skills = ["Python", "JavaScript"]
        job_skills = []
        similarity = self.analyzer.calculate_skills_similarity(cv_skills, job_skills)
        self.assertEqual(similarity, 0.0)  # Pas de correspondance
    
    def test_skills_relationships(self):
        """Test des relations entre compétences"""
        # Test de relation directe
        self.assertTrue(self.analyzer._are_skills_related("python", "django"))
        self.assertTrue(self.analyzer._are_skills_related("django", "python"))
        
        # Test de relation indirecte
        self.assertTrue(self.analyzer._are_skills_related("django", "flask"))
        
        # Test sans relation
        self.assertFalse(self.analyzer._are_skills_related("python", "react"))

if __name__ == "__main__":
    unittest.main()
