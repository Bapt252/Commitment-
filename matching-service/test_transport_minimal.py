#!/usr/bin/env python3
import os
import logging
import json
from typing import Dict, List, Any

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Charger la clé API depuis .env s'il existe
try:
    with open('.env', 'r') as env_file:
        for line in env_file:
            if line.strip().startswith('GOOGLE_MAPS_API_KEY='):
                key = line.strip().split('=', 1)[1].strip('"\'')
                os.environ['GOOGLE_MAPS_API_KEY'] = key
                logger.info("Clé API Google Maps chargée depuis .env")
                break
except Exception as e:
    logger.warning(f"Impossible de charger .env: {e}")

# Charger les données de test
def load_test_data(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de {file_path}: {e}")
        return []

# Test du client Google Maps
class MockSmartMatcher:
    def __init__(self):
        self.matching_details = {}
        logger.info("Mock SmartMatcher créé")
    
    def calculate_location_score(self, candidate, company):
        logger.info(f"Calcul du score de localisation pour {candidate.get('name', 'Candidat')} et {company.get('name', 'Entreprise')}")
        return 0.75

def main():
    logger.info("=== TEST MINIMAL DU MODULE DE TRANSPORT ===")
    
    # Charger les données de test
    candidates = load_test_data('test_data/candidates.json')
    companies = load_test_data('test_data/companies.json')
    
    if not candidates or not companies:
        logger.warning("Données de test manquantes, création de données factices")
        candidates = [{
            "id": "cand001",
            "name": "Jean Dupont",
            "location": "Paris, France",
            "preferred_commute_time": 45,
            "preferred_transport_mode": "driving"
        }]
        companies = [{
            "id": "comp001",
            "name": "TechSolutions",
            "location": "Paris, France",
            "transit_friendly": True
        }]
    
    # Vérifier si le client Google Maps peut être importé
    try:
        from app.google_maps_client import GoogleMapsClient
        logger.info("✅ Import du client Google Maps réussi")
        
        # Créer une instance du client
        api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
        maps_client = GoogleMapsClient(api_key=api_key)
        logger.info("✅ Client Google Maps initialisé")
        
        # Tester une estimation de temps de trajet
        origin = "Paris, France"
        destination = "Lyon, France"
        time = maps_client._estimate_travel_time(origin, destination)
        logger.info(f"Temps de trajet estimé entre {origin} et {destination}: {time} minutes")
        
    except ImportError as e:
        logger.error(f"❌ Erreur lors de l'import du client Google Maps: {e}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'utilisation du client Google Maps: {e}")
    
    # Vérifier si l'extension de transport peut être importée
    try:
        from app.smartmatch_transport import CommuteMatchExtension
        logger.info("✅ Import de l'extension de transport réussi")
        
        # Créer un mock de SmartMatcher
        mock_matcher = MockSmartMatcher()
        logger.info("✅ Mock SmartMatcher créé")
        
        # Tester l'extension de transport
        candidate = candidates[0]
        company = companies[0]
        
        # Créer l'extension
        extension = CommuteMatchExtension(api_key)
        logger.info("✅ Extension CommuteMatch créée")
        
        # Calculer un score
        score = extension.calculate_commute_score(candidate, company)
        logger.info(f"Score de trajet: {score['score']}")
        logger.info(f"Détails: {score['details']}")
        
        # Tester l'analyse de compatibilité
        analysis = extension.analyze_transport_compatibility(candidate, company)
        logger.info(f"Analyse de compatibilité: {analysis}")
        
        logger.info("✅ Test de l'extension réussi")
        
    except ImportError as e:
        logger.error(f"❌ Erreur lors de l'import de l'extension de transport: {e}")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'utilisation de l'extension de transport: {e}")
    
    logger.info("=== TEST TERMINÉ ===")

if __name__ == "__main__":
    main()