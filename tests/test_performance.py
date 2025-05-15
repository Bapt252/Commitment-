#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests de performance pour le système SmartMatch."""

import unittest
import time
import os
import sys
from unittest.mock import patch

# Ajouter le répertoire parent au path pour pouvoir importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import des modules à tester
from app.smartmatch import SmartMatchEngine
from tests.test_data_generator import generate_test_candidates, generate_test_companies

class PerformanceTests(unittest.TestCase):
    """Tests de performance pour le système SmartMatch."""
    
    @patch('app.compat.GoogleMapsClient.get_travel_time')
    def test_matching_performance_small(self, mock_get_travel_time):
        """Test de performance avec un petit jeu de données."""
        # Configurer le mock pour éviter les appels API réels
        mock_get_travel_time.return_value = 30
        
        # Générer un petit jeu de données
        candidates = generate_test_candidates(20)
        companies = generate_test_companies(10)
        
        # Initialiser le moteur de matching
        matcher = SmartMatchEngine()
        
        # Mesurer le temps d'exécution
        start_time = time.time()
        
        results = matcher.match(candidates, companies)
        
        execution_time = time.time() - start_time
        
        # Afficher les informations de performance
        print(f"\nMatching de {len(candidates)} candidats et {len(companies)} entreprises")
        print(f"Temps d'exécution: {execution_time:.2f} secondes")
        print(f"Nombre de matchings calculés: {len(results)}")
        
        # Vérifier que le temps d'exécution est acceptable
        self.assertLess(execution_time, 5)  # Devrait prendre moins de 5 secondes
    
    @patch('app.compat.GoogleMapsClient.get_travel_time')
    def test_matching_performance_medium(self, mock_get_travel_time):
        """Test de performance avec un jeu de données moyen."""
        # Configurer le mock pour éviter les appels API réels
        mock_get_travel_time.return_value = 30
        
        # Générer un jeu de données moyen
        candidates = generate_test_candidates(50)
        companies = generate_test_companies(20)
        
        # Initialiser le moteur de matching
        matcher = SmartMatchEngine()
        
        # Mesurer le temps d'exécution
        start_time = time.time()
        
        results = matcher.match(candidates, companies)
        
        execution_time = time.time() - start_time
        
        # Afficher les informations de performance
        print(f"\nMatching de {len(candidates)} candidats et {len(companies)} entreprises")
        print(f"Temps d'exécution: {execution_time:.2f} secondes")
        print(f"Nombre de matchings calculés: {len(results)}")
        
        # Vérifier que le temps d'exécution est acceptable
        self.assertLess(execution_time, 30)  # Devrait prendre moins de 30 secondes
    
    @unittest.skip("Test de performance long qui n'est pas exécuté par défaut")
    @patch('app.compat.GoogleMapsClient.get_travel_time')
    def test_matching_performance_large(self, mock_get_travel_time):
        """Test de performance avec un grand jeu de données."""
        # Configurer le mock pour éviter les appels API réels
        mock_get_travel_time.return_value = 30
        
        # Générer un grand jeu de données
        candidates = generate_test_candidates(500)
        companies = generate_test_companies(100)
        
        # Initialiser le moteur de matching
        matcher = SmartMatchEngine()
        
        # Mesurer le temps d'exécution
        start_time = time.time()
        
        results = matcher.match(candidates, companies)
        
        execution_time = time.time() - start_time
        
        # Afficher les informations de performance
        print(f"\nMatching de {len(candidates)} candidats et {len(companies)} entreprises")
        print(f"Temps d'exécution: {execution_time:.2f} secondes")
        print(f"Nombre de matchings calculés: {len(results)}")
        
        # Vérifier que le temps d'exécution est acceptable
        self.assertLess(execution_time, 300)  # Devrait prendre moins de 5 minutes
    
    @patch('app.compat.GoogleMapsClient.get_travel_time')
    def test_scoring_performance(self, mock_get_travel_time):
        """Test de performance du calcul de score."""
        # Configurer le mock pour éviter les appels API réels
        mock_get_travel_time.return_value = 30
        
        # Créer un candidat et une entreprise de test
        candidate = {
            "id": "cand_1",
            "skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
            "location": "Paris",
            "remote_preference": "hybrid",
            "experience": 5,
            "salary_expectation": 50000
        }
        
        company = {
            "id": "comp_1",
            "required_skills": ["Python", "JavaScript", "Django", "PostgreSQL"],
            "location": "Paris",
            "remote_policy": "hybrid",
            "required_experience": 3,
            "salary_range": {"min": 45000, "max": 60000}
        }
        
        # Initialiser le moteur de matching
        matcher = SmartMatchEngine()
        
        # Mesurer le temps de 1000 calculs de score
        start_time = time.time()
        
        for _ in range(1000):
            score, details = matcher._calculate_match_score(candidate, company)
        
        execution_time = time.time() - start_time
        
        # Afficher les informations de performance
        print(f"\n1000 calculs de score")
        print(f"Temps d'exécution: {execution_time:.2f} secondes")
        print(f"Temps moyen par calcul: {(execution_time * 1000 / 1000):.2f} ms")
        
        # Vérifier que le temps d'exécution est acceptable
        self.assertLess(execution_time, 5)  # Devrait prendre moins de 5 secondes

if __name__ == "__main__":
    unittest.main()
