#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 TEST RAPIDE JOB PARSER V2 - État actuel
Vérification rapide du problème title: null
"""

import requests
import os
from pathlib import Path

def quick_test_job_parser():
    """Test rapide pour confirmer le problème"""
    print("🔍 TEST RAPIDE JOB PARSER V2")
    print("=" * 40)
    
    # 1. Vérifier que le service répond
    print("1️⃣ Vérification du service...")
    try:
        response = requests.get("http://localhost:5053/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Service accessible")
            data = response.json()
            print(f"   📊 Status: {data.get('status', 'unknown')}")
            
            # Vérifier les parsers
            parsers = data.get('parsers_available', {})
            for parser, available in parsers.items():
                status = "✅" if available else "❌"
                print(f"   {status} {parser}: {available}")
        else:
            print(f"   ❌ Service erreur {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Service inaccessible: {str(e)}")
        return False
    
    # 2. Test avec un fichier réel
    print("\n2️⃣ Test avec fichier...")
    
    job_dir = Path("/Users/baptistecomas/Desktop/FDP TEST/")
    if not job_dir.exists():
        print(f"   ❌ Répertoire non trouvé: {job_dir}")
        return False
    
    job_files = list(job_dir.glob("*.pdf"))
    if not job_files:
        print(f"   ❌ Aucun PDF trouvé")
        return False
    
    test_file = job_files[0]
    print(f"   📋 Test avec: {test_file.name}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': (test_file.name, f, 'application/pdf')}
            response = requests.post(
                "http://localhost:5053/api/parse-job", 
                files=files, 
                timeout=60
            )
        
        print(f"   📡 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            job_info = data.get('data', {}).get('job_info', {})
            title = job_info.get('title', 'null')
            
            print(f"   📝 Titre extrait: '{title}'")
            
            if title and title != 'null' and title.strip():
                print("   ✅ Job Parser fonctionne correctement!")
                return True
            else:
                print("   ❌ PROBLÈME CONFIRMÉ: title = null ou vide")
                print("   🔧 Lancer fix_job_parser_v2.py pour corriger")
                return False
        else:
            print(f"   ❌ Erreur parsing: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur test: {str(e)}")
        return False

def show_system_status():
    """Afficher l'état complet du système"""
    print("\n🎯 ÉTAT SYSTÈME SUPERSMARTMATCH V2.1")
    print("=" * 50)
    
    services = {
        "CV Parser V2": "http://localhost:5051/health",
        "Job Parser V2": "http://localhost:5053/health", 
        "Enhanced API V2.1": "http://localhost:5055/health"
    }
    
    all_ok = True
    
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {service}: OPÉRATIONNEL")
            else:
                print(f"❌ {service}: ERREUR {response.status_code}")
                all_ok = False
        except Exception:
            print(f"❌ {service}: INACCESSIBLE")
            all_ok = False
    
    # Statistiques du projet
    print(f"\n📊 DONNÉES PROJET:")
    
    cv_dir = Path("/Users/baptistecomas/Desktop/CV TEST/")
    job_dir = Path("/Users/baptistecomas/Desktop/FDP TEST/")
    
    cv_count = len(list(cv_dir.glob("*.pdf"))) if cv_dir.exists() else 0
    job_count = len(list(job_dir.glob("*.pdf"))) if job_dir.exists() else 0
    total_matchings = cv_count * job_count
    
    print(f"   📄 CV disponibles: {cv_count}")
    print(f"   💼 Jobs disponibles: {job_count}")
    print(f"   🎯 Matchings possibles: {total_matchings}")
    
    if all_ok:
        print(f"\n🚀 SYSTÈME PRÊT POUR LES TESTS MASSIFS!")
    else:
        print(f"\n⚠️ CORRECTIONS NÉCESSAIRES AVANT TESTS MASSIFS")

if __name__ == "__main__":
    success = quick_test_job_parser()
    show_system_status()
    
    if not success:
        print(f"\n🔧 COMMANDE DE RÉPARATION:")
        print(f"python3 fix_job_parser_v2.py")
