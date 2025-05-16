#!/usr/bin/env python3
"""
Test fonctionnel pour SmartMatch
--------------------------------
Script de test fonctionnel pour vérifier le fonctionnement du système SmartMatch.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

from app.smartmatch import SmartMatcher
import json

def main():
    # Créer une instance du matcher
    matcher = SmartMatcher()
    print("SmartMatcher initialisé")

    # Charger les données de test
    test_data = matcher.load_test_data()
    candidates = test_data["candidates"]
    jobs = test_data["jobs"]
    print(f"Données de test chargées: {len(candidates)} candidats, {len(jobs)} offres d'emploi")

    # Afficher les infos du premier candidat et de la première offre
    print("\nPremier candidat:")
    print(f"  Nom: {candidates[0]['name']}")
    print(f"  Compétences: {', '.join(candidates[0]['skills'])}")

    print("\nPremière offre d'emploi:")
    print(f"  Titre: {jobs[0]['title']}")
    print(f"  Compétences requises: {', '.join(jobs[0]['required_skills'])}")

    # Calculer le match entre le premier candidat et la première offre
    print("\nCalcul du matching...")
    match_result = matcher.calculate_match(candidates[0], jobs[0])

    # Afficher le résultat de manière formatée
    print("\nRésultat du matching:")
    print(f"  Score global: {match_result['overall_score']}")
    print("\n  Scores par catégorie:")
    for category, score in match_result["category_scores"].items():
        print(f"    - {category}: {score}")

    print("\n  Insights:")
    for insight in match_result["insights"]:
        print(f"    - {insight['type']}: {insight['message']} (score: {insight['score']})")

    # Tester le matching par lots (batch matching)
    print("\nTest du matching par lots...")
    batch_results = matcher.batch_match([candidates[0]], [jobs[0]])
    print(f"  Nombre de résultats: {len(batch_results)}")
    print(f"  Premier résultat: Score global = {batch_results[0]['overall_score']}")
    
    print("\nTest terminé avec succès!")

if __name__ == "__main__":
    main()