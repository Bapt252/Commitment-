# Bibliothèque partagée pour les microservices Nexten

Ce dossier contient les modules partagés entre les différents microservices de la plateforme Nexten.

## Structure

```
shared/
├── auth/             # Authentification et autorisation partagées
├── db/               # Utilitaires pour la base de données
├── messaging/        # Communication inter-services
└── utils/            # Fonctions utilitaires communes
```

## Modules disponibles

### Module d'authentification (`auth/`)

- `jwt_auth.py` : Fonctions pour valider les tokens JWT entre services
- `permissions.py` : Vérification des permissions utilisateur

### Module base de données (`db/`)

- `postgres.py` : Utilitaires pour les connexions PostgreSQL
- `redis.py` : Fonctions pour le cache Redis

### Module de messaging (`messaging/`)

- `events.py` : Publication et consommation d'événements inter-services
- `schemas.py` : Schémas des messages échangés

### Utilitaires (`utils/`)

- `logging.py` : Configuration des logs
- `validation.py` : Validateurs communs
- `metrics.py` : Instrumentation pour Prometheus

## Utilisation

Pour utiliser ces modules partagés dans un microservice, ajoutez le chemin du dossier parent au `PYTHONPATH` ou installez-le comme package local :

```python
# Dans votre microservice
from shared.db.postgres import setup_db_session, session_scope
from shared.auth.jwt_auth import validate_service_token
```

Dans une configuration Docker :

```dockerfile
# Copier le dossier shared dans votre image
COPY shared /app/shared
```