# Guide d'intégration du système de tracking

Ce document fournit des instructions détaillées pour intégrer le système de tracking et de collecte de données dans l'application Commitment. Le système permet de suivre le comportement des utilisateurs, de collecter des feedbacks et d'analyser les performances du système de matching, tout en respectant les principes GDPR et la vie privée des utilisateurs.

## Table des matières

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Intégration frontend](#intégration-frontend)
   - [Initialisation du SDK](#initialisation-du-sdk)
   - [Gestion des consentements](#gestion-des-consentements)
   - [Tracking des événements](#tracking-des-événements)
   - [Exemples d'intégration](#exemples-dintégration)
5. [Intégration backend](#intégration-backend)
6. [Sécurité et GDPR](#sécurité-et-gdpr)
7. [Dashboard et analyse](#dashboard-et-analyse)
8. [Résolution des problèmes](#résolution-des-problèmes)

## Prérequis

- Node.js v14+ pour le frontend
- PostgreSQL v12+ pour le stockage des données
- Python 3.9+ pour les services backend

## Installation

### Base de données

Le schéma de la base de données doit être installé en exécutant le script SQL suivant :

```bash
psql -U postgres -d commitment -f database/08_tracking_schema.sql
```

### Backend

Les modules de tracking sont déjà intégrés dans le backend. Assurez-vous d'installer les dépendances nécessaires :

```bash
pip install asyncpg fastapi uvicorn
```

### Frontend

Ajoutez le SDK de tracking à votre application frontend :

```html
<!-- Pour une intégration directe dans le HTML -->
<script src="/js/tracking-sdk.js"></script>

<!-- OU via npm (si disponible) -->
npm install commitment-tracking-sdk
```

## Configuration

### Variables d'environnement

Configurez les variables d'environnement suivantes :

```bash
# Base de données
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=commitment

# Tracking
TRACKING_ENABLED=true
PRIVACY_MODE=standard  # 'standard' ou 'enhanced'
CONSENT_VERSION=1.0
```

### Configuration frontend

Vous pouvez configurer le SDK avec différentes options :

```javascript
const trackerConfig = {
  apiUrl: '/api/events',
  consentUrl: '/api/consent',
  batchSize: 10,           // Nombre d'événements par lot
  flushInterval: 5000,     // Intervalle d'envoi en ms
  useBeacon: true,         // Utiliser Navigator.sendBeacon
  debug: false,            // Mode debug
  anonymizeIp: true        // Anonymiser les IP
};

const tracker = new CommitmentTracking(trackerConfig);
```

## Intégration frontend

### Initialisation du SDK

Initialisez le SDK au chargement de l'application avec l'ID utilisateur :

```javascript
// Dans votre composant principal ou fichier d'initialisation
import { CommitmentTracking } from 'commitment-tracking-sdk';

// Créer une instance
const tracker = new CommitmentTracking();

// Initialiser avec l'ID utilisateur une fois authentifié
async function initializeTracking(userId) {
  const initialized = await tracker.init(userId);
  
  if (!initialized) {
    // Gérer le cas où l'utilisateur n'a pas donné son consentement
    showConsentBanner();
  }
}

// Appeler lors de l'authentification
userAuth.onLogin(user => {
  initializeTracking(user.id);
});
```

### Gestion des consentements

Implémentez un système de gestion des consentements :

```javascript
// Afficher une bannière de consentement
function showConsentBanner() {
  const banner = document.getElementById('consent-banner');
  banner.style.display = 'block';
  
  // Configurer les boutons d'acceptation/refus
  document.getElementById('accept-button').addEventListener('click', () => {
    tracker.setConsent('analytics', true);
    banner.style.display = 'none';
  });
  
  document.getElementById('decline-button').addEventListener('click', () => {
    tracker.setConsent('analytics', false);
    banner.style.display = 'none';
  });
}
```

### Tracking des événements

#### Suivi des événements de matching

```javascript
// Lorsqu'un match est proposé à l'utilisateur
function onMatchProposed(match) {
  tracker.trackMatchProposed({
    matchId: match.id,
    matchScore: match.score,
    matchParameters: match.parameters,
    alternativesCount: match.alternativesCount,
    constraintSatisfaction: match.constraintSatisfaction
  });
  
  // Afficher le match à l'utilisateur...
}

// Lorsqu'un utilisateur visualise un match
function onMatchViewed(match, viewDuration, complete) {
  tracker.trackMatchViewed({
    matchId: match.id,
    viewDurationSeconds: viewDuration,
    viewComplete: complete
  });
}

// Lorsqu'un utilisateur accepte ou refuse un match
function onMatchDecision(match, accepted, decisionTime, reasons) {
  tracker.trackMatchDecision({
    matchId: match.id,
    accepted: accepted,
    decisionTimeSeconds: decisionTime,
    reasons: reasons
  });
}
```

#### Suivi du feedback

```javascript
// Lorsqu'un utilisateur donne son feedback sur un match
function onFeedbackSubmitted(match, rating, feedback, aspects) {
  tracker.trackMatchFeedback({
    matchId: match.id,
    rating: rating,            // 1-5
    feedbackText: feedback,    // Texte libre
    specificAspects: aspects   // Ex: { relevance: 4, timing: 3 }
  });
}
```

#### Suivi des interactions et complétion

```javascript
// Lorsqu'une interaction a lieu après un match
function onUserInteraction(match, type, count, details) {
  tracker.trackMatchInteraction({
    matchId: match.id,
    interactionType: type,     // Ex: 'message', 'activity'
    interactionCount: count,
    details: details
  });
}

// Lorsqu'un engagement est terminé ou abandonné
function onEngagementCompleted(match, successful, duration, rate, indicators) {
  tracker.trackMatchCompletion({
    matchId: match.id,
    completed: successful,
    durationDays: duration,
    completionRate: rate,
    successIndicators: indicators
  });
}
```

### Exemples d'intégration

#### Intégration avec React

```jsx
import React, { useEffect, useState } from 'react';
import { CommitmentTracking } from 'commitment-tracking-sdk';

// Hook personnalisé pour le tracking
function useTracking(userId) {
  const [tracker, setTracker] = useState(null);
  
  useEffect(() => {
    if (!userId) return;
    
    const trackerInstance = new CommitmentTracking();
    trackerInstance.init(userId).then(() => {
      setTracker(trackerInstance);
    });
    
    return () => {
      trackerInstance.destroy();
    };
  }, [userId]);
  
  return tracker;
}

// Exemple de composant qui utilise le tracking
function MatchCard({ match, user }) {
  const tracker = useTracking(user?.id);
  const [viewStartTime, setViewStartTime] = useState(null);
  
  useEffect(() => {
    // Démarrer le chronométrage de visualisation
    setViewStartTime(Date.now());
    
    // Nettoyer lors du démontage
    return () => {
      if (tracker && viewStartTime) {
        const viewDuration = (Date.now() - viewStartTime) / 1000;
        tracker.trackMatchViewed({
          matchId: match.id,
          viewDurationSeconds: viewDuration,
          viewComplete: true
        });
      }
    };
  }, [match.id, tracker]);
  
  const handleAccept = () => {
    if (tracker) {
      const decisionTime = (Date.now() - viewStartTime) / 1000;
      tracker.trackMatchDecision({
        matchId: match.id,
        accepted: true,
        decisionTimeSeconds: decisionTime
      });
    }
    // Logique d'acceptation...
  };
  
  const handleReject = (reasons) => {
    if (tracker) {
      const decisionTime = (Date.now() - viewStartTime) / 1000;
      tracker.trackMatchDecision({
        matchId: match.id,
        accepted: false,
        decisionTimeSeconds: decisionTime,
        reasons: reasons
      });
    }
    // Logique de refus...
  };
  
  return (
    <div className="match-card">
      {/* Contenu de la carte */}
      <button onClick={handleAccept}>Accepter</button>
      <button onClick={() => handleReject(['not_interested'])}>Refuser</button>
    </div>
  );
}
```

#### Intégration avec Vue.js

```javascript
// plugins/tracking.js
import { CommitmentTracking } from 'commitment-tracking-sdk';

export default {
  install(Vue) {
    const tracker = new CommitmentTracking();
    
    // Rendre le tracker disponible globalement
    Vue.prototype.$tracker = tracker;
    
    // Mixin pour initialiser le tracking
    Vue.mixin({
      created() {
        // Si le composant racine et utilisateur connecté
        if (this.$root === this && this.$store.state.auth.user) {
          tracker.init(this.$store.state.auth.user.id);
        }
      }
    });
  }
};

// Dans main.js
import TrackingPlugin from './plugins/tracking';
Vue.use(TrackingPlugin);

// Utilisation dans un composant
export default {
  methods: {
    onMatchAccepted(match) {
      this.$tracker.trackMatchDecision({
        matchId: match.id,
        accepted: true,
        decisionTimeSeconds: this.getViewDuration()
      });
    }
  }
};
```

## Intégration backend

Le système de tracking est déjà intégré dans le backend. Voici comment l'utiliser dans vos routes API :

```python
from fastapi import FastAPI, Depends
from tracking.collector import EventCollector
from tracking.privacy import PrivacyManager
from tracking.schema import MatchProposedEvent

app = FastAPI()

# Dépendance pour obtenir le collecteur d'événements
def get_event_collector():
    privacy_manager = PrivacyManager()
    return EventCollector(privacy_manager)

# Exemple de route qui enregistre un événement lors d'une action
@app.post("/api/matches/{match_id}/propose")
async def propose_match(
    match_id: str,
    match_data: dict,
    collector: EventCollector = Depends(get_event_collector)
):
    # Logique métier...
    
    # Enregistrer l'événement
    event = MatchProposedEvent(
        user_id=match_data["user_id"],
        match_id=match_id,
        match_score=match_data["score"],
        match_parameters=match_data["parameters"],
        alternatives_count=match_data["alternatives_count"],
        constraint_satisfaction=match_data["constraint_satisfaction"]
    )
    await collector.collect_event(event)
    
    return {"status": "success"}
```

## Sécurité et GDPR

Le système intègre plusieurs mécanismes pour assurer la conformité GDPR :

1. **Consentement explicite** : Le tracking n'est activé qu'après consentement explicite de l'utilisateur.
2. **Anonymisation des données** : Les adresses IP sont anonymisées par défaut.
3. **Droit à l'oubli** : Endpoint API pour supprimer toutes les données d'un utilisateur.
4. **Minimisation des données** : Seules les données nécessaires sont collectées.
5. **Conservation limitée** : Mécanisme de nettoyage automatique des données anciennes.

Utilisez les fonctions suivantes pour respecter les droits des utilisateurs :

```python
# Supprimer les données d'un utilisateur
@app.delete("/api/user/{user_id}/data")
async def delete_user_data(
    user_id: str,
    privacy_manager: PrivacyManager = Depends(get_privacy_manager)
):
    success = await privacy_manager.delete_user_data(user_id)
    return {"success": success}

# Anonymiser les données d'un utilisateur
@app.post("/api/user/{user_id}/anonymize")
async def anonymize_user_data(
    user_id: str,
    privacy_manager: PrivacyManager = Depends(get_privacy_manager)
):
    success = await privacy_manager.anonymize_user_data(user_id)
    return {"success": success}
```

## Dashboard et analyse

Un dashboard Grafana est disponible pour visualiser les données de tracking. Accédez-y via :

```
http://localhost:3000/d/commitment/tracking-dashboard
```

Ce dashboard inclut les métriques suivantes :

1. **KPIs généraux** :
   - Taux d'acceptation des matchs
   - Note moyenne de satisfaction
   - Temps de décision moyen

2. **Analyse de conversion** :
   - Funnel de conversion (proposition → visualisation → acceptation)
   - Taux de complétion des engagements

3. **Feedback et satisfaction** :
   - Distribution des notes de feedback
   - Analyse des commentaires textuels

4. **Impact des contraintes** :
   - Corrélation entre respect des contraintes et acceptation
   - Influence des différentes contraintes sur le taux d'acceptation

Pour créer de nouveaux tableaux de bord, utilisez les vues SQL disponibles :

```sql
SELECT * FROM tracking.match_metrics WHERE date > CURRENT_DATE - INTERVAL '30 days';
SELECT * FROM tracking.feedback_metrics WHERE date > CURRENT_DATE - INTERVAL '30 days';
SELECT * FROM tracking.user_sessions WHERE session_duration > INTERVAL '5 minutes';
```

## Résolution des problèmes

### Problèmes courants

1. **Les événements ne sont pas enregistrés** :
   - Vérifiez le consentement utilisateur
   - Assurez-vous que le SDK est correctement initialisé
   - Vérifiez les erreurs dans la console du navigateur

2. **Problèmes de base de données** :
   - Vérifiez que le schéma tracking est créé
   - Vérifiez les permissions de l'utilisateur PostgreSQL

3. **Problèmes de performance** :
   - Augmentez la valeur de `batchSize` pour réduire le nombre de requêtes
   - Optimisez les index de la base de données

### Activation du mode debug

Pour faciliter le débogage, activez le mode debug dans le SDK :

```javascript
const tracker = new CommitmentTracking({
  debug: true
});
```

### Logs serveur

Les logs de tracking sont disponibles dans les fichiers :

```
logs/tracking.log
logs/privacy.log
```
