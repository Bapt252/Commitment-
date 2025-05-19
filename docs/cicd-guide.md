# Guide CI/CD et déploiement

## Vue d'ensemble

Ce guide décrit les pipelines de CI/CD mis en place pour Nexten, incluant les tests automatisés, la construction d'images Docker, et les stratégies de déploiement.

## Architecture CI/CD

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Développeur   │    │   GitHub        │    │  CI Pipeline    │
│                 │─── │                 │───▶│                 │
│ - Code          │ ^  │ - Repository    │    │ - Tests         │
│ - Tests locaux  │ │  │ - Pull Request  │    │ - Build         │
│ - Pre-commit    │ │  │ - Branch main   │    │ - Security      │
└─────────────────┘ │  └─────────────────┘    └─────────────────┘
                    │           │                       │
                    │           ▼                       ▼
┌─────────────────┐ │  ┌─────────────────┐    ┌─────────────────┐
│   Code Review   │ │  │   Container     │    │  CD Pipeline    │
│                 │ │  │   Registry      │    │                 │
│ - Quality Gate  │ │  │                 │───▶│ - Deploy Staging│
│ - Approval      │─┘  │ - Multi-arch    │    │ - Integration   │
│ - Merge         │    │ - Security scan │    │ - Deploy Prod   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Monitoring    │    │   Kubernetes    │    │   Rollback      │
│                 │    │                 │    │                 │
│ - Health checks │◀───│ - Staging       │    │ - Automatic     │
│ - Metrics       │    │ - Production    │    │ - Manual        │
│ - Alerts        │    │ - Canary deploy │    │ - Health-based  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Pipeline de CI (Continuous Integration)

### Déclenchement

- **Push** sur branches : `main`, `develop`, `feature/*`
- **Pull Request** vers `main` ou `develop`
- **Schedule** : Tests nocturnes

### Étapes du pipeline

#### 1. Tests et qualité de code

```yaml
# .github/workflows/ci.yml
jobs:
  test-and-quality:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Poetry
        uses: snok/install-poetry@v1
      
      - name: Install dependencies
        run: poetry install
      
      - name: Code formatting (Black)
        run: poetry run black --check .
      
      - name: Linting (Flake8)
        run: poetry run flake8 .
      
      - name: Security check (Bandit)
        run: poetry run bandit -r .
      
      - name: Unit tests
        run: poetry run pytest tests/unit/ --cov=.
      
      - name: Integration tests
        run: poetry run pytest tests/integration/
```

#### 2. Construction d'images Docker

```yaml
build-images:
  needs: test-and-quality
  strategy:
    matrix:
      service: [cv-parser-service, job-parser-service, matching-service]
  steps:
    - name: Setup Docker Buildx
      uses: docker/setup-buildx-action@v3
    
    - name: Login to GHCR
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Build and push
      uses: docker/build-push-action@v5
      with:
        context: ./${{ matrix.service }}
        platforms: linux/amd64,linux/arm64
        push: true
        tags: ghcr.io/${{ github.repository }}/${{ matrix.service }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

#### 3. Tests de sécurité

```yaml
security-scan:
  steps:
    - name: Trivy vulnerability scan
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload to GitHub Security
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
    
    - name: Secret scanning
      uses: GitGuardian/ggshield-action@v1
      env:
        GITGUARDIAN_API_KEY: ${{ secrets.GITGUARDIAN_API_KEY }}
```

### Métriques de qualité

- **Couverture de tests** : > 80%
- **Complexité cyclomatique** : < 10
- **Duplications** : < 3%
- **Vulnérabilités** : 0 critique/élevée
- **Dettes techniques** : < 5%

## Pipeline de CD (Continuous Deployment)

### Stratégie de déploiement

#### Environnements

1. **Development** : Local avec Docker Compose
2. **Staging** : Auto-déployé sur push `main`
3. **Production** : Déployé sur tags `v*`

#### Déploiement Staging

```yaml
deploy-staging:
  if: github.ref == 'refs/heads/main'
  environment: staging
  steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/cv-parser \
          cv-parser=ghcr.io/${{ github.repository }}/cv-parser-service:${{ github.sha }}
        kubectl rollout status deployment/cv-parser
    
    - name: Health checks
      run: |
        kubectl wait --for=condition=Ready pod -l app=cv-parser
        curl -f ${{ secrets.STAGING_API_URL }}/health
    
    - name: Integration tests
      run: |
        pytest tests/integration/ --base-url=${{ secrets.STAGING_API_URL }}
```

#### Déploiement Production (Canary)

```yaml
deploy-production:
  if: startsWith(github.ref, 'refs/tags/v')
  environment: production
  steps:
    # Déploiement canary (10% du trafic)
    - name: Deploy canary
      run: |
        kubectl apply -f k8s/canary-deployment.yaml
        kubectl set image deployment/cv-parser-canary \
          cv-parser=ghcr.io/${{ github.repository }}/cv-parser-service:${{ github.sha }}
    
    # Surveillance canary
    - name: Monitor canary
      run: |
        python scripts/check_canary_metrics.py \
          --prometheus-url=${{ secrets.PROMETHEUS_URL }} \
          --threshold-error-rate=1 \
          --threshold-latency=1000
    
    # Déploiement complet si canary OK
    - name: Full deployment
      run: |
        kubectl set image deployment/cv-parser \
          cv-parser=ghcr.io/${{ github.repository }}/cv-parser-service:${{ github.sha }}
        kubectl rollout status deployment/cv-parser
        kubectl delete deployment cv-parser-canary
```

### Rollback automatique

```yaml
rollback-production:
  if: failure() && needs.deploy-production.result == 'failure'
  needs: deploy-production
  steps:
    - name: Rollback deployment
      run: |
        kubectl rollout undo deployment/cv-parser
        kubectl rollout status deployment/cv-parser
    
    - name: Notify rollback
      uses: 8398a7/action-slack@v3
      with:
        status: 'warning'
        text: 'Production rollback executed'
        webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Tests automatisés

### Types de tests

#### Tests unitaires

```python
# tests/unit/test_cv_parser.py
import pytest
from cv_parser.service import CVParsingService

class TestCVParsingService:
    @pytest.fixture
    def parser_service(self):
        return CVParsingService()
    
    def test_extract_name(self, parser_service):
        text = "John Doe\nSoftware Engineer"
        result = parser_service.extract_name(text)
        assert result == "John Doe"
    
    def test_extract_skills(self, parser_service):
        text = "Skills: Python, Django, PostgreSQL"
        result = parser_service.extract_skills(text)
        assert "Python" in result
        assert "Django" in result
```

#### Tests d'intégration

```python
# tests/integration/test_full_workflow.py
import requests
import pytest

class TestFullWorkflow:
    @pytest.fixture
    def api_base_url(self):
        return os.getenv("API_BASE_URL", "http://localhost:5050")
    
    def test_cv_parsing_workflow(self, api_base_url):
        # 1. Upload CV
        files = {'file': ('cv.pdf', cv_content, 'application/pdf')}
        response = requests.post(f"{api_base_url}/api/parse-cv/", files=files)
        assert response.status_code == 200
        
        # 2. Get parsing result
        result = response.json()
        assert "parsed_data" in result
        
        # 3. Verify extracted data
        parsed_data = result["parsed_data"]
        assert "name" in parsed_data
        assert "skills" in parsed_data
```

#### Tests de performance

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def test_cv_parsing(self):
        files = {'file': ('test.txt', b'Test CV content')}
        self.client.post("/api/parse-cv/", files=files)
    
    @task(2)
    def test_job_parsing(self):
        payload = {"text": "Software Engineer position..."}
        self.client.post("/api/analyze", json=payload)
    
    @task(1)
    def test_matching(self):
        payload = {
            "cv_data": {"skills": ["Python"]},
            "job_data": {"required_skills": ["Python"]}
        }
        self.client.post("/api/match/simple", json=payload)
```

### Exécution des tests

```bash
# Tests unitaires avec couverture
pytest tests/unit/ --cov=. --cov-report=html

# Tests d'intégration
pytest tests/integration/ --base-url=http://staging.nexten.com

# Tests de performance
locust -f tests/performance/locustfile.py --host=http://staging.nexten.com --users=50 --spawn-rate=5 --run-time=5m
```

## Gestion des environnements

### Configuration par environnement

```yaml
# k8s/environments/staging/values.yaml
namespace: nexten-staging

services:
  cv-parser:
    replicas: 2
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: 1
        memory: 2Gi

# k8s/environments/production/values.yaml
namespace: nexten-production

services:
  cv-parser:
    replicas: 5
    resources:
      requests:
        cpu: 1
        memory: 2Gi
      limits:
        cpu: 2
        memory: 4Gi
    
    autoscaling:
      enabled: true
      minReplicas: 5
      maxReplicas: 20
      targetCPUUtilization: 70
```

### Variables d'environnement

```yaml
# Secrets Kubernetes
apiVersion: v1
kind: Secret
metadata:
  name: nexten-secrets
type: Opaque
data:
  OPENAI_API_KEY: <base64-encoded>
  DATABASE_URL: <base64-encoded>
  REDIS_URL: <base64-encoded>

---
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: nexten-config
data:
  LOG_LEVEL: "INFO"
  ENVIRONMENT: "production"
  PROMETHEUS_ENABLED: "true"
```

## Monitoring des déploiements

### Métriques de déploiement

```python
# Métriques personnalisées
DEPLOYMENT_COUNT = Counter(
    'deployments_total',
    'Total number of deployments',
    ['environment', 'service', 'status']
)

DEPLOYMENT_DURATION = Histogram(
    'deployment_duration_seconds',
    'Deployment duration',
    ['environment', 'service']
)

CANARY_SUCCESS_RATE = Gauge(
    'canary_success_rate',
    'Canary deployment success rate',
    ['service']
)
```

### Health checks post-déploiement

```python
# scripts/post_deploy_checks.py
def check_service_health(api_url):
    """Vérifier la santé du service après déploiement."""
    endpoints = [
        '/health',
        '/metrics',
        '/ready'
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{api_url}{endpoint}")
        if response.status_code != 200:
            return False
    return True

def check_metrics_baseline(prometheus_url, service):
    """Vérifier que les métriques sont dans les limites acceptables."""
    # Vérifier le taux d'erreur
    error_query = f'''
    rate(http_requests_total{{service="{service}",status_code!~"2.."}}[5m])
    '''
    result = prometheus.query(error_query)
    if result and float(result[0]['value'][1]) > 0.01:  # 1%
        return False
    
    # Vérifier le temps de réponse
    latency_query = f'''
    histogram_quantile(0.95, 
        rate(http_request_duration_seconds_bucket{{service="{service}"}}[5m])
    )
    '''
    result = prometheus.query(latency_query)
    if result and float(result[0]['value'][1]) > 1.0:  # 1s
        return False
    
    return True
```

### Alertes de déploiement

```yaml
# alertmanager rules
groups:
  - name: deployment_alerts
    rules:
      - alert: DeploymentFailed
        expr: increase(deployments_total{status="failed"}[5m]) > 0
        labels:
          severity: critical
        annotations:
          summary: "Deployment failed"
          description: "Deployment failed for {{ $labels.service }} in {{ $labels.environment }}"
      
      - alert: CanaryUnhealthy
        expr: canary_success_rate < 0.95
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Canary deployment unhealthy"
          description: "Canary success rate: {{ $value }} for {{ $labels.service }}"
```

## Gestion des secrets

### GitHub Secrets

**Secrets requis :**

- `OPENAI_API_KEY` : Clé API OpenAI
- `KUBE_CONFIG_STAGING` : Config Kubernetes staging
- `KUBE_CONFIG_PRODUCTION` : Config Kubernetes production
- `SLACK_WEBHOOK` : Webhook Slack pour notifications
- `SONAR_TOKEN` : Token SonarQube
- `GITGUARDIAN_API_KEY` : Clé GitGuardian

### Rotation des secrets

```bash
# Script de rotation automatique
#!/bin/bash
# scripts/rotate_secrets.sh

# Générer nouveau secret
NEW_SECRET=$(openssl rand -base64 32)

# Mettre à jour dans Kubernetes
kubectl create secret generic nexten-secrets \
  --from-literal=DATABASE_PASSWORD="$NEW_SECRET" \
  --dry-run=client -o yaml | kubectl apply -f -

# Redémarrer les pods pour prendre en compte le nouveau secret
kubectl rollout restart deployment/cv-parser
kubectl rollout restart deployment/job-parser
kubectl rollout restart deployment/matching-api

# Vérifier que tout fonctionne
sleep 30
kubectl get pods -l app=cv-parser
```

## Bonnes pratiques

### CI/CD

1. **Tests rapides** : < 10 minutes pour le pipeline principal
2. **Parallélisation** : Tests en parallèle quand possible
3. **Cache intelligent** : Réutiliser les dépendances
4. **Fail fast** : Arrêter dès la première erreur critique

### Sécurité

1. **Least privilege** : Permissions minimales nécessaires
2. **Secrets chiffrés** : Pas de secrets en plain text
3. **Scanning continu** : À chaque commit
4. **SBOM** : Software Bill of Materials pour traçabilité

### Déploiement

1. **Blue/Green ou Canary** : Toujours pour la production
2. **Health checks** : Avant de router le trafic
3. **Rollback automatique** : En cas de problème
4. **Monitoring actif** : Surveillance post-déploiement

### Documentation

1. **Runbooks** : Procédures de déploiement
2. **Changelog** : Suivi des changements
3. **Architecture Decision Records** : Justifications techniques
4. **Incident post-mortems** : Apprentissage des échecs

## Dépannage

### Échec de pipeline

```bash
# Reproduire localement
git checkout <commit-sha>
docker-compose -f docker-compose.ci.yml up --build

# Debug des tests
pytest tests/ -v --tb=short --capture=no

# Build local
docker build -t local-test:latest .
docker run --rm local-test:latest
```

### Problèmes de déploiement

```bash
# Status des deployments
kubectl get deployments
kubectl rollout status deployment/cv-parser

# Logs des pods
kubectl logs -l app=cv-parser --tail=100

# Describe pour debug
kubectl describe deployment cv-parser
kubectl describe pod <pod-name>

# Rollback manuel
kubectl rollout undo deployment/cv-parser
```

### Monitoring du CI/CD

```bash
# Métriques GitHub Actions
curl -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/owner/repo/actions/runs"

# Temps de build moyen
gh api repos/:owner/:repo/actions/runs \
  --jq '.workflow_runs[] | [.created_at, .updated_at, .conclusion]'
```

---

**Ressources**

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/)