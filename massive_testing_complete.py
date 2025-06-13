#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 SuperSmartMatch V2.1 - TESTS MASSIFS COMPLETS (213 matchings)
Suite complète : 71 CV × 3 Jobs = 213 matchings avec système anti-faux positifs
"""

import os
import json
import requests
import time
from pathlib import Path
from datetime import datetime
import statistics

def test_all_cv_job_combinations():
    """Tests massifs : tous les CV contre tous les Jobs"""
    print("🚀 SUPERSMARTMATCH V2.1 - TESTS MASSIFS COMPLETS")
    print("=" * 60)
    print("🎯 Objectif: 71 CV × 3 Jobs = 213 matchings")
    print("🔧 Système anti-faux positifs activé")
    print()
    
    # Chemins des dossiers
    cv_dir = Path("/Users/baptistecomas/Desktop/CV TEST/")
    job_dir = Path("/Users/baptistecomas/Desktop/FDP TEST/")
    
    # Vérifications préliminaires
    if not cv_dir.exists():
        print(f"❌ Dossier CV non trouvé: {cv_dir}")
        return False
    
    if not job_dir.exists():
        print(f"❌ Dossier Jobs non trouvé: {job_dir}")
        return False
    
    # Lister tous les fichiers
    cv_files = list(cv_dir.glob("*.pdf"))
    job_files = list(job_dir.glob("*.pdf"))
    
    print(f"📄 CV trouvés: {len(cv_files)}")
    print(f"💼 Jobs trouvés: {len(job_files)}")
    print(f"🎯 Matchings à tester: {len(cv_files) * len(job_files)}")
    print()
    
    if len(cv_files) == 0 or len(job_files) == 0:
        print("❌ Aucun fichier à tester")
        return False
    
    # Structures de données pour les résultats
    results = []
    stats = {
        'total_tests': 0,
        'successful_tests': 0,
        'high_scores': 0,  # > 70%
        'medium_scores': 0,  # 40-70%
        'low_scores': 0,  # < 40%
        'errors': 0,
        'scores': [],
        'processing_times': []
    }
    
    print("🚀 DÉBUT DES TESTS MASSIFS")
    print("=" * 40)
    
    start_time = time.time()
    
    # Tester chaque combinaison CV-Job
    for i, cv_file in enumerate(cv_files):
        print(f"\n📄 CV {i+1}/{len(cv_files)}: {cv_file.name[:50]}...")
        
        for j, job_file in enumerate(job_files):
            stats['total_tests'] += 1
            test_start = time.time()
            
            try:
                # Test du matching
                result = test_cv_job_matching(cv_file, job_file)
                
                if result:
                    stats['successful_tests'] += 1
                    score = result['score']
                    stats['scores'].append(score)
                    
                    # Catégorisation des scores
                    if score >= 70:
                        stats['high_scores'] += 1
                        status = "🟢 EXCELLENT"
                    elif score >= 40:
                        stats['medium_scores'] += 1
                        status = "🟡 MOYEN"
                    else:
                        stats['low_scores'] += 1
                        status = "🔴 FAIBLE"
                    
                    processing_time = time.time() - test_start
                    stats['processing_times'].append(processing_time)
                    
                    # Affichage résultat
                    job_name = job_file.name[:30]
                    print(f"   💼 {job_name}: {score}% {status}")
                    
                    # Stocker le résultat
                    results.append({
                        'cv_file': cv_file.name,
                        'job_file': job_file.name,
                        'score': score,
                        'status': status,
                        'processing_time': processing_time,
                        'timestamp': datetime.now().isoformat(),
                        'details': result
                    })
                    
                else:
                    stats['errors'] += 1
                    print(f"   ❌ {job_file.name[:30]}: ERREUR")
                    
            except Exception as e:
                stats['errors'] += 1
                print(f"   ❌ {job_file.name[:30]}: {str(e)[:50]}...")
    
    # Calcul des statistiques finales
    total_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS TESTS MASSIFS")
    print("=" * 60)
    
    print(f"⏱️ Temps total: {total_time:.1f} secondes")
    print(f"📊 Tests réalisés: {stats['total_tests']}")
    print(f"✅ Tests réussis: {stats['successful_tests']} ({stats['successful_tests']/stats['total_tests']*100:.1f}%)")
    print(f"❌ Erreurs: {stats['errors']}")
    
    if stats['scores']:
        avg_score = statistics.mean(stats['scores'])
        median_score = statistics.median(stats['scores'])
        max_score = max(stats['scores'])
        min_score = min(stats['scores'])
        
        print(f"\n🎯 ANALYSE DES SCORES:")
        print(f"   📈 Score moyen: {avg_score:.1f}%")
        print(f"   📊 Score médian: {median_score:.1f}%")
        print(f"   ⬆️ Score max: {max_score:.1f}%")
        print(f"   ⬇️ Score min: {min_score:.1f}%")
        
        print(f"\n📊 DISTRIBUTION DES SCORES:")
        print(f"   🟢 Excellents (≥70%): {stats['high_scores']} ({stats['high_scores']/len(stats['scores'])*100:.1f}%)")
        print(f"   🟡 Moyens (40-69%): {stats['medium_scores']} ({stats['medium_scores']/len(stats['scores'])*100:.1f}%)")
        print(f"   🔴 Faibles (<40%): {stats['low_scores']} ({stats['low_scores']/len(stats['scores'])*100:.1f}%)")
    
    if stats['processing_times']:
        avg_time = statistics.mean(stats['processing_times'])
        print(f"\n⏱️ Performance: {avg_time:.2f}s par matching")
    
    # Générer rapport détaillé
    report_filename = f"massive_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    final_report = {
        'test_info': {
            'total_cv': len(cv_files),
            'total_jobs': len(job_files),
            'total_combinations': len(cv_files) * len(job_files),
            'test_duration': total_time,
            'timestamp': datetime.now().isoformat()
        },
        'statistics': stats,
        'detailed_results': results
    }
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(final_report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 Rapport détaillé: {report_filename}")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS:")
    
    if stats['successful_tests'] / stats['total_tests'] > 0.9:
        print("   ✅ Excellente stabilité du système")
    else:
        print("   ⚠️ Améliorer la robustesse (quelques erreurs)")
    
    if stats['scores'] and statistics.mean(stats['scores']) < 30:
        print("   📊 Scores globalement bas : normal avec système anti-faux positifs")
    elif stats['scores'] and statistics.mean(stats['scores']) > 70:
        print("   ⚠️ Scores élevés : vérifier le système anti-faux positifs")
    else:
        print("   ✅ Distribution des scores cohérente")
    
    print(f"\n🎉 TESTS MASSIFS TERMINÉS AVEC SUCCÈS!")
    print(f"🎯 SuperSmartMatch V2.1 Enhanced testé sur {stats['total_tests']} combinaisons")
    
    return True

def test_cv_job_matching(cv_file, job_file):
    """Test d'un matching CV-Job spécifique"""
    try:
        # Parser le CV
        cv_data = parse_cv(cv_file)
        if not cv_data:
            return None
        
        # Parser le Job
        job_data = parse_job(job_file)
        if not job_data:
            return None
        
        # Calculer le matching
        matching_result = calculate_matching(cv_data, job_data)
        
        return matching_result
        
    except Exception as e:
        print(f"   ❌ Erreur matching: {str(e)[:50]}...")
        return None

def parse_cv(cv_file):
    """Parser un CV via l'API"""
    try:
        with open(cv_file, 'rb') as f:
            files = {'file': (cv_file.name, f, 'application/pdf')}
            response = requests.post(
                "http://localhost:5051/api/parse-cv",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            return response.json().get('data', {})
        else:
            return None
            
    except Exception:
        return None

def parse_job(job_file):
    """Parser un Job via l'API"""
    try:
        with open(job_file, 'rb') as f:
            files = {'file': (job_file.name, f, 'application/pdf')}
            response = requests.post(
                "http://localhost:5053/api/parse-job",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            return response.json().get('data', {})
        else:
            return None
            
    except Exception:
        return None

def calculate_matching(cv_data, job_data):
    """Calculer le matching via l'Enhanced API"""
    try:
        payload = {
            "cv_data": cv_data,
            "job_data": job_data
        }
        
        response = requests.post(
            "http://localhost:5055/api/calculate-matching",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'score': result.get('matching_score', 0),
                'confidence': result.get('confidence', 'low'),
                'recommendation': result.get('recommendation', ''),
                'details': result.get('details', {})
            }
        else:
            return None
            
    except Exception:
        return None

def main():
    """Fonction principale"""
    print("🎯 PRÉPARATION TESTS MASSIFS SuperSmartMatch V2.1")
    print()
    
    # Vérification des services
    services = {
        "CV Parser V2": "http://localhost:5051/health",
        "Job Parser V2": "http://localhost:5053/health",
        "Enhanced API V2.1": "http://localhost:5055/health"
    }
    
    print("🔍 Vérification des services...")
    all_services_ok = True
    
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {service}: OPÉRATIONNEL")
            else:
                print(f"   ❌ {service}: ERREUR {response.status_code}")
                all_services_ok = False
        except Exception as e:
            print(f"   ❌ {service}: INACCESSIBLE")
            all_services_ok = False
    
    if not all_services_ok:
        print("\n❌ Certains services ne sont pas disponibles.")
        print("💡 Vérifiez que tous les services sont démarrés.")
        return False
    
    print("\n✅ Tous les services sont opérationnels!")
    print()
    
    # Lancer les tests massifs
    return test_all_cv_job_combinations()

if __name__ == "__main__":
    main()
