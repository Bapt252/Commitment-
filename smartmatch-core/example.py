"""
Exemple d'utilisation de l'algorithme SmartMatch
---------------------------------------------------
Ce script montre comment utiliser l'algorithme SmartMatch
pour calculer la correspondance entre candidats et offres d'emploi.
"""

import json
import os
from smartmatch import SmartMatcher

# Initialiser le matcher
api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
matcher = SmartMatcher(api_key=api_key)

# Charger des données de test
test_data = matcher.load_test_data()
candidates = test_data["candidates"]
jobs = test_data["jobs"]

def print_match_result(result):
    """
    Affiche les résultats du matching de manière formatée
    """
    print(f"\n{'=' * 50}")
    print(f"Match: Candidat {result['candidate_id']} - Offre {result['job_id']}")
    print(f"Score global: {result['overall_score']}")
    print("\nScores par catégorie:")
    for category, score in result["category_scores"].items():
        print(f"  - {category}: {score}")
    
    print("\nInsights:")
    strengths = [i for i in result["insights"] if i.get("category") == "strength"]
    weaknesses = [i for i in result["insights"] if i.get("category") == "weakness"]
    mismatches = [i for i in result["insights"] if i.get("category") == "mismatch"]
    
    if strengths:
        print("  Forces:")
        for s in strengths:
            print(f"    - {s['message']}")
    
    if weaknesses:
        print("  Faiblesses:")
        for w in weaknesses:
            print(f"    - {w['message']}")
    
    if mismatches:
        print("  Incompatibilités:")
        for m in mismatches:
            print(f"    - {m['message']}")
    
    print(f"{'=' * 50}\n")

def main():
    print("\n===== DÉMONSTRATION DE SMARTMATCH =====\n")
    
    # Exemple 1: Matching simple entre un candidat et une offre
    print("\n1. MATCHING SIMPLE")
    candidate = candidates[0]  # Jean Dupont
    job = jobs[0]  # Développeur Python Senior
    
    result = matcher.calculate_match(candidate, job)
    print_match_result(result)
    
    # Exemple 2: Trouver la meilleure offre pour un candidat
    print("\n2. MEILLEURE OFFRE POUR UN CANDIDAT")
    candidate = candidates[2]  # Thomas Petit
    
    best_job = None
    best_score = 0
    
    for job in jobs:
        result = matcher.calculate_match(candidate, job)
        if result["overall_score"] > best_score:
            best_score = result["overall_score"]
            best_job = job
            best_result = result
    
    if best_job:
        print(f"Meilleure offre pour {candidate['name']}: {best_job['title']}")
        print_match_result(best_result)
    
    # Exemple 3: Trouver les meilleurs candidats pour une offre
    print("\n3. MEILLEURS CANDIDATS POUR UNE OFFRE")
    job = jobs[1]  # Architecte Java
    
    results = []
    for candidate in candidates:
        result = matcher.calculate_match(candidate, job)
        results.append((candidate, result))
    
    # Trier par score décroissant
    results.sort(key=lambda x: x[1]["overall_score"], reverse=True)
    
    print(f"Meilleurs candidats pour le poste '{job['title']}':")
    for candidate, result in results:
        print(f"- {candidate['name']}: {result['overall_score']}")
    
    # Afficher le détail du meilleur candidat
    if results:
        print("\nDétail du meilleur candidat:")
        print_match_result(results[0][1])
    
    # Exemple 4: Batch matching
    print("\n4. BATCH MATCHING")
    batch_results = matcher.batch_match(candidates, jobs)
    
    print(f"Nombre total de matchings calculés: {len(batch_results)}")
    
    # Trouver le meilleur match global
    best_batch_match = max(batch_results, key=lambda x: x["overall_score"])
    
    print("\nMeilleur match global:")
    best_candidate = next(c for c in candidates if c["id"] == best_batch_match["candidate_id"])
    best_job = next(j for j in jobs if j["id"] == best_batch_match["job_id"])
    
    print(f"Candidat: {best_candidate['name']}")
    print(f"Poste: {best_job['title']}")
    print(f"Score: {best_batch_match['overall_score']}")
    
    print("\n===== FIN DE LA DÉMONSTRATION =====\n")

if __name__ == "__main__":
    main()
