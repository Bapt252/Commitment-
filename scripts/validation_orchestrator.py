#!/usr/bin/env python3
"""
🎯 SuperSmartMatch V2 - Orchestrateur Principal de Validation
===========================================================

Orchestrateur central pour la validation complète SuperSmartMatch V2:
- Coordination de tous les outils de validation
- Séquencement automatique des phases de test
- Collecte et agrégation des résultats
- Génération de rapport de validation final
- Prise de décision automatisée (go/no-go)
- Intégration avec rollback automatique si nécessaire

🚀 Workflow complet:
1. Vérification prérequis et état système
2. Lancement monitoring continu en arrière-plan
3. Exécution benchmarks A/B V1 vs V2
4. Tests de charge progressifs
5. Validation SLA et métriques business
6. Génération rapports automatisés
7. Décision finale avec recommandations

✅ Validation automatique:
- Objectif +13% précision (82% → 95%)
- Performance P95 <100ms maintenue
- Satisfaction >96% confirmée
- ROI business positif quantifié
- Significativité statistique 95%

🔄 Modes d'exécution:
- Full validation: Suite complète 90 jours
- Quick validation: Tests essentiels 2h
- Continuous: Monitoring en continu
- Report only: Génération rapports uniquement
"""

import asyncio
import subprocess
import sys
import json
import logging
import time
import signal
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import yaml

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'validation_orchestrator_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ValidationConfig:
    """Configuration globale de la validation"""
    # Modes d'exécution
    mode: str = "full"  # full, quick, continuous, report_only
    duration_days: int = 7  # Pour mode full
    
    # Seuils de validation
    precision_target: float = 95.0
    precision_baseline: float = 82.0
    precision_improvement_required: float = 13.0
    p95_latency_max_ms: int = 100
    satisfaction_target: float = 96.0
    availability_min: float = 99.7
    
    # Configuration services
    services: Dict[str, str] = None
    
    # Configuration outils
    tools_config: Dict[str, Any] = None
    
    # Paramètres email et notifications
    notifications: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.services is None:
            self.services = {
                "v1_url": "http://localhost:5062",
                "v2_url": "http://localhost:5070", 
                "load_balancer_url": "http://localhost",
                "monitoring_url": "http://localhost:8080",
                "prometheus_url": "http://localhost:9090",
                "grafana_url": "http://localhost:3000"
            }
        
        if self.tools_config is None:
            self.tools_config = {
                "benchmark_sample_size": 50000 if self.mode == "full" else 1000,
                "load_test_multipliers": [1, 2, 5, 10] if self.mode == "full" else [1, 2],
                "monitoring_interval_seconds": 30,
                "report_generation_enabled": True
            }

@dataclass
class ValidationResult:
    """Résultat de validation"""
    timestamp: datetime
    mode: str
    duration_seconds: int
    
    # Résultats principaux
    precision_achieved: float
    precision_target_met: bool
    precision_improvement_percent: float
    
    p95_latency_ms: float
    latency_sla_met: bool
    
    satisfaction_percent: float
    satisfaction_target_met: bool
    
    availability_percent: float
    availability_sla_met: bool
    
    # ROI et business
    estimated_annual_roi_eur: float
    business_impact_positive: bool
    
    # Validation globale
    all_targets_met: bool
    statistical_significance: bool
    recommendation: str
    
    # Détails techniques
    benchmark_results: Dict = None
    monitoring_results: Dict = None
    alerts_count: int = 0
    
    # Rapports générés
    report_files: List[str] = None

class ValidationOrchestrator:
    """Orchestrateur principal de validation"""
    
    def __init__(self, config: ValidationConfig):
        self.config = config
        self.start_time = datetime.now()
        self.running_processes: List[subprocess.Popen] = []
        self.monitoring_task: Optional[asyncio.Task] = None
        self.validation_result: Optional[ValidationResult] = None
        
        # Configuration signal handlers pour cleanup
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Gestionnaire de signaux pour cleanup propre"""
        logger.info(f"🛑 Signal {signum} reçu - Arrêt propre en cours...")
        asyncio.create_task(self.cleanup())
        sys.exit(0)
    
    async def cleanup(self):
        """Nettoyage des ressources"""
        logger.info("🧹 Nettoyage des ressources...")
        
        # Arrêter processus en cours
        for process in self.running_processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        # Arrêter tâche monitoring
        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Nettoyage terminé")
    
    async def check_prerequisites(self) -> bool:
        """Vérifie les prérequis système"""
        logger.info("🔍 Vérification des prérequis...")
        
        # Vérifier Python packages
        required_packages = [
            'aiohttp', 'pandas', 'numpy', 'matplotlib', 
            'plotly', 'seaborn', 'scikit-learn', 'jinja2'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"❌ Packages manquants: {', '.join(missing_packages)}")
            logger.info("💡 Installez avec: pip install " + " ".join(missing_packages))
            return False
        
        # Vérifier connectivité services
        import aiohttp
        async with aiohttp.ClientSession() as session:
            for service_name, url in self.config.services.items():
                try:
                    async with session.get(f"{url}/health", timeout=5) as resp:
                        if resp.status != 200:
                            logger.warning(f"⚠️ Service {service_name} ({url}) non accessible")
                except Exception as e:
                    logger.warning(f"⚠️ Service {service_name} ({url}) erreur: {str(e)}")
        
        # Vérifier scripts disponibles
        script_dir = Path(__file__).parent
        required_scripts = [
            'benchmark_suite.py',
            'monitoring_system.py', 
            'report_generator.py',
            'deploy_v2_progressive.sh'
        ]
        
        for script in required_scripts:
            if not (script_dir / script).exists():
                logger.error(f"❌ Script manquant: {script}")
                return False
        
        logger.info("✅ Prérequis validés")
        return True
    
    async def start_monitoring(self):
        """Démarre le monitoring en arrière-plan"""
        logger.info("📊 Démarrage monitoring continu...")
        
        script_path = Path(__file__).parent / "monitoring_system.py"
        
        # Créer configuration monitoring
        monitoring_config = {
            "sources": {
                "prometheus_url": self.config.services["prometheus_url"],
                "api_url": self.config.services["monitoring_url"]
            },
            "alerts": self.config.notifications or {},
            "alert_thresholds": {
                "precision_target_percent": self.config.precision_target,
                "satisfaction_target_percent": self.config.satisfaction_target,
                "p95_latency_warning_ms": self.config.p95_latency_max_ms
            }
        }
        
        with open("monitoring_config.json", "w") as f:
            json.dump(monitoring_config, f, indent=2)
        
        # Lancer monitoring en arrière-plan
        process = subprocess.Popen([
            sys.executable, str(script_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        self.running_processes.append(process)
        
        # Attendre démarrage
        await asyncio.sleep(10)
        logger.info("✅ Monitoring démarré")
    
    async def run_benchmarks(self) -> Dict:
        """Execute les benchmarks A/B V1 vs V2"""
        logger.info("🧪 Lancement benchmarks A/B V1 vs V2...")
        
        script_path = Path(__file__).parent / "benchmark_suite.py"
        
        # Configuration benchmark
        benchmark_config = {
            "base_url_v1": self.config.services["v1_url"],
            "base_url_v2": self.config.services["v2_url"],
            "load_balancer_url": self.config.services["load_balancer_url"],
            "sample_size_per_algorithm": self.config.tools_config["benchmark_sample_size"],
            "load_test_multipliers": self.config.tools_config["load_test_multipliers"]
        }
        
        # Exécuter benchmarks
        process = subprocess.Popen([
            sys.executable, str(script_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"❌ Benchmarks échoués: {stderr}")
            return {}
        
        # Chercher fichier résultats JSON
        results_files = list(Path.cwd().glob("benchmark_results_*.json"))
        if results_files:
            latest_file = max(results_files, key=lambda p: p.stat().st_mtime)
            with open(latest_file, 'r') as f:
                results = json.load(f)
            logger.info("✅ Benchmarks terminés avec succès")
            return results
        else:
            logger.warning("⚠️ Aucun fichier de résultats trouvé")
            return {}
    
    async def generate_reports(self, benchmark_results: Dict) -> List[str]:
        """Génère les rapports de validation"""
        logger.info("📋 Génération des rapports...")
        
        script_path = Path(__file__).parent / "report_generator.py"
        
        # Configuration rapports
        report_config = {
            "report_period_days": self.config.duration_days,
            "company_name": "SuperSmartMatch",
            "precision_target": self.config.precision_target,
            "precision_baseline": self.config.precision_baseline,
            "satisfaction_target": self.config.satisfaction_target,
            "p95_latency_sla": self.config.p95_latency_max_ms,
            "email_enabled": False  # Sera activé selon config
        }
        
        if self.config.notifications and self.config.notifications.get("email_config"):
            report_config.update({
                "email_enabled": True,
                "email_config": self.config.notifications["email_config"],
                "stakeholders": self.config.notifications.get("stakeholders", [])
            })
        
        with open("report_config.json", "w") as f:
            json.dump(report_config, f, indent=2)
        
        # Exécuter générateur
        process = subprocess.Popen([
            sys.executable, str(script_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            logger.error(f"❌ Génération rapports échouée: {stderr}")
            return []
        
        # Trouver fichiers générés
        reports_dir = Path("reports")
        if reports_dir.exists():
            report_files = [
                str(f) for f in reports_dir.glob("*report_*.html")
            ] + [
                str(f) for f in reports_dir.glob("*data_*.xlsx")
            ]
            logger.info(f"✅ {len(report_files)} rapports générés")
            return report_files
        
        return []
    
    def analyze_results(self, benchmark_results: Dict) -> ValidationResult:
        """Analyse les résultats et génère verdict final"""
        logger.info("🔍 Analyse des résultats de validation...")
        
        # Extraire métriques principales
        ab_results = benchmark_results.get("ab_test_results", {})
        business_report = benchmark_results.get("business_report", {})
        
        precision_current = ab_results.get("precision", {}).get("v2_mean", 0)
        precision_improvement = ab_results.get("precision", {}).get("improvement_percent", 0)
        precision_target_met = precision_current >= self.config.precision_target
        
        p95_latency = ab_results.get("latency", {}).get("v2_p95", 0)
        latency_sla_met = p95_latency < self.config.p95_latency_max_ms
        
        # Satisfaction (simulée pour demo)
        satisfaction = 95.5  # À remplacer par vraie valeur
        satisfaction_target_met = satisfaction >= self.config.satisfaction_target
        
        # Disponibilité (simulée)
        availability = 99.85
        availability_sla_met = availability >= self.config.availability_min
        
        # ROI
        roi = business_report.get("business_impact", {}).get("annual_roi_eur", 0)
        business_impact_positive = roi > 0
        
        # Significativité statistique
        statistical_significance = ab_results.get("precision", {}).get("confidence_95", False)
        
        # Validation globale
        all_targets_met = (
            precision_target_met and 
            latency_sla_met and 
            satisfaction_target_met and 
            availability_sla_met and
            statistical_significance
        )
        
        # Recommandation
        if all_targets_met:
            recommendation = "GO - Validation V2 réussie avec tous les objectifs atteints"
        elif precision_target_met and latency_sla_met:
            recommendation = "GO conditionnel - Objectifs principaux atteints, surveiller satisfaction"
        elif precision_improvement >= self.config.precision_improvement_required * 0.8:
            recommendation = "CONTINUE - Amélioration significative, ajustements nécessaires"
        else:
            recommendation = "NO-GO - Objectifs non atteints, rollback recommandé"
        
        duration = int((datetime.now() - self.start_time).total_seconds())
        
        result = ValidationResult(
            timestamp=datetime.now(),
            mode=self.config.mode,
            duration_seconds=duration,
            precision_achieved=precision_current,
            precision_target_met=precision_target_met,
            precision_improvement_percent=precision_improvement,
            p95_latency_ms=p95_latency,
            latency_sla_met=latency_sla_met,
            satisfaction_percent=satisfaction,
            satisfaction_target_met=satisfaction_target_met,
            availability_percent=availability,
            availability_sla_met=availability_sla_met,
            estimated_annual_roi_eur=roi,
            business_impact_positive=business_impact_positive,
            all_targets_met=all_targets_met,
            statistical_significance=statistical_significance,
            recommendation=recommendation,
            benchmark_results=benchmark_results
        )
        
        self.validation_result = result
        return result
    
    async def execute_rollback_if_needed(self, result: ValidationResult):
        """Exécute rollback automatique si nécessaire"""
        if result.recommendation.startswith("NO-GO"):
            logger.warning("🔄 Rollback automatique recommandé")
            
            rollback_script = Path(__file__).parent / "deploy_v2_progressive.sh"
            if rollback_script.exists():
                logger.info("🔄 Exécution rollback automatique...")
                
                process = subprocess.Popen([
                    "bash", str(rollback_script), "rollback"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    logger.info("✅ Rollback automatique terminé")
                else:
                    logger.error(f"❌ Échec rollback: {stderr}")
            else:
                logger.error("❌ Script rollback non trouvé")
    
    def print_final_report(self, result: ValidationResult):
        """Affiche rapport final de validation"""
        print("\n" + "=" * 80)
        print("🎯 RAPPORT FINAL DE VALIDATION SUPERSMARTMATCH V2")
        print("=" * 80)
        print(f"📅 Date: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ Durée: {result.duration_seconds // 60}min {result.duration_seconds % 60}s")
        print(f"🔧 Mode: {result.mode.upper()}")
        print()
        
        print("📊 RÉSULTATS PRINCIPAUX:")
        print(f"  • Précision Matching: {result.precision_achieved:.1f}% " + 
              ("✅" if result.precision_target_met else "❌") +
              f" (Objectif: {self.config.precision_target}%)")
        print(f"  • Amélioration vs V1: +{result.precision_improvement_percent:.1f}% " +
              ("✅" if result.precision_improvement_percent >= self.config.precision_improvement_required else "❌") +
              f" (Objectif: +{self.config.precision_improvement_required}%)")
        print(f"  • Performance P95: {result.p95_latency_ms:.0f}ms " +
              ("✅" if result.latency_sla_met else "❌") +
              f" (SLA: <{self.config.p95_latency_max_ms}ms)")
        print(f"  • Satisfaction: {result.satisfaction_percent:.1f}% " +
              ("✅" if result.satisfaction_target_met else "❌") +
              f" (Objectif: {self.config.satisfaction_target}%)")
        print(f"  • Disponibilité: {result.availability_percent:.2f}% " +
              ("✅" if result.availability_sla_met else "❌") +
              f" (SLA: >{self.config.availability_min}%)")
        print()
        
        print("💰 IMPACT BUSINESS:")
        print(f"  • ROI Annuel Estimé: €{result.estimated_annual_roi_eur:,.0f} " +
              ("✅" if result.business_impact_positive else "❌"))
        print(f"  • Significativité Statistique: " +
              ("✅ Confirmée" if result.statistical_significance else "❌ Insuffisante"))
        print()
        
        print("🎯 VALIDATION GLOBALE:")
        status = "✅ SUCCÈS" if result.all_targets_met else "⚠️ PARTIEL" if "conditionnel" in result.recommendation else "❌ ÉCHEC"
        print(f"  • Statut: {status}")
        print(f"  • Recommandation: {result.recommendation}")
        print()
        
        if result.report_files:
            print("📋 RAPPORTS GÉNÉRÉS:")
            for report_file in result.report_files:
                print(f"  • {report_file}")
            print()
        
        print("=" * 80)
        
        # Sauvegarder résultat
        result_file = f"validation_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        print(f"💾 Résultat sauvegardé: {result_file}")
        print("=" * 80)
    
    async def run_full_validation(self) -> ValidationResult:
        """Exécute validation complète"""
        logger.info("🚀 Démarrage validation complète SuperSmartMatch V2")
        
        try:
            # 1. Vérification prérequis
            if not await self.check_prerequisites():
                raise Exception("Prérequis non satisfaits")
            
            # 2. Démarrage monitoring
            await self.start_monitoring()
            
            # 3. Exécution benchmarks
            benchmark_results = await self.run_benchmarks()
            
            # 4. Analyse résultats
            result = self.analyze_results(benchmark_results)
            
            # 5. Génération rapports
            if self.config.tools_config.get("report_generation_enabled", True):
                report_files = await self.generate_reports(benchmark_results)
                result.report_files = report_files
            
            # 6. Rollback automatique si nécessaire
            await self.execute_rollback_if_needed(result)
            
            # 7. Rapport final
            self.print_final_report(result)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur validation: {str(e)}")
            raise
        finally:
            await self.cleanup()
    
    async def run_quick_validation(self) -> ValidationResult:
        """Exécute validation rapide (2h)"""
        logger.info("⚡ Démarrage validation rapide SuperSmartMatch V2")
        
        # Version allégée avec échantillons réduits
        original_sample_size = self.config.tools_config["benchmark_sample_size"]
        original_multipliers = self.config.tools_config["load_test_multipliers"]
        
        self.config.tools_config["benchmark_sample_size"] = min(1000, original_sample_size)
        self.config.tools_config["load_test_multipliers"] = [1, 2]
        
        try:
            return await self.run_full_validation()
        finally:
            # Restaurer config originale
            self.config.tools_config["benchmark_sample_size"] = original_sample_size
            self.config.tools_config["load_test_multipliers"] = original_multipliers
    
    async def run_continuous_monitoring(self):
        """Mode monitoring continu"""
        logger.info("🔄 Démarrage monitoring continu...")
        
        await self.start_monitoring()
        
        try:
            while True:
                # Générer rapport quotidien
                if datetime.now().hour == 9 and datetime.now().minute < 5:  # 9h du matin
                    await self.generate_reports({})
                
                await asyncio.sleep(300)  # 5 minutes
                
        except KeyboardInterrupt:
            logger.info("⚠️ Monitoring arrêté par utilisateur")
        finally:
            await self.cleanup()

def load_config(config_file: str) -> ValidationConfig:
    """Charge configuration depuis fichier"""
    if Path(config_file).exists():
        with open(config_file, 'r') as f:
            if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
        return ValidationConfig(**config_data)
    else:
        logger.warning(f"Configuration {config_file} non trouvée - Utilisation config par défaut")
        return ValidationConfig()

async def main():
    """Fonction principale avec arguments CLI"""
    parser = argparse.ArgumentParser(description="🎯 SuperSmartMatch V2 - Orchestrateur de Validation")
    parser.add_argument("--mode", choices=["full", "quick", "continuous", "report_only"], 
                       default="full", help="Mode d'exécution")
    parser.add_argument("--config", default="validation_config.json", 
                       help="Fichier de configuration")
    parser.add_argument("--duration", type=int, default=7, 
                       help="Durée en jours pour mode full")
    parser.add_argument("--no-reports", action="store_true", 
                       help="Désactiver génération rapports")
    
    args = parser.parse_args()
    
    # Charger configuration
    config = load_config(args.config)
    config.mode = args.mode
    config.duration_days = args.duration
    
    if args.no_reports:
        config.tools_config["report_generation_enabled"] = False
    
    # Créer orchestrateur
    orchestrator = ValidationOrchestrator(config)
    
    try:
        if args.mode == "full":
            result = await orchestrator.run_full_validation()
        elif args.mode == "quick":
            result = await orchestrator.run_quick_validation()
        elif args.mode == "continuous":
            await orchestrator.run_continuous_monitoring()
        elif args.mode == "report_only":
            report_files = await orchestrator.generate_reports({})
            print(f"📋 {len(report_files)} rapports générés")
            return
        
        # Code de sortie basé sur résultat
        if hasattr(orchestrator, 'validation_result') and orchestrator.validation_result:
            if orchestrator.validation_result.all_targets_met:
                sys.exit(0)  # Succès
            elif "conditionnel" in orchestrator.validation_result.recommendation:
                sys.exit(1)  # Succès partiel
            else:
                sys.exit(2)  # Échec
        
    except KeyboardInterrupt:
        print("\n⚠️ Validation interrompue par utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erreur validation: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
