# Session 8: Analyse Comportementale et Profiling Utilisateur

Cette session implémente un système complet d'analyse comportementale et de profiling utilisateur pour le projet Commitment. Le système analyse les données de suivi (tracking) utilisateur pour créer des profils enrichis, détecter des patterns comportementaux et calculer des scores de préférence dynamiques.

## 📊 Fonctionnalités implémentées

- **Analyse comportementale** : Traite les données de suivi utilisateur pour créer des profils enrichis
- **Clustering d'utilisateurs** : Segmente automatiquement les utilisateurs en fonction de leur comportement
- **Détection de patterns** : Identifie les séquences d'actions récurrentes dans le comportement utilisateur
- **Scoring de préférences** : Calcule et maintient des scores de préférence dynamiques pour chaque utilisateur
- **API de profils enrichis** : Expose les données de profil via une API REST sécurisée

## 🧩 Architecture et composants

Le système d'analyse comportementale est composé des éléments suivants:

1. **Schéma de base de données** (`database/15_behavioral_analysis_schema.sql`)
   - Tables pour les profils utilisateur enrichis
   - Tables pour les segments d'utilisateurs
   - Tables pour les patterns comportementaux
   - Tables pour les scores de préférence

2. **Module d'analyse comportementale** (`analysis/behavioral_analysis.py`)
   - Analyse des sessions utilisateur
   - Calcul de métriques comportementales
   - Clustering d'utilisateurs
   - Gestion des profils enrichis

3. **Module de détection de patterns** (`analysis/pattern_detection.py`)
   - Analyse de séquences d'actions
   - Détection de patterns comportementaux récurrents
   - Attribution de patterns aux utilisateurs

4. **Module de scoring de préférences** (`analysis/preference_scoring.py`)
   - Calcul de scores de préférence par catégorie
   - Système de pondération temporelle
   - Actualisation dynamique des préférences

5. **API de profils utilisateur** (`api/user_profile_api.py`)
   - Endpoints REST pour accéder aux profils enrichis
   - Fonctionnalités de recherche d'utilisateurs similaires
   - Déclenchement manuel d'analyses

6. **Scripts utilitaires** (`scripts/`)
   - Démarrage et arrêt du service d'API
   - Tâches d'analyse programmées

## 🔧 Installation et configuration

### Prérequis

- Base de données PostgreSQL
- Python 3.9+
- Bibliothèques: pandas, numpy, scikit-learn, flask, sqlalchemy

### Configuration de la base de données

Pour configurer le schéma de base de données:

```bash
psql -U postgres -d commitment -f database/15_behavioral_analysis_schema.sql
```

### Installation des dépendances

```bash
pip install pandas numpy scikit-learn flask sqlalchemy scipy
```

### Variables d'environnement

Les variables d'environnement suivantes peuvent être configurées:

- `DATABASE_URL`: URL de connexion à la base de données (défaut: `postgresql://postgres:postgres@localhost:5432/commitment`)
- `API_KEY`: Clé d'API pour sécuriser les endpoints (défaut: `commitment-session8-key`)
- `PORT`: Port pour le service d'API (défaut: `5002`)

## 🚀 Utilisation

### Démarrer le service d'API

```bash
chmod +x scripts/start_profile_api.sh
./scripts/start_profile_api.sh
```

### Arrêter le service d'API

```bash
chmod +x scripts/stop_profile_api.sh
./scripts/stop_profile_api.sh
```

### Endpoints API disponibles

- `GET /api/profiles/user/{user_id}` - Récupérer le profil enrichi d'un utilisateur
- `GET /api/profiles/user/{user_id}/similar` - Trouver des utilisateurs similaires
- `POST /api/profiles/user/{user_id}/update` - Déclencher une mise à jour de profil
- `POST /api/profiles/analyze` - Lancer une analyse complète pour tous les utilisateurs
- `GET /api/health` - Vérifier l'état du service

Exemple d'utilisation avec curl:

```bash
# Récupérer un profil utilisateur
curl -H "X-API-Key: commitment-session8-key" http://localhost:5002/api/profiles/user/1

# Trouver des utilisateurs similaires
curl -H "X-API-Key: commitment-session8-key" http://localhost:5002/api/profiles/user/1/similar

# Déclencher une analyse complète
curl -X POST -H "X-API-Key: commitment-session8-key" http://localhost:5002/api/profiles/analyze
```

## 📝 Exemples de résultats

### Profil utilisateur enrichi

```json
{
  "profile_id": 1,
  "user_id": 1,
  "username": "user1",
  "active_hours": {
    "morning": 0.2,
    "afternoon": 0.5,
    "evening": 0.3,
    "night": 0.0
  },
  "interaction_frequency": 4.2,
  "session_duration": 15.3,
  "segments": [
    {
      "segment_id": 1,
      "name": "Behavioral Segment 1",
      "description": "Users with similar behavioral patterns",
      "confidence": 0.85
    }
  ],
  "patterns": [
    {
      "pattern_id": 1,
      "name": "Pattern 1: view_profile → like",
      "description": "view_profile → like → message",
      "pattern_type": "interaction",
      "strength": 0.75,
      "observation_count": 12
    }
  ],
  "preferences": {
    "content_type": {
      "profile": {
        "score": 0.65,
        "confidence": 0.8
      },
      "message": {
        "score": 0.35,
        "confidence": 0.8
      }
    }
  },
  "recommendations": [
    {
      "type": "content",
      "item": "profile",
      "score": 0.65,
      "message": "Recommended based on your preference for profile content"
    }
  ]
}
```

## 🔍 Algorithmes et méthodes

### Clustering d'utilisateurs

Deux approches de clustering sont implémentées:

1. **KMeans** - Pour une segmentation basée sur les métriques d'activité
2. **DBSCAN** - Pour identifier les groupes de comportement similaire sans nombre prédéfini de clusters

### Détection de patterns comportementaux

La détection de patterns utilise:

1. Analyse de séquences d'événements
2. Calcul de fréquence et support de sous-séquences
3. Identification des séquences significatives

### Scoring de préférences

Le système de scoring utilise:

1. Pondération temporelle (decay exponentiel)
2. Normalisation des scores entre catégories
3. Calcul de scores de confiance basé sur le volume de données

## 📈 Performance et évolutivité

Le système a été conçu pour évoluer efficacement avec la croissance de la base d'utilisateurs:

- Traitement par lots des analyses lourdes
- Indexation optimisée des tables en base de données
- Mise en cache possible des résultats d'analyse

## 🔒 Sécurité et confidentialité

Mesures de sécurité implémentées:

- Authentification par clé API pour tous les endpoints
- Validation des entrées utilisateur
- Journalisation des accès et opérations

## 📅 Maintenance et évolution

Pour maintenir et faire évoluer ce système:

1. Exécuter régulièrement l'analyse complète (suggestion: tâche cron quotidienne)
2. Surveiller les logs dans `logs/profile_api.log`
3. Ajuster les paramètres des algorithmes en fonction des résultats observés

## 🤝 Intégration avec les modules existants

Ce module complète l'infrastructure de tracking existante en ajoutant:

1. Analyse avancée des données de suivi
2. Segmentation utilisateur pour le marketing et la personnalisation
3. API pour intégrer les insights comportementaux dans l'application

---

Pour toute question ou problème, veuillez ouvrir une issue dans ce dépôt.
