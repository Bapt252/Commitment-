# Système de Tracking et Analyse pour SmartMatch

Ce module implémente le tracking et l'analyse des données de matching pour améliorer continuellement les performances de l'algorithme hongrois avec contraintes.

## Fonctionnalités

1. **Collecte de données d'interactions**
   - Tracking des événements de matching (propositions, visualisations, décisions)
   - Collecte de feedbacks utilisateurs
   - Suivi des performances du matching

2. **Conformité GDPR**
   - Gestion du consentement utilisateur
   - Anonymisation des données
   - Nettoyage automatique des données expirées

3. **Boucle d'amélioration du modèle ML**
   - Rétro-alimentation du modèle d'optimisation
   - Ajustement basé sur les feedbacks utilisateurs
   - Apprentissage continu

4. **API pour l'intégration**
   - Endpoints pour enregistrer les événements
   - Gestion du consentement
   - Accès aux métriques

## Installation et Démarrage

### Prérequis

Assurez-vous d'avoir les dépendances requises:

```bash
pip install -r requirements.txt
```

### Configuration

1. Initialisez la base de données SQLite:

```bash
python setup_db.py
```

2. Créez un modèle ML initial (si nécessaire):

```bash
python init_model.py
```

### Démarrage du serveur

Lancez le serveur API:

```bash
python tracking_server.py
```

Par défaut, le serveur démarre sur `http://0.0.0.0:8001`. Vous pouvez modifier l'hôte et le port avec les variables d'environnement `HOST` et `PORT`.

## Utilisation de l'API

### Gestion du consentement

```python
# Enregistrer le consentement
response = requests.post(
    "http://localhost:8001/api/tracking/consent",
    params={
        "user_id": "user123",
        "analytics": True,
        "preferences": False,
        "improvement": True
    }
)

# Vérifier le statut du consentement
response = requests.get("http://localhost:8001/api/tracking/consent/user123")
```

### Tracking des événements

```python
# Enregistrer une proposition de match
response = requests.post(
    "http://localhost:8001/api/tracking/event/match-proposed",
    params={
        "user_id": "user123",
        "match_id": "match456",
        "match_score": 0.85,
        "alternatives_count": 5,
        "session_id": "session789"
    },
    json={
        "match_parameters": {"weight_skill": 0.7, "weight_availability": 0.3},
        "constraint_satisfaction": {"location": 0.9, "skills": 0.8, "preferences": 0.7}
    }
)

# Enregistrer une décision
response = requests.post(
    "http://localhost:8001/api/tracking/event/match-decision",
    params={
        "user_id": "user123",
        "match_id": "match456",
        "decision": True,  # Accepté
        "decision_time_seconds": 30.5
    },
    json={
        "reasons": ["Compétences pertinentes", "Disponibilité compatible"]
    }
)

# Enregistrer un feedback
response = requests.post(
    "http://localhost:8001/api/tracking/event/match-feedback",
    params={
        "user_id": "user123",
        "match_id": "match456",
        "rating": 4,
        "feedback_text": "Très bon matching, les compétences correspondaient parfaitement."
    },
    json={
        "specific_aspects": {"relevance": 5, "timing": 4, "communication": 3}
    }
)
```

### Consultation des métriques

```python
# Taux d'acceptation
response = requests.get("http://localhost:8001/api/metrics/acceptance", params={"days": 30})

# Métriques de satisfaction
response = requests.get("http://localhost:8001/api/metrics/satisfaction", params={"days": 30})

# Impact des contraintes
response = requests.get("http://localhost:8001/api/metrics/constraints", params={"days": 30})
```

### Maintenance

```python
# Déclencher une mise à jour du modèle ML
response = requests.post("http://localhost:8001/api/ml/update")

# Déclencher le nettoyage des données expirées
response = requests.post("http://localhost:8001/api/privacy/cleanup")
```

## Intégration avec le système existant

L'architecture de tracking est conçue pour s'intégrer facilement avec le système de matching existant. Pour chaque match généré, capturez les événements clés pour alimenter la boucle d'amélioration.

### Exemple simple d'intégration

```python
from tracking.collector import EventCollector
from tracking.privacy import PrivacyManager
from tracking.schema import MatchProposedEvent

# Initialiser les composants de tracking
privacy_manager = PrivacyManager()
event_collector = EventCollector(privacy_manager)

# Dans votre logique de matching
def propose_match(user_id, cv_data, job_data):
    # Logique de matching existante
    match_result = your_existing_matching_function(cv_data, job_data)
    
    # Enregistrer l'événement de matching
    event = MatchProposedEvent(
        user_id=user_id,
        match_id=match_result["id"],
        match_score=match_result["score"],
        match_parameters=match_result["parameters"],
        alternatives_count=len(match_result["alternatives"]),
        constraint_satisfaction=match_result["constraints"]
    )
    
    # Collecte l'événement (si l'utilisateur a donné son consentement)
    event_collector.collect_event(event)
    
    return match_result
```

## Accès à la documentation

La documentation Swagger complète est disponible à l'adresse:

```
http://localhost:8001/docs
```