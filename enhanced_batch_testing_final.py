#!/usr/bin/env python3
"""
Enhanced Batch Testing V2.1 - CORRIGÉ POUR STRUCTURE API
Tests massifs SuperSmartMatch avec extraction correcte des scores
"""

import os
import requests
import json
import time
from datetime import datetime
import pandas as pd
import sys
from pathlib import Path

class EnhancedBatchTesterFixed:
    def __init__(self):
        self.base_url = "http://localhost:5055"
        self.results = []
        self.start_time = None
        
        # Chemins corrigés avec gestion des espaces
        self.cv_folder = Path.home() / "Desktop" / "CV TEST"
        self.job_folder = Path.home() / "Desktop" / "FDP TEST"
        
        # Extensions supportées - PDF UNIQUEMENT
        self.supported_extensions = ['.pdf']
        
    def check_directories(self):
        """
        Vérification de l'existence des dossiers
        """
        print("🔍 VÉRIFICATION DES DOSSIERS:")
        print(f"📁 Dossier CV: {self.cv_folder}")
        
        if not self.cv_folder.exists():
            print(f"❌ Dossier CV non trouvé: {self.cv_folder}")
            return False
        else:
            print(f"✅ Dossier CV trouvé")
            
        print(f"📁 Dossier Jobs: {self.job_folder}")
        if not self.job_folder.exists():
            print(f"❌ Dossier Jobs non trouvé: {self.job_folder}")
            return False
        else:
            print(f"✅ Dossier Jobs trouvé")
            
        return True
    
    def get_files_list(self):
        """
        Récupération de la liste des fichiers PDF uniquement
        """
        print("📄 SCAN DES FICHIERS PDF UNIQUEMENT:")
        
        # Scan CV PDF
        cv_files = []
        if self.cv_folder.exists():
            for file_path in self.cv_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() == '.pdf':
                    cv_files.append(file_path)
        
        print(f"   📋 CV PDF trouvés: {len(cv_files)}")
        for cv in cv_files[:5]:  # Afficher les 5 premiers
            print(f"      - {cv.name}")
        if len(cv_files) > 5:
            print(f"      ... et {len(cv_files) - 5} autres")
        
        # Scan Jobs PDF
        job_files = []
        if self.job_folder.exists():
            for file_path in self.job_folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() == '.pdf':
                    job_files.append(file_path)
        
        print(f"   💼 Jobs PDF trouvés: {len(job_files)}")
        for job in job_files:  # Afficher tous les jobs PDF
            print(f"      - {job.name}")
        
        if len(job_files) == 0:
            print("   ⚠️ AUCUN JOB PDF TROUVÉ !")
            print("   💡 Tous les jobs sont en .docx (non supportés)")
            
        return cv_files, job_files
    
    def check_api_health(self):
        """
        Vérification de l'état des APIs
        """
        print("🏥 VÉRIFICATION APIs:")
        
        apis = [
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
        Test d'un matching individual avec extraction correcte du score
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
                data = response.json()
                
                # CORRECTION : Extraire le score depuis matching_analysis
                if 'matching_analysis' in data and 'total_score' in data['matching_analysis']:
                    data['total_score'] = data['matching_analysis']['total_score']
                
                # Enrichir avec des détails utiles
                if 'matching_analysis' in data:
                    ma = data['matching_analysis']
                    data['domain_score'] = ma.get('detailed_breakdown', {}).get('domain_compatibility', {}).get('score', 0)
                    data['mission_score'] = ma.get('detailed_breakdown', {}).get('missions', {}).get('score', 0)
                    data['skill_score'] = ma.get('detailed_breakdown', {}).get('skills', {}).get('score', 0)
                    data['experience_score'] = ma.get('detailed_breakdown', {}).get('experience', {}).get('score', 0)
                    data['quality_score'] = ma.get('detailed_breakdown', {}).get('quality', {}).get('score', 0)
                    data['recommendation'] = ma.get('recommendation', 'N/A')
                    data['cv_domain'] = ma.get('domain_analysis', {}).get('cv_domain', 'unknown')
                    data['job_domain'] = ma.get('domain_analysis', {}).get('job_domain', 'unknown')
                
                return data
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
    
    def run_focused_tests(self, max_cv=10):
        """
        Tests focalisés sur tous les jobs PDF disponibles
        """
        cv_files, job_files = self.get_files_list()
        
        if len(job_files) == 0:
            print("❌ IMPOSSIBLE DE CONTINUER : Aucun job PDF trouvé")
            print("💡 Convertir des jobs .docx en PDF ou utiliser un autre dataset")
            return
        
        # Limitation des CV pour tests rapides
        test_cvs = cv_files[:max_cv]
        
        total_tests = len(test_cvs) * len(job_files)
        print(f"🎯 TESTS FOCALISÉS ({len(test_cvs)} CV × {len(job_files)} Jobs PDF):")
        print(f"📊 Total tests: {total_tests}")
        
        self.start_time = time.time()
        test_count = 0
        
        for cv_path in test_cvs:
            for job_path in job_files:
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
                    
                    # Affichage des détails
                    if 'cv_domain' in result and 'job_domain' in result:
                        print(f"   📊 Domaines: {result['cv_domain']} → {result['job_domain']}")
                    if 'recommendation' in result:
                        print(f"   💡 {result['recommendation']}")
                        
                elif 'error' in result:
                    print(f"   ❌ Erreur: {result['error']}")
                
                # Pause pour éviter la surcharge
                time.sleep(0.1)
        
        elapsed = time.time() - self.start_time
        print(f"⏱️ Tests terminés en {elapsed:.2f}s")
        
    def run_full_batch(self):
        """
        Tests complets sur tous les fichiers PDF
        """
        print("🚀 TESTS COMPLETS PDF:")
        
        cv_files, job_files = self.get_files_list()
        
        if len(job_files) == 0:
            print("❌ IMPOSSIBLE DE CONTINUER : Aucun job PDF trouvé")
            return
            
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
            
            # Analyse des domaines
            domain_analysis = {}
            for result in self.results:
                if 'cv_domain' in result and 'job_domain' in result and 'total_score' in result:
                    pair = f"{result['cv_domain']} → {result['job_domain']}"
                    if pair not in domain_analysis:
                        domain_analysis[pair] = []
                    domain_analysis[pair].append(result['total_score'])
            
            if domain_analysis:
                print(f"\n🎯 ANALYSE PAR DOMAINES:")
                for pair, scores in sorted(domain_analysis.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True):
                    avg_score = sum(scores) / len(scores)
                    print(f"   {pair}: {avg_score:.1f}% (sur {len(scores)} tests)")
        
        # Top 5 des meilleurs matchs
        if successful_tests > 0:
            best_matches = sorted(
                [r for r in self.results if 'total_score' in r],
                key=lambda x: x['total_score'],
                reverse=True
            )[:5]
            
            print(f"\n🏆 TOP 5 MEILLEURS MATCHS:")
            for i, match in enumerate(best_matches, 1):
                score = match['total_score']
                cv_domain = match.get('cv_domain', 'N/A')
                job_domain = match.get('job_domain', 'N/A')
                print(f"   {i}. {match['cv_file']} ↔ {match['job_file']}: {score}% ({cv_domain} → {job_domain})")
    
    def save_results(self):
        """
        Sauvegarde des résultats
        """
        if not self.results:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sauvegarde JSON
        json_file = f"batch_results_fixed_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Résultats sauvegardés: {json_file}")
        
        # Sauvegarde CSV si pandas disponible
        try:
            df = pd.DataFrame(self.results)
            csv_file = f"batch_results_fixed_{timestamp}.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"📊 CSV généré: {csv_file}")
        except:
            print("⚠️ Pandas non disponible, pas de CSV généré")

def main():
    print("🚀 SuperSmartMatch V2.1 - Enhanced Batch Testing CORRIGÉ")
    print("=" * 60)
    
    tester = EnhancedBatchTesterFixed()
    
    # Vérifications préliminaires
    if not tester.check_directories():
        print("❌ Impossible de continuer sans les dossiers")
        return
    
    # Check des fichiers disponibles
    cv_files, job_files = tester.get_files_list()
    
    if len(job_files) == 0:
        print("\n❌ PROBLÈME CRITIQUE : Aucun job PDF trouvé")
        print("💡 Solutions possibles :")
        print("   1. Convertir les .docx en PDF")
        print("   2. Ajouter des jobs PDF au dossier")
        print("   3. Modifier le Job Parser pour supporter .docx")
        return
    
    if not tester.check_api_health():
        print("⚠️ Enhanced API non accessible")
        return
    
    # Menu des options
    print(f"\n🎯 OPTIONS DE TEST (PDF uniquement):")
    print(f"1. Tests focalisés (10 CV × {len(job_files)} Jobs = {10 * len(job_files)} tests)")
    print(f"2. Tests complets ({len(cv_files)} CV × {len(job_files)} Jobs = {len(cv_files) * len(job_files)} tests)")
    print("3. Test de validation Hugo Salvat")
    print("4. Quitter")
    
    choice = input("Choix (1-4): ").strip()
    
    if choice == "1":
        tester.run_focused_tests()
    elif choice == "2":
        tester.run_full_batch()
    elif choice == "3":
        # Test spécifique Hugo Salvat
        try:
            response = requests.get('http://localhost:5055/api/test/hugo-salvat')
            if response.status_code == 200:
                data = response.json()
                score = data.get('enhanced_result', {}).get('total_score')
                print(f"✅ Hugo Salvat test: Score {score}%")
                print(f"🎯 Résultat attendu: Score < 30% ✅")
            else:
                print(f"❌ Hugo Salvat test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur test Hugo: {e}")
    else:
        print("👋 Au revoir!")
        return
    
    # Analyse et sauvegarde
    if tester.results:
        tester.analyze_results()
        tester.save_results()

if __name__ == "__main__":
    main()
