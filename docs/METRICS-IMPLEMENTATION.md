# 📊 Métriques de Performance - Session 2 Complétée 100%

Ce document explique l'implémentation complète des métriques de performance qui finalise la Session 2 de votre environnement de développement ML/AI.

## 🎯 Objectif

Capturer et visualiser les métriques de performance applicatives pour compléter le monitoring déjà en place avec Prometheus/Grafana.

## 📈 Métriques Implementées

### Métriques API (FastAPI)
- `fastapi_requests_total` - Nombre total de requêtes par service
- `fastapi_request_duration_seconds` - Durée des requêtes API
- `fastapi_requests_in_progress` - Requêtes en cours de traitement

### Métriques ML/AI Business
- `ml_inference_duration_seconds` - Temps d'inférence des modèles ML
- `ml_inference_total` - Nombre d'inférences (succès/échec)
- `parsing_accuracy_score` - Précision du parsing des documents
- `matching_score_distribution` - Distribution des scores de matching
- `file_processing_size_bytes` - Taille des fichiers traités

## 🛠️ Installation

### 1. Automatique
```bash
# Rendre le script exécutable
chmod +x scripts/install-performance-metrics.sh

# Exécuter l'installation
./scripts/install-performance-metrics.sh
```

### 2. Manuelle
```bash
# Installer les dépendances
pip install prometheus-client==0.18.0 structlog==23.1.0

# Redémarrer les services avec monitoring
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d --build
```

## 🔧 Intégration dans vos Services

### Étape 1: Ajouter le middleware
```python
from shared.middleware.metrics import PrometheusMiddleware, metrics_endpoint

app = FastAPI(title="Mon Service")

# Ajouter le middleware
app.add_middleware(PrometheusMiddleware, service_name="mon-service")

# Endpoint pour Prometheus
@app.get("/metrics")
async def get_metrics():
    return await metrics_endpoint()
```

### Étape 2: Tracker les métriques business
```python
from shared.middleware.metrics import (
    track_ml_inference,
    track_parsing_accuracy,
    track_file_processing
)

# Dans vos endpoints
@app.post("/parse")
async def parse_document(file: UploadFile):
    start_time = time.time()
    
    # Track file size
    file_content = await file.read()
    track_file_processing(file.filename.split('.')[-1], "mon-service", len(file_content))
    
    # ML Processing
    try:
        result = await ml_process(file_content)
        
        # Track success
        duration = time.time() - start_time
        track_ml_inference("gpt-4", "mon-service", duration, success=True)
        
        # Track accuracy if available
        if hasattr(result, 'confidence'):
            track_parsing_accuracy("document", "pdf", result.confidence)
            
    except Exception as e:
        # Track failure
        duration = time.time() - start_time
        track_ml_inference("gpt-4", "mon-service", duration, success=False)
        raise
```

## 🚀 Services à Mettre à Jour

### Services Prioritaires
1. **cv-parser-service** (port 5051)
2. **job-parser-service** (port 5055)  
3. **matching-service** (port 5052)
4. **api** (port 5050)

### Checklist d'intégration
- [ ] Ajouter `PrometheusMiddleware` 
- [ ] Créer endpoint `/metrics`
- [ ] Utiliser les fonctions `track_*` pour les métriques business
- [ ] Tester l'endpoint `/metrics`
- [ ] Vérifier dans Prometheus (targets)

## 📊 Dashboards Grafana

### Dashboard Principal
**Nexten ML/AI Performance Dashboard** comprend :
- Taux de requêtes API
- Temps de réponse (95ème percentile)
- Durée des inférences ML
- Taux de succès des inférences
- Distribution des scores de précision
- Taux d'erreur par service

### Accès
- URL: http://localhost:3001
- Login: admin / admin123
- Dashboard: Rechercher "Nexten ML/AI Performance Dashboard"

## 🚨 Alertes Configurées

### Performance
- **HighAPIResponseTime**: Temps de réponse > 5s
- **SlowMLInference**: Inférence ML > 30s
- **HighErrorRate**: Taux d'erreur > 5%

### Qualité  
- **LowParsingAccuracy**: Précision médiane < 80%
- **HighMLFailureRate**: Échec ML > 10%

### Système
- **ServiceDown**: Service indisponible
- **HighMemoryUsage**: RAM > 90%
- **HighCPUUsage**: CPU > 80%

## 🔍 Vérification

### 1. Endpoints de métriques
```bash
# Vérifier que les métriques sont exposées
curl http://localhost:5051/metrics  # CV Parser
curl http://localhost:5055/metrics  # Job Parser  
curl http://localhost:5052/metrics  # Matching
curl http://localhost:5050/metrics  # API Gateway
```

### 2. Prometheus Targets
Vérifier dans Prometheus : http://localhost:9090/targets

### 3. Grafana Dashboards
Vérifier dans Grafana : http://localhost:3001

## 📁 Structure des Fichiers

```
├── shared/
│   ├── middleware/
│   │   └── metrics.py              # Middleware Prometheus
│   └── examples/
│       └── fastapi_metrics_example.py  # Exemple d'intégration
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml          # Config Prometheus mise à jour
│   │   └── rules/
│   │       └── alert_rules.yml     # Règles d'alertes
│   └── grafana/
│       └── dashboards/
│           └── ml-performance-dashboard.json  # Dashboard ML/AI
├── scripts/
│   └── install-performance-metrics.sh  # Script d'installation
└── requirements.txt                # Dépendances mises à jour
```

## 🎉 Résultat Final

**Session 2 : 100% complétée !**

✅ **Environnement de développement optimal**  
✅ **Stack technique définie** (Docker + FastAPI + ML)  
✅ **Monitoring complet** (Prometheus + Grafana + ELK)  
✅ **CI/CD configuré** (GitHub Actions)  
✅ **Outils ML/AI** (Jupyter + MLflow + Locust)  
✅ **Métriques de performance** (API + ML + Business)  

Votre environnement de développement ML/AI est maintenant **professionnel et production-ready** ! 🚀

## 🆘 Support

En cas de problème :
1. Vérifiez les logs Docker : `docker-compose logs [service]`
2. Vérifiez les targets Prometheus : http://localhost:9090/targets
3. Vérifiez les métriques : `curl http://localhost:[port]/metrics`
4. Consultez les dashboards Grafana pour diagnostics

## 📝 Notes de Développement

- Les métriques sont collectées automatiquement via le middleware
- Prometheus scrape toutes les 10-15 secondes
- Les alertes sont évaluées toutes les 15 secondes
- Les dashboards se rafraîchissent toutes les 30 secondes
- La rétention des métriques est de 30 jours par défaut
