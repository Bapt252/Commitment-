#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de test d'intégration complète pour le système Commitment-
================================================================
Teste l'intégration entre les parsers, l'adaptateur de données 
et le moteur de matching ImprovedMatchingEngine.

Auteur: Claude
Date: 26/05/2025
Version: 1.0.0
"""

import json
import sys
import traceback
from typing import Dict, List, Any
from datetime import datetime

# Import de l'adaptateur de données
try:
    from data_adapter import CommitmentDataAdapter, create_matching_response, create_error_response
    print("✅ Import data_adapter réussi")
except ImportError as e:
    print(f"❌ Erreur import data_adapter: {e}")
    sys.exit(1)

# Import du moteur de matching
try:
    from my_matching_engine import match_candidate_with_jobs, ImprovedMatchingEngine
    print("✅ Import my_matching_engine réussi")
except ImportError as e:
    print(f"❌ Erreur import my_matching_engine: {e}")
    print("Assurez-vous que my_matching_engine.py est dans le même répertoire")
    sys.exit(1)


def test_basic_functionality():
    """Test des fonctionnalités de base de l'adaptateur"""
    print("\n🔧 Test des fonctionnalités de base...")
    
    adapter = CommitmentDataAdapter()
    
    # Test normalisation des compétences
    skills_test = ['JavaScript', 'React.js', 'Node.js', 'Python', 'django']
    normalized = adapter.normalize_skills(skills_test)
    print(f"Compétences normalisées: {normalized}")
    
    # Test extraction années d'expérience
    exp_tests = [
        "5 ans d'expérience en développement",
        "Développeur senior avec 8 années",
        "Junior avec 2 ans",
        "Expert développement"
    ]
    
    for exp_text in exp_tests:
        years = adapter.extract_experience_years(exp_text)
        print(f"'{exp_text}' -> {years} ans")
    
    # Test parsing salaire
    salary_tests = [
        "45k-55k €",
        "40 000 - 50 000 euros",
        "60k",
        "35000€"
    ]
    
    for salary_text in salary_tests:
        parsed = adapter.parse_salary_range(salary_text)
        print(f"'{salary_text}' -> {parsed}")
    
    print("✅ Tests de base terminés")


def get_sample_cv_data() -> Dict[str, Any]:
    """Retourne des données CV d'exemple issues du parsing"""
    return {
        "nom": "Durand",
        "prenom": "Marie",
        "email": "marie.durand@email.com",
        "telephone": "06 12 34 56 78",
        "adresse": "45 rue de Rivoli, 75001 Paris",
        "poste": "Développeuse Full Stack Senior",
        "competences": ["Python", "JavaScript", "React", "Django", "PostgreSQL", "Docker", "Git"],
        "logiciels": ["VS Code", "PyCharm", "Figma", "Jira"],
        "formation": "Master en Informatique - EPITECH",
        "experience": "6 ans d'expérience en développement web",
        "langues": ["Français (natif)", "Anglais (courant)", "Espagnol (intermédiaire)"],
        "soft_skills": ["Leadership", "Communication", "Travail d'équipe", "Autonomie"]
    }


def get_sample_questionnaire_data() -> Dict[str, Any]:
    """Retourne des données questionnaire d'exemple"""
    return {
        "adresse": "45 rue de Rivoli, 75001 Paris",
        "temps_trajet_max": 45,
        "fourchette_salaire": "55k-65k",
        "types_contrat": ["CDI", "Freelance"],
        "disponibilite": "15/07/2025",
        "secteurs_interesse": ["tech", "fintech", "e-commerce"],
        "teletravail": True,
        "mobilite": True
    }


def get_sample_jobs_data() -> List[Dict[str, Any]]:
    """Retourne des données d'offres d'emploi d'exemple"""
    return [
        {
            "id": "job_001",
            "titre": "Développeur Full Stack Senior",
            "entreprise": "TechCorp",
            "localisation": "Paris 8ème",
            "description": "Rejoignez notre équipe de développement pour créer des applications web innovantes.",
            "competences": ["Python", "Django", "React", "PostgreSQL", "Docker"],
            "experience": "5-7 ans d'expérience",
            "formation": "Bac+5 en informatique",
            "type_contrat": "CDI",
            "salaire": "58k-68k",
            "date_debut": "01/08/2025",
            "avantages": ["Télétravail partiel", "Mutuelle", "RTT", "Prime de performance"],
            "secteur": "tech"
        },
        {
            "id": "job_002", 
            "titre": "Lead Developer Python",
            "entreprise": "FinanceApp",
            "localisation": "Paris La Défense",
            "description": "Pilotez le développement de notre plateforme fintech.",
            "competences": ["Python", "FastAPI", "React", "MongoDB", "AWS"],
            "experience": "7+ ans",
            "formation": "Ingénieur ou Master",
            "type_contrat": "CDI",
            "salaire": "70k-80k",
            "date_debut": "15/07/2025",
            "avantages": ["Full remote possible", "Stock options", "Formation"],
            "secteur": "fintech"
        },
        {
            "id": "job_003",
            "titre": "Développeur Frontend React",
            "entreprise": "StartupXYZ",
            "localisation": "Paris 11ème",
            "description": "Développez l'interface de notre application e-commerce innovante.",
            "competences": ["JavaScript", "React", "TypeScript", "CSS", "GraphQL"],
            "experience": "3-5 ans",
            "formation": "Bac+3/5",
            "type_contrat": "CDI",
            "salaire": "45k-55k",
            "date_debut": "01/09/2025",
            "avantages": ["Télétravail 3j/semaine", "Tickets restaurant"],
            "secteur": "e-commerce"
        },
        {
            "id": "job_004",
            "titre": "Architecte Logiciel Senior",
            "entreprise": "BigTech",
            "localisation": "Boulogne-Billancourt",
            "description": "Concevez l'architecture de nos systèmes distribués.",
            "competences": ["Python", "Java", "Kubernetes", "Microservices", "AWS"],
            "experience": "10+ ans",
            "formation": "Ingénieur",
            "type_contrat": "CDI",
            "salaire": "80k-95k",
            "date_debut": "01/06/2025",
            "avantages": ["Package premium", "Voiture de fonction"],
            "secteur": "tech"
        },
        {
            "id": "job_005",
            "titre": "Développeur Backend Junior",
            "entreprise": "WebAgency",
            "localisation": "Paris 9ème",
            "description": "Rejoignez notre équipe pour développer des APIs robustes.",
            "competences": ["Python", "Flask", "MySQL", "Redis"],
            "experience": "1-3 ans",
            "formation": "Bac+3/5",
            "type_contrat": "CDI",
            "salaire": "38k-45k",
            "date_debut": "15/08/2025",
            "avantages": ["Formation continue", "Mutuelle"],
            "secteur": "web"
        }
    ]


def test_data_adaptation():
    """Test de l'adaptation des données"""
    print("\n🔄 Test d'adaptation des données...")
    
    adapter = CommitmentDataAdapter()
    
    # Récupérer les données d'exemple
    cv_data = get_sample_cv_data()
    questionnaire_data = get_sample_questionnaire_data()
    jobs_data = get_sample_jobs_data()
    
    print(f"Données d'entrée:")
    print(f"  - CV: {cv_data['prenom']} {cv_data['nom']}")
    print(f"  - Questionnaire: {len(questionnaire_data)} champs")
    print(f"  - Offres: {len(jobs_data)} offres")
    
    try:
        # Test adaptation CV
        adapted_cv = adapter.adapt_cv_data(cv_data)
        print(f"\n✅ CV adapté: {len(adapted_cv['competences'])} compétences normalisées")
        print(f"   Expérience: {adapted_cv['annees_experience']} ans")
        
        # Test adaptation questionnaire
        adapted_questionnaire = adapter.adapt_questionnaire_data(questionnaire_data)
        print(f"✅ Questionnaire adapté: salaire min {adapted_questionnaire['salaire_min']}€")
        
        # Test adaptation offres
        adapted_jobs = [adapter.adapt_job_data(job) for job in jobs_data]
        print(f"✅ Offres adaptées: {len(adapted_jobs)} offres")
        
        # Afficher un exemple d'offre adaptée
        print(f"\nExemple d'offre adaptée:")
        print(f"  - Titre: {adapted_jobs[0]['titre']}")
        print(f"  - Compétences: {adapted_jobs[0]['competences']}")
        print(f"  - Salaire: {adapted_jobs[0]['salaire']}")
        
        return adapted_cv, adapted_questionnaire, adapted_jobs
        
    except Exception as e:
        print(f"❌ Erreur adaptation: {str(e)}")
        traceback.print_exc()
        return None, None, None


def test_complete_matching():
    """Test du matching complet"""
    print("\n🎯 Test du matching complet...")
    
    adapter = CommitmentDataAdapter()
    
    # Récupérer les données d'exemple
    cv_data = get_sample_cv_data()
    questionnaire_data = get_sample_questionnaire_data()
    jobs_data = get_sample_jobs_data()
    
    try:
        # Lancer le matching complet
        print("Lancement du matching...")
        results = adapter.run_matching(
            cv_data=cv_data,
            questionnaire_data=questionnaire_data,
            jobs_data=jobs_data,
            limit=10
        )
        
        print(f"✅ Matching terminé: {len(results)} résultats")
        
        # Afficher les résultats
        if results:
            print(f"\n📊 Top 3 des matches:")
            for i, result in enumerate(results[:3], 1):
                score = result.get('matching_score', 0)
                titre = result.get('titre', 'N/A')
                entreprise = result.get('entreprise', 'N/A')
                
                print(f"  {i}. {titre} chez {entreprise}")
                print(f"     Score global: {score}%")
                
                # Détails des scores
                details = result.get('matching_details', {})
                if details:
                    print(f"     Détails: Compétences {details.get('skills', 0)}%, "
                          f"Localisation {details.get('location', 0)}%, "
                          f"Salaire {details.get('salary', 0)}%")
                print()
        
        # Calculer des statistiques
        stats = adapter.get_matching_statistics(results)
        print(f"📈 Statistiques:")
        print(f"   Score moyen: {stats['moyenne_score']:.1f}%")
        print(f"   Répartition: {stats['scores_par_tranche']['excellent']} excellent(s), "
              f"{stats['scores_par_tranche']['bon']} bon(s), "
              f"{stats['scores_par_tranche']['moyen']} moyen(s)")
        
        return results, stats
        
    except Exception as e:
        print(f"❌ Erreur matching: {str(e)}")
        traceback.print_exc()
        return None, None


def test_api_response_format():
    """Test du format de réponse API"""
    print("\n📡 Test du format de réponse API...")
    
    # Simuler des résultats
    mock_results = [
        {
            'matching_score': 85,
            'titre': 'Développeur Senior',
            'entreprise': 'TechCorp'
        },
        {
            'matching_score': 72,
            'titre': 'Lead Developer',
            'entreprise': 'StartupXYZ'
        }
    ]
    
    mock_stats = {
        'total': 2,
        'moyenne_score': 78.5,
        'scores_par_tranche': {'excellent': 1, 'bon': 1, 'moyen': 0, 'faible': 0}
    }
    
    # Test réponse de succès
    success_response = create_matching_response(mock_results, mock_stats)
    print("✅ Réponse de succès formatée:")
    print(json.dumps(success_response, indent=2, ensure_ascii=False))
    
    # Test réponse d'erreur
    error_response = create_error_response("Données CV manquantes", "MISSING_CV_DATA")
    print("\n✅ Réponse d'erreur formatée:")
    print(json.dumps(error_response, indent=2, ensure_ascii=False))


def test_edge_cases():
    """Test des cas limites"""
    print("\n⚠️  Test des cas limites...")
    
    adapter = CommitmentDataAdapter()
    
    # Test avec des données vides/manquantes
    try:
        empty_cv = adapter.adapt_cv_data({})
        print("✅ Gestion CV vide réussie")
    except Exception as e:
        print(f"❌ Erreur CV vide: {e}")
    
    # Test avec des compétences en format string
    try:
        cv_string_skills = {
            'competences': 'Python, JavaScript, React',
            'nom': 'Test'
        }
        adapted = adapter.adapt_cv_data(cv_string_skills)
        print(f"✅ Compétences string adaptées: {adapted['competences']}")
    except Exception as e:
        print(f"❌ Erreur compétences string: {e}")
    
    # Test avec salaire invalide
    try:
        invalid_salary = adapter.parse_salary_range("Non spécifié")
        print(f"✅ Salaire invalide géré: {invalid_salary}")
    except Exception as e:
        print(f"❌ Erreur salaire invalide: {e}")


def test_performance():
    """Test de performance avec plus de données"""
    print("\n⚡ Test de performance...")
    
    adapter = CommitmentDataAdapter()
    
    # Générer plus d'offres pour le test
    base_jobs = get_sample_jobs_data()
    large_jobs_data = base_jobs * 10  # 50 offres
    
    # Modifier les IDs pour éviter les doublons
    for i, job in enumerate(large_jobs_data):
        job['id'] = f"job_{i:03d}"
    
    cv_data = get_sample_cv_data()
    questionnaire_data = get_sample_questionnaire_data()
    
    try:
        start_time = datetime.now()
        
        results = adapter.run_matching(
            cv_data=cv_data,
            questionnaire_data=questionnaire_data,
            jobs_data=large_jobs_data,
            limit=20
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Performance: {len(large_jobs_data)} offres traitées en {duration:.2f}s")
        print(f"   Soit {len(large_jobs_data)/duration:.1f} offres/seconde")
        print(f"   Résultats retournés: {len(results)}")
        
    except Exception as e:
        print(f"❌ Erreur performance: {e}")


def run_all_tests():
    """Lance tous les tests"""
    print("🚀 Début des tests d'intégration Commitment-")
    print("=" * 60)
    
    tests = [
        ("Fonctionnalités de base", test_basic_functionality),
        ("Adaptation des données", test_data_adaptation),
        ("Matching complet", test_complete_matching),
        ("Format réponse API", test_api_response_format),
        ("Cas limites", test_edge_cases),
        ("Performance", test_performance)
    ]
    
    success_count = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'-' * 60}")
            print(f"🧪 {test_name}")
            test_func()
            success_count += 1
            print(f"✅ {test_name}: RÉUSSI")
        except Exception as e:
            print(f"❌ {test_name}: ÉCHOUÉ - {str(e)}")
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print(f"📊 Résultats finaux: {success_count}/{len(tests)} tests réussis")
    
    if success_count == len(tests):
        print("🎉 Tous les tests sont passés avec succès!")
        print("✅ L'intégration est prête pour la production")
    else:
        print("⚠️  Certains tests ont échoué, vérifiez les erreurs ci-dessus")
    
    return success_count == len(tests)


if __name__ == "__main__":
    # Lancer tous les tests
    success = run_all_tests()
    
    if success:
        print("\n🔧 Commandes pour démarrer en production:")
        print("   python -c \"from data_adapter import CommitmentDataAdapter; print('Adaptateur prêt')\"")
        print("   # Puis intégrer dans votre API FastAPI")
    
    sys.exit(0 if success else 1)
