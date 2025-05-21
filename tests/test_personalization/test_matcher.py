"""
Tests unitaires pour le module matcher de personnalisation.
"""

import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from user_personalization.matcher import PersonalizedMatcher
from user_personalization.weights import UserWeights

class TestPersonalizedMatcher(unittest.TestCase):
    
    def setUp(self):
        # Créer un mock pour la connexion à la base de données
        self.db_mock = MagicMock()
        
        # Créer des mocks pour les modules
        self.weight_manager_mock = MagicMock()
        self.collaborative_filter_mock = MagicMock()
        self.cold_start_mock = MagicMock()
        self.temporal_mock = MagicMock()
        self.ab_test_manager_mock = MagicMock()
        
        # Créer l'objet à tester avec les mocks
        with patch('user_personalization.matcher.WeightManager', return_value=self.weight_manager_mock), \
             patch('user_personalization.matcher.CollaborativeFilter', return_value=self.collaborative_filter_mock), \
             patch('user_personalization.matcher.ColdStartStrategy', return_value=self.cold_start_mock), \
             patch('user_personalization.matcher.TemporalAdjustment', return_value=self.temporal_mock), \
             patch('user_personalization.matcher.ABTestManager', return_value=self.ab_test_manager_mock):
            self.matcher = PersonalizedMatcher(self.db_mock)
    
    def test_get_personalized_matches_cold_start(self):
        # Configurer les mocks pour un utilisateur cold start
        user_id = 123
        base_candidates = [
            {"id": 1, "name": "Candidate 1"},
            {"id": 2, "name": "Candidate 2"}
        ]
        expected_matches = [
            {"id": 2, "name": "Candidate 2"},
            {"id": 1, "name": "Candidate 1"}
        ]
        
        self.cold_start_mock.is_cold_start_user.return_value = True
        self.cold_start_mock.get_recommendations.return_value = expected_matches
        
        # Appeler la méthode à tester
        result = self.matcher.get_personalized_matches(user_id, base_candidates)
        
        # Vérifier le résultat
        self.assertEqual(result, expected_matches)
        self.cold_start_mock.is_cold_start_user.assert_called_once_with(user_id)
        self.cold_start_mock.get_recommendations.assert_called_once_with(user_id, base_candidates, 10)
    
    def test_get_personalized_matches_with_weights(self):
        # Configurer les mocks pour un utilisateur avec des poids
        user_id = 456
        base_candidates = [
            {"id": 1, "name": "Candidate 1", "age": 30, "category": "premium"},
            {"id": 2, "name": "Candidate 2", "age": 25, "category": "new_user"}
        ]
        
        # Mock pour les poids utilisateur
        user_weights = UserWeights(
            attribute_weights={"age": 0.5},
            category_modifiers={"premium": 1.2, "new_user": 1.1}
        )
        self.weight_manager_mock.get_user_weights.return_value = user_weights
        
        # Mock pour les scores collaboratifs
        collab_scores = {1: 0.8, 2: 0.6}
        self.collaborative_filter_mock.get_candidate_scores.return_value = collab_scores
        
        # Mock pour les scores temporels
        temporal_scores = {1: 0.7, 2: 0.9}
        self.temporal_mock.adjust_scores.return_value = temporal_scores
        
        # Mock pour le test A/B
        self.ab_test_manager_mock.get_user_variant.return_value = None
        
        # Mock pour cold start
        self.cold_start_mock.is_cold_start_user.return_value = False
        
        # Appeler la méthode à tester
        result = self.matcher.get_personalized_matches(user_id, base_candidates)
        
        # Vérifier que le résultat contient les candidats avec des scores
        self.assertEqual(len(result), 2)
        self.assertTrue("personalized_score" in result[0])
        self.assertTrue("personalized_score" in result[1])
        
        # Le résultat doit être trié par score
        self.assertTrue(result[0]["personalized_score"] >= result[1]["personalized_score"])
    
    def test_update_feedback(self):
        # Configurer les paramètres pour le test
        user_id = 789
        candidate_id = 101
        feedback_type = "like"
        feedback_value = True
        
        # Appeler la méthode à tester
        result = self.matcher.update_feedback(user_id, candidate_id, feedback_type, feedback_value)
        
        # Vérifier que le résultat est correct
        self.assertTrue(result)
        
        # Vérifier que tous les modules ont été appelés pour mettre à jour le feedback
        self.weight_manager_mock.update_from_feedback.assert_called_once_with(
            user_id, candidate_id, feedback_type, feedback_value)
        self.collaborative_filter_mock.update_from_feedback.assert_called_once_with(
            user_id, candidate_id, feedback_type, feedback_value)
        self.temporal_mock.record_interaction.assert_called_once_with(
            user_id, candidate_id, feedback_type, feedback_value)
        self.ab_test_manager_mock.record_metric.assert_called_once_with(
            user_id, feedback_type, feedback_value)

if __name__ == '__main__':
    unittest.main()
