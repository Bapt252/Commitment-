#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 Diagnostic Job Parser V2 - Identifier l'erreur 500
Tester directement le Job Parser V2 pour comprendre le problème
"""

import requests
import os
import json

def test_job_parser_directly():
    """Tester le Job Parser V2 directement"""
    print("🔍 DIAGNOSTIC JOB PARSER V2 - Erreur 500")
    print("=" * 50)
    
    job_parser_url = "http://localhost:5053"
    job_dir = "/Users/baptistecomas/Desktop/FDP TEST/"
    
    # 1. Test du health check
    print("1️⃣ TEST HEALTH CHECK")
    print("-" * 30)
    try:
        response = requests.get(f"{job_parser_url}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Service healthy")
            print(f"Parsers disponibles: {data.get('parsers_available', {})}")
        else:
            print(f"❌ Service non healthy: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion: {e}")
        return False
    
    # 2. Lister les fichiers Job disponibles
    print(f"\n2️⃣ FICHIERS JOB DISPONIBLES")
    print("-" * 30)
    
    if not os.path.exists(job_dir):
        print(f"❌ Répertoire non trouvé: {job_dir}")
        return False
    
    job_files = [f for f in os.listdir(job_dir) if f.endswith('.pdf')]
    print(f"📊 {len(job_files)} fichiers PDF trouvés:")
    
    for i, job_file in enumerate(job_files[:5]):  # Afficher les 5 premiers
        job_path = os.path.join(job_dir, job_file)
        size = os.path.getsize(job_path)
        print(f"   {i+1}. {job_file} ({size} bytes)")
    
    if len(job_files) > 5:
        print(f"   ... et {len(job_files) - 5} autres")
    
    # 3. Tester le Job Parser V2 avec différents fichiers
    print(f"\n3️⃣ TEST PARSING DIRECT")
    print("-" * 30)
    
    test_files = job_files[:3]  # Tester les 3 premiers
    
    for i, job_file in enumerate(test_files):
        print(f"\n🔍 Test {i+1}/3: {job_file}")
        job_path = os.path.join(job_dir, job_file)
        
        if not os.path.exists(job_path):
            print(f"   ❌ Fichier manquant: {job_path}")
            continue
        
        try:
            # Test avec upload de fichier
            with open(job_path, 'rb') as f:
                files = {'file': (job_file, f, 'application/pdf')}
                response = requests.post(f"{job_parser_url}/api/parse-job", 
                                       files=files, timeout=60)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Parsing réussi!")
                    print(f"   📝 Status: {data.get('status', 'unknown')}")
                    
                    job_data = data.get('data', {})
                    if job_data:
                        print(f"   💼 Titre Job: {job_data.get('job_info', {}).get('title', 'Non détecté')}")
                        print(f"   🎯 Missions: {len(job_data.get('missions', []))}")
                        print(f"   📏 Texte: {job_data.get('_metadata', {}).get('text_length', 0)} caractères")
                    
                except json.JSONDecodeError:
                    print(f"   ⚠️ Réponse non-JSON: {response.text[:100]}...")
                    
            else:
                print(f"   ❌ Erreur {response.status_code}")
                print(f"   Détail: {response.text[:200]}...")
                
        except requests.Timeout:
            print(f"   ❌ Timeout (>60s)")
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)[:100]}...")
    
    # 4. Test avec un fichier spécifique problématique
    print(f"\n4️⃣ TEST FICHIER SPÉCIFIQUE")
    print("-" * 30)
    
    # Chercher le fichier "Opportunite" qui pose problème
    problematic_file = None
    for job_file in job_files:
        if "Opportunite" in job_file:
            problematic_file = job_file
            break
    
    if problematic_file:
        print(f"🎯 Test fichier problématique: {problematic_file}")
        job_path = os.path.join(job_dir, problematic_file)
        
        try:
            # Informations sur le fichier
            size = os.path.getsize(job_path)
            print(f"   📏 Taille: {size} bytes")
            
            # Test de parsing
            with open(job_path, 'rb') as f:
                files = {'file': (problematic_file, f, 'application/pdf')}
                response = requests.post(f"{job_parser_url}/api/parse-job", 
                                       files=files, timeout=90)
            
            print(f"   Status: {response.status_code}")
            print(f"   Réponse: {response.text[:300]}...")
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
    
    print(f"\n5️⃣ RECOMMANDATIONS")
    print("-" * 30)
    print("🔧 Actions possibles :")
    print("   1. Vérifier les logs du Job Parser V2")
    print("   2. Redémarrer le Job Parser V2")
    print("   3. Tester avec un fichier PDF simple")
    print("   4. Vérifier l'espace disque dans /tmp/")
    
    # Test espace disque
    import shutil
    try:
        total, used, free = shutil.disk_usage("/tmp")
        print(f"\n💾 Espace disque /tmp:")
        print(f"   Total: {total // (1024**3)} GB")
        print(f"   Libre: {free // (1024**3)} GB")
        if free < 1024**3:  # < 1GB
            print(f"   ⚠️ Peu d'espace libre!")
    except:
        pass

if __name__ == "__main__":
    test_job_parser_directly()
