# Guide de monitoring et observabilité

## Vue d'ensemble

Ce guide détaille le système de monitoring et d'observabilité mis en place pour Nexten, incluant les métriques, logs, traces et alertes.

## Architecture de monitoring

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Applications  │    │   Prometheus    │    │    Grafana      │
│                 │───▶│                 │───▶│                 │
│ - CV Parser     │    │ - Collecte      │    │ - Visualisation │
│ - Job Parser    │    │ - Stockage      │    │ - Dashboards    │
│ - Matching API  │    │ - Alertes       │    │ - Alertes       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Logstash      │    │ AlertManager    │    │     Jaeger      │
│                 │    │                 │    │                 │
│ - Traitement    │    │ - Routage       │    │ - Tracing       │
│ - Enrichissement│    │ - Notifications │    │ - Debugging     │
│ - Indexation    │    │ - Déduplication │    │ - Performance   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐                            ┌─────────────────┐
│ Elasticsearch   │                            │  Applications   │
│                 │                            │                 │
│ - Stockage logs │                            │ - Instrumentation|
│ - Recherche     │                            │ - Spans         │
│ - Agrégation    │                            │ - Contexte      │
└─────────────────┘                            └─────────────────┘
         │
         ▼
┌─────────────────┐
│     Kibana      │
│                 │
│ - Interface logs│
│ - Recherche     │
│ - Visualisation │
└─────────────────┘
```

## Métriques Prometheus

### Métriques d'application

#### HTTP/API

```python
# Nombre total de requêtes
http_requests_total{method, endpoint, status_code, service}

# Durée des requêtes
http_request_duration_seconds{method, endpoint, service}

# Nombre de requêtes actives
http_requests_active{service}

# Taille des requêtes/réponses
http_request_size_bytes{method, endpoint, service}
http_response_size_bytes{method, endpoint, status_code, service}
```

#### Machine Learning

```python
# Traitement ML
ml_processing_duration_seconds{service, operation, model_type}
ml_requests_total{service, operation, status}
ml_errors_total{service, operation, error_type}

# API OpenAI
openai_api_calls_total{service, model, status}
openai_tokens_total{service, model, type}  # type: prompt|completion
```

#### Base de données

```python
# Connexions
db_connections_active{service, database}

# Requêtes
db_query_duration_seconds{service, operation, table}

# Redis
redis_operations_total{service, operation, status}
redis_operation_duration_seconds{service, operation}
```

#### Système

```python
# CPU et mémoire
system_cpu_usage_percent{service}
system_memory_usage_bytes{service, type}  # type: rss|vms

# Standard Node Exporter
node_cpu_seconds_total
node_memory_MemTotal_bytes
node_filesystem_size_bytes
```

### Configuration Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Services applicatifs
  - job_name: 'cv-parser'
    static_configs:
      - targets: ['cv-parser:5000']
    metrics_path: /metrics
    scrape_interval: 5s

  # Monitoring système
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # Bases de données
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

## Dashboards Grafana

### Dashboard API Performance

**Panels principaux :**

1. **Request Rate** (req/s)
   - Query: `sum(rate(http_requests_total[5m]))`
   - Visualisation: Stat

2. **Error Rate** (%)
   - Query: `(sum(rate(http_requests_total{status_code!~"2.."}[5m])) / sum(rate(http_requests_total[5m]))) * 100`
   - Seuils: Vert <1%, Jaune <5%, Rouge ≥5%

3. **Response Time** (95th percentile)
   - Query: `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`
   - Seuils: Vert <0.5s, Jaune <1s, Rouge ≥1s

4. **Active Requests**
   - Query: `sum(http_requests_active)`
   - Visualisation: Gauge

### Dashboard ML Operations

**Panels principaux :**

1. **ML Success Rate**
   - Query: `(sum(rate(ml_requests_total{status="success"}[5m])) / sum(rate(ml_requests_total[5m]))) * 100`

2. **Processing Time Distribution**
   - Queries: 50th, 95th, 99th percentiles
   - Visualisation: Time series

3. **OpenAI API Usage**
   - Calls per second: `sum(rate(openai_api_calls_total[5m]))`
   - Tokens per hour: `sum(rate(openai_tokens_total[1h]))`

4. **Error Distribution**
   - Query: `sum(rate(ml_errors_total[5m])) by (error_type)`
   - Visualisation: Pie chart

### Dashboard System Health

**Panels principaux :**

1. **CPU Usage**
   - Query: `100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)`

2. **Memory Usage**
   - Query: `(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100`

3. **Disk Usage**
   - Query: `(1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100`

4. **Network I/O**
   - Queries: `rate(node_network_receive_bytes_total[5m])`, `rate(node_network_transmit_bytes_total[5m])`

## Logging structuré

### Format des logs

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "INFO",
  "logger": "cv-parser",
  "service": "cv-parser",
  "message": "CV parsed successfully",
  "correlation_id": "req-12345-abcde",
  "user_id": "user-456",
  "document_id": "doc-789",
  "processing_time_ms": 1250,
  "model_used": "gpt-4",
  "tokens_used": 150
}
```

### Configuration Logstash

```ruby
# Pipeline de traitement
input {
  beats {
    port => 5044
  }
}

filter {
  # Parse JSON logs
  if [message] =~ /^\{.*\}$/ {
    json {
      source => "message"
    }
  }
  
  # Anonymise les données sensibles
  if [message] =~ /api_key|password|token/ {
    mutate {
      gsub => [
        "message", "(['\"])(api_key|password|token)(['\"]:\s*['\"])[^'\"]*(['\"])", "\1\2\3***\4"
      ]
    }
  }
  
  # Géolocalisation
  if [client_ip] {
    geoip {
      source => "client_ip"
      target => "geoip"
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "nexten-logs-%{+YYYY.MM.dd}"
  }
}
```

### Recherche dans Kibana

**Requêtes utiles :**

```
# Erreurs par service
level:ERROR AND service:cv-parser

# Requêtes lentes
processing_time_ms:>5000

# Erreurs OpenAI
service:* AND error_type:"OpenAIError"

# Utilisateur spécifique
user_id:"user-123" AND timestamp:[now-1h TO now]

# Correlation tracking
correlation_id:"req-12345-abcde"
```

## Tracing distribué avec Jaeger

### Instrumentation

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configuration du tracing
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Export vers Jaeger
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)
span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Utilisation
@app.post("/parse-cv")
async def parse_cv(file: UploadFile):
    with tracer.start_as_current_span("parse_cv") as span:
        span.set_attributes({
            "file.name": file.filename,
            "file.size": len(await file.read())
        })
        
        # Traitement...
        result = await process_cv(file)
        
        span.set_attributes({
            "result.status": "success",
            "result.entities_count": len(result.entities)
        })
        
        return result
```

### Analyse des traces

**Cas d'usage :**

1. **Debugging de latence** : Identifier les goulots d'étranglement
2. **Analyse de dépendances** : Comprendre les interactions entre services
3. **Détection d'erreurs** : Tracer la propagation des erreurs
4. **Optimisation** : Identifier les appels redondants

## Alertes et notifications

### Règles d'alertes Prometheus

```yaml
# alerts.yml
groups:
  - name: api_alerts
    rules:
      # Taux d'erreur élevé
      - alert: HighErrorRate
        expr: |
          (
            rate(http_requests_total{status_code!~"2.."}[5m]) /
            rate(http_requests_total[5m])
          ) * 100 > 5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Taux d'erreur élevé détecté"
          description: "Taux d'erreur: {{ $value }}% pour {{ $labels.service }}"
      
      # Temps de réponse élevé
      - alert: HighResponseTime
        expr: |
          histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Temps de réponse élevé"
          description: "95e percentile: {{ $value }}s pour {{ $labels.service }}"
```

### Configuration AlertManager

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.company.com:587'
  smtp_from: 'alerts@nexten.com'

route:
  group_by: ['alertname', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
      repeat_interval: 5m

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://slack-webhook/alerts'
  
  - name: 'critical-alerts'
    email_configs:
      - to: 'oncall@nexten.com'
        subject: '🚨 [CRITICAL] {{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
    
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/...'
        channel: '#alerts'
        title: '🚨 Critical Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

## Surveillance proactive

### SLIs/SLOs

**Service Level Indicators :**

1. **Disponibilité** : % de requêtes réussies (non 5xx)
2. **Latence** : 95e percentile des temps de réponse
3. **Qualité** : Taux de parsing réussi
4. **Performance ML** : Temps de traitement moyen

**Service Level Objectives :**

- Disponibilité ≥ 99.9%
- Latence P95 ≤ 500ms
- Taux d'erreur ≤ 0.1%
- Temps de parsing ≤ 10s (P95)

### Surveillance automatisée

```python
# scripts/health_check.py
import requests
import prometheus_client

def check_service_health():
    services = [
        ('cv-parser', 'http://cv-parser:5000/health'),
        ('job-parser', 'http://job-parser:5000/health'),
        ('matching-api', 'http://matching-api:5000/health')
    ]
    
    for service_name, url in services:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                service_up.labels(service=service_name).set(1)
            else:
                service_up.labels(service=service_name).set(0)
        except Exception:
            service_up.labels(service=service_name).set(0)

service_up = prometheus_client.Gauge(
    'service_health_status',
    'Service health status',
    ['service']
)
```

## Dépannage

### Prometheus

```bash
# Vérifier les targets
curl http://localhost:9090/api/v1/targets

# Tester une query
curl 'http://localhost:9090/api/v1/query?query=up'

# Recharger la configuration
curl -X POST http://localhost:9090/-/reload
```

### Grafana

```bash
# Réinitialiser le mot de passe admin
docker-compose exec grafana grafana-cli admin reset-admin-password newpassword

# Import de dashboard
curl -X POST \
  http://admin:admin@localhost:3001/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @dashboard.json
```

### Elasticsearch/Kibana

```bash
# Status du cluster
curl http://localhost:9200/_cluster/health

# Lister les indices
curl http://localhost:9200/_cat/indices

# Créer un index pattern
curl -X POST "localhost:5601/api/saved_objects/index-pattern/nexten-logs-*" \
  -H 'Content-Type: application/json' \
  -H 'kbn-xsrf: true' \
  -d '{
    "attributes": {
      "title": "nexten-logs-*",
      "timeFieldName": "@timestamp"
    }
  }'
```

### Jaeger

```bash
# Vérifier les traces
curl "http://localhost:16686/api/traces?service=cv-parser&limit=10"

# Status du collector
curl http://localhost:14269/metrics
```

## Bonnes pratiques

### Métriques

1. **Nommage cohérent** : `service_operation_unit_total`
2. **Labels utiles** : service, method, status_code
3. **Cardinalité limitée** : Éviter les labels dynamiques
4. **Instrumentation progressive** : Commencer simple, enrichir

### Logs

1. **Format structuré** : JSON avec schema cohérent
2. **Niveaux appropriés** : DEBUG/INFO/WARN/ERROR
3. **Contexte riche** : correlation_id, user_id, etc.
4. **Pas de données sensibles** : Anonymisation automatique

### Alertes

1. **Actionables** : Chaque alerte doit avoir une action
2. **Priorités claires** : Critical/Warning/Info
3. **Runbooks** : Documentation des actions
4. **Éviter la fatigue** : Pas trop d'alertes

### Performances

1. **Rétention adaptée** : Ajuster selon l'usage
2. **Agrégations** : Pré-calculer les métriques fréquentes
3. **Sampling** : Pour les traces à fort volume
4. **Monitoring du monitoring** : Surveiller les outils eux-mêmes

---

**Ressources**

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Elasticsearch Guide](https://www.elastic.co/guide/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)