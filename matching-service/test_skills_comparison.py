#!/usr/bin/env python3
"""
Script de test pour comparer l'algorithme original et l'algorithme amélioré
de calcul des scores de compétences pour SmartMatch.

Ce script montre l'amélioration des scores de compétences (de 0.2 à des valeurs plus élevées)
grâce à l'intégration de l'analyse sémantique et d'autres améliorations.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

# Ajuster le chemin pour trouver les modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.smartmatch import SmartMatcher
from app.smartmatch_enhanced import SmartMatcherEnhanced

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Données de test plus élaborées
def get_test_data():
    """
    Génère des données de test pour comparer les algorithmes de matching
    
    Returns:
        Dict: Dictionnaire contenant des candidats et des offres de test
    """
    # Candidats
    candidates = [
        {
            "id": "c1",
            "name": "Jean Dupont",
            "skills": [
                {"name": "Python", "level": "expert"},
                {"name": "Django", "level": "avancé"},
                {"name": "JavaScript", "level": "intermédiaire"},
                {"name": "React", "level": "intermédiaire"},
                {"name": "SQL", "level": "avancé"},
                {"name": "Git", "level": "expert"}
            ],
            "location": "48.8566,2.3522",  # Paris
            "years_of_experience": 5,
            "education_level": "master",
            "remote_work": True,
            "salary_expectation": 65000,
            "job_type": "full_time",
            "industry": "tech"
        },
        {
            "id": "c2",
            "name": "Marie Martin",
            "skills": [
                {"name": "Java", "level": "expert"},
                {"name": "Spring", "level": "avancé"},
                {"name": "Hibernate", "level": "avancé"},
                {"name": "PostgreSQL", "level": "intermédiaire"},
                {"name": "Docker", "level": "intermédiaire"},
                {"name": "Kubernetes", "level": "débutant"}
            ],
            "location": "45.7640,4.8357",  # Lyon
            "years_of_experience": 8,
            "education_level": "bachelor",
            "remote_work": False,
            "salary_expectation": 70000,
            "job_type": "full_time",
            "industry": "finance",
            "alternative_industries": ["tech", "consulting"]
        },
        {
            "id": "c3",
            "name": "Thomas Petit",
            "skills": [
                {"name": "JavaScript", "level": "expert"},
                {"name": "Vue.js", "level": "avancé"},
                {"name": "Node.js", "level": "avancé"},
                {"name": "Express", "level": "intermédiaire"},
                {"name": "MongoDB", "level": "intermédiaire"},
                {"name": "AWS", "level": "débutant"}
            ],
            "location": "43.2965,5.3698",  # Marseille
            "years_of_experience": 3,
            "education_level": "bachelor",
            "remote_work": True,
            "salary_expectation": 52000,
            "job_type": "contract",
            "industry": "tech"
        },
        {
            "id": "c4",
            "name": "Léa Bernard",
            "skills": [
                {"name": "ML", "level": "expert"},             # Abréviation de Machine Learning
                {"name": "Deep Learning", "level": "avancé"},
                {"name": "PyTorch", "level": "avancé"},
                {"name": "NLP", "level": "intermédiaire"},
                {"name": "Computer Vision", "level": "intermédiaire"},
                {"name": "Python", "level": "expert"}
            ],
            "location": "48.1173,7.3586",  # Colmar
            "years_of_experience": 4,
            "education_level": "phd",
            "remote_work": True,
            "salary_expectation": 75000,
            "job_type": "full_time",
            "industry": "research"
        },
        {
            "id": "c5",
            "name": "Simon Moreau",
            "skills": [
                {"name": "C++", "level": "expert"},
                {"name": "C", "level": "expert"},
                {"name": "Embedded Systems", "level": "avancé"},
                {"name": "RTOS", "level": "avancé"},
                {"name": "Assembly", "level": "intermédiaire"},
                {"name": "Microcontrollers", "level": "expert"}
            ],
            "location": "47.2183,1.5536",  # Centre de la France
            "years_of_experience": 12,
            "education_level": "master",
            "remote_work": False,
            "salary_expectation": 80000,
            "job_type": "full_time",
            "industry": "electronics"
        }
    ]
    
    # Offres d'emploi
    jobs = [
        {
            "id": "j1",
            "title": "Développeur Python Senior",
            "required_skills": [
                {"name": "Python", "level": "avancé"},
                {"name": "Django", "level": "intermédiaire"},
                {"name": "SQL", "level": "intermédiaire"}
            ],
            "preferred_skills": [
                {"name": "React", "level": "intermédiaire"},
                {"name": "Docker", "level": "débutant"},
                {"name": "AWS", "level": "débutant"}
            ],
            "location": "48.8847,2.2967",  # Levallois-Perret
            "min_years_of_experience": 4,
            "max_years_of_experience": 8,
            "required_education": "bachelor",
            "offers_remote": True,
            "salary_range": {"min": 55000, "max": 75000},
            "job_type": "full_time",
            "industry": "tech"
        },
        {
            "id": "j2",
            "title": "Architecte Java",
            "required_skills": [
                {"name": "Java", "level": "expert"},
                {"name": "Spring", "level": "avancé"},
                {"name": "Microservices", "level": "avancé"},
                {"name": "Kubernetes", "level": "intermédiaire"}
            ],
            "preferred_skills": [
                {"name": "AWS", "level": "intermédiaire"},
                {"name": "CI/CD", "level": "intermédiaire"},
                {"name": "Terraform", "level": "débutant"}
            ],
            "location": "48.8566,2.3522",  # Paris
            "min_years_of_experience": 5,
            "max_years_of_experience": 10,
            "required_education": "master",
            "offers_remote": False,
            "salary_range": {"min": 65000, "max": 85000},
            "job_type": "full_time",
            "industry": "finance"
        },
        {
            "id": "j3",
            "title": "Développeur Frontend",
            "required_skills": [
                {"name": "JavaScript", "level": "avancé"},
                {"name": "HTML", "level": "avancé"},
                {"name": "CSS", "level": "avancé"},
                {"name": "React", "level": "avancé"}
            ],
            "preferred_skills": [
                {"name": "TypeScript", "level": "intermédiaire"},
                {"name": "Redux", "level": "intermédiaire"},
                {"name": "GraphQL", "level": "débutant"}
            ],
            "location": "43.6043,1.4437",  # Toulouse
            "min_years_of_experience": 2,
            "max_years_of_experience": 5,
            "required_education": "bachelor",
            "offers_remote": True,
            "salary_range": {"min": 45000, "max": 60000},
            "job_type": "contract",
            "industry": "tech"
        },
        {
            "id": "j4",
            "title": "Data Scientist - Machine Learning",
            "required_skills": [
                {"name": "Machine Learning", "level": "avancé"},
                {"name": "Python", "level": "avancé"},
                {"name": "Statistics", "level": "avancé"}
            ],
            "preferred_skills": [
                {"name": "Deep Learning", "level": "intermédiaire"},
                {"name": "TensorFlow", "level": "intermédiaire"},
                {"name": "NLP", "level": "débutant"}
            ],
            "location": "48.8566,2.3522",  # Paris
            "min_years_of_experience": 3,
            "max_years_of_experience": 7,
            "required_education": "master",
            "offers_remote": True,
            "salary_range": {"min": 60000, "max": 80000},
            "job_type": "full_time",
            "industry": "tech"
        },
        {
            "id": "j5",
            "title": "Ingénieur Systèmes Embarqués",
            "required_skills": [
                {"name": "C", "level": "expert"},
                {"name": "Embedded Programming", "level": "avancé"},
                {"name": "Firmware", "level": "avancé"}
            ],
            "preferred_skills": [
                {"name": "C++", "level": "intermédiaire"},
                {"name": "RTOS", "level": "intermédiaire"},
                {"name": "Linux Kernel", "level": "débutant"}
            ],
            "location": "45.7640,4.8357",  # Lyon
            "min_years_of_experience": 5,
            "max_years_of_experience": 15,
            "required_education": "master",
            "offers_remote": False,
            "salary_range": {"min": 65000, "max": 90000},
            "job_type": "full_time",
            "industry": "electronics"
        }
    ]
    
    return {"candidates": candidates, "jobs": jobs}

def run_comparison_test():
    """
    Exécute les tests de comparaison entre les deux algorithmes
    et affiche les résultats
    """
    logger.info("Démarrage des tests de comparaison")
    
    # Créer les instances des deux matcheurs
    original_matcher = SmartMatcher()
    enhanced_matcher = SmartMatcherEnhanced()
    
    # Charger les données de test
    test_data = get_test_data()
    candidates = test_data["candidates"]
    jobs = test_data["jobs"]
    
    # Stocker les résultats pour comparaison
    results_original = []
    results_enhanced = []
    
    # Exécuter le matching pour chaque paire
    for candidate in candidates:
        for job in jobs:
            # Matcher original
            original_match = original_matcher.calculate_match(candidate, job)
            original_skill_score = original_match["category_scores"]["skills"]
            results_original.append({
                "candidate_id": candidate["id"],
                "job_id": job["id"],
                "candidate_name": candidate["name"],
                "job_title": job["title"],
                "skill_score": original_skill_score,
                "overall_score": original_match["overall_score"]
            })
            
            # Matcher amélioré
            enhanced_match = enhanced_matcher.calculate_match(candidate, job)
            enhanced_skill_score = enhanced_match["category_scores"]["skills"]
            results_enhanced.append({
                "candidate_id": candidate["id"],
                "job_id": job["id"],
                "candidate_name": candidate["name"],
                "job_title": job["title"],
                "skill_score": enhanced_skill_score,
                "overall_score": enhanced_match["overall_score"]
            })
    
    # Créer des DataFrames pour l'analyse
    df_original = pd.DataFrame(results_original)
    df_enhanced = pd.DataFrame(results_enhanced)
    
    # Fusionner les résultats pour la comparaison
    df_comparison = pd.DataFrame({
        'candidate_id': df_original['candidate_id'],
        'job_id': df_original['job_id'],
        'candidate_name': df_original['candidate_name'],
        'job_title': df_original['job_title'],
        'original_skill_score': df_original['skill_score'],
        'enhanced_skill_score': df_enhanced['skill_score'],
        'improvement': df_enhanced['skill_score'] - df_original['skill_score'],
        'original_overall': df_original['overall_score'],
        'enhanced_overall': df_enhanced['overall_score'],
        'overall_improvement': df_enhanced['overall_score'] - df_original['overall_score']
    })
    
    # Calculer les statistiques globales
    avg_original_skill = df_original['skill_score'].mean()
    avg_enhanced_skill = df_enhanced['skill_score'].mean()
    improvement_pct = ((avg_enhanced_skill - avg_original_skill) / avg_original_skill) * 100
    
    # Afficher les résultats
    logger.info("\n=== RÉSULTATS DES TESTS DE COMPARAISON ===")
    logger.info(f"Score moyen des compétences (original): {avg_original_skill:.2f}")
    logger.info(f"Score moyen des compétences (amélioré): {avg_enhanced_skill:.2f}")
    logger.info(f"Amélioration moyenne: {improvement_pct:.1f}%")
    
    # Afficher le tableau de comparaison
    print("\n=== COMPARAISON DÉTAILLÉE ===")
    comparison_table = df_comparison[['candidate_name', 'job_title', 'original_skill_score', 
                                     'enhanced_skill_score', 'improvement']]
    print(tabulate(comparison_table, headers='keys', tablefmt='pretty', floatfmt='.2f'))
    
    # Trouver les cas d'amélioration les plus significatifs
    top_improvements = df_comparison.sort_values('improvement', ascending=False).head(3)
    print("\n=== AMÉLIORATIONS LES PLUS SIGNIFICATIVES ===")
    print(tabulate(top_improvements[['candidate_name', 'job_title', 'original_skill_score', 
                                   'enhanced_skill_score', 'improvement']], 
                 headers='keys', tablefmt='pretty', floatfmt='.2f'))
    
    # Créer une visualisation des résultats
    create_comparison_chart(df_comparison)
    
    return df_comparison

def create_comparison_chart(df_comparison):
    """
    Crée un graphique de comparaison des scores de compétences
    
    Args:
        df_comparison (DataFrame): DataFrame contenant les données de comparaison
    """
    try:
        # Créer une étiquette combinée pour l'axe x
        df_comparison['match_label'] = df_comparison['candidate_name'].str.split().str[0] + ' / ' + \
                                      df_comparison['job_title'].str.split('-').str[0]
        
        # Configurer le graphique
        plt.figure(figsize=(12, 6))
        
        # Créer un graphique à barres groupées
        x = range(len(df_comparison))
        width = 0.35
        
        plt.bar([i - width/2 for i in x], df_comparison['original_skill_score'], 
                width, label='Original', color='lightcoral')
        plt.bar([i + width/2 for i in x], df_comparison['enhanced_skill_score'], 
                width, label='Amélioré', color='lightgreen')
        
        # Ajouter des étiquettes et un titre
        plt.xlabel('Paires Candidat / Offre')
        plt.ylabel('Score de compétences')
        plt.title('Comparaison des scores de compétences: Original vs Amélioré')
        plt.xticks(x, df_comparison['match_label'], rotation=45, ha='right')
        plt.legend()
        
        # Ajuster la mise en page
        plt.tight_layout()
        
        # Enregistrer le graphique
        output_file = 'skills_score_comparison.png'
        plt.savefig(output_file)
        
        logger.info(f"Graphique enregistré dans {output_file}")
        
    except Exception as e:
        logger.error(f"Erreur lors de la création du graphique: {str(e)}")

if __name__ == "__main__":
    run_comparison_test()
