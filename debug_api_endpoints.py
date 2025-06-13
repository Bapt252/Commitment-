#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 SuperSmartMatch V2.1 Enhanced - Débogage API
Diagnostiquer et corriger les erreurs d'API
"""

import requests
import json
import os

def test_api_endpoints():
    """Tester tous les endpoints de l'Enhanced API"""
    print("🔍 DÉBOGAGE DES ENDPOINTS - Enhanced API V2.1")
    print("=" * 60)
    
    base_url = "http://localhost:5055"
    
    # 1. Test du health check
    print("1️⃣ TEST HEALTH CHECK")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoints disponibles:")
            for key, endpoint in data.get("endpoints", {}).items():
                print(f"   - {key}: {endpoint}")
        print()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    # 2. Test Hugo Salvat avec GET
    print("2️⃣ TEST HUGO SALVAT (GET)")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/api/test/hugo-salvat")
        print(f"GET Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ GET fonctionne!")
            print(f"Réponse: {response.text[:200]}...")
        else:
            print(f"❌ GET échoue: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Erreur GET: {e}")
    
    # 3. Test Hugo Salvat avec POST
    print("\n3️⃣ TEST HUGO SALVAT (POST)")
    print("-" * 30)
    try:
        response = requests.post(f"{base_url}/api/test/hugo-salvat")
        print(f"POST Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ POST fonctionne!")
        else:
            print(f"❌ POST échoue: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Erreur POST: {e}")
    
    # 4. Test des endpoints de matching
    print("\n4️⃣ TEST ENDPOINTS MATCHING")
    print("-" * 30)
    
    endpoints = [
        "/api/matching/complete",
        "/api/matching/enhanced", 
        "/api/matching/files"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Test {endpoint}:")
        
        # Test GET
        try:
            response = requests.get(f"{base_url}{endpoint}")
            print(f"   GET: {response.status_code}")
            if response.status_code != 404:
                print(f"   Réponse: {response.text[:100]}...")
        except Exception as e:
            print(f"   GET Erreur: {e}")
        
        # Test POST simple
        try:
            response = requests.post(f"{base_url}{endpoint}")
            print(f"   POST (vide): {response.status_code}")
            if response.status_code == 400:
                print(f"   Message: {response.text[:100]}...")
        except Exception as e:
            print(f"   POST Erreur: {e}")
    
    # 5. Test avec des fichiers réels
    print("\n5️⃣ TEST AVEC FICHIERS RÉELS")
    print("-" * 30)
    
    cv_path = "/Users/baptistecomas/Desktop/CV TEST/SALVAT Hugo_CV.pdf"
    job_path = "/Users/baptistecomas/Desktop/FDP TEST/Bcom HR  Opportunite Assistant  Facturation  CDI (1).pdf"
    
    if os.path.exists(cv_path) and os.path.exists(job_path):
        # Test format 1: chemins simples
        data1 = {
            'cv_path': cv_path,
            'job_path': job_path
        }
        
        try:
            response = requests.post(f"{base_url}/api/matching/files", json=data1)
            print(f"Format 1 (chemins): {response.status_code}")
            if response.status_code != 200:
                print(f"   Erreur: {response.text[:200]}")
        except Exception as e:
            print(f"Format 1 Erreur: {e}")
        
        # Test format 2: avec files upload
        try:
            with open(cv_path, 'rb') as cv_file, open(job_path, 'rb') as job_file:
                files = {
                    'cv_file': cv_file,
                    'job_file': job_file
                }
                response = requests.post(f"{base_url}/api/matching/files", files=files)
                print(f"Format 2 (upload): {response.status_code}")
                if response.status_code != 200:
                    print(f"   Erreur: {response.text[:200]}")
        except Exception as e:
            print(f"Format 2 Erreur: {e}")
        
        # Test format 3: données base64
        try:
            import base64
            with open(cv_path, 'rb') as f:
                cv_b64 = base64.b64encode(f.read()).decode()
            with open(job_path, 'rb') as f:
                job_b64 = base64.b64encode(f.read()).decode()
            
            data3 = {
                'cv_data': cv_b64,
                'job_data': job_b64,
                'cv_filename': 'SALVAT Hugo_CV.pdf',
                'job_filename': 'Opportunite Assistant Facturation.pdf'
            }
            
            response = requests.post(f"{base_url}/api/matching/files", json=data3)
            print(f"Format 3 (base64): {response.status_code}")
            if response.status_code == 200:
                print("✅ Format 3 fonctionne!")
                print(f"   Réponse: {response.text[:200]}...")
            else:
                print(f"   Erreur: {response.text[:200]}")
        except Exception as e:
            print(f"Format 3 Erreur: {e}")
    
    else:
        print("❌ Fichiers de test non trouvés")
    
    print(f"\n6️⃣ RECOMMANDATIONS")
    print("-" * 30)
    print("✅ Testez manuellement :")
    print(f"   curl -X GET {base_url}/api/test/hugo-salvat")
    print(f"   curl -X POST {base_url}/api/matching/files -H 'Content-Type: application/json' -d '{{}}'")

if __name__ == "__main__":
    test_api_endpoints()
