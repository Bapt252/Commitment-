#!/usr/bin/env python3
"""Script pour vérifier les métriques lors d'un déploiement canary."""

import argparse
import sys
import time
from datetime import datetime, timedelta
import requests
from prometheus_api_client import PrometheusConnect


def check_error_rate(prom: PrometheusConnect, threshold: float) -> bool:
    """Vérifier le taux d'erreur du canary."""
    query = '''
    (
        sum(rate(http_requests_total{deployment="canary",status_code!~"2.."}[5m])) /
        sum(rate(http_requests_total{deployment="canary"}[5m]))
    ) * 100
    '''
    
    result = prom.custom_query(query)
    
    if not result:
        print("Warning: No error rate data found for canary")
        return True
    
    error_rate = float(result[0]['value'][1])
    print(f"Canary error rate: {error_rate:.2f}%")
    
    if error_rate > threshold:
        print(f"ERROR: Canary error rate ({error_rate:.2f}%) exceeds threshold ({threshold}%)")
        return False
    
    return True


def check_latency(prom: PrometheusConnect, threshold: float) -> bool:
    """Vérifier la latence du canary."""
    query = '''
    histogram_quantile(0.95, 
        sum(rate(http_request_duration_seconds_bucket{deployment="canary"}[5m])) by (le)
    ) * 1000
    '''
    
    result = prom.custom_query(query)
    
    if not result:
        print("Warning: No latency data found for canary")
        return True
    
    latency = float(result[0]['value'][1])
    print(f"Canary 95th percentile latency: {latency:.2f}ms")
    
    if latency > threshold:
        print(f"ERROR: Canary latency ({latency:.2f}ms) exceeds threshold ({threshold}ms)")
        return False
    
    return True


def check_cpu_usage(prom: PrometheusConnect, threshold: float = 80) -> bool:
    """Vérifier l'usage CPU du canary."""
    query = '''
    avg(rate(container_cpu_usage_seconds_total{pod=~".*-canary-.*"}[5m])) * 100
    '''
    
    result = prom.custom_query(query)
    
    if not result:
        print("Warning: No CPU usage data found for canary")
        return True
    
    cpu_usage = float(result[0]['value'][1])
    print(f"Canary CPU usage: {cpu_usage:.2f}%")
    
    if cpu_usage > threshold:
        print(f"WARNING: Canary CPU usage ({cpu_usage:.2f}%) exceeds threshold ({threshold}%)")
        # Ne pas échouer pour l'usage CPU, juste avertir
    
    return True


def check_memory_usage(prom: PrometheusConnect, threshold: float = 85) -> bool:
    """Vérifier l'usage mémoire du canary."""
    query = '''
    avg(container_memory_usage_bytes{pod=~".*-canary-.*"} / 
        container_spec_memory_limit_bytes{pod=~".*-canary-.*"}) * 100
    '''
    
    result = prom.custom_query(query)
    
    if not result:
        print("Warning: No memory usage data found for canary")
        return True
    
    memory_usage = float(result[0]['value'][1])
    print(f"Canary memory usage: {memory_usage:.2f}%")
    
    if memory_usage > threshold:
        print(f"WARNING: Canary memory usage ({memory_usage:.2f}%) exceeds threshold ({threshold}%)")
        # Ne pas échouer pour l'usage mémoire, juste avertir
    
    return True


def compare_with_stable(prom: PrometheusConnect) -> bool:
    """Comparer les métriques du canary avec la version stable."""
    # Comparer les taux d'erreur
    canary_error_query = '''
    sum(rate(http_requests_total{deployment="canary",status_code!~"2.."}[5m])) /
    sum(rate(http_requests_total{deployment="canary"}[5m]))
    '''
    
    stable_error_query = '''
    sum(rate(http_requests_total{deployment="stable",status_code!~"2.."}[5m])) /
    sum(rate(http_requests_total{deployment="stable"}[5m]))
    '''
    
    canary_error = prom.custom_query(canary_error_query)
    stable_error = prom.custom_query(stable_error_query)
    
    if canary_error and stable_error:
        canary_rate = float(canary_error[0]['value'][1])
        stable_rate = float(stable_error[0]['value'][1])
        
        if canary_rate > stable_rate * 2:  # Canary a 2x plus d'erreurs
            print(f"ERROR: Canary error rate ({canary_rate:.4f}) is significantly higher than stable ({stable_rate:.4f})")
            return False
    
    # Comparer les latences
    canary_latency_query = '''
    histogram_quantile(0.95, 
        sum(rate(http_request_duration_seconds_bucket{deployment="canary"}[5m])) by (le)
    )
    '''
    
    stable_latency_query = '''
    histogram_quantile(0.95, 
        sum(rate(http_request_duration_seconds_bucket{deployment="stable"}[5m])) by (le)
    )
    '''
    
    canary_latency = prom.custom_query(canary_latency_query)
    stable_latency = prom.custom_query(stable_latency_query)
    
    if canary_latency and stable_latency:
        canary_lat = float(canary_latency[0]['value'][1])
        stable_lat = float(stable_latency[0]['value'][1])
        
        if canary_lat > stable_lat * 1.5:  # Canary est 50% plus lent
            print(f"ERROR: Canary latency ({canary_lat:.3f}s) is significantly higher than stable ({stable_lat:.3f}s)")
            return False
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Check canary deployment metrics')
    parser.add_argument('--prometheus-url', required=True, help='Prometheus server URL')
    parser.add_argument('--threshold-error-rate', type=float, default=1.0, help='Error rate threshold (%)')
    parser.add_argument('--threshold-latency', type=float, default=1000, help='Latency threshold (ms)')
    parser.add_argument('--wait-time', type=int, default=300, help='Time to wait before checking (seconds)')
    
    args = parser.parse_args()
    
    print(f"Waiting {args.wait_time} seconds for metrics to stabilize...")
    time.sleep(args.wait_time)
    
    try:
        prom = PrometheusConnect(url=args.prometheus_url)
        
        print("\n=== Checking Canary Deployment Metrics ===")
        
        checks = [
            check_error_rate(prom, args.threshold_error_rate),
            check_latency(prom, args.threshold_latency),
            check_cpu_usage(prom),
            check_memory_usage(prom),
            compare_with_stable(prom)
        ]
        
        if all(checks):
            print("\n✓ All canary metrics are healthy. Proceeding with full deployment.")
            sys.exit(0)
        else:
            print("\n✗ Canary metrics indicate issues. Deployment should be rolled back.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error checking canary metrics: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()