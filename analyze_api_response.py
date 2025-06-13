#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 ANALYSE RÉPONSE ENHANCED API - Structure exacte de la réponse
Voir exactement ce que retourne l'Enhanced API pour adapter le code
"""

import requests
import json
from pathlib import Path

def analyze_api_response():
    """Analyser en détail la réponse de l'Enhanced API"""
    print("🔍 ANALYSE RÉPONSE ENHANCED API")
    print("=" * 45)
    print("🎯 Objectif: Voir la structure exacte de la réponse")
    print()
    
    # Parser CV et Job
    cv_file = Path("/Users/baptistecomas/Desktop/CV TEST/SALVAT Hugo_CV.pdf")
    job_file = list(Path("/Users/baptistecomas/Desktop/FDP TEST/").glob("*.pdf"))[0]
    
    cv_data = parse_cv(cv_file)
    job_data = parse_job(job_file)
    
    if not cv_data or not job_data:
        print("❌ Erreur parsing")
        return False
    
    # Test tous les endpoints avec affichage complet
    endpoints = [
        '/api/matching/enhanced',
        '/api/matching/complete',
        '/api/test/hugo-salvat'
    ]
    
    payload = {
        "cv_data": cv_data,
        "job_data": job_data
    }
    
    for endpoint in endpoints:
        print(f"\n📡 ENDPOINT: {endpoint}")
        print("-" * 40)
        
        try:
            if endpoint == '/api/test/hugo-salvat':
                # GET sans payload
                response = requests.get(f"http://localhost:5055{endpoint}", timeout=15)
            else:
                # POST avec payload
                response = requests.post(f"http://localhost:5055{endpoint}", 
                                       json=payload, timeout=15)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Afficher la structure complète
                print(f"📊 RÉPONSE COMPLÈTE:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                
                # Analyser spécifiquement
                print(f"\n🔍 ANALYSE:")
                print(f"   📝 Keys: {list(result.keys())}")
                
                # Chercher où pourrait être le score
                for key, value in result.items():
                    if isinstance(value, dict):
                        print(f"   📂 {key}: {list(value.keys())}")
                        # Si c'est matching_analysis, creuser plus
                        if key == 'matching_analysis':
                            print(f"      🎯 matching_analysis contient:")
                            for sub_key, sub_value in value.items():
                                if isinstance(sub_value, (int, float)):
                                    print(f"         📊 {sub_key}: {sub_value}")
                                elif isinstance(sub_value, dict):
                                    print(f"         📂 {sub_key}: {list(sub_value.keys())}")
                                else:
                                    print(f"         📝 {sub_key}: {type(sub_value).__name__}")
                    elif isinstance(value, (int, float)):
                        print(f"   📊 {key}: {value}")
                    elif isinstance(value, list):
                        print(f"   📋 {key}: liste de {len(value)} éléments")
                    else:
                        print(f"   📝 {key}: {type(value).__name__}")
                
            else:
                print(f"❌ Erreur: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n" + "=" * 45)
    print("💡 OBJECTIF: Trouver où est le score final !")
    print("Probablement dans matching_analysis ou un sous-objet")

def parse_cv(cv_file):
    """Parser CV simple"""
    try:
        with open(cv_file, 'rb') as f:
            files = {'file': (cv_file.name, f, 'application/pdf')}
            response = requests.post("http://localhost:5051/api/parse-cv", files=files, timeout=30)
        return response.json().get('data', {}) if response.status_code == 200 else None
    except:
        return None

def parse_job(job_file):
    """Parser Job simple"""
    try:
        with open(job_file, 'rb') as f:
            files = {'file': (job_file.name, f, 'application/pdf')}
            response = requests.post("http://localhost:5053/api/parse-job", files=files, timeout=30)
        return response.json().get('data', {}) if response.status_code == 200 else None
    except:
        return None

if __name__ == "__main__":
    analyze_api_response()
