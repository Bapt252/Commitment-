# Guide de test du service de personnalisation

Ce document explique comment tester le service de personnalisation nouvellement implémenté pour la plateforme Commitment.

## Prérequis

- Docker et Docker Compose installés
- Le service de matching et Redis en cours d'exécution
- Une clé API OpenAI valide (pour le parsing des CV et fiches de poste)

## 1. Démarrage des services

### Démarrer le service de personnalisation

```bash
# Rendre le script exécutable
chmod +x personalization-service/start-personalization.sh

# Démarrer le service
cd personalization-service
./start-personalization.sh
```

Si vous souhaitez le démarrer en mode développement (rechargement automatique) :

```bash
./start-personalization.sh dev
```

### Vérifier que le service est actif

```bash
curl http://localhost:5060/health
```

Vous devriez obtenir une réponse JSON confirmant que le service est en cours d'exécution.

## 2. Tests fonctionnels

### Tester la personnalisation des poids de matching

Cette API permet de personnaliser les poids utilisés pour le matching en fonction des préférences utilisateur.

```bash
curl -X POST http://localhost:5060/api/v1/personalize/matching \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "job_id": 456,
    "candidate_id": 789,
    "original_weights": {
      "skills": 0.4,
      "experience": 0.3,
      "education": 0.2,
      "certifications": 0.1
    }
  }'
```

### Tester la personnalisation des résultats de recherche

Cette API permet de réordonner les résultats de recherche en fonction des préférences utilisateur.

```bash
curl -X POST http://localhost:5060/api/v1/personalize/job-search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "results": [
      {
        "job_id": 123,
        "score": 0.85,
        "title": "Développeur Full Stack",
        "category": "Development"
      },
      {
        "job_id": 456,
        "score": 0.75,
        "title": "Data Scientist",
        "category": "Data Science"
      }
    ],
    "search_query": "développeur",
    "context": {
      "source": "search_page",
      "filters": {
        "location": "Paris"
      }
    }
  }'
```

### Enregistrer un feedback utilisateur

Cette API permet d'enregistrer des actions utilisateur pour améliorer les recommandations futures.

```bash
curl -X POST http://localhost:5060/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "job_id": 456,
    "action": "like",
    "context": {
      "source": "search_results",
      "position": 2
    }
  }'
```

### Récupérer les préférences utilisateur

```bash
curl http://localhost:5060/api/v1/preferences/user123
```

### Sauvegarder les préférences utilisateur

```bash
curl -X POST http://localhost:5060/api/v1/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "preferences": {
      "matching_weights": {
        "skills": 0.5,
        "experience": 0.3,
        "education": 0.1,
        "certifications": 0.1
      },
      "job_preferences": {
        "categories": ["Development", "Data Science"],
        "contract_types": ["CDI", "Freelance"],
        "locations": ["Paris", "Lyon", "Remote"],
        "remote": 0.7
      }
    }
  }'
```

## 3. Tests d'intégration avec le service de matching

Pour tester l'intégration avec le service de matching, vous pouvez utiliser l'API de matching avec le paramètre `user_id` :

```bash
curl -X POST http://localhost:5052/queue-matching \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 123,
    "job_id": 456,
    "webhook_url": "http://localhost:8080/callback"
  }' \
  -G -d "user_id=user123"
```

Vous pouvez également tester le matching en masse :

```bash
curl -X POST http://localhost:5052/queue-matching/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 123,
    "job_ids": [456, 789, 101],
    "webhook_url": "http://localhost:8080/callback"
  }' \
  -G -d "user_id=user123"
```

## 4. Tests A/B

Le service de personnalisation inclut un système de tests A/B. Vous pouvez vérifier les tests actifs et leurs résultats :

```bash
# Récupérer les tests A/B actifs
curl http://localhost:5060/api/v1/ab-tests

# Récupérer les résultats des tests A/B
curl http://localhost:5060/api/v1/ab-tests/results
```

## 5. Tests de performance

Pour tester les performances du service, vous pouvez utiliser l'outil Apache Benchmark :

```bash
# Installer l'outil si nécessaire
sudo apt install apache2-utils

# Tester les performances de la personnalisation des poids (10 requêtes concurrentes, 100 requêtes au total)
ab -n 100 -c 10 -T application/json -p personalization_payload.json http://localhost:5060/api/v1/personalize/matching
```

Créez d'abord un fichier `personalization_payload.json` avec le contenu suivant :

```json
{
  "user_id": "user123",
  "job_id": 456,
  "candidate_id": 789,
  "original_weights": {
    "skills": 0.4,
    "experience": 0.3,
    "education": 0.2,
    "certifications": 0.1
  }
}
```

## 6. Dépannage

### Le service ne démarre pas

- Vérifiez que Redis est en cours d'exécution (`docker ps | grep redis`)
- Vérifiez les logs d'erreur dans `personalization-service/logs/error.log`
- Assurez-vous que le port 5060 n'est pas déjà utilisé par un autre service

### Problèmes d'intégration avec le service de matching

- Vérifiez que la communication entre les services fonctionne en testant la santé des deux services
- Examinez les logs des deux services pour détecter d'éventuelles erreurs
- Assurez-vous que la configuration réseau Docker permet aux conteneurs de communiquer

### Erreurs dans les résultats personnalisés

- Pour les nouveaux utilisateurs, le système utilise le mécanisme de démarrage à froid
- Assurez-vous d'avoir enregistré suffisamment de feedbacks pour obtenir des recommandations personnalisées (au moins 5)
- Vérifiez que les données utilisées pour les tests sont cohérentes et représentatives
