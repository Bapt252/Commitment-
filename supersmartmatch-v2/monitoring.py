#!/usr/bin/env python3
"""
SuperSmartMatch V2 - Performance Monitoring and Metrics
Real-time monitoring, performance analysis, and service health tracking

🔍 Features:
- Real-time performance metrics collection
- Algorithm performance comparison
- Circuit breaker status monitoring
- Service health analysis
- Custom alerts and notifications
- Performance optimization recommendations
"""

import asyncio
import time
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =================== METRICS DATA STRUCTURES ===================

@dataclass
class ServiceMetrics:
    """Service-level metrics"""
    service_name: str
    timestamp: datetime
    response_time_ms: float
    status_code: int
    algorithm_used: str
    success: bool
    error_message: Optional[str] = None

@dataclass
class AlgorithmPerformance:
    """Algorithm performance metrics"""
    algorithm_name: str
    total_requests: int
    success_count: int
    failure_count: int
    avg_response_time_ms: float
    min_response_time_ms: float
    max_response_time_ms: float
    p95_response_time_ms: float
    avg_confidence: float
    avg_match_score: float
    success_rate: float

@dataclass
class SystemHealth:
    """Overall system health metrics"""
    timestamp: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time_ms: float
    services_status: Dict[str, str]
    circuit_breakers: Dict[str, str]
    error_rate: float
    uptime_seconds: float

@dataclass
class PerformanceAlert:
    """Performance alert definition"""
    alert_type: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    message: str
    timestamp: datetime
    metric_value: float
    threshold: float
    service: str

# =================== METRICS COLLECTOR ===================

class MetricsCollector:
    """Collects and analyzes performance metrics"""
    
    def __init__(self, v2_port: int = 5070, collection_interval: int = 60):
        self.v2_port = v2_port
        self.collection_interval = collection_interval
        self.start_time = datetime.now()
        
        # Metrics storage
        self.service_metrics: deque = deque(maxlen=10000)
        self.algorithm_stats: Dict[str, List[float]] = defaultdict(list)
        self.response_times: deque = deque(maxlen=1000)
        self.error_counts: Dict[str, int] = defaultdict(int)
        
        # Alert thresholds
        self.thresholds = {
            'response_time_ms': 150,
            'error_rate': 0.05,
            'circuit_breaker_open': True
        }
        
        # HTTP client for API calls
        self.client = httpx.AsyncClient(timeout=10.0)
        
        logger.info(f"MetricsCollector initialized for port {v2_port}")
    
    async def collect_health_metrics(self) -> Optional[Dict[str, Any]]:
        """Collect health metrics from SuperSmartMatch V2"""
        try:
            response = await self.client.get(f"http://localhost:{self.v2_port}/health")
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Health check failed with status {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Failed to collect health metrics: {e}")
            return None
    
    async def collect_stats_metrics(self) -> Optional[Dict[str, Any]]:
        """Collect detailed stats from SuperSmartMatch V2"""
        try:
            response = await self.client.get(f"http://localhost:{self.v2_port}/stats")
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Stats collection failed with status {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Failed to collect stats metrics: {e}")
            return None
    
    async def test_algorithm_performance(self, algorithm: str) -> Optional[ServiceMetrics]:
        """Test specific algorithm performance"""
        
        test_request = {
            "candidate": {
                "name": "Performance Test",
                "email": "perf@example.com",
                "technical_skills": [
                    {"name": "Python", "level": "Expert", "years": 5}
                ]
            },
            "offers": [
                {
                    "id": "perf_test_job",
                    "title": "Test Job",
                    "company": "Test Company",
                    "required_skills": ["Python"]
                }
            ],
            "algorithm": algorithm
        }
        
        try:
            start_time = time.time()
            response = await self.client.post(
                f"http://localhost:{self.v2_port}/api/v2/match",
                json=test_request
            )
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                return ServiceMetrics(
                    service_name="supersmartmatch-v2",
                    timestamp=datetime.now(),
                    response_time_ms=response_time_ms,
                    status_code=response.status_code,
                    algorithm_used=data.get("algorithm_used", algorithm),
                    success=data.get("success", False)
                )
            else:
                return ServiceMetrics(
                    service_name="supersmartmatch-v2",
                    timestamp=datetime.now(),
                    response_time_ms=response_time_ms,
                    status_code=response.status_code,
                    algorithm_used=algorithm,
                    success=False,
                    error_message=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"Algorithm performance test failed for {algorithm}: {e}")
            return ServiceMetrics(
                service_name="supersmartmatch-v2",
                timestamp=datetime.now(),
                response_time_ms=0,
                status_code=0,
                algorithm_used=algorithm,
                success=False,
                error_message=str(e)
            )
    
    def analyze_algorithm_performance(self) -> Dict[str, AlgorithmPerformance]:
        """Analyze performance by algorithm"""
        
        algorithm_data = defaultdict(lambda: {
            'response_times': [],
            'success_count': 0,
            'failure_count': 0,
            'confidence_scores': [],
            'match_scores': []
        })
        
        # Group metrics by algorithm
        for metric in self.service_metrics:
            algo = metric.algorithm_used
            data = algorithm_data[algo]
            
            if metric.success:
                data['success_count'] += 1
                data['response_times'].append(metric.response_time_ms)
            else:
                data['failure_count'] += 1
        
        # Calculate performance statistics
        results = {}
        for algo, data in algorithm_data.items():
            response_times = data['response_times']
            total_requests = data['success_count'] + data['failure_count']
            
            if total_requests > 0 and response_times:
                results[algo] = AlgorithmPerformance(
                    algorithm_name=algo,
                    total_requests=total_requests,
                    success_count=data['success_count'],
                    failure_count=data['failure_count'],
                    avg_response_time_ms=statistics.mean(response_times) if response_times else 0,
                    min_response_time_ms=min(response_times) if response_times else 0,
                    max_response_time_ms=max(response_times) if response_times else 0,
                    p95_response_time_ms=self._calculate_percentile(response_times, 95) if response_times else 0,
                    avg_confidence=statistics.mean(data['confidence_scores']) if data['confidence_scores'] else 0,
                    avg_match_score=statistics.mean(data['match_scores']) if data['match_scores'] else 0,
                    success_rate=data['success_count'] / total_requests
                )
        
        return results
    
    def _calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of a list"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def generate_system_health(self) -> SystemHealth:
        """Generate overall system health report"""
        
        now = datetime.now()
        uptime = (now - self.start_time).total_seconds()
        
        # Calculate overall metrics
        total_requests = len(self.service_metrics)
        successful_requests = sum(1 for m in self.service_metrics if m.success)
        failed_requests = total_requests - successful_requests
        
        # Calculate average response time
        response_times = [m.response_time_ms for m in self.service_metrics if m.success]
        avg_response_time = statistics.mean(response_times) if response_times else 0
        
        # Calculate error rate
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        return SystemHealth(
            timestamp=now,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time_ms=avg_response_time,
            services_status=self._get_services_status(),
            circuit_breakers=self._get_circuit_breaker_status(),
            error_rate=error_rate,
            uptime_seconds=uptime
        )
    
    def _get_services_status(self) -> Dict[str, str]:
        """Get status of external services"""
        # This would be populated from actual service health checks
        return {
            "supersmartmatch-v2": "healthy",
            "nexten-matcher": "unknown",
            "v1-algorithms": "unknown",
            "redis": "unknown"
        }
    
    def _get_circuit_breaker_status(self) -> Dict[str, str]:
        """Get circuit breaker status"""
        # This would be populated from actual circuit breaker monitoring
        return {
            "nexten": "closed",
            "v1": "closed"
        }
    
    def check_alerts(self, system_health: SystemHealth) -> List[PerformanceAlert]:
        """Check for performance alerts"""
        
        alerts = []
        now = datetime.now()
        
        # Response time alert
        if system_health.avg_response_time_ms > self.thresholds['response_time_ms']:
            alerts.append(PerformanceAlert(
                alert_type="HIGH_RESPONSE_TIME",
                severity="HIGH",
                message=f"Average response time ({system_health.avg_response_time_ms:.1f}ms) exceeds threshold ({self.thresholds['response_time_ms']}ms)",
                timestamp=now,
                metric_value=system_health.avg_response_time_ms,
                threshold=self.thresholds['response_time_ms'],
                service="supersmartmatch-v2"
            ))
        
        # Error rate alert
        if system_health.error_rate > self.thresholds['error_rate']:
            alerts.append(PerformanceAlert(
                alert_type="HIGH_ERROR_RATE",
                severity="CRITICAL",
                message=f"Error rate ({system_health.error_rate:.1%}) exceeds threshold ({self.thresholds['error_rate']:.1%})",
                timestamp=now,
                metric_value=system_health.error_rate,
                threshold=self.thresholds['error_rate'],
                service="supersmartmatch-v2"
            ))
        
        # Circuit breaker alerts
        for service, status in system_health.circuit_breakers.items():
            if status == "open":
                alerts.append(PerformanceAlert(
                    alert_type="CIRCUIT_BREAKER_OPEN",
                    severity="CRITICAL",
                    message=f"Circuit breaker for {service} is open",
                    timestamp=now,
                    metric_value=1.0,
                    threshold=0.0,
                    service=service
                ))
        
        return alerts
    
    def generate_recommendations(self, algorithm_performance: Dict[str, AlgorithmPerformance]) -> List[str]:
        """Generate performance optimization recommendations"""
        
        recommendations = []
        
        # Analyze algorithm performance
        if algorithm_performance:
            best_algo = min(algorithm_performance.values(), key=lambda x: x.avg_response_time_ms)
            worst_algo = max(algorithm_performance.values(), key=lambda x: x.avg_response_time_ms)
            
            if worst_algo.avg_response_time_ms > best_algo.avg_response_time_ms * 2:
                recommendations.append(
                    f"Consider optimizing {worst_algo.algorithm_name} algorithm - "
                    f"it's {worst_algo.avg_response_time_ms / best_algo.avg_response_time_ms:.1f}x slower than {best_algo.algorithm_name}"
                )
            
            # Check success rates
            for algo, perf in algorithm_performance.items():
                if perf.success_rate < 0.95:
                    recommendations.append(
                        f"Algorithm {algo} has low success rate ({perf.success_rate:.1%}) - check for errors"
                    )
        
        # Check response time distribution
        response_times = [m.response_time_ms for m in self.service_metrics if m.success]
        if response_times:
            p95 = self._calculate_percentile(response_times, 95)
            avg = statistics.mean(response_times)
            
            if p95 > avg * 3:
                recommendations.append(
                    "High response time variance detected - consider implementing caching or load balancing"
                )
        
        return recommendations

# =================== MONITORING DASHBOARD ===================

class MonitoringDashboard:
    """Real-time monitoring dashboard"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    def print_dashboard(self, system_health: SystemHealth, algorithm_performance: Dict[str, AlgorithmPerformance], alerts: List[PerformanceAlert]):
        """Print monitoring dashboard to console"""
        
        print("\n" + "="*80)
        print("🚀 SuperSmartMatch V2 - Real-time Monitoring Dashboard")
        print("="*80)
        
        # System Health
        print(f"\n📊 System Health - {system_health.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Uptime: {timedelta(seconds=int(system_health.uptime_seconds))}")
        print(f"   Total Requests: {system_health.total_requests}")
        print(f"   Success Rate: {(system_health.successful_requests / max(system_health.total_requests, 1)):.1%}")
        print(f"   Error Rate: {system_health.error_rate:.1%}")
        print(f"   Avg Response Time: {system_health.avg_response_time_ms:.1f}ms")
        
        # Services Status
        print(f"\n🔧 Services Status:")
        for service, status in system_health.services_status.items():
            status_icon = "✅" if status == "healthy" else "❓" if status == "unknown" else "❌"
            print(f"   {status_icon} {service}: {status}")
        
        # Circuit Breakers
        print(f"\n⚡ Circuit Breakers:")
        for service, status in system_health.circuit_breakers.items():
            status_icon = "✅" if status == "closed" else "⚠️" if status == "half_open" else "❌"
            print(f"   {status_icon} {service}: {status}")
        
        # Algorithm Performance
        if algorithm_performance:
            print(f"\n🧠 Algorithm Performance:")
            for algo, perf in sorted(algorithm_performance.items(), key=lambda x: x[1].avg_response_time_ms):
                print(f"   📈 {algo}:")
                print(f"      Requests: {perf.total_requests} | Success: {perf.success_rate:.1%}")
                print(f"      Response Time: {perf.avg_response_time_ms:.1f}ms (avg) | {perf.p95_response_time_ms:.1f}ms (p95)")
                print(f"      Range: {perf.min_response_time_ms:.1f}ms - {perf.max_response_time_ms:.1f}ms")
        
        # Alerts
        if alerts:
            print(f"\n🚨 Active Alerts:")
            for alert in alerts:
                severity_icon = "🔴" if alert.severity == "CRITICAL" else "🟡" if alert.severity == "HIGH" else "🟢"
                print(f"   {severity_icon} [{alert.severity}] {alert.alert_type}: {alert.message}")
        else:
            print(f"\n✅ No Active Alerts")
        
        # Recommendations
        recommendations = self.collector.generate_recommendations(algorithm_performance)
        if recommendations:
            print(f"\n💡 Optimization Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("\n" + "="*80)

# =================== MAIN MONITORING LOOP ===================

async def main_monitoring_loop():
    """Main monitoring loop"""
    
    collector = MetricsCollector()
    dashboard = MonitoringDashboard(collector)
    
    logger.info("Starting SuperSmartMatch V2 monitoring...")
    
    try:
        while True:
            # Collect metrics
            health_data = await collector.collect_health_metrics()
            stats_data = await collector.collect_stats_metrics()
            
            # Test algorithm performance
            algorithms = ["auto", "nexten", "smart", "enhanced", "semantic"]
            for algo in algorithms:
                metric = await collector.test_algorithm_performance(algo)
                if metric:
                    collector.service_metrics.append(metric)
            
            # Analyze performance
            algorithm_performance = collector.analyze_algorithm_performance()
            system_health = collector.generate_system_health()
            alerts = collector.check_alerts(system_health)
            
            # Display dashboard
            dashboard.print_dashboard(system_health, algorithm_performance, alerts)
            
            # Wait for next collection interval
            await asyncio.sleep(collector.collection_interval)
            
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Monitoring error: {e}")
    finally:
        await collector.client.aclose()

# =================== CLI INTERFACE ===================

def export_metrics_json(collector: MetricsCollector, filename: str):
    """Export metrics to JSON file"""
    
    algorithm_performance = collector.analyze_algorithm_performance()
    system_health = collector.generate_system_health()
    
    export_data = {
        "export_timestamp": datetime.now().isoformat(),
        "system_health": asdict(system_health),
        "algorithm_performance": {k: asdict(v) for k, v in algorithm_performance.items()},
        "recent_metrics": [asdict(m) for m in list(collector.service_metrics)[-100:]]
    }
    
    with open(filename, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    logger.info(f"Metrics exported to {filename}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "export":
        # Export mode
        collector = MetricsCollector()
        filename = sys.argv[2] if len(sys.argv) > 2 else "supersmartmatch_v2_metrics.json"
        
        # Collect some sample metrics
        async def collect_and_export():
            for i in range(10):
                metric = await collector.test_algorithm_performance("auto")
                if metric:
                    collector.service_metrics.append(metric)
            
            export_metrics_json(collector, filename)
        
        asyncio.run(collect_and_export())
    else:
        # Real-time monitoring mode
        asyncio.run(main_monitoring_loop())
