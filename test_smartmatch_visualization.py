#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour tester l'intégration entre SmartMatch et la visualisation.
"""

import os
import sys
import json
import argparse
import random
import logging
from app.visualization.demo import generate_sample_data
from app.visualization.integration import SmartMatchWithVisualization

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Quelques constantes
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

def main():
    """Fonction principale pour tester l'intégration du matching avec la visualisation."""
    parser = argparse.ArgumentParser(description="Test de l'intégration SmartMatch avec visualisation")
    parser.add_argument("--num-candidates", type=int, default=10, help="Nombre de candidats")
    parser.add_argument("--num-companies", type=int, default=5, help="Nombre d'entreprises")
    parser.add_argument("--output-dir", type=str, default="output/smartmatch_dashboard", help="Répertoire de sortie")
    parser.add_argument("--json-only", action="store_true", help="Générer uniquement le fichier JSON (pas de HTML)")
    parser.add_argument("--weights", type=str, help="Pondérations au format JSON: ex. '{\"skills\":0.4,\"location\":0.3}'")
    args = parser.parse_args()
    
    logger.info(f"Génération de {args.num_candidates} candidats et {args.num_companies} entreprises")
    
    # Générer des candidats et entreprises pour le test
    candidates = []
    companies = []
    
    # Générer des candidats
    for i in range(args.num_candidates):
        candidate_id = f"C{random.randint(1000, 9999)}"
        skills = random.sample(ALL_SKILLS, random.randint(3, 8))
        
        candidate = {
            "id": candidate_id,
            "skills": skills,
            "location": random.choice(LOCATIONS),
            "remote_preference": random.choice(["full", "hybrid", "office"]),
            "experience": random.randint(1, 10),
            "salary_expectation": random.randint(35000, 90000)
        }
        candidates.append(candidate)
    
    # Générer des entreprises
    for i in range(args.num_companies):
        company_id = f"E{random.randint(1000, 9999)}"
        skills = random.sample(ALL_SKILLS, random.randint(3, 7))
        
        company = {
            "id": company_id,
            "required_skills": skills,
            "location": random.choice(LOCATIONS),
            "remote_policy": random.choice(["full", "hybrid", "office_only"]),
            "required_experience": random.randint(1, 8),
            "salary_range": {
                "min": random.randint(30000, 50000),
                "max": random.randint(60000, 100000)
            }
        }
        companies.append(company)
    
    # Créer l'instance d'intégration
    sm_vis = SmartMatchWithVisualization(output_dir=args.output_dir)
    
    # Appliquer les pondérations personnalisées si fournies
    if args.weights:
        try:
            weights = json.loads(args.weights)
            sm_vis.set_weights(weights)
            logger.info(f"Pondérations appliquées: {weights}")
        except json.JSONDecodeError:
            logger.error(f"Erreur: '{args.weights}' n'est pas un JSON valide. Utilisation des pondérations par défaut.")
    
    # Exécuter le matching et générer les visualisations
    try:
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
        else:
            print("Aucun match trouvé.")
        
        # Afficher un résumé des statistiques
        print("\nRésumé du rapport:")
        report = result["report"]
        print(f"- Total des matches: {report['total_matches']}")
        print(f"- Score moyen: {report['average_score']:.2f}")
        print(f"- Distribution des scores: {report['score_distribution']}")
        
        # Afficher les compétences manquantes les plus fréquentes
        print("- Top compétences manquantes:")
        for i, skill_gap in enumerate(report['top_skills_gaps'][:5], 1):
            print(f"  {i}. {skill_gap['skill']} ({skill_gap['count']} fois)")
    
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du matching et de la visualisation: {e}", exc_info=True)
        print(f"\nUne erreur est survenue: {e}")
        print("Vérifiez les logs pour plus de détails.")

if __name__ == "__main__":
    main()
