#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 SuperSmartMatch V2.1 Enhanced - Tests Massifs COMPLETS
Objectif: 2,812 matchings (74 CV × 38 Jobs) avec anti-faux positifs
"""

import os
import requests
import time
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

class SuperSmartMatchMassiveTesting:
    def __init__(self):
        self.cv_dir = "/Users/baptistecomas/Desktop/CV TEST/"
        self.job_dir = "/Users/baptistecomas/Desktop/FDP TEST/"
        self.api_base = "http://localhost:5055"
        self.results = []
        
    def validate_services(self):
        """Vérifier que tous les services sont opérationnels"""
        print("🔍 VÉRIFICATION DES SERVICES")
        print("-" * 40)
        
        services = [
            ("CV Parser V2", "http://localhost:5051/health"),
            ("Job Parser V2", "http://localhost:5053/health"),
            ("Enhanced API V2.1", "http://localhost:5055/health")
        ]
        
        all_healthy = True
        for name, url in services:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200 and "healthy" in response.text:
                    print(f"   ✅ {name}: Opérationnel")
                else:
                    print(f"   ❌ {name}: Problème de santé")
                    all_healthy = False
            except:
                print(f"   ❌ {name}: Inaccessible")
                all_healthy = False
                
        return all_healthy
    
    def get_files(self):
        """Récupérer les listes de fichiers CV et Jobs"""
        cv_files = [f for f in os.listdir(self.cv_dir) if f.endswith('.pdf')]
        job_files = [f for f in os.listdir(self.job_dir) if f.endswith('.pdf')]
        
        print(f"📊 CV trouvés: {len(cv_files)}")
        print(f"📊 Jobs trouvés: {len(job_files)}")
        print(f"🎯 Total matchings: {len(cv_files)} × {len(job_files)} = {len(cv_files) * len(job_files)}")
        
        return cv_files, job_files
    
    def test_hugo_salvat_validation(self):
        """Test spécifique Hugo Salvat pour validation anti-faux positifs"""
        print("\n🧪 VALIDATION HUGO SALVAT - Anti-faux positifs")
        print("-" * 50)
        
        try:
            response = requests.post(f"{self.api_base}/api/test/hugo-salvat", timeout=30)
            if response.status_code == 200:
                data = response.json()
                score = data.get('matching_score', 0)
                print(f"   ✅ Hugo Salvat vs Facturation: {score}%")
                if score <= 30:
                    print(f"   ✅ Rejet correct (score ≤ 30%)")
                    return True
                else:
                    print(f"   ⚠️ Score trop élevé pour un faux positif!")
                    return False
            else:
                print(f"   ❌ Erreur API: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
            return False
    
    def run_sample_batch(self, sample_size=25):
        """Tester un échantillon pour validation"""
        print(f"\n🔬 TEST ÉCHANTILLON ({sample_size} matchings)")
        print("-" * 50)
        
        cv_files, job_files = self.get_files()
        
        # Prendre un échantillon
        cv_sample = cv_files[:5]  # 5 CV
        job_sample = job_files[:5]  # 5 Jobs = 25 matchings
        
        results = []
        total_tests = len(cv_sample) * len(job_sample)
        completed = 0
        
        for cv in cv_sample:
            for job in job_sample:
                completed += 1
                print(f"🔄 Test {completed}/{total_tests}: {cv[:20]}... vs {job[:20]}...")
                
                try:
                    response = requests.post(f"{self.api_base}/api/matching/files", 
                        json={
                            'cv_path': os.path.join(self.cv_dir, cv),
                            'job_path': os.path.join(self.job_dir, job)
                        }, timeout=45)
                    
                    if response.status_code == 200:
                        data = response.json()
                        score = data.get('matching_score', 0)
                        compatibility = data.get('domain_compatibility', 'unknown')
                        alerts = len(data.get('alerts', []))
                        
                        result = {
                            'cv_file': cv,
                            'job_file': job,
                            'score': score,
                            'compatibility': compatibility,
                            'alerts': alerts,
                            'status': 'success'
                        }
                        results.append(result)
                        
                        status_icon = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
                        print(f"   {status_icon} Score: {score}% | Compatibilité: {compatibility}")
                        
                    else:
                        print(f"   ❌ Erreur HTTP: {response.status_code}")
                        results.append({
                            'cv_file': cv,
                            'job_file': job,
                            'score': 0,
                            'status': f'error_{response.status_code}'
                        })
                        
                except Exception as e:
                    print(f"   ❌ Erreur: {str(e)[:50]}...")
                    results.append({
                        'cv_file': cv,
                        'job_file': job,
                        'score': 0,
                        'status': 'error_timeout'
                    })
                
                time.sleep(1)  # Pause pour éviter la surcharge
        
        return results
    
    def run_full_massive_test(self):
        """Lancer les tests massifs complets"""
        print(f"\n🚀 TESTS MASSIFS COMPLETS - SuperSmartMatch V2.1")
        print("=" * 60)
        
        cv_files, job_files = self.get_files()
        total_tests = len(cv_files) * len(job_files)
        
        print(f"⚠️  ATTENTION: {total_tests} tests vont être lancés!")
        print(f"⏱️  Temps estimé: ~{total_tests * 2 // 60} minutes")
        
        response = input("Continuer ? (y/N): ")
        if response.lower() != 'y':
            print("❌ Tests annulés")
            return []
        
        results = []
        completed = 0
        start_time = time.time()
        
        for i, cv in enumerate(cv_files):
            for j, job in enumerate(job_files):
                completed += 1
                
                if completed % 50 == 0:
                    elapsed = time.time() - start_time
                    rate = completed / elapsed * 60  # tests/minute
                    remaining = (total_tests - completed) / rate if rate > 0 else 0
                    print(f"\n📊 Progression: {completed}/{total_tests} ({completed/total_tests*100:.1f}%)")
                    print(f"⏱️  Temps restant: ~{remaining:.1f} minutes")
                
                try:
                    response = requests.post(f"{self.api_base}/api/matching/files", 
                        json={
                            'cv_path': os.path.join(self.cv_dir, cv),
                            'job_path': os.path.join(self.job_dir, job)
                        }, timeout=60)
                    
                    if response.status_code == 200:
                        data = response.json()
                        score = data.get('matching_score', 0)
                        compatibility = data.get('domain_compatibility', 'unknown')
                        alerts = len(data.get('alerts', []))
                        
                        result = {
                            'cv_file': cv,
                            'job_file': job,
                            'score': score,
                            'compatibility': compatibility,
                            'alerts': alerts,
                            'status': 'success',
                            'timestamp': datetime.now().isoformat()
                        }
                        results.append(result)
                        
                    else:
                        results.append({
                            'cv_file': cv,
                            'job_file': job,
                            'score': 0,
                            'status': f'error_{response.status_code}',
                            'timestamp': datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    results.append({
                        'cv_file': cv,
                        'job_file': job,
                        'score': 0,
                        'status': f'error_timeout',
                        'error': str(e)[:100],
                        'timestamp': datetime.now().isoformat()
                    })
                
                # Petite pause pour ne pas surcharger
                time.sleep(0.5)
        
        return results
    
    def analyze_results(self, results):
        """Analyser les résultats des tests"""
        print(f"\n📊 ANALYSE DES RÉSULTATS")
        print("=" * 40)
        
        if not results:
            print("❌ Aucun résultat à analyser")
            return
        
        df = pd.DataFrame(results)
        
        # Statistiques générales
        total = len(results)
        success = len(df[df['status'] == 'success'])
        success_rate = success / total * 100 if total > 0 else 0
        
        print(f"📊 Total tests: {total}")
        print(f"✅ Succès: {success} ({success_rate:.1f}%)")
        print(f"❌ Échecs: {total - success} ({100 - success_rate:.1f}%)")
        
        if success > 0:
            successful_df = df[df['status'] == 'success']
            
            avg_score = successful_df['score'].mean()
            high_scores = len(successful_df[successful_df['score'] >= 70])
            medium_scores = len(successful_df[(successful_df['score'] >= 40) & (successful_df['score'] < 70)])
            low_scores = len(successful_df[successful_df['score'] < 40])
            
            print(f"\n🎯 DISTRIBUTION DES SCORES:")
            print(f"   🟢 Élevé (≥70%): {high_scores} ({high_scores/success*100:.1f}%)")
            print(f"   🟡 Moyen (40-69%): {medium_scores} ({medium_scores/success*100:.1f}%)")
            print(f"   🔴 Faible (<40%): {low_scores} ({low_scores/success*100:.1f}%)")
            print(f"   📈 Score moyen: {avg_score:.1f}%")
            
            # Anti-faux positifs
            if 'alerts' in successful_df.columns:
                with_alerts = len(successful_df[successful_df['alerts'] > 0])
                print(f"\n🚨 ALERTES ANTI-FAUX POSITIFS:")
                print(f"   ⚠️  Matchings avec alertes: {with_alerts} ({with_alerts/success*100:.1f}%)")
        
        # Sauvegarder les résultats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"massive_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Résultats sauvegardés: {filename}")
        
        return df

def main():
    print("🚀 SuperSmartMatch V2.1 Enhanced - Tests Massifs")
    print("=" * 60)
    
    tester = SuperSmartMatchMassiveTesting()
    
    # 1. Vérifier les services
    if not tester.validate_services():
        print("\n❌ Certains services ne sont pas opérationnels!")
        print("   Démarrez tous les services avant de continuer.")
        return
    
    # 2. Test de validation Hugo Salvat
    if not tester.test_hugo_salvat_validation():
        print("\n⚠️  Le test de validation Hugo Salvat a échoué!")
        response = input("Continuer quand même ? (y/N): ")
        if response.lower() != 'y':
            return
    
    # 3. Menu de choix
    print(f"\n🎯 CHOIX DU TYPE DE TEST:")
    print(f"   1. Test échantillon (25 matchings)")
    print(f"   2. Tests massifs complets (2,812 matchings)")
    print(f"   3. Quitter")
    
    choice = input("Votre choix (1-3): ")
    
    if choice == "1":
        results = tester.run_sample_batch()
        tester.analyze_results(results)
        
    elif choice == "2":
        results = tester.run_full_massive_test()
        tester.analyze_results(results)
        
    else:
        print("👋 Au revoir!")
        return
    
    print(f"\n✅ Tests terminés avec succès!")
    print(f"🎯 SuperSmartMatch V2.1 Enhanced - Mission accomplie!")

if __name__ == "__main__":
    main()
