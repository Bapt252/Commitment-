#!/usr/bin/env python3
"""Script pour vérifier qu'un déploiement s'est bien passé."""

import argparse
import sys
import time
import requests
from prometheus_api_client import PrometheusConnect


def check_health_endpoints(api_url: str) -> bool:
    """Vérifier que tous les endpoints de santé répondent."""
    endpoints = [
        '/health',
        '/metrics',
        '/api/cv-parser/health',
        '/api/job-parser/health',
        '/api/matching/health'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{api_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✓ {endpoint} is healthy")
            else:
                print(f"✗ {endpoint} returned {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"✗ {endpoint} failed: {e}")
            return False
    
    return True


def check_service_metrics(prom: PrometheusConnect) -> bool:
    """Vérifier que tous les services rapportent des métriques."""
    services = ['cv-parser', 'job-parser', 'matching-api', 'backend']
    
    for service in services:
        query = f'up{{job="{service}"}}}'
        result = prom.custom_query(query)
        
        if not result or float(result[0]['value'][1]) != 1:
            print(f"✗ Service {service} is not reporting metrics")
            return False
        
        print(f"✓ Service {service} is up and reporting metrics")
    
    return True


def check_error_rates(prom: PrometheusConnect, threshold: float = 5.0) -> bool:
    """Vérifier que les taux d'erreur sont acceptables."""
    query = '''
    (
        sum(rate(http_requests_total{status_code!~"2.."}[5m])) /
        sum(rate(http_requests_total[5m]))
    ) * 100
    '''
    
    result = prom.custom_query(query)
    
    if not result:
        print("Warning: No error rate data available")
        return True
    
    error_rate = float(result[0]['value'][1])
    print(f"Current error rate: {error_rate:.2f}%")
    
    if error_rate > threshold:
        print(f"✗ Error rate ({error_rate:.2f}%) exceeds threshold ({threshold}%)")
        return False
    
    print(f"✓ Error rate is within acceptable limits")
    return True


def check_response_times(prom: PrometheusConnect, threshold: float = 2.0) -> bool:
    """Vérifier que les temps de réponse sont acceptables."""
    query = '''
    histogram_quantile(0.95, 
        sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
    )
    '''
    
    result = prom.custom_query(query)
    
    if not result:
        print("Warning: No response time data available")
        return True
    
    response_time = float(result[0]['value'][1])
    print(f"95th percentile response time: {response_time:.3f}s")
    
    if response_time > threshold:
        print(f"✗ Response time ({response_time:.3f}s) exceeds threshold ({threshold}s)")
        return False
    
    print(f"✓ Response times are within acceptable limits")
    return True


def check_resource_usage(prom: PrometheusConnect) -> bool:
    """Vérifier l'usage des ressources."""
    # Vérifier l'usage CPU
    cpu_query = '''
    avg(rate(container_cpu_usage_seconds_total[5m])) * 100
    '''
    
    cpu_result = prom.custom_query(cpu_query)
    if cpu_result:
        cpu_usage = float(cpu_result[0]['value'][1])
        print(f"Average CPU usage: {cpu_usage:.2f}%")
        
        if cpu_usage > 90:
            print(f"⚠️  High CPU usage detected: {cpu_usage:.2f}%")
    
    # Vérifier l'usage mémoire
    memory_query = '''
    avg(container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100
    '''
    
    memory_result = prom.custom_query(memory_query)
    if memory_result:
        memory_usage = float(memory_result[0]['value'][1])
        print(f"Average memory usage: {memory_usage:.2f}%")
        
        if memory_usage > 90:
            print(f"⚠️  High memory usage detected: {memory_usage:.2f}%")
    
    return True


def check_database_connections(prom: PrometheusConnect) -> bool:
    """Vérifier les connexions à la base de données."""
    query = 'pg_stat_database_numbackends{datname="nexten"}'
    
    result = prom.custom_query(query)
    
    if not result:
        print("Warning: No database connection data available")
        return True
    
    connections = float(result[0]['value'][1])
    print(f"Active database connections: {connections}")
    
    if connections > 80:  # Assuming max_connections = 100
        print(f"⚠️  High number of database connections: {connections}")
    
    return True


def run_smoke_tests(api_url: str) -> bool:
    """Exécuter des tests de fumée basiques."""
    print("\nRunning smoke tests...")
    
    # Test 1: Parsing CV
    try:
        response = requests.post(
            f"{api_url}/api/parse-cv/",
            files={'file': ('test.txt', b'Sample CV content')},
            timeout=30
        )
        if response.status_code in [200, 202]:
            print("✓ CV parsing endpoint is functional")
        else:
            print(f"✗ CV parsing endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ CV parsing test failed: {e}")
        return False
    
    # Test 2: Job parsing
    try:
        response = requests.post(
            f"{api_url}/api/analyze",
            json={'text': 'Sample job description'},
            timeout=30
        )
        if response.status_code in [200, 202]:
            print("✓ Job parsing endpoint is functional")
        else:
            print(f"✗ Job parsing endpoint returned {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Job parsing test failed: {e}")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Verify deployment health')
    parser.add_argument('--api-url', required=True, help='API base URL')
    parser.add_argument('--prometheus-url', required=True, help='Prometheus server URL')
    parser.add_argument('--skip-smoke-tests', action='store_true', help='Skip smoke tests')
    
    args = parser.parse_args()
    
    print("=== Deployment Verification ===")
    print(f"API URL: {args.api_url}")
    print(f"Prometheus URL: {args.prometheus_url}")
    print()
    
    try:
        prom = PrometheusConnect(url=args.prometheus_url)
        
        # Attendre que les métriques se stabilisent
        print("Waiting for metrics to stabilize...")
        time.sleep(30)
        
        checks = [
            ("Health endpoints", lambda: check_health_endpoints(args.api_url)),
            ("Service metrics", lambda: check_service_metrics(prom)),
            ("Error rates", lambda: check_error_rates(prom)),
            ("Response times", lambda: check_response_times(prom)),
            ("Resource usage", lambda: check_resource_usage(prom)),
            ("Database connections", lambda: check_database_connections(prom))
        ]
        
        if not args.skip_smoke_tests:
            checks.append(("Smoke tests", lambda: run_smoke_tests(args.api_url)))
        
        print("\n=== Running Verification Checks ===")
        
        results = []
        for check_name, check_func in checks:
            print(f"\n--- {check_name} ---")
            try:
                result = check_func()
                results.append(result)
                if result:
                    print(f"✓ {check_name} passed")
                else:
                    print(f"✗ {check_name} failed")
            except Exception as e:
                print(f"✗ {check_name} failed with error: {e}")
                results.append(False)
        
        print("\n=== Verification Summary ===")
        passed = sum(results)
        total = len(results)
        print(f"Passed: {passed}/{total}")
        
        if all(results):
            print("✓ All verification checks passed. Deployment is healthy.")
            sys.exit(0)
        else:
            print("✗ Some verification checks failed. Manual investigation required.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error during verification: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()