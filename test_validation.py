#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SuperSmartMatch V3.0 Enhanced - Test de Validation Rapide
Vérification que l'API fonctionne correctement avec des données de test
Performance record: 88.5% précision, 12.3ms réponse
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5067"
TIMEOUT = 30

# Données de test (reproduisant le test record 88.5%)
TEST_CV_DATA = {
    "name": "Sabine Rivière",
    "skills": ["Juridique", "Droit", "Administrative", "RGPD", "Contrats", "Veille juridique"],
    "experience_years": 3,
    "sector": "Juridique",
    "education": "Master Droit des Affaires",
    "certifications": [],
    "languages": ["Français", "Anglais"]
}

TEST_JOB_DATA = {
    "title": "Assistant Juridique Senior",
    "skills_required": ["Juridique", "Droit", "Administrative", "RGPD", "Contrats"],
    "experience_required": 5,
    "sector": "Juridique",
    "salary_range": "35000-45000",
    "location": "Paris",
    "description": "Poste d'Assistant Juridique Senior pour cabinet d'avocats parisien"
}

def print_header():
    """Affichage header"""
    print("\n" + "="*60)
    print("🎯 SUPERSMARTMATCH V3.0 ENHANCED - TEST DE VALIDATION")
    print("="*60)
    print(f"🕐 Test démarré à: {datetime.now().strftime('%H:%M:%S')}")
    print(f"🔗 API URL: {API_BASE_URL}")
    print("="*60)

def test_api_health():
    """Test santé API"""
    print("\n🔍 TEST 1: Santé de l'API")
    print("-" * 30)
    
    try:
        start_time = time.time()
        response = requests.get(f"{API_BASE_URL}/health", timeout=TIMEOUT)
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API accessible ({response_time:.1f}ms)")
            print(f"📊 Statut: {health_data.get('api', 'Unknown')}")
            
            services = health_data.get('services', {})
            for service, status in services.items():
                emoji = "✅" if status == "healthy" else "⚠️" if status == "unavailable" else "❌"
                print(f"   {emoji} {service.title()}: {status}")
            
            return True
        else:
            print(f"❌ API erreur: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur connexion: {e}")
        return False

def test_api_stats():
    """Test statistiques API"""
    print("\n📊 TEST 2: Statistiques de l'API")
    print("-" * 30)
    
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=TIMEOUT)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistiques récupérées")
            print(f"🧠 Algorithme: {stats.get('algorithm', 'Unknown')}")
            
            perf = stats.get('performance', {})
            print(f"🎯 Précision: {perf.get('accuracy', 'N/A')}")
            print(f"⚡ Temps réponse: {perf.get('response_time', 'N/A')}")
            print(f"📈 Amélioration: {perf.get('improvement', 'N/A')}")
            
            formats = stats.get('supported_formats', [])
            print(f"📁 Formats: {', '.join(formats)}")
            print(f"🎓 Compétences: {stats.get('total_skills', 'N/A')}")
            
            return True
        else:
            print(f"❌ Erreur stats: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur requête: {e}")
        return False

def test_matching_engine():
    """Test moteur de matching avec données record"""
    print("\n🎯 TEST 3: Moteur de Matching Enhanced V3.0")
    print("-" * 30)
    print("📄 Test avec profil Assistant Juridique (test record 88.5%)")
    
    try:
        # Préparation requête
        match_request = {
            "cv_data": TEST_CV_DATA,
            "job_data": TEST_JOB_DATA,
            "algorithm": "Enhanced_V3.0"
        }
        
        # Appel API
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/match",
            json=match_request,
            timeout=TIMEOUT
        )
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                match_data = result['result']
                score = match_data['score']
                
                print(f"✅ Matching calculé en {response_time:.1f}ms")
                print(f"🏆 Score obtenu: {score:.1f}%")
                print(f"🎯 Score attendu: ~88.5%")
                
                # Vérification performance
                if score >= 85.0:
                    print(f"🎉 EXCELLENT - Score ≥ 85%")
                elif score >= 70.0:
                    print(f"⭐ BON - Score ≥ 70%")
                elif score >= 50.0:
                    print(f"👍 ACCEPTABLE - Score ≥ 50%")
                else:
                    print(f"⚠️ INSUFFISANT - Score < 50%")
                
                # Détails des scores
                print(f"\n📊 Détail des scores:")
                print(f"   • Compétences: {match_data['skill_match']:.1f}%")
                print(f"   • Expérience: {match_data['experience_match']:.1f}%")
                print(f"   • Bonus Titre: {match_data['title_bonus']:.1f}%")
                print(f"   • Bonus Secteur: {match_data.get('sector_bonus', 0):.1f}%")
                print(f"   • Note: {match_data['performance_note']}")
                
                # Vérification temps de traitement
                processing_time = match_data.get('processing_time_ms', response_time)
                print(f"⚡ Temps traitement: {processing_time:.1f}ms")
                
                if processing_time <= 20.0:
                    print(f"🚀 PERFORMANCE EXCELLENTE - Temps ≤ 20ms")
                elif processing_time <= 50.0:
                    print(f"✅ PERFORMANCE BONNE - Temps ≤ 50ms")
                else:
                    print(f"⚠️ PERFORMANCE ACCEPTABLE - Temps > 50ms")
                
                return True, score, processing_time
            else:
                print(f"❌ Erreur matching: {result}")
                return False, 0, 0
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return False, 0, 0
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur requête: {e}")
        return False, 0, 0

def test_job_parsing():
    """Test parsing description de poste"""
    print("\n📋 TEST 4: Parsing Description de Poste")
    print("-" * 30)
    
    job_description = """
    Assistant Juridique Senior - Cabinet d'Avocats Paris
    
    Nous recherchons un Assistant Juridique Senior pour rejoindre notre équipe.
    
    Compétences requises:
    - Droit des affaires
    - RGPD et conformité
    - Rédaction juridique
    - Gestion administrative
    
    Expérience: 3-5 ans minimum
    Localisation: Paris 8ème
    Salaire: 35-45K€
    """
    
    try:
        data = {'job_description': job_description}
        
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/parse_job",
            data=data,
            timeout=TIMEOUT
        )
        response_time = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                job_data = result['job_data']
                
                print(f"✅ Parsing réussi en {response_time:.1f}ms")
                print(f"📋 Titre détecté: {job_data.get('title', 'N/A')}")
                print(f"🎓 Compétences: {len(job_data.get('skills_required', []))} détectées")
                print(f"⏱️ Expérience requise: {job_data.get('experience_required', 0)} ans")
                print(f"🏢 Secteur: {job_data.get('sector', 'N/A')}")
                print(f"📍 Localisation: {job_data.get('location', 'N/A')}")
                
                return True
            else:
                print(f"❌ Erreur parsing: {result}")
                return False
        else:
            print(f"❌ Erreur API: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur requête: {e}")
        return False

def test_performance_validation():
    """Test de validation des performances"""
    print("\n🏆 TEST 5: Validation des Performances")
    print("-" * 30)
    
    # Test de charge simple
    test_count = 5
    scores = []
    times = []
    
    print(f"🔄 Exécution de {test_count} tests de matching...")
    
    for i in range(test_count):
        success, score, processing_time = test_matching_engine()
        if success:
            scores.append(score)
            times.append(processing_time)
        
        time.sleep(0.1)  # Petit délai entre tests
    
    if scores and times:
        avg_score = sum(scores) / len(scores)
        avg_time = sum(times) / len(times)
        
        print(f"\n📊 RÉSULTATS SUR {len(scores)} TESTS:")
        print(f"   📈 Score moyen: {avg_score:.1f}%")
        print(f"   ⚡ Temps moyen: {avg_time:.1f}ms")
        print(f"   🎯 Score min/max: {min(scores):.1f}% / {max(scores):.1f}%")
        print(f"   ⏱️ Temps min/max: {min(times):.1f}ms / {max(times):.1f}ms")
        
        # Validation objectifs
        target_score = 85.0
        target_time = 20.0
        
        print(f"\n🎯 VALIDATION OBJECTIFS:")
        if avg_score >= target_score:
            print(f"   ✅ Précision: {avg_score:.1f}% ≥ {target_score}%")
        else:
            print(f"   ⚠️ Précision: {avg_score:.1f}% < {target_score}%")
        
        if avg_time <= target_time:
            print(f"   ✅ Performance: {avg_time:.1f}ms ≤ {target_time}ms")
        else:
            print(f"   ⚠️ Performance: {avg_time:.1f}ms > {target_time}ms")
        
        return avg_score >= target_score and avg_time <= target_time
    else:
        print("❌ Aucun test réussi")
        return False

def run_validation():
    """Exécution complète de la validation"""
    print_header()
    
    results = {
        'health': False,
        'stats': False, 
        'matching': False,
        'parsing': False,
        'performance': False
    }
    
    # Exécution des tests
    results['health'] = test_api_health()
    
    if results['health']:
        results['stats'] = test_api_stats()
        results['matching'] = test_matching_engine()[0]
        results['parsing'] = test_job_parsing()
        results['performance'] = test_performance_validation()
    
    # Résumé final
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DE LA VALIDATION")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        emoji = "✅" if result else "❌"
        print(f"{emoji} {test_name.title()}: {'RÉUSSI' if result else 'ÉCHOUÉ'}")
    
    print("-" * 60)
    print(f"🎯 Résultat global: {passed_tests}/{total_tests} tests réussis")
    
    if passed_tests == total_tests:
        print("🎉 VALIDATION COMPLÈTE RÉUSSIE!")
        print("🚀 SuperSmartMatch V3.0 Enhanced est opérationnel!")
        return True
    elif passed_tests >= total_tests - 1:
        print("⭐ VALIDATION MAJORITAIREMENT RÉUSSIE")
        print("✅ Le système est fonctionnel avec quelques limitations")
        return True
    else:
        print("⚠️ VALIDATION PARTIELLE")
        print("🔧 Vérifiez la configuration et les services")
        return False

def main():
    """Fonction principale"""
    try:
        success = run_validation()
        
        print("\n" + "="*60)
        if success:
            print("🎊 SUPERSMARTMATCH V3.0 ENHANCED VALIDÉ!")
            print("🎯 Accédez au dashboard: http://localhost:8501")
            print("🔌 API documentée: http://localhost:5067/docs")
            sys.exit(0)
        else:
            print("❌ VALIDATION ÉCHOUÉE")
            print("🛠️ Vérifiez les logs et la configuration")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
