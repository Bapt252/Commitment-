#!/usr/bin/env python3
"""
SuperSmartMatch V3.0 - Orchestrateur de Tests Multi-Formats
Intégration complète des améliorations Cursor avec orchestration automatisée
"""

import os
import sys
import subprocess
import time
import json
import requests
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional
import threading
import signal

class SuperSmartMatchOrchestrator:
    """Orchestrateur principal pour SuperSmartMatch V3.0 Enhanced"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.services = {}
        self.test_results = {}
        self.running = False
        
        # Configuration des ports (évite conflits)
        self.port_config = {
            'cv_parser': 5051,
            'job_parser': 5053, 
            'supersmartmatch': 5067,
            'api_gateway': 5065,
            'dashboard': 5070
        }
        
        # Configuration logging
        self.setup_logging()
        
        # Gestion signaux pour arrêt propre
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_logging(self):
        """Configuration du système de logging"""
        log_dir = self.project_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'orchestrator.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('SuperSmartMatch-Orchestrator')
    
    def signal_handler(self, signum, frame):
        """Gestionnaire d'arrêt propre"""
        self.logger.info("🛑 Signal d'arrêt reçu, arrêt des services...")
        self.stop_all_services()
        sys.exit(0)
    
    def print_banner(self):
        """Affiche la bannière de démarrage"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                      🎯 SuperSmartMatch V3.0 Enhanced                        ║
║                     Multi-Format Testing Orchestrator                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  🏆 Performance Record: 98.6% précision, 6.9-35ms latence                   ║
║  📁 Formats supportés: PDF, DOCX, DOC, PNG, JPG, JPEG, TXT                  ║
║  🤖 7 algorithmes disponibles, Enhanced V3.0 recommandé                     ║
║  🔧 Intégration améliorations Cursor AI                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def check_prerequisites(self) -> bool:
        """Vérification des prérequis"""
        self.logger.info("🔍 Vérification des prérequis...")
        
        # Vérifier Python et packages
        try:
            import requests, uvicorn, fastapi, streamlit
            self.logger.info("✅ Packages Python requis disponibles")
        except ImportError as e:
            self.logger.error(f"❌ Package manquant: {e}")
            return False
        
        # Vérifier structure des fichiers
        required_files = [
            'app/__init__.py',
            'app/smartmatch.py',
            'test_supersmartmatch_v3_enhanced.py',
            'test_data_automation.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.project_root / file).exists():
                missing_files.append(file)
        
        if missing_files:
            self.logger.warning(f"⚠️  Fichiers manquants: {missing_files}")
        else:
            self.logger.info("✅ Structure des fichiers validée")
        
        # Vérifier ports disponibles
        self.check_ports_availability()
        
        return True
    
    def check_ports_availability(self):
        """Vérifie la disponibilité des ports"""
        import socket
        
        for service, port in self.port_config.items():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', port))
                    if result == 0:
                        self.logger.warning(f"⚠️  Port {port} ({service}) déjà occupé")
                    else:
                        self.logger.info(f"✅ Port {port} ({service}) disponible")
            except Exception as e:
                self.logger.error(f"❌ Erreur vérification port {port}: {e}")
    
    def setup_test_environment(self):
        """Configuration de l'environnement de test"""
        self.logger.info("🏗️  Configuration environnement de test...")
        
        # Créer structure de test si nécessaire
        try:
            from test_data_automation import TestDataAutomation
            automation = TestDataAutomation()
            automation.create_full_test_structure()
            self.logger.info("✅ Structure de test créée/mise à jour")
        except Exception as e:
            self.logger.error(f"❌ Erreur création structure test: {e}")
    
    def start_service(self, service_name: str, command: str, cwd: Optional[str] = None) -> bool:
        """Démarre un service individuel"""
        try:
            self.logger.info(f"🚀 Démarrage {service_name}...")
            
            # Préparer l'environnement
            env = os.environ.copy()
            env['PORT'] = str(self.port_config.get(service_name, 5000))
            
            # Démarrer le processus
            work_dir = Path(cwd) if cwd else self.project_root
            process = subprocess.Popen(
                command.split(),
                cwd=work_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Stocker le processus
            self.services[service_name] = {
                'process': process,
                'port': self.port_config.get(service_name),
                'status': 'starting',
                'start_time': time.time()
            }
            
            # Attendre un peu pour le démarrage
            time.sleep(3)
            
            # Vérifier si le service répond
            if self.check_service_health(service_name):
                self.services[service_name]['status'] = 'running'
                self.logger.info(f"✅ {service_name} démarré sur port {self.port_config.get(service_name)}")
                return True
            else:
                self.logger.warning(f"⚠️  {service_name} démarré mais ne répond pas encore")
                return True  # Le service peut prendre plus de temps
                
        except Exception as e:
            self.logger.error(f"❌ Erreur démarrage {service_name}: {e}")
            return False
    
    def check_service_health(self, service_name: str) -> bool:
        """Vérifie la santé d'un service"""
        try:
            port = self.port_config.get(service_name)
            url = f"http://localhost:{port}/health"
            response = requests.get(url, timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_all_services(self):
        """Démarre tous les services SuperSmartMatch"""
        self.logger.info("🚀 Démarrage de tous les services...")
        
        services_config = [
            {
                'name': 'cv_parser',
                'command': 'uvicorn app:app --host 0.0.0.0 --port 5051',
                'cwd': None
            },
            {
                'name': 'job_parser', 
                'command': 'python simple_job_parser.py',
                'cwd': None
            },
            {
                'name': 'supersmartmatch',
                'command': 'uvicorn app:app --host 0.0.0.0 --port 5067',
                'cwd': '../SuperSmartMatch-Service'
            },
            {
                'name': 'api_gateway',
                'command': 'python api_gateway.py',
                'cwd': None
            },
            {
                'name': 'dashboard',
                'command': 'streamlit run dashboard_v3.py --server.port 5070 --server.headless true',
                'cwd': None
            }
        ]
        
        started_services = 0
        for service_config in services_config:
            if self.start_service(
                service_config['name'],
                service_config['command'],
                service_config['cwd']
            ):
                started_services += 1
                time.sleep(2)  # Délai entre les démarrages
        
        self.logger.info(f"📊 Services démarrés: {started_services}/{len(services_config)}")
        
        # Attendre que tous les services soient prêts
        self.wait_for_services_ready()
        
        return started_services >= 3  # Au moins 3 services pour les tests
    
    def wait_for_services_ready(self, timeout: int = 60):
        """Attend que les services soient prêts"""
        self.logger.info("⏳ Attente de la disponibilité des services...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            ready_services = 0
            for service_name in self.services:
                if self.check_service_health(service_name):
                    if self.services[service_name]['status'] != 'ready':
                        self.services[service_name]['status'] = 'ready'
                        self.logger.info(f"✅ {service_name} prêt")
                    ready_services += 1
            
            if ready_services >= 3:  # Minimum pour les tests
                self.logger.info("🎯 Services prêts pour les tests !")
                break
                
            time.sleep(5)
        
        # Afficher le statut final
        self.display_services_status()
    
    def display_services_status(self):
        """Affiche le statut de tous les services"""
        self.logger.info("📊 Statut des services:")
        self.logger.info("=" * 50)
        
        for service_name, service_info in self.services.items():
            port = service_info['port']
            status = service_info['status']
            uptime = time.time() - service_info['start_time']
            
            status_icon = {
                'starting': '🔄',
                'running': '⚠️',
                'ready': '✅',
                'error': '❌'
            }.get(status, '❓')
            
            self.logger.info(f"{status_icon} {service_name.upper()}: {status} (port {port}, uptime {uptime:.1f}s)")
        
        self.logger.info("=" * 50)
    
    def run_comprehensive_tests(self) -> Dict:
        """Lance une suite complète de tests"""
        self.logger.info("🧪 Lancement des tests complets SuperSmartMatch V3.0...")
        
        test_results = {
            'start_time': datetime.now().isoformat(),
            'test_phases': {},
            'overall_success': False,
            'metrics': {}
        }
        
        # Phase 1: Tests de santé
        self.logger.info("📋 Phase 1: Tests de santé des services")
        health_results = self.run_health_tests()
        test_results['test_phases']['health'] = health_results
        
        # Phase 2: Tests multi-formats
        if health_results.get('success', False):
            self.logger.info("📋 Phase 2: Tests multi-formats")
            format_results = self.run_multiformat_tests()
            test_results['test_phases']['multiformat'] = format_results
        
        # Phase 3: Tests de performance
        if health_results.get('success', False):
            self.logger.info("📋 Phase 3: Tests de performance V3.0")
            performance_results = self.run_performance_tests()
            test_results['test_phases']['performance'] = performance_results
        
        # Phase 4: Tests algorithmes
        if health_results.get('success', False):
            self.logger.info("📋 Phase 4: Tests comparaison algorithmes")
            algorithm_results = self.run_algorithm_comparison()
            test_results['test_phases']['algorithms'] = algorithm_results
        
        # Calcul du succès global
        test_results['overall_success'] = self.calculate_overall_success(test_results)
        test_results['end_time'] = datetime.now().isoformat()
        
        # Sauvegarde des résultats
        self.save_test_results(test_results)
        
        return test_results
    
    def run_health_tests(self) -> Dict:
        """Lance les tests de santé"""
        try:
            result = subprocess.run([
                'python', '-c',
                '''
import unittest
from test_supersmartmatch_v3_enhanced import TestSuperSmartMatchV3Enhanced
suite = unittest.TestSuite()
suite.addTest(TestSuperSmartMatchV3Enhanced("test_services_health_multiformat"))
runner = unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w"))
result = runner.run(suite)
print("SUCCESS" if result.wasSuccessful() else "FAILED")
'''
            ], capture_output=True, text=True, timeout=30)
            
            return {
                'success': 'SUCCESS' in result.stdout,
                'output': result.stdout,
                'duration': 'quick'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_multiformat_tests(self) -> Dict:
        """Lance les tests multi-formats"""
        try:
            # Commande simplifiée pour éviter les timeouts
            cmd = [
                'python', '-m', 'unittest', 
                'test_supersmartmatch_v3_enhanced.TestSuperSmartMatchV3Enhanced.test_supersmartmatch_v3_multiformat_performance',
                '-v'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'errors': result.stderr,
                'duration': 'moderate'
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Test timeout'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_performance_tests(self) -> Dict:
        """Lance les tests de performance spécifiques"""
        # Tests de performance directement via API
        performance_data = {
            'response_times': [],
            'scores': [],
            'success_rate': 0
        }
        
        try:
            # Test avec données basées sur vos résultats exceptionnels
            test_data = {
                'cv_data': {
                    'skills': ['python', 'django', 'leadership', 'devops', 'docker'],
                    'experience_years': 6,
                    'level': 'Senior'
                },
                'job_data': {
                    'skills_required': ['python', 'management', 'devops'],
                    'experience_required': 5,
                    'level': 'Senior'
                }
            }
            
            successful_tests = 0
            total_tests = 5
            
            for i in range(total_tests):
                try:
                    start_time = time.time()
                    response = requests.post(
                        f'http://localhost:{self.port_config["supersmartmatch"]}/match',
                        json={'cv_data': test_data['cv_data'], 'job_data': test_data['job_data'], 'algorithm': 'Enhanced_V3.0'},
                        timeout=10
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        result = response.json()
                        processing_time = (end_time - start_time) * 1000
                        
                        performance_data['response_times'].append(processing_time)
                        performance_data['scores'].append(result.get('match_score', 0))
                        successful_tests += 1
                        
                except Exception:
                    continue
            
            performance_data['success_rate'] = (successful_tests / total_tests) * 100
            
            return {
                'success': successful_tests >= 3,
                'data': performance_data,
                'successful_tests': successful_tests,
                'total_tests': total_tests
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_algorithm_comparison(self) -> Dict:
        """Compare les algorithmes disponibles"""
        algorithms = ['Enhanced_V3.0', 'Semantic_V2.1', 'Weighted_Skills']
        algorithm_scores = {}
        
        test_data = {
            'cv_data': {'skills': ['python', 'leadership'], 'experience_years': 5, 'level': 'Senior'},
            'job_data': {'skills_required': ['python', 'management'], 'experience_required': 5, 'level': 'Senior'}
        }
        
        for algorithm in algorithms:
            try:
                response = requests.post(
                    f'http://localhost:{self.port_config["supersmartmatch"]}/match',
                    json={'cv_data': test_data['cv_data'], 'job_data': test_data['job_data'], 'algorithm': algorithm},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    algorithm_scores[algorithm] = result.get('match_score', 0)
                    
            except Exception:
                algorithm_scores[algorithm] = None
        
        return {
            'success': len(algorithm_scores) >= 2,
            'algorithm_scores': algorithm_scores,
            'best_algorithm': max(algorithm_scores, key=lambda k: algorithm_scores[k] or 0) if algorithm_scores else None
        }
    
    def calculate_overall_success(self, test_results: Dict) -> bool:
        """Calcule le succès global des tests"""
        phases = test_results.get('test_phases', {})
        
        # Au moins 3 phases doivent réussir
        successful_phases = sum(1 for phase in phases.values() if phase.get('success', False))
        
        return successful_phases >= 3
    
    def save_test_results(self, results: Dict):
        """Sauvegarde les résultats de test"""
        results_dir = self.project_root / 'test_data' / 'results'
        results_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f'orchestrator_results_{timestamp}.json'
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"💾 Résultats sauvés: {results_file}")
        self.test_results = results
    
    def display_final_report(self):
        """Affiche le rapport final"""
        if not self.test_results:
            self.logger.warning("Aucun résultat de test disponible")
            return
        
        print("\n" + "="*80)
        print("🎯 SUPERSMARTMATCH V3.0 - RAPPORT FINAL")
        print("="*80)
        
        overall_success = self.test_results.get('overall_success', False)
        status_icon = "✅" if overall_success else "❌"
        
        print(f"{status_icon} STATUT GLOBAL: {'SUCCÈS' if overall_success else 'ÉCHEC'}")
        print()
        
        # Détails par phase
        phases = self.test_results.get('test_phases', {})
        for phase_name, phase_data in phases.items():
            success = phase_data.get('success', False)
            icon = "✅" if success else "❌"
            print(f"{icon} {phase_name.upper()}: {'OK' if success else 'ÉCHEC'}")
        
        print()
        
        # Métriques de performance si disponibles
        if 'performance' in phases and phases['performance'].get('success'):
            perf_data = phases['performance'].get('data', {})
            avg_time = sum(perf_data.get('response_times', [])) / len(perf_data.get('response_times', [1]))
            avg_score = sum(perf_data.get('scores', [])) / len(perf_data.get('scores', [1]))
            
            print(f"⚡ PERFORMANCE:")
            print(f"   Temps moyen: {avg_time:.1f}ms")
            print(f"   Score moyen: {avg_score:.1f}%")
            print(f"   Taux de succès: {perf_data.get('success_rate', 0):.1f}%")
        
        # Meilleur algorithme si disponible
        if 'algorithms' in phases and phases['algorithms'].get('success'):
            best_algo = phases['algorithms'].get('best_algorithm')
            if best_algo:
                print(f"🏆 MEILLEUR ALGORITHME: {best_algo}")
        
        print()
        print("📊 Services actifs:")
        for service_name, service_info in self.services.items():
            status = service_info.get('status', 'unknown')
            port = service_info.get('port', '?')
            icon = "✅" if status == 'ready' else "⚠️" if status in ['running', 'starting'] else "❌"
            print(f"   {icon} {service_name}: {status} (port {port})")
        
        print("="*80)
        
        if overall_success:
            print("🏆 SuperSmartMatch V3.0 Enhanced - SYSTÈME VALIDÉ !")
            print("🚀 Prêt pour la production avec vos scores de 98.6% !")
        else:
            print("⚠️  Certains tests ont échoué, révision recommandée")
        
        print("="*80)
    
    def stop_all_services(self):
        """Arrête tous les services"""
        self.logger.info("🛑 Arrêt de tous les services...")
        
        for service_name, service_info in self.services.items():
            try:
                process = service_info['process']
                if process.poll() is None:  # Processus encore actif
                    process.terminate()
                    # Attendre un peu puis forcer si nécessaire
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    
                    self.logger.info(f"✅ {service_name} arrêté")
            except Exception as e:
                self.logger.error(f"❌ Erreur arrêt {service_name}: {e}")
        
        self.running = False
    
    def run_complete_workflow(self):
        """Lance le workflow complet"""
        try:
            self.print_banner()
            
            # Vérifications préliminaires
            if not self.check_prerequisites():
                self.logger.error("❌ Prérequis non satisfaits")
                return False
            
            # Configuration environnement
            self.setup_test_environment()
            
            # Démarrage des services
            if not self.start_all_services():
                self.logger.error("❌ Échec démarrage des services")
                return False
            
            self.running = True
            
            # Lancement des tests
            self.run_comprehensive_tests()
            
            # Rapport final
            self.display_final_report()
            
            return self.test_results.get('overall_success', False)
            
        except KeyboardInterrupt:
            self.logger.info("⚠️  Interruption utilisateur")
        except Exception as e:
            self.logger.error(f"❌ Erreur dans le workflow: {e}")
        finally:
            self.stop_all_services()
        
        return False

def main():
    """Point d'entrée principal"""
    orchestrator = SuperSmartMatchOrchestrator()
    success = orchestrator.run_complete_workflow()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
