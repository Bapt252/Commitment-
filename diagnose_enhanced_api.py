#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 Diagnostic Enhanced API V2.1 - Identifier pourquoi les scores sont à 0%
"""

import requests
import os
import json

def test_enhanced_api_matching():
    """Tester l'Enhanced API V2.1 en détail"""
    print("🔍 DIAGNOSTIC ENHANCED API V2.1 - Scores à 0%")
    print("=" * 55)
    
    api_url = "http://localhost:5055"
    
    # 1. Test du health check détaillé
    print("1️⃣ TEST HEALTH CHECK DÉTAILLÉ")
    print("-" * 35)
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Enhanced API healthy")
            print(f"Version: {data.get('version', 'unknown')}")
            print(f"Service: {data.get('service', 'unknown')}")
            print("Endpoints disponibles:")
            for key, endpoint in data.get('endpoints', {}).items():
                print(f"   - {key}: {endpoint}")
            print("Features:")
            for feature in data.get('features', []):
                print(f"   - {feature}")
        else:
            print(f"❌ API non healthy: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False
    
    # 2. Test avec des fichiers spécifiques
    print(f"\n2️⃣ TEST MATCHING AVEC FICHIERS RÉELS")
    print("-" * 35)
    
    cv_path = "/Users/baptistecomas/Desktop/CV TEST/SALVAT Hugo_CV.pdf"
    job_path = "/Users/baptistecomas/Desktop/FDP TEST/Bcom HR - Fiche de poste Assistant Facturation.pdf"
    
    if not os.path.exists(cv_path):
        print(f"❌ CV non trouvé: {cv_path}")
        # Essayer de trouver d'autres CV
        cv_dir = "/Users/baptistecomas/Desktop/CV TEST/"
        if os.path.exists(cv_dir):
            cv_files = [f for f in os.listdir(cv_dir) if f.endswith('.pdf')]
            if cv_files:
                cv_path = os.path.join(cv_dir, cv_files[0])
                print(f"✅ CV alternatif trouvé: {cv_files[0]}")
            else:
                print("❌ Aucun CV trouvé")
                return False
        else:
            print("❌ Répertoire CV non trouvé")
            return False
    
    if not os.path.exists(job_path):
        print(f"❌ Job non trouvé: {job_path}")
        # Essayer de trouver d'autres Jobs
        job_dir = "/Users/baptistecomas/Desktop/FDP TEST/"
        if os.path.exists(job_dir):
            job_files = [f for f in os.listdir(job_dir) if f.endswith('.pdf')]
            if job_files:
                job_path = os.path.join(job_dir, job_files[0])
                print(f"✅ Job alternatif trouvé: {job_files[0]}")
            else:
                print("❌ Aucun Job trouvé")
                return False
        else:
            print("❌ Répertoire Job non trouvé")
            return False
    
    # 3. Test de l'endpoint matching/files
    print(f"\n3️⃣ TEST ENDPOINT /api/matching/files")
    print("-" * 35)
    
    try:
        with open(cv_path, 'rb') as cv_file, open(job_path, 'rb') as job_file:
            files = {
                'cv_file': (os.path.basename(cv_path), cv_file, 'application/pdf'),
                'job_file': (os.path.basename(job_path), job_file, 'application/pdf')
            }
            
            response = requests.post(f"{api_url}/api/matching/files", 
                                   files=files, timeout=90)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Matching réussi!")
                print(f"📊 Score: {data.get('matching_score', 'N/A')}%")
                print(f"🔧 Version algo: {data.get('algorithm_version', 'N/A')}")
                print(f"🎯 Compatibilité: {data.get('domain_compatibility', 'N/A')}")
                print(f"🚨 Alertes: {len(data.get('alerts', []))}")
                
                # Détails du matching
                matching_details = data.get('matching_details', {})
                if matching_details:
                    print("\n📋 DÉTAILS DU MATCHING:")
                    for key, value in matching_details.items():
                        print(f"   {key}: {value}")
                
                # CV Data analysé
                cv_analysis = data.get('cv_analysis', {})
                if cv_analysis:
                    print(f"\n👤 ANALYSE CV:")
                    print(f"   Nom: {cv_analysis.get('personal_info', {}).get('name', 'N/A')}")
                    print(f"   Compétences: {len(cv_analysis.get('skills', []))}")
                    print(f"   Expériences: {len(cv_analysis.get('professional_experience', []))}")
                
                # Job Data analysé
                job_analysis = data.get('job_analysis', {})
                if job_analysis:
                    print(f"\n💼 ANALYSE JOB:")
                    print(f"   Titre: {job_analysis.get('job_info', {}).get('title', 'N/A')}")
                    print(f"   Missions: {len(job_analysis.get('missions', []))}")
                    print(f"   Skills requis: {len(job_analysis.get('requirements', {}).get('technical_skills', []))}")
                
                # Afficher la réponse complète si le score est 0
                if data.get('matching_score', 0) == 0:
                    print(f"\n⚠️ SCORE 0% - RÉPONSE COMPLÈTE:")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + "...")
                
            except json.JSONDecodeError:
                print(f"❌ Réponse non-JSON: {response.text[:200]}...")
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Détail: {response.text[:300]}...")
            
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    
    # 4. Test des autres endpoints
    print(f"\n4️⃣ TEST AUTRES ENDPOINTS")
    print("-" * 35)
    
    endpoints_to_test = [
        "/api/matching/complete",
        "/api/matching/enhanced"
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n🔍 Test {endpoint}:")
        try:
            with open(cv_path, 'rb') as cv_file, open(job_path, 'rb') as job_file:
                files = {
                    'cv_file': (os.path.basename(cv_path), cv_file, 'application/pdf'),
                    'job_file': (os.path.basename(job_path), job_file, 'application/pdf')
                }
                
                response = requests.post(f"{api_url}{endpoint}", 
                                       files=files, timeout=60)
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    score = data.get('matching_score', 0)
                    print(f"   Score: {score}%")
                    if score == 0:
                        print(f"   ⚠️ Score 0% aussi sur cet endpoint")
                except:
                    print(f"   ⚠️ Réponse non-JSON")
            else:
                print(f"   ❌ Erreur: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)[:50]}...")

    print(f"\n5️⃣ RECOMMANDATIONS")
    print("-" * 35)
    print("🔧 Problèmes possibles :")
    print("   1. L'algorithme de matching retourne toujours 0")
    print("   2. Les données CV/Job ne sont pas correctement parsées")
    print("   3. Les seuils de scoring sont trop élevés")
    print("   4. L'Enhanced API V2.1 a un bug de calcul")

if __name__ == "__main__":
    test_enhanced_api_matching()
