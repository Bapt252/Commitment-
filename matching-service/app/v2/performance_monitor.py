"""
SuperSmartMatch V2 - Performance Monitor

Advanced performance monitoring system with real-time metrics collection,
A/B testing framework, and intelligent alerting for production monitoring.
"""

import logging
import asyncio
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics

logger = logging.getLogger(__name__)

@dataclass
class RequestMetrics:
    """Individual request metrics"""
    timestamp: float
    algorithm: str
    execution_time_ms: float
    result_count: int
    success: bool
    context: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class AlgorithmStats:
    """Algorithm performance statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    total_execution_time_ms: float = 0.0
    avg_execution_time_ms: float = 0.0
    p95_execution_time_ms: float = 0.0
    p99_execution_time_ms: float = 0.0
    min_execution_time_ms: float = float('inf')
    max_execution_time_ms: float = 0.0
    error_rate: float = 0.0
    avg_result_count: float = 0.0
    
    # Recent performance window (last 100 requests)
    recent_execution_times: List[float] = None
    
    def __post_init__(self):
        if self.recent_execution_times is None:
            self.recent_execution_times = []

@dataclass
class SystemHealthMetrics:
    """Overall system health metrics"""
    uptime_seconds: float
    total_requests: int
    requests_per_minute: float
    avg_response_time_ms: float
    error_rate: float
    active_algorithms: List[str]
    cache_hit_rate: float
    memory_usage_mb: float
    cpu_usage_percent: float

class ABTestingFramework:
    """A/B Testing framework for algorithm comparison"""
    
    def __init__(self):
        self.test_groups = {}
        self.metrics = defaultdict(list)
        self.active_tests = {}
    
    def create_test(self, test_name: str, algorithm_a: str, algorithm_b: str, 
                   traffic_split: float = 0.5) -> None:
        """Create a new A/B test"""
        self.active_tests[test_name] = {
            'algorithm_a': algorithm_a,
            'algorithm_b': algorithm_b,
            'traffic_split': traffic_split,
            'start_time': time.time(),
            'total_requests': 0
        }
        logger.info(f"Created A/B test '{test_name}': {algorithm_a} vs {algorithm_b}")
    
    def get_algorithm_for_request(self, test_name: str, user_id: str) -> str:
        """Get algorithm assignment for user in A/B test"""
        if test_name not in self.active_tests:
            return None
        
        test = self.active_tests[test_name]
        
        # Consistent assignment based on user_id hash
        import hashlib
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        assignment = (user_hash % 100) / 100.0
        
        algorithm = (test['algorithm_a'] if assignment < test['traffic_split'] 
                    else test['algorithm_b'])
        
        test['total_requests'] += 1
        return algorithm
    
    def record_test_result(self, test_name: str, algorithm: str, 
                          metrics: RequestMetrics) -> None:
        """Record metrics for A/B test"""
        if test_name in self.active_tests:
            self.metrics[f"{test_name}_{algorithm}"].append(metrics)
    
    def get_test_results(self, test_name: str) -> Dict[str, Any]:
        """Get A/B test results with statistical analysis"""
        if test_name not in self.active_tests:
            return {}
        
        test = self.active_tests[test_name]
        
        # Collect metrics for both algorithms
        a_metrics = self.metrics.get(f"{test_name}_{test['algorithm_a']}", [])
        b_metrics = self.metrics.get(f"{test_name}_{test['algorithm_b']}", [])
        
        if not a_metrics or not b_metrics:
            return {"status": "insufficient_data"}
        
        # Calculate statistics
        a_times = [m.execution_time_ms for m in a_metrics if m.success]
        b_times = [m.execution_time_ms for m in b_metrics if m.success]
        
        a_success_rate = sum(1 for m in a_metrics if m.success) / len(a_metrics)
        b_success_rate = sum(1 for m in b_metrics if m.success) / len(b_metrics)
        
        results = {
            'test_name': test_name,
            'algorithm_a': test['algorithm_a'],
            'algorithm_b': test['algorithm_b'],
            'duration_hours': (time.time() - test['start_time']) / 3600,
            'total_requests': test['total_requests'],
            'algorithm_a_stats': {
                'requests': len(a_metrics),
                'success_rate': a_success_rate,
                'avg_time_ms': statistics.mean(a_times) if a_times else 0,
                'p95_time_ms': self._percentile(a_times, 95) if a_times else 0
            },
            'algorithm_b_stats': {
                'requests': len(b_metrics),
                'success_rate': b_success_rate,
                'avg_time_ms': statistics.mean(b_times) if b_times else 0,
                'p95_time_ms': self._percentile(b_times, 95) if b_times else 0
            }
        }
        
        # Statistical significance test (basic)
        if len(a_times) > 30 and len(b_times) > 30:
            try:
                from scipy import stats
                t_stat, p_value = stats.ttest_ind(a_times, b_times)
                results['statistical_significance'] = {
                    't_statistic': t_stat,
                    'p_value': p_value,
                    'significant': p_value < 0.05
                }
            except ImportError:
                logger.warning("scipy not available for statistical tests")
        
        return results
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

class AlertingSystem:
    """Intelligent alerting system for performance degradation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_thresholds = config.get('alert_thresholds', {
            'error_rate_critical': 0.05,      # 5% error rate
            'response_time_critical': 200,    # 200ms P95
            'response_time_warning': 150,     # 150ms P95
            'success_rate_critical': 0.90     # 90% success rate
        })
        self.alert_history = deque(maxlen=1000)
        self.cooldown_periods = defaultdict(float)
        self.cooldown_duration = 300  # 5 minutes
    
    def check_alerts(self, algorithm_stats: Dict[str, AlgorithmStats]) -> List[Dict[str, Any]]:
        """Check for alert conditions and return alerts"""
        alerts = []
        current_time = time.time()
        
        for algorithm, stats in algorithm_stats.items():
            # Skip if in cooldown
            if current_time - self.cooldown_periods[algorithm] < self.cooldown_duration:
                continue
            
            # Check error rate
            if stats.error_rate > self.alert_thresholds['error_rate_critical']:
                alerts.append({
                    'level': 'CRITICAL',
                    'algorithm': algorithm,
                    'metric': 'error_rate',
                    'value': stats.error_rate,
                    'threshold': self.alert_thresholds['error_rate_critical'],
                    'message': f"High error rate: {stats.error_rate:.2%}"
                })
                self.cooldown_periods[algorithm] = current_time
            
            # Check response time
            if stats.p95_execution_time_ms > self.alert_thresholds['response_time_critical']:
                alerts.append({
                    'level': 'CRITICAL',
                    'algorithm': algorithm,
                    'metric': 'response_time',
                    'value': stats.p95_execution_time_ms,
                    'threshold': self.alert_thresholds['response_time_critical'],
                    'message': f"High response time P95: {stats.p95_execution_time_ms:.1f}ms"
                })
                self.cooldown_periods[algorithm] = current_time
            
            elif stats.p95_execution_time_ms > self.alert_thresholds['response_time_warning']:
                alerts.append({
                    'level': 'WARNING',
                    'algorithm': algorithm,
                    'metric': 'response_time',
                    'value': stats.p95_execution_time_ms,
                    'threshold': self.alert_thresholds['response_time_warning'],
                    'message': f"Elevated response time P95: {stats.p95_execution_time_ms:.1f}ms"
                })
        
        # Record alerts
        for alert in alerts:
            alert['timestamp'] = current_time
            self.alert_history.append(alert)
            logger.warning(f"ALERT [{alert['level']}]: {alert['message']}")
        
        return alerts
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get alerts from recent hours"""
        cutoff_time = time.time() - (hours * 3600)
        return [alert for alert in self.alert_history 
                if alert['timestamp'] > cutoff_time]

class PerformanceMonitor:
    """
    Comprehensive performance monitoring system for SuperSmartMatch V2
    
    Features:
    - Real-time metrics collection and analysis
    - A/B testing framework
    - Intelligent alerting
    - Performance trend analysis
    - Algorithm optimization recommendations
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.start_time = time.time()
        
        # Metrics storage
        self.algorithm_stats = defaultdict(AlgorithmStats)
        self.request_history = deque(maxlen=self.config.get('max_history_size', 10000))
        self.minute_buckets = defaultdict(list)  # For requests per minute calculation
        
        # Components
        self.ab_testing = ABTestingFramework()
        self.alerting = AlertingSystem(self.config)
        
        # Configuration
        self.enable_detailed_logging = self.config.get('enable_detailed_logging', True)
        self.metrics_retention_hours = self.config.get('metrics_retention_hours', 24)
        
        logger.info("PerformanceMonitor initialized")
    
    async def record_request(self, 
                           algorithm: str,
                           execution_time: float,
                           result_count: int,
                           success: bool,
                           context: Optional[Dict[str, Any]] = None,
                           user_id: Optional[str] = None) -> None:
        """
        Record a request's performance metrics.
        
        Args:
            algorithm: Algorithm used
            execution_time: Execution time in milliseconds
            result_count: Number of results returned
            success: Whether the request succeeded
            context: Additional context information
            user_id: User identifier for A/B testing
        """
        
        timestamp = time.time()
        context = context or {}
        
        # Create metrics record
        metrics = RequestMetrics(
            timestamp=timestamp,
            algorithm=algorithm,
            execution_time_ms=execution_time,
            result_count=result_count,
            success=success,
            context=context,
            user_id=user_id
        )
        
        # Store in history
        self.request_history.append(metrics)
        
        # Update algorithm statistics
        await self._update_algorithm_stats(algorithm, metrics)
        
        # Record for A/B testing if applicable
        for test_name in self.ab_testing.active_tests:
            if self.ab_testing.active_tests[test_name].get('algorithm_a') == algorithm or \
               self.ab_testing.active_tests[test_name].get('algorithm_b') == algorithm:
                self.ab_testing.record_test_result(test_name, algorithm, metrics)
        
        # Update minute buckets for RPM calculation
        minute_bucket = int(timestamp // 60)
        self.minute_buckets[minute_bucket].append(metrics)
        
        # Clean old minute buckets
        cutoff_minute = minute_bucket - self.metrics_retention_hours * 60
        keys_to_remove = [k for k in self.minute_buckets.keys() if k < cutoff_minute]
        for key in keys_to_remove:
            del self.minute_buckets[key]
        
        # Log detailed metrics if enabled
        if self.enable_detailed_logging:
            logger.debug(f"Request recorded: {algorithm} - {execution_time:.1f}ms - "
                        f"{'SUCCESS' if success else 'FAILED'} - {result_count} results")
    
    async def _update_algorithm_stats(self, algorithm: str, metrics: RequestMetrics) -> None:
        """Update algorithm statistics with new metrics"""
        stats = self.algorithm_stats[algorithm]
        
        # Update counters
        stats.total_requests += 1
        if metrics.success:
            stats.successful_requests += 1
        
        # Update execution time statistics
        if metrics.success:  # Only count successful requests for timing
            stats.total_execution_time_ms += metrics.execution_time_ms
            stats.avg_execution_time_ms = (
                stats.total_execution_time_ms / stats.successful_requests
            )
            
            # Update min/max
            stats.min_execution_time_ms = min(
                stats.min_execution_time_ms, metrics.execution_time_ms
            )
            stats.max_execution_time_ms = max(
                stats.max_execution_time_ms, metrics.execution_time_ms
            )
            
            # Update recent execution times for percentile calculation
            stats.recent_execution_times.append(metrics.execution_time_ms)
            if len(stats.recent_execution_times) > 100:
                stats.recent_execution_times = stats.recent_execution_times[-100:]
            
            # Calculate percentiles
            if len(stats.recent_execution_times) >= 20:  # Need minimum sample size
                sorted_times = sorted(stats.recent_execution_times)
                stats.p95_execution_time_ms = sorted_times[int(len(sorted_times) * 0.95)]
                stats.p99_execution_time_ms = sorted_times[int(len(sorted_times) * 0.99)]
        
        # Update error rate
        stats.error_rate = 1.0 - (stats.successful_requests / stats.total_requests)
        
        # Update average result count
        stats.avg_result_count = (
            (stats.avg_result_count * (stats.total_requests - 1) + metrics.result_count) /
            stats.total_requests
        )
    
    async def get_summary_stats(self) -> Dict[str, Any]:
        """Get comprehensive summary statistics"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # Calculate overall metrics
        total_requests = sum(stats.total_requests for stats in self.algorithm_stats.values())
        total_successful = sum(stats.successful_requests for stats in self.algorithm_stats.values())
        
        # Calculate requests per minute (last hour)
        recent_hour_start = int((current_time - 3600) // 60)
        recent_requests = []
        for minute_bucket in range(recent_hour_start, int(current_time // 60) + 1):
            recent_requests.extend(self.minute_buckets.get(minute_bucket, []))
        
        rpm = len(recent_requests) / min(60, uptime / 60) if uptime > 0 else 0
        
        # Calculate overall average response time
        if total_successful > 0:
            total_execution_time = sum(
                stats.total_execution_time_ms for stats in self.algorithm_stats.values()
            )
            avg_response_time = total_execution_time / total_successful
        else:
            avg_response_time = 0
        
        # Get algorithm details
        algorithm_details = {}
        for algorithm, stats in self.algorithm_stats.items():
            algorithm_details[algorithm] = asdict(stats)
        
        # Check for alerts
        current_alerts = self.alerting.check_alerts(self.algorithm_stats)
        
        summary = {
            'system_health': {
                'status': 'healthy' if not current_alerts else 'warning',
                'uptime_seconds': uptime,
                'total_requests': total_requests,
                'successful_requests': total_successful,
                'success_rate': total_successful / total_requests if total_requests > 0 else 1.0,
                'error_rate': 1.0 - (total_successful / total_requests) if total_requests > 0 else 0.0,
                'requests_per_minute': rpm,
                'avg_response_time_ms': avg_response_time
            },
            'algorithms': algorithm_details,
            'alerts': {
                'current': current_alerts,
                'recent_24h': self.alerting.get_recent_alerts(24)
            },
            'ab_tests': {
                test_name: self.ab_testing.get_test_results(test_name)
                for test_name in self.ab_testing.active_tests
            },
            'recommendations': await self._generate_recommendations()
        }
        
        return summary
    
    async def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on performance data"""
        recommendations = []
        
        for algorithm, stats in self.algorithm_stats.items():
            # High error rate recommendation
            if stats.error_rate > 0.02:  # >2% error rate
                recommendations.append({
                    'type': 'error_rate',
                    'algorithm': algorithm,
                    'message': f"High error rate ({stats.error_rate:.1%}) - investigate {algorithm} algorithm stability",
                    'priority': 'high' if stats.error_rate > 0.05 else 'medium'
                })
            
            # High response time recommendation
            if stats.p95_execution_time_ms > 120:  # >120ms P95
                recommendations.append({
                    'type': 'performance',
                    'algorithm': algorithm,
                    'message': f"High response time P95 ({stats.p95_execution_time_ms:.1f}ms) - consider optimization",
                    'priority': 'high' if stats.p95_execution_time_ms > 150 else 'medium'
                })
            
            # Low usage recommendation (if one algorithm is rarely used)
            total_requests = sum(s.total_requests for s in self.algorithm_stats.values())
            if total_requests > 100 and stats.total_requests / total_requests < 0.05:
                recommendations.append({
                    'type': 'usage',
                    'algorithm': algorithm,
                    'message': f"Low usage ({stats.total_requests}/{total_requests} requests) - verify algorithm selection logic",
                    'priority': 'low'
                })
        
        return recommendations
    
    # A/B Testing methods
    
    def start_ab_test(self, test_name: str, algorithm_a: str, algorithm_b: str,
                     traffic_split: float = 0.5) -> None:
        """Start a new A/B test"""
        self.ab_testing.create_test(test_name, algorithm_a, algorithm_b, traffic_split)
    
    def get_ab_test_assignment(self, test_name: str, user_id: str) -> Optional[str]:
        """Get algorithm assignment for user in A/B test"""
        return self.ab_testing.get_algorithm_for_request(test_name, user_id)
    
    def get_ab_test_results(self, test_name: str) -> Dict[str, Any]:
        """Get A/B test results"""
        return self.ab_testing.get_test_results(test_name)
    
    def stop_ab_test(self, test_name: str) -> Dict[str, Any]:
        """Stop A/B test and return final results"""
        if test_name in self.ab_testing.active_tests:
            results = self.ab_testing.get_test_results(test_name)
            del self.ab_testing.active_tests[test_name]
            logger.info(f"A/B test '{test_name}' stopped")
            return results
        return {}
    
    # Export and reporting methods
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format"""
        if format == 'json':
            return json.dumps(asdict(self.algorithm_stats), indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def reset_stats(self) -> None:
        """Reset all statistics (useful for testing)"""
        self.algorithm_stats.clear()
        self.request_history.clear()
        self.minute_buckets.clear()
        self.start_time = time.time()
        logger.info("Performance statistics reset")
