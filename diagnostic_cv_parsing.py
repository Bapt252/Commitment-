#!/usr/bin/env python3
"""
Diagnostic détaillé d'un CV spécifique
Pour comprendre pourquoi tous les domaines sont "unknown"
"""

import requests
import json
from pathlib import Path

def analyze_specific_cv(cv_name):
    """
    Analyse détaillée d'un CV spécifique
    """
    print(f"🔍 ANALYSE DÉTAILLÉE: {cv_name}")
    print("=" * 50)
    
    cv_folder = Path("/Users/baptistecomas/Desktop/CV TEST")
    cv_path = cv_folder / cv_name
    
    if not cv_path.exists():
        print(f"❌ CV non trouvé: {cv_path}")
        return
    
    # Test avec Enhanced API pour matching complet
    job_folder = Path("/Users/baptistecomas/Desktop/FDP TEST")
    job_files = list(job_folder.glob("*.pdf"))
    
    if not job_files:
        print("❌ Aucun job PDF trouvé")
        return
    
    job_path = job_files[0]  # Premier job PDF
    
    print(f"📄 CV: {cv_path.name}")
    print(f"💼 Job: {job_path.name}")
    
    try:
        with open(cv_path, 'rb') as cv_file, open(job_path, 'rb') as job_file:
            files = {
                'cv_file': (cv_path.name, cv_file, 'application/pdf'),
                'job_file': (job_path.name, job_file, 'application/pdf')
            }
            
            response = requests.post(
                'http://localhost:5055/api/matching/files',
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"\n📊 DONNÉES CV EXTRAITES:")
                print("-" * 30)
                cv_data = data.get('cv_data', {}).get('data', {})
                
                # Infos personnelles
                personal = cv_data.get('personal_info', {})
                print(f"👤 Nom: {personal.get('name', 'N/A')}")
                print(f"📧 Email: {personal.get('email', 'N/A')}")
                print(f"📱 Téléphone: {personal.get('phone', 'N/A')}")
                
                # Expérience
                experience = cv_data.get('professional_experience', [])
                print(f"\n💼 EXPÉRIENCE PROFESSIONNELLE: {len(experience)} entrée(s)")
                for i, exp in enumerate(experience[:3]):
                    print(f"   {i+1}. {exp}")
                
                # Compétences
                skills = cv_data.get('skills', [])
                print(f"\n🛠️ COMPÉTENCES: {len(skills)} trouvée(s)")
                for i, skill in enumerate(skills[:5]):
                    print(f"   {i+1}. {skill}")
                
                # Formations
                education = cv_data.get('education', [])
                print(f"\n🎓 FORMATIONS: {len(education)} trouvée(s)")
                for i, edu in enumerate(education[:3]):
                    print(f"   {i+1}. {edu}")
                
                # Métadonnées
                metadata = cv_data.get('_metadata', {})
                print(f"\n📋 MÉTADONNÉES:")
                print(f"   Longueur texte: {metadata.get('text_length', 0)} caractères")
                print(f"   Statut parsing: {metadata.get('processing_status', 'N/A')}")
                print(f"   Version parser: {metadata.get('parser_version', 'N/A')}")
                
                # Analyse des domaines
                print(f"\n🎯 ANALYSE DOMAINES:")
                matching = data.get('matching_analysis', {})
                domain_analysis = matching.get('domain_analysis', {})
                print(f"   CV Domaine: {domain_analysis.get('cv_domain', 'N/A')}")
                print(f"   Job Domaine: {domain_analysis.get('job_domain', 'N/A')}")
                print(f"   Compatibilité: {domain_analysis.get('compatibility_level', 'N/A')}")
                
                # Détails des missions
                missions_detail = matching.get('detailed_breakdown', {}).get('missions', {}).get('details', {})
                print(f"\n📋 MISSIONS ANALYSÉES:")
                print(f"   CV Missions filtrées: {len(missions_detail.get('filtered_cv_missions', []))}")
                print(f"   Job Missions filtrées: {len(missions_detail.get('filtered_job_missions', []))}")
                
                cv_missions = missions_detail.get('filtered_cv_missions', [])
                for i, mission in enumerate(cv_missions[:3]):
                    print(f"      CV {i+1}: {mission}")
                
                job_missions = missions_detail.get('filtered_job_missions', [])
                for i, mission in enumerate(job_missions[:3]):
                    print(f"      Job {i+1}: {mission}")
                
                # Score final
                total_score = matching.get('total_score', 0)
                print(f"\n🏆 SCORE FINAL: {total_score}%")
                
                # Recommandation
                recommendation = matching.get('recommendation', 'N/A')
                print(f"💡 RECOMMANDATION: {recommendation}")
                
            else:
                print(f"❌ Erreur API: {response.status_code}")
                print(f"📄 Response: {response.text[:300]}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

def compare_hugo_vs_dataset():
    """
    Comparaison Hugo Salvat vs CV du dataset
    """
    print(f"\n\n🆚 COMPARAISON HUGO SALVAT vs DATASET")
    print("=" * 50)
    
    # Test Hugo Salvat
    print(f"1️⃣ HUGO SALVAT (test intégré):")
    try:
        response = requests.get('http://localhost:5055/api/test/hugo-salvat')
        if response.status_code == 200:
            data = response.json()
            enhanced = data.get('enhanced_result', {})
            domain_analysis = enhanced.get('domain_analysis', {})
            print(f"   CV Domaine: {domain_analysis.get('cv_domain', 'N/A')}")
            print(f"   Job Domaine: {domain_analysis.get('job_domain', 'N/A')}")
            print(f"   Score: {enhanced.get('total_score', 'N/A')}%")
            print(f"   Compatibilité: {domain_analysis.get('compatibility_level', 'N/A')}")
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    # Test CV dataset
    print(f"\n2️⃣ CV DATASET (Vincent Lecocq - Contrôleur de gestion):")
    analyze_specific_cv("CV_Vincent_Lecocq_Controleur_de_gestion_Jan25.pdf")

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC CV PARSING - SuperSmartMatch V2.1")
    print("=" * 60)
    
    # Analyse d'un CV spécifique qui devrait avoir un domaine identifiable
    analyze_specific_cv("CV_Vincent_Lecocq_Controleur_de_gestion_Jan25.pdf")
    
    # Comparaison Hugo vs Dataset
    compare_hugo_vs_dataset()
    
    print(f"\n\n🎯 CONCLUSIONS:")
    print("1. Vérifier si le CV Parser extrait correctement les données")
    print("2. Identifier pourquoi les domaines restent 'unknown'")
    print("3. Comparer la qualité Hugo Salvat vs CV réels")
