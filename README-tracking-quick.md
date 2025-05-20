# Guide d'intégration du système de tracking

Ce document explique comment intégrer et utiliser le système de tracking dans le projet Commitment.

## Vue d'ensemble

Le système de tracking est conçu pour collecter des données comportementales sur les interactions des utilisateurs avec le système de matching. Il permet de :

- Suivre les événements utilisateur (proposition, visualisation, acceptation, refus de matchs)
- Collecter les feedbacks utilisateur
- Stocker les métriques de performance des matchs
- Respecter les exigences GDPR (consentement, droit à l'oubli)

## Structure du système

Le système comprend :

1. **Schéma de base de données** - `database/08_tracking_schema.sql`
2. **Simulation de test** - `test_tracking_simulation.py`
3. **Modules Python** - `tracking/schema.py`, `tracking/collector.py`, `tracking/privacy.py`
4. **API REST** - `api/events_api.py`, `api/consent_api.py`, `api/feedback_api.py`
5. **Dashboard** - Configuration Grafana dans `monitoring/grafana/dashboards/tracking-dashboard.json`

## Mise en place

### 1. Base de données

Appliquer le schéma de base de données :

```bash
psql -U postgres -d commitment -f database/08_tracking_schema.sql
```

### 2. Tests de simulation

Pour tester le système sans configurer la base de données :

```bash
python test_tracking_simulation.py
```

Cette simulation montre :
- La gestion du consentement utilisateur
- La collecte d'événements de différents types
- Le calcul de statistiques basiques

### 3. Intégration frontend

Le système peut être intégré avec n'importe quel frontend en utilisant des appels d'API REST.

Exemples d'événements à suivre :

#### Match proposé
```javascript
fetch('/api/events/match/proposed', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    event_id: 'evt_123',
    user_id: 'user_456',
    match_id: 'match_789',
    match_score: 85.5,
    match_parameters: { "skill_weight": 0.7 },
    alternatives_count: 5,
    constraint_satisfaction: { "skills": 0.9, "location": 0.8 },
    timestamp: new Date().toISOString()
  })
});
```

#### Match visualisé
```javascript
fetch('/api/events/match/viewed', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    event_id: 'evt_124',
    user_id: 'user_456',
    match_id: 'match_789',
    view_duration_seconds: 45.2,
    view_complete: true,
    timestamp: new Date().toISOString()
  })
});
```

#### Match accepté
```javascript
fetch('/api/events/match/accepted', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    event_id: 'evt_125',
    user_id: 'user_456',
    match_id: 'match_789',
    decision_time_seconds: 12.5,
    timestamp: new Date().toISOString()
  })
});
```

#### Feedback
```javascript
fetch('/api/events/match/feedback', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    event_id: 'evt_126',
    user_id: 'user_456',
    match_id: 'match_789',
    rating: 4,
    feedback_text: "Ce match était très pertinent pour mes compétences",
    specific_aspects: { "relevance": 5, "timing": 3 },
    timestamp: new Date().toISOString()
  })
});
```

### 4. Gestion du consentement

Le système nécessite le consentement utilisateur avant de collecter des données :

```javascript
// Définir le consentement
fetch('/api/consent/set', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user_456',
    consent_type: 'analytics',
    is_granted: true
  })
});

// Vérifier le consentement
fetch('/api/consent/check?user_id=user_456&consent_type=analytics')
  .then(response => response.json())
  .then(data => {
    if (data.has_consent) {
      // Collecter des données...
    } else {
      // Afficher une bannière de consentement...
    }
  });
```

### 5. Conformité GDPR

Le système prend en charge les fonctionnalités GDPR :

```javascript
// Droit à l'oubli - suppression des données
fetch('/api/user/user_456/data', {
  method: 'DELETE'
});

// Anonymisation des données
fetch('/api/user/user_456/anonymize', {
  method: 'POST'
});
```

## Dashboard et analyse

Le dashboard Grafana est disponible à l'adresse :

```
http://localhost:3000/d/3aeIakjnzz/commitment-tracking-dashboard
```

Il affiche :
- Taux d'acceptation des matchs
- Distribution des notes de feedback
- Temps moyen de décision
- Impact des contraintes sur les décisions
- Corrélation entre scores de match et satisfaction

## Prochaines étapes

Pour une intégration complète :

1. Adapter les noms de domaine et les URLs dans les exemples ci-dessus
2. Configurer le système de monitoring avec Grafana et Prometheus
3. Mettre en place les alertes pour les anomalies dans les métriques
4. Développer des analyses avancées basées sur les données collectées

## Ressources supplémentaires

- [Documentation complète](docs/tracking-integration-guide.md)
- [Exemples d'intégration](examples/tracking-integration/)
- [Documentation API](api/README.md)
