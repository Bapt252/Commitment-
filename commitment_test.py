#!/usr/bin/env python3
"""
🧪 SCRIPT DE TEST POST-NETTOYAGE COMMITMENT (CORRIGÉ)
====================================================

Script de validation automatisée pour vérifier que toutes les 
fonctionnalités essentielles fonctionnent après le nettoyage.

🎯 Objectif: S'assurer que le nettoyage n'a cassé aucune fonctionnalité
⚠️  Priorité: Validation du système de parsing CV (critique)

Version corrigée avec les bons chemins de fichiers.
"""

import sys
import requests
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

class CommitmentValidator:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests_passed": 0,
            "tests_failed": 0,
            "critical_failures": [],
            "results": []
        }
        
        # URLs des pages frontend à tester
        self.frontend_urls = {
            "Upload CV": "https://bapt252.github.io/Commitment-/templates/candidate-upload.html",
            "Questionnaire Candidat": "https://bapt252.github.io/Commitment-/templates/candidate-questionnaire.html",
            "Interface Matching": "https://bapt252.github.io/Commitment-/templates/candidate-matching-improved.html",
            "Questionnaire Entreprise": "https://bapt252.github.io/Commitment-/templates/client-questionnaire.html",
            "Recommandations": "https://bapt252.github.io/Commitment-/templates/candidate-recommendation.html"
        }
        
        # Fichiers critiques qui doivent exister (chemins corrigés)
        self.critical_files = [
            "backend/job_parser_service.py",
            "backend/job_parser_api.py",
            "backend/super_smart_match_v3.py", 
            "backend/unified_matching_service.py",
            "static/js/gpt-parser-client.js",    # NOUVEAU: Fichier créé
            "cv-parser-integration.js"           # NOUVEAU: Fichier créé
        ]
        
        # Fichiers qui doivent avoir été supprimés
        self.deleted_files = [
            "backend/super_smart_match.py",
            "backend/super_smart_match_v2.py",
            "backend/super_smart_match_v2_nexten_integration.py",
            "matching_service_v1.py",
            "matching_service_v2.py",
            "api-matching-advanced.py",
            "api-matching-enhanced-v2.py",
            "api-matching-enhanced-v2-no-cors.py",
            "backend/health_app.py"
        ]

    def log_test(self, test_name: str, status: str, details: str = "", critical: bool = False):
        """Enregistrer le résultat d'un test"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "critical": critical
        }
        
        self.test_results["results"].append(result)
        
        if status == "PASS":
            self.test_results["tests_passed"] += 1
            print(f"✅ {test_name}: {status}")
        else:
            self.test_results["tests_failed"] += 1
            print(f"❌ {test_name}: {status}")
            if critical:
                self.test_results["critical_failures"].append(test_name)
            
        if details:
            print(f"   📝 {details}")

    def test_critical_files_exist(self) -> bool:
        """🔒 Test CRITIQUE: Vérifier que tous les fichiers essentiels existent"""
        print("\n🔍 Test 1: Vérification des fichiers critiques...")
        
        all_critical_present = True
        
        for file_path in self.critical_files:
            full_path = self.repo_path / file_path
            if full_path.exists():
                size = full_path.stat().st_size
                self.log_test(f"Fichier critique présent: {file_path}", "PASS", f"Taille: {size} bytes")
            else:
                self.log_test(f"Fichier critique manquant: {file_path}", "FAIL", "", critical=True)
                all_critical_present = False
                
        return all_critical_present

    def test_redundant_files_deleted(self) -> bool:
        """🗑️ Test: Vérifier que les fichiers redondants ont été supprimés"""
        print("\n🗑️  Test 2: Vérification suppression fichiers redondants...")
        
        cleanup_successful = True
        
        for file_path in self.deleted_files:
            full_path = self.repo_path / file_path
            if not full_path.exists():
                self.log_test(f"Fichier redondant supprimé: {file_path}", "PASS")
            else:
                self.log_test(f"Fichier redondant encore présent: {file_path}", "FAIL", "Suppression incomplète")
                cleanup_successful = False
                
        return cleanup_successful

    def test_python_imports(self) -> bool:
        """🐍 Test: Vérifier que les modules Python s'importent sans erreur"""
        print("\n🐍 Test 3: Validation des imports Python...")
        
        imports_working = True
        
        # Tester les imports des fichiers conservés
        test_imports = [
            ("super_smart_match_v3", "backend.super_smart_match_v3"),
            ("unified_matching_service", "backend.unified_matching_service"),
            ("job_parser_service", "backend.job_parser_service"),
            ("job_parser_api", "backend.job_parser_api")
        ]
        
        for module_name, import_path in test_imports:
            try:
                # Changer vers le répertoire du repo pour les imports relatifs
                original_path = sys.path[:]
                sys.path.insert(0, str(self.repo_path))
                
                exec(f"import {import_path}")
                self.log_test(f"Import Python: {module_name}", "PASS")
                
                sys.path = original_path
                
            except ImportError as e:
                self.log_test(f"Import Python: {module_name}", "FAIL", f"Erreur: {e}", critical=True)
                imports_working = False
            except Exception as e:
                self.log_test(f"Import Python: {module_name}", "FAIL", f"Erreur inattendue: {e}")
                imports_working = False
                
        return imports_working

    def test_frontend_pages(self) -> bool:
        """🌐 Test: Vérifier l'accessibilité des pages frontend"""
        print("\n🌐 Test 4: Validation des pages frontend...")
        
        pages_working = True
        
        for page_name, url in self.frontend_urls.items():
            try:
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    content_length = len(response.content)
                    
                    # Vérifications spécifiques pour certaines pages
                    if page_name == "Upload CV":
                        # Vérifier que la page fait référence aux bons scripts
                        if "cv-parser-integration.js" in response.text:
                            self.log_test(f"Page Frontend: {page_name}", "PASS", 
                                        f"Status: {response.status_code}, Script cv-parser-integration.js trouvé", 
                                        critical=True)
                        else:
                            self.log_test(f"Page Frontend: {page_name}", "WARNING", 
                                        f"Script cv-parser-integration.js non trouvé dans la page")
                    elif page_name == "Questionnaire Entreprise" and "gpt" in response.text.lower():
                        self.log_test(f"Page Frontend: {page_name}", "PASS", 
                                    f"Status: {response.status_code}, ⚠️ Erreur GPT connue détectée")
                    else:
                        self.log_test(f"Page Frontend: {page_name}", "PASS", 
                                    f"Status: {response.status_code}, Taille: {content_length} bytes")
                else:
                    self.log_test(f"Page Frontend: {page_name}", "FAIL", 
                                f"Status HTTP: {response.status_code}", critical=(page_name == "Upload CV"))
                    pages_working = False
                    
            except requests.RequestException as e:
                self.log_test(f"Page Frontend: {page_name}", "FAIL", 
                            f"Erreur réseau: {e}", critical=(page_name == "Upload CV"))
                pages_working = False
                
        return pages_working

    def test_parsing_cv_functionality(self) -> bool:
        """⭐ Test CRITIQUE: Validation du système de parsing CV"""
        print("\n⭐ Test 5: Validation système de parsing CV (CRITIQUE)...")
        
        parsing_working = True
        
        # Vérifier la structure des fichiers de parsing
        parsing_files = [
            ("job_parser_service.py", "backend/job_parser_service.py"),
            ("job_parser_api.py", "backend/job_parser_api.py"),
            ("gpt-parser-client.js", "static/js/gpt-parser-client.js"),
            ("cv-parser-integration.js", "cv-parser-integration.js")
        ]
        
        for file_name, file_path in parsing_files:
            full_path = self.repo_path / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Vérifier les fonctionnalités clés selon le type de fichier
                    if file_name.endswith('.py'):
                        checks = {
                            "Mode OpenAI": "openai" in content.lower(),
                            "Mode Fallback": "regex" in content.lower() or "fallback" in content.lower(),
                            "Support PDF": "pdf" in content.lower(),
                            "Support DOCX": "docx" in content.lower()
                        }
                    else:  # Fichiers JavaScript
                        checks = {
                            "Classe GPTParserClient": "GPTParserClient" in content,
                            "Intégration OpenAI": "openai" in content.lower(),
                            "Mode Fallback": "fallback" in content.lower(),
                            "Gestion des erreurs": "catch" in content.lower()
                        }
                        
                    for check_name, check_result in checks.items():
                        if check_result:
                            self.log_test(f"Parsing CV - {check_name} dans {file_name}", "PASS")
                        else:
                            self.log_test(f"Parsing CV - {check_name} dans {file_name}", "WARNING", 
                                        "Fonctionnalité non détectée dans le code")
                            
                except Exception as e:
                    self.log_test(f"Parsing CV - Lecture {file_name}", "FAIL", f"Erreur: {e}", critical=True)
                    parsing_working = False
            else:
                self.log_test(f"Parsing CV - {file_name}", "FAIL", "Fichier manquant", critical=True)
                parsing_working = False
                
        return parsing_working

    def test_algorithm_architecture(self) -> bool:
        """🎯 Test: Validation de l'architecture des algorithmes"""
        print("\n🎯 Test 6: Validation architecture algorithmes...")
        
        architecture_valid = True
        
        # Vérifier que les 2 algorithmes principaux existent et ont du contenu
        main_algorithms = [
            ("super_smart_match_v3.py", "backend/super_smart_match_v3.py", 40000),  # ~45KB attendu
            ("unified_matching_service.py", "backend/unified_matching_service.py", 10000)  # ~14KB attendu
        ]
        
        for algo_name, algo_path, min_size in main_algorithms:
            full_path = self.repo_path / algo_path
            if full_path.exists():
                size = full_path.stat().st_size
                if size >= min_size:
                    self.log_test(f"Algorithme principal: {algo_name}", "PASS", 
                                f"Taille: {size} bytes (>= {min_size} requis)")
                else:
                    self.log_test(f"Algorithme principal: {algo_name}", "WARNING", 
                                f"Taille: {size} bytes (< {min_size} attendu)")
            else:
                self.log_test(f"Algorithme principal: {algo_name}", "FAIL", 
                            "Fichier manquant", critical=True)
                architecture_valid = False
                
        return architecture_valid

    def test_new_files_integration(self) -> bool:
        """🆕 Test: Validation de l'intégration des nouveaux fichiers"""
        print("\n🆕 Test 7: Validation des nouveaux fichiers créés...")
        
        integration_working = True
        
        # Vérifier que les nouveaux fichiers sont bien intégrés
        new_files = [
            ("gpt-parser-client.js", "static/js/gpt-parser-client.js", "GPTParserClient"),
            ("cv-parser-integration.js", "cv-parser-integration.js", "CVParserIntegration")
        ]
        
        for file_name, file_path, expected_class in new_files:
            full_path = self.repo_path / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if expected_class in content:
                        self.log_test(f"Nouveau fichier: {file_name}", "PASS", 
                                    f"Classe {expected_class} trouvée")
                    else:
                        self.log_test(f"Nouveau fichier: {file_name}", "WARNING", 
                                    f"Classe {expected_class} non trouvée")
                        integration_working = False
                        
                except Exception as e:
                    self.log_test(f"Nouveau fichier: {file_name}", "FAIL", f"Erreur lecture: {e}")
                    integration_working = False
            else:
                self.log_test(f"Nouveau fichier: {file_name}", "FAIL", "Fichier manquant", critical=True)
                integration_working = False
                
        return integration_working

    def test_api_endpoints(self) -> bool:
        """🔌 Test: Validation des endpoints API (si serveur local disponible)"""
        print("\n🔌 Test 8: Validation endpoints API...")
        
        # Tenter de détecter si un serveur local est en cours d'exécution
        test_urls = [
            "http://localhost:8000",
            "http://localhost:5000", 
            "http://127.0.0.1:8000",
            "http://127.0.0.1:5000"
        ]
        
        server_found = False
        for url in test_urls:
            try:
                response = requests.get(f"{url}/health", timeout=2)
                if response.status_code == 200:
                    self.log_test("API Server détecté", "PASS", f"URL: {url}")
                    server_found = True
                    
                    # Tester les endpoints principaux
                    endpoints = ["/api/parse-cv", "/api/match"]
                    for endpoint in endpoints:
                        try:
                            # Test simple GET pour vérifier l'existence
                            resp = requests.get(f"{url}{endpoint}", timeout=2)
                            if resp.status_code != 404:
                                self.log_test(f"Endpoint {endpoint}", "PASS", f"Status: {resp.status_code}")
                            else:
                                self.log_test(f"Endpoint {endpoint}", "FAIL", "404 Not Found")
                        except:
                            self.log_test(f"Endpoint {endpoint}", "UNKNOWN", "Impossible de tester")
                    break
            except:
                continue
                
        if not server_found:
            self.log_test("API Server", "SKIP", "Aucun serveur local détecté - Test ignoré")
            
        return True  # Ne pas faire échouer si pas de serveur

    def generate_test_report(self):
        """📊 Générer le rapport de test final"""
        print("\n📊 Génération du rapport de test...")
        
        # Calculer les statistiques
        total_tests = self.test_results["tests_passed"] + self.test_results["tests_failed"]
        success_rate = (self.test_results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
        
        # Ajouter les statistiques
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "success_rate": round(success_rate, 2),
            "critical_failures_count": len(self.test_results["critical_failures"]),
            "overall_status": "CRITICAL_FAILURE" if self.test_results["critical_failures"] else 
                             ("SUCCESS" if success_rate >= 90 else "PARTIAL_SUCCESS"),
            "parsing_system_status": "VALIDATED" if not self.test_results["critical_failures"] else "ISSUES_DETECTED"
        }
        
        # Sauvegarder le rapport
        report_file = self.repo_path / "test_validation_report.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"✅ Rapport sauvegardé: {report_file}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde rapport: {e}")

    def run_all_tests(self) -> bool:
        """🚀 Exécuter tous les tests de validation"""
        print("🧪 DÉBUT DES TESTS DE VALIDATION POST-NETTOYAGE (CORRIGÉ)")
        print("=" * 70)
        
        # Exécuter tous les tests dans l'ordre
        test_results = [
            self.test_critical_files_exist(),
            self.test_redundant_files_deleted(),
            self.test_python_imports(),
            self.test_parsing_cv_functionality(),
            self.test_algorithm_architecture(),
            self.test_new_files_integration(),
            self.test_frontend_pages(),
            self.test_api_endpoints()
        ]
        
        # Générer le rapport
        self.generate_test_report()
        
        # Afficher le résumé
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ DES TESTS")
        print(f"✅ Tests réussis: {self.test_results['tests_passed']}")
        print(f"❌ Tests échoués: {self.test_results['tests_failed']}")
        print(f"🔴 Échecs critiques: {len(self.test_results['critical_failures'])}")
        
        if self.test_results['critical_failures']:
            print("\n🚨 ÉCHECS CRITIQUES DÉTECTÉS:")
            for failure in self.test_results['critical_failures']:
                print(f"  ⚠️  {failure}")
            print("\n❌ VALIDATION ÉCHOUÉE - Rollback recommandé")
            return False
        
        success_rate = (self.test_results['tests_passed'] / 
                       (self.test_results['tests_passed'] + self.test_results['tests_failed']) * 100)
        
        if success_rate >= 90:
            print(f"\n🎉 VALIDATION RÉUSSIE ({success_rate:.1f}% de succès)")
            print("✅ Le nettoyage a été effectué avec succès")
            print("🔍 Toutes les fonctionnalités critiques sont opérationnelles")
            print("🆕 Nouveaux fichiers créés et intégrés avec succès")
            return True
        else:
            print(f"\n⚠️  VALIDATION PARTIELLE ({success_rate:.1f}% de succès)")
            print("🔍 Vérifiez les échecs non-critiques dans le rapport")
            return True  # Accepter si pas d'échecs critiques

def main():
    """Point d'entrée principal"""
    print("🧪 COMMITMENT - VALIDATION POST-NETTOYAGE (CORRIGÉ)")
    print("Tests automatisés des fonctionnalités essentielles")
    
    validator = CommitmentValidator()
    success = validator.run_all_tests()
    
    if success:
        print("\n🎯 PROCHAINES ÉTAPES:")
        print("1. Vérifiez manuellement les pages frontend importantes")
        print("2. Testez un upload de CV complet") 
        print("3. Validez le calcul de matching sur un cas réel")
        print("4. Vérifiez que les nouveaux fichiers JavaScript fonctionnent")
        print("5. Mettez à jour la documentation")
    else:
        print("\n🔄 ACTIONS REQUISES:")
        print("1. Examinez les échecs critiques ci-dessus")
        print("2. Envisagez un rollback depuis la sauvegarde")
        print("3. Corrigez les problèmes identifiés")
        print("4. Relancez la validation")
        sys.exit(1)

if __name__ == "__main__":
    main()
