"""
Exemple d'intégration complète de SmartMatch avec les questionnaires
------------------------------------------------------------------
Ce script montre comment intégrer les questionnaires candidat et client
avec l'algorithme SmartMatch pour générer des matchings.
"""

import json
import logging
from typing import Dict, List, Any

# Importer les modules nécessaires
from smartmatch import SmartMatcher
from smartmatch_extended import SmartMatcherExtended, create_extended_matcher
from questionnaire_integration import (
    transform_candidate_questionnaire_to_smartmatch,
    transform_client_questionnaire_to_smartmatch
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_example_integration():
    """
    Exécute un exemple d'intégration complet
    """
    # Données d'exemple des questionnaires
    candidate_questionnaire = {
        "full-name": "Jean Dupont",
        "job-title": "Développeur Python",
        "transport-method": ["public-transport", "vehicle"],
        "commute-time-public-transport": "45",
        "commute-time-vehicle": "30",
        "address": "123 Rue de Paris, 75001 Paris",
        "address-lat": "48.8566",
        "address-lng": "2.3522",
        "office-preference": "no-preference",
        "motivation-order": "remuneration,evolution,flexibility,location,other",
        "structure-type": ["startup", "pme"],
        "has-sector-preference": "yes",
        "sector-preference": ["tech", "finance"],
        "salary-range": "40K€ - 50K€ brut annuel",
        "availability": "1month",
        "currently-employed": "yes",
        "listening-reason": "no-evolution",
        "notice-period": "2months",
        "notice-negotiable": "yes",
        "recruitment-status": "in-progress"
    }
    
    client_questionnaire = {
        "company-name": "TechSolutions",
        "company-address": "456 Avenue de la République, 75011 Paris",
        "company-address-lat": "48.8592",
        "company-address-lng": "2.3781",
        "experience-required": "5-10",
        "sector-knowledge": "yes",
        "sector-list": "tech",
        "work-environment": "openspace",
        "recruitment-delay": ["1month"],
        "can-handle-notice": "yes",
        "notice-duration": "2months"
    }
    
    job_extracted_data = {
        "job-title-value": "Développeur Python Senior",
        "job-contract-value": "CDI",
        "job-location-value": "Paris, France (Télétravail possible 2j/semaine)",
        "job-experience-value": "5 ans minimum sur des technologies similaires",
        "job-education-value": "Bac+5 ingénieur ou équivalent",
        "job-salary-value": "45K€ - 55K€ selon profil",
        "job-skills-value": "<div class=\"tag\">Python</div><div class=\"tag\">Django</div><div class=\"tag\">PostgreSQL</div><div class=\"tag\">Docker</div>",
        "job-responsibilities-value": "Développement de nouvelles fonctionnalités, maintenance...",
        "job-benefits-value": "Télétravail 2j/semaine, RTT, tickets restaurant",
        "evolution_perspectives": "Possibilité d'évoluer vers un poste de lead developer en 2-3 ans"
    }
    
    # Transformation des données de questionnaire en format SmartMatch
    logger.info("Transformation des données de questionnaire en format SmartMatch...")
    
    candidate = transform_candidate_questionnaire_to_smartmatch(candidate_questionnaire)
    # Ajouter des compétences pour l'exemple (normalement extraites du CV)
    candidate["skills"] = ["Python", "Django", "JavaScript", "React", "SQL", "Git"]
    candidate["years_of_experience"] = 6
    candidate["education_level"] = "master"
    
    job = transform_client_questionnaire_to_smartmatch(client_questionnaire, job_extracted_data)
    
    # Afficher les données transformées
    logger.info("\nDonnées transformées pour le candidat:")
    print(json.dumps(candidate, indent=2))
    
    logger.info("\nDonnées transformées pour le job:")
    print(json.dumps(job, indent=2))
    
    # Exécuter le matching avec SmartMatcher de base
    logger.info("\nExécution du matching avec SmartMatcher standard...")
    
    standard_matcher = SmartMatcher()
    standard_result = standard_matcher.calculate_match(candidate, job)
    
    logger.info(f"Score standard: {standard_result['overall_score']}")
    logger.info("Scores par catégorie:")
    for category, score in standard_result["category_scores"].items():
        logger.info(f"  {category}: {score}")
    
    logger.info("\nExécution du matching avec SmartMatcherExtended...")
    
    # Exécuter le matching avec SmartMatcherExtended
    extended_matcher = create_extended_matcher()
    extended_result = extended_matcher.calculate_match(candidate, job)
    
    logger.info(f"Score étendu: {extended_result['overall_score']}")
    logger.info("Scores par catégorie:")
    for category, score in extended_result["category_scores"].items():
        logger.info(f"  {category}: {score}")
    
    # Comparer les résultats
    logger.info("\nComparaison des insights:")
    
    print("\n=== Insights du SmartMatcher standard ===")
    for insight in standard_result["insights"]:
        print(f"[{insight['category']}] {insight['message']} (score: {insight['score']})")
    
    print("\n=== Insights du SmartMatcherExtended ===")
    for insight in extended_result["insights"]:
        print(f"[{insight['category']}] {insight['message']} (score: {insight['score']})")
    
    logger.info("\nL'intégration des questionnaires avec SmartMatch est terminée avec succès!")
    
    return standard_result, extended_result

def run_batch_integration():
    """
    Exécute un exemple d'intégration par lots
    """
    # Créer plusieurs candidats de test
    candidates_data = [
        {
            "full-name": "Jean Dupont",
            "address-lat": "48.8566",
            "address-lng": "2.3522",
            "office-preference": "openspace",
            "remote_work": True,
            "skills": ["Python", "Django", "JavaScript"],
            "years_of_experience": 5,
            "education_level": "master",
            "salary-range": "45K€ - 50K€",
            "transport-method": ["public-transport"],
            "commute-time-public-transport": 40
        },
        {
            "full-name": "Marie Martin",
            "address-lat": "48.8592",
            "address-lng": "2.3781",
            "office-preference": "office",
            "remote_work": False,
            "skills": ["Java", "Spring", "SQL"],
            "years_of_experience": 8,
            "education_level": "bachelor",
            "salary-range": "60K€ - 70K€",
            "transport-method": ["vehicle"],
            "commute-time-vehicle": 30
        },
        {
            "full-name": "Ahmed Benali",
            "address-lat": "48.8759",
            "address-lng": "2.3521",
            "office-preference": "no-preference",
            "remote_work": True,
            "skills": ["JavaScript", "Vue.js", "Node.js", "MongoDB"],
            "years_of_experience": 3,
            "education_level": "bachelor",
            "salary-range": "40K€ - 45K€",
            "transport-method": ["public-transport", "bike"],
            "commute-time-public-transport": 45,
            "commute-time-bike": 25
        }
    ]
    
    # Créer plusieurs jobs de test
    jobs_data = [
        {
            "job-title-value": "Développeur Python Senior",
            "job-location-value": "Paris, 75011",
            "job-contract-value": "CDI",
            "job-salary-value": "45K€ - 55K€",
            "job-skills-value": "Python, Django, REST API, SQL",
            "job-experience-value": "5 ans",
            "job-education-value": "Bac+5",
            "job-benefits-value": "Télétravail 2j/semaine",
            "company-address-lat": "48.8592",
            "company-address-lng": "2.3781",
            "work-environment": "openspace",
            "offers_remote": True
        },
        {
            "job-title-value": "Lead Developer Java",
            "job-location-value": "Paris, 75008",
            "job-contract-value": "CDI",
            "job-salary-value": "65K€ - 75K€",
            "job-skills-value": "Java, Spring, Microservices, SQL",
            "job-experience-value": "7-10 ans",
            "job-education-value": "Bac+5",
            "job-benefits-value": "RTT, CE, Parking",
            "company-address-lat": "48.8729",
            "company-address-lng": "2.3149",
            "work-environment": "office",
            "offers_remote": False
        },
        {
            "job-title-value": "Développeur Frontend",
            "job-location-value": "Paris, 75002 (Full Remote possible)",
            "job-contract-value": "CDI",
            "job-salary-value": "40K€ - 50K€",
            "job-skills-value": "JavaScript, Vue.js, HTML, CSS",
            "job-experience-value": "2-4 ans",
            "job-education-value": "Bac+3/4",
            "job-benefits-value": "Full Remote, Flexible",
            "company-address-lat": "48.8674",
            "company-address-lng": "2.3508",
            "work-environment": "openspace",
            "offers_remote": True
        }
    ]
    
    # Convertir les données brutes en format SmartMatch
    candidates = []
    for candidate_data in candidates_data:
        candidate = transform_candidate_questionnaire_to_smartmatch(candidate_data)
        
        # Ajouter des coordonnées complètes pour la localisation
        if candidate_data.get("address-lat") and candidate_data.get("address-lng"):
            candidate["location"] = f"{candidate_data['address-lat']},{candidate_data['address-lng']}"
        
        # S'assurer que les compétences sont correctement renseignées
        if "skills" in candidate_data:
            candidate["skills"] = candidate_data["skills"]
        
        candidates.append(candidate)
    
    jobs = []
    for job_data in jobs_data:
        job = transform_client_questionnaire_to_smartmatch({}, job_data)
        
        # Ajouter des coordonnées complètes pour la localisation
        if job_data.get("company-address-lat") and job_data.get("company-address-lng"):
            job["location"] = f"{job_data['company-address-lat']},{job_data['company-address-lng']}"
        
        # Remplir directement les champs manquants
        if "offers_remote" in job_data:
            job["offers_remote"] = job_data["offers_remote"]
        
        if "work-environment" in job_data:
            job["work_environment"] = job_data["work-environment"]
        
        jobs.append(job)
    
    # Exécuter le matching par lots
    matcher = create_extended_matcher()
    results = matcher.batch_match(candidates, jobs)
    
    # Afficher les meilleurs matchings pour chaque candidat
    for i, candidate in enumerate(candidates):
        candidate_results = [r for r in results if r["candidate_id"] == candidate["id"]]
        candidate_results.sort(key=lambda x: x["overall_score"], reverse=True)
        
        print(f"\n=== Meilleurs matchings pour {candidate['name']} ===")
        for j, result in enumerate(candidate_results[:2]):  # Top 2 matchings
            job_index = next(i for i, j in enumerate(jobs) if j["id"] == result["job_id"])
            print(f"{j+1}. {jobs[job_index]['title']} - Score: {result['overall_score']}")
            print(f"   Forces: {', '.join([i['message'] for i in result['insights'] if i['category'] == 'strength'][:2])}")
            if any(i['category'] == 'weakness' for i in result['insights']):
                print(f"   Faiblesses: {', '.join([i['message'] for i in result['insights'] if i['category'] == 'weakness'][:1])}")
    
    return results

# Si le script est exécuté directement
if __name__ == "__main__":
    print("=== EXEMPLE D'INTÉGRATION SIMPLE ===")
    standard_result, extended_result = run_example_integration()
    
    print("\n\n=== EXEMPLE D'INTÉGRATION PAR LOTS ===")
    batch_results = run_batch_integration()
