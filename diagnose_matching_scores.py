#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 DIAGNOSTIC ALGORITHME MATCHING - Pourquoi tous les scores sont à 0% ?
Analyser en détail pourquoi l'Enhanced API retourne systématiquement 0%
"""

import requests
import json
from pathlib import Path

def diagnose_matching_algorithm():
    """Diagnostiquer pourquoi tous les scores sont à 0%"""
    print("🔍 DIAGNOSTIC ALGORITHME MATCHING - SCORES À 0%")
    print("=" * 55)
    print("🎯 Objectif: Comprendre pourquoi tous les scores = 0%")
    print()
    
    # 1. Test avec un CV et Job spécifiques
    print("1️⃣ Test détaillé avec CV/Job spécifiques...")
    
    # Utiliser Hugo Salvat (qu'on connaît bien)
    cv_file = Path("/Users/baptistecomas/Desktop/CV TEST/SALVAT Hugo_CV.pdf")
    job_file = list(Path("/Users/baptistecomas/Desktop/FDP TEST/").glob("*.pdf"))[0]
    
    print(f"   📄 CV: {cv_file.name}")
    print(f"   💼 Job: {job_file.name}")
    
    # Parser les fichiers
    cv_data = parse_cv_detailed(cv_file)
    job_data = parse_job_detailed(job_file)
    
    if not cv_data or not job_data:
        print("   ❌ Erreur parsing")
        return False
    
    # 2. Analyser les données parsées
    print("\n2️⃣ Analyse des données parsées...")
    analyze_parsed_data(cv_data, job_data)
    
    # 3. Test du matching avec analyse détaillée
    print("\n3️⃣ Test matching avec analyse détaillée...")
    result = test_matching_detailed(cv_data, job_data)
    
    # 4. Test de tous les endpoints disponibles
    print("\n4️⃣ Test de tous les endpoints Enhanced API...")
    test_all_endpoints(cv_data, job_data)
    
    return True

def parse_cv_detailed(cv_file):
    """Parser CV avec analyse détaillée"""
    try:
        with open(cv_file, 'rb') as f:
            files = {'file': (cv_file.name, f, 'application/pdf')}
            response = requests.post(
                "http://localhost:5051/api/parse-cv",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            
            print(f"   ✅ CV parsé: {len(str(data))} caractères de données")
            print(f"   📝 Sections CV: {list(data.keys())}")
            
            # Analyser le contenu
            personal_info = data.get('personal_info', {})
            skills = data.get('skills', [])
            experiences = data.get('professional_experience', [])
            
            print(f"   👤 Nom: {personal_info.get('name', 'Non trouvé')}")
            print(f"   🛠️ Compétences: {len(skills)} trouvées")
            print(f"   💼 Expériences: {len(experiences)} trouvées")
            
            if skills:
                print(f"   📋 Premières compétences: {skills[:5]}")
            
            return data
        else:
            print(f"   ❌ Erreur CV: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception CV: {e}")
        return None

def parse_job_detailed(job_file):
    """Parser Job avec analyse détaillée"""
    try:
        with open(job_file, 'rb') as f:
            files = {'file': (job_file.name, f, 'application/pdf')}
            response = requests.post(
                "http://localhost:5053/api/parse-job",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json().get('data', {})
            
            print(f"   ✅ Job parsé: {len(str(data))} caractères de données")
            print(f"   📝 Sections Job: {list(data.keys())}")
            
            # Analyser le contenu
            job_info = data.get('job_info', {})
            missions = data.get('missions', [])
            requirements = data.get('requirements', {})
            
            print(f"   💼 Titre: {job_info.get('title', 'Non trouvé')}")
            print(f"   🎯 Missions: {len(missions)} trouvées")
            print(f"   📋 Requirements: {list(requirements.keys()) if requirements else 'Aucun'}")
            
            if missions:
                print(f"   📋 Premières missions: {missions[:3]}")
            
            return data
        else:
            print(f"   ❌ Erreur Job: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception Job: {e}")
        return None

def analyze_parsed_data(cv_data, job_data):
    """Analyser la structure des données parsées"""
    print("   🔍 Analyse structure des données...")
    
    # Analyser CV
    cv_skills = cv_data.get('skills', [])
    cv_technical = cv_data.get('technical_skills', [])
    cv_experiences = cv_data.get('professional_experience', [])
    
    print(f"   📄 CV:")
    print(f"      - Skills générales: {len(cv_skills)}")
    print(f"      - Skills techniques: {len(cv_technical)}")
    print(f"      - Expériences: {len(cv_experiences)}")
    
    # Analyser Job
    job_missions = job_data.get('missions', [])
    job_requirements = job_data.get('requirements', {})
    job_technical = job_requirements.get('technical_skills', []) if job_requirements else []
    
    print(f"   💼 Job:")
    print(f"      - Missions: {len(job_missions)}")
    print(f"      - Requirements: {job_requirements is not None}")
    print(f"      - Skills techniques requis: {len(job_technical)}")
    
    # Vérifier les points de matching potentiels
    cv_all_skills = set(cv_skills + cv_technical)
    job_all_skills = set(job_technical)
    
    common_skills = cv_all_skills.intersection(job_all_skills)
    print(f"   🎯 Skills en commun: {len(common_skills)}")
    if common_skills:
        print(f"      Exemples: {list(common_skills)[:3]}")
    
    # Vérifier si les données sont vides
    cv_empty = len(cv_skills) == 0 and len(cv_technical) == 0 and len(cv_experiences) == 0
    job_empty = len(job_missions) == 0 and len(job_technical) == 0
    
    if cv_empty:
        print("   ⚠️ ALERTE: Données CV quasi-vides")
    if job_empty:
        print("   ⚠️ ALERTE: Données Job quasi-vides")

def test_matching_detailed(cv_data, job_data):
    """Tester le matching avec analyse détaillée"""
    payload = {
        "cv_data": cv_data,
        "job_data": job_data
    }
    
    print(f"   📤 Payload size: {len(json.dumps(payload))} caractères")
    
    try:
        # Test endpoint enhanced
        response = requests.post(
            "http://localhost:5055/api/matching/enhanced",
            json=payload,
            timeout=15
        )
        
        print(f"   📡 Status: {response.status_code}")
        print(f"   📋 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Réponse reçue:")
            print(f"      📊 Score: {result.get('matching_score', result.get('score', 'N/A'))}")
            print(f"      🎯 Confidence: {result.get('confidence', 'N/A')}")
            print(f"      📝 Keys: {list(result.keys())}")
            
            # Analyser les détails du calcul
            details = result.get('details', {})
            if details:
                print(f"      🔍 Détails calcul: {list(details.keys())}")
                for key, value in details.items():
                    if isinstance(value, (int, float)):
                        print(f"         {key}: {value}")
            
            return result
        else:
            print(f"   ❌ Erreur: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return None

def test_all_endpoints(cv_data, job_data):
    """Tester tous les endpoints disponibles"""
    endpoints = [
        '/api/matching/enhanced',
        '/api/matching/complete', 
        '/api/matching/files',
        '/api/test/hugo-salvat'
    ]
    
    payload = {
        "cv_data": cv_data,
        "job_data": job_data
    }
    
    for endpoint in endpoints:
        print(f"   🔍 Test {endpoint}...")
        try:
            if endpoint == '/api/test/hugo-salvat':
                # Endpoint spécial sans payload
                response = requests.get(f"http://localhost:5055{endpoint}", timeout=10)
            else:
                response = requests.post(f"http://localhost:5055{endpoint}", 
                                       json=payload, timeout=15)
            
            print(f"      Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                score = result.get('matching_score', result.get('score', 'N/A'))
                print(f"      Score: {score}")
            else:
                print(f"      Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"      Exception: {str(e)[:50]}")

def main():
    """Fonction principale"""
    print("🎯 DIAGNOSTIC: Pourquoi tous les scores sont à 0% ?")
    print("Même les incompatibilités devraient avoir 10-20%...")
    print()
    
    success = diagnose_matching_algorithm()
    
    print("\n" + "=" * 55)
    print("📊 CONCLUSIONS:")
    print("1. Si données CV/Job vides → scores 0% normaux")
    print("2. Si données OK mais score 0% → algorithme défaillant")
    print("3. Si erreur API → endpoint mal configuré")
    
    print("\n🔧 SOLUTIONS POSSIBLES:")
    print("   1. Vérifier qualité extraction CV/Job")
    print("   2. Ajuster seuils algorithme matching")
    print("   3. Débugger Enhanced API internals")
    
    return success

if __name__ == "__main__":
    main()
