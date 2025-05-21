# Guide d'utilisation de l'analyse comportementale et profiling utilisateur

Ce guide explique comment utiliser le service d'analyse comportementale et profiling utilisateur implémenté dans la session 8.

## 1. Introduction

Le service d'analyse comportementale permet de :
- Créer des profils utilisateur enrichis basés sur leur comportement
- Regrouper les utilisateurs en segments (clusters) selon leurs caractéristiques
- Détecter des patterns comportementaux récurrents
- Calculer des scores de préférence dynamiques pour améliorer les recommandations

## 2. Démarrage du service

```bash
# Démarrer l'ensemble de l'application
docker-compose up -d

# OU démarrer uniquement le service d'analyse comportementale
./start-user-behavior.sh
```

Le service est accessible à l'adresse : http://localhost:5057

## 3. Endpoints API

### Vérification de santé

```bash
curl http://localhost:5057/health
```

### Gestion des profils utilisateur

**Créer/mettre à jour un profil**
```bash
curl -X POST http://localhost:5057/api/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "name": "John Doe",
    "email": "john@example.com",
    "interactions": [
      {
        "user_id": "user123",
        "action_type": "view_job",
        "timestamp": "2025-05-20T10:00:00Z",
        "item_id": "job-123",
        "job_category": "Development"
      }
    ]
  }'
```

**Récupérer tous les profils**
```bash
curl http://localhost:5057/api/profiles
```

**Récupérer un profil spécifique**
```bash
curl http://localhost:5057/api/profiles?user_id=user123
```

### Clustering utilisateur

**Créer des clusters**
```bash
curl -X POST http://localhost:5057/api/clusters \
  -H "Content-Type: application/json" \
  -d '{
    "n_clusters": 3
  }'
```

**Récupérer les clusters**
```bash
curl http://localhost:5057/api/clusters
```

### Détection de patterns comportementaux

**Détecter les patterns**
```bash
curl -X POST http://localhost:5057/api/patterns \
  -H "Content-Type: application/json" \
  -d '{
    "actions": [
      {
        "user_id": "user123",
        "action_type": "login",
        "timestamp": "2025-05-19T09:00:00Z"
      },
      {
        "user_id": "user123",
        "action_type": "view_job",
        "timestamp": "2025-05-19T09:05:00Z"
      },
      {
        "user_id": "user123",
        "action_type": "login",
        "timestamp": "2025-05-20T09:00:00Z"
      },
      {
        "user_id": "user123",
        "action_type": "view_job",
        "timestamp": "2025-05-20T09:05:00Z"
      }
    ]
  }'
```

**Récupérer les patterns**
```bash
curl http://localhost:5057/api/patterns
```

**Récupérer les patterns d'un utilisateur spécifique**
```bash
curl http://localhost:5057/api/patterns?user_id=user123
```

### Scores de préférence

**Calculer les scores**
```bash
curl -X POST http://localhost:5057/api/preference-scores \
  -H "Content-Type: application/json" \
  -d '{
    "actions": [
      {
        "user_id": "user123",
        "action_type": "view_job",
        "timestamp": "2025-05-20T10:00:00Z",
        "item_id": "job-123",
        "job_category": "Development"
      },
      {
        "user_id": "user123",
        "action_type": "view_job",
        "timestamp": "2025-05-20T11:00:00Z",
        "item_id": "job-456",
        "job_category": "Data Science"
      },
      {
        "user_id": "user123",
        "action_type": "apply_job",
        "timestamp": "2025-05-20T11:15:00Z",
        "item_id": "job-456",
        "job_category": "Data Science"
      }
    ],
    "categories": ["Development", "Data Science", "DevOps"],
    "recency_decay": 0.9,
    "time_window_days": 30
  }'
```

**Récupérer les scores**
```bash
curl http://localhost:5057/api/preference-scores
```

**Récupérer les scores d'un utilisateur spécifique**
```bash
curl http://localhost:5057/api/preference-scores?user_id=user123
```

### Ajout d'interactions et mise à jour globale

```bash
curl -X POST http://localhost:5057/api/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "interactions": [
      {
        "user_id": "user123",
        "action_type": "search",
        "timestamp": "2025-05-21T08:30:00Z",
        "query": "data science"
      }
    ]
  }'
```

## 4. Intégration avec le reste du système

Le service d'analyse comportementale est intégré avec le reste de l'application via l'API principale :

```bash
# Envoyer des données de comportement utilisateur
curl -X POST http://localhost:5050/api/analytics/user-behavior \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "action_type": "view_job",
    "item_id": "job-789",
    "job_category": "DevOps",
    "timestamp": "2025-05-21T08:30:00Z"
  }'

# Récupérer les recommandations basées sur le comportement
curl http://localhost:5050/api/recommendations/user123
```

## 5. Format des données

### Actions utilisateur

Chaque action utilisateur doit contenir au minimum :

```json
{
  "user_id": "identifiant_unique",
  "action_type": "type_action",  // ex: login, view_job, apply_job, search
  "timestamp": "2025-05-21T08:30:00Z"  // format ISO 8601
}
```

Attributs additionnels selon le type d'action :

- Pour les vues de fiches de poste : `item_id`, `job_category`, `duration` (en secondes)
- Pour les candidatures : `item_id`, `job_category`
- Pour les recherches : `query`

## 6. Tests unitaires

Pour exécuter les tests unitaires :

```bash
# Installer pytest si nécessaire
pip install pytest

# Exécuter les tests
python -m pytest tests/unit/comportement/
```