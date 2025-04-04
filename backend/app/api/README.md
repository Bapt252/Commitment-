# API Commitment

Ce document décrit l'API RESTful qui permet d'intégrer tous les composants ML du projet Commitment.

## Informations générales

- **Version**: 1.0.0
- **Base URL**: `/api/v1`
- **Documentation Swagger**: `/docs`
- **Documentation ReDoc**: `/redoc`

## Authentification

À implémenter dans une version future. Pour l'instant, l'API est accessible sans authentification pour faciliter le développement.

## Endpoints

L'API est structurée autour des ressources suivantes:

### Fiches de poste

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/job-posts/` | Créer une nouvelle fiche de poste |
| POST | `/job-posts/parse` | Analyser une fiche de poste sans l'enregistrer |
| GET | `/job-posts/` | Récupérer la liste des fiches de poste |
| GET | `/job-posts/{job_post_id}` | Récupérer une fiche de poste spécifique |

### Questionnaires

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/questionnaires/` | Créer un nouveau questionnaire |
| POST | `/questionnaires/{questionnaire_id}/analyze` | Analyser les réponses à un questionnaire |
| GET | `/questionnaires/` | Récupérer la liste des questionnaires |
| GET | `/questionnaires/{questionnaire_id}` | Récupérer un questionnaire spécifique |

### Matching

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/matching/` | Générer des matchings |
| GET | `/matching/{matching_id}` | Récupérer un matching spécifique |
| GET | `/matching/job/{job_post_id}` | Récupérer les matchings pour une fiche de poste |
| GET | `/matching/candidate/{candidate_id}` | Récupérer les matchings pour un candidat |

### Feedback

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/feedback/` | Soumettre un feedback |
| POST | `/feedback/batch` | Soumettre plusieurs feedbacks |
| GET | `/feedback/` | Récupérer la liste des feedbacks |
| GET | `/feedback/{feedback_id}` | Récupérer un feedback spécifique |
| GET | `/feedback/stats` | Récupérer des statistiques sur les feedbacks |

## Détails des endpoints

### Fiches de poste

#### POST `/job-posts/`

Télécharge et analyse une fiche de poste.

**Requête**:
- `file`: Fichier PDF, DOCX ou TXT (optionnel)
- `job_data`: Données JSON (optionnel)

**Réponse**:
```json
{
  "id": 1,
  "title": "Développeur Full Stack",
  "description": "Poste de développeur full stack...",
  "company": "Tech Company",
  "location": "Paris",
  "contract_type": "CDI",
  "salary_range": "45K-55K",
  "skills": ["Python", "JavaScript", "React"],
  "created_at": "2025-04-01T10:00:00",
  "updated_at": "2025-04-01T10:00:00"
}
```

#### POST `/job-posts/parse`

Analyse une fiche de poste sans l'enregistrer.

**Requête**:
- `file`: Fichier PDF, DOCX ou TXT

**Réponse**:
```json
{
  "title": "Développeur Full Stack",
  "description": "Poste de développeur full stack...",
  "company": "Tech Company",
  "location": "Paris",
  "contract_type": "CDI",
  "salary_range": "45K-55K",
  "skills": ["Python", "JavaScript", "React"],
  "confidence_scores": {
    "title": 0.95,
    "skills": 0.9,
    "location": 0.8
  }
}
```

### Matching

#### POST `/matching/`

Génère des matchings entre une fiche de poste et des candidats.

**Requête**:
```json
{
  "job_post_id": 1,
  "candidate_ids": [1, 2, 3],
  "min_score": 0.7
}
```

**Réponse**:
```json
[
  {
    "job_post_id": 1,
    "candidate_id": 1,
    "overall_score": 0.85,
    "score_details": [
      {
        "category": "skills",
        "score": 0.9,
        "explanation": "Compétences techniques correspondantes"
      },
      {
        "category": "experience",
        "score": 0.8,
        "explanation": "5 ans d'expérience"
      }
    ],
    "strengths": ["Python", "Machine Learning"],
    "gaps": ["Cloud AWS"],
    "recommendations": ["Formation AWS recommandée"],
    "created_at": "2025-04-01T10:00:00"
  }
]
```

### Questionnaires

#### POST `/questionnaires/{questionnaire_id}/analyze`

Analyse les réponses d'un candidat à un questionnaire.

**Requête**:
```json
{
  "candidate_id": 1,
  "answers": [
    {
      "question_id": 1,
      "value": 4
    },
    {
      "question_id": 2,
      "value": "J'ai 5 ans d'expérience avec PostgreSQL et MongoDB."
    }
  ]
}
```

**Réponse**:
```json
{
  "candidate_id": 1,
  "questionnaire_id": 1,
  "scores": {
    "programming": 0.8,
    "database": 0.9,
    "soft_skills": 0.7,
    "overall": 0.8
  },
  "strengths": ["Bases de données", "Programmation"],
  "areas_for_improvement": ["Compétences interpersonnelles"],
  "recommended_job_categories": ["Développeur backend", "Ingénieur base de données"],
  "analysis_timestamp": "2025-04-01T10:30:00"
}
```

### Feedback

#### POST `/feedback/`

Soumet un feedback pour amélioration continue.

**Requête**:
```json
{
  "entity_type": "matching",
  "entity_id": 1,
  "rating": 4,
  "comments": "Bon matching mais il manque quelques compétences clés",
  "aspects": {
    "skills": 3,
    "experience": 5,
    "education": 4
  },
  "submitted_by": "user@example.com"
}
```

**Réponse**:
```json
{
  "id": 1,
  "entity_type": "matching",
  "entity_id": 1,
  "rating": 4,
  "comments": "Bon matching mais il manque quelques compétences clés",
  "aspects": {
    "skills": 3,
    "experience": 5,
    "education": 4
  },
  "submitted_by": "user@example.com",
  "created_at": "2025-04-01T11:00:00"
}
```

## Codes d'erreur

| Code | Description |
|------|-------------|
| 400 | Requête invalide |
| 404 | Ressource non trouvée |
| 422 | Erreur de validation des données |
| 500 | Erreur serveur |

## Modèles de données

Voir les fichiers de modèles dans `app/models/` pour les définitions Pydantic complètes.

## Déploiement

L'API peut être déployée de plusieurs façons:

1. **Développement**: `uvicorn app.main:app --reload`
2. **Docker**: `docker-compose up`
3. **Production**: Kubernetes avec configuration de scaling (voir `k8s/`)
