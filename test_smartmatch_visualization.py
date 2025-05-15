#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour tester l'intégration entre SmartMatch et la visualisation.
"""

import os
import sys
import json
import argparse
from app.visualization.demo import generate_sample_data
from app.visualization.integration import SmartMatchWithVisualization

def main():
    """Fonction principale pour tester l'intégration du matching avec la visualisation."""
    parser = argparse.ArgumentParser(description="Test de l'intégration SmartMatch avec visualisation")
    parser.add_argument("--num-candidates", type=int, default=10, help="Nombre de candidats")
    parser.add_argument("--num-companies", type=int, default=5, help="Nombre d'entreprises")
    parser.add_argument("--output-dir", type=str, default="output/smartmatch_dashboard", help="Répertoire de sortie")
    parser.add_argument("--json-only", action="store_true", help="Générer uniquement le fichier JSON (pas de HTML)")
    parser.add_argument("--weights", type=str, help="Pondérations au format JSON: ex. '{\"skills\":0.4,\"location\":0.3}'")
    args = parser.parse_args()
    
    # Générer des données d'exemple pour les candidats et entreprises
    candidates = []
    companies = []
    
    # Utiliser la fonction de génération de données d'exemple
    mock_matches = generate_sample_data(args.num_candidates * args.num_companies)
    
    # Extraire des candidats et entreprises à partir des matches générés
    used_candidate_ids = set()
    used_company_ids = set()
    
    for match in mock_matches:
        candidate_id = match["candidate_id"]
        company_id = match["company_id"]
        
        # Candidat
        if candidate_id not in used_candidate_ids and len(candidates) < args.num_candidates:
            candidate = {
                "id": candidate_id,
                "skills": match["details"]["matched_skills"] + ([] if random.random() < 0.5 else ["ExtraSkill"]),
                "location": match["candidate_location"],
                "remote_preference": random.choice(["full", "hybrid", "office"]),
                "experience": random.randint(1, 10),
                "salary_expectation": random.randint(35000, 90000)
            }
            candidates.append(candidate)
            used_candidate_ids.add(candidate_id)
        
        # Entreprise
        if company_id not in used_company_ids and len(companies) < args.num_companies:
            company = {
                "id": company_id,
                "required_skills": match["details"]["matched_skills"] + match["details"]["missing_skills"],
                "location": match["company_location"],
                "remote_policy": random.choice(["full", "hybrid", "office_only"]),
                "required_experience": random.randint(1, 8),
                "salary_range": {
                    "min": random.randint(30000, 50000),
                    "max": random.randint(60000, 100000)
                }
            }
            companies.append(company)
            used_company_ids.add(company_id)
    
    # S'assurer que nous avons suffisamment de données
    while len(candidates) < args.num_candidates:
        candidate_id = f"C{random.randint(1000, 9999)}"
        if candidate_id not in used_candidate_ids:
            candidate = {
                "id": candidate_id,
                "skills": random.sample(ALL_SKILLS, random.randint(3, 8)),
                "location": random.choice(LOCATIONS),
                "remote_preference": random.choice(["full", "hybrid", "office"]),
                "experience": random.randint(1, 10),
                "salary_expectation": random.randint(35000, 90000)
            }
            candidates.append(candidate)
            used_candidate_ids.add(candidate_id)
    
    while len(companies) < args.num_companies:
        company_id = f"E{random.randint(1000, 9999)}"
        if company_id not in used_company_ids:
            company = {
                "id": company_id,
                "required_skills": random.sample(ALL_SKILLS, random.randint(3, 7)),
                "location": random.choice(LOCATIONS),
                "remote_policy": random.choice(["full", "hybrid", "office_only"]),
                "required_experience": random.randint(1, 8),
                "salary_range": {
                    "min": random.randint(30000, 50000),
                    "max": random.randint(60000, 100000)
                }
            }
            companies.append(company)
            used_company_ids.add(company_id)
    
    # Créer l'instance d'intégration
    sm_vis = SmartMatchWithVisualization(output_dir=args.output_dir)
    
    # Appliquer les pondérations personnalisées si fournies
    if args.weights:
        try:
            weights = json.loads(args.weights)
            sm_vis.set_weights(weights)
            print(f"Pondérations appliquées: {weights}")
        except json.JSONDecodeError:
            print(f"Erreur: '{args.weights}' n'est pas un JSON valide. Utilisation des pondérations par défaut.")
    
    # Exécuter le matching et générer les visualisations
    result = sm_vis.match_and_visualize(
        candidates, 
        companies,
        generate_html=not args.json_only,
        export_json=True
    )
    
    # Afficher les résultats
    print(f"\nTraitement terminé. {len(result['match_results'])} matches trouvés.")
    
    if "dashboard" in result["output_paths"]:
        print(f"Tableau de bord généré: {os.path.abspath(result['output_paths']['dashboard'])}")
    
    if "json" in result["output_paths"]:
        print(f"Données JSON exportées: {os.path.abspath(result['output_paths']['json'])}")
    
    # Afficher un échantillon d'explication détaillée
    if result["match_results"]:
        best_match = result["match_results"][0]
        print("\nExplication détaillée du meilleur match:")
        explanation = sm_vis.explain_match(best_match)
        print(explanation)
    
    print("\nRésumé du rapport:")
    report = result["report"]
    print(f"- Total des matches: {report['total_matches']}")
    print(f"- Score moyen: {report['average_score']:.2f}")
    print(f"- Distribution des scores: {report['score_distribution']}")
    
    # Afficher les compétences manquantes les plus fréquentes
    print("- Top compétences manquantes:")
    for i, skill_gap in enumerate(report['top_skills_gaps'][:5], 1):
        print(f"  {i}. {skill_gap['skill']} ({skill_gap['count']} fois)")

if __name__ == "__main__":
    # Quelques constantes
    import random
    
    ALL_SKILLS = [
        "Python", "JavaScript", "Java", "C#", "Ruby", "PHP",
        "React", "Angular", "Vue.js", "Node.js", "Django", "Flask", 
        "Spring", "ASP.NET", "Ruby on Rails", "Laravel",
        "SQL", "MongoDB", "PostgreSQL", "MySQL", "Oracle", "Redis",
        "AWS", "Azure", "Google Cloud", "Docker", "Kubernetes", "Jenkins",
        "TensorFlow", "PyTorch", "Scikit-learn", "NLP", "Computer Vision",
        "DevOps", "Agile", "Scrum", "Git", "CI/CD"
    ]
    
    LOCATIONS = [
        "Paris, France", "Lyon, France", "Marseille, France", "Toulouse, France",
        "Bordeaux, France", "Nantes, France", "Strasbourg, France", "Lille, France"
    ]
    
    main()
