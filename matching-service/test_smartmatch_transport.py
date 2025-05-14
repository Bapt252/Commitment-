#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour le système SmartMatch avec l'extension de transport.

Ce script permet de tester l'intégration du client Google Maps et 
des fonctionnalités avancées de matching géographique.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ajouter le répertoire du projet au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des modules du projet
try:
    from app.smartmatch import SmartMatcher
    from app.google_maps_client import GoogleMapsClient
    from app.smartmatch_transport import CommuteMatchExtension, enhance_smartmatch_with_transport
    logger.info("Modules importés avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules: {e}")
    sys.exit(1)

class TestSmartMatchTransport(unittest.TestCase):
    """
    Tests unitaires pour les fonctionnalités de transport de SmartMatch.
    """
    
    def setUp(self):
        """Prépare les tests en chargeant les données de test."""
        self.candidates = self._load_json('test_data/candidates.json')
        self.companies = self._load_json('test_data/companies.json')
        
        # Initialiser le client Google Maps avec un mode mock si pas de clé API
        api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        self.maps_client = GoogleMapsClient(api_key=api_key)
        
        # Initialiser le SmartMatcher
        self.matcher = SmartMatcher()
        
        # Améliorer avec l'extension de transport
        self.enhanced_matcher = enhance_smartmatch_with_transport(self.matcher, api_key=api_key)
    
    def _load_json(self, file_path):
        """Charge des données JSON depuis un fichier."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement de {file_path}: {e}")
            return []
    
    def test_google_maps_client(self):
        """Teste le client Google Maps."""
        origin = "Paris, France"
        destination = "Lyon, France"
        
        # Tester les différents modes de transport
        travel_times = {}
        for mode in ['driving', 'transit', 'walking', 'bicycling']:
            time = self.maps_client.get_travel_time(origin, destination, mode=mode)
            travel_times[mode] = time
            logger.info(f"Temps de trajet en {mode}: {time} minutes")
        
        # Vérifier au moins un mode valide
        valid_times = [time for time in travel_times.values() if time > 0]
        self.assertTrue(len(valid_times) > 0, "Au moins un mode de transport devrait être valide")
    
    def test_commute_match_extension(self):
        """Teste l'extension CommuteMatch."""
        extension = CommuteMatchExtension()
        
        # Tester le calcul du score de trajet
        candidate = self.candidates[0]  # Jean Dupont à Paris
        company = self.companies[0]     # TechSolutions à Paris
        
        score = extension.calculate_commute_score(candidate, company)
        logger.info(f"Score de trajet: {score['score']}")
        logger.info(f"Détails: {score['details']}")
        
        # Vérifier que le score est dans l'intervalle [0, 1]
        self.assertTrue(0 <= score['score'] <= 1, "Le score doit être entre 0 et 1")
        
        # Tester l'analyse de compatibilité
        analysis = extension.analyze_transport_compatibility(candidate, company)
        logger.info(f"Analyse de compatibilité: {analysis}")
        
        # Vérifier que l'analyse contient les champs attendus
        self.assertIn('commute_score', analysis)
        self.assertIn('accessibility_score', analysis)
        self.assertIn('remote_match', analysis)
        self.assertIn('transport_match', analysis)
    
    def test_enhanced_matcher_location_score(self):
        """Teste le calcul amélioré du score de localisation."""
        candidate = self.candidates[0]  # Jean Dupont à Paris
        company = self.companies[0]     # TechSolutions à Paris
        
        # Calculer le score
        location_score = self.enhanced_matcher.calculate_location_score(candidate, company)
        logger.info(f"Score de localisation amélioré: {location_score}")
        
        # Vérifier que le score est dans l'intervalle [0, 1]
        self.assertTrue(0 <= location_score <= 1, "Le score doit être entre 0 et 1")
    
    def test_matching_with_transport(self):
        """Teste le matching complet avec les critères de transport."""
        # Exécuter le matching
        matches = self.enhanced_matcher.match(self.candidates, self.companies)
        
        # Vérifier qu'il y a des résultats
        self.assertTrue(len(matches) > 0, "Le matching devrait produire des résultats")
        
        # Afficher les meilleurs matchings
        logger.info("Top 3 des meilleurs matchings:")
        for i, match in enumerate(matches[:3]):
            logger.info(f"{i+1}. Candidat {match['candidate_id']} - "
                       f"Entreprise {match['company_id']} - "
                       f"Score: {match['score']:.2f}")
        
        # Vérifier la génération d'insights de trajet
        insights = self.enhanced_matcher.generate_insights(matches)
        
        # Filtrer les insights de type commute
        commute_insights = [insight for insight in insights if insight.get('type') in ['commute', 'transport_mode']]
        
        # Afficher les insights de trajet
        logger.info("Insights de trajet:")
        for insight in commute_insights:
            logger.info(f"[{insight['type']}] {insight['message']}")
        
        # Vérifier qu'il y a au moins un insight de trajet
        self.assertTrue(len(commute_insights) > 0, "Il devrait y avoir au moins un insight de trajet")
    
    @patch('app.google_maps_client.GoogleMapsClient.get_travel_time')
    def test_with_mocked_maps_api(self, mock_get_travel_time):
        """Teste le système avec une API Maps simulée."""
        # Configurer le mock pour simuler différents temps de trajet
        def side_effect(origin, destination, mode='driving'):
            # Paris -> Paris : court trajet
            if 'Paris' in origin and 'Paris' in destination:
                return {'driving': 15, 'transit': 25, 'walking': 45, 'bicycling': 20}.get(mode, 30)
            
            # Lyon -> Lyon : court trajet
            elif 'Lyon' in origin and 'Lyon' in destination:
                return {'driving': 20, 'transit': 30, 'walking': 50, 'bicycling': 25}.get(mode, 35)
            
            # Paris -> Lyon : long trajet
            elif 'Paris' in origin and 'Lyon' in destination:
                return {'driving': 240, 'transit': 120, 'walking': -1, 'bicycling': -1}.get(mode, -1)
            
            # Lyon -> Paris : long trajet
            elif 'Lyon' in origin and 'Paris' in destination:
                return {'driving': 240, 'transit': 120, 'walking': -1, 'bicycling': -1}.get(mode, -1)
            
            # Par défaut : trajet moyen
            else:
                return {'driving': 60, 'transit': 90, 'walking': 120, 'bicycling': 45}.get(mode, 60)
        
        mock_get_travel_time.side_effect = side_effect
        
        # Tester le matching avec l'API simulée
        extension = CommuteMatchExtension()
        
        # Tester différentes combinaisons de candidats et entreprises
        test_cases = [
            (self.candidates[0], self.companies[0], "Même ville"),        # Paris -> Paris
            (self.candidates[1], self.companies[3], "Même ville"),        # Lyon -> Lyon
            (self.candidates[0], self.companies[3], "Villes différentes") # Paris -> Lyon
        ]
        
        for candidate, company, description in test_cases:
            score = extension.calculate_commute_score(candidate, company)
            logger.info(f"Score de trajet ({description}): {score['score']}")
            logger.info(f"Détails: {score['details']}")
            
            # Vérifier que le score est dans l'intervalle [0, 1]
            self.assertTrue(0 <= score['score'] <= 1, "Le score doit être entre 0 et 1")

def run_tests():
    """Exécute les tests unitaires."""
    logger.info("=== TESTS DU SYSTÈME SMARTMATCH AVEC EXTENSION DE TRANSPORT ===")
    
    # Charger la variable d'environnement GOOGLE_MAPS_API_KEY depuis .env si présent
    try:
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('GOOGLE_MAPS_API_KEY='):
                        key = line.strip().split('=', 1)[1].strip('"\'')
                        os.environ['GOOGLE_MAPS_API_KEY'] = key
                        logger.info("Clé API Google Maps chargée depuis .env")
                        break
    except Exception as e:
        logger.warning(f"Erreur lors du chargement du fichier .env: {e}")
    
    # Exécuter les tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    logger.info("=== FIN DES TESTS ===")

if __name__ == "__main__":
    run_tests()
