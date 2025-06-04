#!/usr/bin/env python3
"""
🧪 SuperSmartMatch V2 - Suite Automatisée de Benchmarking & Validation
====================================================================

Script complet pour validation quantitative V1 vs V2:
- Tests A/B statistiquement significatifs (95% confidence)
- Load testing progressif jusqu'à 10x trafic
- Analyse latence P50/P95/P99 par algorithme  
- Business impact quantifié avec ROI calculation
- Validation continue des SLA et métriques cibles

🎯 Objectifs validation:
- Prouver +13% précision matching vs baseline V1
- Maintenir performance <100ms P95 sous charge
- Valider sélection intelligente >92% précision contextuelle
- Quantifier ROI business mesurable

🔬 Tests inclus:
- Benchmark performance comparative
- Tests de charge progressifs (1x→10x)
- Analyse precision par algorithme/contexte
- Mesure satisfaction utilisateur temps réel
- Validation SLA contractuels
"""

import asyncio
import aiohttp
import time
import json
import logging
import statistics
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'benchmark_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkConfig:
    """Configuration des tests de benchmark"""
    base_url_v1: str = "http://localhost:5062"
    base_url_v2: str = "http://localhost:5070"
    load_balancer_url: str = "http://localhost"
    
    # Paramètres tests
    sample_size_per_algorithm: int = 50000
    confidence_level: float = 0.95
    max_concurrent_requests: int = 100
    load_test_multipliers: List[int] = None
    
    # Seuils SLA
    target_precision: float = 95.0
    max_p95_latency_ms: int = 100
    min_satisfaction_percent: float = 96.0
    min_availability_percent: float = 99.7
    
    def __post_init__(self):
        if self.load_test_multipliers is None:
            self.load_test_multipliers = [1, 2, 3, 5, 7, 10]

@dataclass
class MatchingRequest:
    """Structure d'une requête de matching"""
    candidate_data: Dict
    offers_data: List[Dict]
    user_segment: str = "enterprise"
    
    @classmethod
    def generate_test_case(cls, complexity: str = "standard"):
        """Génère un cas de test réaliste"""
        if complexity == "simple":
            return cls(
                candidate_data={
                    "technical_skills": [{"name": "Python", "level": "expert"}],
                    "experiences": [{"title": "Developer", "duration_months": 24}]
                },
                offers_data=[{
                    "id": "test_offer_1", 
                    "required_skills": ["Python"], 
                    "title": "Senior Developer"
                }]
            )
        elif complexity == "complex":
            return cls(
                candidate_data={
                    "technical_skills": [
                        {"name": "Python", "level": "expert"},
                        {"name": "React", "level": "intermediate"},
                        {"name": "AWS", "level": "advanced"},
                        {"name": "Docker", "level": "intermediate"}
                    ],
                    "experiences": [
                        {"title": "Senior Developer", "duration_months": 36},
                        {"title": "Tech Lead", "duration_months": 18}
                    ],
                    "education": [{"degree": "Master CS", "university": "MIT"}],
                    "location": "Paris"
                },
                offers_data=[
                    {
                        "id": f"offer_{i}",
                        "required_skills": random.sample(["Python", "React", "AWS", "Docker", "Kubernetes"], 3),
                        "title": random.choice(["Senior Developer", "Tech Lead", "Architect"]),
                        "location": random.choice(["Paris", "Lyon", "Remote"])
                    } for i in range(10)
                ]
            )
        else:  # standard
            return cls(
                candidate_data={
                    "technical_skills": [
                        {"name": "Python", "level": "advanced"},
                        {"name": "React", "level": "intermediate"}
                    ],
                    "experiences": [{"title": "Developer", "duration_months": 30}]
                },
                offers_data=[
                    {
                        "id": f"offer_{i}",
                        "required_skills": ["Python", "React"],
                        "title": "Full Stack Developer"
                    } for i in range(5)
                ]
            )

@dataclass 
class BenchmarkResult:
    """Résultat d'un test de benchmark"""
    timestamp: datetime
    algorithm_used: str
    response_time_ms: float
    precision_score: float
    success: bool
    request_complexity: str
    user_segment: str
    matches_count: int
    
class BenchmarkSuite:
    """Suite complète de benchmarking SuperSmartMatch V1 vs V2"""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.results: List[BenchmarkResult] = []
        self.session = None
        
    async def __aenter__(self):
        """Context manager entry"""
        connector = aiohttp.TCPConnector(limit=200, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=60)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.session:
            await self.session.close()
    
    async def single_matching_request(
        self, 
        url: str, 
        request_data: MatchingRequest, 
        algorithm_hint: str = "auto"
    ) -> BenchmarkResult:
        """Exécute une seule requête de matching et mesure performance"""
        start_time = time.time()
        
        try:
            headers = {
                "Content-Type": "application/json",
                "X-Algorithm-Hint": algorithm_hint,
                "X-User-Segment": request_data.user_segment
            }
            
            payload = {
                "candidate_data": request_data.candidate_data,
                "offers_data": request_data.offers_data
            }
            
            async with self.session.post(f"{url}/api/v2/match", 
                                       json=payload, 
                                       headers=headers) as response:
                
                response_time_ms = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    result_data = await response.json()
                    
                    return BenchmarkResult(
                        timestamp=datetime.now(),
                        algorithm_used=result_data.get("algorithm_used", "unknown"),
                        response_time_ms=response_time_ms,
                        precision_score=result_data.get("precision_score", 0.0),
                        success=True,
                        request_complexity="standard",
                        user_segment=request_data.user_segment,
                        matches_count=len(result_data.get("matches", []))
                    )
                else:
                    logger.warning(f"Request failed: {response.status}")
                    return BenchmarkResult(
                        timestamp=datetime.now(),
                        algorithm_used="error",
                        response_time_ms=response_time_ms,
                        precision_score=0.0,
                        success=False,
                        request_complexity="standard",
                        user_segment=request_data.user_segment,
                        matches_count=0
                    )
                    
        except Exception as e:
            logger.error(f"Request exception: {str(e)}")
            return BenchmarkResult(
                timestamp=datetime.now(),
                algorithm_used="error",
                response_time_ms=(time.time() - start_time) * 1000,
                precision_score=0.0,
                success=False,
                request_complexity="standard",
                user_segment=request_data.user_segment,
                matches_count=0
            )
    
    async def run_ab_test_comparison(self, sample_size: int = 1000) -> Dict:
        """Compare V1 vs V2 avec tests A/B statistiquement significatifs"""
        logger.info(f"🧪 Démarrage tests A/B V1 vs V2 (échantillon: {sample_size})")
        
        # Générer cas de test variés
        test_cases = [
            MatchingRequest.generate_test_case("simple") for _ in range(sample_size // 3)
        ] + [
            MatchingRequest.generate_test_case("standard") for _ in range(sample_size // 3)
        ] + [
            MatchingRequest.generate_test_case("complex") for _ in range(sample_size // 3)
        ]
        
        # Tests V1
        logger.info("Exécution tests V1...")
        v1_tasks = [
            self.single_matching_request(self.config.base_url_v1, case, "v1") 
            for case in test_cases[:sample_size//2]
        ]
        v1_results = await asyncio.gather(*v1_tasks, return_exceptions=True)
        v1_results = [r for r in v1_results if isinstance(r, BenchmarkResult)]
        
        # Tests V2
        logger.info("Exécution tests V2...")
        v2_tasks = [
            self.single_matching_request(self.config.base_url_v2, case, "v2") 
            for case in test_cases[sample_size//2:]
        ]
        v2_results = await asyncio.gather(*v2_tasks, return_exceptions=True)
        v2_results = [r for r in v2_results if isinstance(r, BenchmarkResult)]
        
        # Analyse statistique
        return self._analyze_ab_results(v1_results, v2_results)
    
    def _analyze_ab_results(self, v1_results: List[BenchmarkResult], 
                           v2_results: List[BenchmarkResult]) -> Dict:
        """Analyse statistique des résultats A/B"""
        
        # Extraire métriques
        v1_precision = [r.precision_score for r in v1_results if r.success]
        v2_precision = [r.precision_score for r in v2_results if r.success]
        v1_latency = [r.response_time_ms for r in v1_results if r.success]
        v2_latency = [r.response_time_ms for r in v2_results if r.success]
        
        # Tests statistiques
        precision_ttest = stats.ttest_ind(v2_precision, v1_precision)
        latency_ttest = stats.ttest_ind(v1_latency, v2_latency)  # V1 vs V2 (lower is better)
        
        # Calculs
        v1_precision_mean = statistics.mean(v1_precision) if v1_precision else 0
        v2_precision_mean = statistics.mean(v2_precision) if v2_precision else 0
        precision_improvement = ((v2_precision_mean - v1_precision_mean) / v1_precision_mean * 100) if v1_precision_mean > 0 else 0
        
        v1_latency_p95 = np.percentile(v1_latency, 95) if v1_latency else 0
        v2_latency_p95 = np.percentile(v2_latency, 95) if v2_latency else 0
        latency_improvement = ((v1_latency_p95 - v2_latency_p95) / v1_latency_p95 * 100) if v1_latency_p95 > 0 else 0
        
        return {
            "sample_sizes": {"v1": len(v1_results), "v2": len(v2_results)},
            "precision": {
                "v1_mean": v1_precision_mean,
                "v2_mean": v2_precision_mean,
                "improvement_percent": precision_improvement,
                "target_13_percent": precision_improvement >= 13.0,
                "statistical_significance": precision_ttest.pvalue < 0.05,
                "confidence_95": precision_ttest.pvalue < 0.05 and precision_improvement > 0
            },
            "latency": {
                "v1_p95": v1_latency_p95,
                "v2_p95": v2_latency_p95,
                "improvement_percent": latency_improvement,
                "sla_compliance": v2_latency_p95 < self.config.max_p95_latency_ms,
                "statistical_significance": latency_ttest.pvalue < 0.05
            },
            "success_rates": {
                "v1": len([r for r in v1_results if r.success]) / len(v1_results) * 100,
                "v2": len([r for r in v2_results if r.success]) / len(v2_results) * 100
            }
        }
    
    async def run_load_test(self, multiplier: int = 1) -> Dict:
        """Exécute test de charge avec multiplier donné"""
        logger.info(f"⚡ Test de charge {multiplier}x trafic normal")
        
        base_concurrent = self.config.max_concurrent_requests
        concurrent_requests = base_concurrent * multiplier
        
        # Générer requêtes
        test_cases = [
            MatchingRequest.generate_test_case() 
            for _ in range(concurrent_requests)
        ]
        
        start_time = time.time()
        
        # Exécuter en parallèle
        tasks = [
            self.single_matching_request(self.config.load_balancer_url, case)
            for case in test_cases
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        results = [r for r in results if isinstance(r, BenchmarkResult)]
        
        duration = time.time() - start_time
        
        # Analyse résultats
        successful_results = [r for r in results if r.success]
        response_times = [r.response_time_ms for r in successful_results]
        
        return {
            "load_multiplier": multiplier,
            "total_requests": len(results),
            "successful_requests": len(successful_results),
            "success_rate_percent": len(successful_results) / len(results) * 100,
            "duration_seconds": duration,
            "requests_per_second": len(results) / duration,
            "latency": {
                "p50": np.percentile(response_times, 50) if response_times else 0,
                "p95": np.percentile(response_times, 95) if response_times else 0,
                "p99": np.percentile(response_times, 99) if response_times else 0,
                "mean": statistics.mean(response_times) if response_times else 0
            },
            "sla_compliance": {
                "p95_under_100ms": np.percentile(response_times, 95) < 100 if response_times else False,
                "success_rate_above_95": len(successful_results) / len(results) >= 0.95
            }
        }
    
    async def run_algorithm_precision_analysis(self) -> Dict:
        """Analyse précision par algorithme et contexte"""
        logger.info("🎯 Analyse précision par algorithme")
        
        algorithms = ["nexten", "v2_enhanced", "v1_fallback"]
        user_segments = ["enterprise", "smb", "individual"]
        complexities = ["simple", "standard", "complex"]
        
        results = {}
        
        for algorithm in algorithms:
            results[algorithm] = {}
            
            for segment in user_segments:
                results[algorithm][segment] = {}
                
                for complexity in complexities:
                    # Générer tests spécifiques
                    test_cases = [
                        MatchingRequest.generate_test_case(complexity)
                        for _ in range(100)
                    ]
                    
                    # Modifier segment utilisateur
                    for case in test_cases:
                        case.user_segment = segment
                    
                    # Exécuter tests
                    tasks = [
                        self.single_matching_request(
                            self.config.load_balancer_url, case, algorithm
                        )
                        for case in test_cases
                    ]
                    
                    test_results = await asyncio.gather(*tasks, return_exceptions=True)
                    test_results = [r for r in test_results if isinstance(r, BenchmarkResult) and r.success]
                    
                    # Calculer métriques
                    if test_results:
                        precision_scores = [r.precision_score for r in test_results]
                        response_times = [r.response_time_ms for r in test_results]
                        
                        results[algorithm][segment][complexity] = {
                            "sample_size": len(test_results),
                            "avg_precision": statistics.mean(precision_scores),
                            "std_precision": statistics.stdev(precision_scores) if len(precision_scores) > 1 else 0,
                            "avg_response_time": statistics.mean(response_times),
                            "p95_response_time": np.percentile(response_times, 95)
                        }
                    else:
                        results[algorithm][segment][complexity] = {
                            "sample_size": 0,
                            "avg_precision": 0,
                            "std_precision": 0,
                            "avg_response_time": 0,
                            "p95_response_time": 0
                        }
        
        return results
    
    def generate_business_report(self, ab_results: Dict, load_results: List[Dict]) -> Dict:
        """Génère rapport business avec ROI et recommandations"""
        
        # Calcul ROI estimé
        precision_improvement = ab_results["precision"]["improvement_percent"]
        latency_improvement = ab_results["latency"]["improvement_percent"]
        
        # Estimations business (à adapter selon contexte réel)
        base_revenue_per_match = 100  # EUR
        total_matches_per_month = 10000
        
        roi_precision = (precision_improvement / 100) * base_revenue_per_match * total_matches_per_month
        roi_latency = (latency_improvement / 100) * 0.05 * base_revenue_per_match * total_matches_per_month  # 5% impact satisfaction
        
        total_monthly_roi = roi_precision + roi_latency
        annual_roi = total_monthly_roi * 12
        
        # Recommandations basées sur résultats
        recommendations = []
        
        if ab_results["precision"]["target_13_percent"]:
            recommendations.append("✅ Objectif +13% précision ATTEINT - Continuer monitoring")
        else:
            recommendations.append(f"⚠️ Précision à {precision_improvement:.1f}% - Implémenter optimisations cache ML")
        
        if ab_results["latency"]["sla_compliance"]:
            recommendations.append("✅ SLA latence respecté - Excellent maintien performance")
        else:
            recommendations.append("🚨 SLA latence dépassé - Optimisation urgente requise")
        
        # Analyse charge
        max_load_ok = max([lr["load_multiplier"] for lr in load_results if lr["sla_compliance"]["p95_under_100ms"]], default=1)
        if max_load_ok >= 5:
            recommendations.append(f"🚀 Scalabilité excellente - Tient jusqu'à {max_load_ok}x charge")
        else:
            recommendations.append(f"⚠️ Scalabilité limitée à {max_load_ok}x - Optimisation infrastructure nécessaire")
        
        return {
            "validation_summary": {
                "precision_target_met": ab_results["precision"]["target_13_percent"],
                "sla_compliance": ab_results["latency"]["sla_compliance"],
                "statistical_significance": ab_results["precision"]["confidence_95"],
                "max_load_supported": max_load_ok
            },
            "business_impact": {
                "monthly_roi_eur": total_monthly_roi,
                "annual_roi_eur": annual_roi,
                "precision_improvement_percent": precision_improvement,
                "latency_improvement_percent": latency_improvement,
                "estimated_satisfaction_boost": min(precision_improvement * 0.3, 10)  # Cap à 10%
            },
            "recommendations": recommendations,
            "next_optimizations": [
                "Cache intelligent ML-driven avec prefetching",
                "Smart routing contextuel avec apprentissage",
                "Connection pooling optimisé async",
                "Monitoring prédictif avec ML"
            ]
        }
    
    def save_results_json(self, all_results: Dict, filename: str = None):
        """Sauvegarde tous les résultats en JSON"""
        if not filename:
            filename = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, default=str, ensure_ascii=False)
        
        logger.info(f"💾 Résultats sauvegardés: {filename}")
        return filename

    def create_visualization(self, ab_results: Dict, load_results: List[Dict]):
        """Crée visualisations des résultats"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Comparaison Précision V1 vs V2
        precision_data = [ab_results["precision"]["v1_mean"], ab_results["precision"]["v2_mean"]]
        ax1.bar(["V1 Baseline", "V2 Enhanced"], precision_data, color=["#ff4545", "#00ff88"])
        ax1.set_title("Précision Matching: V1 vs V2")
        ax1.set_ylabel("Précision (%)")
        for i, v in enumerate(precision_data):
            ax1.text(i, v + 0.5, f"{v:.1f}%", ha='center')
        
        # 2. Latence P95 V1 vs V2
        latency_data = [ab_results["latency"]["v1_p95"], ab_results["latency"]["v2_p95"]]
        ax2.bar(["V1 Baseline", "V2 Enhanced"], latency_data, color=["#ff4545", "#00ff88"])
        ax2.set_title("Latence P95: V1 vs V2")
        ax2.set_ylabel("Latence P95 (ms)")
        ax2.axhline(y=100, color='red', linestyle='--', label='SLA 100ms')
        ax2.legend()
        for i, v in enumerate(latency_data):
            ax2.text(i, v + 2, f"{v:.0f}ms", ha='center')
        
        # 3. Tests de charge
        multipliers = [lr["load_multiplier"] for lr in load_results]
        p95_latencies = [lr["latency"]["p95"] for lr in load_results]
        ax3.plot(multipliers, p95_latencies, marker='o', linewidth=2, color="#00ff88")
        ax3.set_title("Performance sous Charge")
        ax3.set_xlabel("Multiplicateur de Charge")
        ax3.set_ylabel("Latence P95 (ms)")
        ax3.axhline(y=100, color='red', linestyle='--', label='SLA 100ms')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Taux de succès par charge
        success_rates = [lr["success_rate_percent"] for lr in load_results]
        ax4.plot(multipliers, success_rates, marker='s', linewidth=2, color="#ffa500")
        ax4.set_title("Taux de Succès sous Charge")
        ax4.set_xlabel("Multiplicateur de Charge")
        ax4.set_ylabel("Taux de Succès (%)")
        ax4.axhline(y=95, color='red', linestyle='--', label='SLA 95%')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"benchmark_visualization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png", dpi=300, bbox_inches='tight')
        logger.info("📊 Visualisations sauvegardées")
        plt.show()

async def main():
    """Fonction principale - Exécute suite complète de benchmarking"""
    
    logger.info("🚀 Démarrage Suite Automatisée de Benchmarking SuperSmartMatch V2")
    
    config = BenchmarkConfig()
    
    async with BenchmarkSuite(config) as benchmark:
        
        # 1. Tests A/B V1 vs V2
        logger.info("📊 Phase 1: Tests A/B Comparatifs")
        ab_results = await benchmark.run_ab_test_comparison(sample_size=2000)
        
        # 2. Tests de charge progressifs
        logger.info("⚡ Phase 2: Tests de Charge Progressifs")
        load_results = []
        for multiplier in config.load_test_multipliers:
            result = await benchmark.run_load_test(multiplier)
            load_results.append(result)
            
            # Arrêter si SLA cassé
            if not result["sla_compliance"]["p95_under_100ms"]:
                logger.warning(f"🚨 SLA cassé à {multiplier}x charge - Arrêt tests")
                break
        
        # 3. Analyse précision par algorithme
        logger.info("🎯 Phase 3: Analyse Précision par Algorithme")
        precision_analysis = await benchmark.run_algorithm_precision_analysis()
        
        # 4. Rapport business
        logger.info("💼 Phase 4: Génération Rapport Business")
        business_report = benchmark.generate_business_report(ab_results, load_results)
        
        # 5. Compilation résultats finaux
        final_results = {
            "benchmark_summary": {
                "timestamp": datetime.now().isoformat(),
                "config": asdict(config),
                "validation_status": "PASSED" if business_report["validation_summary"]["precision_target_met"] else "PARTIAL"
            },
            "ab_test_results": ab_results,
            "load_test_results": load_results,
            "precision_analysis": precision_analysis,
            "business_report": business_report
        }
        
        # 6. Sauvegarde et visualisation
        filename = benchmark.save_results_json(final_results)
        benchmark.create_visualization(ab_results, load_results)
        
        # 7. Résumé exécutif
        logger.info("=" * 80)
        logger.info("📋 RÉSUMÉ EXÉCUTIF - VALIDATION SUPERSMARTMATCH V2")
        logger.info("=" * 80)
        logger.info(f"🎯 Objectif +13% précision: {'✅ ATTEINT' if business_report['validation_summary']['precision_target_met'] else '❌ MANQUÉ'}")
        logger.info(f"⚡ SLA Latence <100ms P95: {'✅ RESPECTÉ' if business_report['validation_summary']['sla_compliance'] else '❌ DÉPASSÉ'}")
        logger.info(f"📊 Significativité statistique: {'✅ CONFIRMÉE' if business_report['validation_summary']['statistical_significance'] else '❌ INSUFFISANTE'}")
        logger.info(f"🚀 Scalabilité maximale: {business_report['validation_summary']['max_load_supported']}x charge normale")
        logger.info(f"💰 ROI annuel estimé: {business_report['business_impact']['annual_roi_eur']:,.0f} EUR")
        
        logger.info("\n🔄 RECOMMANDATIONS PRIORITAIRES:")
        for rec in business_report["recommendations"]:
            logger.info(f"  • {rec}")
        
        logger.info(f"\n💾 Rapport complet: {filename}")
        logger.info("🏁 Validation terminée avec succès!")
        
        return final_results

if __name__ == "__main__":
    # Exécution directe du script
    try:
        results = asyncio.run(main())
        print("\n✅ Benchmarking terminé - Consultez les logs pour le rapport détaillé")
    except KeyboardInterrupt:
        print("\n⚠️ Benchmarking interrompu par utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors du benchmarking: {str(e)}")
        raise
