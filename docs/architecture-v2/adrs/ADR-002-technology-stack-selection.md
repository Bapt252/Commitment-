# ADR-002: Sélection du Stack Technologique V2

## Statut
**ACCEPTÉ** - Date: 2025-05-27

## Contexte
Le choix des technologies pour SuperSmartMatch V2 est critique pour atteindre les objectifs de performance :
- **Latence** : <200ms pour 10 offres, <2s pour 100+ offres
- **Throughput** : 1000+ matchings/minute
- **Disponibilité** : 99.9% uptime
- **Scalabilité** : Support 10x croissance utilisateurs

## Décisions Technologiques

### 1. Langages de Programmation

#### Python 3.11+ pour Services ML/AI
**Justification :**
- Écosystème ML/AI mature (scikit-learn, TensorFlow, PyTorch)
- Bibliothèques de parsing avancées (spaCy, NLTK)
- FastAPI pour APIs haute performance
- Expertise équipe existante

**Services concernés :**
- Scoring Engine Service
- Parsing Service
- Behavior Analytics Service
- Explainability Service

#### Go pour Services Performance-Critiques
**Justification :**
- Performance native exceptionnelle
- Concurrence native (goroutines)
- Faible consommation mémoire
- Compilation statique (containers optimisés)

**Services concernés :**
- API Gateway
- Geolocation Service (calculs intensifs)
- Cache Service

#### TypeScript/Node.js pour Services I/O
**Justification :**
- Excellent pour I/O asynchrone
- Écosystème frontend partagé
- Développement rapide
- Event-driven architecture naturelle

**Services concernés :**
- Notification Service
- WebSocket Service (temps réel)
- File Upload Service

### 2. Frameworks Web

#### FastAPI (Python)
```python
# Exemple configuration FastAPI optimisée
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="SuperSmartMatch API",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configuration pour performance
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auto-validation et sérialisation Pydantic
class MatchingRequest(BaseModel):
    cv_data: dict
    job_data: List[dict]
    algorithm: str = "supersmartmatch"
    limit: int = 10

@app.post("/api/v2/match")
async def match_candidates(request: MatchingRequest):
    # Traitement asynchrone optimisé
    return await matching_service.process(request)
```

#### Gin (Go)
```go
// Configuration Gin optimisée
func setupRouter() *gin.Engine {
    gin.SetMode(gin.ReleaseMode)
    r := gin.New()
    
    // Middleware optimisé
    r.Use(gin.Logger())
    r.Use(gin.Recovery())
    r.Use(cors.Default())
    
    // Health checks
    r.GET("/health", healthCheck)
    
    // API versioning
    v2 := r.Group("/api/v2")
    {
        v2.POST("/geocode", geocodeHandler)
        v2.POST("/distance", distanceHandler)
    }
    
    return r
}
```

### 3. Base de Données

#### PostgreSQL 14+ (Primary Database)
**Justification :**
- ACID compliance pour cohérence
- Performance excellente avec optimisations
- JSON/JSONB pour flexibilité
- Partitioning natif
- Extensions avancées (PostGIS pour géolocalisation)

**Configuration Optimisée :**
```sql
-- Partitioning par région pour scalabilité
CREATE TABLE matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL,
    job_id UUID NOT NULL,
    region VARCHAR(50) NOT NULL,
    matching_score DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
) PARTITION BY HASH (region);

-- Index optimisés
CREATE INDEX CONCURRENTLY idx_matches_score 
ON matches (matching_score DESC, created_at DESC);

CREATE INDEX CONCURRENTLY idx_matches_candidate 
ON matches (candidate_id, job_id);
```

#### Redis Cluster (Cache & Queues)
**Justification :**
- Performance exceptionnelle (sub-millisecond)
- Structures de données avancées
- Pub/Sub pour events temps réel
- Persistence configurable
- Clustering natif pour HA

**Configuration Cluster :**
```yaml
Redis Cluster Configuration:
  nodes: 6 (3 master, 3 replica)
  memory_per_node: 8GB
  persistence: RDB + AOF
  eviction_policy: allkeys-lru
  maxmemory_samples: 10
```

#### Elasticsearch (Search & Analytics)
**Justification :**
- Full-text search optimisé
- Aggregations complexes pour analytics
- Scalabilité horizontale
- Intégration logging (ELK)

### 4. Orchestration et Déploiement

#### Kubernetes
**Justification :**
- Standard industrie pour microservices
- Auto-scaling horizontal/vertical
- Self-healing capabilities
- Écosystème mature
- Multi-cloud portability

**Configuration Cluster :**
```yaml
Cluster Specifications:
  Node Pool 1 (System):
    node_count: 3
    machine_type: e2-standard-4
    preemptible: false
    
  Node Pool 2 (Applications):
    node_count: 6-20 (auto-scaling)
    machine_type: e2-standard-8
    preemptible: true (cost optimization)
    
  Storage:
    type: SSD Persistent Disks
    class: premium-rwo
```

#### Istio Service Mesh
**Justification :**
- mTLS automatique entre services
- Traffic management avancé
- Observability intégrée
- Circuit breaking natif
- Canary deployments

### 5. Monitoring et Observability

#### Prometheus + Grafana
**Métriques de Performance :**
```yaml
KPIs Surveillés:
  - Request latency (P50, P95, P99)
  - Throughput (RPS)
  - Error rate (4xx, 5xx)
  - Memory/CPU utilization
  - Database connection pool
  - Cache hit ratio
  - ML model accuracy
```

#### Jaeger (Distributed Tracing)
**Configuration :**
```yaml
Tracing Configuration:
  sampling_strategy: probabilistic
  sampling_rate: 0.1  # 10% en production
  max_traces_per_second: 100
  retention_period: 7d
```

### 6. CI/CD Pipeline

#### GitHub Actions + ArgoCD
**Pipeline Automatisé :**
```yaml
# .github/workflows/deploy.yml
name: Deploy SuperSmartMatch V2

on:
  push:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Tests
        run: |
          pytest tests/ --cov=./ --cov-report=xml
          
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker Images
        run: |
          docker build -t supersmartmatch/scoring-engine:${{ github.sha }} .
          docker push supersmartmatch/scoring-engine:${{ github.sha }}
          
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          argocd app sync supersmartmatch-v2 --force
```

## Alternatives Considérées

### Bases de Données
- **MongoDB** ❌ : Cohérence éventuelle non acceptable
- **CockroachDB** ⚖️ : Complexité vs. bénéfices
- **TimescaleDB** ⚖️ : Spécialisé time-series uniquement

### Langages
- **Java/Spring Boot** ❌ : Overhead mémoire
- **Rust** ❌ : Courbe d'apprentissage équipe
- **.NET Core** ❌ : Écosystème ML limité

### Orchestration
- **Docker Swarm** ❌ : Fonctionnalités limitées
- **AWS ECS** ❌ : Vendor lock-in
- **Nomad** ❌ : Écosystème moins mature

## Benchmarks de Performance

### Tests de Charge
```yaml
Load Testing Results:
  Scoring Engine (Python/FastAPI):
    - 1000 RPS: P95 latency 180ms ✅
    - 2000 RPS: P95 latency 350ms ⚠️
    - 3000 RPS: P95 latency 800ms ❌
    
  Geolocation Service (Go/Gin):
    - 5000 RPS: P95 latency 50ms ✅
    - 10000 RPS: P95 latency 120ms ✅
    - 15000 RPS: P95 latency 300ms ⚠️
```

### Optimisations Identifiées
```python
# Connection pooling optimisé
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Cache Redis avec pipeline
import redis.asyncio as redis

class OptimizedRedisClient:
    async def batch_get(self, keys: List[str]):
        pipe = self.redis.pipeline()
        for key in keys:
            pipe.get(key)
        return await pipe.execute()
```

## Migration Path

### Phase 1: Infrastructure (Semaines 1-2)
- Setup Kubernetes cluster
- Deploy monitoring stack
- Configure CI/CD pipelines

### Phase 2: Core Services (Semaines 3-6)
- Migrate API Gateway
- Deploy new database with migration scripts
- Implement core business services

### Phase 3: Advanced Features (Semaines 7-10)
- ML services deployment
- Performance optimization
- Load testing validation

## Coûts d'Infrastructure

### Estimation Mensuelle
```yaml
AWS/GCP Costs (Production):
  Kubernetes Cluster: $2,500
  Databases (PostgreSQL + Redis): $1,800
  Load Balancers: $200
  Monitoring Stack: $300
  Storage (MinIO): $400
  
Total Estimated: $5,200/month
Vs V1 Current: $3,800/month
Increment: +37% (justified by performance gains)
```

## Métriques de Validation

Cette décision sera validée par :
- **Performance benchmarks** : Atteinte des SLAs définis
- **Developer Experience** : Productivité équipe de développement
- **Operational Metrics** : MTTR, deployment frequency
- **Business Metrics** : User satisfaction, conversion rates

---
**Auteur**: Architecture Team  
**Reviewers**: CTO, Lead Developers, DevOps Team  
**Approbation finale**: CTO - 2025-05-27