#!/usr/bin/env python3
"""
Enhanced Batch Testing V2.1 - CORRIGÉ
Tests massifs SuperSmartMatch avec gestion des espaces dans les chemins
"""

import os
import requests
import json
import time
from datetime import datetime
import pandas as pd
import sys
from pathlib import Path

class EnhancedBatchTester:
    def __init__(self):
        self.base_url = "http://localhost:5055"
        self.results = []
        self.start_time = None
        
        # Chemins corrigés avec gestion des espaces
        self.cv_folder = Path.home() / "Desktop" / "CV TEST"
        self.job_folder = Path.home() / "Desktop" / "FDP TEST"
        
        # Extensions supportées
        self.supported_extensions = ['.pdf', '.doc', '.docx']
        
    def check_directories(self):
        """
        Vérification de l'existence des dossiers
        """
        print("🔍 VÉRIFICATION DES DOSSIERS:")
        print(f"📁 Dossier CV: {self.cv_folder}")
        
        if not self.cv_folder.exists():
            print(f"❌ Dossier CV non trouvé: {self.cv_folder}")
            # Tentative de localisation automatique
            potential_paths = [
                Path.home() / "Desktop" / "CV TEST",
                Path.home() / "Desktop" / "CV_TEST",
                Path.home() / "Desktop" / "CVTEST",
                Path("/Users/baptistecomas/Desktop/CV TEST"),
                Path("/Users/baptistecomas/Desktop/CV_TEST")
            ]
            
            for path in potential_paths:
                if path.exists():
                    print(f"✅ Dossier CV trouvé: {path}")
                    self.cv_folder = path
                    break
            else:
                print("❌ Aucun dossier CV trouvé dans les emplacements possibles")
                return False
        else:
            print(f"✅ Dossier CV trouvé")
            
        print(f"📁 Dossier Jobs: {self.job_folder}")
        if not self.job_folder.exists():
            print(f"❌ Dossier Jobs non trouvé: {self.job_folder}")
            # Tentative de localisation automatique
            potential_paths = [
                Path.home() / "Desktop" / "FDP TEST",
                Path.home() / "Desktop" / "FDP_TEST",
                Path.home() / "Desktop" / "FDPTEST", 
                Path("/Users/baptistecomas/Desktop/FDP TEST"),
                Path("/Users/baptistecomas/Desktop/FDP_TEST")
            ]
            
            for path in potential_paths:
                if path.exists():
                    print(f"✅ Dossier Jobs trouvé: {path}")
                    self.job_folder = path
                    break
            else:
                print("❌ Aucun dossier Jobs trouvé dans les emplacements possibles")
                return False
        else:
            print(f"✅ Dossier Jobs trouvé")
            
        return True
    
    def get_files_list(self):
        """
        Récupération de la liste des fichiers avec gestion des espaces
        """
        print("📄 SCAN DES FICHIERS:")
        
        # Scan CV
        cv_files = []
        if self.cv_folder.exists():
            for file_path in self.cv_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                    cv_files.append(file_path)
        
        print(f"   📋 CV trouvés: {len(cv_files)}")
        for cv in cv_files[:5]:  # Afficher les 5 premiers
            print(f"      - {cv.name}")
        if len(cv_files) > 5:
            print(f"      ... et {len(cv_files) - 5} autres")
        
        # Scan Jobs
        job_files = []
        if self.job_folder.exists():
            for file_path in self.job_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                    job_files.append(file_path)
        
        print(f"   💼 Jobs trouvés: {len(job_files)}")
        for job in job_files[:5]:  # Afficher les 5 premiers
            print(f"      - {job.name}")
        if len(job_files) > 5:
            print(f"      ... et {len(job_files) - 5} autres")
            
        return cv_files, job_files
    
    def check_api_health(self):
        """
        Vérification de l'état des APIs
        """
        print("🏥 VÉRIFICATION APIs:")
        
        apis = [
            ("CV Parser V2", "http://localhost:5051/health"),
            ("Job Parser V2", "http://localhost:5053/health"),
            ("Enhanced API V2.1", "http://localhost:5055/health")
        ]
        
        all_healthy = True
        for name, url in apis:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {name}: OK")
                else:
                    print(f"   ❌ {name}: Erreur {response.status_code}")
                    all_healthy = False
            except Exception as e:
                print(f"   ❌ {name}: Non accessible ({e})")
                all_healthy = False
                
        return all_healthy
    
    def test_single_match(self, cv_path, job_path):
        """
        Test d'un matching individual avec gestion robuste des chemins
        """
        try:
            # Utilisation de Path pour gérer les espaces correctement
            with open(cv_path, 'rb') as cv_file, open(job_path, 'rb') as job_file:
                files = {
                    'cv_file': (cv_path.name, cv_file, 'application/pdf'),
                    'job_file': (job_path.name, job_file, 'application/pdf')
                }
                
                response = requests.post(
                    f"{self.base_url}/api/matching/files",
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    'error': f"HTTP {response.status_code}",
                    'details': response.text[:200]
                }
                
        except Exception as e:
            return {
                'error': str(e),
                'details': f"Erreur lors du test {cv_path.name} vs {job_path.name}"
            }
    
    def run_focused_tests(self, max_cv=10, max_jobs=5):
        """
        Tests focalisés pour validation rapide
        """
        print(f"🎯 TESTS FOCALISÉS ({max_cv} CV × {max_jobs} Jobs):")
        
        cv_files, job_files = self.get_files_list()
        
        # Limitation pour tests rapides
        test_cvs = cv_files[:max_cv]
        test_jobs = job_files[:max_jobs]
        
        total_tests = len(test_cvs) * len(test_jobs)
        print(f"📊 Total tests: {total_tests}")
        
        self.start_time = time.time()
        test_count = 0
        
        for cv_path in test_cvs:
            for job_path in test_jobs:
                test_count += 1
                print(f"🔄 Test {test_count}/{total_tests}: {cv_path.name} ↔ {job_path.name}")
                
                result = self.test_single_match(cv_path, job_path)
                
                # Enrichissement des résultats
                result['cv_file'] = cv_path.name
                result['job_file'] = job_path.name
                result['test_number'] = test_count
                result['timestamp'] = datetime.now().isoformat()
                
                self.results.append(result)
                
                # Affichage du score si disponible
                if 'total_score' in result:
                    score = result['total_score']
                    status = "🎯" if score >= 70 else "⚠️" if score >= 50 else "❌"
                    print(f"   {status} Score: {score}%")
                elif 'error' in result:
                    print(f"   ❌ Erreur: {result['error']}")
                
                # Pause pour éviter la surcharge
                time.sleep(0.1)
        
        elapsed = time.time() - self.start_time
        print(f"⏱️ Tests terminés en {elapsed:.2f}s")
        
    def run_full_batch(self):
        """
        Tests complets sur tous les fichiers
        """
        print("🚀 TESTS COMPLETS:")
        
        cv_files, job_files = self.get_files_list()
        total_tests = len(cv_files) * len(job_files)
        
        print(f"📊 Total tests: {total_tests}")
        print("⚠️ Cela peut prendre du temps...")
        
        confirm = input("Continuer? (y/N): ").lower()
        if confirm != 'y':
            print("❌ Tests annulés")
            return
        
        self.start_time = time.time()
        test_count = 0
        
        for cv_path in cv_files:
            for job_path in job_files:
                test_count += 1
                
                if test_count % 10 == 0:
                    elapsed = time.time() - self.start_time
                    avg_time = elapsed / test_count
                    remaining = (total_tests - test_count) * avg_time
                    print(f"🔄 Progress: {test_count}/{total_tests} - ETA: {remaining/60:.1f}min")
                
                result = self.test_single_match(cv_path, job_path)
                result['cv_file'] = cv_path.name
                result['job_file'] = job_path.name
                result['test_number'] = test_count
                result['timestamp'] = datetime.now().isoformat()
                
                self.results.append(result)
    
    def analyze_results(self):
        """
        Analyse des résultats de tests
        """
        if not self.results:
            print("❌ Aucun résultat à analyser")
            return
        
        print("\n📊 ANALYSE DES RÉSULTATS:")
        print("=" * 50)
        
        # Statistiques de base
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if 'total_score' in r])
        error_tests = total_tests - successful_tests
        
        print(f"📈 Tests réussis: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"❌ Tests en erreur: {error_tests}")
        
        if successful_tests > 0:
            scores = [r['total_score'] for r in self.results if 'total_score' in r]
            print(f"🎯 Score moyen: {sum(scores)/len(scores):.1f}%")
            print(f"🏆 Score max: {max(scores):.1f}%")
            print(f"📉 Score min: {min(scores):.1f}%")
            
            # Distribution des scores
            high_scores = len([s for s in scores if s >= 70])
            medium_scores = len([s for s in scores if 50 <= s < 70])
            low_scores = len([s for s in scores if s < 50])
            
            print(f"\n📊 DISTRIBUTION:")
            print(f"   🎯 Scores élevés (≥70%): {high_scores}")
            print(f"   ⚠️ Scores moyens (50-69%): {medium_scores}")
            print(f"   ❌ Scores faibles (<50%): {low_scores}")
        
        # Top 5 des meilleurs matchs
        if successful_tests > 0:
            best_matches = sorted(
                [r for r in self.results if 'total_score' in r],
                key=lambda x: x['total_score'],
                reverse=True
            )[:5]
            
            print(f"\n🏆 TOP 5 MEILLEURS MATCHS:")
            for i, match in enumerate(best_matches, 1):
                print(f"   {i}. {match['cv_file']} ↔ {match['job_file']}: {match['total_score']}%")
    
    def save_results(self):
        """
        Sauvegarde des résultats
        """
        if not self.results:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sauvegarde JSON
        json_file = f"batch_results_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés: {json_file}")
        
        # Sauvegarde CSV si pandas disponible
        try:
            df = pd.DataFrame(self.results)
            csv_file = f"batch_results_{timestamp}.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"📊 CSV généré: {csv_file}")
        except:
            print("⚠️ Pandas non disponible, pas de CSV généré")

def main():
    print("🚀 SuperSmartMatch V2.1 - Enhanced Batch Testing CORRIGÉ")
    print("=" * 60)
    
    tester = EnhancedBatchTester()
    
    # Vérifications préliminaires
    if not tester.check_directories():
        print("❌ Impossible de continuer sans les dossiers")
        return
    
    if not tester.check_api_health():
        print("⚠️ Certaines APIs ne sont pas accessibles")
        print("💡 Vérifiez que les services sont démarrés sur ports 5051, 5053, 5055")
        
        continue_anyway = input("Continuer quand même? (y/N): ").lower()
        if continue_anyway != 'y':
            return
    
    # Menu des options
    print("\n🎯 OPTIONS DE TEST:")
    print("1. Tests focalisés (10 CV × 5 Jobs = 50 tests)")
    print("2. Tests complets (tous les fichiers)")
    print("3. Test spécifique BATU Sam.pdf")
    print("4. Quitter")
    
    choice = input("Choix (1-4): ").strip()
    
    if choice == "1":
        tester.run_focused_tests()
    elif choice == "2":
        tester.run_full_batch()
    elif choice == "3":
        # Test spécifique pour BATU Sam
        cv_files, job_files = tester.get_files_list()
        batu_file = None
        for cv in cv_files:
            if "BATU" in cv.name and "Sam" in cv.name:
                batu_file = cv
                break
        
        if batu_file and job_files:
            print(f"🎯 Test spécifique: {batu_file.name}")
            result = tester.test_single_match(batu_file, job_files[0])
            print(f"📊 Résultat: {result}")
        else:
            print("❌ BATU Sam.pdf non trouvé")
    else:
        print("👋 Au revoir!")
        return
    
    # Analyse et sauvegarde
    if tester.results:
        tester.analyze_results()
        tester.save_results()

if __name__ == "__main__":
    main()
