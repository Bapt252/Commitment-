#!/usr/bin/env python3
"""
Exemple d'utilisation de l'intégration SmartMatch avec les questionnaires
------------------------------------------------------------------------
Ce script démontre comment utiliser le module questionnaire_connector.py
pour intégrer les questionnaires à l'algorithme SmartMatch.
"""

import json
import os
from pathlib import Path
from questionnaire_connector import SmartMatchIntegration

# Chemin vers les fichiers d'exemple (à adapter selon votre environnement)
EXAMPLES_DIR = Path(__file__).parent / "examples"

def load_example_data(filename):
    """Charge des données JSON d'exemple"""
    try:
        filepath = EXAMPLES_DIR / filename
        if not filepath.exists():
            print(f"Fichier {filename} non trouvé dans {EXAMPLES_DIR}")
            return {}
            
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erreur lors du chargement de {filename}: {str(e)}")
        return {}

def main():
    """Fonction principale"""
    print("=== DÉMONSTRATION DE L'INTÉGRATION SMARTMATCH AVEC LES QUESTIONNAIRES ===\n")
    
    # Initialiser le système d'intégration
    # Dans un environnement réel, utilisez votre clé API Google Maps
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    integration = SmartMatchIntegration(api_key=api_key)
    
    print("1. Chargement des données d'exemple...")
    
    # Charger les données CV et questionnaire candidat
    cv_data = load_example_data("example_cv.json")
    candidate_questionnaire = load_example_data("example_candidate_questionnaire.json")
    
    if not cv_data or not candidate_questionnaire:
        print("Impossible de charger les données candidat. Utilisation de données fictives.")
        cv_data = {
            "nom": "Dupont",
            "prenom": "Jean",
            "poste": "Développeur Python Senior",
            "competences": ["Python", "Django", "Flask", "REST API"],
            "logiciels": ["Git", "Docker", "VS Code", "PyCharm"],
            "email": "jean.dupont@example.com",
            "telephone": "06 12 34 56 78",
            "adresse": "123 rue de Paris, 75001 Paris"
        }
        
        candidate_questionnaire = {
            "transport-method": ["public-transport", "vehicle"],
            "commute-time-public-transport": "45",
            "commute-time-vehicle": "30",
            "address": "123 rue de Paris, 75001 Paris",
            "office-preference": "open-space",
            "motivation-order": "remuneration,evolution,flexibility",
            "structure-type": ["pme", "startup"],
            "has-sector-preference": "yes",
            "sector-preference": ["tech", "finance"],
            "salary-range": "45K - 55K",
            "availability": "1month",
            "currently-employed": "yes",
            "notice-period": "1month",
            "notice-negotiable": "yes"
        }
    
    # Charger les données offre d'emploi et questionnaire client
    job_data = load_example_data("example_job.json")
    client_questionnaire = load_example_data("example_client_questionnaire.json")
    
    if not job_data or not client_questionnaire:
        print("Impossible de charger les données entreprise. Utilisation de données fictives.")
        job_data = {
            "title": "Développeur Python Senior",
            "company": "Acme Inc.",
            "location": "Paris",
            "contract_type": "CDI",
            "skills": ["Python", "Django", "Flask", "SQL", "Git", "Docker"],
            "experience": "5 ans d'expérience en développement Python",
            "education": "Diplôme d'ingénieur ou équivalent",
            "salary": "45K - 55K",
            "responsibilities": [
                "Développer des applications web avec Django",
                "Maintenir les API REST existantes",
                "Participer à la conception technique"
            ],
            "benefits": [
                "Télétravail partiel",
                "Mutuelle d'entreprise",
                "Tickets restaurant"
            ]
        }
        
        client_questionnaire = {
            "company-name": "Acme Inc.",
            "company-address": "45 avenue de la République, 75011 Paris",
            "company-size": "pme",
            "recruitment-delay": "1month",
            "can-handle-notice": "yes",
            "notice-duration": "2months",
            "work-environment": "open-space",
            "remote-work": "yes",
            "evolution-perspectives": "Possibilité d'évolution vers un poste de Lead Developer.",
            "benefits": "Télétravail 2j/sem, RTT, Tickets restaurant, Mutuelle"
        }
    
    print("2. Traitement des données candidat...")
    candidate_smartmatch = integration.process_candidate_submission(cv_data, candidate_questionnaire)
    
    print("3. Traitement des données offre d'emploi...")
    job_smartmatch = integration.process_job_submission(job_data, client_questionnaire)
    
    print("4. Calcul du matching...")
    
    # Utiliser enhanced_match si disponible
    if hasattr(integration.data_adapter, 'enhanced_match'):
        match_result = integration.data_adapter.enhanced_match(candidate_smartmatch, job_smartmatch)
        print("Calcul effectué avec la méthode enhanced_match")
    else:
        print("La méthode enhanced_match n'est pas disponible.")
        print("Pour un matching complet, assurez-vous que le module smartmatch_data_adapter.py")
        print("contient bien la méthode enhanced_match avec les fonctions de matching avancées.")
        
        print("\nUtilisation du matcher standard à la place (résultats limités)...")
        
        if integration.matcher:
            match_result = integration.matcher.calculate_match(candidate_smartmatch, job_smartmatch)
        else:
            print("SmartMatcher non disponible. Simulation d'un résultat de matching.")
            match_result = {
                "overall_score": 0.75,
                "category_scores": {
                    "skills": 0.8,
                    "location": 0.7,
                    "experience": 0.9
                },
                "insights": [
                    {"type": "skills_match", "message": "Bonne correspondance de compétences", "category": "strength"},
                    {"type": "location_match", "message": "Localisation acceptable", "category": "neutral"}
                ]
            }
    
    print("\n=== RÉSULTAT DU MATCHING ===")
    print(f"Score global: {match_result.get('overall_score', 0) * 100:.1f}%")
    
    print("\nScores par catégorie:")
    for category, score in match_result.get('category_scores', {}).items():
        print(f"  - {category}: {score * 100:.1f}%")
    
    print("\nInsights:")
    for insight in match_result.get('insights', []):
        category = insight.get('category', '')
        category_symbol = "✅" if category == "strength" else "⚠️" if category == "neutral" else "❌"
        print(f"{category_symbol} {insight.get('message', '')}")
    
    print("\n5. Sauvegarde des profils (simulation)...")
    candidate_id = integration.save_to_database(candidate_smartmatch, 'candidate')
    job_id = integration.save_to_database(job_smartmatch, 'job')
    
    print(f"Candidat sauvegardé avec ID: {candidate_id}")
    print(f"Offre sauvegardée avec ID: {job_id}")
    
    print("\nPour une intégration complète avec une base de données:")
    print("1. Implémentez les méthodes save_to_database() et load_from_database()")
    print("2. Intégrez avec votre système de stockage (SQL, NoSQL, etc.)")
    print("3. Ajoutez la gestion d'erreurs et les transactions si nécessaire")
    
    print("\n=== DÉMONSTRATION TERMINÉE ===")

if __name__ == "__main__":
    main()
