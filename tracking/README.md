# Guide d'utilisation du système de tracking

Ce module implémente un système de tracking pour collecter et analyser les données d'interaction des utilisateurs avec le système de matching.

## Structure des fichiers

- **tracking_simulator.py** : Contient la classe `TrackingSimulation` qui simule un système de tracking sans base de données
- **test_tracking_advanced.py** : Tests unitaires pour valider le fonctionnement du système de tracking

## Comment exécuter les tests

### 1. Test de la simulation

Pour tester la simulation de tracking, exécutez :

```bash
python tracking_simulator.py
```

Ce script démontre le fonctionnement de la classe `TrackingSimulation` avec des données générées aléatoirement.

### 2. Exécution des tests unitaires

Pour exécuter les tests unitaires :

```bash
python test_tracking_advanced.py
```

Ou avec le framework unittest :

```bash
python -m unittest test_tracking_advanced.py
```

## Fonctionnalités implémentées

- **Gestion du consentement utilisateur** (conformité GDPR)
- **Tracking d'événements** (propositions de match, visualisations, décisions)
- **Collecte de feedbacks** avec niveaux de satisfaction
- **Calcul de statistiques** (taux d'acceptation, note moyenne, etc.)

## Intégration avec d'autres modules

Pour intégrer ce système dans votre code :

```python
from tracking_simulator import TrackingSimulation

# Créer une instance du système de tracking
tracking = TrackingSimulation()

# Enregistrer le consentement utilisateur
tracking.set_user_consent("user123", "analytics", True)

# Suivre un événement de proposition de match
tracking.track_match_proposed(
    "user123", "match456", 0.85,
    {"skill_weight": 0.7},
    5,
    {"skills": 0.9, "location": 0.8}
)

# Calculer des statistiques
stats = tracking.calculate_statistics()
print(stats["acceptance_rate"])
```

## Développement futur

Pour une implémentation complète du système de tracking, les étapes suivantes sont envisagées :

1. Connecter le système à une base de données PostgreSQL
2. Développer une API REST pour la collecte d'événements depuis le frontend
3. Mettre en place des tableaux de bord de visualisation avec Grafana

## Résolution des problèmes d'importation

Si vous rencontrez des erreurs d'importation avec la classe `TrackingSimulation`, assurez-vous que :

1. Les fichiers sont dans le même répertoire
2. Vous utilisez l'importation correcte dans vos scripts :
   ```python
   from tracking_simulator import TrackingSimulation
   ```
