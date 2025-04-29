
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
    
    # Chercher des motifs courants dans les noms de fichiers CV
    # Exemple: "CV Comptable junior FR(4)"
    if "CV" in name_part:
        # Ignorer la partie "CV" et se concentrer sur le reste
        parts = name_part.replace("CV", "").strip().split(" ")
        if parts:
            # Utiliser les premières parties comme informations de poste, pas comme nom
            job_title = " ".join(parts).strip()
            return "", job_title  # Pas de nom détecté, mais titre de poste possible
    
    # Essayer de diviser en nom/prénom
    parts = name_part.replace('_', ' ').replace('-', ' ').split(' ')
    
    if len(parts) >= 2:
        prenom = parts[0].capitalize()
        nom = ' '.join(parts[1:]).capitalize()
    else:
        # Ne pas générer de noms par défaut si aucun n'est trouvé
        prenom = ""
        nom = ""
        
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
    prenom, job_title = extract_name_from_filename(filename)
    
    # Extraction basique de mots-clés du texte du CV si fourni
    skills = []
    if cv_text:
        # Compétences techniques courantes à chercher
        tech_keywords = [
            "Python", "Java", "JavaScript", "HTML", "CSS", "PHP", "C++", "C#",
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "Docker", "Kubernetes",
            "AWS", "Azure", "Git", "Linux", "React", "Angular", "Vue.js", "Node.js"
        ]
        
        # Langues courantes à chercher
        language_keywords = [
            "Français", "French", "Anglais", "English", "Espagnol", "Spanish",
            "Allemand", "German", "Italien", "Italian", "Chinois", "Chinese",
            "Japonais", "Japanese", "Arabe", "Arabic", "Russe", "Russian"
        ]
        
        # Chercher les compétences dans le texte
        for keyword in tech_keywords:
            if keyword.lower() in cv_text.lower():
                skills.append(keyword)
        
        # Limiter à maximum 8 compétences
        skills = skills[:8]
    
    # Si aucune compétence n'est trouvée, utiliser quelques exemples pour démo
    if not skills:
        skills = ["Java", "Python", "SQL", "Anglais (avancé)", "Français (intermédiaire)"]
    
    # Expériences professionnelles (simplifiées sans données fictives)
    experiences = []
    if cv_text:
        # Détection basique d'expériences basée sur des mots-clés
        exp_count = max(1, min(cv_text.lower().count("expérience"), 
                               cv_text.lower().count("stage") + 
                               cv_text.lower().count("emploi")))
        
        # Créer des structures vides pour que le frontend puisse les afficher
        for i in range(exp_count):
            experiences.append({
                "title": "",
                "company": "",
                "start_date": "",
                "end_date": "",
                "description": ""
            })
    else:
        # Deux expériences vides par défaut
        experiences = [
            {"title": "", "company": "", "start_date": "", "end_date": "", "description": ""},
            {"title": "", "company": "", "start_date": "", "end_date": "", "description": ""}
        ]
    
    # Structure compatible avec le format attendu par le frontend
    mock_data = {
        "personal_info": {
            "name": prenom,  # Pas de nom fictif
            "email": "",  # Pas d'email fictif
            "phone": "",  # Pas de téléphone fictif
            "address": ""
        },
        "position": job_title,
        "skills": [{"name": skill} for skill in skills],
        "languages": [
            {"language": "Français", "level": "natif"},
            {"language": "Anglais", "level": "avancé"}
        ],
        "experience": experiences,
        "education": [
            {
                "degree": "",
                "institution": "",
                "start_date": "",
                "end_date": ""
            }
        ]
    }
    
    # Simuler un délai pour imiter l'API
    time.sleep(0.5)
    
    logger.info(f"Données CV simulées générées pour le fichier: {filename}")
    
    return mock_data
