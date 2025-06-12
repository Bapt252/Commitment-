#!/usr/bin/env python3
"""
🩺 Réparation du CV Parser - Résolution du problème d'extraction BATU Sam.pdf
Script pour diagnostiquer et résoudre le problème du service CV Parser
"""

import requests
import json
import subprocess
import time
import psutil
import signal
from pathlib import Path

class CVParserFixer:
    
    def __init__(self):
        self.cv_parser_url = "http://localhost:5051"
        self.test_file_path = "/Users/baptistecomas/Desktop/BATU Sam.pdf"
        
    def check_service_status(self) -> dict:
        """Vérifie l'état du service CV Parser"""
        print("💊 Vérification du service CV Parser...")
        
        try:
            # Test de connexion
            response = requests.get(f"{self.cv_parser_url}/health", timeout=5)
            service_responsive = response.ok
            
            # Recherche du processus
            cv_parser_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if '5051' in cmdline or 'cv-parser' in cmdline.lower() or 'parseur-cv' in cmdline.lower():
                        cv_parser_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline
                        })
                except:
                    continue
            
            return {
                'responsive': service_responsive,
                'processes': cv_parser_processes,
                'port_5051_used': self.check_port_usage(5051)
            }
            
        except Exception as e:
            return {
                'responsive': False,
                'error': str(e),
                'processes': [],
                'port_5051_used': self.check_port_usage(5051)
            }
    
    def check_port_usage(self, port: int) -> list:
        """Vérifie quels processus utilisent un port"""
        try:
            result = subprocess.run(['lsof', '-i', f':{port}'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                processes = []
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        processes.append({
                            'command': parts[0],
                            'pid': parts[1],
                            'full_line': line
                        })
                return processes
            return []
        except:
            return []
    
    def test_file_extraction(self, file_path: str) -> dict:
        """Test l'extraction avec le CV Parser"""
        print(f"🧪 Test extraction: {Path(file_path).name}")
        
        if not Path(file_path).exists():
            return {'error': f'Fichier non trouvé: {file_path}'}
        
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    f"{self.cv_parser_url}/api/parse-cv/",
                    files={'file': f},
                    data={'force_refresh': 'true'},
                    timeout=30
                )
            
            if response.ok:
                cv_data = response.json()
                return {
                    'success': True,
                    'text_length': len(cv_data.get('raw_text', '')),
                    'response': cv_data
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def restart_cv_parser_service(self) -> dict:
        """Redémarre le service CV Parser"""
        print("🔄 Redémarrage du service CV Parser...")
        
        status = self.check_service_status()
        
        # Arrêter les processus existants
        stopped_processes = []
        for proc_info in status['processes']:
            try:
                pid = int(proc_info['pid'])
                process = psutil.Process(pid)
                process.terminate()
                stopped_processes.append(pid)
                print(f"   🛑 Processus arrêté: PID {pid}")
            except:
                print(f"   ❌ Impossible d'arrêter: PID {proc_info['pid']}")
        
        # Attendre que les processus se terminent
        time.sleep(3)
        
        # Forcer l'arrêt si nécessaire
        for pid in stopped_processes:
            try:
                process = psutil.Process(pid)
                if process.is_running():
                    process.kill()
                    print(f"   💀 Processus forcé: PID {pid}")
            except:
                pass
        
        print("   ⏳ Attente 5 secondes...")
        time.sleep(5)
        
        # Vérifier si le port est libéré
        port_usage = self.check_port_usage(5051)
        if port_usage:
            print(f"   ⚠️  Port 5051 toujours utilisé par: {port_usage}")
            return {
                'success': False,
                'message': 'Impossible de libérer le port 5051'
            }
        else:
            print("   ✅ Port 5051 libéré")
            return {
                'success': True,
                'message': 'Service arrêté. Redémarrer manuellement le CV Parser.',
                'instructions': [
                    "1. Aller dans le dossier du CV Parser",
                    "2. Exécuter: python parseur-cv-v2.py (ou equivalent)",
                    "3. Vérifier que le service démarre sur le port 5051"
                ]
            }
    
    def install_pdf_dependencies(self) -> dict:
        """Installe/met à jour les dépendances PDF"""
        print("📦 Mise à jour des dépendances PDF...")
        
        dependencies = [
            'pdfplumber',
            'PyPDF2',
            'python-pdf2',
            'pdfminer',
            'pdfminer.six'
        ]
        
        results = {}
        
        for dep in dependencies:
            try:
                print(f"   📦 Installation: {dep}")
                result = subprocess.run([
                    'pip', 'install', '--upgrade', dep
                ], capture_output=True, text=True, timeout=60)
                
                results[dep] = {
                    'success': result.returncode == 0,
                    'output': result.stdout if result.returncode == 0 else result.stderr
                }
                
                if result.returncode == 0:
                    print(f"   ✅ {dep} installé/mis à jour")
                else:
                    print(f"   ❌ Erreur {dep}: {result.stderr[:100]}")
                    
            except Exception as e:
                results[dep] = {'success': False, 'error': str(e)}
                print(f"   ❌ Exception {dep}: {e}")
        
        return results
    
    def run_comprehensive_fix(self) -> dict:
        """Lance une réparation complète"""
        print("🔧 RÉPARATION COMPLÈTE DU CV PARSER")
        print("="*50)
        
        results = {}
        
        # 1. État initial
        print("\n1️⃣ ÉTAT INITIAL")
        initial_status = self.check_service_status()
        results['initial_status'] = initial_status
        
        print(f"   Service responsive: {initial_status['responsive']}")
        print(f"   Processus trouvés: {len(initial_status['processes'])}")
        
        # 2. Test extraction initial
        print("\n2️⃣ TEST EXTRACTION INITIAL")
        initial_test = self.test_file_extraction(self.test_file_path)
        results['initial_test'] = initial_test
        
        if initial_test.get('success'):
            print(f"   Texte extrait: {initial_test['text_length']} caractères")
            if initial_test['text_length'] > 100:
                print("   ✅ Problème résolu!")
                return results
        else:
            print(f"   ❌ Échec: {initial_test.get('error', 'Erreur inconnue')}")
        
        # 3. Mise à jour des dépendances
        print("\n3️⃣ MISE À JOUR DÉPENDANCES PDF")
        deps_result = self.install_pdf_dependencies()
        results['dependencies'] = deps_result
        
        # 4. Redémarrage du service
        print("\n4️⃣ REDÉMARRAGE DU SERVICE")
        restart_result = self.restart_cv_parser_service()
        results['restart'] = restart_result
        
        if restart_result['success']:
            print("   ✅ Service arrêté")
            print("   🔧 ACTIONS MANUELLES REQUISES:")
            for instruction in restart_result['instructions']:
                print(f"      {instruction}")
        else:
            print(f"   ❌ Échec redémarrage: {restart_result['message']}")
        
        return results
    
    def wait_for_service_restart(self, timeout: int = 60) -> bool:
        """Attend que le service redémarre"""
        print(f"⏳ Attente redémarrage service (max {timeout}s)...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"{self.cv_parser_url}/health", timeout=2)
                if response.ok:
                    print("   ✅ Service redémarré!")
                    return True
            except:
                pass
            
            time.sleep(2)
            print("   ⏳ En attente...")
        
        print("   ❌ Timeout - Service non redémarré")
        return False
    
    def final_test(self) -> dict:
        """Test final après réparation"""
        print("\n5️⃣ TEST FINAL")
        
        # Attendre que le service redémarre
        if not self.wait_for_service_restart():
            return {
                'success': False,
                'message': 'Service non redémarré'
            }
        
        # Test d'extraction final
        final_test = self.test_file_extraction(self.test_file_path)
        
        if final_test.get('success') and final_test.get('text_length', 0) > 100:
            print(f"   ✅ SUCCÈS: {final_test['text_length']} caractères extraits")
            return {
                'success': True,
                'text_length': final_test['text_length'],
                'message': 'Problème résolu!'
            }
        else:
            print(f"   ❌ ÉCHEC: {final_test.get('text_length', 0)} caractères")
            return {
                'success': False,
                'message': 'Problème persistant après réparation',
                'details': final_test
            }

def main():
    # Vérifier si psutil est installé
    try:
        import psutil
    except ImportError:
        print("❌ Module psutil requis non installé")
        print("🔧 Installation en cours...")
        subprocess.run(['pip', 'install', 'psutil'], check=True)
        import psutil
    
    fixer = CVParserFixer()
    
    print("🩺 CV PARSER FIXER - SuperSmartMatch V2.1")
    print("="*50)
    
    # Réparation complète
    results = fixer.run_comprehensive_fix()
    
    # Affichage du résumé
    print("\n📋 RÉSUMÉ DE LA RÉPARATION")
    print("="*30)
    
    initial_responsive = results.get('initial_status', {}).get('responsive', False)
    print(f"Service initial: {'✅ Opérationnel' if initial_responsive else '❌ Problème'}")
    
    initial_extraction = results.get('initial_test', {}).get('text_length', 0)
    print(f"Extraction initiale: {initial_extraction} caractères")
    
    deps_success = sum(1 for dep, res in results.get('dependencies', {}).items() 
                      if res.get('success', False))
    total_deps = len(results.get('dependencies', {}))
    print(f"Dépendances: {deps_success}/{total_deps} mises à jour")
    
    restart_success = results.get('restart', {}).get('success', False)
    print(f"Redémarrage: {'✅ OK' if restart_success else '❌ Échec'}")
    
    if restart_success:
        print("\n🔧 PROCHAINES ÉTAPES:")
        print("1. Redémarrer manuellement le service CV Parser")
        print("2. Exécuter: python batu_sam_diagnostic.py")
        print("3. Vérifier que l'extraction fonctionne")

if __name__ == "__main__":
    main()
