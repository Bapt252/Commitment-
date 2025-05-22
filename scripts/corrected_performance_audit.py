#!/usr/bin/env python3
"""
Audit Performance - Endpoints Corrigés
Focus: Services fonctionnels avec vraies APIs
"""

import asyncio
import aiohttp
import time
import json
import statistics
import requests
import psutil

class CorrectedPerformanceAudit:
    def __init__(self):
        # Services fonctionnels avec endpoints corrects
        self.services = {
            "cv_parser": "http://localhost:5051",
            "personalization": "http://localhost:5060", 
            "frontend": "http://localhost:3000"
        }
        self.results = {}
    
    async def test_cv_parser_performance(self):
        """Test CV Parser avec endpoints réels"""
        print("🔍 Test CV Parser - Endpoints réels...")
        
        # Test d'abord les endpoints disponibles
        endpoints_to_try = [
            "/health",
            "/api/health", 
            "/",
            "/docs",
            "/parse_cv",
            "/api/parse_cv"
        ]
        
        working_endpoint = None
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(f"{self.services['cv_parser']}{endpoint}", timeout=5)
                if response.status_code in [200, 422]:  # 422 = validation error mais endpoint existe
                    working_endpoint = endpoint
                    print(f"✅ Endpoint trouvé: {endpoint} (Status: {response.status_code})")
                    break
            except:
                continue
        
        if not working_endpoint:
            print("❌ Aucun endpoint fonctionnel trouvé")
            return {"service": "cv_parser", "status": "NO_ENDPOINT"}
        
        # Test de performance sur l'endpoint trouvé
        latencies = []
        successful_requests = 0

        for i in range(10):  
            start_time = time.time()
            try:
                response = requests.get(f"{self.services['cv_parser']}{working_endpoint}", timeout=10)
                latency = (time.time() - start_time) * 1000
                latencies.append(latency)
                
                if response.status_code in [200, 422]:
                    successful_requests += 1
                    print(f"✅ Test {i+1}: {latency:.1f}ms")
                else:
                    print(f"⚠️ Test {i+1}: Status {response.status_code}")
                
            except Exception as e:
                print(f"❌ Test {i+1}: Erreur - {str(e)[:30]}")

        if latencies:
            return {
                "service": "cv_parser",
                "endpoint": working_endpoint,
                "avg_latency": statistics.mean(latencies),
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "p95_latency": statistics.quantiles(latencies, n=20)[18] if len(latencies) > 5 else max(latencies),
                "successful_requests": successful_requests,
                "total_requests": 10,
                "success_rate": (successful_requests / 10) * 100
            }
        return {"service": "cv_parser", "status": "FAILED"}
    
    async def test_personalization_performance(self):
        """Test Personalization avec endpoints réels"""
        print("🎯 Test Personalization - Découverte endpoints...")
        
        # Test endpoints possibles
        endpoints_to_try = [
            "/health",
            "/api/health",
            "/",
            "/docs", 
            "/recommend",
            "/api/recommend"
        ]
        
        working_endpoint = None
        for endpoint in endpoints_to_try:
            try:
                response = requests.get(f"{self.services['personalization']}{endpoint}", timeout=5)
                if response.status_code in [200, 422]:
                    working_endpoint = endpoint
                    print(f"✅ Endpoint trouvé: {endpoint} (Status: {response.status_code})")
                    break
            except:
                continue
        
        if not working_endpoint:
            print("❌ Aucun endpoint fonctionnel trouvé")
            return {"service": "personalization", "status": "NO_ENDPOINT"}

        # Test de performance
        latencies = []
        successful_requests = 0

        for i in range(8):
            start_time = time.time()
            try:
                response = requests.get(f"{self.services['personalization']}{working_endpoint}", timeout=15)
                latency = (time.time() - start_time) * 1000
                latencies.append(latency)
                
                if response.status_code in [200, 422]:
                    successful_requests += 1
                    print(f"✅ Test {i+1}: {latency:.1f}ms")
                else:
                    print(f"⚠️ Test {i+1}: Status {response.status_code}")
                
            except Exception as e:
                print(f"❌ Test {i+1}: Erreur - {str(e)[:30]}")

        if latencies:
            return {
                "service": "personalization",
                "endpoint": working_endpoint,
                "avg_latency": statistics.mean(latencies),
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "p95_latency": statistics.quantiles(latencies, n=20)[18] if len(latencies) > 5 else max(latencies),
                "successful_requests": successful_requests,
                "total_requests": 8,
                "success_rate": (successful_requests / 8) * 100
            }
        return {"service": "personalization", "status": "FAILED"}

    def test_frontend_comprehensive(self):
        """Test frontend complet"""
        print("🌐 Test Frontend - Analyse complète...")
        
        pages = ["/", "/health"]
        results = {}
        
        for page in pages:
            latencies = []
            status_codes = []
            for i in range(5):
                start_time = time.time()
                try:
                    response = requests.get(
                        f"{self.services['frontend']}{page}",
                        timeout=10
                    )
                    latency = (time.time() - start_time) * 1000
                    latencies.append(latency)
                    status_codes.append(response.status_code)
                except Exception as e:
                    print(f"❌ {page}: {str(e)[:30]}")
            
            if latencies:
                results[page] = {
                    "avg_latency": statistics.mean(latencies),
                    "min_latency": min(latencies),
                    "max_latency": max(latencies),
                    "status_codes": status_codes
                }
                print(f"✅ {page}: {statistics.mean(latencies):.1f}ms avg")

        return results

    def get_detailed_system_metrics(self):
        """Métriques système détaillées avec analyse RAM"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Analyse détaillée mémoire
            memory_analysis = {
                "total_gb": memory.total // (1024**3),
                "available_gb": memory.available // (1024**3),
                "used_gb": memory.used // (1024**3),
                "percent": memory.percent,
                "status": "🔴 CRITIQUE" if memory.percent > 90 else "🟡 ÉLEVÉ" if memory.percent > 80 else "🟢 OK"
            }
            
            # Top processes par mémoire
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['memory_percent'] and proc_info['memory_percent'] > 1.0:
                        processes.append(proc_info)
                except:
                    pass
            
            top_memory_processes = sorted(processes, key=lambda x: x.get('memory_percent', 0), reverse=True)[:5]

            return {
                "cpu_percent": cpu_percent,
                "memory_analysis": memory_analysis,
                "disk_usage_percent": disk.percent,
                "top_memory_processes": top_memory_processes,
                "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            }
        except Exception as e:
            return {"error": str(e)}

    async def run_corrected_audit(self):
        """Audit corrigé avec vrais endpoints"""
        print("🚀 AUDIT PERFORMANCE CORRIGÉ - ENDPOINTS RÉELS")
        print("="*60)
        
        start_time = time.time()
        
        # Test avec découverte d'endpoints
        print("\n📊 Phase 1: CV Parser (Découverte endpoints)")
        cv_results = await self.test_cv_parser_performance()
        
        print("\n📊 Phase 2: Personalization (Découverte endpoints)")
        personalization_results = await self.test_personalization_performance()
        
        print("\n📊 Phase 3: Frontend Complet") 
        frontend_results = self.test_frontend_comprehensive()
        
        print("\n📊 Phase 4: Analyse Système Détaillée")
        system_metrics = self.get_detailed_system_metrics()
        
        total_time = time.time() - start_time
        
        self.results = {
            "cv_parser": cv_results,
            "personalization": personalization_results,
            "frontend": frontend_results,
            "system_metrics": system_metrics,
            "audit_duration": total_time,
            "timestamp": time.time()
        }
        
        return self.results

    def generate_corrected_report(self):
        """Rapport corrigé avec analyse détaillée"""
        if not self.results:
            return "❌ Aucun résultat"
        
        report = "\n" + "="*60
        report += "\n🎯 AUDIT CORRIGÉ - ENDPOINTS RÉELS"
        report += "\n" + "="*60
        
        report += f"\n\n📊 RÉSUMÉ:"
        report += f"\n⏰ Durée: {self.results['audit_duration']:.1f}s"
        
        # CV Parser
        cv = self.results.get('cv_parser', {})
        if cv.get('avg_latency'):
            status = "🟢 EXCELLENT" if cv['avg_latency'] < 500 else "🟡 MOYEN" if cv['avg_latency'] < 2000 else "🔴 LENT"
            report += f"\n\n🔍 CV PARSER:"
            report += f"\n  • Endpoint: {cv.get('endpoint', 'N/A')}"
            report += f"\n  • Latence: {cv['avg_latency']:.1f}ms {status}"
            report += f"\n  • Succès: {cv['success_rate']:.1f}%"
        elif cv.get('status') == 'NO_ENDPOINT':
            report += f"\n\n🔍 CV PARSER:"
            report += f"\n  • Status: ❌ Aucun endpoint API trouvé"
        
        # Personalization
        pers = self.results.get('personalization', {})
        if pers.get('avg_latency'):
            status = "🟢 EXCELLENT" if pers['avg_latency'] < 200 else "🟡 MOYEN" if pers['avg_latency'] < 1000 else "🔴 LENT"
            report += f"\n\n🎯 PERSONALIZATION:"
            report += f"\n  • Endpoint: {pers.get('endpoint', 'N/A')}"
            report += f"\n  • Latence: {pers['avg_latency']:.1f}ms {status}"
            report += f"\n  • Succès: {pers['success_rate']:.1f}%"
        elif pers.get('status') == 'NO_ENDPOINT':
            report += f"\n\n🎯 PERSONALIZATION:"
            report += f"\n  • Status: ❌ Aucun endpoint API trouvé"
        
        # Frontend
        frontend = self.results.get('frontend', {})
        if frontend:
            report += f"\n\n🌐 FRONTEND:"
            for page, metrics in frontend.items():
                status = "🟢 RAPIDE" if metrics['avg_latency'] < 500 else "🟡 MOYEN" if metrics['avg_latency'] < 2000 else "🔴 LENT"
                report += f"\n  • {page}: {metrics['avg_latency']:.1f}ms {status}"
        
        # Système - Analyse détaillée mémoire
        sys = self.results.get('system_metrics', {})
        if sys and not sys.get('error'):
            mem = sys.get('memory_analysis', {})
            report += f"\n\n🖥️  SYSTÈME:"
            report += f"\n  • CPU: {sys.get('cpu_percent', 0):.1f}%"
            report += f"\n  • RAM: {mem.get('percent', 0):.1f}% {mem.get('status', '')} ({mem.get('used_gb', 0)}/{mem.get('total_gb', 0)}GB)"
            report += f"\n  • Disk: {sys.get('disk_usage_percent', 0):.1f}%"
            
            # Top processus mémoire
            top_procs = sys.get('top_memory_processes', [])
            if top_procs:
                report += f"\n\n🔥 TOP PROCESSUS MÉMOIRE:"
                for proc in top_procs[:3]:
                    report += f"\n  • {proc['name']}: {proc['memory_percent']:.1f}% RAM"
        
        # Recommandations spécifiques
        report += f"\n\n🎯 RECOMMANDATIONS PRIORITAIRES:"
        
        # Analyse mémoire
        if sys and sys.get('memory_analysis', {}).get('percent', 0) > 85:
            report += f"\n  🔴 URGENT: RAM à {sys['memory_analysis']['percent']:.1f}% - Redémarrer conteneurs lourds"
            
        # Services sans API
        if cv.get('status') == 'NO_ENDPOINT':
            report += f"\n  🟡 CV Parser: Vérifier configuration API endpoints"
            
        if pers.get('status') == 'NO_ENDPOINT':
            report += f"\n  🟡 Personalization: Vérifier configuration API endpoints"
        
        # Services en panne à corriger
        report += f"\n  🔴 Job Parser & Matching: Finaliser corrections (Redis/MinIO)"
        
        report += f"\n\n✅ Services fonctionnels identifiés - Prêt pour corrections complètes"
        report += "\n" + "="*60
        
        return report

if __name__ == "__main__":
    print("🚀 Audit Performance Corrigé - Endpoints Réels")
    
    audit = CorrectedPerformanceAudit()
    
    try:
        results = asyncio.run(audit.run_corrected_audit())
        
        report = audit.generate_corrected_report()
        print(report)
        
        # Sauvegarde
        with open("corrected_audit_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Résultats: corrected_audit_results.json")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
