#!/usr/bin/env python3
"""
Diagnostic ultra-détaillé des réponses API
Pour comprendre pourquoi les scores ne s'affichent pas
"""

import requests
import json
from pathlib import Path

def test_api_response_detailed():
    """
    Test détaillé des réponses API avec affichage complet
    """
    print("🔍 DIAGNOSTIC DÉTAILLÉ DES RÉPONSES API")
    print("=" * 50)
    
    cv_folder = Path("/Users/baptistecomas/Desktop/CV TEST")
    job_folder = Path("/Users/baptistecomas/Desktop/FDP TEST")
    
    # Prendre les premiers fichiers PDF
    cv_files = list(cv_folder.glob("*.pdf"))
    job_files = list(job_folder.glob("*.pdf"))
    
    if not cv_files or not job_files:
        print("❌ Fichiers PDF non trouvés")
        return
    
    cv_path = cv_files[0]  # Cv_Mohamed_Ouadhane.pdf
    job_path = job_files[0]  # Assistant Juridique
    
    print(f"📄 CV: {cv_path.name}")
    print(f"💼 Job: {job_path.name}")
    
    try:
        with open(cv_path, 'rb') as cv_file, open(job_path, 'rb') as job_file:
            files = {
                'cv_file': (cv_path.name, cv_file, 'application/pdf'),
                'job_file': (job_path.name, job_file, 'application/pdf')
            }
            
            print(f"\n🚀 Envoi de la requête...")
            response = requests.post(
                'http://localhost:5055/api/matching/files',
                files=files,
                timeout=30
            )
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📋 Headers: {dict(response.headers)}")
            print(f"📄 Raw Response Text:")
            print("-" * 30)
            print(response.text)
            print("-" * 30)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"\n✅ JSON parsé avec succès:")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    
                    # Vérifier les clés disponibles
                    print(f"\n🔑 Clés disponibles:")
                    for key in data.keys():
                        print(f"   - {key}: {type(data[key])}")
                    
                    # Chercher le score
                    if 'total_score' in data:
                        print(f"\n🎯 Score trouvé: {data['total_score']}")
                    else:
                        print(f"\n❌ Pas de clé 'total_score' trouvée")
                        # Chercher d'autres clés potentielles
                        for key, value in data.items():
                            if 'score' in key.lower():
                                print(f"   Clé potentielle: {key} = {value}")
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Erreur JSON: {e}")
                    print("La réponse n'est pas du JSON valide")
            else:
                print(f"❌ Erreur HTTP {response.status_code}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_hugo_salvat_detailed():
    """
    Test détaillé du endpoint Hugo Salvat
    """
    print(f"\n\n🧪 TEST HUGO SALVAT DÉTAILLÉ")
    print("=" * 40)
    
    try:
        response = requests.get('http://localhost:5055/api/test/hugo-salvat')
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Raw Response:")
        print("-" * 20)
        print(response.text)
        print("-" * 20)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"\n✅ JSON Hugo Salvat:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print(f"❌ Réponse non-JSON")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_all_three_jobs():
    """
    Test avec les 3 jobs PDF disponibles
    """
    print(f"\n\n🧪 TEST AVEC LES 3 JOBS PDF")
    print("=" * 40)
    
    cv_folder = Path("/Users/baptistecomas/Desktop/CV TEST")
    job_folder = Path("/Users/baptistecomas/Desktop/FDP TEST")
    
    cv_files = list(cv_folder.glob("*.pdf"))
    job_files = list(job_folder.glob("*.pdf"))
    
    if not cv_files or not job_files:
        print("❌ Fichiers non trouvés")
        return
    
    cv_path = cv_files[0]  # Cv_Mohamed_Ouadhane.pdf
    
    for i, job_path in enumerate(job_files):
        print(f"\n📄 Test {i+1}/3: {job_path.name}")
        
        try:
            with open(cv_path, 'rb') as cv_file, open(job_path, 'rb') as job_file:
                files = {
                    'cv_file': (cv_path.name, cv_file, 'application/pdf'),
                    'job_file': (job_path.name, job_file, 'application/pdf')
                }
                
                response = requests.post(
                    'http://localhost:5055/api/matching/files',
                    files=files,
                    timeout=15
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        score = data.get('total_score', 'N/A')
                        print(f"   ✅ Score: {score}")
                        
                        # Afficher quelques détails
                        if 'domain_score' in data:
                            print(f"   📊 Domain: {data['domain_score']}")
                        if 'mission_score' in data:
                            print(f"   🎯 Mission: {data['mission_score']}")
                            
                    except:
                        print(f"   ❌ Réponse non-JSON")
                        print(f"   📄 Raw: {response.text[:100]}...")
                else:
                    print(f"   ❌ Erreur {response.status_code}")
                    print(f"   📄 Error: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_api_response_detailed()
    test_hugo_salvat_detailed()
    test_all_three_jobs()
    
    print(f"\n\n🎯 CONCLUSIONS:")
    print("1. Vérifier si l'API retourne la bonne structure JSON")
    print("2. Identifier pourquoi les scores ne s'affichent pas")
    print("3. Comprendre si le problème vient de l'API ou du parsing")
