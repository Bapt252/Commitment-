"""
Tests unitaires pour Nexten SmartMatch
--------------------------------------
Suite de tests unitaires pour valider le fonctionnement du système SmartMatch.

Auteur: Claude/Anthropic
Date: 14/05/2025
"""

import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au chemin de recherche pour l'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer le SmartMatcher
try:
    from app.smartmatch import SmartMatcher
except ImportError:
    print("Erreur: Impossible d'importer SmartMatcher. Vérifiez que vous exécutez le script depuis le bon répertoire.")
    sys.exit(1)

class TestSmartMatcher(unittest.TestCase):
    """Suite de tests pour la classe SmartMatcher"""
    
    def setUp(self):
        """Initialisation avant chaque test"""
        self.api_key = "test_api_key"
        self.matcher = SmartMatcher(api_key=self.api_key)
        self.test_data = self.matcher.load_test_data()
        
        # Échantillons pour les tests
        self.candidate = self.test_data["candidates"][0]  # Jean Dupont
        self.job = self.test_data["jobs"][0]  # Développeur Python Senior
    
    @patch('app.smartmatch.requests.get')
    def test_calculate_travel_time(self, mock_get):
        """Teste le calcul du temps de trajet avec Google Maps API"""
        # Simuler une réponse réussie de l'API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "OK",
            "rows": [
                {
                    "elements": [
                        {
                            "status": "OK",
                            "duration": {
                                "value": 1800,  # 30 minutes en secondes
                                "text": "30 mins"
                            }
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Exécuter le test
        origin = "48.8566,2.3522"  # Paris
        destination = "48.8847,2.2967"  # Levallois-Perret
        travel_time = self.matcher.calculate_travel_time(origin, destination)
        
        # Vérifier le résultat
        self.assertEqual(travel_time, 30)
        
        # Vérifier que la requête a été correctement formée
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(kwargs['params']['origins'], origin)
        self.assertEqual(kwargs['params']['destinations'], destination)
        self.assertEqual(kwargs['params']['key'], self.api_key)
    
    def test_expand_skills(self):
        """Teste l'expansion des compétences avec synonymes"""
        # Compétences à tester
        skills = ["Python", "JavaScript", "Git"]
        
        # Exécuter l'expansion
        expanded = self.matcher.expand_skills(skills)
        
        # Vérifier que les compétences originales sont présentes
        for skill in skills:
            self.assertIn(skill, expanded)
        
        # Vérifier que des synonymes ont été ajoutés
        self.assertGreater(len(expanded), len(skills))
        self.assertIn("Django", expanded)  # Django est un framework Python
        self.assertIn("React", expanded)   # React est une bibliothèque JavaScript
    
    def test_calculate_skill_match(self):
        """Teste le calcul du score de correspondance des compétences"""
        # Calculer le score
        score = self.matcher.calculate_skill_match(self.candidate, self.job)
        
        # Vérifier que le score est dans la plage [0, 1]
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # Jean Dupont a 3/3 compétences requises pour le poste de Développeur Python Senior
        # On s'attend à un score élevé
        self.assertGreaterEqual(score, 0.7)
    
    def test_calculate_location_match(self):
        """Teste le calcul du score de correspondance de localisation"""
        # Mocker la fonction calculate_travel_time pour retourner une valeur connue
        with patch.object(SmartMatcher, 'calculate_travel_time', return_value=25):
            # Calculer le score
            score = self.matcher.calculate_location_match(self.candidate, self.job)
            
            # Vérifier que le score est dans la plage [0, 1]
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            
            # 25 minutes est un excellent temps de trajet, on s'attend à un score de 1.0
            self.assertEqual(score, 1.0)
    
    def test_calculate_experience_match(self):
        """Teste le calcul du score de correspondance d'expérience"""
        # Jean Dupont a 5 ans d'expérience, le job demande min 4 ans et max 8 ans
        score = self.matcher.calculate_experience_match(self.candidate, self.job)
        
        # On s'attend à un score parfait car il est dans la fourchette idéale
        self.assertEqual(score, 1.0)
        
        # Tester avec un candidat sous-qualifié
        under_qualified = self.candidate.copy()
        under_qualified["years_of_experience"] = 2
        score = self.matcher.calculate_experience_match(under_qualified, self.job)
        
        # On s'attend à un score inférieur à 0.5 car il est sous-qualifié
        self.assertLess(score, 0.5)
        
        # Tester avec un candidat surqualifié
        over_qualified = self.candidate.copy()
        over_qualified["years_of_experience"] = 15
        score = self.matcher.calculate_experience_match(over_qualified, self.job)
        
        # On s'attend à un score inférieur à 1.0 mais supérieur à 0.5
        self.assertLess(score, 1.0)
        self.assertGreater(score, 0.5)
    
    def test_calculate_education_match(self):
        """Teste le calcul du score de correspondance d'éducation"""
        # Jean Dupont a un master, le job demande une licence (bachelor)
        score = self.matcher.calculate_education_match(self.candidate, self.job)
        
        # On s'attend à un score élevé mais pas parfait car il est surqualifié
        self.assertLess(score, 1.0)
        self.assertGreater(score, 0.5)
        
        # Tester avec un candidat ayant exactement le niveau requis
        exact_match = self.candidate.copy()
        exact_match["education_level"] = "bachelor"
        score = self.matcher.calculate_education_match(exact_match, self.job)
        
        # On s'attend à un score parfait
        self.assertEqual(score, 1.0)
        
        # Tester avec un candidat sous-qualifié
        under_qualified = self.candidate.copy()
        under_qualified["education_level"] = "high_school"
        score = self.matcher.calculate_education_match(under_qualified, self.job)
        
        # On s'attend à un score faible
        self.assertLess(score, 0.5)
    
    def test_calculate_preference_match(self):
        """Teste le calcul du score de correspondance des préférences"""
        # Jean Dupont veut du remote, le job offre du remote
        score = self.matcher.calculate_preference_match(self.candidate, self.job)
        
        # Vérifier que le score est dans la plage [0, 1]
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        # On s'attend à un score élevé car les préférences correspondent
        self.assertGreaterEqual(score, 0.7)
        
        # Tester avec un mismatch de remote
        mismatch_job = self.job.copy()
        mismatch_job["offers_remote"] = False
        score = self.matcher.calculate_preference_match(self.candidate, mismatch_job)
        
        # On s'attend à un score plus faible
        self.assertLess(score, 0.7)
    
    def test_calculate_match(self):
        """Teste le calcul global du score de matching"""
        # Calculer le match
        match_result = self.matcher.calculate_match(self.candidate, self.job)
        
        # Vérifier la structure du résultat
        self.assertIn("overall_score", match_result)
        self.assertIn("category_scores", match_result)
        self.assertIn("insights", match_result)
        
        # Vérifier que le score global est dans la plage [0, 1]
        self.assertGreaterEqual(match_result["overall_score"], 0.0)
        self.assertLessEqual(match_result["overall_score"], 1.0)
        
        # Vérifier que les scores de catégorie sont présents
        categories = ["skills", "location", "experience", "education", "preferences"]
        for category in categories:
            self.assertIn(category, match_result["category_scores"])
    
    def test_generate_insights(self):
        """Teste la génération d'insights"""
        # Simuler des scores
        skill_score = 0.9
        location_score = 0.8
        experience_score = 1.0
        education_score = 0.7
        preference_score = 0.6
        
        # Générer les insights
        insights = self.matcher.generate_insights(
            self.candidate, self.job,
            skill_score, location_score, experience_score,
            education_score, preference_score
        )
        
        # Vérifier que des insights ont été générés
        self.assertGreater(len(insights), 0)
        
        # Vérifier la structure des insights
        for insight in insights:
            self.assertIn("type", insight)
            self.assertIn("message", insight)
            self.assertIn("score", insight)
            self.assertIn("category", insight)
    
    def test_batch_match(self):
        """Teste le matching par lots"""
        # Exécuter le batch matching
        results = self.matcher.batch_match(
            self.test_data["candidates"], 
            self.test_data["jobs"]
        )
        
        # Vérifier que le nombre de résultats est correct
        expected_count = len(self.test_data["candidates"]) * len(self.test_data["jobs"])
        self.assertEqual(len(results), expected_count)
        
        # Vérifier la structure des résultats
        for result in results:
            self.assertIn("overall_score", result)
            self.assertIn("category_scores", result)
            self.assertIn("insights", result)

if __name__ == "__main__":
    unittest.main()
