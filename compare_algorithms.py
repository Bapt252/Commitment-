#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de comparaison entre l'algorithme original et votre algorithme personnalisé
"""

import time
import statistics
from matching_engine import match_candidate_with_jobs as algo_original

# Algorithme personnalisé activé
from my_matching_engine import match_candidate_with_jobs as algo_custom

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
                    "salaire": "35K-45K€",
                    "localisation": "Paris"
                },
                {
                    "id": 2,
                    "titre": "Data Scientist",
                    "competences": ["Python", "Machine Learning", "Pandas"],
                    "type_contrat": "CDI", 
                    "salaire": "45K-55K€",
                    "localisation": "Lyon"
                },
                {
                    "id": 3,
                    "titre": "Java Developer",
                    "competences": ["Java", "Spring", "MySQL"],
                    "type_contrat": "CDI",
                    "salaire": "40K-50K€",
                    "localisation": "Paris"
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
                    "salaire": "65K-80K€",
                    "localisation": "Paris"
                },
                {
                    "id": 2,
                    "titre": "ML Engineer",
                    "competences": ["Python", "TensorFlow", "Kubernetes"],
                    "type_contrat": "CDI",
                    "salaire": "60K-75K€",
                    "localisation": "Remote"
                },
                {
                    "id": 3,
                    "titre": "Backend Developer",
                    "competences": ["Python", "FastAPI", "PostgreSQL"],
                    "type_contrat": "CDI",
                    "salaire": "50K-65K€",
                    "localisation": "Lyon"
                }
            ]
        },
        {
            "name": "Frontend Developer",
            "cv_data": {
                "competences": ["JavaScript", "React", "Vue.js", "CSS"],
                "annees_experience": 3,
                "formation": "Master Web"
            },
            "questionnaire_data": {
                "contrats_recherches": ["CDI", "CDD"],
                "adresse": "Lyon",
                "salaire_min": 42000
            },
            "job_data": [
                {
                    "id": 1,
                    "titre": "React Developer",
                    "competences": ["JavaScript", "React", "TypeScript"],
                    "type_contrat": "CDI",
                    "salaire": "42K-52K€",
                    "localisation": "Lyon"
                },
                {
                    "id": 2,
                    "titre": "Vue.js Developer",
                    "competences": ["JavaScript", "Vue.js", "Nuxt.js"],
                    "type_contrat": "CDD",
                    "salaire": "40K-48K€",
                    "localisation": "Remote"
                },
                {
                    "id": 3,
                    "titre": "Full-Stack Developer",
                    "competences": ["JavaScript", "React", "Node.js", "MongoDB"],
                    "type_contrat": "CDI",
                    "salaire": "45K-55K€",
                    "localisation": "Paris"
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
        print(f"  ⏱️  Temps: {time_orig:.4f}s")
        print(f"  📊 Score moyen: {avg_score_orig:.1f}%")
        print(f"  🎯 Meilleur match: {result_orig[0]['matching_score']}% - {result_orig[0]['titre']}")
        
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
        print(f"  ⏱️  Temps: {time_custom:.4f}s")
        print(f"  📊 Score moyen: {avg_score_custom:.1f}%")
        print(f"  🎯 Meilleur match: {result_custom[0]['matching_score']}% - {result_custom[0]['titre']}")
        
        # Comparaison
        improvement = avg_score_custom - avg_score_orig
        speed_ratio = time_orig / time_custom if time_custom > 0 else float('inf')
        
        print(f"📈 AMÉLIORATION:")
        print(f"  Score: {improvement:+.1f}% {'✅' if improvement > 0 else '❌' if improvement < -2 else '⚖️'}")
        print(f"  Vitesse: {speed_ratio:.1f}x {'⚡' if speed_ratio >= 1 else '🐌'}")
        
        # Analyse détaillée des différences
        print(f"🔍 ANALYSE DÉTAILLÉE:")
        for i, (orig, custom) in enumerate(zip(result_orig, result_custom)):
            score_diff = custom['matching_score'] - orig['matching_score']
            emoji = "📈" if score_diff > 0 else "📉" if score_diff < 0 else "➡️"
            print(f"  {emoji} Offre {i+1}: {score_diff:+d}% ({orig['matching_score']}% → {custom['matching_score']}%)")
    
    # Statistiques globales
    print(f"\n📊 STATISTIQUES GLOBALES")
    print("=" * 30)
    print(f"Algorithme ORIGINAL:")
    print(f"  Score moyen global: {statistics.mean(results_original):.1f}%")
    print(f"  Temps moyen: {statistics.mean(times_original):.4f}s")
    print(f"  Consistance: {statistics.stdev(results_original):.1f}% (écart-type)")
    
    print(f"\nVotre ALGORITHME:")
    print(f"  Score moyen global: {statistics.mean(results_custom):.1f}%")
    print(f"  Temps moyen: {statistics.mean(times_custom):.4f}s")
    print(f"  Consistance: {statistics.stdev(results_custom):.1f}% (écart-type)")
    
    # Amélioration globale
    global_improvement = statistics.mean(results_custom) - statistics.mean(results_original)
    speed_improvement = statistics.mean(times_original) / statistics.mean(times_custom)
    
    print(f"\n🎯 PERFORMANCE GLOBALE:")
    print(f"  📈 Amélioration score: {global_improvement:+.1f}%")
    print(f"  ⚡ Facteur vitesse: {speed_improvement:.1f}x")
    print(f"  🎨 Consistance: {'✅ Améliorée' if statistics.stdev(results_custom) < statistics.stdev(results_original) else '❌ Dégradée'}")
    
    print(f"\n🔧 RECOMMANDATIONS:")
    if global_improvement > 5:
        print(f"  🎉 Excellent ! Votre algorithme surpasse l'original")
        print(f"  💡 Gains principaux : Localisation et compétences sémantiques")
    elif global_improvement > 0:
        print(f"  👍 Bonne amélioration, continuez l'optimisation")
        print(f"  💡 Focus sur : Ajustement des pondérations")
    else:
        print(f"  🔄 Besoin d'ajustements, analysez les cas problématiques")
        print(f"  💡 Vérifiez : Calculs de localisation et bonus/malus")
    
    if speed_improvement < 0.8:
        print(f"  ⚠️  Optimisez les performances (trop lent)")
    elif speed_improvement > 1.2:
        print(f"  ⚡ Excellent gain de vitesse !")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"  1. 🧪 Testez avec de vraies données")
    print(f"  2. 🔧 Ajustez les pondérations si nécessaire")
    print(f"  3. 📊 Intégrez dans l'API de matching")
    print(f"  4. 📈 Surveillez les métriques en production")

if __name__ == "__main__":
    compare_algorithms()
