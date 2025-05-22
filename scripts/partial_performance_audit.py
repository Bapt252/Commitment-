#!/usr/bin/env python3
"""
Audit Performance Partiel - Services Fonctionnels Commitment-
Focus: CV Parser, Personalization, Frontend
"""

import asyncio
import aiohttp
import time
import json
import statistics
import requests
import psutil

class PartialPerformanceAudit:
    def __init__(self):
        # Services fonctionnels actuels
        self.services = {
            "cv_parser": "http://localhost:5051",
            "personalization": "http://localhost:5060", 
            "frontend": "http://localhost:3000"
        }
        self.results = {}
    
    async def test_cv_parser_performance(self):
        """Test performance CV Parser avec données réelles"""
        print("🔍 Test CV Parser - Performance détaillée...")
        
        test_cv = {
            "content": """Jean Dupont
Développeur Full Stack Senior
5 ans d'expérience

COMPÉTENCES:
• Python, Django, FastAPI
• React, JavaScript, TypeScript  
• PostgreSQL, Redis, Docker
• AWS, CI/CD, Git

EXPÉRIENCE:
2020-2025: Lead Developer chez TechCorp
- Développement d'applications web scalables
- Architecture microservices
- Management équipe de 4 développeurs

2018-2020: Développeur Backend chez StartupInc  
- APIs REST avec Django
- Optimisation base de données
- Intégration services tiers

FORMATION:
2018: Master Informatique - École Polytechnique

LOCALISATION: Paris, France
SALAIRE SOUHAITÉ: 65000€"""
        }

        latencies = []
        successful_requests = 0

        for i in range(15):  
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.services['cv_parser']}/parse_cv",
                    json=test_cv,
                    timeout=10
                )
                latency = (time.time() - start_time) * 1000
                latencies.append(latency)
                
                if response.status_code == 200:
                    successful_requests += 1
                    data = response.json()
                    skills_count = len(data.get('skills', [])) if isinstance(data, dict) else 0
                    print(f"✅ CV {i+1}: {latency:.1f}ms - Skills: {skills_count}")
                else:
                    print(f"⚠️  CV {i+1}: Status {response.status_code}")
                
            except Exception as e:
                print(f"❌ CV {i+1}: Erreur - {str(e)[:50]}")

        if latencies:
            return {
                "service": "cv_parser",
                "avg_latency": statistics.mean(latencies),
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "p95_latency": statistics.quantiles(latencies, n=20)[18] if len(latencies) > 5 else max(latencies),
                "successful_requests": successful_requests,
                "total_requests": 15,
                "success_rate": (successful_requests / 15) * 100
            }
        return {"service": "cv_parser", "status": "FAILED"}
    
    async def test_personalization_performance(self):
        """Test performance service personnalisation"""
        print("🎯 Test Personalization - Recommandations...")
        
        user_profiles = [
            {
                "user_id": f"test_user_{i}",
                "preferences": {
                    "location": "Paris",
                    "salary_min": 45000 + (i * 5000),
                    "skills": ["Python", "React", "Docker"][:i%3+1],
                    "experience_level": ["junior", "mid", "senior"][i%3]
                }
            }
            for i in range(10)
        ]

        latencies = []
        successful_requests = 0

        for i, profile in enumerate(user_profiles):
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.services['personalization']}/recommend",
                    json=profile,
                    timeout=15
                )
                latency = (time.time() - start_time) * 1000
                latencies.append(latency)
                
                if response.status_code == 200:
                    successful_requests += 1
                    data = response.json()
                    recs = len(data.get('recommendations', [])) if isinstance(data, dict) else 0
                    print(f"✅ User {i+1}: {latency:.1f}ms - {recs} recs")
                else:
                    print(f"⚠️  User {i+1}: Status {response.status_code}")
                
            except Exception as e:
                print(f"❌ User {i+1}: Erreur - {str(e)[:50]}")

        if latencies:
            return {
                "service": "personalization", 
                "avg_latency": statistics.mean(latencies),
                "min_latency": min(latencies),
                "max_latency": max(latencies),
                "p95_latency": statistics.quantiles(latencies, n=20)[18] if len(latencies) > 5 else max(latencies),
                "successful_requests": successful_requests,
                "total_requests": 10,
                "success_rate": (successful_requests / 10) * 100
            }
        return {"service": "personalization", "status": "FAILED"}

    def test_frontend_responsiveness(self):
        """Test responsive frontend"""
        print("🌐 Test Frontend - Temps de chargement...")
        
        pages = ["/", "/health", "/api/health"]
        results = {}
        
        for page in pages:
            latencies = []
            for i in range(5):
                start_time = time.time()
                try:
                    response = requests.get(
                        f"{self.services['frontend']}{page}",
                        timeout=10
                    )
                    latency = (time.time() - start_time) * 1000
                    latencies.append(latency)
                except Exception as e:
                    print(f"❌ {page}: {str(e)[:30]}")
            
            if latencies:
                results[page] = {
                    "avg_latency": statistics.mean(latencies),
                    "min_latency": min(latencies),
                    "max_latency": max(latencies)
                }
                print(f"✅ {page}: {statistics.mean(latencies):.1f}ms avg")

        return results

    def get_system_metrics(self):
        """Métriques système détaillées"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Top processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    if proc_info['cpu_percent'] and proc_info['cpu_percent'] > 1.0:
                        processes.append(proc_info)
                except:
                    pass
            
            top_processes = sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:5]

            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available // (1024**3),
                "memory_used_gb": memory.used // (1024**3),
                "disk_usage_percent": disk.percent,
                "top_processes": top_processes,
                "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            }
        except Exception as e:
            return {"error": str(e)}

    async def run_partial_audit(self):
        """Exécution audit partiel"""
        print("🚀 AUDIT PERFORMANCE PARTIEL - SERVICES FONCTIONNELS")
        print("="*60)
        
        start_time = time.time()
        
        # Test séquentiel pour éviter surcharge
        print("\n📊 Phase 1: CV Parser Performance")
        cv_results = await self.test_cv_parser_performance()
        
        print("\n📊 Phase 2: Personalization Performance")
        personalization_results = await self.test_personalization_performance()
        
        print("\n📊 Phase 3: Frontend Responsiveness") 
        frontend_results = self.test_frontend_responsiveness()
        
        print("\n📊 Phase 4: Métriques Système")
        system_metrics = self.get_system_metrics()
        
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

    def generate_report(self):
        """Rapport audit partiel"""
        if not self.results:
            return "❌ Aucun résultat"
        
        report = "\n" + "="*60
        report += "\n🎯 AUDIT PARTIEL - SERVICES FONCTIONNELS COMMITMENT-"
        report += "\n" + "="*60
        
        report += f"\n\n📊 RÉSUMÉ:"
        report += f"\n⏰ Durée: {self.results['audit_duration']:.1f}s"
        report += f"\n🎯 Services: CV Parser, Personalization, Frontend"
        
        # CV Parser
        cv = self.results.get('cv_parser', {})
        if cv and cv.get('avg_latency'):
            status = "🟢 EXCELLENT" if cv['avg_latency'] < 500 else "🟡 MOYEN" if cv['avg_latency'] < 2000 else "🔴 LENT"
            report += f"\n\n🔍 CV PARSER:"
            report += f"\n  • Latence: {cv['avg_latency']:.1f}ms {status}"
            report += f"\n  • Succès: {cv['success_rate']:.1f}%"
            report += f"\n  • P95: {cv['p95_latency']:.1f}ms"
        
        # Personalization
        pers = self.results.get('personalization', {})
        if pers and pers.get('avg_latency'):
            status = "🟢 EXCELLENT" if pers['avg_latency'] < 200 else "🟡 MOYEN" if pers['avg_latency'] < 1000 else "🔴 LENT"
            report += f"\n\n🎯 PERSONALIZATION:"
            report += f"\n  • Latence: {pers['avg_latency']:.1f}ms {status}"
            report += f"\n  • Succès: {pers['success_rate']:.1f}%"
            report += f"\n  • P95: {pers['p95_latency']:.1f}ms"
        
        # Frontend
        frontend = self.results.get('frontend', {})
        if frontend:
            report += f"\n\n🌐 FRONTEND:"
            for page, metrics in frontend.items():
                status = "🟢 RAPIDE" if metrics['avg_latency'] < 500 else "🟡 MOYEN" if metrics['avg_latency'] < 2000 else "🔴 LENT"
                report += f"\n  • {page}: {metrics['avg_latency']:.1f}ms {status}"
        
        # Système
        sys = self.results.get('system_metrics', {})
        if sys and not sys.get('error'):
            report += f"\n\n🖥️  SYSTÈME:"
            report += f"\n  • CPU: {sys.get('cpu_percent', 0):.1f}%"
            report += f"\n  • RAM: {sys.get('memory_percent', 0):.1f}%"
            report += f"\n  • Disk: {sys.get('disk_usage_percent', 0):.1f}%"
        
        # Recommandations
        report += f"\n\n🎯 RECOMMANDATIONS:"
        
        if cv and cv.get('avg_latency', 0) > 1000:
            report += f"\n  🔴 CV Parser lent: optimiser parsing"
        
        if pers and pers.get('avg_latency', 0) > 500:
            report += f"\n  🟡 Personalization: optimiser recommandations"
            
        if sys and sys.get('cpu_percent', 0) > 80:
            report += f"\n  🔴 CPU surchargé"
            
        if sys and sys.get('memory_percent', 0) > 85:
            report += f"\n  🔴 RAM saturée"
        
        report += f"\n\n✅ Prêt pour audit complet post-corrections"
        report += "\n" + "="*60
        
        return report

if __name__ == "__main__":
    print("🚀 Lancement Audit Performance Partiel")
    
    audit = PartialPerformanceAudit()
    
    try:
        results = asyncio.run(audit.run_partial_audit())
        
        report = audit.generate_report()
        print(report)
        
        # Sauvegarde
        with open("partial_audit_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Résultats: partial_audit_results.json")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
