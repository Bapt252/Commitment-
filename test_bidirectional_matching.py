#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test pour le matching bidirectionnel

Ce script permet de tester le système de matching bidirectionnel
en simulant des candidats et une offre d'emploi.
"""

import json
import os
from bidirectional_matching_engine import get_candidates_for_job

# Charger les données de test
def load_test_data():
    """Charge les données d'exemple pour les tests"""
    
    # Vérifier si les fichiers existent
    if not os.path.exists('job_test.json'):
        print("Erreur: Fichier job_test.json introuvable")
        return None, None, None
    
    if not os.path.exists('company_preferences.json'):
        print("Erreur: Fichier company_preferences.json introuvable")
        return None, None, None
    
    # Charger les données
    with open('job_test.json', 'r', encoding='utf-8') as f:
        job_data = json.load(f)
    
    with open('company_preferences.json', 'r', encoding='utf-8') as f:
        company_preferences = json.load(f)
    
    # Simuler quelques candidats
    candidates_data = [
        {
            'email': 'john.doe@example.com',
            'cv_data': {
                'nom': 'Doe',
                'prenom': 'John',
                'competences': ['React', 'Node.js', 'Express', 'MongoDB', 'Git', 'JavaScript'],
                'annees_experience': 4,
                'formation': 'Master en informatique',
                'soft_skills': ['Communication', 'Travail d\'\u00e9quipe', 'Adaptabilité']
            },
            'questionnaire_data': {
                'contrats_recherches': ['CDI'],
                'adresse': '10 Rue de Rivoli, 75001 Paris',
                'temps_trajet_max': 30,
                'date_disponibilite': '01/05/2025',
                'salaire_min': 50000,
                'preferences_culture': {
                    'valeurs_importantes': ['Innovation', 'Équilibre vie pro/perso'],
                    'taille_equipe_preferee': 'moyenne',
                    'methodologie_preferee': 'Agile/Scrum',
                    'environnement_prefere': 'Startup dynamique'
                }
            }
        },
        {
            'email': 'alice.smith@example.com',
            'cv_data': {
                'nom': 'Smith',
                'prenom': 'Alice',
                'competences': ['React', 'Vue.js', 'TypeScript', 'GraphQL', 'AWS'],
                'annees_experience': 6,
                'formation': 'Master en génie logiciel',
                'soft_skills': ['Leadership', 'Gestion du temps', 'Résolution de problèmes']
            },
            'questionnaire_data': {
                'contrats_recherches': ['CDI', 'CDD'],
                'adresse': '25 Avenue des Champs-Élysées, 75008 Paris',
                'temps_trajet_max': 45,
                'date_disponibilite': '15/06/2025',
                'salaire_min': 55000,
                'preferences_culture': {
                    'valeurs_importantes': ['Excellence technique', 'Méritocratie'],
                    'taille_equipe_preferee': 'petite',
                    'methodologie_preferee': 'Kanban',
                    'environnement_prefere': 'Entreprise établie'
                }
            }
        },
        {
            'email': 'thomas.durand@example.com',
            'cv_data': {
                'nom': 'Durand',
                'prenom': 'Thomas',
                'competences': ['Angular', 'Java', 'Spring', 'SQL', 'Docker'],
                'annees_experience': 8,
                'formation': 'École d\'ingénieur',
                'soft_skills': ['Communication', 'Autonomie', 'Rigueur']
            },
            'questionnaire_data': {
                'contrats_recherches': ['CDI'],
                'adresse': '5 Rue de la Paix, 75002 Paris',
                'temps_trajet_max': 60,
                'date_disponibilite': '01/07/2025',
                'salaire_min': 65000,
                'preferences_culture': {
                    'valeurs_importantes': ['Stabilité', 'Excellence technique'],
                    'taille_equipe_preferee': 'grande',
                    'methodologie_preferee': 'SAFe',
                    'environnement_prefere': 'Grande entreprise'
                }
            }
        },
        {
            'email': 'sophie.martin@example.com',
            'cv_data': {
                'nom': 'Martin',
                'prenom': 'Sophie',
                'competences': ['React', 'Node.js', 'MongoDB', 'Redis', 'Docker', 'Kubernetes'],
                'annees_experience': 3,
                'formation': 'Bootcamp développement web + Bac+3 marketing',
                'soft_skills': ['Créativité', 'Travail d\'\u00e9quipe', 'Adaptabilité', 'Résolution de problèmes']
            },
            'questionnaire_data': {
                'contrats_recherches': ['CDI', 'Freelance'],
                'adresse': '8 Boulevard Saint-Germain, 75005 Paris',
                'temps_trajet_max': 40,
                'date_disponibilite': '15/05/2025',
                'salaire_min': 48000,
                'preferences_culture': {
                    'valeurs_importantes': ['Innovation', 'Équilibre vie pro/perso', 'Inclusivité'],
                    'taille_equipe_preferee': 'moyenne',
                    'methodologie_preferee': 'Agile/Scrum',
                    'environnement_prefere': 'Startup en croissance'
                }
            }
        },
        {
            'email': 'lucas.bernard@example.com',
            'cv_data': {
                'nom': 'Bernard',
                'prenom': 'Lucas',
                'competences': ['JavaScript', 'React', 'Node.js', 'Express', 'MongoDB', 'AWS'],
                'annees_experience': 1,
                'formation': 'Licence en informatique',
                'soft_skills': ['Enthousiasme', 'Adaptabilité', 'Apprentissage rapide']
            },
            'questionnaire_data': {
                'contrats_recherches': ['CDI', 'CDD', 'Stage'],
                'adresse': '30 Rue du Faubourg Saint-Antoine, 75012 Paris',
                'temps_trajet_max': 45,
                'date_disponibilite': '01/05/2025',
                'salaire_min': 38000,
                'preferences_culture': {
                    'valeurs_importantes': ['Apprentissage continu', 'Innovation'],
                    'taille_equipe_preferee': 'petite',
                    'methodologie_preferee': 'Agile/Scrum',
                    'environnement_prefere': 'Startup dynamique'
                }
            }
        }
    ]
    
    return job_data, candidates_data, company_preferences

def main():
    """Fonction principale pour exécuter le test"""
    
    # Charger les données de test
    job_data, candidates_data, company_preferences = load_test_data()
    
    if not job_data or not candidates_data or not company_preferences:
        return
    
    print("=== Test du matching bidirectionnel ===\n")
    print(f"Poste: {job_data['titre']} chez {job_data['entreprise']}")
    print(f"Localisation: {job_data['localisation']}")
    print(f"Type de contrat: {job_data['type_contrat']}")
    print(f"Compétences requises: {', '.join(job_data['competences'])}")
    print(f"Expérience: {job_data['experience']}")
    print()
    
    # Obtenir les candidats pour cette offre
    matched_candidates = get_candidates_for_job(
        job_data, 
        candidates_data, 
        company_preferences
    )
    
    # Afficher les résultats
    print(f"Top {len(matched_candidates)} candidats pour ce poste:\n")
    
    for i, candidate in enumerate(matched_candidates):
        print(f"#{i+1} - {candidate['name']} ({candidate['email']})")
        print(f"  Score: {candidate['matching_score']}%")
        print("  Détails des scores:")
        
        for criterion, score in candidate['matching_details'].items():
            print(f"    - {criterion}: {score}%")
        
        print("  Explications:")
        for criterion, explanation in candidate['matching_explanations'].items():
            print(f"    - {criterion}: {explanation}")
        
        if candidate['deal_breakers']:
            print("  ATTENTION - Critères bloquants:")
            for deal_breaker in candidate['deal_breakers']:
                print(f"    - {deal_breaker}")
        
        print()

if __name__ == "__main__":
    main()
