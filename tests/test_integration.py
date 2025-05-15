#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests d'intégration pour le système SmartMatch."""

import unittest
import json
import os
import sys
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au path pour pouvoir importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import des modules à tester
from app.smartmatch import SmartMatchEngine
from app.insight_generator import InsightGenerator
from app.data_loader import DataLoader
from tests.test_data_generator import generate_test_candidates, generate_test_companies

class IntegrationTests(unittest.TestCase):
    """Tests d'intégration pour le système SmartMatch."""
    
    @classmethod
    def setUpClass(cls):
        """Initialisation générale des tests."""
        # Générer des données de test
        cls.candidates = generate_test_candidates(10)
        cls.companies = generate_test_companies(5)
        
        # Répertoire pour les données de test
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), "test_output")
        os.makedirs(cls.test_data_dir, exist_ok=True)
    
    def setUp(self):
        """Initialisation des tests."""
        # Initialiser les composants
        with patch('app.compat.GoogleMapsClient.get_travel_time', return_value=30):
            self.matcher = SmartMatchEngine()
            self.insight_generator = InsightGenerator()
            self.data_loader = DataLoader()
    
    def test_full_matching_pipeline(self):
        """Test du pipeline complet de matching."""
        with patch('app.compat.GoogleMapsClient.get_travel_time', return_value=30):
            # Exécuter le matching
            results = self.matcher.match(self.candidates, self.companies)
            
            # Vérifications
            self.assertIsNotNone(results)
            self.assertGreater(len(results), 0)
            
            # Vérifier la structure des résultats
            for match in results:
                self.assertIn("candidate_id", match)
                self.assertIn("company_id", match)
                self.assertIn("score", match)
                self.assertIn("details", match)
                
                # Vérifier que les scores sont dans une plage valide
                self.assertGreaterEqual(match["score"], 0)
                self.assertLessEqual(match["score"], 1)
                
                # Vérifier les détails
                details = match["details"]
                self.assertIn("skills_score", details)
                self.assertIn("location_score", details)
                self.assertIn("remote_score", details)
                self.assertIn("experience_score", details)
                self.assertIn("salary_score", details)
    
    def test_insights_generation(self):
        """Test de la génération d'insights à partir des résultats de matching."""
        with patch('app.compat.GoogleMapsClient.get_travel_time', return_value=30):
            # Exécuter le matching
            results = self.matcher.match(self.candidates, self.companies)
            
            # Générer des insights
            insights = self.insight_generator.generate_insights(results)
            
            # Vérifications
            self.assertIsNotNone(insights)
            self.assertGreater(len(insights), 0)
            
            # Vérifier la structure des insights
            for insight in insights:
                self.assertIn("type", insight)
                self.assertIn("message", insight)
    
    def test_data_saving(self):
        """Test de la sauvegarde des résultats de matching."""
        with patch('app.compat.GoogleMapsClient.get_travel_time', return_value=30):
            # Exécuter le matching
            results = self.matcher.match(self.candidates, self.companies)
            
            # Sauvegarder les résultats en JSON
            json_file = os.path.join(self.test_data_dir, "matching_results.json")
            self.data_loader.save_results(results, json_file)
            
            # Vérifier que le fichier a été créé
            self.assertTrue(os.path.exists(json_file))
            
            # Charger le fichier pour vérifier son contenu
            with open(json_file, 'r', encoding='utf-8') as f:
                loaded_results = json.load(f)
            
            # Vérifier que les données chargées correspondent aux résultats originaux
            self.assertEqual(len(loaded_results), len(results))
            
            # Sauvegarder les résultats en CSV
            csv_file = os.path.join(self.test_data_dir, "matching_results.csv")
            self.data_loader.save_results(results, csv_file)
            
            # Vérifier que le fichier a été créé
            self.assertTrue(os.path.exists(csv_file))
    
    def test_weight_adjustments(self):
        """Test de l'ajustement des pondérations du matching."""
        with patch('app.compat.GoogleMapsClient.get_travel_time', return_value=30):
            # Exécuter le matching avec les pondérations par défaut
            default_results = self.matcher.match(self.candidates, self.companies)
            
            # Modifier les pondérations
            new_weights = {
                "skills": 0.6,  # Mettre plus d'accent sur les compétences
                "location": 0.1,  # Moins d'importance à la localisation
                "remote_policy": 0.1,
                "experience": 0.1,
                "salary": 0.1
            }
            self.matcher.set_weights(new_weights)
            
            # Exécuter le matching avec les nouvelles pondérations
            new_results = self.matcher.match(self.candidates, self.companies)
            
            # Vérifier que les résultats ont changé
            if len(default_results) > 0 and len(new_results) > 0:
                # Comparer les scores du premier match
                self.assertNotEqual(default_results[0]["score"], new_results[0]["score"])
    
    def test_bidirectional_matching(self):
        """Test du matching bidirectionnel (préférences des deux côtés)."""
        with patch('app.compat.GoogleMapsClient.get_travel_time', return_value=30):
            # Créer des candidats et entreprises avec des préférences spécifiques
            candidates = [
                {
                    "id": "cand_remote",
                    "skills": ["Python", "JavaScript"],
                    "location": "Paris",
                    "remote_preference": "full",  # Préfère full remote
                    "experience": 5,
                    "salary_expectation": 50000
                },
                {
                    "id": "cand_office",
                    "skills": ["Python", "JavaScript"],
                    "location": "Paris",
                    "remote_preference": "office",  # Préfère bureau
                    "experience": 5,
                    "salary_expectation": 50000
                }
            ]
            
            companies = [
                {
                    "id": "comp_remote",
                    "required_skills": ["Python", "JavaScript"],
                    "location": "Paris",
                    "remote_policy": "full",  # Full remote
                    "required_experience": 3,
                    "salary_range": {"min": 45000, "max": 60000}
                },
                {
                    "id": "comp_office",
                    "required_skills": ["Python", "JavaScript"],
                    "location": "Paris",
                    "remote_policy": "office_only",  # Exige présentiel
                    "required_experience": 3,
                    "salary_range": {"min": 45000, "max": 60000}
                }
            ]
            
            # Exécuter le matching
            results = self.matcher.match(candidates, companies)
            
            # Vérifier que les matchings correspondent aux préférences
            best_matches = {}
            for match in results:
                candidate_id = match["candidate_id"]
                if candidate_id not in best_matches or match["score"] > best_matches[candidate_id]["score"]:
                    best_matches[candidate_id] = match
            
            # Le candidat remote devrait mieux matcher avec l'entreprise remote
            if "cand_remote" in best_matches:
                self.assertEqual(best_matches["cand_remote"]["company_id"], "comp_remote")
            
            # Le candidat bureau devrait mieux matcher avec l'entreprise office
            if "cand_office" in best_matches:
                self.assertEqual(best_matches["cand_office"]["company_id"], "comp_office")

if __name__ == "__main__":
    unittest.main()
