# Service de Personnalisation - Session 10

## Description

Service de personnalisation des recommandations d'emploi basé sur :
- Apprentissage des préférences utilisateur
- Recommandation collaborative
- Gestion du cold start
- Adaptation temporelle des préférences
- Tests A/B

## Endpoints

### Health Check
```
GET /health
```

### Collecte de Feedback
```
POST /api/feedback
{
  "user_id": "string",
  "job_id": "string",
  "action": "apply|save|view|ignore|reject",
  "match_score": float
}
```

### Poids Personnalisés
```
GET /api/personalized-weights/{user_id}
```

### Score Hybride
```
POST /api/hybrid-score
{
  "user_id": "string",
  "job_id": "string",
  "base_match_score": float
}
```

### Test A/B
```
POST /api/ab-test
{
  "user_id": "string",
  "variant": "control|demographic|collaborative|hybrid"
}
```

### Statistiques Utilisateur
```
GET /api/user-stats/{user_id}
```

### Recommandations Collaboratives
```
POST /api/collaborative-recommendations
{
  "user_id": "string",
  "candidate_jobs": ["job1", "job2", ...]
}
```

## Configuration

- `PORT`: Port d'écoute (défaut: 5060)
- `REDIS_HOST`: Hôte Redis
- `REDIS_PORT`: Port Redis
- `REDIS_DB`: Base de données Redis
- `DEBUG`: Mode debug

## Tests

```bash
python -m pytest test_personalization.py -v
```