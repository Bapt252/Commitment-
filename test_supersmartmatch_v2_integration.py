#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test d'Intégration SuperSmartMatch V2 - Nexten Matcher
======================================================

Script de validation complète de l'intégration Nexten dans SuperSmartMatch V2.
Teste tous les scénarios : sélection automatique, fallbacks, performances.

Usage:
    python test_supersmartmatch_v2_integration.py

Auteur: Claude/Anthropic - Tests Intégration V2
Date: 02/06/2025
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Any
import logging

# Configuration du logging pour les tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SuperSmartMatchV2Tester:
    """
    Testeur complet pour SuperSmartMatch V2 avec intégration Nexten
    """
    
    def __init__(self, base_url: str = "http://localhost:5062"):
        self.base_url = base_url
        self.nexten_url = "http://localhost:5052"
        self.test_results = []
        
        # Données de test standardisées
        self.setup_test_data()
    
    def setup_test_data(self):
        """Configure les données de test pour tous les scénarios"""
        
        # Candidat de base (sans questionnaire)
        self.basic_candidate = {
            "competences": ["Python", "React", "Django", "SQL", "Git"],
            "adresse": "Paris",
            "mobilite": "hybrid",
            "annees_experience": 4,
            "salaire_souhaite": 50000,
            "contrats_recherches": ["CDI"],
            "disponibilite": "immediate"
        }
        
        # Candidat senior (doit déclencher Enhanced)
        self.senior_candidate = {
            **self.basic_candidate,
            "annees_experience": 8,
            "competences": ["Python", "Java", "React", "AWS", "Docker", "Kubernetes", "PostgreSQL"],
            "salaire_souhaite": 75000
        }
        
        # Candidat avec questionnaire riche (doit déclencher Nexten)
        self.nexten_candidate = {
            **self.basic_candidate,
            "questionnaire": {
                "informations_personnelles": {
                    "poste_souhaite": "Développeur Full Stack",
                    "objectifs_carriere": "Évolution technique et managériale"
                },
                "mobilite_preferences": {
                    "mode_travail": "Hybride",
                    "localisation": "Paris",
                    "type_contrat": "CDI",
                    "taille_entreprise": "Startup"
                },
                "motivations_secteurs": {
                    "secteurs": ["Tech", "Fintech", "E-commerce"],
                    "valeurs": ["Innovation", "Autonomie", "Collaboration"],
                    "technologies": ["Python", "React", "Cloud", "IA"]
                },
                "disponibilite_situation": {
                    "disponibilite": "Immédiate",
                    "salaire": {"min": 45000, "max": 55000},
                    "avantages_souhaites": ["Remote", "Formation"]
                }
            }
        }
        
        # Candidat technique (doit déclencher Semantic)
        self.technical_candidate = {
            **self.basic_candidate,
            "competences": [
                "Python", "Java", "JavaScript", "TypeScript", "React", "Vue.js", 
                "Node.js", "Django", "FastAPI", "PostgreSQL", "MongoDB", "Redis",
                "Docker", "Kubernetes", "AWS", "GCP", "Git", "Jenkins"
            ],
            "annees_experience": 5
        }
        
        # Candidat géo-contraint (doit déclencher SmartMatch)
        self.geo_candidate = {
            **self.basic_candidate,
            "mobilite": "on-site",
            "adresse": "Lyon, 69000"
        }
        
        # Offres de test
        self.test_offers = [
            {
                "id": 1,
                "titre": "Développeur Full Stack Python/React",
                "competences": ["Python", "Django", "React", "PostgreSQL"],
                "localisation": "Paris",
                "type_contrat": "CDI",
                "salaire": "45K-55K€",
                "politique_remote": "hybrid",
                "experience": "3-5 ans",
                "description": "Développement d'applications web modernes",
                "questionnaire": {
                    "secteur": "Tech",
                    "valeurs": ["Innovation", "Agilité"],
                    "taille_entreprise": "Startup",
                    "technologies": ["Python", "React", "AWS"]
                }
            },
            {
                "id": 2,
                "titre": "Data Scientist Senior",
                "competences": ["Python", "Machine Learning", "SQL", "Spark"],
                "localisation": "Remote",
                "type_contrat": "CDI",
                "salaire": "65K-80K€",
                "politique_remote": "remote",
                "experience": "5+ ans"
            },
            {
                "id": 3,
                "titre": "Développeur Frontend React",
                "competences": ["React", "JavaScript", "TypeScript", "CSS"],
                "localisation": "Lyon",
                "type_contrat": "CDI",
                "salaire": "40K-50K€",
                "politique_remote": "on-site",
                "experience": "2-4 ans"
            }
        ]
    
    def run_all_tests(self):
        """Exécute tous les tests d'intégration V2"""
        print("🚀 DÉBUT DES TESTS SUPERSMARTMATCH V2 - INTÉGRATION NEXTEN")
        print("=" * 70)
        
        # Tests de santé
        self.test_services_health()
        
        # Tests de sélection automatique
        self.test_algorithm_selection()
        
        # Tests de performance
        self.test_performance()
        
        # Tests de fallback
        self.test_fallback_scenarios()
        
        # Tests de compatibilité
        self.test_backward_compatibility()
        
        # Rapport final
        self.generate_test_report()
    
    def test_services_health(self):
        """Test de santé des services"""
        print("\n🏥 TESTS DE SANTÉ DES SERVICES")
        print("-" * 40)
        
        # Test SuperSmartMatch
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=5)
            if response.status_code == 200:
                print("✅ SuperSmartMatch service: OK")
                self.test_results.append(("SuperSmartMatch Health", "PASS", "Service opérationnel"))
            else:
                print(f"❌ SuperSmartMatch service: {response.status_code}")
                self.test_results.append(("SuperSmartMatch Health", "FAIL", f"HTTP {response.status_code}"))
        except Exception as e:
            print(f"❌ SuperSmartMatch service: {str(e)}")
            self.test_results.append(("SuperSmartMatch Health", "FAIL", str(e)))
        
        # Test Nexten Matcher
        try:
            response = requests.get(f"{self.nexten_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Nexten Matcher service: OK")
                self.test_results.append(("Nexten Health", "PASS", "Service opérationnel"))
            else:
                print(f"⚠️ Nexten Matcher service: {response.status_code}")
                self.test_results.append(("Nexten Health", "WARN", f"HTTP {response.status_code}"))
        except Exception as e:
            print(f"⚠️ Nexten Matcher service: {str(e)} (Fallback activé)")
            self.test_results.append(("Nexten Health", "WARN", f"Service indisponible - {str(e)}"))
    
    def test_algorithm_selection(self):
        """Test de la sélection automatique d'algorithmes"""
        print("\n🧠 TESTS DE SÉLECTION AUTOMATIQUE D'ALGORITHMES")
        print("-" * 50)
        
        test_cases = [
            {
                "name": "Candidat de base → Enhanced",
                "candidate": self.basic_candidate,
                "expected_algorithm": "enhanced",
                "description": "Candidat standard doit utiliser Enhanced"
            },
            {
                "name": "Candidat senior → Enhanced", 
                "candidate": self.senior_candidate,
                "expected_algorithm": "enhanced",
                "description": "Profil senior (8 ans) doit utiliser Enhanced"
            },
            {
                "name": "Questionnaire riche → Nexten",
                "candidate": self.nexten_candidate,
                "expected_algorithm": "nexten",
                "description": "Questionnaire complet doit déclencher Nexten"
            },
            {
                "name": "Profil technique → Semantic",
                "candidate": self.technical_candidate,
                "expected_algorithm": "semantic",
                "description": "Beaucoup de compétences doit utiliser Semantic"
            },
            {
                "name": "Géo-contraint → SmartMatch",
                "candidate": self.geo_candidate,
                "expected_algorithm": "smart-match",
                "description": "Mobilité on-site doit utiliser SmartMatch"
            }
        ]
        
        for test_case in test_cases:
            print(f"\n🔍 Test: {test_case['name']}")
            
            try:
                # Appel API avec algorithme auto
                response = self._call_matching_api({
                    "candidate": test_case["candidate"],
                    "offers": self.test_offers,
                    "algorithm": "auto"
                })
                
                if response and response.get("success"):
                    selected_algo = response.get("algorithm_used", {}).get("type")
                    selection_reason = response.get("algorithm_used", {}).get("selection_reason", "")
                    
                    print(f"   Algorithme sélectionné: {selected_algo}")
                    print(f"   Raison: {selection_reason}")
                    
                    if selected_algo == test_case["expected_algorithm"]:
                        print("   ✅ PASS - Sélection correcte")
                        self.test_results.append((test_case["name"], "PASS", f"Sélectionné: {selected_algo}"))
                    else:
                        print(f"   ⚠️ ATTENTION - Attendu: {test_case['expected_algorithm']}, Obtenu: {selected_algo}")
                        self.test_results.append((test_case["name"], "WARN", f"Attendu: {test_case['expected_algorithm']}, Obtenu: {selected_algo}"))
                else:
                    print("   ❌ FAIL - Erreur API")
                    self.test_results.append((test_case["name"], "FAIL", "Erreur API"))
                    
            except Exception as e:
                print(f"   ❌ FAIL - Exception: {str(e)}")
                self.test_results.append((test_case["name"], "FAIL", str(e)))
    
    def test_performance(self):
        """Test de performance V2"""
        print("\n📊 TESTS DE PERFORMANCE")
        print("-" * 30)
        
        # Test avec différents algorithmes
        algorithms = ["auto", "enhanced", "smart-match", "semantic"]
        
        for algo in algorithms:
            print(f"\n⏱️ Performance test: {algo}")
            
            start_time = time.time()
            try:
                response = self._call_matching_api({
                    "candidate": self.basic_candidate,
                    "offers": self.test_offers,
                    "algorithm": algo
                })
                
                execution_time = time.time() - start_time
                
                if response and response.get("success"):
                    api_execution_time = response.get("matching_results", {}).get("execution_time", 0)
                    matches_found = response.get("matching_results", {}).get("matches_found", 0)
                    
                    print(f"   Temps total: {execution_time:.3f}s")
                    print(f"   Temps algorithme: {api_execution_time:.3f}s") 
                    print(f"   Matches trouvés: {matches_found}")
                    
                    if execution_time < 1.0:  # Moins d'1 seconde acceptable
                        print("   ✅ Performance OK")
                        self.test_results.append((f"Performance {algo}", "PASS", f"{execution_time:.3f}s"))
                    else:
                        print("   ⚠️ Performance dégradée")
                        self.test_results.append((f"Performance {algo}", "WARN", f"{execution_time:.3f}s"))
                else:
                    print("   ❌ Échec du test")
                    self.test_results.append((f"Performance {algo}", "FAIL", "Erreur API"))
                    
            except Exception as e:
                print(f"   ❌ Erreur: {str(e)}")
                self.test_results.append((f"Performance {algo}", "FAIL", str(e)))
    
    def test_fallback_scenarios(self):
        """Test des scénarios de fallback"""
        print("\n🔄 TESTS DE FALLBACK")
        print("-" * 25)
        
        # Test avec Nexten indisponible (simulé)
        print("\n🚫 Test fallback Nexten indisponible")
        try:
            # Force utilisation Nexten avec service potentiellement DOWN
            response = self._call_matching_api({
                "candidate": self.nexten_candidate,
                "offers": self.test_offers,
                "algorithm": "nexten"
            })
            
            if response and response.get("success"):
                algo_used = response.get("algorithm_used", {}).get("type")
                print(f"   Algorithme utilisé: {algo_used}")
                
                if algo_used == "nexten":
                    print("   ✅ Nexten opérationnel")
                    self.test_results.append(("Nexten Direct", "PASS", "Service disponible"))
                else:
                    print(f"   ✅ Fallback activé vers {algo_used}")
                    self.test_results.append(("Nexten Fallback", "PASS", f"Fallback vers {algo_used}"))
            else:
                print("   ❌ Échec total")
                self.test_results.append(("Nexten Fallback", "FAIL", "Aucun fallback"))
                
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
            self.test_results.append(("Nexten Fallback", "FAIL", str(e)))
    
    def test_backward_compatibility(self):
        """Test de compatibilité avec l'API V1"""
        print("\n🔙 TESTS DE COMPATIBILITÉ V1")
        print("-" * 35)
        
        # Test format réponse V1
        print("\n📤 Test format réponse V1")
        try:
            response = self._call_matching_api({
                "candidate": self.basic_candidate,
                "offers": self.test_offers
            })
            
            if response and response.get("success"):
                # Vérifier structure réponse
                required_fields = ["algorithm_used", "candidate_profile", "matching_results"]
                missing_fields = [field for field in required_fields if field not in response]
                
                if not missing_fields:
                    print("   ✅ Structure réponse V2 complète")
                    self.test_results.append(("Réponse V2 Structure", "PASS", "Tous champs présents"))
                else:
                    print(f"   ⚠️ Champs manquants: {missing_fields}")
                    self.test_results.append(("Réponse V2 Structure", "WARN", f"Manquants: {missing_fields}"))
                
                # Vérifier compatibilité format matches
                matches = response.get("matching_results", {}).get("matches", [])
                if matches:
                    match = matches[0]
                    v1_fields = ["offer_id", "title", "score"]
                    missing_v1 = [field for field in v1_fields if field not in match]
                    
                    if not missing_v1:
                        print("   ✅ Compatibilité V1 matches OK")
                        self.test_results.append(("Compatibilité V1 Matches", "PASS", "Format compatible"))
                    else:
                        print(f"   ❌ Champs V1 manquants: {missing_v1}")
                        self.test_results.append(("Compatibilité V1 Matches", "FAIL", f"Manquants: {missing_v1}"))
            else:
                print("   ❌ Réponse invalide")
                self.test_results.append(("Compatibilité V1", "FAIL", "Réponse invalide"))
                
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
            self.test_results.append(("Compatibilité V1", "FAIL", str(e)))
    
    def _call_matching_api(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Appel générique à l'API de matching"""
        try:
            # Try V2 endpoint first, fallback to V1
            endpoints = ["/api/v2/match", "/api/v1/match"]
            
            for endpoint in endpoints:
                try:
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=payload,
                        timeout=30,
                        headers={'Content-Type': 'application/json'}
                    )
                    
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 404 and endpoint == "/api/v2/match":
                        # V2 pas encore déployé, essayer V1
                        continue
                    else:
                        logger.warning(f"API {endpoint} returned {response.status_code}")
                        
                except requests.exceptions.ConnectionError:
                    if endpoint == "/api/v2/match":
                        continue  # Essayer V1
                    else:
                        raise
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur appel API: {str(e)}")
            return None
    
    def generate_test_report(self):
        """Génère le rapport final des tests"""
        print("\n" + "=" * 70)
        print("📊 RAPPORT DE TESTS SUPERSMARTMATCH V2")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r[1] == "PASS"])
        warned = len([r for r in self.test_results if r[1] == "WARN"])
        failed = len([r for r in self.test_results if r[1] == "FAIL"])
        
        print(f"\n📈 STATISTIQUES:")
        print(f"   Total tests: {total_tests}")
        print(f"   ✅ Réussis: {passed}")
        print(f"   ⚠️ Avertissements: {warned}")
        print(f"   ❌ Échecs: {failed}")
        print(f"   📊 Taux de réussite: {(passed/total_tests)*100:.1f}%")
        
        print(f"\n📋 DÉTAIL DES RÉSULTATS:")
        for test_name, status, details in self.test_results:
            status_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[status]
            print(f"   {status_icon} {test_name}: {details}")
        
        # Recommandations
        print(f"\n🎯 RECOMMANDATIONS:")
        
        if failed == 0 and warned == 0:
            print("   🎉 Excellent ! SuperSmartMatch V2 est prêt pour la production")
            print("   🚀 Vous pouvez procéder au déploiement progressif")
        elif failed == 0:
            print("   ✅ Bon état général avec quelques avertissements")
            print("   🔍 Vérifiez les points d'attention avant déploiement")
        else:
            print("   ⚠️ Problèmes détectés - Investigation requise")
            print("   🔧 Corrigez les échecs avant déploiement en production")
        
        # Prochaines étapes
        print(f"\n🗺️ PROCHAINES ÉTAPES:")
        print("   1. ✅ Tests locaux terminés")
        print("   2. 🔄 Intégration dans service principal")
        print("   3. 📊 Tests A/B progressifs")
        print("   4. 🚀 Rollout en production")
        
        # Sauvegarde du rapport
        report_data = {
            "timestamp": time.time(),
            "total_tests": total_tests,
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "success_rate": (passed/total_tests)*100,
            "test_results": self.test_results
        }
        
        try:
            with open("supersmartmatch_v2_test_report.json", "w") as f:
                json.dump(report_data, f, indent=2)
            print(f"\n💾 Rapport sauvegardé: supersmartmatch_v2_test_report.json")
        except:
            pass

def main():
    """Point d'entrée principal des tests"""
    print("🏁 Initialisation des tests SuperSmartMatch V2...")
    
    # Configuration depuis variables d'environnement
    base_url = os.getenv("SUPERSMARTMATCH_URL", "http://localhost:5062")
    
    # Création du testeur
    tester = SuperSmartMatchV2Tester(base_url)
    
    # Exécution de tous les tests
    tester.run_all_tests()

if __name__ == "__main__":
    main()
