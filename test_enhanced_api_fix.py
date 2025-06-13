#!/usr/bin/env python3
"""
🧪 Test Rapide - Validation de la correction Enhanced API V2.1
Vérifie que matching_score, confidence, recommendation sont présents
"""

import requests
import json
from datetime import datetime

def test_enhanced_api_fix():
    """Test de validation de la correction Enhanced API"""
    print("🧪 TEST RAPIDE - ENHANCED API V2.1 CORRIGÉE")
    print("=" * 50)
    print("🎯 Objectif: Vérifier que matching_score, confidence, recommendation")
    print("   sont maintenant présents dans la réponse JSON")
    print()
    
    # Données de test simulées
    test_cv_data = {
        "candidate_name": "Jean Dupont",
        "experience_years": 5,
        "technical_skills": ["Python", "JavaScript", "SQL", "Excel", "ERP"],
        "soft_skills": ["Communication", "Travail en équipe"],
        "professional_experience": [{
            "missions": [
                {"category": "development", "description": "Développement applications"},
                {"category": "analysis", "description": "Analyse de données"},
                {"category": "management", "description": "Gestion d'équipe"}
            ]
        }],
        "mission_summary": {"confidence_avg": 0.9}
    }
    
    test_job_data = {
        "job_info": {"title": "Développeur Full Stack"},
        "missions": [
            {"category": "development", "description": "Développement web"},
            {"category": "analysis", "description": "Analyse technique"}
        ],
        "requirements": {
            "technical_skills": ["Python", "JavaScript", "React"],
            "soft_skills": ["Communication"],
            "experience_level": "3-7 ans"
        }
    }
    
    # Test 1: Health check de la nouvelle API
    print("🔍 TEST 1: Health Check de l'API corrigée...")
    try:
        response = requests.get("http://localhost:5055/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("   ✅ Enhanced API accessible")
            print(f"   📋 Version: {health_data.get('version', 'Unknown')}")
            print(f"   📋 Service: {health_data.get('service', 'Unknown')}")
            
            # Vérifier les nouveaux endpoints
            endpoints = health_data.get('endpoints', {})
            if 'calculate_matching' in endpoints:
                print("   ✅ Endpoint /api/calculate-matching présent")
            else:
                print("   ❌ Endpoint /api/calculate-matching MANQUANT")
                return False
        else:
            print(f"   ❌ Enhanced API inaccessible (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Enhanced API non démarrée: {e}")
        print("   💡 Démarrez l'Enhanced API avec:")
        print("      python api-matching-enhanced-v2.1-fixed.py")
        return False
    
    # Test 2: Test de l'endpoint corrigé /api/calculate-matching
    print("\\n🔍 TEST 2: Endpoint /api/calculate-matching...")
    try:
        payload = {
            "cv_data": test_cv_data,
            "job_data": test_job_data
        }
        
        response = requests.post(
            "http://localhost:5055/api/calculate-matching",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Endpoint accessible et répond 200 OK")
            
            # Vérifier les champs requis
            required_fields = ['matching_score', 'confidence', 'recommendation']
            all_fields_present = True
            
            for field in required_fields:
                if field in data:
                    value = data[field]
                    print(f"   ✅ {field}: {value}")
                else:
                    print(f"   ❌ {field}: MANQUANT")
                    all_fields_present = False
            
            # Vérifier les types de données
            if all_fields_present:
                score = data['matching_score']
                confidence = data['confidence']
                recommendation = data['recommendation']
                
                if isinstance(score, (int, float)) and 0 <= score <= 100:
                    print(f"   ✅ Score valide: {score}%")
                else:
                    print(f"   ❌ Score invalide: {score}")
                    all_fields_present = False
                
                if confidence in ['low', 'medium', 'high']:
                    print(f"   ✅ Confidence valide: {confidence}")
                else:
                    print(f"   ❌ Confidence invalide: {confidence}")
                    all_fields_present = False
                
                if isinstance(recommendation, str) and len(recommendation) > 0:
                    print(f"   ✅ Recommendation valide: {recommendation[:50]}...")
                else:
                    print(f"   ❌ Recommendation invalide")
                    all_fields_present = False
            
            return all_fields_present
            
        else:
            print(f"   ❌ Erreur HTTP {response.status_code}: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur lors du test: {e}")
        return False

def test_alias_endpoint():
    """Test de l'endpoint alias /api/matching/enhanced"""
    print("\\n🔍 TEST 3: Endpoint alias /api/matching/enhanced...")
    
    test_payload = {
        "cv_data": {"candidate_name": "Test User", "technical_skills": ["Excel"]},
        "job_data": {"requirements": {"technical_skills": ["Excel", "Word"]}}
    }
    
    try:
        response = requests.post(
            "http://localhost:5055/api/matching/enhanced",
            json=test_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'matching_score' in data:
                print("   ✅ Endpoint alias fonctionne correctement")
                return True
            else:
                print("   ❌ Endpoint alias ne retourne pas matching_score")
                return False
        else:
            print(f"   ❌ Endpoint alias erreur {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur test alias: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 VALIDATION CORRECTION ENHANCED API V2.1")
    print("Tests de validation que la correction résout le problème")
    print()
    
    # Tests de validation
    test1_ok = test_enhanced_api_fix()
    test2_ok = test_alias_endpoint()
    
    print("\\n" + "=" * 50)
    print("📊 RÉSULTATS DE VALIDATION")
    print("=" * 50)
    
    if test1_ok and test2_ok:
        print("✅ VALIDATION RÉUSSIE!")
        print("🎯 L'Enhanced API retourne maintenant:")
        print("   - matching_score au niveau racine")
        print("   - confidence (low/medium/high)")
        print("   - recommendation (texte)")
        print()
        print("🚀 PROCHAINES ÉTAPES:")
        print("   1. Arrêter l'ancienne Enhanced API (Ctrl+C)")
        print("   2. Démarrer la nouvelle version:")
        print("      python api-matching-enhanced-v2.1-fixed.py")
        print("   3. Lancer les tests massifs:")
        print("      python massive_testing_complete.py")
        print()
        print("🎉 Les 213 tests massifs devraient maintenant afficher")
        print("   des scores réalistes au lieu de 0% !")
        
    else:
        print("❌ VALIDATION ÉCHOUÉE!")
        print("🔧 Vérifiez que la nouvelle Enhanced API est démarrée:")
        print("   python api-matching-enhanced-v2.1-fixed.py")
        
    return test1_ok and test2_ok

if __name__ == "__main__":
    main()
