# CV Parser Service - Service de mock parsing pour les tests sans API OpenAI

import json
import logging
import time
import random
import os.path
from typing import Dict, Any, Optional

# Setup logging
logger = logging.getLogger(__name__)

def extract_name_from_filename(filename: str) -> tuple:
    """Extrait un nom et prénom potentiels à partir du nom de fichier"""
    # Enlever l'extension
    basename = os.path.basename(filename)
    name_part = os.path.splitext(basename)[0]
    
    # Essayer de diviser en nom/prénom
    parts = name_part.replace('_', ' ').replace('-', ' ').split(' ')
    
    if len(parts) >= 2:
        prenom = parts[0].capitalize()
        nom = ' '.join(parts[1:]).capitalize()
    else:
        prenom = name_part.capitalize()
        nom = "Exemple"
        
    return prenom, nom

def get_mock_cv_data(cv_text: str = None, filename: str = "CV.pdf") -> Dict[str, Any]:
    """Génère des données simulées d'un CV pour les tests
    
    Args:
        cv_text: Texte du CV (facultatif)
        filename: Nom du fichier CV
        
    Returns:
        Dict[str, Any]: Données structurées simulées d'un CV
    """
    # Extraire un nom potentiel du nom de fichier
    prenom, nom = extract_name_from_filename(filename)
    
    # Liste de compétences techniques génériques
    tech_skills = [
        "Python", "JavaScript", "HTML/CSS", "Git", "Docker", 
        "SQL", "React", "Node.js", "AWS", "Linux"
    ]
    
    # Liste de logiciels génériques
    software_skills = [
        "Microsoft Office", "Adobe Photoshop", "JIRA", "Trello",
        "Slack", "GitHub", "VS Code", "Figma", "Notion"
    ]
    
    # Liste de soft skills génériques
    soft_skills = [
        "Communication", "Travail d'équipe", "Résolution de problèmes",
        "Gestion du temps", "Adaptabilité", "Leadership", "Créativité"
    ]
    
    # Sélectionner aléatoirement des compétences
    selected_tech = random.sample(tech_skills, min(5, len(tech_skills)))
    selected_software = random.sample(software_skills, min(3, len(software_skills)))
    selected_soft = random.sample(soft_skills, min(4, len(soft_skills)))
    
    # Générer des expériences professionnelles fictives
    experiences = [
        {
            "entreprise": "TechCorp Solutions",
            "poste": "Développeur Full-Stack",
            "date_debut": "2020-01",
            "date_fin": "2023-06",
            "description": "Développement d'applications web, collaboration avec les équipes produit, maintenance de services existants."
        },
        {
            "entreprise": "InnoSoft",
            "poste": "Développeur Front-End",
            "date_debut": "2018-03",
            "date_fin": "2019-12",
            "description": "Conception et implémentation d'interfaces utilisateur, optimisation des performances."
        }
    ]
    
    # Générer des formations fictives
    formations = [
        {
            "etablissement": "Université de Tech",
            "diplome": "Master en Informatique",
            "date_debut": "2016",
            "date_fin": "2018"
        },
        {
            "etablissement": "École d'Ingénieurs TechSup",
            "diplome": "Licence en Développement Logiciel",
            "date_debut": "2013",
            "date_fin": "2016"
        }
    ]
    
    # Générer des langues fictives
    langues = [
        {"langue": "Français", "niveau": "Natif"},
        {"langue": "Anglais", "niveau": "Courant"},
        {"langue": "Espagnol", "niveau": "Intermédiaire"}
    ]
    
    # Données structurées du mock CV
    mock_data = {
        "informations_personnelles": {
            "nom": nom,
            "prenom": prenom,
            "email": f"{prenom.lower()}.{nom.lower()}@example.com",
            "telephone": "+33 6 12 34 56 78",
            "adresse": "123 Avenue des Développeurs, 75000 Paris",
            "linkedin": f"linkedin.com/in/{prenom.lower()}-{nom.lower()}"
        },
        "competences_techniques": selected_tech,
        "logiciels": selected_software,
        "soft_skills": selected_soft,
        "experiences_professionnelles": experiences,
        "formation": formations,
        "langues": langues,
        "certifications": [
            "AWS Certified Developer",
            "Scrum Master Certified"
        ],
        "interets": [
            "Nouvelles technologies",
            "Développement durable",
            "Musique",
            "Voyages"
        ]
    }
    
    # Simuler un délai pour imiter l'API
    time.sleep(1.5)
    
    logger.info(f"Données CV simulées générées pour: {prenom} {nom}")
    
    return mock_data
