#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 DIAGNOSTIC ENHANCED API V2.1 - Identifier le problème de matching
Test spécifique de l'API Enhanced pour comprendre pourquoi tous les matchings échouent
"""

import requests
import json
from pathlib import Path

def test_enhanced_api_detailed():
    """Test détaillé de l'Enhanced API pour identifier le problème"""
    print("🔍 DIAGNOSTIC ENHANCED API V2.1 - PROBLÈME MATCHING")
    print("=" * 55)
    
    # 1. Test health check
    print("1️⃣ Test Health Check Enhanced API...")
    try:
        response = requests.get("http://localhost:5055/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Health check OK")
            print(f"   Response: {response.json()}")
        else:
            print("   ❌ Health check échoué")
            return False
    except Exception as e:
        print(f"   ❌ Erreur health check: {e}")
        return False
    
    # 2. Test parsing CV individuel
    print("\n2️⃣ Test parsing CV individuel...")
    cv_file = Path("/Users/baptistecomas/Desktop/CV TEST/SALVAT Hugo_CV.pdf")
    
    if not cv_file.exists():
        print(f"   ❌ Fichier CV test non trouvé: {cv_file}")
        return False
    
    try:
        with open(cv_file, 'rb') as f:
            files = {'file': (cv_file.name, f, 'application/pdf')}
            response = requests.post(
                "http://localhost:5051/api/parse-cv",
                files=files,
                timeout=30
            )
        
        print(f"   Status CV: {response.status_code}")
        if response.status_code == 200:
            cv_data = response.json().get('data', {})
            print("   ✅ CV parsé avec succès")
            print(f"   📝 Clés CV: {list(cv_data.keys())}")
        else:
            print(f"   ❌ Erreur parsing CV: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur CV: {e}")
        return False
    
    # 3. Test parsing Job individuel
    print("\n3️⃣ Test parsing Job individuel...")
    job_file = Path("/Users/baptistecomas/Desktop/FDP TEST/Bcom HR  Opportunité de poste Assistant Juridique.pdf")
    
    if not job_file.exists():
        # Essayer avec les autres fichiers
        job_files = list(Path("/Users/baptistecomas/Desktop/FDP TEST/").glob("*.pdf"))
        if job_files:
            job_file = job_files[0]
        else:
            print("   ❌ Aucun fichier Job trouvé")
            return False
    
    try:
        with open(job_file, 'rb') as f:
            files = {'file': (job_file.name, f, 'application/pdf')}
            response = requests.post(
                "http://localhost:5053/api/parse-job",
                files=files,
                timeout=30
            )
        
        print(f"   Status Job: {response.status_code}")
        if response.status_code == 200:
            job_data = response.json().get('data', {})
            print("   ✅ Job parsé avec succès")
            print(f"   📝 Clés Job: {list(job_data.keys())}")
        else:
            print(f"   ❌ Erreur parsing Job: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur Job: {e}")
        return False
    
    # 4. Test API Enhanced - Calculate Matching
    print("\n4️⃣ Test Enhanced API Calculate Matching...")
    
    payload = {
        "cv_data": cv_data,
        "job_data": job_data
    }
    
    try:
        response = requests.post(
            "http://localhost:5055/api/calculate-matching",
            json=payload,
            timeout=15
        )
        
        print(f"   Status Matching: {response.status_code}")
        print(f"   Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Matching calculé avec succès")
            print(f"   📊 Score: {result.get('matching_score', 'N/A')}")
            print(f"   🎯 Confidence: {result.get('confidence', 'N/A')}")
            return True
        else:
            print(f"   ❌ Erreur matching:")
            print(f"   Status: {response.status_code}")
            print(f"   Text: {response.text}")
            
            # Essayer de voir si c'est un problème d'endpoint
            print(f"\n   🔍 Test endpoints alternatifs...")
            
            # Test endpoint racine
            try:
                root_response = requests.get("http://localhost:5055/", timeout=5)
                print(f"   Root endpoint status: {root_response.status_code}")
            except Exception as e:
                print(f"   Root endpoint error: {e}")
            
            # Test avec un payload simple
            try:
                simple_payload = {"test": "data"}
                simple_response = requests.post(
                    "http://localhost:5055/api/calculate-matching",
                    json=simple_payload,
                    timeout=5
                )
                print(f"   Simple payload status: {simple_response.status_code}")
                print(f"   Simple payload response: {simple_response.text[:200]}")
            except Exception as e:
                print(f"   Simple payload error: {e}")
            
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur requête matching: {e}")
        return False

def check_enhanced_api_endpoints():
    """Vérifier quels endpoints sont disponibles sur l'Enhanced API"""
    print("\n5️⃣ Vérification des endpoints Enhanced API...")
    
    base_url = "http://localhost:5055"
    endpoints_to_test = [
        "/",
        "/health", 
        "/api/",
        "/api/calculate-matching",
        "/docs",
        "/openapi.json"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   {endpoint}: {response.status_code}")
            if response.status_code == 200 and len(response.text) < 200:
                print(f"      Content: {response.text[:100]}")
        except Exception as e:
            print(f"   {endpoint}: ERREUR ({str(e)[:30]})")

def main():
    """Fonction principale"""
    print("🎯 OBJECTIF: Identifier pourquoi tous les 213 matchings échouent")
    print("Même si les services individuels fonctionnent...")
    print()
    
    success = test_enhanced_api_detailed()
    check_enhanced_api_endpoints()
    
    print("\n" + "=" * 55)
    if success:
        print("✅ Enhanced API fonctionne - Le problème est ailleurs")
        print("💡 Vérifier la logique du script de test massif")
    else:
        print("❌ Enhanced API défaillante - Problème identifié")
        print("💡 L'Enhanced API ne traite pas correctement les matchings")
        
    print("\n🔧 SOLUTIONS POSSIBLES:")
    print("   1. Redémarrer l'Enhanced API V2.1")
    print("   2. Vérifier l'endpoint /api/calculate-matching")
    print("   3. Tester avec des données simplifiées")
    
    return success

if __name__ == "__main__":
    main()
