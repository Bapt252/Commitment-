"""
Tests unitaires pour l'API REST de personnalisation.
"""

import unittest
import json
from unittest.mock import MagicMock, patch
import sys
import os

# Ajouter le répertoire parent au chemin Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from user_personalization.api import app

class TestPersonalizationAPI(unittest.TestCase):
    
    def setUp(self):
        # Configurer le client de test Flask
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Mock pour PersonalizedMatcher
        self.matcher_mock = MagicMock()
        
        # Patch pour les fonctions de connexion à la base de données et d'obtention du matcher
        self.db_patch = patch('user_personalization.api.get_db')
        self.matcher_patch = patch('user_personalization.api.get_matcher', return_value=self.matcher_mock)
        
        # Démarrer les patches
        self.db_mock = self.db_patch.start()
        self.get_matcher_mock = self.matcher_patch.start()
        
        # Mock pour _get_base_candidates
        self.get_candidates_patch = patch('user_personalization.api._get_base_candidates')
        self.get_candidates_mock = self.get_candidates_patch.start()
    
    def tearDown(self):
        # Arrêter les patches
        self.db_patch.stop()
        self.matcher_patch.stop()
        self.get_candidates_patch.stop()
    
    def test_get_personalized_matches(self):
        # Configurer les mocks
        user_id = 123
        base_candidates = [
            {"id": 1, "name": "Candidate 1"},
            {"id": 2, "name": "Candidate 2"}
        ]
        expected_matches = [
            {"id": 2, "name": "Candidate 2", "personalized_score": 0.85},
            {"id": 1, "name": "Candidate 1", "personalized_score": 0.75}
        ]
        
        self.get_candidates_mock.return_value = base_candidates
        self.matcher_mock.get_personalized_matches.return_value = expected_matches
        
        # Faire la requête à l'API
        response = self.client.get(f'/api/personalization/matches/{user_id}?limit=10')
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('matches', data)
        self.assertEqual(data['matches'], expected_matches)
        
        # Vérifier que les mocks ont été appelés correctement
        self.get_candidates_mock.assert_called_once_with(user_id, 20)
        self.matcher_mock.get_personalized_matches.assert_called_once()
    
    def test_record_feedback(self):
        # Configurer les données de la requête
        feedback_data = {
            'user_id': 456,
            'candidate_id': 789,
            'feedback_type': 'match',
            'feedback_value': True
        }
        
        self.matcher_mock.update_feedback.return_value = True
        
        # Faire la requête à l'API
        response = self.client.post(
            '/api/personalization/feedback',
            data=json.dumps(feedback_data),
            content_type='application/json'
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        
        # Vérifier que le mock a été appelé correctement
        self.matcher_mock.update_feedback.assert_called_once_with(
            feedback_data['user_id'],
            feedback_data['candidate_id'],
            feedback_data['feedback_type'],
            feedback_data['feedback_value']
        )

if __name__ == '__main__':
    unittest.main()
