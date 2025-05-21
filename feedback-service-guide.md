# Guide d'utilisation du service de feedback et d'apprentissage continu

Ce guide explique comment utiliser le service de feedback et d'apprentissage continu de Commitment.

## Aperçu

Le service de feedback et d'apprentissage continu (port 5058) est responsable de :

1. **Collecte de feedback multi-canal** - Recueille le feedback explicite et implicite des utilisateurs via différentes sources
2. **Analyse de sentiment et de sujets** - Analyse le feedback pour extraire le sentiment et les sujets principaux
3. **Prédiction de satisfaction** - Prédit le niveau de satisfaction des utilisateurs
4. **Apprentissage continu** - Met à jour et améliore constamment les modèles pour une meilleure précision
5. **Intégration avec le service d'analyse comportementale** - Se connecte avec le service d'analyse comportementale (port 5057) pour enrichir les profiles utilisateurs

## Démarrage rapide

```bash
# Rendre le script exécutable
chmod +x start-feedback.sh

# Démarrer le service
./start-feedback.sh
```

## Endpoints API

Le service expose les endpoints suivants :

### Vérification de santé

```bash
# Vérifier que le service fonctionne
curl http://localhost:5058/health
```

Réponse attendue :
```json
{
  "status": "healthy",
  "service": "feedback-service"
}
```

### Collecte de feedback explicite

```bash
# Soumettre un feedback explicite
curl -X POST http://localhost:5058/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "content": "J'\''ai trouvé le matching de CV très précis et pertinent",
    "source": "web_app",
    "type": "explicit",
    "rating": 4,
    "category": "matching_quality"
  }'
```

Réponse attendue :
```json
{
  "id": "f8e7d6c5-b4a3-42f1-9087-654321abcdef",
  "status": "success",
  "sentiment": {
    "polarity": 0.75,
    "subjectivity": 0.6,
    "label": "positive"
  },
  "topics": ["matching", "precision", "pertinence"],
  "satisfaction_score": 85
}
```

### Collecte de feedback implicite

```bash
# Soumettre un feedback implicite basé sur des interactions
curl -X POST http://localhost:5058/api/feedback/implicit \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "interactions": [
      {
        "action_type": "view_job",
        "item_id": "job-456",
        "timestamp": "2025-05-21T08:30:00Z",
        "job_category": "Development"
      },
      {
        "action_type": "apply_job",
        "item_id": "job-456",
        "timestamp": "2025-05-21T08:35:00Z",
        "job_category": "Development"
      }
    ]
  }'
```

Réponse attendue :
```json
{
  "feedback_ids": [
    "a1b2c3d4-e5f6-47g8-9h10-ijklmnopqrst",
    "u1v2w3x4-y5z6-78a9-b0c1-defghijklmno"
  ],
  "status": "success",
  "satisfaction_score": 75
}
```

### Récupération de feedbacks

```bash
# Récupérer tous les feedbacks
curl http://localhost:5058/api/feedback

# Filtrer par utilisateur
curl http://localhost:5058/api/feedback?user_id=user123

# Filtrer par source
curl http://localhost:5058/api/feedback?source=web_app

# Filtrer par type
curl http://localhost:5058/api/feedback?type=explicit

# Filtrer par période
curl "http://localhost:5058/api/feedback?start_date=2025-05-01T00:00:00Z&end_date=2025-05-22T00:00:00Z"
```

### Récupération d'un feedback spécifique

```bash
# Récupérer un feedback par son ID
curl http://localhost:5058/api/feedback/f8e7d6c5-b4a3-42f1-9087-654321abcdef
```

### Analytics de sentiment

```bash
# Récupérer les analytics de sentiment
curl http://localhost:5058/api/analytics/sentiment

# Filtrer par utilisateur
curl http://localhost:5058/api/analytics/sentiment?user_id=user123

# Filtrer par période
curl "http://localhost:5058/api/analytics/sentiment?start_date=2025-05-01T00:00:00Z&end_date=2025-05-22T00:00:00Z"
```

### Analytics de sujets

```bash
# Récupérer les analytics des sujets
curl http://localhost:5058/api/analytics/topics

# Filtrer par utilisateur
curl http://localhost:5058/api/analytics/topics?user_id=user123
```

### Prédiction de satisfaction

```bash
# Obtenir la prédiction de satisfaction pour un utilisateur
curl http://localhost:5058/api/prediction/satisfaction?user_id=user123
```

### Réentraînement du modèle

```bash
# Déclencher un réentraînement du modèle
curl -X POST http://localhost:5058/api/learning/retrain \
  -H "Content-Type: application/json" \
  -d '{
    "full_retrain": true
  }'
```

### Intégration avec le service d'analyse comportementale

```bash
# Intégrer les données comportementales
curl -X POST http://localhost:5058/api/integration/behavior \
  -H "Content-Type: application/json" \
  -d '{
    "profiles": [
      {
        "user_id": "user123",
        "action_count": 42,
        "preferences": {
          "job_categories": {
            "Development": 0.8,
            "DevOps": 0.6
          }
        },
        "engagement_score": 0.75
      }
    ]
  }'
```

## Structure des données

### Feedback explicite

```json
{
  "user_id": "string",  // ID de l'utilisateur (facultatif)
  "content": "string",  // Contenu du feedback (obligatoire)
  "source": "string",   // Source du feedback: web_app, mobile_app, email, survey, chatbot, social_media
  "type": "string",     // Type de feedback: explicit, implicit
  "rating": number,     // Note numérique (1-5)
  "category": "string", // Catégorie: UI, UX, matching_quality, search, etc.
  "context": {          // Contexte supplémentaire (facultatif)
    "page": "string",
    "feature": "string"
  }
}
```

### Interaction pour feedback implicite

```json
{
  "action_type": "string",  // Type d'action: view_job, apply_job, save_job, etc.
  "item_id": "string",      // ID de l'élément concerné
  "timestamp": "string",    // Format ISO 8601
  "job_category": "string", // Pour les actions liées aux emplois
  "duration": number,       // Durée en secondes (facultatif)
  "details": {}             // Détails supplémentaires (facultatif)
}
```

## Intégration avec d'autres services

### Service d'analyse comportementale

Le service de feedback s'intègre avec le service d'analyse comportementale (port 5057) pour :

1. Enrichir les profils utilisateurs avec des données de satisfaction
2. Améliorer la prédiction de satisfaction en utilisant les patterns comportementaux
3. Fournir des insights sur les corrélations entre comportement et satisfaction

Pour activer cette intégration, assurez-vous que les deux services sont en cours d'exécution :

```bash
./start-user-behavior.sh
./start-feedback.sh
```

## Exemples d'utilisation avancée

### Workflow complet pour un nouvel utilisateur

1. Créer un profil utilisateur via le service d'analyse comportementale
2. Collecter des interactions implicites au fur et à mesure de l'utilisation
3. Collecter du feedback explicite après certaines actions clés
4. Obtenir une prédiction de satisfaction
5. Analyser les tendances de sentiment et de sujets

### Mise en place d'un tableau de bord analytique

Utilisez les endpoints analytics pour alimenter un tableau de bord avec :

- Tendances de satisfaction dans le temps
- Sujets les plus mentionnés dans les feedbacks
- Corrélations entre comportement et satisfaction
- Segmentation des utilisateurs par niveau de satisfaction

## Dépannage

### Le service ne démarre pas

Vérifiez :
- Les logs du conteneur : `docker-compose logs feedback-service`
- La connexion à la base de données PostgreSQL
- La connexion à Redis

### Erreurs d'API

Codes d'erreur courants :
- 400: Requête invalide (données manquantes ou incorrectes)
- 404: Ressource non trouvée
- 500: Erreur interne du serveur

## Ressources supplémentaires

- [Documentation API complète](/api-docs/feedback-service)
- [Architecture technique](/docs/architecture/feedback-service)
- [Modèle de prédiction de satisfaction](/docs/models/satisfaction-predictor)
