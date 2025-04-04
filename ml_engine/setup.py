#!/usr/bin/env python
# -*- coding: utf-8 -*-

from data_collection import setup_database
import os
import json

def setup_environment():
    """
    Configure l'environnement pour le moteur ML:
    - Initialise la base de données
    - Crée les répertoires nécessaires
    - Configure les exemples de données si nécessaire
    """
    # Créer le répertoire models s'il n'existe pas
    if not os.path.exists("./models"):
        os.makedirs("./models")
        print("Répertoire 'models' créé.")
    
    # Créer le répertoire sample_data s'il n'existe pas
    if not os.path.exists("./sample_data"):
        os.makedirs("./sample_data")
        print("Répertoire 'sample_data' créé.")
        
        # Créer un fichier d'exemple pour les données d'entraînement
        sample_data = [
            {
                "raw_text": """Développeur Full Stack H/F
                
                Entreprise innovante cherche un(e) développeur(se) Full Stack expérimenté(e).
                
                Compétences requises :
                - JavaScript / TypeScript
                - React.js
                - Node.js
                - SQL / NoSQL
                
                Expérience: 3-5 ans minimum
                Formation: Bac+5 informatique ou équivalent
                Contrat: CDI
                Lieu: Paris (télétravail possible 3j/semaine)
                Rémunération: 45-55K€ selon expérience
                """,
                "job_title": "Développeur Full Stack H/F",
                "experience": "3-5 ans minimum",
                "skills": ["JavaScript", "TypeScript", "React.js", "Node.js", "SQL", "NoSQL"],
                "education": "Bac+5 informatique ou équivalent",
                "contract": "CDI",
                "location": "Paris (télétravail possible 3j/semaine)",
                "salary": "45-55K€ selon expérience"
            },
            {
                "raw_text": """Data Scientist Senior (H/F)
                
                Nous recherchons un(e) Data Scientist avec au moins 5 ans d'expérience.
                
                Compétences: Python, TensorFlow, scikit-learn, NLP
                
                Diplôme: Bac+5 minimum en data science, statistiques ou informatique
                Type de contrat: CDI temps plein
                Localisation: Lyon, possibilité de télétravail partiel
                Salaire: 60-70K€ annuel
                """,
                "job_title": "Data Scientist Senior (H/F)",
                "experience": "5 ans d'expérience",
                "skills": ["Python", "TensorFlow", "scikit-learn", "NLP"],
                "education": "Bac+5 minimum en data science, statistiques ou informatique",
                "contract": "CDI temps plein",
                "location": "Lyon, possibilité de télétravail partiel",
                "salary": "60-70K€ annuel"
            },
            {
                "raw_text": """Chef de projet IT (H/F)
                
                Notre entreprise recrute un Chef de projet IT pour piloter nos projets de transformation digitale.
                
                Profil recherché :
                - Expérience de 8 à 10 ans en gestion de projets IT
                - Maîtrise des méthodologies Agile/Scrum
                - Compétences en management d'équipe
                - Anglais professionnel
                
                Formation : Bac+5 école d'ingénieur ou équivalent
                Contrat : CDI
                Lieu : Nantes, hybride (2j de télétravail/semaine)
                Rémunération : 65-75K€ selon profil
                """,
                "job_title": "Chef de projet IT (H/F)",
                "experience": "8 à 10 ans en gestion de projets IT",
                "skills": ["Gestion de projet", "Agile", "Scrum", "Management d'équipe", "Anglais"],
                "education": "Bac+5 école d'ingénieur ou équivalent",
                "contract": "CDI",
                "location": "Nantes, hybride (2j de télétravail/semaine)",
                "salary": "65-75K€ selon profil"
            }
        ]
        
        with open("./sample_data/job_postings.json", "w", encoding="utf-8") as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        print("Fichier d'exemple 'job_postings.json' créé.")
    
    # Initialiser la base de données
    db_engine = setup_database()
    print("Base de données initialisée.")
    
    print("\nConfiguration terminée. Vous pouvez maintenant:")
    print("1. Ajouter des données d'exemple: python train_models.py --setup-sample")
    print("2. Entraîner les modèles: python train_models.py")
    print("3. Lancer l'API: python api.py")

if __name__ == "__main__":
    setup_environment()