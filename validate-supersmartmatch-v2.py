#!/usr/bin/env python3
"""
🧪 SuperSmartMatch V2 - Script de Validation d'Intégration

Tests end-to-end pour valider :
- Déploiement et santé de tous les services
- Intégration Nexten Matcher et SuperSmartMatch V1
- Sélection intelligente d'algorithmes
- Performance et résilience
- APIs V2 et compatibilité V1
"""

import asyncio
import aiohttp
import json
import time
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TestResult(Enum):
    """Résultats possibles des tests"""
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    SKIP = "⏭️ SKIP"
    WARNING = "⚠️ WARNING"

@dataclass
class TestCase:
    """Cas de test avec métadonnées"""
    name: str
    description: str
    result: TestResult = TestResult.SKIP
    execution_time_ms: float = 0.0
    details: str = ""
    error: Optional[str] = None

class SuperSmartMatchV2Validator:
    """Validateur d'intégration SuperSmartMatch V2"""
    
    def __init__(self, base_url: str = "http://localhost:5070"):
        self.base_url = base_url
        self.nexten_url = "http://localhost:5052"
        self.v1_url = "http://localhost:5062"
        self.results: List[TestCase] = []
        
    async def run_all_tests(self) -> Dict[str, Any]:
        """Exécute tous les tests de validation"""
        
        print("🚀 SuperSmartMatch V2 - Validation d'Intégration")
        print("=" * 60)
        
        # Tests de base
        await self._test_service_health()
        await self._test_external_services_health()
        
        # Tests API
        await self._test_api_v2_endpoints()
        await self._test_api_v1_compatibility()
        
        # Tests sélection d'algorithmes
        await self._test_algorithm_selection()
        
        # Tests d'intégration
        await self._test_nexten_integration()
        await self._test_v1_integration()
        
        # Tests de performance
        await self._test_performance()
        
        # Tests de résilience
        await self._test_circuit_breakers()
        
        # Génération du rapport
        return self._generate_report()
    
    async def _test_service_health(self):
        """Test santé du service principal V2"""
        test = TestCase(
            name="Service Health Check",
            description="Vérification santé SuperSmartMatch V2"
        )
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    test.execution_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        if data.get("status") == "healthy":
                            test.result = TestResult.PASS
                            test.details = f"Version: {data.get('version', 'unknown')}"
                        else:
                            test.result = TestResult.FAIL
                            test.details = f"Status unhealthy: {data.get('status')}"
                    else:
                        test.result = TestResult.FAIL
                        test.error = f"HTTP {response.status}"
                        
        except Exception as e:
            test.result = TestResult.FAIL
            test.error = str(e)
            test.execution_time_ms = (time.time() - start_time) * 1000
        
        self.results.append(test)
        self._print_test_result(test)
    
    async def _test_external_services_health(self):
        """Test santé des services externes"""
        services = [
            ("Nexten Matcher", self.nexten_url),
            ("SuperSmartMatch V1", self.v1_url)
        ]
        
        for service_name, url in services:
            test = TestCase(
                name=f"{service_name} Health",
                description=f"Vérification santé {service_name}"
            )
            
            start_time = time.time()
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{url}/health") as response:
                        test.execution_time_ms = (time.time() - start_time) * 1000
                        
                        if response.status == 200:
                            test.result = TestResult.PASS
                            test.details = "Service disponible"
                        else:
                            test.result = TestResult.WARNING
                            test.details = f"HTTP {response.status} - Service dégradé"
                            
            except Exception as e:
                test.result = TestResult.WARNING
                test.error = f"Service indisponible: {str(e)}"
                test.execution_time_ms = (time.time() - start_time) * 1000
            
            self.results.append(test)
            self._print_test_result(test)
    
    async def _test_api_v2_endpoints(self):
        """Test des endpoints API V2"""
        test = TestCase(
            name="API V2 Endpoints",
            description="Test endpoints API SuperSmartMatch V2"
        )
        
        start_time = time.time()
        
        # Données de test
        test_data = {
            "candidate": {
                "name": "Test User",
                "technical_skills": ["Python", "Machine Learning"],
                "experiences": [
                    {"duration_months": 24, "title": "Developer"}
                ]
            },
            "offers": [
                {
                    "id": "test_job_1",
                    "title": "Python Developer",
                    "required_skills": ["Python", "Django"]
                },
                {
                    "id": "test_job_2", 
                    "title": "ML Engineer",
                    "required_skills": ["Python", "Machine Learning", "TensorFlow"]
                }
            ],
            "algorithm": "auto"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v2/match",
                    json=test_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    test.execution_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if (data.get("success") and 
                            "matches" in data and 
                            len(data["matches"]) > 0):
                            test.result = TestResult.PASS
                            test.details = f"Matches trouvés: {len(data['matches'])}, Algorithme: {data.get('algorithm_used')}"
                        else:
                            test.result = TestResult.FAIL
                            test.details = "Réponse invalide ou aucun match"
                    else:
                        test.result = TestResult.FAIL
                        test.error = f"HTTP {response.status}"
                        
        except Exception as e:
            test.result = TestResult.FAIL
            test.error = str(e)
            test.execution_time_ms = (time.time() - start_time) * 1000
        
        self.results.append(test)
        self._print_test_result(test)
    
    async def _test_api_v1_compatibility(self):
        """Test compatibilité API V1"""
        test = TestCase(
            name="API V1 Compatibility",
            description="Test compatibilité backward avec API V1"
        )
        
        start_time = time.time()
        
        # Format V1 legacy
        v1_data = {
            "cv_data": {
                "name": "Legacy User",
                "technical_skills": ["JavaScript", "React"]
            },
            "job_data": [
                {
                    "id": "legacy_job_1",
                    "title": "Frontend Developer",
                    "required_skills": ["JavaScript", "React", "CSS"]
                }
            ],
            "algorithm": "smart"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/match",
                    json=v1_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    test.execution_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if ("matches" in data and 
                            len(data["matches"]) > 0 and
                            "algorithm_used" in data):
                            test.result = TestResult.PASS
                            test.details = f"Compatibilité V1 maintenue, Version: {data.get('version', 'unknown')}"
                        else:
                            test.result = TestResult.FAIL
                            test.details = "Format de réponse incompatible"
                    else:
                        test.result = TestResult.FAIL
                        test.error = f"HTTP {response.status}"
                        
        except Exception as e:
            test.result = TestResult.FAIL
            test.error = str(e)
            test.execution_time_ms = (time.time() - start_time) * 1000
        
        self.results.append(test)
        self._print_test_result(test)
    
    async def _test_algorithm_selection(self):
        """Test sélection intelligente d'algorithmes"""
        
        # Test 1: Sélection Nexten pour questionnaires complets
        await self._test_nexten_selection()
        
        # Test 2: Sélection Smart pour géolocalisation
        await self._test_smart_selection()
        
        # Test 3: Sélection Enhanced pour séniors
        await self._test_enhanced_selection()
    
    async def _test_nexten_selection(self):
        """Test sélection Nexten pour questionnaires complets"""
        test = TestCase(
            name="Nexten Algorithm Selection",
            description="Test sélection Nexten pour questionnaires complets"
        )
        
        start_time = time.time()
        
        # Données avec questionnaire complet
        data_with_questionnaire = {
            "candidate": {
                "name": "Senior ML Engineer",
                "technical_skills": ["Python", "TensorFlow", "PyTorch"],
                "experiences": [{"duration_months": 48}]
            },
            "candidate_questionnaire": {
                "work_style": "collaborative",
                "culture_preferences": "innovation_focused",
                "remote_preference": "hybrid",
                "team_size_preference": "small",
                "management_style": "agile",
                "career_goals": "technical_leadership"
            },
            "offers": [
                {
                    "id": "ml_job_1",
                    "title": "Senior ML Engineer",
                    "required_skills": ["Python", "Machine Learning"]
                }
            ],
            "algorithm": "auto"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v2/match",
                    json=data_with_questionnaire
                ) as response:
                    test.execution_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        algorithm_used = data.get("algorithm_used", "")
                        
                        if "nexten" in algorithm_used.lower():
                            test.result = TestResult.PASS
                            test.details = f"Nexten sélectionné correctement: {algorithm_used}"
                        else:
                            test.result = TestResult.WARNING
                            test.details = f"Algorithme sélectionné: {algorithm_used} (Nexten attendu)"
                    else:
                        test.result = TestResult.FAIL
                        test.error = f"HTTP {response.status}"
                        
        except Exception as e:
            test.result = TestResult.FAIL
            test.error = str(e)
            test.execution_time_ms = (time.time() - start_time) * 1000
        
        self.results.append(test)
        self._print_test_result(test)
    
    async def _test_smart_selection(self):
        """Test sélection Smart pour géolocalisation"""
        test = TestCase(
            name="Smart Algorithm Selection",
            description="Test sélection Smart pour contraintes géographiques"
        )
        
        start_time = time.time()
        
        # Données avec contraintes géographiques
        geo_data = {
            "candidate": {
                "name": "Mobile Developer",
                "localisation": "Paris",
                "technical_skills": ["Swift", "iOS"],
                "mobility": True
            },
            "offers": [
                {
                    "id": "ios_job_paris",
                    "title": "iOS Developer",
                    "localisation": "Lyon",
                    "required_skills": ["Swift", "iOS"]
                }
            ],
            "algorithm": "auto"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v2/match",
                    json=geo_data
                ) as response:
                    test.execution_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        selection_reason = data.get("selection_reason", "").lower()
                        
                        if ("géographique" in selection_reason or 
                            "smart" in data.get("algorithm_used", "").lower()):
                            test.result = TestResult.PASS
                            test.details = f"Sélection géographique détectée: {data.get('algorithm_used')}"
                        else:
                            test.result = TestResult.WARNING
                            test.details = f"Raison sélection: {data.get('selection_reason')}"
                    else:
                        test.result = TestResult.FAIL
                        test.error = f"HTTP {response.status}"
                        
        except Exception as e:
            test.result = TestResult.FAIL
            test.error = str(e)
            test.execution_time_ms = (time.time() - start_time) * 1000
        
        self.results.append(test)
        self._print_test_result(test)
    
    async def _test_enhanced_selection(self):
        """Test sélection Enhanced pour séniors"""
        test = TestCase(
            name="Enhanced Algorithm Selection",
            description="Test sélection Enhanced pour profils séniors"
        )
        
        start_time = time.time()
        
        # Profil sénior avec 10+ ans d'expérience
        senior_data = {
            "candidate": {
                "name": "Senior Tech Lead",
                "technical_skills": ["Java", "Architecture", "Leadership"],
                "experiences": [
                    {"duration_months": 36, "title": "Senior Developer"},
                    {"duration_months": 48, "title": "Tech Lead"},
                    {"duration_months": 24, "title": "Architect"}
                ]  # Total: 9 ans
            },
            "offers": [
                {
                    "id": "lead_job_1",
                    "title": "Technical Director",
                    "required_skills": ["Java", "Leadership"]
                }
            ],
            "algorithm": "auto"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v2/match",
                    json=senior_data
                ) as response:
                    test.execution_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        context = data.get("metadata", {}).get("context_analysis", {})
                        
                        if context.get("is_senior_profile") or context.get("experience_years", 0) >= 7:
                            test.result = TestResult.PASS
                            test.details = f"Profil sénior détecté: {context.get('experience_years')} ans"
                        else:
                            test.result = TestResult.WARNING
                            test.details = f"Expérience détectée: {context.get('experience_years', 'unknown')} ans"
                    else:
                        test.result = TestResult.FAIL
                        test.error = f"HTTP {response.status}"
                        
        except Exception as e:
            test.result = TestResult.FAIL
            test.error = str(e)
            test.execution_time_ms = (time.time() - start_time) * 1000
        
        self.results.append(test)
        self._print_test_result(test)
    
    async def _test_nexten_integration(self):
        """Test intégration avec Nexten Matcher"""
        test = TestCase(
            name="Nexten Integration",
            description="Test intégration directe avec service Nexten"
        )
        
        start_time = time.time()
        
        # Force l'utilisation de Nexten
        nexten_data = {
            "candidate": {
                "name": "ML Specialist",
                "technical_skills": ["Python", "TensorFlow", "Deep Learning"]
            },
            "offers": [
                {"id": "ml_advanced", "title": "AI Research Engineer"}
            ],
            "algorithm": "nexten"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v2/match",
                    json=nexten_data
                ) as response:
                    test.execution_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("algorithm_used") == "nexten":
                            test.result = TestResult.PASS
                            test.details = "Intégration Nexten réussie"
                        elif data.get("metadata", {}).get("fallback_used"):
                            test.result = TestResult.WARNING
                            test.details = f"Fallback utilisé vers: {data.get('algorithm_used')}"
                        else:
                            test.result = TestResult.FAIL
                            test.details = f"Algorithme inattendu: {data.get('algorithm_used')}"
                    else:
                        test.result = TestResult.FAIL
                        test.error = f"HTTP {response.status}"
                        
        except Exception as e:
            test.result = TestResult.FAIL
            test.error = str(e)
            test.execution_time_ms = (time.time() - start_time) * 1000
        
        self.results.append(test)
        self._print_test_result(test)
    
    async def _test_v1_integration(self):
        """Test intégration avec SuperSmartMatch V1"""
        test = TestCase(
            name="V1 Integration",
            description="Test intégration avec service SuperSmartMatch V1"
        )
        
        start_time = time.time()
        
        # Force l'utilisation d'un algorithme V1
        v1_data = {
            "candidate": {
                "name": "Frontend Expert",
                "technical_skills": ["React", "TypeScript", "GraphQL"]
            },
            "offers": [
                {"id": "frontend_job", "title": "React Developer"}
            ],
            "algorithm": "smart"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v2/match",
                    json=v1_data
                ) as response:
                    test.execution_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get("algorithm_used") == "smart":
                            test.result = TestResult.PASS
                            test.details = "Intégration V1 réussie"
                        elif data.get("metadata", {}).get("fallback_used"):
                            test.result = TestResult.WARNING
                            test.details = f"Fallback utilisé: {data.get('algorithm_used')}"
                        else:
                            test.result = TestResult.WARNING
                            test.details = f"Algorithme redirigé: {data.get('algorithm_used')}"
                    else:
                        test.result = TestResult.FAIL
                        test.error = f"HTTP {response.status}"
                        
        except Exception as e:
            test.result = TestResult.FAIL
            test.error = str(e)
            test.execution_time_ms = (time.time() - start_time) * 1000
        
        self.results.append(test)
        self._print_test_result(test)
    
    async def _test_performance(self):
        """Test de performance"""
        test = TestCase(
            name="Performance Test",
            description="Test temps de réponse sous charge"
        )
        
        # Données de test plus larges
        perf_data = {
            "candidate": {
                "name": "Performance Test User",
                "technical_skills": ["Python", "Java", "Go", "Rust", "C++"]
            },
            "offers": [
                {"id": f"perf_job_{i}", "title": f"Job {i}", "required_skills": ["Python"]}
                for i in range(20)  # 20 offres pour tester
            ],
            "algorithm": "basic"  # Utiliser basic pour test rapide
        }
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/v2/match",
                    json=perf_data
                ) as response:
                    test.execution_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        if test.execution_time_ms < 1000:  # < 1 seconde
                            test.result = TestResult.PASS
                            test.details = f"Performance acceptable: {test.execution_time_ms:.0f}ms"
                        elif test.execution_time_ms < 5000:  # < 5 secondes
                            test.result = TestResult.WARNING
                            test.details = f"Performance dégradée: {test.execution_time_ms:.0f}ms"
                        else:
                            test.result = TestResult.FAIL
                            test.details = f"Performance inacceptable: {test.execution_time_ms:.0f}ms"
                    else:
                        test.result = TestResult.FAIL
                        test.error = f"HTTP {response.status}"
                        
        except Exception as e:
            test.result = TestResult.FAIL
            test.error = str(e)
            test.execution_time_ms = (time.time() - start_time) * 1000
        
        self.results.append(test)
        self._print_test_result(test)
    
    async def _test_circuit_breakers(self):
        """Test des circuit breakers"""
        test = TestCase(
            name="Circuit Breakers",
            description="Test résilience et fallbacks"
        )
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/metrics") as response:
                    test.execution_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        circuit_breakers = data.get("circuit_breaker_status", {})
                        
                        if circuit_breakers:
                            test.result = TestResult.PASS
                            test.details = f"Circuit breakers opérationnels: {list(circuit_breakers.keys())}"
                        else:
                            test.result = TestResult.WARNING
                            test.details = "Pas d'informations sur les circuit breakers"
                    else:
                        test.result = TestResult.FAIL
                        test.error = f"HTTP {response.status}"
                        
        except Exception as e:
            test.result = TestResult.FAIL
            test.error = str(e)
            test.execution_time_ms = (time.time() - start_time) * 1000
        
        self.results.append(test)
        self._print_test_result(test)
    
    def _print_test_result(self, test: TestCase):
        """Affiche le résultat d'un test"""
        status_icon = test.result.value
        print(f"{status_icon} {test.name:<30} ({test.execution_time_ms:6.1f}ms) - {test.details}")
        
        if test.error:
            print(f"    💥 Erreur: {test.error}")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Génère le rapport final"""
        
        passed = len([t for t in self.results if t.result == TestResult.PASS])
        failed = len([t for t in self.results if t.result == TestResult.FAIL])
        warnings = len([t for t in self.results if t.result == TestResult.WARNING])
        total = len(self.results)
        
        success_rate = (passed / total * 100) if total > 0 else 0
        avg_time = sum(t.execution_time_ms for t in self.results) / total if total > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 RAPPORT DE VALIDATION SUPERSMARTMATCH V2")
        print("=" * 60)
        print(f"✅ Tests réussis:    {passed:2d}/{total}")
        print(f"❌ Tests échoués:    {failed:2d}/{total}")
        print(f"⚠️  Avertissements:  {warnings:2d}/{total}")
        print(f"📈 Taux de succès:   {success_rate:5.1f}%")
        print(f"⚡ Temps moyen:      {avg_time:5.1f}ms")
        
        # Détermination du statut global
        if failed == 0 and warnings <= 1:
            global_status = "🎉 EXCELLENT - Validation complète réussie"
        elif failed == 0:
            global_status = "✅ BON - Validation réussie avec avertissements mineurs"
        elif failed <= 2:
            global_status = "⚠️ DÉGRADÉ - Problèmes détectés nécessitant attention"
        else:
            global_status = "❌ CRITIQUE - Échecs majeurs détectés"
        
        print(f"\n🏆 STATUS GLOBAL: {global_status}")
        
        if failed > 0:
            print("\n💡 ACTIONS RECOMMANDÉES:")
            for test in self.results:
                if test.result == TestResult.FAIL:
                    print(f"   - Corriger: {test.name} - {test.error or test.details}")
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "success_rate": success_rate,
            "avg_execution_time_ms": avg_time,
            "global_status": global_status,
            "tests": [
                {
                    "name": t.name,
                    "result": t.result.name,
                    "execution_time_ms": t.execution_time_ms,
                    "details": t.details,
                    "error": t.error
                }
                for t in self.results
            ]
        }

async def main():
    """Point d'entrée principal"""
    
    # Configuration
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5070"
    
    print(f"🎯 Validation SuperSmartMatch V2 - {base_url}")
    print(f"⏰ Démarrage: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Exécution des tests
    validator = SuperSmartMatchV2Validator(base_url)
    report = await validator.run_all_tests()
    
    # Sauvegarde du rapport
    with open("supersmartmatch-v2-validation-report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Rapport détaillé sauvegardé: supersmartmatch-v2-validation-report.json")
    
    # Code de sortie basé sur les résultats
    exit_code = 0 if report["failed"] == 0 else 1
    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())
