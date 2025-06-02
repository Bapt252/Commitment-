"""
SuperSmartMatch V2 - Collecteur de métriques
============================================

Collecte et gestion des métriques de performance en temps réel.
Support pour Redis et Prometheus.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque

import redis.asyncio as redis
from prometheus_client import Counter, Histogram, Gauge, start_http_server

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class MatchingMetric:
    """Métrique d'une requête de matching"""
    timestamp: float
    algorithm: str
    duration: float
    success: bool
    num_jobs: int
    num_results: int
    error_type: Optional[str] = None


@dataclass
class SystemMetric:
    """Métrique système"""
    timestamp: float
    metric_type: str
    value: float
    tags: Dict[str, str]


class MetricsCollector:
    """Collecteur de métriques pour SuperSmartMatch V2"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.metrics_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.prometheus_enabled = getattr(settings, 'prometheus_enabled', True)
        self.start_time = time.time()
        
        # Métriques Prometheus
        if self.prometheus_enabled:
            self._init_prometheus_metrics()
    
    def _init_prometheus_metrics(self):
        """Initialise les métriques Prometheus"""
        self.request_counter = Counter(
            'supersmartmatch_v2_requests_total',
            'Nombre total de requêtes',
            ['algorithm', 'success']
        )
        
        self.request_duration = Histogram(
            'supersmartmatch_v2_request_duration_seconds',
            'Durée des requêtes en secondes',
            ['algorithm']
        )
        
        self.active_requests = Gauge(
            'supersmartmatch_v2_active_requests',
            'Nombre de requêtes actives'
        )
        
        self.algorithm_selection = Counter(
            'supersmartmatch_v2_algorithm_selections_total',
            'Sélections d\'algorithmes',
            ['algorithm']
        )
        
        self.external_service_status = Gauge(
            'supersmartmatch_v2_external_service_status',
            'Status des services externes',
            ['service']
        )
        
        self.circuit_breaker_state = Gauge(
            'supersmartmatch_v2_circuit_breaker_state',
            'État des circuit breakers',
            ['service', 'state']
        )
    
    async def initialize(self):
        """Initialise le collecteur de métriques"""
        try:
            # Connexion Redis si activée
            if getattr(settings, 'cache_enabled', True):
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    max_connections=getattr(settings, 'redis_max_connections', 20)
                )
                
                # Test de connexion
                await self.redis_client.ping()
                logger.info("✅ Connexion Redis établie pour les métriques")
            
            # Démarrage du serveur Prometheus si activé
            if self.prometheus_enabled:
                prometheus_port = getattr(settings, 'prometheus_port', 9090)
                start_http_server(prometheus_port)
                logger.info(f"✅ Serveur Prometheus démarré sur port {prometheus_port}")
            
            # Démarrage des tâches de nettoyage
            asyncio.create_task(self._cleanup_old_metrics())
            
            logger.info("✅ MetricsCollector initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation des métriques: {e}")
            # Ne pas faire planter l'app si les métriques échouent
    
    async def cleanup(self):
        """Nettoyage des ressources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                logger.info("✅ Connexion Redis fermée")
        except Exception as e:
            logger.error(f"❌ Erreur lors du nettoyage des métriques: {e}")
    
    async def record_matching_request(
        self,
        algorithm: str,
        duration: float,
        success: bool,
        num_jobs: int,
        num_results: int,
        error_type: Optional[str] = None
    ):
        """Enregistre une métrique de requête de matching"""
        
        metric = MatchingMetric(
            timestamp=time.time(),
            algorithm=algorithm,
            duration=duration,
            success=success,
            num_jobs=num_jobs,
            num_results=num_results,
            error_type=error_type
        )
        
        # Cache local
        self.metrics_cache['matching_requests'].append(metric)
        
        # Redis
        if self.redis_client:
            try:
                await self._store_metric_in_redis('matching_requests', metric)
            except Exception as e:
                logger.warning(f"Erreur Redis pour métrique: {e}")
        
        # Prometheus
        if self.prometheus_enabled:
            self.request_counter.labels(
                algorithm=algorithm,
                success=str(success)
            ).inc()
            
            self.request_duration.labels(algorithm=algorithm).observe(duration)
            
            self.algorithm_selection.labels(algorithm=algorithm).inc()
        
        logger.debug(f"📊 Métrique enregistrée: {algorithm} - {duration:.3f}s - Succès: {success}")
    
    async def record_error(self, error_type: str, endpoint: str):
        """Enregistre une erreur"""
        
        metric = {
            'timestamp': time.time(),
            'error_type': error_type,
            'endpoint': endpoint
        }
        
        # Cache local
        self.metrics_cache['errors'].append(metric)
        
        # Redis
        if self.redis_client:
            try:
                cache_prefix = getattr(settings, 'cache_prefix', 'supersmartmatch_v2')
                key = f"{cache_prefix}:errors"
                await self.redis_client.lpush(key, json.dumps(metric))
                retention_hours = getattr(settings, 'metrics_retention_hours', 24)
                await self.redis_client.expire(key, retention_hours * 3600)
            except Exception as e:
                logger.warning(f"Erreur Redis pour erreur: {e}")
    
    async def record_external_service_status(self, service: str, status: bool):
        """Enregistre le status d'un service externe"""
        
        if self.prometheus_enabled:
            self.external_service_status.labels(service=service).set(1 if status else 0)
        
        # Cache local
        self.metrics_cache['service_status'][service] = {
            'status': status,
            'timestamp': time.time()
        }
    
    async def record_circuit_breaker_state(self, service: str, state: str):
        """Enregistre l'état d'un circuit breaker"""
        
        if self.prometheus_enabled:
            # Reset all states for this service
            for s in ['closed', 'open', 'half_open']:
                self.circuit_breaker_state.labels(service=service, state=s).set(0)
            
            # Set current state
            self.circuit_breaker_state.labels(service=service, state=state).set(1)
        
        logger.info(f"🔧 Circuit breaker {service}: {state}")
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques actuelles"""
        
        try:
            # Métriques de base
            metrics = {
                'timestamp': time.time(),
                'version': '2.0.0',
                'uptime_seconds': time.time() - self.start_time
            }
            
            # Métriques des requêtes
            matching_metrics = list(self.metrics_cache['matching_requests'])
            if matching_metrics:
                total_requests = len(matching_metrics)
                successful_requests = sum(1 for m in matching_metrics if m.success)
                
                metrics.update({
                    'total_requests': total_requests,
                    'successful_requests': successful_requests,
                    'success_rate': successful_requests / total_requests if total_requests > 0 else 0,
                    'average_duration': sum(m.duration for m in matching_metrics) / total_requests if total_requests > 0 else 0
                })
                
                # Répartition par algorithme
                algorithm_stats = defaultdict(lambda: {'count': 0, 'success': 0, 'duration': 0})
                for metric in matching_metrics:
                    stats = algorithm_stats[metric.algorithm]
                    stats['count'] += 1
                    if metric.success:
                        stats['success'] += 1
                    stats['duration'] += metric.duration
                
                # Calcul des moyennes
                for algo, stats in algorithm_stats.items():
                    if stats['count'] > 0:
                        stats['success_rate'] = stats['success'] / stats['count']
                        stats['avg_duration'] = stats['duration'] / stats['count']
                
                metrics['algorithm_stats'] = dict(algorithm_stats)
            
            # Status des services externes
            metrics['external_services'] = dict(self.metrics_cache['service_status'])
            
            # Métriques des dernières 24h depuis Redis si disponible
            if self.redis_client:
                try:
                    historical_metrics = await self._get_historical_metrics()
                    metrics['historical'] = historical_metrics
                except Exception as e:
                    logger.warning(f"Erreur récupération métriques historiques: {e}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des métriques: {e}")
            return {'error': str(e), 'timestamp': time.time()}
    
    async def _store_metric_in_redis(self, metric_type: str, metric: MatchingMetric):
        """Stocke une métrique dans Redis"""
        
        cache_prefix = getattr(settings, 'cache_prefix', 'supersmartmatch_v2')
        key = f"{cache_prefix}:metrics:{metric_type}"
        data = asdict(metric)
        
        # Ajout avec timestamp pour tri temporel
        await self.redis_client.zadd(key, {json.dumps(data): metric.timestamp})
        
        # Nettoyage des anciennes métriques (garde les dernières 24h)
        retention_hours = getattr(settings, 'metrics_retention_hours', 24)
        cutoff = time.time() - (retention_hours * 3600)
        await self.redis_client.zremrangebyscore(key, 0, cutoff)
    
    async def _get_historical_metrics(self) -> Dict[str, Any]:
        """Récupère les métriques historiques depuis Redis"""
        
        cache_prefix = getattr(settings, 'cache_prefix', 'supersmartmatch_v2')
        key = f"{cache_prefix}:metrics:matching_requests"
        
        # Récupération des données des dernières 24h
        cutoff = time.time() - (24 * 3600)
        raw_data = await self.redis_client.zrangebyscore(key, cutoff, '+inf')
        
        if not raw_data:
            return {}
        
        # Parse des données
        metrics = []
        for data in raw_data:
            try:
                metric = json.loads(data)
                metrics.append(metric)
            except json.JSONDecodeError:
                continue
        
        if not metrics:
            return {}
        
        # Calculs historiques
        total = len(metrics)
        successful = sum(1 for m in metrics if m['success'])
        
        # Répartition par heure
        hourly_stats = defaultdict(lambda: {'count': 0, 'success': 0})
        for metric in metrics:
            hour = int(metric['timestamp']) // 3600 * 3600
            hourly_stats[hour]['count'] += 1
            if metric['success']:
                hourly_stats[hour]['success'] += 1
        
        return {
            'period_hours': 24,
            'total_requests': total,
            'success_rate': successful / total if total > 0 else 0,
            'hourly_distribution': dict(hourly_stats)
        }
    
    async def _cleanup_old_metrics(self):
        """Tâche de nettoyage périodique des métriques"""
        
        while True:
            try:
                cleanup_interval = getattr(settings, 'metrics_cleanup_interval', 3600)
                await asyncio.sleep(cleanup_interval)
                
                # Nettoyage du cache local
                retention_hours = getattr(settings, 'metrics_retention_hours', 24)
                cutoff = time.time() - (retention_hours * 3600)
                
                for metric_type, metrics in self.metrics_cache.items():
                    if metric_type == 'matching_requests':
                        # Garde seulement les métriques récentes
                        while metrics and metrics[0].timestamp < cutoff:
                            metrics.popleft()
                
                logger.debug("🧹 Nettoyage des métriques anciennes effectué")
                
            except Exception as e:
                logger.error(f"❌ Erreur lors du nettoyage des métriques: {e}")
    
    def set_active_requests(self, count: int):
        """Met à jour le nombre de requêtes actives"""
        if self.prometheus_enabled:
            self.active_requests.set(count)
