# Système d'amélioration continue basé sur le feedback

Ce document décrit l'architecture et le fonctionnement du système d'amélioration continue basé sur le feedback mis en place dans le projet Commitment.

## 1. Architecture générale

Le système est organisé en plusieurs composants interconnectés :

```
┌─────────────────┐      ┌────────────────┐     ┌─────────────────┐
│                 │      │                │     │                 │
│  Application    │──────▶  Collecte de   │────▶│  Base de données│
│  Commitment     │      │  Feedback      │     │  de Feedback    │
│                 │      │                │     │                 │
└─────────────────┘      └────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
┌─────────────────┐      ┌────────────────┐     ┌─────────────────┐
│                 │      │                │     │                 │
│  Déploiement    │◀─────│  Pipeline CI/CD│◀────│  Module d'analyse│
│  des modèles    │      │                │     │  et entraînement │
│                 │      │                │     │                 │
└─────────────────┘      └────────────────┘     └─────────────────┘
```

## 2. Collecte de feedback

### Feedback explicite

Les utilisateurs peuvent évaluer la qualité des matchings de plusieurs façons :

- **Note globale** : Évaluation de 1 à 5 étoiles
- **Commentaires qualitatifs** sur la pertinence des matchings
- **Évaluation par aspect** (compétences, expérience, etc.)

### Feedback implicite

Le système collecte également des indicateurs comportementaux :

- Taux de conversion (matching → engagement)
- Temps passé sur les profils recommandés
- Nombre de messages échangés après matching

## 3. Stockage et modèles de données

Le système utilise plusieurs tables dans la base de données :

- `matchings` : Les matchings générés par le système
- `matching_feedbacks` : Retours des utilisateurs sur les matchings
- `model_metrics` : Métriques des différentes versions de modèles
- `feedback_alerts` : Alertes générées par le système de monitoring

## 4. Pipeline d'entraînement automatisé

Le processus d'entraînement se déroule comme suit :

1. **Déclenchement** : Périodique ou basé sur un seuil (X nouveaux feedbacks)
2. **Préparation des données** : Extraction et nettoyage des données d'entraînement
3. **Validation croisée** : Évaluation avec techniques de cross-validation
4. **Comparaison** : Mesure de l'amélioration vs. modèle en production
5. **Déploiement** : Si les performances sont meilleures (avec seuil minimum d'amélioration)

## 5. Métriques suivies

### Métriques de performance du modèle

- **Précision** (accuracy) : Pourcentage de matchings corrects
- **Recall** : Capacité à identifier tous les matchings pertinents
- **Score F1** : Moyenne harmonique entre précision et recall
- **AUC-ROC** : Performance globale du classifieur

### Métriques business

- **Taux de satisfaction** : Basé sur les notes des utilisateurs
- **Taux d'engagement** : Pourcentage de matchings aboutissant à une interaction
- **Conversion business** : Taux de matchings débouchant sur un recrutement

## 6. Monitoring et alertes

Le système comprend un module de monitoring qui :

- Détecte les anomalies dans les patterns de feedback
- Alerte sur une baisse significative des métriques (>5%)
- Identifie les cas d'échec spécifiques pour analyse
- Génère des rapports périodiques de performance

## 7. Utilisation dans le code

### Collecter un feedback

```python
# Exemple d'appel API
feedback = {
    "matching_id": 123,
    "user_id": 456,
    "rating": 4,
    "comment": "Très bon matching sur les compétences techniques",
    "interaction_happened": True
}

response = requests.post("/api/feedback-system/", json=feedback)
```

### Récupérer des statistiques

```python
# Obtenir des statistiques sur les derniers 30 jours
stats = requests.get("/api/feedback-system/stats?days=30").json()

# Vérifier l'état de santé du système
health = requests.get("/api/monitoring/health").json()
```

## 8. Pipeline Airflow

Un DAG Airflow est configuré pour orchestrer les tâches récurrentes :

1. Vérification de la qualité des données
2. Déclenchement de l'entraînement
3. Évaluation des nouvelles métriques
4. Vérification du déploiement
5. Génération d'alertes si nécessaire

## 9. Intégration avec MLflow

Le système utilise MLflow pour :

- Le suivi des expériences d'entraînement
- L'enregistrement et le versionnage des modèles
- La comparaison des performances entre versions
- Le déploiement des modèles

## 10. Prochaines évolutions

- Implémentation d'A/B testing pour comparer des variantes de modèles
- Analyse sémantique des commentaires textuels
- Ajout de métriques comportementales plus avancées
- Extension du système à d'autres composants de la plateforme
