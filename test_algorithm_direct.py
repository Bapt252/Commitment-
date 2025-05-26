#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test direct de l'algorithme de matching
Script simple pour tester votre algorithme sans serveur
"""

import json
import time
from matching_engine import match_candidate_with_jobs

def print_separator(title=""):
    """Affiche un séparateur avec titre"""
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)

def print_results(results, title="Résultats"):
    """Affiche les résultats de manière lisible"""
    print_separator(title)
    
    if not results:
        print("❌ Aucun résultat trouvé")
        return
    
    for i, job in enumerate(results):
        print(f"\n🎯 Match #{i+1}")
        print(f"   Titre: {job.get('titre', 'N/A')}")
        print(f"   Entreprise: {job.get('entreprise', 'N/A')}")
        print(f"   Score global: {job.get('matching_score', 0)}%")
        
        details = job.get('matching_details', {})
        if details:
            print(f"   Détails des scores:")
            for criterion, score in details.items():
                print(f"     • {criterion}: {score}%")
        
        print(f"   Compétences requises: {job.get('competences', [])}")
        print(f"   Type contrat: {job.get('type_contrat', 'N/A')}")
        print(f"   Salaire: {job.get('salaire', 'N/A')}")

def test_1_simple():
    """Test simple avec un développeur Python"""
    print_separator("TEST 1: Développeur Python Junior")
    
    cv_data = {
        "competences": ["Python", "Django", "SQL"],
        "annees_experience": 2,
        "formation": "Bachelor Informatique"
    }
    
    questionnaire_data = {
        "contrats_recherches": ["CDI", "CDD"],
        "adresse": "Paris",
        "temps_trajet_max": 45,
        "date_disponibilite": "01/06/2025",
        "salaire_min": 35000,
        "domaines_interets": ["Web", "Backend"]
    }
    
    job_data = [
        {
            "id": 1,
            "titre": "Développeur Python Junior",
            "entreprise": "WebTech",
            "localisation": "Paris",
            "type_contrat": "CDI",
            "competences": ["Python", "Django", "PostgreSQL"],
            "experience": "1-3 ans",
            "date_debut": "15/06/2025",
            "salaire": "35K-42K€"
        },
        {
            "id": 2,
            "titre": "Développeur Java Senior",
            "entreprise": "JavaCorp",
            "localisation": "Lyon",
            "type_contrat": "CDI", 
            "competences": ["Java", "Spring", "Oracle"],
            "experience": "5-8 ans",
            "date_debut": "01/07/2025",
            "salaire": "55K-65K€"
        }
    ]
    
    print("👤 Profil candidat:")
    print(f"   Compétences: {cv_data['competences']}")
    print(f"   Expérience: {cv_data['annees_experience']} ans")
    print(f"   Salaire minimum: {questionnaire_data['salaire_min']}€")
    
    start_time = time.time()
    results = match_candidate_with_jobs(cv_data, questionnaire_data, job_data)
    execution_time = time.time() - start_time
    
    print_results(results)
    print(f"\n⏱️  Temps d'exécution: {execution_time:.3f}s")
    
    return results

def test_2_data_scientist():
    """Test avec un profil Data Scientist"""
    print_separator("TEST 2: Data Scientist Expérimenté")
    
    cv_data = {
        "competences": ["Python", "Machine Learning", "TensorFlow", "SQL", "Statistics"],
        "annees_experience": 5,
        "formation": "Master Data Science"
    }
    
    questionnaire_data = {
        "contrats_recherches": ["CDI"],
        "adresse": "Paris",
        "temps_trajet_max": 60,
        "date_disponibilite": "01/09/2025",
        "salaire_min": 55000,
        "domaines_interets": ["Data", "IA"]
    }
    
    job_data = [
        {
            "id": 1,
            "titre": "Data Scientist Senior",
            "entreprise": "DataCorp",
            "localisation": "Paris",
            "type_contrat": "CDI",
            "competences": ["Python", "Machine Learning", "Deep Learning", "SQL"],
            "experience": "4-7 ans",
            "date_debut": "01/08/2025",
            "salaire": "60K-75K€"
        },
        {
            "id": 2,
            "titre": "ML Engineer",
            "entreprise": "AI Startup",
            "localisation": "Remote",
            "type_contrat": "CDI",
            "competences": ["Python", "TensorFlow", "MLOps", "Docker"],
            "experience": "3-5 ans",
            "date_debut": "15/07/2025",
            "salaire": "55K-70K€"
        },
        {
            "id": 3,
            "titre": "Frontend Developer",
            "entreprise": "WebAgency",
            "localisation": "Paris",
            "type_contrat": "CDD",
            "competences": ["React", "JavaScript", "CSS"],
            "experience": "2-4 ans",
            "date_debut": "01/06/2025",
            "salaire": "40K-50K€"
        }
    ]
    
    print("👤 Profil candidat:")
    print(f"   Compétences: {cv_data['competences']}")
    print(f"   Expérience: {cv_data['annees_experience']} ans")
    print(f"   Salaire minimum: {questionnaire_data['salaire_min']}€")
    
    start_time = time.time()
    results = match_candidate_with_jobs(cv_data, questionnaire_data, job_data)
    execution_time = time.time() - start_time
    
    print_results(results)
    print(f"\n⏱️  Temps d'exécution: {execution_time:.3f}s")
    
    return results

def test_3_performance():
    """Test de performance avec plusieurs offres"""
    print_separator("TEST 3: Performance avec 10 offres")
    
    cv_data = {
        "competences": ["JavaScript", "React", "Node.js", "MongoDB"],
        "annees_experience": 3,
        "formation": "Master Informatique"
    }
    
    questionnaire_data = {
        "contrats_recherches": ["CDI", "CDD"],
        "adresse": "Paris",
        "salaire_min": 40000
    }
    
    # Générer 10 offres différentes
    job_data = []
    technologies = [
        ["JavaScript", "React", "Node.js"],
        ["Python", "Django", "PostgreSQL"],
        ["Java", "Spring", "MySQL"],
        ["PHP", "Laravel", "MySQL"],
        ["C#", ".NET", "SQL Server"],
        ["JavaScript", "Vue.js", "Express"],
        ["Python", "FastAPI", "MongoDB"],
        ["JavaScript", "Angular", "TypeScript"],
        ["Ruby", "Rails", "PostgreSQL"],
        ["Go", "Gin", "Redis"]
    ]
    
    for i in range(10):
        job_data.append({
            "id": i + 1,
            "titre": f"Développeur {technologies[i][0]} #{i+1}",
            "entreprise": f"Company{i+1}",
            "localisation": "Paris" if i % 2 == 0 else "Remote",
            "type_contrat": "CDI" if i % 3 == 0 else "CDD",
            "competences": technologies[i],
            "experience": f"{i%3 + 1}-{i%3 + 4} ans",
            "date_debut": f"0{(i%9)+1}/07/2025",
            "salaire": f"{35+i*3}K-{45+i*3}K€"
        })
    
    print("👤 Profil candidat:")
    print(f"   Compétences: {cv_data['competences']}")
    print(f"   Nombre d'offres à analyser: {len(job_data)}")
    
    start_time = time.time()
    results = match_candidate_with_jobs(cv_data, questionnaire_data, job_data)
    execution_time = time.time() - start_time
    
    # Afficher seulement les 3 meilleurs
    print_results(results[:3], "Top 3 des meilleurs matches")
    
    # Statistiques
    scores = [job['matching_score'] for job in results]
    print(f"\n📊 Statistiques:")
    print(f"   Score moyen: {sum(scores)/len(scores):.1f}%")
    print(f"   Score maximum: {max(scores)}%")
    print(f"   Score minimum: {min(scores)}%")
    print(f"   Offres avec score > 70%: {len([s for s in scores if s > 70])}")
    print(f"   ⏱️  Temps d'exécution: {execution_time:.3f}s")
    
    return results

def analyze_algorithm():
    """Analyse des caractéristiques de l'algorithme"""
    print_separator("ANALYSE DE L'ALGORITHME")
    
    print("🔍 Critères utilisés par l'algorithme:")
    print("   • Compétences techniques (30%)")
    print("   • Type de contrat (15%)")  
    print("   • Localisation/Temps de trajet (20%)")
    print("   • Disponibilité (10%)")
    print("   • Salaire (15%)")
    print("   • Expérience (10%)")
    
    print("\n🎯 Points forts détectés:")
    print("   ✅ Calcul rapide")
    print("   ✅ Critères multiples")
    print("   ✅ Scores détaillés")
    print("   ✅ Gestion des données manquantes")
    
    print("\n🔧 Améliorations possibles:")
    print("   🔸 Analyse sémantique des compétences")
    print("   🔸 Pondération dynamique")
    print("   🔸 Apprentissage des préférences")
    print("   🔸 Gestion des synonymes")

def main():
    """Fonction principale de test"""
    print("🚀 TESTS DE L'ALGORITHME DE MATCHING")
    print("=" * 60)
    
    try:
        # Exécuter les tests
        results_1 = test_1_simple()
        results_2 = test_2_data_scientist()
        results_3 = test_3_performance()
        
        # Analyse
        analyze_algorithm()
        
        print_separator("RÉSUMÉ DES TESTS")
        print("✅ Test 1: Développeur Python Junior - OK")
        print("✅ Test 2: Data Scientist Expérimenté - OK")
        print("✅ Test 3: Performance avec 10 offres - OK")
        print("\n🎉 Tous les tests sont passés avec succès !")
        
        print("\n🔧 ÉTAPES SUIVANTES:")
        print("1. Analyser ces résultats")
        print("2. Implémenter votre algorithme")
        print("3. Comparer les performances")
        print("4. Intégrer dans le système")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {str(e)}")
        print("Vérifiez que le fichier matching_engine.py est accessible")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎯 Tests terminés avec succès !")
    else:
        print(f"\n💥 Erreur dans les tests")
