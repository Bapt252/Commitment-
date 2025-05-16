# -*- coding: utf-8 -*-
"""
Exemple d'utilisation de SmartMatch avec intégration des questionnaires
-----------------------------------------------------------------------
Ce script démontre comment utiliser SmartMatch avec les données des questionnaires
pour obtenir des résultats de matching pertinents et détaillés.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import json
import os
from pprint import pprint
from questionnaire_integration import process_questionnaires
from smartmatch_enhanced import SmartMatcherEnhanced

# Exemple de données de questionnaire candidat
CANDIDATE_QUESTIONNAIRE_DATA = {
    "full-name": "Jean Dupont",
    "job-title": "Développeur Full Stack",
    "address-lat": "48.8566",
    "address-lng": "2.3522",
    "office-preference": "open-space",
    "transport-method": ["public-transport", "bike"],
    "commute-time-public-transport": "45",
    "commute-time-bike": "30",
    "salary-range": "45K€ - 55K€",
    "has-sector-preference": "yes",
    "sector-preference": ["tech", "consulting"],
    "prohibited-sector": ["finance"],
    "motivation-order": "evolution,remuneration,flexibility,location,other",
    "availability": "1month",
    "currently-employed": "yes",
    "structure-type": ["startup", "pme"],
    "skills": ["JavaScript", "React", "Node.js", "Python", "Django"]
}

# Exemple de données de questionnaire client
CLIENT_QUESTIONNAIRE_DATA = {
    "company-name": "TechStartup SAS",
    "company-address": "123 Avenue de la République, 75011 Paris",
    "sector-list": "tech",
    "work-environment": "open-space",
    "experience-required": "5-10",
    "sector-knowledge": "no",
    "can-handle-notice": "yes",
    "notice-duration": "2months",
    "company-size": "startup"
}

# Exemple de données de fiche de poste
JOB_DATA = {
    "job-title-value": "Développeur Full Stack JavaScript",
    "job-contract-value": "CDI",
    "job-location-value": "Paris",
    "job-experience-value": "Au moins 3 ans d'expérience",
    "job-education-value": "Bac+5 ou équivalent",
    "job-salary-value": "Entre 50K€ et 65K€ selon expérience",
    "job-skills-value": "React, Node.js, Express, MongoDB, TypeScript, Git",
    "job-responsibilities-value": "Développer de nouvelles fonctionnalités, Travailler en équipe agile, Possibilité de télétravail 2 jours par semaine",
    "job-benefits-value": "Tickets restaurant, Mutuelle, RTT, Télétravail partiel"
}

def run_example():
    """
    Exécute l'exemple complet de matching avec les données des questionnaires
    """
    print("\n=== Exemple d'intégration des questionnaires avec SmartMatch ===\n")
    
    # Étape 1: Transformer les données des questionnaires
    print("1. Transformation des données des questionnaires...\n")
    candidate, job = process_questionnaires(CANDIDATE_QUESTIONNAIRE_DATA, JOB_DATA, CLIENT_QUESTIONNAIRE_DATA)
    
    print("Données du candidat transformées :")
    pprint(candidate)
    print("\nDonnées du poste transformées :")
    pprint(job)
    
    # Étape 2: Calculer le matching avec SmartMatcherEnhanced
    print("\n2. Calcul du matching avec SmartMatcherEnhanced...\n")
    
    # Initialiser le matcher (avec ou sans clé API Google Maps)
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    matcher = SmartMatcherEnhanced(api_key=api_key)
    
    # Calculer le match
    result = matcher.calculate_match(candidate, job)
    
    # Afficher les résultats
    print("Résultat du matching :")
    print(f"Score global: {result['overall_score']}")
    print("\nScores par catégorie:")
    for category, score in result["category_scores"].items():
        print(f"  - {category}: {score}")
    
    print("\nInsights générés:")
    for insight in result["insights"]:
        print(f"  - [{insight['category']}] {insight['message']}")
    
    # Étape 3: Démonstration de cas d'utilisation spécifiques
    print("\n3. Démonstration de cas d'utilisation spécifiques...\n")
    
    # Cas 1: Sector mismatch
    print("Cas 1: Secteur incompatible")
    test_job = job.copy()
    test_job["industry"] = "finance"  # Le candidat a indiqué que finance est un secteur rédhibitoire
    result1 = matcher.calculate_match(candidate, test_job)
    print(f"  Score global: {result1['overall_score']}")
    dealbreakers = [i for i in result1["insights"] if i.get("category") == "dealbreaker"]
    if dealbreakers:
        print(f"  Élément rédhibitoire détecté: {dealbreakers[0]['message']}")
    
    # Cas 2: Perfect match with all preferences
    print("\nCas 2: Correspondance parfaite sur toutes les préférences")
    perfect_job = job.copy()
    perfect_job["required_skills"] = ["JavaScript", "React", "Node.js", "Python", "Django"]
    perfect_job["offers_remote"] = True
    perfect_job["evolution_perspectives"] = "Évolution rapide vers un poste de lead developer puis CTO"
    perfect_job["benefits_description"] = "Horaires flexibles, RTT, Télétravail, Formation continue"
    result2 = matcher.calculate_match(candidate, perfect_job)
    print(f"  Score global: {result2['overall_score']}")
    strengths = [i for i in result2["insights"] if i.get("category") == "strength"]
    print(f"  Nombre de points forts: {len(strengths)}")
    print(f"  Exemple: {strengths[0]['message']}")
    
    # Étape 4: Conclusion
    print("\n4. Conclusion")
    print("L'intégration des questionnaires avec SmartMatch permet une analyse plus précise")
    print("des préférences et des contraintes, pour des matchings plus pertinents.")

if __name__ == "__main__":
    run_example()