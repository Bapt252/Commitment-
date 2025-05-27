# ADR-003: Stratégie de Cache Multi-Niveaux

## Statut
**ACCEPTÉ** - Date: 2025-05-27

## Contexte
SuperSmartMatch V1 souffre de performances insuffisantes avec des temps de réponse >2s pour des requêtes complexes. L'audit a identifié l'absence de stratégie de cache comme un facteur critique.

### Problèmes V1 identifiés :
- Pas de cache pour les calculs de géolocalisation
- Recalcul systématique des scores de matching
- Requêtes répétitives sur la base de données
- Parsing redondant des mêmes CV/jobs
- Latence élevée pour les requêtes d'analytics

### Objectifs de Performance V2 :
- **95% des requêtes en <200ms**
- **Cache hit rate >90%**
- **Réduction de 80% de la charge DB**
- **Support 10x du traffic concurrent**

## Décision

Nous implémentons une **stratégie de cache multi-niveaux (L1, L2, L3)** avec invalidation intelligente et TTL adaptatifs.

### Architecture de Cache

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   L1 Cache      │    │    L2 Cache      │    │   L3 Cache      │
│  (In-Memory)    │◄──►│  (Redis Cluster) │◄──►│ (Materialized   │
│                 │    │                  │    │  Views)         │
│ • LRU           │    │ • Distributed    │    │ • PostgreSQL    │
│ • 100MB/pod     │    │ • 64GB total     │    │ • Refresh 15min │
│ • TTL 5min      │    │ • TTL 1-24h      │    │ • Partitioned   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Stratégie par Couche

### L1 Cache - In-Memory Application

**Technologie :** Python `cachetools` + Go `golang-lru`

**Utilisation :**
- Données ultra-fréquentes (user sessions, preferences)
- Résultats de calculs récents
- Configuration et paramètres système

**Configuration :**
```python
from cachetools import TTLCache, LRUCache

# Cache des sessions utilisateur
user_cache = TTLCache(maxsize=10000, ttl=300)  # 5 minutes

# Cache des configurations
config_cache = LRUCache(maxsize=1000)

# Cache des résultats de matching récents
matching_cache = TTLCache(maxsize=5000, ttl=180)  # 3 minutes
```

### L2 Cache - Redis Cluster Distribué

**Technologie :** Redis Cluster 7.0+

**Configuration Cluster :**
```yaml
Redis Cluster:
  nodes: 6 (3 master, 3 replica)
  memory_per_node: 16GB
  total_memory: 96GB
  persistence: RDB snapshot every 15min
  eviction_policy: allkeys-lru
  maxmemory_samples: 10
```

**Données Cachées :**
```python
# Structure des clés Redis optimisée
CACHE_KEYS = {
    # Géolocalisation (TTL: 7 jours)
    "geo:distance:{origin}:{destination}": "travel_time_minutes",
    "geo:geocode:{address}": "lat,lng,formatted_address",
    
    # Matching scores (TTL: 1 heure)
    "match:{candidate_id}:{job_id}:{algorithm}": "score_data",
    "match:bulk:{query_hash}": "matching_results",
    
    # Profils utilisateur (TTL: 24 heures)
    "profile:candidate:{id}": "parsed_cv_data",
    "profile:job:{id}": "parsed_job_data",
    
    # Analytics (TTL: 6 heures)
    "analytics:stats:{date}:{sector}": "aggregated_stats",
    "analytics:trends:{period}": "trend_data"
}
```

**Client Redis Optimisé :**
```python
import redis.asyncio as redis
from redis.cluster import RedisCluster

class SmartCacheClient:
    def __init__(self):
        self.redis = RedisCluster(
            startup_nodes=[
                {"host": "redis-node1", "port": 7000},
                {"host": "redis-node2", "port": 7000},
                {"host": "redis-node3", "port": 7000}
            ],
            decode_responses=True,
            max_connections_per_node=50,
            health_check_interval=30
        )
    
    async def get_or_compute(self, key: str, compute_func, ttl: int = 3600):
        """Pattern: Cache-aside avec fallback"""
        try:
            # Tentative lecture cache
            cached = await self.redis.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        
        # Fallback: calcul et mise en cache
        result = await compute_func()
        try:
            await self.redis.setex(key, ttl, json.dumps(result))
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
        
        return result
    
    async def batch_get(self, keys: List[str]) -> Dict[str, Any]:
        """Récupération batch optimisée"""
        pipe = self.redis.pipeline()
        for key in keys:
            pipe.get(key)
        
        results = await pipe.execute()
        return {
            key: json.loads(value) if value else None 
            for key, value in zip(keys, results)
        }
```

### L3 Cache - Materialized Views Database

**Technologie :** PostgreSQL Materialized Views

**Utilisation :**
- Agrégations complexes pour analytics
- Données de référence (secteurs, compétences)
- Statistiques pré-calculées

**Configuration :**
```sql
-- Vue matérialisée pour statistiques matching
CREATE MATERIALIZED VIEW mv_matching_stats AS
SELECT 
    DATE_TRUNC('hour', created_at) as hour,
    job_sector,
    COUNT(*) as total_matches,
    AVG(matching_score) as avg_score,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY matching_score) as p95_score
FROM matches 
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY hour, job_sector;

-- Index pour accès rapide
CREATE INDEX idx_mv_matching_stats_hour 
ON mv_matching_stats (hour DESC, job_sector);

-- Refresh automatique
CREATE OR REPLACE FUNCTION refresh_matching_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_matching_stats;
END;
$$ LANGUAGE plpgsql;

-- Planification refresh toutes les 15 minutes
SELECT cron.schedule('refresh-stats', '*/15 * * * *', 'SELECT refresh_matching_stats();');
```

## Stratégies TTL par Type de Données

### TTL Statiques
```python
TTL_CONFIG = {
    # Données quasi-immutables
    'user_profiles': 24 * 3600,      # 24 heures
    'job_descriptions': 6 * 3600,     # 6 heures
    'company_data': 7 * 24 * 3600,    # 7 jours
    
    # Données calculées
    'matching_scores': 3600,          # 1 heure
    'geo_distances': 7 * 24 * 3600,   # 7 jours
    'skill_embeddings': 24 * 3600,    # 24 heures
    
    # Données temps réel
    'user_sessions': 1800,            # 30 minutes
    'api_rate_limits': 60,            # 1 minute
    'health_checks': 30,              # 30 secondes
    
    # Analytics
    'daily_stats': 4 * 3600,          # 4 heures
    'trend_analysis': 2 * 3600,       # 2 heures
    'ml_predictions': 1800            # 30 minutes
}
```

### TTL Adaptatifs
```python
class AdaptiveTTL:
    def __init__(self):
        self.access_patterns = {}
    
    def calculate_ttl(self, key: str, base_ttl: int) -> int:
        """Ajuste TTL selon fréquence d'accès"""
        pattern = self.access_patterns.get(key, {'hits': 0, 'last_access': 0})
        
        now = time.time()
        time_since_access = now - pattern['last_access']
        
        # TTL plus long pour données très accédées
        if pattern['hits'] > 100 and time_since_access < 3600:
            return base_ttl * 2
        
        # TTL plus court pour données peu accédées
        elif pattern['hits'] < 10 and time_since_access > 7200:
            return base_ttl // 2
        
        return base_ttl
```

## Invalidation Intelligente

### Event-Driven Invalidation
```python
from typing import List

class CacheInvalidator:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.invalidation_patterns = {
            'user_updated': ['profile:candidate:{user_id}', 'match:*:{user_id}:*'],
            'job_updated': ['profile:job:{job_id}', 'match:*:*:{job_id}'],
            'algorithm_updated': ['match:*:*:{algorithm}'],
            'geo_data_updated': ['geo:*']
        }
    
    async def invalidate_on_event(self, event_type: str, entity_id: str):
        """Invalidation basée sur les événements métier"""
        patterns = self.invalidation_patterns.get(event_type, [])
        
        for pattern in patterns:
            key_pattern = pattern.format(
                user_id=entity_id,
                job_id=entity_id,
                algorithm=entity_id
            )
            
            # Scan et suppression des clés matchées
            async for key in self.redis.scan_iter(match=key_pattern):
                await self.redis.delete(key)
                
        logger.info(f"Invalidated cache for event {event_type}:{entity_id}")
```

### Cache Warming
```python
class CacheWarmer:
    def __init__(self, cache_client, db_client):
        self.cache = cache_client
        self.db = db_client
    
    async def warm_popular_data(self):
        """Pré-charge les données populaires"""
        # Top entreprises et jobs consultés
        popular_jobs = await self.db.get_popular_jobs(limit=1000)
        
        tasks = []
        for job in popular_jobs:
            task = self._warm_job_data(job['id'])
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _warm_job_data(self, job_id: str):
        """Précharge données job spécifique"""
        # Parsing job si pas en cache
        await self.cache.get_or_compute(
            f"profile:job:{job_id}",
            lambda: self.parse_job(job_id),
            ttl=6*3600
        )
        
        # Géocodage localisation
        job_data = await self.db.get_job(job_id)
        if job_data.get('location'):
            await self.cache.get_or_compute(
                f"geo:geocode:{job_data['location']}",
                lambda: self.geocode(job_data['location']),
                ttl=7*24*3600
            )
```

## Monitoring et Métriques

### Métriques de Performance Cache
```python
from prometheus_client import Counter, Histogram, Gauge

# Métriques Prometheus
cache_hits = Counter('cache_hits_total', 'Total cache hits', ['level', 'operation'])
cache_misses = Counter('cache_misses_total', 'Total cache misses', ['level', 'operation'])
cache_latency = Histogram('cache_operation_duration_seconds', 'Cache operation latency')
cache_memory_usage = Gauge('cache_memory_bytes', 'Cache memory usage', ['level'])

class MonitoredCache:
    def __init__(self, cache_client):
        self.cache = cache_client
    
    async def get(self, key: str):
        start_time = time.time()
        try:
            result = await self.cache.get(key)
            if result:
                cache_hits.labels(level='L2', operation='get').inc()
            else:
                cache_misses.labels(level='L2', operation='get').inc()
            return result
        finally:
            cache_latency.observe(time.time() - start_time)
```

### Dashboard Grafana
```yaml
Cache Metrics Dashboard:
  Panels:
    - Cache Hit Ratio by Level
    - Average Response Time by Operation
    - Memory Usage Trends
    - Cache Eviction Rate
    - Top Cache Keys by Access Frequency
    - Cache Invalidation Events
```

## Tests de Performance

### Benchmark Cache Hit Scenarios
```python
import pytest
import asyncio
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_cache_performance():
    """Test performance cache multi-niveaux"""
    cache = SmartCacheClient()
    
    # Simulation 1000 requêtes identiques
    start_time = time.time()
    
    tasks = []
    for i in range(1000):
        task = cache.get_or_compute(
            "test:key:123",
            lambda: expensive_computation(),
            ttl=3600
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    duration = time.time() - start_time
    
    # Assertions performance
    assert duration < 5.0  # Moins de 5 secondes pour 1000 requêtes
    assert all(r == results[0] for r in results)  # Cohérence
    
async def expensive_computation():
    """Simulation calcul coûteux"""
    await asyncio.sleep(0.1)  # 100ms
    return {"result": "computed_value", "timestamp": time.time()}
```

## Coûts et Dimensionnement

### Estimation Ressources
```yaml
Cache Infrastructure Costs:
  Redis Cluster (Production):
    - 6 nodes x 16GB RAM: $1,200/month
    - Network bandwidth: $200/month
    - Backup storage: $100/month
    
  Application Memory (L1):
    - 20 pods x 2GB cache: 40GB total
    - No additional cost (included in pod memory)
    
  Database (L3 - Materialized Views):
    - Additional storage: 100GB
    - Additional compute: 2 vCPU
    - Estimated cost: $300/month
    
Total Cache Infrastructure: ~$1,800/month
```

### ROI Estimé
```yaml
Performance Gains:
  - Database load reduction: -80%
  - Average response time: -70% (from 800ms to 240ms)
  - Infrastructure scaling needs: -50%
  
Cost Savings:
  - Database instance downsizing: -$800/month
  - Reduced auto-scaling events: -$400/month
  - Lower bandwidth costs: -$200/month
  
Net ROI: +$400/month (Cost reduction exceeds cache costs)
```

## Migration Strategy

### Phase 1: Infrastructure Setup
```bash
# Déploiement Redis Cluster
helm install redis-cluster bitnami/redis-cluster \
  --set cluster.nodes=6 \
  --set cluster.replicas=1 \
  --set auth.enabled=true \
  --set persistence.enabled=true

# Configuration monitoring
kubectl apply -f monitoring/redis-exporter.yaml
```

### Phase 2: Application Integration
```python
# Migration graduelle service par service
CACHE_ROLLOUT_PLAN = {
    'week_1': ['geolocation-service'],
    'week_2': ['scoring-engine', 'parsing-service'],
    'week_3': ['behavior-service', 'analytics-service'],
    'week_4': ['all-remaining-services']
}
```

### Phase 3: Optimization
- Monitoring cache hit rates
- Ajustement TTL selon patterns d'usage
- Cache warming automatique
- Fine-tuning configurations

## Alternatives Considérées

### Autres Solutions de Cache
- **Memcached** ❌ : Fonctionnalités limitées vs Redis
- **Hazelcast** ⚖️ : Plus complexe, moins adopté
- **Apache Ignite** ❌ : Overhead Java important
- **Amazon ElastiCache** ⚖️ : Vendor lock-in

### Patterns Alternatifs
- **Write-through** ❌ : Latence d'écriture élevée
- **Write-behind** ❌ : Risque de perte de données
- **Cache-aside** ✅ : Choisi pour flexibilité

## Risques et Mitigations

### Risques Identifiés
1. **Cache invalidation complexity** → Event-driven invalidation
2. **Memory pressure on Redis** → Monitoring + auto-scaling
3. **Cache stampede** → Lock mechanisms
4. **Data consistency** → TTL courts pour données critiques

### Monitoring Critiques
```yaml
Alerts Configuration:
  - Redis memory usage >85%
  - Cache hit rate <80%
  - Cache latency P95 >10ms
  - Redis cluster node down
  - Excessive cache evictions
```

## Validation et Métriques de Succès

Cette stratégie sera validée par :
- **Cache hit rate >90%** sur 30 jours
- **Réduction latence P95 >60%** vs. baseline sans cache
- **Réduction charge DB >70%** mesurée en QPS
- **Zero cache-related incidents** pendant 3 mois

---
**Auteur**: Performance Engineering Team  
**Reviewers**: Architecture Team, SRE Team  
**Approbation finale**: CTO - 2025-05-27