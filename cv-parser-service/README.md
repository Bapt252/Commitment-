# NexTen CV Parser Service

Service asynchrone de parsing de CV basé sur FastAPI, RQ (Redis Queue) et GPT-4o-mini.

## Fonctionnalités

- **Traitement asynchrone** des fichiers CV via Redis Queue
- **Files d'attente prioritaires** (premium, standard, batch)
- **Circuit breaker pattern** pour la protection contre les pannes d'API OpenAI
- **Retry avec backoff exponentiel** pour la gestion robuste des erreurs
- **Validation avancée des fichiers** (format, taille, signature, structure)
- **Stockage multi-tier** des résultats (Redis, PostgreSQL, MinIO)
- **Callback webhook** avec signature HMAC pour notification des services externes
- **Dead letter queue** pour traitement des jobs échoués
- **Monitoring** via RQ Dashboard et logs structurés au format JSON

## Architecture

```
   ┌──────────┐         ┌───────────┐         ┌──────────┐
   │ Frontend │ ──────► │   API     │ ──────► │ CV Parser│
   │          │ ◄────── │ Gateway   │ ◄────── │  Service │
   └──────────┘         └───────────┘         └────┬─────┘
                                                    │
                                                    ▼
                                              ┌──────────┐
                 ┌───────────────────────────►│  Redis   │
                 │                            │ (Queues) │
                 │                            └────┬─────┘
                 │                                 │
┌────────────────┴───┐                     ┌──────▼──────┐
│     RQ Workers      │◄────────────────────►    MinIO    │
│ (premium/standard)  │                     │ (Stockage)  │
└────────────────┬───┘                     └──────▲──────┘
                 │                                 │
                 │                            ┌────┴─────┐
                 └───────────────────────────►│PostgreSQL │
                                              │(Résultats)│
                                              └──────────┘
```

## Installation et démarrage

### Prérequis

- Docker et Docker Compose
- Clé API OpenAI (pour GPT-4o-mini)

### Démarrage avec Docker Compose

1. Définir la clé API OpenAI dans le fichier `.env` :

```
OPENAI_API_KEY=votre-cle-api-openai
```

2. Lancer les services avec Docker Compose :

```bash
docker-compose up -d
```

3. Vérifier l'état des services :

```bash
docker-compose ps
```

## API

### POST /api/queue

Place un CV en file d'attente pour traitement asynchrone.

**Paramètres**

- `file`: Fichier CV (PDF, DOCX, DOC, TXT, RTF)
- `priority`: Priorité de traitement (`premium`, `standard`, `batch`)
- `webhook_url`: URL de callback après traitement (optionnel)
- `webhook_secret`: Secret pour signature HMAC (optionnel)

**Réponse**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "priority": "premium",
  "estimated_wait": "30s",
  "webhook_configured": true
}
```

### GET /api/result/{job_id}

Récupère le résultat d'un job de parsing CV.

**Réponses possibles**

**Job en attente**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "position_in_queue": 3
}
```

**Job en cours**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "started_at": "2023-05-20T14:30:45Z"
}
```

**Job terminé**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "done",
  "result": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "file_name": "john_doe_cv.pdf",
    "processing_time": 3.45,
    "parsed_at": 1684596718.456,
    "data": {
      "personal_info": { ... },
      "skills": [ ... ],
      "experience": [ ... ],
      "education": [ ... ],
      "languages": [ ... ]
    }
  }
}
```

**Job échoué**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "error": "Document PDF corrompu ou protégé par mot de passe"
}
```

## Système de Callback Webhook

Le service peut notifier un service externe lorsqu'un parsing est terminé via un webhook HTTP.

### Format de requête

- **Méthode**: POST
- **En-têtes**:
  - `Content-Type: application/json`
  - `X-Signature: [signature-hmac]` (si webhook_secret fourni)

### Payload

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "done",
  "timestamp": 1684596718,
  "data": {
    // Résultat complet du parsing
  }
}
```

### Vérification de signature

Pour vérifier l'authenticité du webhook:

```python
import hmac
import hashlib
import json

def verify_webhook(request_body, signature, secret):
    expected = hmac.new(
        secret.encode(),
        request_body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

## Monitoring

### RQ Dashboard

Accès à l'interface RQ Dashboard: http://localhost:9181

### Redis Commander

Accès à l'interface Redis Commander: http://localhost:8081

## Configuration

Les options de configuration sont disponibles via variables d'environnement ou fichier `.env`. Voir `app/core/config.py` pour la liste complète des options.

Principales options:

| Variable | Description | Valeur par défaut |
|----------|-------------|-------------------|
| `OPENAI_API_KEY` | Clé API OpenAI | **(Requis)** |
| `OPENAI_MODEL` | Modèle OpenAI à utiliser | `gpt-4o-mini` |
| `REDIS_HOST` | Hôte Redis | `redis` |
| `REDIS_PORT` | Port Redis | `6379` |
| `MINIO_ENDPOINT` | Endpoint MinIO | `storage:9000` |
| `MINIO_ACCESS_KEY` | Clé d'accès MinIO | `minioadmin` |
| `MINIO_SECRET_KEY` | Clé secrète MinIO | `minioadmin` |
| `MINIO_BUCKET_NAME` | Nom du bucket MinIO | `cv-files` |
| `MAX_CONTENT_LENGTH` | Taille max de fichier (octets) | `10485760` (10MB) |
| `CIRCUIT_BREAKER_ENABLED` | Activer le circuit breaker | `true` |
| `MAX_RETRIES` | Nombre max de tentatives | `3` |

## Tests

### Tests manuels

Pour soumettre un CV de test:

```bash
curl -X POST http://localhost:5051/api/queue \
  -F "file=@/path/to/cv.pdf" \
  -F "priority=premium"
```

Vérifier le résultat:

```bash
curl http://localhost:5051/api/result/{job_id}
```

## Architecture technique

### Technologies

- **FastAPI**: API asynchrone haute performance
- **RQ (Redis Queue)**: File d'attente basée sur Redis
- **Redis**: Cache et broker de messages
- **OpenAI API**: Analyse du contenu avec GPT-4o-mini
- **MinIO**: Stockage objet compatible S3
- **PostgreSQL**: Stockage persistant des résultats
- **Docker**: Conteneurisation

### Patterns

- **Circuit Breaker**: Protection contre les pannes d'API
- **Retry Pattern**: Résilience aux erreurs temporaires
- **Dead Letter Queue**: Gestion des échecs
- **Multi-tier Storage**: Stockage adapté à la taille et durée de vie
- **Priority Queue**: Gestion des priorités de traitement

## Contribuer

Pour contribuer :

1. Fork le dépôt
2. Créer une branche (`git checkout -b feature/ma-fonctionnalite`)
3. Commit vos changements (`git commit -am 'Ajout de ma fonctionnalite'`)
4. Push la branche (`git push origin feature/ma-fonctionnalite`)
5. Créer une nouvelle Pull Request
