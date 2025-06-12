#!/usr/bin/env python3
"""
Diagnostic et correction du système de classification des domaines
Le problème : missions extraites mais domaines non identifiés
"""

import requests
import json
from pathlib import Path

def test_domain_classification():
    """
    Test spécifique du système de classification des domaines
    """
    print("🔍 DIAGNOSTIC SYSTÈME DE CLASSIFICATION DES DOMAINES")
    print("=" * 60)
    
    # Test avec Vincent Lecocq (missions comptabilité claires)
    cv_folder = Path("/Users/baptistecomas/Desktop/CV TEST")
    cv_path = cv_folder / "CV_Vincent_Lecocq_Controleur_de_gestion_Jan25.pdf"
    
    job_folder = Path("/Users/baptistecomas/Desktop/FDP TEST")
    job_files = list(job_folder.glob("*.pdf"))
    
    if not cv_path.exists() or not job_files:
        print("❌ Fichiers non trouvés")
        return
    
    # Test avec job Facturation (devrait matcher)
    facturation_job = None
    for job in job_files:
        if "Facturation" in job.name:
            facturation_job = job
            break
    
    if not facturation_job:
        facturation_job = job_files[0]
    
    print(f"📄 CV: {cv_path.name}")
    print(f"💼 Job: {facturation_job.name}")
    
    try:
        with open(cv_path, 'rb') as cv_file, open(facturation_job, 'rb') as job_file:
            files = {
                'cv_file': (cv_path.name, cv_file, 'application/pdf'),
                'job_file': (facturation_job.name, job_file, 'application/pdf')
            }
            
            response = requests.post(
                'http://localhost:5055/api/matching/files',
                files=files,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"\n🔍 ANALYSE DÉTAILLÉE DU PROBLÈME:")
                print("-" * 40)
                
                # Missions CV brutes
                cv_data = data.get('cv_data', {}).get('data', {})
                experience = cv_data.get('professional_experience', [])
                
                print(f"📋 MISSIONS CV BRUTES:")
                for exp in experience:
                    missions = exp.get('missions', [])
                    for mission in missions:
                        print(f"   - {mission}")
                
                # Missions Job brutes
                job_data = data.get('job_data', {}).get('data', {})
                job_missions = job_data.get('missions', [])
                
                print(f"\n💼 MISSIONS JOB BRUTES:")
                for mission in job_missions:
                    print(f"   - {mission}")
                
                # Analyse du matching
                matching = data.get('matching_analysis', {})
                missions_detail = matching.get('detailed_breakdown', {}).get('missions', {}).get('details', {})
                
                print(f"\n🎯 APRÈS FILTRAGE/CLASSIFICATION:")
                print(f"   CV Missions filtrées: {missions_detail.get('filtered_cv_missions', [])}")
                print(f"   Job Missions filtrées: {missions_detail.get('filtered_job_missions', [])}")
                
                # Détails de domaines
                cv_domain_details = missions_detail.get('cv_domain_details', {})
                job_domain_details = missions_detail.get('job_domain_details', {})
                
                print(f"\n📊 DÉTAILS CLASSIFICATION CV:")
                if cv_domain_details:
                    scores = cv_domain_details.get('scores', {})
                    for domain, score in scores.items():
                        if score > 0:
                            print(f"   {domain}: {score} points")
                    print(f"   Domaine choisi: {missions_detail.get('cv_domain', 'unknown')}")
                else:
                    print("   ❌ Aucun détail de classification CV")
                
                print(f"\n📊 DÉTAILS CLASSIFICATION JOB:")
                if job_domain_details:
                    scores = job_domain_details.get('scores', {})
                    for domain, score in scores.items():
                        if score > 0:
                            print(f"   {domain}: {score} points")
                    print(f"   Domaine choisi: {missions_detail.get('job_domain', 'unknown')}")
                else:
                    print("   ❌ Aucun détail de classification Job")
                
                # Score final
                print(f"\n🏆 RÉSULTAT FINAL:")
                print(f"   Score total: {matching.get('total_score', 0)}%")
                print(f"   Recommandation: {matching.get('recommendation', 'N/A')}")
                
            else:
                print(f"❌ Erreur API: {response.status_code}")
                print(f"Response: {response.text[:300]}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

def compare_working_vs_broken():
    """
    Comparaison entre Hugo Salvat (qui marche) et CV réels (cassés)
    """
    print(f"\n\n🆚 COMPARAISON SYSTÈME FONCTIONNEL vs CASSÉ")
    print("=" * 60)
    
    print(f"1️⃣ HUGO SALVAT (FONCTIONNE) :")
    try:
        response = requests.get('http://localhost:5055/api/test/hugo-salvat')
        if response.status_code == 200:
            data = response.json()
            enhanced = data.get('enhanced_result', {})
            
            # Détails des missions
            missions_detail = enhanced.get('detailed_breakdown', {}).get('missions', {}).get('details', {})
            
            print(f"   CV Missions filtrées: {len(missions_detail.get('filtered_cv_missions', []))}")
            for mission in missions_detail.get('filtered_cv_missions', [])[:3]:
                print(f"      - {mission}")
            
            print(f"   Job Missions filtrées: {len(missions_detail.get('filtered_job_missions', []))}")
            for mission in missions_detail.get('filtered_job_missions', [])[:3]:
                print(f"      - {mission}")
            
            # Domaines identifiés
            domain_analysis = enhanced.get('domain_analysis', {})
            print(f"   ✅ CV Domaine: {domain_analysis.get('cv_domain')}")
            print(f"   ✅ Job Domaine: {domain_analysis.get('job_domain')}")
            print(f"   ✅ Score: {enhanced.get('total_score')}%")
            
        else:
            print(f"   ❌ Erreur: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    
    print(f"\n2️⃣ VINCENT LECOCQ (CASSÉ) :")
    print(f"   ❌ CV Missions filtrées: 0 (alors qu'elles existent !)")
    print(f"   ❌ Job Missions filtrées: 0")
    print(f"   ❌ CV Domaine: unknown")
    print(f"   ❌ Job Domaine: unknown")
    print(f"   ❌ Score: 22%")

def diagnose_classification_algorithm():
    """
    Test pour comprendre pourquoi l'algorithme de classification échoue
    """
    print(f"\n\n🔬 DIAGNOSTIC ALGORITHME DE CLASSIFICATION")
    print("=" * 60)
    
    print(f"🎯 MISSIONS VINCENT LECOCQ ANALYSÉES:")
    missions = [
        "Facturation clients et suivi des règlements",
        "Saisie des écritures comptables dans Oracle", 
        "Contrôle et validation des comptes",
        "Gestion des relances clients",
        "Reporting mensuel et indicateurs de performance"
    ]
    
    # Mots-clés attendus par domaine
    domains_keywords = {
        'facturation': ['facturation', 'facture', 'client'],
        'comptabilité': ['comptable', 'comptabilité', 'écritures', 'comptes'],
        'contrôle': ['contrôle', 'validation', 'vérification'],
        'gestion': ['gestion', 'suivi'],
        'reporting': ['reporting', 'indicateurs', 'performance']
    }
    
    print(f"\n📊 ANALYSE MANUELLE DES MISSIONS:")
    for mission in missions:
        print(f"\n   Mission: '{mission}'")
        mission_lower = mission.lower()
        
        for domain, keywords in domains_keywords.items():
            matches = [kw for kw in keywords if kw in mission_lower]
            if matches:
                print(f"      ✅ {domain}: {matches}")
    
    print(f"\n💡 CONCLUSION:")
    print(f"   Vincent Lecocq devrait être classé:")
    print(f"   ✅ Domaine principal: COMPTABILITÉ (écritures comptables, comptes)")
    print(f"   ✅ Domaine secondaire: FACTURATION (facturation clients)")
    print(f"   ✅ Domaine tertiaire: CONTRÔLE (contrôle et validation)")
    
    print(f"\n🚨 PROBLÈME IDENTIFIÉ:")
    print(f"   Le système de classification ne détecte pas ces mots-clés évidents !")

if __name__ == "__main__":
    test_domain_classification()
    compare_working_vs_broken()
    diagnose_classification_algorithm()
    
    print(f"\n\n🎯 ACTIONS URGENTES REQUISES:")
    print("1. 🔧 CORRIGER le système de classification des domaines")
    print("2. 🔍 VÉRIFIER pourquoi les missions ne sont pas filtrées")
    print("3. ⚙️ AJUSTER les mots-clés de reconnaissance des domaines")
    print("4. 🧪 TESTER avec des mots-clés plus permissifs")
    print("5. 🚀 RELANCER les tests une fois corrigé")
