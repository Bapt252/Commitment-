# Guide de Test pour le Service de Personnalisation

Ce document détaille comment tester le service de personnalisation après son intégration dans le projet Commitment.

## Prérequis

1. Assurez-vous que tous les services sont démarrés :
   ```bash
   docker-compose up -d
   ```

2. Vérifiez que le service de personnalisation est en cours d'exécution :
   ```bash
   curl http://localhost:5060/health
   ```
   Vous devriez recevoir une réponse indiquant que le service est en bonne santé.

## 1. Test de la personnalisation des résultats de recherche

### 1.1. Créer des préférences utilisateur

Commencez par créer des préférences pour un utilisateur test :

```bash
curl -X POST http://localhost:5060/api/v1/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "preferences": {
      "job_type": ["CDI", "Freelance"],
      "location": ["Paris", "Remote"],
      "skills": ["Python", "JavaScript", "React"],
      "company_size": ["Startup", "PME"],
      "weights": {
        "skills": 0.5,
        "experience": 0.3,
        "education": 0.1,
        "certifications": 0.1
      }
    }
  }'
```

### 1.2. Tester la personnalisation des résultats

Envoyez une requête pour personnaliser des résultats de recherche :

```bash
curl -X POST http://localhost:5060/api/v1/personalize/job-search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "results": [
      {"job_id": 1, "score": 0.75, "title": "Développeur Python", "location": "Paris", "company": "Tech Corp", "skills": ["Python", "Django", "SQL"]},
      {"job_id": 2, "score": 0.82, "title": "Développeur Frontend", "location": "Lyon", "company": "Web Agency", "skills": ["JavaScript", "React", "CSS"]},
      {"job_id": 3, "score": 0.68, "title": "Data Scientist", "location": "Remote", "company": "AI Startup", "skills": ["Python", "SQL", "Machine Learning"]}
    ],
    "search_query": "développeur python",
    "context": {"location": "Paris"}
  }'
```

Vous devriez recevoir les résultats réordonnés en fonction des préférences de l'utilisateur.

## 2. Test de la personnalisation des poids de matching

### 2.1. Personnalisation des poids

Envoyez une requête pour obtenir des poids personnalisés pour le matching :

```bash
curl -X POST http://localhost:5060/api/v1/personalize/matching \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "job_id": 1,
    "candidate_id": 101,
    "original_weights": {
      "skills": 0.4,
      "experience": 0.3,
      "education": 0.2,
      "certifications": 0.1
    }
  }'
```

### 2.2. Vérifier l'intégration avec le service de matching

Envoyez une requête de matching en incluant l'ID utilisateur :

```bash
curl -X POST http://localhost:5052/api/v1/queue-matching \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": 101,
    "job_id": 1,
    "webhook_url": "http://example.com/webhook"
  }' \
  -G --data-urlencode "user_id=user123"
```

Vérifiez ensuite le résultat du matching pour voir si les poids personnalisés ont été appliqués :

```bash
# Remplacez JOB_ID par l'ID retourné dans la réponse précédente
curl http://localhost:5052/api/v1/result/JOB_ID
```

## 3. Test du feedback utilisateur

Enregistrez un feedback utilisateur pour améliorer les futures recommandations :

```bash
curl -X POST http://localhost:5052/api/v1/record-feedback \
  -G \
  --data-urlencode "user_id=user123" \
  --data-urlencode "job_id=1" \
  --data-urlencode "action=like" \
  -H "Content-Type: application/json" \
  -d '{"source": "search_results", "position": 2}'
```

Puis testez à nouveau la personnalisation des résultats pour voir si le feedback a été pris en compte.

## 4. Test du démarrage à froid

Testez la personnalisation pour un nouvel utilisateur sans historique :

```bash
curl -X POST http://localhost:5060/api/v1/personalize/job-search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "new_user_456",
    "results": [
      {"job_id": 1, "score": 0.75, "title": "Développeur Python", "location": "Paris", "company": "Tech Corp", "skills": ["Python", "Django", "SQL"]},
      {"job_id": 2, "score": 0.82, "title": "Développeur Frontend", "location": "Lyon", "company": "Web Agency", "skills": ["JavaScript", "React", "CSS"]},
      {"job_id": 3, "score": 0.68, "title": "Data Scientist", "location": "Remote", "company": "AI Startup", "skills": ["Python", "SQL", "Machine Learning"]}
    ],
    "search_query": "développeur senior",
    "context": {"location": "Paris"}
  }'
```

Le service devrait appliquer une stratégie de démarrage à froid basée sur la requête de recherche.

## 5. Test des tests A/B

### 5.1. Vérifier le groupe A/B d'un utilisateur

```bash
curl -X POST http://localhost:5060/api/v1/personalize/job-search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_ab_789",
    "results": [],
    "search_query": "test"
  }'
```

La réponse devrait indiquer le groupe A/B de l'utilisateur ("control", "variant_a" ou "variant_b").

## 6. Scénario de test complet

Voici un scénario de test de bout en bout pour valider l'intégration complète :

1. Créez un nouveau candidat et une nouvelle offre d'emploi via les services de parsing respectifs.
2. Créez un profil utilisateur avec des préférences spécifiques.
3. Effectuez un matching entre le candidat et l'offre en utilisant l'ID utilisateur.
4. Vérifiez que les poids personnalisés ont été appliqués dans le résultat du matching.
5. Enregistrez un feedback positif (like) pour ce matching.
6. Effectuez à nouveau un matching similaire et vérifiez que le score a été amélioré.

Vous pouvez automatiser ce scénario à l'aide du script de test fourni :

```bash
./test-personalization.sh
```

## 7. Surveillance et métriques

Vous pouvez surveiller les performances des tests A/B via le endpoint suivant :

```bash
curl "http://localhost:5060/api/v1/ab/stats?test_id=personalization_test&event_type=conversion"
```

Cela vous permettra de comparer les taux de conversion entre les différentes variantes de personnalisation.

## Résolution des problèmes

Si vous rencontrez des problèmes lors des tests :

1. Vérifiez les logs du service de personnalisation :
   ```bash
   docker logs nexten-personalization
   ```

2. Assurez-vous que les tables nécessaires ont été créées dans la base de données :
   ```bash
   docker exec -it nexten-postgres psql -U postgres -d nexten -c "\dt"
   ```

3. Vérifiez la connectivité entre les services :
   ```bash
   docker exec -it nexten-personalization curl http://matching-api:5000/health
   ```
