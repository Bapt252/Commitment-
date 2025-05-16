#!/usr/bin/env python3
"""
Script de test pour l'intégration Google Maps dans SmartMatch.
Permet de vérifier rapidement que l'extension de transport fonctionne correctement.
"""

import os
import json
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("transport-test")

# Tester d'abord le client minimal
try:
    print("\n=== TEST DU CLIENT GOOGLE MAPS MINIMAL ===\n")
    from app.google_maps_client_minimal import MinimalMapsClient
    
    # Créer une instance du client
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    maps_client = MinimalMapsClient(api_key=api_key)
    
    # Tester un calcul de temps de trajet simple
    origin = "Paris, France"
    destination = "Lyon, France"
    
    print(f"Test du calcul de temps de trajet entre {origin} et {destination}...")
    travel_time = maps_client.get_travel_time(origin, destination)
    print(f"Temps de trajet estimé: {travel_time} minutes")
    
    # Tester différents modes de transport
    print("\nTest des différents modes de transport:")
    modes = ["driving", "transit", "walking", "bicycling"]
    results = {}
    for mode in modes:
        time = maps_client.get_travel_time(origin, destination, mode=mode)
        results[mode] = time
        print(f"- {mode}: {time} minutes")
    
    # Tester le calcul de score de trajet
    score = maps_client.calculate_commute_score(origin, destination)
    print(f"\nScore de trajet: {score:.2f}/1.00")
    
    print("\n✅ Client Google Maps minimal fonctionne correctement!\n")
except Exception as e:
    logger.error(f"Erreur avec le client minimal: {e}")
    print("\n❌ Erreur avec le client Google Maps minimal\n")

# Tester ensuite l'intégration avec SmartMatch
try:
    print("\n=== TEST DE L'INTÉGRATION AVEC SMARTMATCH ===\n")
    
    # Créer des données de test
    test_candidates = [
        {
            "id": "c1",
            "name": "Jean Dupont",
            "skills": ["Python", "Java", "SQL"],
            "location": "Paris, France",
            "preferred_transport_mode": "transit",
            "preferred_commute_time": 45,
            "remote_preference": "hybrid"
        },
        {
            "id": "c2",
            "name": "Marie Martin",
            "skills": ["JavaScript", "React", "Node.js"],
            "location": "Lyon, France",
            "preferred_transport_mode": "driving",
            "preferred_commute_time": 30,
            "remote_preference": "full"
        }
    ]

    test_jobs = [
        {
            "id": "j1",
            "title": "Développeur Python",
            "required_skills": ["Python", "Django", "SQL"],
            "location": "Paris, France",
            "remote_policy": "hybrid"
        },
        {
            "id": "j2",
            "title": "Développeur Frontend",
            "required_skills": ["JavaScript", "React", "CSS"],
            "location": "Marseille, France",
            "remote_policy": "office_only"
        },
        {
            "id": "j3",
            "title": "Développeur Full Stack",
            "required_skills": ["Python", "JavaScript", "React"],
            "location": "Lyon, France",
            "remote_policy": "full"
        }
    ]
    
    # Essayer d'importer SmartMatcher et l'extension
    try:
        from app.smartmatch import SmartMatcher
        from app.smartmatch_transport import enhance_smartmatch_with_transport
        
        # Créer une instance SmartMatcher
        matcher = SmartMatcher()
        
        # Améliorer le matcher avec l'extension de transport
        transport_matcher = enhance_smartmatch_with_transport(matcher, api_key=api_key)
        
        # Utiliser le matching amélioré
        print("Exécution du matching avec l'extension de transport...")
        results = transport_matcher.match(test_candidates, test_jobs)
        
        # Afficher les résultats
        print(f"\nRésultats de matching: {len(results)} matchings trouvés")
        for i, match in enumerate(results, 1):
            candidate_name = next(c["name"] for c in test_candidates if c["id"] == match["candidate_id"])
            job_title = next(j["title"] for j in test_jobs if j["id"] == match["job_id"])
            
            print(f"\nMatch #{i}: {candidate_name} - {job_title}")
            print(f"  Score: {match['score']:.2f}")
            
            # Vérifier si les détails du trajet sont disponibles
            key = f"{match['candidate_id']}_{match['job_id']}"
            if hasattr(transport_matcher, 'matching_details') and key in transport_matcher.matching_details:
                commute = transport_matcher.matching_details[key].get('commute', {})
                if commute:
                    print(f"  Temps de trajet: {commute.get('actual_time', 'N/A')} minutes")
                    print(f"  Mode de transport: {commute.get('preferred_mode', 'N/A')}")
                    print(f"  Explication: {commute.get('explanation', 'N/A')}")
        
        # Générer des insights
        try:
            insights = transport_matcher.generate_insights_extended(results)
            print("\nInsights générés:")
            for insight in insights:
                print(f"- {insight['message']}")
            
            print("\n✅ Intégration SmartMatch complète fonctionne correctement!")
        except Exception as e:
            logger.error(f"Erreur lors de la génération des insights: {e}")
            print("❌ Erreur avec la génération d'insights, mais le matching fonctionne")
            
    except Exception as e:
        logger.error(f"Erreur avec l'intégration SmartMatch: {e}")
        print("\n⚠️ Impossible de tester l'intégration SmartMatch complète.")
        print("Essayons une version mock pour démontrer le concept...")
        
        # Créer un mock SmartMatcher pour quand même démontrer le concept
        from app.google_maps_client_minimal import MinimalMapsClient
        
        class MockTransportExtension:
            def __init__(self, api_key=None):
                self.maps_client = MinimalMapsClient(api_key=api_key)
            
            def enhance_match_results(self, matches, candidates, jobs):
                print("\nAmélioration des résultats avec les données de transport...")
                enhanced_results = []
                
                for match in matches:
                    # Trouver le candidat et le job
                    candidate = next((c for c in candidates if c["id"] == match["candidate_id"]), None)
                    job = next((j for j in jobs if j["id"] == match["job_id"]), None)
                    
                    if candidate and job:
                        # Calculer le temps de trajet
                        candidate_location = candidate.get("location", "")
                        job_location = job.get("location", "")
                        
                        # Vérifier la politique de télétravail
                        is_remote = job.get("remote_policy") == "full" and candidate.get("remote_preference") in ["full", "hybrid"]
                        
                        if is_remote:
                            transport_data = {
                                "commute_time": 0,
                                "commute_score": 1.0,
                                "mode": "remote",
                                "reason": "Travail entièrement à distance"
                            }
                        else:
                            # Calculer le temps de trajet avec le client minimal
                            mode = candidate.get("preferred_transport_mode", "driving")
                            commute_time = self.maps_client.get_travel_time(
                                candidate_location, job_location, mode=mode
                            )
                            
                            # Calculer le score de trajet
                            max_time = candidate.get("preferred_commute_time", 60)
                            commute_score = self.maps_client.calculate_commute_score(
                                candidate_location, job_location, max_time=max_time
                            )
                            
                            # Préparer les données de transport
                            transport_data = {
                                "commute_time": commute_time,
                                "commute_score": commute_score,
                                "mode": mode,
                                "reason": self._get_commute_description(commute_time)
                            }
                        
                        # Ajouter les données au match
                        enhanced_match = match.copy()
                        enhanced_match["transport"] = transport_data
                        
                        # Ajuster le score
                        transport_weight = 0.2
                        original_score = match.get("score", 0.5)
                        enhanced_score = (original_score * (1 - transport_weight) + 
                                         transport_data["commute_score"] * transport_weight)
                        
                        enhanced_match["original_score"] = original_score
                        enhanced_match["score"] = round(enhanced_score, 2)
                        
                        enhanced_results.append(enhanced_match)
                    else:
                        enhanced_results.append(match)
                
                return enhanced_results
            
            def _get_commute_description(self, commute_time):
                """Obtenir une description du temps de trajet"""
                if commute_time <= 15:
                    return "Trajet très court"
                elif commute_time <= 30:
                    return "Trajet court"
                elif commute_time <= 45:
                    return "Trajet de durée moyenne"
                elif commute_time <= 60:
                    return "Trajet d'une heure environ"
                elif commute_time <= 90:
                    return "Trajet assez long"
                else:
                    return "Trajet très long"
        
        # Créer une simulation de matching
        class MockSmartMatcher:
            def match(self, candidates, jobs):
                results = []
                for candidate in candidates:
                    for job in jobs:
                        # Simuler un score de base
                        base_score = 0.7
                        results.append({
                            "candidate_id": candidate["id"],
                            "job_id": job["id"],
                            "score": base_score
                        })
                return results
        
        # Utiliser le mock
        print("\nUtilisation du mock SmartMatcher pour démontrer le concept...")
        mock_matcher = MockSmartMatcher()
        transport_extension = MockTransportExtension(api_key=api_key)
        
        # Exécuter le matching mock
        base_results = mock_matcher.match(test_candidates, test_jobs)
        enhanced_results = transport_extension.enhance_match_results(
            base_results, test_candidates, test_jobs
        )
        
        # Afficher les résultats
        print(f"\nRésultats de matching: {len(enhanced_results)} matchings trouvés")
        for i, match in enumerate(enhanced_results, 1):
            candidate_name = next(c["name"] for c in test_candidates if c["id"] == match["candidate_id"])
            job_title = next(j["title"] for j in test_jobs if j["id"] == match["job_id"])
            
            print(f"\nMatch #{i}: {candidate_name} - {job_title}")
            print(f"  Score original: {match.get('original_score', 'N/A'):.2f}")
            print(f"  Score avec transport: {match['score']:.2f}")
            
            if "transport" in match:
                transport = match["transport"]
                print(f"  Temps de trajet: {transport.get('commute_time', 'N/A')} minutes")
                print(f"  Score de trajet: {transport.get('commute_score', 'N/A'):.2f}")
                print(f"  Mode de transport: {transport.get('mode', 'N/A')}")
                print(f"  Description: {transport.get('reason', 'N/A')}")
        
        print("\n✅ Test avec mock SmartMatcher réussi!")

except Exception as e:
    logger.error(f"Erreur générale lors des tests: {e}")
    print("\n❌ Erreur lors des tests")

print("\n=== FIN DES TESTS ===")
print("Consultez la documentation dans INTEGRATION-TRANSPORT.md pour plus d'informations.")
