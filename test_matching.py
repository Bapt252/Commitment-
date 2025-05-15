#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Script de test pour le service de matching SmartMatch."""

import json
import asyncio
import os
from app.adapters.matching_pipeline import MatchingPipeline

async def main():
    """Fonction principale pour tester le matching."""
    print("Test du service de matching SmartMatch")
    
    # Créer le répertoire des résultats s'il n'existe pas
    os.makedirs("matching_results", exist_ok=True)
    
    # Initialiser le pipeline de matching
    pipeline = MatchingPipeline()
    
    # Charger les données de test
    with open("test_data/example_cv.json", "r") as f:
        cv_data = json.load(f)
    
    with open("test_data/example_job.json", "r") as f:
        job_data = json.load(f)
    
    # Exécuter le matching
    print("Exécution du matching...")
    result = await pipeline.parse_and_match_cv_job(cv_data, job_data)
    
    # Afficher le résultat
    print("\nRésultat du matching:")
    print(f"Candidat: {result['candidate']['name']}")
    print(f"Poste: {result['job']['name']}")
    print(f"Score: {result['score']}%")
    
    print("\nDétails par critère:")
    for criterion, data in result["details"].items():
        print(f"- {criterion}: {data['score'] * 100:.1f}% (poids: {data['weight'] * 100:.0f}%)")
    
    # Si des détails sur les compétences sont disponibles
    if "skills" in result["details"] and "details" in result["details"]["skills"]:
        skills_details = result["details"]["skills"]["details"]
        
        print("\nCompétences correspondantes:")
        for skill in skills_details["matching_skills"]:
            print(f"- {skill}")
        
        print("\nCompétences manquantes:")
        for skill in skills_details["missing_skills"]:
            print(f"- {skill}")

if __name__ == "__main__":
    asyncio.run(main())
