#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour comparer les différentes implémentations d'analyse de compétences

Ce script compare les trois versions de l'algorithme de matching des compétences:
1. Original (SmartMatcher)
2. Amélioré (SmartMatcherEnhanced)
3. Sémantique (SmartMatcherSemanticEnhanced)

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import os
import sys
import json
import logging
import time
import argparse
from typing import Dict, List, Any
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate

# Configurer le chemin pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import des implémentations de SmartMatcher
from app.smartmatch import SmartMatcher
from app.smartmatch_enhanced import SmartMatcherEnhanced, get_enhanced_matcher
from app.smartmatch_semantic_enhanced import SmartMatcherSemanticEnhanced, get_semantic_enhanced_matcher

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_test_data(file_path=None):
    """
    Charge les données de test depuis un fichier JSON ou utilise les données par défaut
    
    Args:
        file_path: Chemin du fichier JSON de test (optionnel)
        
    Returns:
        Dict: Dictionnaire avec candidats et offres d'emploi
    """
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Données chargées depuis {file_path}")
                return data
        except Exception as e:
            logger.error(f"Erreur lors du chargement du fichier {file_path}: {str(e)}")
    
    # Utiliser les données internes si pas de fichier ou erreur
    matcher = SmartMatcher()
    test_data = matcher.load_test_data()
    
    # Enrichir les données de test pour mieux tester l'analyse sémantique
    enriched_data = enrich_test_data(test_data)
    
    logger.info("Données de test internes enrichies utilisées")
    return enriched_data

def enrich_test_data(test_data):
    """
    Enrichit les données de test avec des variantes de compétences
    pour mieux tester l'analyse sémantique
    
    Args:
        test_data: Données de test originales
        
    Returns:
        Dict: Données de test enrichies
    """
    # Faire une copie profonde
    enriched = {
        "candidates": test_data["candidates"].copy(),
        "jobs": test_data["jobs"].copy()
    }
    
    # Ajouter un candidat avec des variantes de compétences
    enriched["candidates"].append({
        "id": "c_semantic",
        "name": "Sémantique Test",
        "skills": ["Python3", "ReactJS", "JS", "ML", "CI/CD", "Docker Containers"],
        "location": "48.8566,2.3522",  # Paris
        "years_of_experience": 5,
        "education_level": "master",
        "remote_work": True,
        "salary_expectation": 65000,
        "job_type": "full_time",
        "industry": "tech"
    })
    
    # Ajouter une offre d'emploi avec des variantes de compétences
    enriched["jobs"].append({
        "id": "j_semantic",
        "title": "Test Sémantique",
        "required_skills": ["Python", "React", "JavaScript"],
        "preferred_skills": ["Machine Learning", "DevOps", "Containerization"],
        "location": "48.8566,2.3522",  # Paris
        "min_years_of_experience": 3,
        "max_years_of_experience": 7,
        "required_education": "bachelor",
        "offers_remote": True,
        "salary_range": {"min": 55000, "max": 75000},
        "job_type": "full_time",
        "industry": "tech"
    })
    
    return enriched

def run_comparison(test_data, output_dir=None):
    """
    Exécute une comparaison complète des trois algorithmes
    
    Args:
        test_data: Données de test
        output_dir: Répertoire pour enregistrer les résultats (optionnel)
        
    Returns:
        DataFrame: Résultats de la comparaison
    """
    # Créer les instances des trois implémentations
    original_matcher = SmartMatcher()
    enhanced_matcher = get_enhanced_matcher()
    semantic_matcher = get_semantic_enhanced_matcher()
    
    matchers = [
        ("Original", original_matcher),
        ("Amélioré", enhanced_matcher),
        ("Sémantique", semantic_matcher)
    ]
    
    # Extraire les données
    candidates = test_data["candidates"]
    jobs = test_data["jobs"]
    
    # Préparer les résultats
    results = []
    
    # Exécuter le matching pour chaque paire
    for i, candidate in enumerate(candidates):
        for j, job in enumerate(jobs):
            row = {
                "candidate_id": candidate["id"],
                "job_id": job["id"],
                "candidate_name": candidate["name"],
                "job_title": job["title"]
            }
            
            for name, matcher in matchers:
                # Chronométrer l'exécution
                start_time = time.time()
                
                match_result = matcher.calculate_match(candidate, job)
                
                duration = time.time() - start_time
                
                # Stocker les résultats
                skill_score = match_result["category_scores"]["skills"]
                overall_score = match_result["overall_score"]
                
                row[f"{name}_skill_score"] = skill_score
                row[f"{name}_overall_score"] = overall_score
                row[f"{name}_duration"] = duration
            
            results.append(row)
    
    # Créer le DataFrame
    df = pd.DataFrame(results)
    
    # Calculer les métriques
    metrics = calculate_metrics(df, matchers)
    
    # Afficher les résultats
    display_results(df, metrics, matchers)
    
    # Générer des visualisations
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        create_visualizations(df, matchers, os.path.join(output_dir, "skills_comparison"))
    
    return df

def calculate_metrics(df, matchers):
    """
    Calcule des métriques statistiques sur les résultats
    
    Args:
        df: DataFrame avec les résultats
        matchers: Liste des implémentations testées
        
    Returns:
        Dict: Métriques calculées
    """
    metrics = {}
    
    for name, _ in matchers:
        # Métriques pour les scores de compétences
        skill_scores = df[f"{name}_skill_score"]
        metrics[f"{name}_skill_mean"] = skill_scores.mean()
        metrics[f"{name}_skill_median"] = skill_scores.median()
        metrics[f"{name}_skill_std"] = skill_scores.std()
        metrics[f"{name}_skill_min"] = skill_scores.min()
        metrics[f"{name}_skill_max"] = skill_scores.max()
        
        # Métriques pour les scores globaux
        overall_scores = df[f"{name}_overall_score"]
        metrics[f"{name}_overall_mean"] = overall_scores.mean()
        metrics[f"{name}_overall_median"] = overall_scores.median()
        metrics[f"{name}_overall_std"] = overall_scores.std()
        
        # Métriques de performance
        duration = df[f"{name}_duration"]
        metrics[f"{name}_duration_mean"] = duration.mean() * 1000  # en ms
        metrics[f"{name}_duration_median"] = duration.median() * 1000  # en ms
        metrics[f"{name}_duration_max"] = duration.max() * 1000  # en ms
    
    # Calcul des améliorations
    metrics["Enhanced_vs_Original_skill_improvement"] = (
        (metrics["Amélioré_skill_mean"] - metrics["Original_skill_mean"]) / 
        metrics["Original_skill_mean"] * 100
    )
    metrics["Semantic_vs_Original_skill_improvement"] = (
        (metrics["Sémantique_skill_mean"] - metrics["Original_skill_mean"]) / 
        metrics["Original_skill_mean"] * 100
    )
    metrics["Semantic_vs_Enhanced_skill_improvement"] = (
        (metrics["Sémantique_skill_mean"] - metrics["Amélioré_skill_mean"]) / 
        metrics["Amélioré_skill_mean"] * 100
    )
    
    return metrics

def display_results(df, metrics, matchers):
    """
    Affiche les résultats de la comparaison
    
    Args:
        df: DataFrame avec les résultats
        metrics: Métriques calculées
        matchers: Liste des implémentations testées
    """
    print("\n=== RÉSULTATS DE LA COMPARAISON DES ALGORITHMES ===")
    
    # Afficher les scores moyens
    print("\nScores moyens de correspondance des compétences:")
    for name, _ in matchers:
        mean_score = metrics[f"{name}_skill_mean"]
        median_score = metrics[f"{name}_skill_median"]
        print(f"- {name}: {mean_score:.4f} (médiane: {median_score:.4f})")
    
    # Afficher les améliorations
    print("\nAméliorations relatives:")
    print(f"- Amélioré vs Original: {metrics['Enhanced_vs_Original_skill_improvement']:.1f}%")
    print(f"- Sémantique vs Original: {metrics['Semantic_vs_Original_skill_improvement']:.1f}%")
    print(f"- Sémantique vs Amélioré: {metrics['Semantic_vs_Enhanced_skill_improvement']:.1f}%")
    
    # Afficher les performances
    print("\nTemps d'exécution moyen (ms):")
    for name, _ in matchers:
        duration_mean = metrics[f"{name}_duration_mean"]
        duration_max = metrics[f"{name}_duration_max"]
        print(f"- {name}: {duration_mean:.2f} ms (max: {duration_max:.2f} ms)")
    
    # Afficher un tableau détaillé des 5 meilleurs matchings
    print("\n=== TOP 5 DES MEILLEURS MATCHINGS PAR ALGORITHME ===")
    for name, _ in matchers:
        top5 = df.sort_values(f"{name}_skill_score", ascending=False).head(5)
        print(f"\nTop 5 pour {name}:")
        columns = ["candidate_name", "job_title", f"{name}_skill_score"]
        print(tabulate(top5[columns], headers="keys", tablefmt="pretty", floatfmt=".4f"))
    
    # Identifier les cas avec les plus grandes différences
    print("\n=== PLUS GRANDES DIFFÉRENCES ENTRE ALGORITHMES ===")
    df["Semantic_vs_Original_diff"] = df["Sémantique_skill_score"] - df["Original_skill_score"]
    largest_diff = df.sort_values("Semantic_vs_Original_diff", ascending=False).head(5)
    columns = ["candidate_name", "job_title", "Original_skill_score", "Sémantique_skill_score", "Semantic_vs_Original_diff"]
    print(tabulate(largest_diff[columns], headers="keys", tablefmt="pretty", floatfmt=".4f"))

def create_visualizations(df, matchers, output_prefix):
    """
    Crée des visualisations des résultats
    
    Args:
        df: DataFrame avec les résultats
        matchers: Liste des implémentations testées
        output_prefix: Préfixe pour les fichiers de sortie
    """
    # Créer un histogramme comparatif des scores de compétences
    plt.figure(figsize=(12, 6))
    
    for name, _ in matchers:
        plt.hist(df[f"{name}_skill_score"], bins=20, alpha=0.5, label=name)
    
    plt.xlabel('Score de correspondance des compétences')
    plt.ylabel('Fréquence')
    plt.title('Distribution des scores de compétences par algorithme')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f"{output_prefix}_histogram.png")
    
    # Créer un graphique à barres des temps d'exécution
    plt.figure(figsize=(10, 5))
    
    durations = [df[f"{name}_duration"].mean() * 1000 for name, _ in matchers]
    names = [name for name, _ in matchers]
    
    plt.bar(names, durations)
    plt.xlabel('Algorithme')
    plt.ylabel('Temps d\'exécution moyen (ms)')
    plt.title('Comparaison des temps d\'exécution')
    plt.grid(True, alpha=0.3, axis='y')
    plt.savefig(f"{output_prefix}_performance.png")
    
    # Créer un graphique de dispersion pour comparer les algorithmes deux à deux
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    axes[0].scatter(df["Original_skill_score"], df["Amélioré_skill_score"], alpha=0.6)
    axes[0].set_xlabel('Score Original')
    axes[0].set_ylabel('Score Amélioré')
    axes[0].set_title('Original vs Amélioré')
    axes[0].grid(True, alpha=0.3)
    axes[0].plot([0, 1], [0, 1], 'r--', alpha=0.5)  # Ligne de référence
    
    axes[1].scatter(df["Original_skill_score"], df["Sémantique_skill_score"], alpha=0.6)
    axes[1].set_xlabel('Score Original')
    axes[1].set_ylabel('Score Sémantique')
    axes[1].set_title('Original vs Sémantique')
    axes[1].grid(True, alpha=0.3)
    axes[1].plot([0, 1], [0, 1], 'r--', alpha=0.5)  # Ligne de référence
    
    plt.tight_layout()
    plt.savefig(f"{output_prefix}_scatter.png")
    
    logger.info(f"Visualisations enregistrées avec le préfixe: {output_prefix}")

def main():
    """Fonction principale"""
    # Parser des arguments
    parser = argparse.ArgumentParser(description="Compare les différentes implémentations d'analyse de compétences")
    parser.add_argument("--data", help="Chemin vers un fichier JSON de données de test")
    parser.add_argument("--output", help="Répertoire pour enregistrer les résultats")
    args = parser.parse_args()
    
    # Charger les données de test
    test_data = load_test_data(args.data)
    
    # Exécuter la comparaison
    results = run_comparison(test_data, args.output)
    
    logger.info("Comparaison terminée")

if __name__ == "__main__":
    main()
