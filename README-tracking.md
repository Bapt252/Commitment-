# Système de Tracking et Analyse des Données de Matching

Ce module intègre le suivi, la collecte et l'analyse des données de matching pour améliorer en continu la qualité des correspondances proposées par l'algorithme hongrois avec contraintes.

## Fonctionnalités

1. **Collecte de données sur l'efficacité des matchs**
   - Tracking des événements utilisateurs (propositions, visualisations, acceptations, rejets)
   - Collecte de feedbacks structurés
   - Métriques de succès des engagements

2. **Conformité GDPR / Privacy by Design**
   - Gestion du consentement utilisateur
   - Anonymisation des données
   - Politique de conservation limitée

3. **Boucle de rétroaction ML**
   - Apprentissage continu basé sur le feedback utilisateur
   - Ajustement automatique des poids du modèle
   - Amélioration des contraintes pertinentes

4. **Analyse de performance**
   - KPIs de performance des matchs
   - Visualisations et tableaux de bord
   - Alertes automatiques

## Architecture

```
tracking/           # Collecte et gestion des données d'événements
├── schema.py       # Modèles de données événements/feedback
├── collector.py    # Collecteur d'événements utilisateur
├── privacy.py      # Gestion consentement et anonymisation
└── processor.py    # Traitement temps réel des données

api/                # API pour integration frontend
├── events_api.py   # Endpoints pour événements frontend
├── feedback_api.py # Collecte structurée de feedback
└── consent_api.py  # Gestion des consentements utilisateurs

analysis/           # Analyse et exploitation des données
├── metrics_calculator.py  # KPIs de performance des matchs
├── feedback_analyzer.py   # Analyse du feedback utilisateur
└── ml_feedback_loop.py    # Ajustement auto des poids du modèle

dashboard/          # Visualisation et monitoring
├── data_connectors.py     # Connexion aux sources de données
├── visualizations.py      # Graphiques et tableaux d'analyse
└── performance_monitors.py # Alertes et monitoring temps réel
```

## Installation

1. Installer les dépendances:
```bash
pip install fastapi uvicorn pandas numpy nltk asyncpg motor
```

2. Configurer les variables d'environnement:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_NAME=commitment
```

## Utilisation

1. Lancer le serveur:
```bash
python main.py
```

2. Accéder aux endpoints API:
   - API Events: `http://localhost:8000/api/events/`
   - API Consent: `http://localhost:8000/api/consent/`
   - API Feedback: `http://localhost:8000/api/feedback/`
   - Métriques: `http://localhost:8000/api/metrics/`

## Métriques clés

1. **Taux d'acceptation**
   - Pourcentage de matchs proposés qui sont acceptés
   - Tendance au fil du temps

2. **Satisfaction utilisateur**
   - Distribution des notes de feedback
   - Commentaires et thèmes récurrents

3. **Taux de complétion**
   - Pourcentage d'engagements terminés avec succès
   - Durée moyenne des engagements

4. **Impact des contraintes**
   - Corrélation entre satisfaction des contraintes et acceptation
   - Identification des contraintes les plus influentes

5. **Efficacité globale**
   - Score composite tenant compte de l'acceptation, satisfaction et complétion
   - Performance de l'optimiseur ML

## Boucle de feedback ML

Le système met à jour automatiquement les poids du modèle d'optimisation ML en fonction des feedbacks utilisateurs et des résultats des engagements. Ce processus comprend:

1. Collecte des données d'événements (acceptation, rejet, feedback, complétion)
2. Prétraitement et extraction de features
3. Mise à jour périodique du modèle
4. Évaluation continue des performances

## Conformité GDPR

1. **Consentement explicite**
   - Collecte de consentement granulaire
   - Possibilité de retrait du consentement

2. **Minimisation des données**
   - Anonymisation des identifiants utilisateurs
   - Collecte uniquement des données nécessaires

3. **Conservation limitée**
   - Nettoyage automatique des données après la période de rétention
   - Exports des données personnelles sur demande

4. **Droit à l'oubli**
   - Endpoint API pour suppression des données utilisateur
