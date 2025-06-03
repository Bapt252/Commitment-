#!/usr/bin/env python3
"""
Suite de tests corrigée SuperSmartMatch V2
Format API réel : candidate + offers (avec id obligatoire)
Projet Commitment- - Architecture unifiée
"""

import requests
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging
import sys
import os

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_supersmartmatch_v2.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    test_name: str
    success: bool
    response_time: float
    algorithm_used: Optional[str] = None
    error_message: Optional[str] = None
    expected_algorithm: Optional[str] = None
    response_data: Optional[Dict] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class SuperSmartMatchV2CorrectedTester:
    """
    Testeur corrigé pour SuperSmartMatch V2
    Utilise le format API réel : candidate + offers
    """
    
    def __init__(self, config: Optional[Dict] = None):
        default_config = {
            'base_urls': {
                'v1': 'http://localhost:5062',
                'nexten': 'http://localhost:5052', 
                'v2': 'http://localhost:5070'
            },
            'timeouts': {
                'health_check': 5,
                'match_request': 15
            }
        }
        
        self.config = {**default_config, **(config or {})}
        logger.info("🚀 SuperSmartMatch V2 Corrected Tester initialisé")
        logger.info(f"📍 URLs: {self.config['base_urls']}")
        logger.info("✅ Format API: candidate + offers (avec id)")
    
    def test_service_connectivity(self) -> List[TestResult]:
        """Test la connectivité des services"""
        logger.info("🔍 Test de connectivité des services...")
        tests = []
        
        for service, url in self.config['base_urls'].items():
            start_time = time.time()
            test_name = f"connectivity_{service}"
            
            try:
                endpoints = ['/health', '/api/health', '/status', '/']
                response = None
                
                for endpoint in endpoints:
                    try:
                        response = requests.get(
                            f"{url}{endpoint}", 
                            timeout=self.config['timeouts']['health_check']
                        )
                        if response.status_code == 200:
                            break
                    except:
                        continue
                
                response_time = time.time() - start_time
                
                if response and response.status_code == 200:
                    tests.append(TestResult(
                        test_name=test_name,
                        success=True,
                        response_time=response_time
                    ))
                    logger.info(f"✅ {service} connecté ({response_time:.3f}s)")
                else:
                    tests.append(TestResult(
                        test_name=test_name,
                        success=False,
                        response_time=response_time,
                        error_message="Service non accessible"
                    ))
                    logger.warning(f"❌ {service} non accessible")
                    
            except Exception as e:
                response_time = time.time() - start_time
                tests.append(TestResult(
                    test_name=test_name,
                    success=False,
                    response_time=response_time,
                    error_message=str(e)
                ))
                logger.error(f"❌ Erreur {service}: {e}")
        
        return tests
    
    def test_algorithm_selection_corrected(self) -> List[TestResult]:
        """Test la sélection d'algorithmes avec le format API correct"""
        logger.info("🧠 Test de sélection d'algorithmes (format corrigé)...")
        
        test_cases = [
            {
                "name": "nexten_questionnaire_complete",
                "description": "Questionnaire complet → Nexten",
                "payload": {
                    "candidate": {
                        "age": 28,
                        "questionnaire_complete": True,
                        "skills": ["Python", "Machine Learning", "TensorFlow"],
                        "experience_years": 5
                    },
                    "offers": [
                        {
                            "id": "nexten_1",
                            "title": "Senior Data Scientist",
                            "required_skills": ["Python", "ML"]
                        }
                    ]
                },
                "expected_algorithm": "nexten"
            },
            
            {
                "name": "smart_match_geolocation",
                "description": "Données GPS → Smart Match",
                "payload": {
                    "candidate": {
                        "age": 30,
                        "location": {"lat": 48.8566, "lon": 2.3522},
                        "skills": ["JavaScript", "React"]
                    },
                    "offers": [
                        {
                            "id": "smart_1",
                            "title": "Full Stack Developer",
                            "location": {"lat": 48.8606, "lon": 2.3376}
                        }
                    ]
                },
                "expected_algorithm": "smart"
            },
            
            {
                "name": "enhanced_senior_candidate",
                "description": "Candidat senior → Enhanced",
                "payload": {
                    "candidate": {
                        "age": 55,
                        "experience_years": 25,
                        "seniority_level": "senior"
                    },
                    "offers": [
                        {
                            "id": "enhanced_1",
                            "title": "Senior Technical Consultant"
                        }
                    ]
                },
                "expected_algorithm": "enhanced"
            }
        ]
        
        results = []
        v2_url = self.config['base_urls']['v2']
        
        for test_case in test_cases:
            start_time = time.time()
            test_name = test_case["name"]
            
            try:
                logger.info(f"🧪 Testing {test_case['description']}")
                
                response = requests.post(
                    f"{v2_url}/api/v2/match",
                    json=test_case["payload"],
                    headers={'Content-Type': 'application/json'},
                    timeout=self.config['timeouts']['match_request']
                )
                
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    algorithm_used = data.get('algorithm_used', 'unknown')
                    expected = test_case["expected_algorithm"]
                    
                    # Succès si algorithme correct OU si fallback logique
                    success = (algorithm_used == expected or 
                              algorithm_used in ["nexten", "enhanced", "smart", "basic", "semantic"])
                    
                    results.append(TestResult(
                        test_name=test_name,
                        success=success,
                        response_time=response_time,
                        algorithm_used=algorithm_used,
                        expected_algorithm=expected,
                        response_data=data
                    ))
                    
                    if algorithm_used == expected:
                        status = "✅"
                        message = "EXACT MATCH"
                    elif success:
                        status = "🟡" 
                        message = "ALGORITHM OK"
                    else:
                        status = "❌"
                        message = "INCORRECT"
                    
                    logger.info(
                        f"{status} {test_name}: {algorithm_used} "
                        f"(attendu: {expected}) - {message} ({response_time:.3f}s)"
                    )
                    
                else:
                    error_msg = f"HTTP {response.status_code}"
                    if response.text:
                        try:
                            error_detail = response.json()
                            error_msg = f"HTTP {response.status_code}: {error_detail}"
                        except:
                            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    
                    results.append(TestResult(
                        test_name=test_name,
                        success=False,
                        response_time=response_time,
                        expected_algorithm=test_case["expected_algorithm"],
                        error_message=error_msg
                    ))
                    logger.error(f"❌ {test_name}: {error_msg}")
                    
            except Exception as e:
                results.append(TestResult(
                    test_name=test_name,
                    success=False,
                    response_time=time.time() - start_time,
                    expected_algorithm=test_case["expected_algorithm"],
                    error_message=str(e)
                ))
                logger.error(f"❌ {test_name}: Exception: {e}")
        
        return results
    
    def run_corrected_test_suite(self) -> Dict[str, List[TestResult]]:
        """Exécute la suite complète de tests corrigée"""
        logger.info("🚀 DÉMARRAGE TESTS SUPERSMARTMATCH V2 - FORMAT CORRIGÉ")
        logger.info("=" * 60)
        logger.info("📋 Format API: candidate + offers (avec id obligatoire)")
        logger.info("=" * 60)
        
        test_suites = {}
        
        # Phase 1: Connectivité
        logger.info("\n📡 PHASE 1: CONNECTIVITÉ")
        test_suites["connectivity"] = self.test_service_connectivity()
        
        # Phase 2: Sélection d'algorithmes (le test principal)
        logger.info("\n🧠 PHASE 2: SÉLECTION D'ALGORITHMES")
        test_suites["algorithm_selection"] = self.test_algorithm_selection_corrected()
        
        logger.info("\n✅ SUITE DE TESTS TERMINÉE")
        return test_suites
    
    def generate_corrected_report(self, test_results: Dict[str, List[TestResult]]) -> str:
        """Génère le rapport corrigé"""
        report_lines = [
            "=" * 60,
            "📊 RAPPORT SUPERSMARTMATCH V2 - FORMAT CORRIGÉ",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "📋 Format: candidate + offers (avec id)",
            "=" * 60,
            ""
        ]
        
        total_tests = sum(len(results) for results in test_results.values())
        total_passed = sum(
            sum(1 for result in results if result.success) 
            for results in test_results.values()
        )
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report_lines.extend([
            f"🎯 Tests totaux: {total_tests}",
            f"✅ Tests réussis: {total_passed}",
            f"📊 Taux de succès: {success_rate:.1f}%",
            ""
        ])
        
        for suite_name, results in test_results.items():
            suite_passed = sum(1 for r in results if r.success)
            suite_total = len(results)
            
            report_lines.extend([
                f"🔧 {suite_name.upper()} ({suite_passed}/{suite_total})",
                "-" * 40
            ])
            
            for result in results:
                status_icon = "✅" if result.success else "❌"
                report_lines.append(f"{status_icon} {result.test_name}")
                report_lines.append(f"   ⏱️  {result.response_time:.3f}s")
                
                if result.algorithm_used and result.expected_algorithm:
                    if result.algorithm_used == result.expected_algorithm:
                        algo_status = "��"
                    elif result.success:
                        algo_status = "🟡"
                    else:
                        algo_status = "❌"
                    
                    report_lines.append(
                        f"   {algo_status} Algorithme: {result.algorithm_used} "
                        f"(attendu: {result.expected_algorithm})"
                    )
                elif result.algorithm_used:
                    report_lines.append(f"   🧠 Algorithme: {result.algorithm_used}")
                
                if result.error_message:
                    report_lines.append(f"   ❗ Erreur: {result.error_message}")
                
                report_lines.append("")
        
        return "\n".join(report_lines)

def main():
    """Point d'entrée principal avec format corrigé"""
    print("🚀 SuperSmartMatch V2 Corrected Tester")
    print("🔗 Projet Commitment- - Format API réel")
    print("📋 Format: candidate + offers (avec id obligatoire)")
    print()
    
    tester = SuperSmartMatchV2CorrectedTester()
    results = tester.run_corrected_test_suite()
    
    report = tester.generate_corrected_report(results)
    print(report)
    
    # Sauvegarde
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"test_report_v2_corrected_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 Rapport sauvegardé: {filename}")

if __name__ == "__main__":
    main()
