# Service de Matching - Nexten

Ce service permet de calculer et gérer les scores de matching entre candidats et offres d'emploi, avec un système de files d'attente prioritaires basé sur Redis/RQ.

## Fonctionnalités

- **Calcul asynchrone de matching** entre candidats et offres d'emploi
- **Files d'attente prioritaires** :
  - `matching_high` : Pour les calculs urgents/prioritaires
  - `matching_standard` : Pour les calculs standard
  - `matching_bulk` : Pour les calculs en masse/batch
- **Chaînage de jobs** : Possibilité de déclencher un calcul de matching après un parsing de CV
- **Notifications webhooks** avec signature HMAC
- **Résilience** : Circuit breaker, retries, dead letter queue, etc.
- **Monitoring** via RQ Dashboard

## Architecture

Le service est composé de plusieurs composants :

- **API FastAPI** : Points d'entrée pour mettre en file d'attente les calculs et récupérer les résultats
- **Workers RQ** : Travailleurs qui exécutent les calculs de matching de manière asynchrone
- **Redis** : Stockage des jobs et des résultats temporaires
- **PostgreSQL** : Stockage persistant des résultats de matching
- **MinIO** : Stockage des résultats volumineux (optionnel)

## Structure du projet

```
matching-service/
├── app/
│   ├── main.py                    # Point d'entrée FastAPI
│   ├── api/
│   │   └── routes.py              # Routes API
│   ├── core/
│   │   ├── config.py              # Configuration
│   │   ├── database.py            # Utilitaires DB
│   │   ├── logging.py             # Configuration logging
│   │   ├── redis.py               # Utilitaires Redis
│   │   └── resilience.py          # Circuit breaker, retry
│   ├── models/
│   │   └── matching.py            # Modèles de données
│   ├── services/
│   │   ├── matching.py            # Service de matching
│   │   └── notification.py        # Service de notification
│   └── workers/
│       ├── tasks.py               # Tâches RQ
│       └── worker.py              # Configuration worker
├── Dockerfile
├── main.py                        # Point d'entrée FastAPI
├── requirements.txt
└── worker.py                      # Point d'entrée worker
```

## Utilisation via API

### Mettre en file d'attente un calcul de matching

```bash
curl -X POST "http://localhost:5052/api/v1/queue-matching" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 123,
    "job_id": 456,
    "webhook_url": "https://example.com/webhook"
  }' \
  -G -d "priority=matching_high"
```

### Mettre en file d'attente plusieurs calculs (bulk)

```bash
curl -X POST "http://localhost:5052/api/v1/queue-matching/bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 123,
    "job_ids": [101, 102, 103],
    "webhook_url": "https://example.com/webhook"
  }' \
  -G -d "priority=matching_bulk"
```

### Récupérer le résultat d'un calcul

```bash
curl -X GET "http://localhost:5052/api/v1/result/job-id-12345"
```

### Vérifier le statut d'un job

```bash
curl -X GET "http://localhost:5052/api/v1/status/job-id-12345"
```

## Utilisation via Python

```python
import redis
from rq import Queue

# Connexion directe à Redis
redis_conn = redis.Redis(host='redis', port=6379)

# Création d'une file d'attente
queue = Queue('matching_high', connection=redis_conn)

# Enchaînement simple
job = queue.enqueue(
    'app.workers.tasks.calculate_matching_score_task',
    args=(123, 456),  # candidate_id, job_id
    job_id="matching-123-456",
    meta={"webhook_url": "https://example.com/webhook"}
)

# Pour un job avec dépendance (après parsing)
job = queue.enqueue(
    'app.workers.tasks.calculate_matching_score_task',
    args=(123, 456),
    depends_on="parsing-job-id-123",
    job_id="matching-123-456-after-parsing",
    meta={"webhook_url": "https://example.com/webhook"}
)
```

## Chaînage avec le service de Parsing CV

Le service de matching peut être automatiquement déclenché après un parsing de CV :

```python
# Dans cv-parser-service
from app.utils.job_chaining import chain_cv_parsing_with_matching

# Après parsing d'un CV
result = chain_cv_parsing_with_matching(
    candidate_id=candidate_id,
    job_ids=[101, 102, 103],
    parsing_job_id=parsing_job.id,
    matching_api_url="http://matching-api:5000",
    webhook_url="https://example.com/webhook"
)
```

## Configuration

Le service utilise les variables d'environnement suivantes (avec valeurs par défaut) :

```
# Service
SERVICE_NAME=matching-service
DEBUG=false
LOG_LEVEL=INFO
PORT=5000

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_JOB_TIMEOUT=3600
REDIS_JOB_TTL=86400

# PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/nexten

# MinIO
MINIO_ENDPOINT=storage:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=matching-results

# Webhook
WEBHOOK_SECRET=your-secret-key
WEBHOOK_RETRY_COUNT=3

# Worker
MAX_RETRIES=3
WORKER_CONCURRENCY=4
```

## Déploiement

Le service peut être déployé avec Docker et Docker Compose :

```bash
docker-compose up -d
```

Cela démarre :
- L'API matching-api 
- Les workers avec différentes priorités
- Les services associés (Redis, PostgreSQL, MinIO, etc.)

## Monitoring

Le service peut être surveillé via :

- **RQ Dashboard** : Disponible sur http://localhost:9181
- **Redis Commander** : Disponible sur http://localhost:8081
- **Logs** : Générés au format JSON ou texte selon la configuration

## Développement

### Prérequis

- Python 3.9+
- Redis
- PostgreSQL

### Installation

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

### Démarrage local

```bash
# Terminal 1 : API FastAPI
python main.py

# Terminal 2 : Worker
python worker.py
```
