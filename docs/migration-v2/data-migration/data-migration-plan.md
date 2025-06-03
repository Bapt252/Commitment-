# Plan de Migration des Données - SuperSmartMatch V1→V2

## 🎯 Objectif
Migration sécurisée des données et état entre V1 (port 5062) et V2 (port 5070) sans perte ni corruption durant la coexistence.

## 📊 Analyse des Données

### Services Source
```yaml
V1 SuperSmartMatch (5062):
  - Cache Redis: clés "match:*", "candidate:*"
  - Sessions actives: format "offers" legacy
  - Métriques historiques: 6 mois données
  - Configuration: algorithmes weights

Nexten Matcher (5052):
  - ML Models: 40K lignes état
  - Training data: embeddings cache
  - Performance metrics: temps réponse
  - Feature flags: ML activations
```

### Service Cible V2 (5070)
```yaml
Format unifié:
  - "offers" → "jobs" transformation
  - Cache consolidé multi-algorithmes
  - Métriques unifiées V1+Nexten
  - Configuration centralisée
```

## 🔄 Stratégie de Migration Progressive

### Phase 1: Synchronisation Bidirectionnelle (J-7 à J-1)
```bash
# Service de sync temps réel
services:
  data-sync:
    image: supersmartmatch/data-sync:v1.0
    environment:
      - SOURCE_V1=redis://v1-redis:6379
      - SOURCE_NEXTEN=redis://nexten-redis:6379
      - TARGET_V2=redis://v2-redis:6379
      - SYNC_MODE=bidirectional
      - TRANSFORM_FORMAT=offers_to_jobs
```

### Phase 2: Migration Sessions Actives (J-Day)
```python
# Script migration sessions
def migrate_active_sessions():
    active_sessions = redis_v1.keys("session:*")
    for session_key in active_sessions:
        session_data = redis_v1.hgetall(session_key)
        
        # Transform format offers → jobs
        transformed_data = transform_session_format(session_data)
        
        # Dual write: V1 + V2
        redis_v1.hset(session_key, mapping=session_data)
        redis_v2.hset(session_key, mapping=transformed_data)
        
        # TTL preservation
        ttl = redis_v1.ttl(session_key)
        redis_v2.expire(session_key, ttl)
```

### Phase 3: Validation Cohérence (Temps Réel)
```yaml
Métriques de validation:
  - sync_lag: <100ms entre V1/V2
  - data_integrity: 100% checksum match
  - session_consistency: 0 session perdue
  - cache_hit_preservation: >95% maintained
```

## 🔐 Sécurité des Données

### Backup Avant Migration
```bash
# Backup automatisé
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Redis V1 backup
redis-cli --rdb /backups/v1_${TIMESTAMP}.rdb

# Nexten state backup
tar -czf /backups/nexten_${TIMESTAMP}.tar.gz /app/nexten/models/

# V2 state backup (rollback point)
redis-cli -p 6380 --rdb /backups/v2_${TIMESTAMP}.rdb
```

### Validation Intégrité
```python
def validate_data_integrity():
    # Checksum comparison
    v1_checksums = calculate_cache_checksums(redis_v1)
    v2_checksums = calculate_cache_checksums(redis_v2, transform=True)
    
    integrity_score = compare_checksums(v1_checksums, v2_checksums)
    
    if integrity_score < 0.999:
        trigger_rollback("Data integrity failed")
    
    return integrity_score
```

## 📈 Monitoring Migration

### Métriques Temps Réel
```yaml
Dashboards Grafana:
  migration_progress:
    - sync_completion_percentage
    - data_consistency_score
    - active_sessions_migrated
    - cache_hit_ratio_v1_vs_v2
  
  performance_impact:
    - response_time_degradation
    - memory_usage_during_sync
    - cpu_impact_migration
    - network_bandwidth_sync
```

### Alerting Migration
```yaml
Prometheus Alerts:
  - SyncLagHigh: sync_lag > 500ms
  - DataInconsistency: integrity_score < 0.95
  - SessionLoss: active_sessions_lost > 0
  - MigrationStalled: sync_progress unchanged 5min
```

## 🔄 Plan de Rollback Données

### Triggers Automatiques
```yaml
Conditions rollback:
  - Data integrity < 95%
  - Sessions perdues > 0
  - Sync lag > 1000ms sustained
  - Cache corruption détectée
```

### Procédure de Restauration
```bash
#!/bin/bash
# Rollback automatisé
echo "🚨 ROLLBACK DATA MIGRATION INITIATED"

# Stop sync service
docker-compose stop data-sync

# Restore V1 backup
redis-cli FLUSHALL
redis-cli --rdb /backups/v1_latest.rdb

# Clear V2 inconsistent data
redis-cli -p 6380 FLUSHALL

# Restart V1 services
docker-compose restart supersmartmatch-v1 nexten

echo "✅ Data rollback completed - V1 restored"
```

## 📋 Checklist Validation

### Pre-Migration
- [ ] Backup V1/Nexten complets
- [ ] Service sync testé en staging
- [ ] Scripts transformation validés
- [ ] Monitoring dashboards opérationnels

### Pendant Migration
- [ ] Sync lag < 100ms maintenu
- [ ] Integrity score > 99.9%
- [ ] Sessions actives préservées
- [ ] Performance impact < 5%

### Post-Migration
- [ ] Validation intégrité complète
- [ ] Tests fonctionnels V2 OK
- [ ] Monitoring comparatif actif
- [ ] Plan rollback testé et ready

## 🎯 Critères de Succès

**Zero Data Loss**: 100% des sessions et cache préservés
**Format Consistency**: Transformation offers→jobs validée
**Performance**: Impact migration < 5% response time
**Rollback Ready**: Restauration < 2min si nécessaire