#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de comparaison entre l'algorithme original et votre algorithme personnalisé
"""

import time
import statistics
from matching_engine import match_candidate_with_jobs as algo_original

# TODO: Décommentez quand vous aurez créé votre algorithme
# from my_matching_engine import match_candidate_with_jobs as algo_custom

def compare_algorithms():
    """Compare les performances des deux algorithmes"""
    
    print("🔬 COMPARAISON D'ALGORITHMES DE MATCHING")
    print("=" * 50)
    
    # Données de test standardisées
    test_cases = [
        {
            "name": "Développeur Python Junior",
            "cv_data": {
                "competences": ["Python", "Django", "SQL"],
                "annees_experience": 2,
                "formation": "Bachelor Informatique"
            },
            "questionnaire_data": {
                "contrats_recherches": ["CDI"],
                "adresse": "Paris",
                "salaire_min": 35000
            },
            "job_data": [
                {
                    "id": 1,
                    "titre": "Développeur Python",
                    "competences": ["Python", "Django", "PostgreSQL"],
                    "type_contrat": "CDI",
                    "salaire": "35K-45K€"
                },
                {
                    "id": 2,
                    "titre": "Data Scientist",
                    "competences": ["Python", "Machine Learning", "Pandas"],
                    "type_contrat": "CDI", 
                    "salaire": "45K-55K€"
                },
                {
                    "id": 3,
                    "titre": "Java Developer",
                    "competences": ["Java", "Spring", "MySQL"],
                    "type_contrat": "CDI",
                    "salaire": "40K-50K€"
                }
            ]
        },
        {
            "name": "Data Scientist Senior",
            "cv_data": {
                "competences": ["Python", "Machine Learning", "TensorFlow", "SQL"],
                "annees_experience": 6,
                "formation": "PhD Data Science"
            },
            "questionnaire_data": {
                "contrats_recherches": ["CDI"],
                "adresse": "Paris",
                "salaire_min": 60000
            },
            "job_data": [
                {
                    "id": 1,
                    "titre": "Senior Data Scientist",
                    "competences": ["Python", "Machine Learning", "Deep Learning"],
                    "type_contrat": "CDI",
                    "salaire": "65K-80K€"
                },
                {
                    "id": 2,
                    "titre": "ML Engineer",
                    "competences": ["Python", "TensorFlow", "Kubernetes"],
                    "type_contrat": "CDI",
                    "salaire": "60K-75K€"
                },
                {
                    "id": 3,
                    "titre": "Backend Developer",
                    "competences": ["Python", "FastAPI", "PostgreSQL"],
                    "type_contrat": "CDI",
                    "salaire": "50K-65K€"
                }
            ]
        }
    ]
    
    results_original = []
    results_custom = []
    times_original = []
    times_custom = []
    
    for test_case in test_cases:
        print(f"\n🧪 Test: {test_case['name']}")
        print("-" * 30)
        
        # Test algorithme original
        start_time = time.time()
        result_orig = algo_original(
            test_case['cv_data'], 
            test_case['questionnaire_data'], 
            test_case['job_data']
        )
        time_orig = time.time() - start_time
        
        times_original.append(time_orig)
        avg_score_orig = sum(job['matching_score'] for job in result_orig) / len(result_orig)
        results_original.append(avg_score_orig)
        
        print(f"Algorithme ORIGINAL:")
        print(f"  ⏱️  Temps: {time_orig:.3f}s")
        print(f"  📊 Score moyen: {avg_score_orig:.1f}%")
        print(f"  🎯 Meilleur match: {result_orig[0]['matching_score']}% - {result_orig[0]['titre']}")
        
        # TODO: Décommentez quand vous aurez votre algorithme
        """
        # Test votre algorithme
        start_time = time.time()
        result_custom = algo_custom(
            test_case['cv_data'], 
            test_case['questionnaire_data'], 
            test_case['job_data']
        )
        time_custom = time.time() - start_time
        
        times_custom.append(time_custom)
        avg_score_custom = sum(job['matching_score'] for job in result_custom) / len(result_custom)
        results_custom.append(avg_score_custom)
        
        print(f"Votre ALGORITHME:")
        print(f"  ⏱️  Temps: {time_custom:.3f}s")
        print(f"  📊 Score moyen: {avg_score_custom:.1f}%")
        print(f"  🎯 Meilleur match: {result_custom[0]['matching_score']}% - {result_custom[0]['titre']}")
        
        # Comparaison
        improvement = avg_score_custom - avg_score_orig
        speed_ratio = time_orig / time_custom if time_custom > 0 else float('inf')
        
        print(f"📈 AMÉLIORATION:")
        print(f"  Score: {improvement:+.1f}% {'✅' if improvement > 0 else '❌'}")
        print(f"  Vitesse: {speed_ratio:.1f}x {'⚡' if speed_ratio >= 1 else '🐌'}")
        """
        
        print("Votre ALGORITHME: ⏳ Pas encore implémenté")
        print("👉 Créez 'my_matching_engine.py' pour voir la comparaison")
    
    # Statistiques globales
    print(f"\n📊 STATISTIQUES GLOBALES")
    print("=" * 30)
    print(f"Algorithme ORIGINAL:")
    print(f"  Score moyen global: {statistics.mean(results_original):.1f}%")
    print(f"  Temps moyen: {statistics.mean(times_original):.3f}s")
    print(f"  Consistance: {statistics.stdev(results_original):.1f}% (écart-type)")
    
    print(f"\n🎯 OBJECTIFS pour votre algorithme:")
    print(f"  📈 Score moyen: > {statistics.mean(results_original) + 10:.1f}%")
    print(f"  ⚡ Temps: < {statistics.mean(times_original) * 2:.3f}s")
    print(f"  🎨 Consistance: < {statistics.stdev(results_original):.1f}%")
    
    print(f"\n🔧 ÉTAPES pour implémenter:")
    print(f"  1. cp matching_engine.py my_matching_engine.py")
    print(f"  2. Modifier la fonction match_candidate_with_jobs()")
    print(f"  3. Décommenter les lignes dans ce script")
    print(f"  4. Relancer: python compare_algorithms.py")

if __name__ == "__main__":
    compare_algorithms()
