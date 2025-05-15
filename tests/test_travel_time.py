#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests unitaires pour le calcul des temps de trajet."""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Ajouter le répertoire parent au path pour pouvoir importer les modules du projet
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import des modules à tester
from app.compat import GoogleMapsClient

class TravelTimeTests(unittest.TestCase):
    """Tests pour le calcul des temps de trajet."""
    
    def setUp(self):
        """Initialisation des tests."""
        # Créer un mock pour la clé API Google Maps
        self.api_key = "fake_api_key"
        
        # Initialiser le client avec la clé mock
        with patch.dict('os.environ', {'GOOGLE_MAPS_API_KEY': self.api_key}):
            self.client = GoogleMapsClient()
    
    @patch('requests.get')
    def test_get_travel_time_success(self, mock_get):
        """Test du calcul du temps de trajet avec succès."""
        # Configurer le mock pour simuler une réponse réussie de l'API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "rows": [{
                "elements": [{
                    "status": "OK",
                    "duration": {"value": 1800},  # 30 minutes en secondes
                    "distance": {"value": 15000}  # 15 km en mètres
                }]
            }]
        }
        mock_get.return_value = mock_response
        
        # Appeler la méthode à tester
        origin = "75001 Paris, France"
        destination = "92100 Boulogne-Billancourt, France"
        travel_time = self.client.get_travel_time(origin, destination)
        
        # Vérifier les résultats
        self.assertEqual(travel_time, 30)  # 30 minutes
        mock_get.assert_called_once()
        
        # Vérifier que les bons paramètres ont été utilisés
        args, kwargs = mock_get.call_args
        self.assertIn("origins=75001+Paris%2C+France", kwargs.get("params", {}).values())
        self.assertIn("destinations=92100+Boulogne-Billancourt%2C+France", kwargs.get("params", {}).values())
    
    @patch('requests.get')
    def test_get_travel_time_api_error(self, mock_get):
        """Test du calcul du temps de trajet avec une erreur API."""
        # Configurer le mock pour simuler une erreur de l'API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ZERO_RESULTS"}
        mock_get.return_value = mock_response
        
        # Appeler la méthode à tester
        origin = "75001 Paris, France"
        destination = "New York, USA"  # Destination trop éloignée
        travel_time = self.client.get_travel_time(origin, destination)
        
        # Vérifier les résultats
        self.assertEqual(travel_time, -1)  # Code d'erreur
    
    @patch('requests.get')
    def test_get_travel_time_http_error(self, mock_get):
        """Test du calcul du temps de trajet avec une erreur HTTP."""
        # Configurer le mock pour simuler une erreur HTTP
        mock_response = MagicMock()
        mock_response.status_code = 400  # Bad Request
        mock_get.return_value = mock_response
        
        # Appeler la méthode à tester
        origin = "75001 Paris, France"
        destination = "92100 Boulogne-Billancourt, France"
        travel_time = self.client.get_travel_time(origin, destination)
        
        # Vérifier les résultats
        self.assertEqual(travel_time, -1)  # Code d'erreur
    
    @patch('requests.get')
    def test_get_travel_time_exception(self, mock_get):
        """Test du calcul du temps de trajet avec une exception."""
        # Configurer le mock pour lever une exception
        mock_get.side_effect = Exception("Test exception")
        
        # Appeler la méthode à tester
        origin = "75001 Paris, France"
        destination = "92100 Boulogne-Billancourt, France"
        travel_time = self.client.get_travel_time(origin, destination)
        
        # Vérifier les résultats
        self.assertEqual(travel_time, -1)  # Code d'erreur
    
    def test_get_travel_time_missing_api_key(self):
        """Test du calcul du temps de trajet sans clé API."""
        # Créer un client sans clé API
        client = GoogleMapsClient(api_key=None)
        
        # Appeler la méthode à tester
        origin = "75001 Paris, France"
        destination = "92100 Boulogne-Billancourt, France"
        travel_time = client.get_travel_time(origin, destination)
        
        # Vérifier les résultats
        self.assertEqual(travel_time, -1)  # Code d'erreur
    
    @patch('requests.get')
    def test_travel_time_cache(self, mock_get):
        """Test du cache des temps de trajet."""
        # Configurer le mock pour simuler une réponse réussie de l'API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "rows": [{
                "elements": [{
                    "status": "OK",
                    "duration": {"value": 1800},  # 30 minutes en secondes
                    "distance": {"value": 15000}  # 15 km en mètres
                }]
            }]
        }
        mock_get.return_value = mock_response
        
        # Appeler la méthode à tester deux fois avec les mêmes paramètres
        origin = "75001 Paris, France"
        destination = "92100 Boulogne-Billancourt, France"
        travel_time1 = self.client.get_travel_time(origin, destination)
        travel_time2 = self.client.get_travel_time(origin, destination)
        
        # Vérifier les résultats
        self.assertEqual(travel_time1, 30)  # 30 minutes
        self.assertEqual(travel_time2, 30)  # 30 minutes
        mock_get.assert_called_once()  # L'API devrait être appelée une seule fois

if __name__ == "__main__":
    unittest.main()
