#!/usr/bin/env python3
"""
Diagnostic urgent pour les erreurs HTTP 400
"""

import requests
import json
from pathlib import Path

def test_enhanced_api_detailed():
    """Test détaillé de l'Enhanced API"""
    print("🔍 DIAGNOSTIC ENHANCED API")
    print("=" * 40)
    
    # Test de santé
    try:
        response = requests.get('http://localhost:5055/health')
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Version: {data.get('version')}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test Hugo Salvat (connu pour fonctionner)
    try:
        response = requests.get('http://localhost:5055/api/test/hugo-salvat')
        print(f"✅ Hugo Salvat test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Score: {data.get('total_score')}%")
        else:
            print(f"   ❌ Error: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Hugo Salvat test failed: {e}")
    
    # Test avec fichiers réels
    cv_folder = Path("/Users/baptistecomas/Desktop/CV TEST")
    job_folder = Path("/Users/baptistecomas/Desktop/FDP TEST")
    
    if not cv_folder.exists() or not job_folder.exists():
        print("❌ Dossiers non trouvés")
        return
    
    # Prendre le premier CV PDF
    cv_files = list(cv_folder.glob("*.pdf"))
    job_files = list(job_folder.glob("*.pdf"))  # D'abord chercher des PDF
    docx_files = list(job_folder.glob("*.docx"))  # Puis des DOCX
    
    print(f"\n📁 Fichiers trouvés:")
    print(f"   CV PDF: {len(cv_files)}")
    print(f"   Job PDF: {len(job_files)}")
    print(f"   Job DOCX: {len(docx_files)}")
    
    if cv_files and job_files:
        print(f"\n🧪 Test CV PDF + Job PDF:")
        test_file_matching(cv_files[0], job_files[0])
    
    if cv_files and docx_files:
        print(f"\n🧪 Test CV PDF + Job DOCX:")
        test_file_matching(cv_files[0], docx_files[0])

def test_file_matching(cv_path, job_path):
    """Test de matching avec gestion d'erreurs détaillée"""
    print(f"   CV: {cv_path.name}")
    print(f"   Job: {job_path.name}")
    
    try:
        with open(cv_path, 'rb') as cv_file, open(job_path, 'rb') as job_file:
            files = {
                'cv_file': (cv_path.name, cv_file, 'application/pdf' if cv_path.suffix == '.pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
                'job_file': (job_path.name, job_file, 'application/pdf' if job_path.suffix == '.pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
            }
            
            response = requests.post(
                'http://localhost:5055/api/matching/files',
                files=files,
                timeout=30
            )
            
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Score: {data.get('total_score', 'N/A')}%")
            else:
                print(f"   ❌ Error: {response.text[:300]}")
                
                # Essayer de parser comme JSON
                try:
                    error_data = response.json()
                    print(f"   🔍 Error details: {error_data}")
                except:
                    pass
                    
    except Exception as e:
        print(f"   ❌ Exception: {e}")

def test_individual_parsers():
    """Test des parsers individuels"""
    print(f"\n🧪 TEST PARSERS INDIVIDUELS:")
    
    cv_folder = Path("/Users/baptistecomas/Desktop/CV TEST")
    job_folder = Path("/Users/baptistecomas/Desktop/FDP TEST")
    
    if cv_folder.exists():
        cv_files = list(cv_folder.glob("*.pdf"))
        if cv_files:
            cv_path = cv_files[0]
            print(f"\n📄 Test CV Parser: {cv_path.name}")
            try:
                with open(cv_path, 'rb') as file:
                    files = {'file': file}
                    response = requests.post('http://localhost:5051/parse', files=files)
                    print(f"   Status: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"   ✅ Texte extrait: {len(data.get('text', ''))} caractères")
                    else:
                        print(f"   ❌ Error: {response.text[:200]}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")
    
    if job_folder.exists():
        job_files = list(job_folder.glob("*.docx"))
        if job_files:
            job_path = job_files[0]
            print(f"\n💼 Test Job Parser: {job_path.name}")
            try:
                with open(job_path, 'rb') as file:
                    files = {'file': file}
                    response = requests.post('http://localhost:5053/parse', files=files)
                    print(f"   Status: {response.status_code}")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"   ✅ Texte extrait: {len(data.get('text', ''))} caractères")
                    else:
                        print(f"   ❌ Error: {response.text[:200]}")
            except Exception as e:
                print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    test_enhanced_api_detailed()
    test_individual_parsers()
    
    print(f"\n🎯 ACTIONS RECOMMANDÉES:")
    print("1. Vérifier les logs du service Enhanced API V2.1")
    print("2. Redémarrer les services si nécessaire")
    print("3. Tester avec des fichiers PDF uniquement")
    print("4. Vérifier la configuration des content-types")
