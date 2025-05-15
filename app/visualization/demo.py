#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de démonstration pour le visualiseur de résultats de matching.
"""

import os
import json
import sys
import random
from app.visualization.match_visualizer import MatchVisualizer

def generate_sample_data(num_matches=10):
    """
    Génère des données de matching d'exemple pour tester la visualisation.
    
    Args:
        num_matches (int): Nombre de matches à générer
        
    Returns:
        list: Liste des résultats de matching simulés
    """
    matches = []
    
    # Compétences pour l'exemple
    all_skills = [
        "Python", "JavaScript", "Java", "C#", "Ruby", "PHP",
        "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", 
        "Spring", "ASP.NET", "Ruby on Rails", "Laravel",
        "SQL", "MongoDB", "PostgreSQL", "MySQL", "Oracle", "Redis",
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins",
        "TensorFlow", "PyTorch", "Scikit-learn", "NLP", "Computer Vision",
        "DevOps", "Agile", "Scrum", "Git", "CI/CD"
    ]
    
    # Villes et localisations pour l'exemple
    locations = [
        "Paris, France", "Lyon, France", "Marseille, France", "Toulouse, France",
        "Bordeaux, France", "Nantes, France", "Strasbourg, France", "Lille, France"
    ]
    
    for i in range(num_matches):
        # Générer un score aléatoire entre 0.3 et 1.0
        score = round(random.uniform(0.3, 1.0), 2)
        
        # Générer des IDs pour le candidat et l'entreprise
        candidate_id = f"C{random.randint(1000, 9999)}"
        company_id = f"E{random.randint(1000, 9999)}"
        
        # Sélectionner des compétences pour le candidat et l'entreprise
        num_candidate_skills = random.randint(3, 8)
        num_company_skills = random.randint(3, 7)
        
        candidate_skills = random.sample(all_skills, num_candidate_skills)
        company_skills = random.sample(all_skills, num_company_skills)
        
        # Déterminer les compétences communes et manquantes
        matched_skills = list(set(candidate_skills) & set(company_skills))
        missing_skills = list(set(company_skills) - set(candidate_skills))
        
        # Générer des scores pour chaque critère
        skills_score = round(random.uniform(0.3, 1.0), 2)
        location_score = round(random.uniform(0.3, 1.0), 2)
        remote_score = round(random.uniform(0.3, 1.0), 2)
        experience_score = round(random.uniform(0.3, 1.0), 2)
        salary_score = round(random.uniform(0.3, 1.0), 2)
        
        # Générer des localisations aléatoires
        candidate_location = random.choice(locations)
        company_location = random.choice(locations)
        
        # Calculer un temps de trajet réaliste
        if candidate_location == company_location:
            travel_time = random.randint(5, 25)
        else:
            travel_time = random.randint(30, 180)
        
        # Créer l'objet match
        match = {
            "candidate_id": candidate_id,
            "company_id": company_id,
            "score": score,
            "candidate_location": candidate_location,
            "company_location": company_location,
            "details": {
                "skills_score": skills_score,
                "location_score": location_score,
                "remote_score": remote_score,
                "experience_score": experience_score,
                "salary_score": salary_score,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "travel_time_minutes": travel_time
            }
        }
        
        matches.append(match)
    
    # Trier par score décroissant
    matches.sort(key=lambda x: x["score"], reverse=True)
    
    return matches

def main():
    """Fonction principale pour la démo du visualiseur."""
    # Générer des données d'exemple
    sample_matches = generate_sample_data(15)
    
    # Initialiser le visualiseur
    visualizer = MatchVisualizer(output_dir="output/demo_dashboard")
    
    # Générer le tableau de bord
    dashboard_path = visualizer.generate_dashboard(sample_matches)
    
    # Exporter également au format JSON
    json_path = visualizer.export_json(sample_matches)
    
    # Générer un rapport statistique
    report = visualizer.generate_report(sample_matches)
    
    # Afficher les informations
    print(f"Tableau de bord généré: {os.path.abspath(dashboard_path)}")
    print(f"Données JSON exportées: {os.path.abspath(json_path)}")
    print("\nRésumé du rapport:")
    print(f"- Total des matches: {report['total_matches']}")
    print(f"- Score moyen: {report['average_score']:.2f}")
    print(f"- Distribution des scores: {report['score_distribution']}")
    print("- Top 5 compétences manquantes:")
    for i, skill_gap in enumerate(report['top_skills_gaps'][:5], 1):
        print(f"  {i}. {skill_gap['skill']} ({skill_gap['count']} fois)")

if __name__ == "__main__":
    main()
