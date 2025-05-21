# Service de Personnalisation pour Commitment

Ce service permet de personnaliser les résultats de matching entre CV et offres d'emploi en fonction des préférences des utilisateurs, de leur comportement passé et de techniques d'apprentissage automatique avancées.

## Fonctionnalités principales

1. **Personnalisation des résultats de recherche** : Réordonne et améliore les résultats de recherche d'offres d'emploi en fonction des préférences et du comportement de l'utilisateur.

2. **Personnalisation des poids de matching** : Ajuste les poids utilisés dans l'algorithme de matching (compétences, expérience, éducation, certifications) selon les préférences de l'utilisateur.

3. **Gestion du démarrage à froid** : Propose des recommandations initiales pour les nouveaux utilisateurs sans historique d'interactions.

4. **Filtrage collaboratif** : Utilise les préférences d'utilisateurs similaires pour améliorer les recommandations.

5. **Gestion de la dérive temporelle** : Prend en compte l'évolution des préférences utilisateur au fil du temps, donnant plus de poids aux interactions récentes.

6. **Tests A/B intégrés** : Permet d'expérimenter et d'évaluer différentes stratégies de personnalisation.

## Architecture

Le service de personnalisation est construit comme un microservice indépendant qui s'intègre avec le service de matching existant. Il est composé des modules suivants :

- **API Flask** (`api.py`) : Point d'entrée principal du service, expose les endpoints REST
- **Modèle de préférences** (`models/preference_model.py`) : Gère les préférences utilisateur et leur application
- **Filtrage collaboratif** (`models/collaborative_filter.py`) : Implémente les algorithmes de recommandation collaborative
- **Gestionnaire de démarrage à froid** (`models/cold_start.py`) : Gère les nouveaux utilisateurs sans historique
- **Gestionnaire de dérive temporelle** (`models/temporal_drift.py`) : Adapte les préférences en fonction de leur évolution dans le temps
- **Chargeur de données** (`utils/data_loader.py`) : Interface avec la base de données et les services externes
- **Gestionnaire de tests A/B** (`utils/ab_testing.py`) : Permet de tester différentes stratégies de personnalisation

## Intégration avec le système existant

Le service de personnalisation s'intègre avec le service de matching existant via un client personnalisé (`matching-service/app/services/personalization_client.py`). Ce client est utilisé à deux endroits clés :

1. Dans le processus de matching (`matching_service.py`) pour personnaliser les poids de matching
2. Dans le processus de recherche pour personnaliser l'ordre des résultats

## Configuration

Le service peut être configuré via des variables d'environnement ou le fichier `config.py` :

- `PORT` : Port d'écoute du service (défaut : 5060)
- `DATABASE_URL` : URL de connexion à la base de données
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB` : Configuration de Redis
- `MATCHING_SERVICE_URL` : URL du service de matching
- `AB_TESTING_ENABLED` : Active/désactive les tests A/B
- `COLLABORATIVE_FILTER_ENABLED` : Active/désactive le filtrage collaboratif
- `TEMPORAL_DRIFT_ENABLED` : Active/désactive la gestion de la dérive temporelle

## Base de données

Le service nécessite plusieurs tables dans la base de données PostgreSQL :

- `user_preferences` : Stocke les préférences des utilisateurs
- `user_interactions` : Enregistre les interactions utilisateur (vues, recherches, etc.)
- `user_feedback` : Stocke les feedbacks explicites (likes, dislikes, etc.)
- `ab_test_results` : Enregistre les résultats des tests A/B

Un script de migration SQL est fourni dans `migrations/init_db.sql`.

## Démarrage du service

```bash
# Démarrer le service directement
cd personalization-service
./start-personalization.sh

# Ou via Docker Compose (recommandé)
docker-compose up -d personalization-service
```

## Endpoints API

### Santé du service
- `GET /health` : Vérifie l'état du service
- `GET /` : Informations sur le service

### Personnalisation
- `POST /api/v1/personalize/job-search` : Personnalise les résultats de recherche d'offres
- `POST /api/v1/personalize/matching` : Personnalise les poids de matching

### Gestion des préférences
- `POST /api/v1/preferences` : Enregistre les préférences d'un utilisateur
- `GET /api/v1/preferences/<user_id>` : Récupère les préférences d'un utilisateur

### Feedback
- `POST /api/v1/feedback` : Enregistre un feedback utilisateur

## Tests

Voir le guide de test dans [TESTING.md](TESTING.md) pour des exemples d'utilisation et des cas de test.
