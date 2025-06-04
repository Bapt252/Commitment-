#!/usr/bin/env python3
"""Script pour générer un rapport de métriques détaillé."""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
from prometheus_api_client import PrometheusConnect
import requests


class MetricsReporter:
    """Générateur de rapports de métriques."""
    
    def __init__(self, prometheus_url: str):
        self.prom = PrometheusConnect(url=prometheus_url)
        self.report_data = {}
    
    def get_service_health(self) -> Dict[str, Any]:
        """Obtenir l'état de santé des services."""
        services = ['cv-parser', 'job-parser', 'matching-api', 'backend', 'frontend']
        health_data = {}
        
        for service in services:
            query = f'up{{job="{service}"}}'
            result = self.prom.custom_query(query)
            
            if result:
                health_data[service] = {
                    'status': 'up' if float(result[0]['value'][1]) == 1 else 'down',
                    'last_seen': result[0]['value'][0]
                }
            else:
                health_data[service] = {
                    'status': 'unknown',
                    'last_seen': None
                }
        
        return health_data
    
    def get_request_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Obtenir les métriques de requêtes."""
        # Taux de requêtes
        request_rate_query = f'sum(rate(http_requests_total[{hours}h]))'
        request_rate = self.prom.custom_query(request_rate_query)
        
        # Taux d'erreur
        error_rate_query = f'''
        (
            sum(rate(http_requests_total{{status_code!~"2.."}}[{hours}h])) /
            sum(rate(http_requests_total[{hours}h]))
        ) * 100
        '''
        error_rate = self.prom.custom_query(error_rate_query)
        
        # Temps de réponse
        response_time_query = f'''
        histogram_quantile(0.95, 
            sum(rate(http_request_duration_seconds_bucket[{hours}h])) by (le)
        )
        '''
        response_time = self.prom.custom_query(response_time_query)
        
        # Requêtes par service
        requests_by_service_query = f'sum(rate(http_requests_total[{hours}h])) by (service)'
        requests_by_service = self.prom.custom_query(requests_by_service_query)
        
        return {
            'total_request_rate': float(request_rate[0]['value'][1]) if request_rate else 0,
            'error_rate_percent': float(error_rate[0]['value'][1]) if error_rate else 0,
            'response_time_95th_percentile': float(response_time[0]['value'][1]) if response_time else 0,
            'requests_by_service': {
                item['metric']['service']: float(item['value'][1])
                for item in requests_by_service
            } if requests_by_service else {}
        }
    
    def get_ml_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Obtenir les métriques ML."""
        # Taux de succès ML
        ml_success_rate_query = f'''
        (
            sum(rate(ml_requests_total{{status="success"}}[{hours}h])) /
            sum(rate(ml_requests_total[{hours}h]))
        ) * 100
        '''
        ml_success_rate = self.prom.custom_query(ml_success_rate_query)
        
        # Temps de traitement ML
        ml_processing_time_query = f'''
        histogram_quantile(0.95, 
            sum(rate(ml_processing_duration_seconds_bucket[{hours}h])) by (le)
        )
        '''
        ml_processing_time = self.prom.custom_query(ml_processing_time_query)
        
        # Appels OpenAI
        openai_calls_query = f'sum(rate(openai_api_calls_total[{hours}h]))'
        openai_calls = self.prom.custom_query(openai_calls_query)
        
        # Tokens OpenAI
        openai_tokens_query = f'sum(rate(openai_tokens_total[{hours}h]))'
        openai_tokens = self.prom.custom_query(openai_tokens_query)
        
        # Erreurs ML par type
        ml_errors_by_type_query = f'sum(rate(ml_errors_total[{hours}h])) by (error_type)'
        ml_errors_by_type = self.prom.custom_query(ml_errors_by_type_query)
        
        return {
            'ml_success_rate_percent': float(ml_success_rate[0]['value'][1]) if ml_success_rate else 0,
            'ml_processing_time_95th_percentile': float(ml_processing_time[0]['value'][1]) if ml_processing_time else 0,
            'openai_calls_rate': float(openai_calls[0]['value'][1]) if openai_calls else 0,
            'openai_tokens_rate': float(openai_tokens[0]['value'][1]) if openai_tokens else 0,
            'ml_errors_by_type': {
                item['metric']['error_type']: float(item['value'][1])
                for item in ml_errors_by_type
            } if ml_errors_by_type else {}
        }
    
    def get_system_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Obtenir les métriques système."""
        # Usage CPU
        cpu_usage_query = f'avg(rate(container_cpu_usage_seconds_total[{hours}h])) * 100'
        cpu_usage = self.prom.custom_query(cpu_usage_query)
        
        # Usage mémoire
        memory_usage_query = f'''
        avg(container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100
        '''
        memory_usage = self.prom.custom_query(memory_usage_query)
        
        # Connexions base de données
        db_connections_query = 'pg_stat_database_numbackends{datname="nexten"}'
        db_connections = self.prom.custom_query(db_connections_query)
        
        # État Redis
        redis_connected_clients_query = 'redis_connected_clients'
        redis_clients = self.prom.custom_query(redis_connected_clients_query)
        
        return {
            'avg_cpu_usage_percent': float(cpu_usage[0]['value'][1]) if cpu_usage else 0,
            'avg_memory_usage_percent': float(memory_usage[0]['value'][1]) if memory_usage else 0,
            'database_connections': float(db_connections[0]['value'][1]) if db_connections else 0,
            'redis_connected_clients': float(redis_clients[0]['value'][1]) if redis_clients else 0
        }
    
    def get_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """Obtenir les tendances de performance."""
        # Tendance du taux d'erreur
        error_trend_query = f'''
        (
            sum(rate(http_requests_total{{status_code!~"2.."}}[1h])) /
            sum(rate(http_requests_total[1h]))
        ) * 100
        '''
        
        # Obtenir les données des derniers jours
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        error_trend = self.prom.custom_query_range(
            query=error_trend_query,
            start_time=start_time,
            end_time=end_time,
            step='1h'
        )
        
        # Tendance du temps de réponse
        response_time_trend_query = f'''
        histogram_quantile(0.95, 
            sum(rate(http_request_duration_seconds_bucket[1h])) by (le)
        )
        '''
        
        response_time_trend = self.prom.custom_query_range(
            query=response_time_trend_query,
            start_time=start_time,
            end_time=end_time,
            step='1h'
        )
        
        return {
            'error_rate_trend': error_trend[0]['values'] if error_trend else [],
            'response_time_trend': response_time_trend[0]['values'] if response_time_trend else []
        }
    
    def generate_alerts(self) -> List[Dict[str, Any]]:
        """Générer des alertes basées sur les métriques."""
        alerts = []
        
        # Vérifier le taux d'erreur
        error_rate = self.report_data.get('request_metrics', {}).get('error_rate_percent', 0)
        if error_rate > 5:
            alerts.append({
                'severity': 'warning' if error_rate < 10 else 'critical',
                'message': f'High error rate: {error_rate:.2f}%',
                'metric': 'error_rate',
                'value': error_rate,
                'threshold': 5
            })
        
        # Vérifier le temps de réponse
        response_time = self.report_data.get('request_metrics', {}).get('response_time_95th_percentile', 0)
        if response_time > 2:
            alerts.append({
                'severity': 'warning' if response_time < 5 else 'critical',
                'message': f'High response time: {response_time:.2f}s',
                'metric': 'response_time',
                'value': response_time,
                'threshold': 2
            })
        
        # Vérifier l'usage CPU
        cpu_usage = self.report_data.get('system_metrics', {}).get('avg_cpu_usage_percent', 0)
        if cpu_usage > 80:
            alerts.append({
                'severity': 'warning' if cpu_usage < 90 else 'critical',
                'message': f'High CPU usage: {cpu_usage:.2f}%',
                'metric': 'cpu_usage',
                'value': cpu_usage,
                'threshold': 80
            })
        
        # Vérifier l'usage mémoire
        memory_usage = self.report_data.get('system_metrics', {}).get('avg_memory_usage_percent', 0)
        if memory_usage > 85:
            alerts.append({
                'severity': 'warning' if memory_usage < 95 else 'critical',
                'message': f'High memory usage: {memory_usage:.2f}%',
                'metric': 'memory_usage',
                'value': memory_usage,
                'threshold': 85
            })
        
        # Vérifier les services down
        service_health = self.report_data.get('service_health', {})
        for service, health in service_health.items():
            if health['status'] != 'up':
                alerts.append({
                    'severity': 'critical',
                    'message': f'Service {service} is {health["status"]}',
                    'metric': 'service_health',
                    'value': health['status'],
                    'service': service
                })
        
        return alerts
    
    def generate_report(self, hours: int = 24, days: int = 7) -> Dict[str, Any]:
        """Générer le rapport complet."""
        print("Collecting service health metrics...")
        self.report_data['service_health'] = self.get_service_health()
        
        print("Collecting request metrics...")
        self.report_data['request_metrics'] = self.get_request_metrics(hours)
        
        print("Collecting ML metrics...")
        self.report_data['ml_metrics'] = self.get_ml_metrics(hours)
        
        print("Collecting system metrics...")
        self.report_data['system_metrics'] = self.get_system_metrics(hours)
        
        print("Collecting performance trends...")
        self.report_data['performance_trends'] = self.get_performance_trends(days)
        
        print("Generating alerts...")
        self.report_data['alerts'] = self.generate_alerts()
        
        # Ajouter des métadonnées
        self.report_data['metadata'] = {
            'generated_at': datetime.now().isoformat(),
            'time_range_hours': hours,
            'trend_days': days,
            'total_alerts': len(self.report_data['alerts']),
            'critical_alerts': len([a for a in self.report_data['alerts'] if a['severity'] == 'critical'])
        }
        
        return self.report_data
    
    def save_report(self, output_file: str):
        """Sauvegarder le rapport en JSON."""
        with open(output_file, 'w') as f:
            json.dump(self.report_data, f, indent=2, default=str)
        
        print(f"Report saved to {output_file}")
    
    def print_summary(self):
        """Afficher un résumé du rapport."""
        print("\n=== METRICS REPORT SUMMARY ===")
        print(f"Generated at: {self.report_data['metadata']['generated_at']}")
        print(f"Time range: {self.report_data['metadata']['time_range_hours']} hours")
        print()
        
        # Santé des services
        print("Service Health:")
        for service, health in self.report_data['service_health'].items():
            status_icon = "✓" if health['status'] == 'up' else "✗"
            print(f"  {status_icon} {service}: {health['status']}")
        print()
        
        # Métriques clés
        request_metrics = self.report_data['request_metrics']
        print("Key Metrics:")
        print(f"  Request rate: {request_metrics['total_request_rate']:.2f} req/s")
        print(f"  Error rate: {request_metrics['error_rate_percent']:.2f}%")
        print(f"  Response time (95th): {request_metrics['response_time_95th_percentile']:.3f}s")
        
        ml_metrics = self.report_data['ml_metrics']
        print(f"  ML success rate: {ml_metrics['ml_success_rate_percent']:.2f}%")
        print(f"  OpenAI calls rate: {ml_metrics['openai_calls_rate']:.2f} calls/s")
        print()
        
        # Alertes
        alerts = self.report_data['alerts']
        if alerts:
            print(f"Alerts ({len(alerts)}):")
            for alert in alerts:
                severity_icon = "🚨" if alert['severity'] == 'critical' else "⚠️"
                print(f"  {severity_icon} {alert['message']}")
        else:
            print("✓ No alerts")
        print()


def main():
    parser = argparse.ArgumentParser(description='Generate metrics report')
    parser.add_argument('--prometheus-url', required=True, help='Prometheus server URL')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--hours', type=int, default=24, help='Time range in hours')
    parser.add_argument('--days', type=int, default=7, help='Trend analysis days')
    parser.add_argument('--summary', action='store_true', help='Print summary to console')
    
    args = parser.parse_args()
    
    try:
        reporter = MetricsReporter(args.prometheus_url)
        print("Generating metrics report...")
        
        report = reporter.generate_report(args.hours, args.days)
        reporter.save_report(args.output)
        
        if args.summary:
            reporter.print_summary()
        
        # Code de sortie basé sur les alertes critiques
        critical_alerts = len([a for a in report['alerts'] if a['severity'] == 'critical'])
        if critical_alerts > 0:
            print(f"\nWARNING: {critical_alerts} critical alerts found!")
            sys.exit(1)
        else:
            print("\n✓ Report generated successfully, no critical issues.")
            sys.exit(0)
    
    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
