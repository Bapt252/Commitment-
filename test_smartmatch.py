#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script de test pour le système Nexten SmartMatch.
Ce script vérifie tous les composants du système de matching bidirectionnel.
"""

import os
import sys
import json
import logging
import pandas as pd
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SmartMatch-Test")

# Ajout du répertoire du projet au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des modules du projet
try:
    from app.smartmatch import SmartMatchEngine
    from app.compat import GoogleMapsClient
    from app.semantic_analysis import SemanticAnalyzer
    from app.data_loader import DataLoader
    from app.insight_generator import InsightGenerator
    logger.info("Tous les modules ont été importés avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules: {e}")
    sys.exit(1)

def load_test_data():
    """
    Charge les données de test depuis les fichiers JSON ou CSV
    """
    logger.info("Chargement des données de test...")
    try:
        data_loader = DataLoader()
        
        # Charger les données des candidats
        candidates = data_loader.load_candidates("./test_data/candidates.json")
        logger.info(f"Nombre de candidats chargés: {len(candidates)}")
        
        # Charger les données des entreprises
        companies = data_loader.load_companies("./test_data/companies.json")
        logger.info(f"Nombre d'entreprises chargées: {len(companies)}")
        
        return candidates, companies
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données de test: {e}")
        # Créer des données de test minimales si le chargement échoue
        logger.info("Création de données de test minimales...")
        
        candidates = [
            {
                "id": "cand1",
                "name": "Jean Dupont",
                "skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
                "experience": 3,
                "location": "Paris, France",
                "remote_preference": "hybrid",
                "salary_expectation": 60000
            },
            {
                "id": "cand2",
                "name": "Marie Martin",
                "skills": ["Java", "Spring", "Hibernate", "SQL", "Git"],
                "experience": 5,
                "location": "Lyon, France",
                "remote_preference": "full",
                "salary_expectation": 70000
            }
        ]
        
        companies = [
            {
                "id": "comp1",
                "name": "TechSolutions",
                "required_skills": ["Python", "JavaScript", "React"],
                "location": "Paris, France",
                "remote_policy": "hybrid",
                "salary_range": {"min": 50000, "max": 75000}
            },
            {
                "id": "comp2",
                "name": "DataInnovate",
                "required_skills": ["Java", "SQL", "Big Data"],
                "location": "Marseille, France",
                "remote_policy": "office_only",
                "salary_range": {"min": 60000, "max": 85000}
            }
        ]
        
        return candidates, companies

def test_google_maps_api():
    """
    Teste la connexion à l'API Google Maps et le calcul des temps de trajet
    """
    logger.info("Test de l'API Google Maps...")
    try:
        maps_client = GoogleMapsClient()
        origin = "Paris, France"
        destination = "Versailles, France"
        
        travel_time = maps_client.get_travel_time(origin, destination)
        logger.info(f"Temps de trajet de {origin} à {destination}: {travel_time} minutes")
        
        if travel_time > 0:
            logger.info("✅ Test de l'API Google Maps réussi")
            return True
        else:
            logger.warning("⚠️ Le temps de trajet calculé est de 0 minute, vérifiez les données")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur lors du test de l'API Google Maps: {e}")
        return False

def test_semantic_analysis():
    """
    Teste l'analyseur sémantique des compétences
    """
    logger.info("Test de l'analyseur sémantique...")
    try:
        analyzer = SemanticAnalyzer()
        
        skills1 = ["Python", "Django", "Flask"]
        skills2 = ["Python", "Web Development", "API Design"]
        
        similarity = analyzer.calculate_similarity(skills1, skills2)
        logger.info(f"Similarité entre {skills1} et {skills2}: {similarity}")
        
        if 0 <= similarity <= 1:
            logger.info("✅ Test de l'analyseur sémantique réussi")
            return True
        else:
            logger.warning(f"⚠️ La similarité calculée ({similarity}) n'est pas dans l'intervalle [0,1]")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur lors du test de l'analyseur sémantique: {e}")
        return False

def test_matching_engine(candidates, companies):
    """
    Teste le moteur de matching
    """
    logger.info("Test du moteur de matching...")
    try:
        engine = SmartMatchEngine()
        
        # Configuration des poids
        weights = {
            "skills": 0.4,
            "location": 0.3,
            "experience": 0.15,
            "remote_policy": 0.1,
            "salary": 0.05
        }
        engine.set_weights(weights)
        
        # Exécution du matching
        matching_results = engine.match(candidates, companies)
        
        if matching_results and len(matching_results) > 0:
            # Afficher quelques résultats
            for i, result in enumerate(matching_results[:2]):
                logger.info(f"Match {i+1}: Candidat {result['candidate_id']} - Entreprise {result['company_id']} - Score: {result['score']}")
            
            logger.info("✅ Test du moteur de matching réussi")
            return True, matching_results
        else:
            logger.warning("⚠️ Aucun résultat de matching trouvé")
            return False, None
    except Exception as e:
        logger.error(f"❌ Erreur lors du test du moteur de matching: {e}")
        return False, None

def test_insight_generator(matching_results):
    """
    Teste le générateur d'insights
    """
    if not matching_results:
        logger.warning("⚠️ Pas de résultats de matching pour générer des insights")
        return False
    
    logger.info("Test du générateur d'insights...")
    try:
        insight_gen = InsightGenerator()
        insights = insight_gen.generate_insights(matching_results)
        
        if insights and len(insights) > 0:
            logger.info(f"Nombre d'insights générés: {len(insights)}")
            logger.info(f"Exemple d'insight: {insights[0]}")
            logger.info("✅ Test du générateur d'insights réussi")
            return True
        else:
            logger.warning("⚠️ Aucun insight généré")
            return False
    except Exception as e:
        logger.error(f"❌ Erreur lors du test du générateur d'insights: {e}")
        return False

def export_results(matching_results):
    """
    Exporte les résultats de matching au format JSON et CSV
    """
    if not matching_results:
        logger.warning("⚠️ Pas de résultats à exporter")
        return
    
    try:
        # Timestamp pour le nom de fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export JSON
        json_file = f"./test_results/matching_results_{timestamp}.json"
        os.makedirs(os.path.dirname(json_file), exist_ok=True)
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(matching_results, f, ensure_ascii=False, indent=2)
        
        # Export CSV
        csv_file = f"./test_results/matching_results_{timestamp}.csv"
        df = pd.DataFrame(matching_results)
        df.to_csv(csv_file, index=False)
        
        logger.info(f"Résultats exportés en JSON: {json_file}")
        logger.info(f"Résultats exportés en CSV: {csv_file}")
    except Exception as e:
        logger.error(f"Erreur lors de l'export des résultats: {e}")

def run_all_tests():
    """
    Exécute tous les tests en séquence
    """
    logger.info("=== DÉMARRAGE DES TESTS DU SYSTÈME NEXTEN SMARTMATCH ===")
    
    test_summary = {
        "google_maps": False,
        "semantic_analysis": False,
        "matching_engine": False,
        "insight_generator": False
    }
    
    # 1. Charger les données de test
    candidates, companies = load_test_data()
    
    # 2. Tester l'API Google Maps
    test_summary["google_maps"] = test_google_maps_api()
    
    # 3. Tester l'analyseur sémantique
    test_summary["semantic_analysis"] = test_semantic_analysis()
    
    # 4. Tester le moteur de matching
    success, matching_results = test_matching_engine(candidates, companies)
    test_summary["matching_engine"] = success
    
    # 5. Tester le générateur d'insights
    if matching_results:
        test_summary["insight_generator"] = test_insight_generator(matching_results)
    
    # 6. Exporter les résultats
    if matching_results:
        export_results(matching_results)
    
    # Afficher le résumé des tests
    logger.info("=== RÉSUMÉ DES TESTS ===")
    for test_name, success in test_summary.items():
        status = "✅ RÉUSSI" if success else "❌ ÉCHOUÉ"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(test_summary.values())
    if all_passed:
        logger.info("✅✅✅ TOUS LES TESTS ONT RÉUSSI")
    else:
        logger.warning("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
    
    return all_passed, test_summary

if __name__ == "__main__":
    success, summary = run_all_tests()
    sys.exit(0 if success else 1)