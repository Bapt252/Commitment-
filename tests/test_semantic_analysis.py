#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests unitaires pour l'analyse sémantique des compétences."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Ajouter le répertoire parent au path pour pouvoir importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import des modules à tester
from app.semantic_analysis import SemanticAnalyzer

class SemanticAnalysisTests(unittest.TestCase):
    """Tests pour l'analyse sémantique des compétences."""
    
    def setUp(self):
        """Initialisation des tests."""
        self.analyzer = SemanticAnalyzer()
    
    def test_normalize_skill(self):
        """Test de la normalisation des compétences."""
        # Test de la conversion en minuscules
        self.assertEqual(self.analyzer.normalize_skill("Python"), "python")
        self.assertEqual(self.analyzer.normalize_skill("JAVA"), "java")
        
        # Test des synonymes
        self.assertEqual(self.analyzer.normalize_skill("js"), "javascript")
        self.assertEqual(self.analyzer.normalize_skill("reactjs"), "react")
        self.assertEqual(self.analyzer.normalize_skill("nodejs"), "node.js")
    
    def test_calculate_similarity_identical_skills(self):
        """Test du calcul de similarité avec des compétences identiques."""
        skills1 = ["Python", "JavaScript", "React"]
        skills2 = ["Python", "JavaScript", "React"]
        similarity = self.analyzer.calculate_similarity(skills1, skills2)
        self.assertAlmostEqual(similarity, 1.0, places=2)
    
    def test_calculate_similarity_no_overlap(self):
        """Test du calcul de similarité sans chevauchement de compétences."""
        skills1 = ["Python", "Django", "PostgreSQL"]
        skills2 = ["JavaScript", "React", "Node.js"]
        similarity = self.analyzer.calculate_similarity(skills1, skills2)
        self.assertLessEqual(similarity, 0.4)  # Devrait être relativement bas
    
    def test_calculate_similarity_partial_overlap(self):
        """Test du calcul de similarité avec chevauchement partiel."""
        skills1 = ["Python", "JavaScript", "React", "Django"]
        skills2 = ["Python", "JavaScript", "Node.js", "Express"]
        similarity = self.analyzer.calculate_similarity(skills1, skills2)
        self.assertGreaterEqual(similarity, 0.5)  # Chevauchement significatif
        self.assertLessEqual(similarity, 0.8)  # Mais pas identique
    
    def test_calculate_similarity_with_synonyms(self):
        """Test du calcul de similarité avec des synonymes."""
        skills1 = ["Python", "js", "reactjs"]
        skills2 = ["python", "JavaScript", "React"]
        similarity = self.analyzer.calculate_similarity(skills1, skills2)
        self.assertAlmostEqual(similarity, 1.0, places=2)  # Devrait être très proche de 1.0
    
    def test_calculate_similarity_related_skills(self):
        """Test du calcul de similarité avec des compétences liées."""
        skills1 = ["Python", "Data Science"]
        skills2 = ["Machine Learning", "Python"]
        similarity = self.analyzer.calculate_similarity(skills1, skills2)
        self.assertGreaterEqual(similarity, 0.7)  # Data Science et Machine Learning sont liés
    
    def test_calculate_similarity_empty_lists(self):
        """Test du calcul de similarité avec des listes vides."""
        skills1 = []
        skills2 = ["Python", "JavaScript"]
        similarity1 = self.analyzer.calculate_similarity(skills1, skills2)
        similarity2 = self.analyzer.calculate_similarity(skills2, skills1)
        self.assertEqual(similarity1, 0.0)
        self.assertEqual(similarity2, 0.0)
        
        # Deux listes vides
        similarity3 = self.analyzer.calculate_similarity([], [])
        self.assertEqual(similarity3, 0.0)
    
    def test_get_skill_gaps_identical_skills(self):
        """Test de l'identification des compétences manquantes avec des compétences identiques."""
        candidate_skills = ["Python", "JavaScript", "React"]
        job_skills = ["Python", "JavaScript", "React"]
        gaps = self.analyzer.get_skill_gaps(candidate_skills, job_skills)
        self.assertEqual(gaps, [])
    
    def test_get_skill_gaps_missing_skills(self):
        """Test de l'identification des compétences manquantes."""
        candidate_skills = ["Python", "JavaScript"]
        job_skills = ["Python", "JavaScript", "React", "Node.js"]
        gaps = self.analyzer.get_skill_gaps(candidate_skills, job_skills)
        self.assertIn("react", gaps)
        self.assertIn("node.js", gaps)
    
    def test_get_skill_gaps_with_similar_skills(self):
        """Test de l'identification des compétences manquantes avec des compétences similaires."""
        # Le candidat a Python et Data Science, qui est similaire à Machine Learning
        candidate_skills = ["Python", "Data Science"]
        job_skills = ["Python", "Machine Learning"]
        gaps = self.analyzer.get_skill_gaps(candidate_skills, job_skills)
        self.assertEqual(gaps, [])  # Pas de lacune car Data Science et Machine Learning sont similaires
        
        # Maintenant avec une compétence vraiment manquante
        job_skills = ["Python", "Machine Learning", "AWS"]
        gaps = self.analyzer.get_skill_gaps(candidate_skills, job_skills)
        self.assertEqual(len(gaps), 1)
        self.assertIn("aws", gaps)
    
    def test_get_skill_gaps_with_synonyms(self):
        """Test de l'identification des compétences manquantes avec des synonymes."""
        candidate_skills = ["Python", "js", "vuejs"]
        job_skills = ["python", "JavaScript", "React"]
        gaps = self.analyzer.get_skill_gaps(candidate_skills, job_skills)
        self.assertEqual(len(gaps), 1)
        self.assertIn("react", gaps)

if __name__ == "__main__":
    unittest.main()
