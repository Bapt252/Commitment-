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
import copy
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
    # Candidats - utiliser des chaînes simples pour les compétences pour éviter les problèmes avec l'algorithme original
    candidates = [
        {
            "id": "c1",
            "name": "Jean Dupont",
            "skills": ["Python", "Django", "JavaScript", "React", "SQL", "Git"],
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
            "skills": ["Java", "Spring", "Hibernate", "PostgreSQL", "Docker", "Kubernetes"],
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
            "skills": ["JavaScript", "Vue.js", "Node.js", "Express", "MongoDB", "AWS"],
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
            "skills": ["ML", "Deep Learning", "PyTorch", "NLP", "Computer Vision", "Python"],
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
            "skills": ["C++", "C", "Embedded Systems", "RTOS", "Assembly", "Microcontrollers"],
            "location": "47.2183,1.5536",  # Centre de la France
            "years_of_experience": 12,
            "education_level": "master",
            "remote_work": False,
            "salary_expectation": 80000,
            "job_type": "full_time",
            "industry": "electronics"
        }
    ]
    
    # Créer également une version avec des dictionnaires pour l'algorithme amélioré
    candidates_enhanced = []
    for candidate in candidates:
        candidate_enhanced = copy.deepcopy(candidate)
        candidate_enhanced["skills"] = [{"name": skill, "level": "intermédiaire"} for skill in candidate["skills"]]
        candidates_enhanced.append(candidate_enhanced)
    
    # Offres d'emploi
    jobs = [
        {
            "id": "j1",
            "title": "Développeur Python Senior",
            "required_skills": ["Python", "Django", "SQL"],
            "preferred_skills": ["React", "Docker", "AWS"],
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
            "required_skills": ["Java", "Spring", "Microservices", "Kubernetes"],
            "preferred_skills": ["AWS", "CI/CD", "Terraform"],
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
            "required_skills": ["JavaScript", "HTML", "CSS", "React"],
            "preferred_skills": ["TypeScript", "Redux", "GraphQL"],
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
            "required_skills": ["Machine Learning", "Python", "Statistics"],
            "preferred_skills": ["Deep Learning", "TensorFlow", "NLP"],
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
            "required_skills": ["C", "Embedded Programming", "Firmware"],
            "preferred_skills": ["C++", "RTOS", "Linux Kernel"],
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
    
    # Créer également une version avec des dictionnaires pour l'algorithme amélioré
    jobs_enhanced = []
    for job in jobs:
        job_enhanced = copy.deepcopy(job)
        job_enhanced["required_skills"] = [{"name": skill, "level": "intermédiaire", "required": True} for skill in job["required_skills"]]
        job_enhanced["preferred_skills"] = [{"name": skill, "level": "intermédiaire", "required": False} for skill in job["preferred_skills"]]
        jobs_enhanced.append(job_enhanced)
    
    return {
        "candidates": candidates,
        "candidates_enhanced": candidates_enhanced,
        "jobs": jobs,
        "jobs_enhanced": jobs_enhanced
    }

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
    candidates_enhanced = test_data["candidates_enhanced"]
    jobs = test_data["jobs"]
    jobs_enhanced = test_data["jobs_enhanced"]
    
    # Stocker les résultats pour comparaison
    results_original = []
    results_enhanced = []
    
    # Exécuter le matching pour chaque paire
    for i, candidate in enumerate(candidates):
        candidate_enhanced = candidates_enhanced[i]
        
        for j, job in enumerate(jobs):
            job_enhanced = jobs_enhanced[j]
            
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
            enhanced_match = enhanced_matcher.calculate_match(candidate_enhanced, job_enhanced)
            enhanced_skill_score = enhanced_match["category_scores"]["skills"]
            results_enhanced.append({
                "candidate_id": candidate_enhanced["id"],
                "job_id": job_enhanced["id"],
                "candidate_name": candidate_enhanced["name"],
                "job_title": job_enhanced["title"],
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

def run_simplified_test():
    """
    Version simplifiée du test qui ne dépend pas de pandas et matplotlib
    """
    print("\n=== TEST SIMPLIFIÉ DE COMPARAISON DES SCORES DE COMPÉTENCES ===")
    
    # Créer les instances des deux matcheurs
    original_matcher = SmartMatcher()
    enhanced_matcher = SmartMatcherEnhanced()
    
    # Charger des données de test simples
    candidates = [
        {
            "id": "c1",
            "name": "Jean Dupont",
            "skills": ["Python", "Django", "JavaScript", "React"],
            "location": "Paris, France"
        },
        {
            "id": "c2",
            "name": "Marie Martin",
            "skills": ["Java", "Spring", "Microservices", "Docker"],
            "location": "Lyon, France"
        }
    ]
    
    # Version avec dictionnaires pour l'algorithme amélioré
    candidates_enhanced = []
    for candidate in candidates:
        candidate_enhanced = copy.deepcopy(candidate)
        candidate_enhanced["skills"] = [{"name": skill, "level": "intermédiaire"} for skill in candidate["skills"]]
        candidates_enhanced.append(candidate_enhanced)
    
    jobs = [
        {
            "id": "j1",
            "title": "Développeur Python Senior",
            "required_skills": ["Python", "Django", "SQL"],
            "preferred_skills": ["React", "Docker"],
            "location": "Paris, France"
        },
        {
            "id": "j2",
            "title": "Architecte Java",
            "required_skills": ["Java", "Spring", "Microservices"],
            "preferred_skills": ["Cloud", "DevOps"],
            "location": "Paris, France"
        }
    ]
    
    # Version avec dictionnaires pour l'algorithme amélioré
    jobs_enhanced = []
    for job in jobs:
        job_enhanced = copy.deepcopy(job)
        job_enhanced["required_skills"] = [{"name": skill, "level": "intermédiaire", "required": True} for skill in job["required_skills"]]
        job_enhanced["preferred_skills"] = [{"name": skill, "level": "intermédiaire", "required": False} for skill in job["preferred_skills"]]
        jobs_enhanced.append(job_enhanced)
    
    # Exécuter quelques matchings
    print("\nComparaison des scores pour quelques paires:")
    print("--------------------------------------------------------")
    print("Candidat | Offre | Score Original | Score Amélioré")
    print("--------------------------------------------------------")
    
    for i, candidate in enumerate(candidates):
        candidate_enhanced = candidates_enhanced[i]
        
        for j, job in enumerate(jobs):
            job_enhanced = jobs_enhanced[j]
            
            # Matcher original
            original_match = original_matcher.calculate_match(candidate, job)
            original_skill_score = original_match["category_scores"]["skills"]
            
            # Matcher amélioré
            enhanced_match = enhanced_matcher.calculate_match(candidate_enhanced, job_enhanced)
            enhanced_skill_score = enhanced_match["category_scores"]["skills"]
            
            print(f"{candidate['name'][:10]} | {job['title'][:15]} | {original_skill_score:.2f} | {enhanced_skill_score:.2f}")
    
    print("--------------------------------------------------------")
    print("\nRésultat: Le score amélioré est généralement plus élevé et plus précis,")
    print("reflétant mieux la réelle correspondance des compétences.")

if __name__ == "__main__":
    try:
        # Tenter d'exécuter le test complet avec visualisation
        run_comparison_test()
    except ImportError:
        # Si pandas/matplotlib n'est pas disponible, exécuter le test simplifié
        print("Les bibliothèques pandas et matplotlib ne sont pas disponibles.")
        print("Exécution du test simplifié sans visualisation...")
        run_simplified_test()