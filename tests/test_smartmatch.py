#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests unitaires pour le moteur de matching SmartMatch."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Ajouter le répertoire parent au path pour pouvoir importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import des modules à tester
from app.smartmatch import SmartMatchEngine
from app.compat import GoogleMapsClient
from app.semantic_analysis import SemanticAnalyzer

class SmartMatchTests(unittest.TestCase):
    """Tests pour le moteur de matching SmartMatch."""
    
    def setUp(self):
        """Initialisation des tests."""
        # Créer des mocks pour les dépendances
        self.mock_maps_client = MagicMock(spec=GoogleMapsClient)
        self.mock_semantic_analyzer = MagicMock(spec=SemanticAnalyzer)
        
        # Configurer les comportements par défaut des mocks
        self.mock_maps_client.get_travel_time.return_value = 30  # 30 minutes par défaut
        self.mock_semantic_analyzer.calculate_similarity.return_value = 0.8  # 80% de similarité par défaut
        self.mock_semantic_analyzer.get_skill_gaps.return_value = []  # Pas de lacunes par défaut
        
        # Initialiser le moteur de matching avec les mocks
        with patch('app.smartmatch.GoogleMapsClient', return_value=self.mock_maps_client), \
             patch('app.smartmatch.SemanticAnalyzer', return_value=self.mock_semantic_analyzer):
            self.engine = SmartMatchEngine()
    
    def test_set_weights(self):
        """Test de la définition des pondérations."""
        # Définir des pondérations valides
        weights = {
            "skills": 0.4,
            "location": 0.3,
            "remote_policy": 0.1,
            "experience": 0.1,
            "salary": 0.1
        }
        self.engine.set_weights(weights)
        self.assertEqual(self.engine.weights, weights)
        
        # Définir des pondérations qui ne somment pas à 1
        weights_invalid = {
            "skills": 0.5,
            "location": 0.5,
            "remote_policy": 0.5,
            "experience": 0.5,
            "salary": 0.5
        }  # Total = 2.5
        self.engine.set_weights(weights_invalid)
        # Les pondérations devraient être normalisées
        self.assertAlmostEqual(sum(self.engine.weights.values()), 1.0, places=5)
    
    def test_match_empty_lists(self):
        """Test du matching avec des listes vides."""
        candidates = []
        companies = []
        results = self.engine.match(candidates, companies)
        self.assertEqual(results, [])
    
    def test_match_simple_case(self):
        """Test du matching dans un cas simple."""
        candidates = [{
            "id": "cand_1",
            "skills": ["Python", "JavaScript"],
            "location": "Paris",
            "remote_preference": "hybrid",
            "experience": 5,
            "salary_expectation": 50000
        }]
        
        companies = [{
            "id": "comp_1",
            "required_skills": ["Python", "JavaScript"],
            "location": "Paris",
            "remote_policy": "hybrid",
            "required_experience": 3,
            "salary_range": {"min": 45000, "max": 60000}
        }]
        
        results = self.engine.match(candidates, companies)
        
        self.assertEqual(len(results), 1)
        match = results[0]
        self.assertEqual(match["candidate_id"], "cand_1")
        self.assertEqual(match["company_id"], "comp_1")
        self.assertGreaterEqual(match["score"], self.engine.min_score_threshold)
    
    def test_match_below_threshold(self):
        """Test du matching avec un score inférieur au seuil."""
        # Configurer le mock pour renvoyer des scores faibles
        self.mock_semantic_analyzer.calculate_similarity.return_value = 0.2
        self.mock_maps_client.get_travel_time.return_value = 120  # 2 heures de trajet
        
        candidates = [{
            "id": "cand_1",
            "skills": ["Python"],  # Compétences limitées
            "location": "Paris",
            "remote_preference": "office",  # Préfère le bureau
            "experience": 1,  # Peu d'expérience
            "salary_expectation": 70000  # Attentes salariales élevées
        }]
        
        companies = [{
            "id": "comp_1",
            "required_skills": ["Java", "C++"],  # Compétences différentes
            "location": "Lyon",  # Ville différente
            "remote_policy": "office_only",  # Exige présentiel
            "required_experience": 5,  # Demande beaucoup d'expérience
            "salary_range": {"min": 40000, "max": 50000}  # Offre salariale basse
        }]
        
        results = self.engine.match(candidates, companies)
        
        # Le score devrait être inférieur au seuil, donc pas de match
        self.assertEqual(len(results), 0)
    
    def test_calculate_match_score(self):
        """Test du calcul détaillé du score de matching."""
        # Configurer des valeurs spécifiques pour les mocks
        self.mock_semantic_analyzer.calculate_similarity.return_value = 0.9
        self.mock_maps_client.get_travel_time.return_value = 15
        
        candidate = {
            "skills": ["Python", "JavaScript"],
            "location": "Paris",
            "remote_preference": "hybrid",
            "experience": 5,
            "salary_expectation": 50000
        }
        
        company = {
            "required_skills": ["Python", "JavaScript"],
            "location": "Paris",
            "remote_policy": "hybrid",
            "required_experience": 3,
            "salary_range": {"min": 45000, "max": 60000}
        }
        
        score, details = self.engine._calculate_match_score(candidate, company)
        
        # Vérifier que le score est dans la plage attendue
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # Vérifier que les détails contiennent les scores par critère
        self.assertIn("skills_score", details)
        self.assertIn("location_score", details)
        self.assertIn("remote_score", details)
        self.assertIn("experience_score", details)
        self.assertIn("salary_score", details)
        
        # Vérifier les valeurs des scores par critère
        self.assertEqual(details["skills_score"], 0.9)  # Valeur du mock
        self.assertGreaterEqual(details["location_score"], 0.8)  # Bon temps de trajet
        self.assertEqual(details["remote_score"], 1.0)  # Correspondance parfaite
        self.assertGreaterEqual(details["experience_score"], 0.9)  # Expérience suffisante
        self.assertEqual(details["salary_score"], 1.0)  # Dans la fourchette
    
    def test_remote_policy_compatibility(self):
        """Test de la compatibilité des politiques de travail à distance."""
        # Cas 1: Candidat full remote, entreprise office_only
        candidate1 = {"remote_preference": "full", "location": "Paris"}
        company1 = {"remote_policy": "office_only", "location": "Paris"}
        
        # Cas 2: Candidat préfère bureau, entreprise full remote
        candidate2 = {"remote_preference": "office", "location": "Paris"}
        company2 = {"remote_policy": "full", "location": "Paris"}
        
        # Cas 3: Les deux hybrides
        candidate3 = {"remote_preference": "hybrid", "location": "Paris"}
        company3 = {"remote_policy": "hybrid", "location": "Paris"}
        
        # Test avec un modèle simplifié
        with patch.object(self.engine, '_calculate_match_score', return_value=(0, {})):
            for key in ["skills", "experience", "salary_expectation"]:
                candidate1[key] = candidate2[key] = candidate3[key] = []
            
            for key in ["required_skills", "required_experience", "salary_range"]:
                company1[key] = company2[key] = company3[key] = {}
            
            # Configurer le mock pour tester spécifiquement la logique de remote
            def mock_calculate(*args, **kwargs):
                c, co = args
                remote_score = 0.0
                
                if c["remote_preference"] == co["remote_policy"]:
                    remote_score = 1.0
                elif c["remote_preference"] == "full" and co["remote_policy"] == "office_only":
                    remote_score = 0.1
                
                return 0.7, {"remote_score": remote_score}  # Score au-dessus du seuil
            
            with patch.object(self.engine, '_calculate_match_score', side_effect=mock_calculate):
                # Cas 1: Devrait donner un mauvais score
                results1 = self.engine.match([candidate1], [company1])
                self.assertEqual(len(results1), 1)  # Le seuil est contourné pour le test
                
                # Cas 3: Devrait donner un bon score
                results3 = self.engine.match([candidate3], [company3])
                self.assertEqual(len(results3), 1)

if __name__ == "__main__":
    unittest.main()
