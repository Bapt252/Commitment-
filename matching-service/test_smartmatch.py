#!/usr/bin/env python3
"""
Script de test pour Nexten SmartMatch
-------------------------------------
Teste le système SmartMatch avec des données simulées et affiche les résultats.

Auteur: Claude/Anthropic
Date: 14/05/2025
"""

import os
import sys
import json
import time
import logging
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any

# Ajouter le répertoire parent au chemin de recherche pour l'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer le SmartMatcher
try:
    from app.smartmatch import SmartMatcher
except ImportError:
    print("Erreur: Impossible d'importer SmartMatcher. Vérifiez que vous exécutez le script depuis le bon répertoire.")
    sys.exit(1)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_comprehensive_test(api_key: str = None) -> pd.DataFrame:
    """
    Exécute un test complet du système SmartMatch et analyse les résultats
    
    Args:
        api_key (str): Clé API Google Maps pour les calculs de distance
        
    Returns:
        pd.DataFrame: DataFrame pandas contenant les résultats du matching
    """
    logger.info("Démarrage du test complet SmartMatch")
    
    # Initialiser le SmartMatcher
    matcher = SmartMatcher(api_key=api_key)
    logger.info("SmartMatcher initialisé")
    
    # Charger les données de test
    test_data = matcher.load_test_data()
    candidates = test_data["candidates"]
    jobs = test_data["jobs"]
    logger.info(f"Données de test chargées: {len(candidates)} candidats, {len(jobs)} emplois")
    
    # Exécuter le matching par lots
    start_time = time.time()
    results = matcher.batch_match(candidates, jobs)
    duration = time.time() - start_time
    logger.info(f"Matching terminé en {duration:.2f} secondes")
    
    # Convertir les résultats en DataFrame pandas
    df_results = pd.DataFrame(results)
    
    # Afficher les statistiques
    print("\n=== STATISTIQUES DU MATCHING ===")
    print(f"Nombre total de matchings: {len(df_results)}")
    print(f"Score moyen global: {df_results['overall_score'].mean():.2f}")
    print(f"Score médian global: {df_results['overall_score'].median():.2f}")
    print(f"Score maximum: {df_results['overall_score'].max():.2f}")
    print(f"Score minimum: {df_results['overall_score'].min():.2f}")
    
    # Extraire les scores par catégorie
    category_scores = pd.DataFrame([
        {
            'candidate_id': row['candidate_id'],
            'job_id': row['job_id'],
            'overall': row['overall_score'],
            'skills': row['category_scores']['skills'],
            'location': row['category_scores']['location'],
            'experience': row['category_scores']['experience'],
            'education': row['category_scores']['education'],
            'preferences': row['category_scores']['preferences']
        }
        for _, row in df_results.iterrows()
    ])
    
    # Afficher les scores moyens par catégorie
    print("\n=== SCORES MOYENS PAR CATÉGORIE ===")
    for category in ['skills', 'location', 'experience', 'education', 'preferences']:
        print(f"Score moyen {category}: {category_scores[category].mean():.2f}")
    
    # Afficher les meilleurs matchs
    print("\n=== TOP 3 DES MEILLEURS MATCHS ===")
    top_matches = df_results.sort_values('overall_score', ascending=False).head(3)
    for _, match in top_matches.iterrows():
        candidate_id = match['candidate_id']
        job_id = match['job_id']
        score = match['overall_score']
        
        # Trouver les noms correspondants
        candidate_name = next((c['name'] for c in candidates if c['id'] == candidate_id), candidate_id)
        job_title = next((j['title'] for j in jobs if j['id'] == job_id), job_id)
        
        print(f"Match: {candidate_name} - {job_title} (Score: {score:.2f})")
        
        # Afficher les insights
        if match['insights']:
            print("  Insights:")
            for insight in match['insights']:
                if insight['category'] == 'strength':
                    print(f"  ✓ {insight['message']} ({insight['score']:.2f})")
                elif insight['category'] == 'weakness':
                    print(f"  ✗ {insight['message']} ({insight['score']:.2f})")
                else:
                    print(f"  ! {insight['message']} ({insight['score']:.2f})")
    
    return category_scores

def create_radar_chart(data: pd.DataFrame, candidate_id: str, job_id: str):
    """
    Crée un graphique radar pour visualiser les scores par catégorie d'un match
    
    Args:
        data (pd.DataFrame): DataFrame contenant les scores par catégorie
        candidate_id (str): ID du candidat
        job_id (str): ID de l'offre d'emploi
    """
    # Filtrer les données pour le match spécifié
    match_data = data[(data['candidate_id'] == candidate_id) & (data['job_id'] == job_id)]
    
    if match_data.empty:
        logger.warning(f"Aucune donnée trouvée pour le match {candidate_id}-{job_id}")
        return
    
    # Extraire les scores
    match_scores = match_data.iloc[0]
    categories = ['skills', 'location', 'experience', 'education', 'preferences']
    scores = [match_scores[cat] for cat in categories]
    
    # Créer le graphique radar
    angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
    angles += angles[:1]  # Boucler le graphique
    scores += scores[:1]  # Boucler les scores
    
    # Configurer la figure
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # Dessiner le graphique
    ax.plot(angles, scores, linewidth=2, linestyle='solid', label=f"Match {candidate_id}-{job_id}")
    ax.fill(angles, scores, alpha=0.25)
    
    # Configurer les axes
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
    ax.set_ylim(0, 1)
    
    # Ajouter un titre
    plt.title(f"Profil du match {candidate_id}-{job_id} (Score global: {match_scores['overall']:.2f})", size=15)
    
    # Sauvegarder le graphique
    plt.tight_layout()
    filename = f"match_radar_{candidate_id}_{job_id}.png"
    plt.savefig(filename)
    logger.info(f"Graphique radar sauvegardé sous {filename}")
    plt.close()

def create_comparison_chart(data: pd.DataFrame):
    """
    Crée un graphique de comparaison des scores moyens par catégorie pour tous les matchs
    
    Args:
        data (pd.DataFrame): DataFrame contenant les scores par catégorie
    """
    # Calculer les scores moyens par catégorie
    categories = ['skills', 'location', 'experience', 'education', 'preferences']
    avg_scores = [data[cat].mean() for cat in categories]
    
    # Créer le graphique à barres
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, avg_scores, color='skyblue')
    
    # Ajouter les valeurs au-dessus des barres
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{height:.2f}', ha='center', va='bottom')
    
    # Configurer les axes
    ax.set_ylim(0, 1)
    ax.set_ylabel('Score moyen')
    ax.set_title('Scores moyens par catégorie pour tous les matchs')
    
    # Sauvegarder le graphique
    plt.tight_layout()
    filename = "category_comparison.png"
    plt.savefig(filename)
    logger.info(f"Graphique de comparaison sauvegardé sous {filename}")
    plt.close()

def create_heatmap(data: pd.DataFrame):
    """
    Crée une heatmap des scores globaux pour tous les candidats et offres d'emploi
    
    Args:
        data (pd.DataFrame): DataFrame contenant les scores par catégorie
    """
    # Pivoter les données pour créer la matrice de heatmap
    pivot_data = data.pivot_table(
        values='overall', 
        index='candidate_id', 
        columns='job_id'
    )
    
    # Créer la heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(pivot_data, cmap='YlGnBu', vmin=0, vmax=1)
    
    # Ajouter la barre de couleur
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Score', rotation=-90, va="bottom")
    
    # Configurer les ticks
    ax.set_xticks(range(len(pivot_data.columns)))
    ax.set_yticks(range(len(pivot_data.index)))
    ax.set_xticklabels(pivot_data.columns)
    ax.set_yticklabels(pivot_data.index)
    
    # Étiqueter les axes
    plt.ylabel('Candidat ID')
    plt.xlabel('Offre ID')
    plt.title('Heatmap des scores de matching')
    
    # Ajouter les valeurs dans les cellules
    for i in range(len(pivot_data.index)):
        for j in range(len(pivot_data.columns)):
            value = pivot_data.iloc[i, j]
            ax.text(j, i, f'{value:.2f}', ha="center", va="center", color="black" if value > 0.5 else "white")
    
    # Sauvegarder le graphique
    plt.tight_layout()
    filename = "matching_heatmap.png"
    plt.savefig(filename)
    logger.info(f"Heatmap sauvegardée sous {filename}")
    plt.close()

def main():
    """
    Fonction principale exécutant le test complet et générant les visualisations
    """
    # Vérifier si une clé API est fournie
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "AIzaSyC5cpNgAXN1U0L14pB4HmD7BvP8pD6K8t8")
    
    # Exécuter le test complet
    try:
        results = run_comprehensive_test(api_key)
        
        # Sauvegarder les résultats
        results.to_csv('matching_results.csv', index=False)
        logger.info("Résultats sauvegardés dans matching_results.csv")
        
        # Générer des visualisations
        # 1. Graphique radar pour le meilleur match
        top_match = results.sort_values('overall', ascending=False).iloc[0]
        create_radar_chart(results, top_match['candidate_id'], top_match['job_id'])
        
        # 2. Graphique de comparaison des catégories
        create_comparison_chart(results)
        
        # 3. Heatmap des matchs
        create_heatmap(results)
        
        print("\nTest terminé avec succès. Consultez les fichiers CSV et PNG générés pour les résultats détaillés.")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du test: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
