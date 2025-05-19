# Guide de configuration de l'environnement de développement

## Vue d'ensemble

Ce guide vous accompagne dans la configuration d'un environnement de développement complet pour le projet Nexten, incluant :

- Configuration des outils de développement
- Setup du monitoring et observabilité
- Configuration des tests automatisés
- Pipelines CI/CD

## Prérequis

### Outils requis

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Python** (version 3.11+)
- **Poetry** (gestionnaire de dépendances Python)
- **Git** (version 2.30+)

### Comptes et accès

- Compte GitHub avec accès au repository
- Clé API OpenAI (pour les services ML)
- Accès aux services de monitoring (optionnel)

## Installation rapide

### 1. Cloner le repository

```bash
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-
```

### 2. Exécuter le script de setup

```bash
chmod +x scripts/dev-setup.sh
./scripts/dev-setup.sh
```

Ce script configure automatiquement :
- Poetry et l'environnement virtuel
- Pre-commit hooks
- Répertoires nécessaires
- Configuration de base

### 3. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env avec vos clés API
```

### 4. Démarrer l'environnement

```bash
make dev-up
```

## Structure du projet

```
Commitment-/
├── .github/workflows/           # Pipelines CI/CD
├── backend/                     # API principale
├── cv-parser-service/          # Service de parsing CV
├── job-parser-service/         # Service de parsing emploi
├── matching-service/           # Service de matching
├── frontend/                   # Interface utilisateur
├── monitoring/                 # Configuration monitoring
│   ├── prometheus/            # Configuration Prometheus
│   ├── grafana/              # Dashboards Grafana
│   └── logstash/             # Pipeline de logs
├── shared/                    # Composants partagés
│   ├── middleware/           # Middleware FastAPI
│   └── metrics/              # Métriques Prometheus
├── tests/                     # Tests
│   ├── unit/                 # Tests unitaires
│   ├── integration/          # Tests d'intégration
│   └── performance/          # Tests de performance
├── scripts/                   # Scripts utilitaires
└── docs/                      # Documentation
```

## Configuration des services

### Services principaux

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | Interface utilisateur React |
| API Backend | 5050 | API principale FastAPI |
| CV Parser | 5051 | Service de parsing CV |
| Job Parser | 5055 | Service de parsing emploi |
| Matching API | 5052 | Service de matching |
| Data Adapter | 5053 | Adaptateur de données |

### Services d'infrastructure

| Service | Port | Description |
|---------|------|-------------|
| PostgreSQL | 5432 | Base de données principale |
| Redis | 6379 | Cache et files d'attente |
| MinIO | 9000/9001 | Stockage d'objets |

### Services de monitoring

| Service | Port | Description |
|---------|------|-------------|
| Prometheus | 9090 | Collecte de métriques |
| Grafana | 3001 | Visualisation (admin/admin) |
| Elasticsearch | 9200 | Stockage de logs |
| Kibana | 5601 | Interface de logs |
| Jaeger | 16686 | Tracing distribué |
| AlertManager | 9093 | Gestion d'alertes |

### Services de développement

| Service | Port | Description |
|---------|------|-------------|
| JupyterLab | 8888 | Développement ML (token: development) |
| MLflow | 5005 | Tracking ML |
| Locust | 8089 | Tests de performance |

## Commandes utiles

### Gestion de l'environnement

```bash
# Démarrer tous les services
make dev-up

# Arrêter tous les services
make dev-down

# Reconstruire les images
make dev-build

# Voir les logs
make logs

# Ouvrir les interfaces de monitoring
make monitoring
```

### Tests

```bash
# Tous les tests
make test

# Tests d'intégration
make test-integration

# Tests de performance
make performance-test
```

### Qualité de code

```bash
# Vérifier la qualité du code
make lint

# Formater le code
make format

# Scan de sécurité
make security
```

### Base de données

```bash
# Exécuter les migrations
make migration

# Accéder à la base de données
docker-compose exec postgres psql -U postgres -d nexten
```

## Développement avec les métriques

### Ajout de métriques dans un service

```python
from shared.metrics import setup_prometheus_middleware, track_ml_operation
from fastapi import FastAPI

app = FastAPI()

# Configuration du middleware
setup_prometheus_middleware(app, "mon-service")

# Tracking d'opération ML
@track_ml_operation("mon-service", "parsing", "gpt-4")
async def parse_document(text: str):
    # Votre logique ici
    pass
```

### Logging structuré

```python
from shared.logging_config import get_logger

logger = get_logger("mon-service")

# Log avec contexte
logger.info(
    "Document processed",
    document_id=doc_id,
    processing_time=duration,
    user_id=user_id
)
```

## Monitoring et alertes

### Dashboards Grafana

1. **API Performance** : Métriques de performance des APIs
2. **ML Operations** : Suivi des opérations ML/AI
3. **System Health** : État des services et ressources

### Alertes configurées

- Taux d'erreur > 5%
- Temps de réponse > 1s (95e percentile)
- Usage CPU > 80%
- Usage mémoire > 85%
- Services indisponibles

### Accès aux logs

- **Kibana** : http://localhost:5601
- **Logs structurés** : Format JSON avec correlation IDs
- **Filtres prédéfinis** : Par service, niveau, utilisateur

## Debugging

### Problèmes courants

#### Services qui ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs service-name

# Vérifier l'état des conteneurs
docker-compose ps

# Redémarrer un service spécifique
docker-compose restart service-name
```

#### Problèmes de permissions

```bash
# Réinitialiser les permissions
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh
```

#### Problèmes de mémoire

```bash
# Nettoyer les images Docker
docker system prune -af

# Augmenter les limites Docker Desktop
# Ajuster dans les préférences Docker
```

### Profiling des performances

```python
# Profiling Python avec py-spy
py-spy record -o profile.svg -- python main.py

# Profiling mémoire
mprof run main.py
mprof plot
```

## Contribution

### Workflow de développement

1. Créer une branche feature
2. Développer avec tests
3. Vérifier la qualité du code
4. Créer une Pull Request
5. Review et merge

### Pre-commit hooks

Les hooks suivants s'exécutent automatiquement :

- **Black** : Formatage du code
- **Flake8** : Linting
- **isort** : Tri des imports
- **Bandit** : Scan de sécurité
- **YAML/JSON** : Validation des fichiers

### Tests obligatoires

- Tests unitaires (couverture > 80%)
- Tests d'intégration
- Tests de sécurité
- Validation des métriques

## Déploiement

### Environnements

1. **Development** : Local avec docker-compose
2. **Staging** : Auto-déployé sur push main
3. **Production** : Déployé sur tags

### Pipeline CI/CD

1. **Tests** : Unitaires, intégration, sécurité
2. **Build** : Images Docker multi-architecture
3. **Deploy Staging** : Déploiement automatique
4. **Production** : Déploiement canary avec validation

## Support

### Ressources

- [Documentation API](../api-docs/)
- [Guide architecture](./architecture.md)
- [Runbooks](./runbooks/)

### Contact

- **Issues** : GitHub Issues
- **Discussions** : GitHub Discussions
- **Urgences** : Slack #alerts

---

**Note** : Ce document est maintenu automatiquement. Pour des modifications, éditez le fichier source et créez une PR.