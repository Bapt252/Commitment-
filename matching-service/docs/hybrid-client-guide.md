# Guide d'utilisation du client Google Maps hybride

Ce guide explique comment utiliser le client Google Maps hybride pour le module de transport Nexten SmartMatch.

## Présentation

Le client hybride est une solution qui combine l'API Google Maps réelle avec une simulation intelligente. Il est conçu pour :

1. Utiliser l'API Google Maps quand elle fonctionne correctement
2. Basculer automatiquement en mode simulation quand l'API échoue
3. Collecter des statistiques d'utilisation pour le débogage

Cette approche garantit que votre système de matching fonctionnera toujours, même en cas de problèmes avec l'API Google Maps.

## Installation

Le client hybride est fourni sous forme d'un module Python unique que vous pouvez intégrer à votre projet.

1. Assurez-vous que le fichier `hybrid_maps_client.py` est dans le répertoire `app/`
2. Importez-le dans votre code

## Utilisation de base

```python
from app.hybrid_maps_client import HybridGoogleMapsClient
from app.smartmatch_transport import CommuteMatchExtension

# Initialiser le client hybride
maps_client = HybridGoogleMapsClient()

# Utiliser le client hybride avec l'extension de transport
transport_extension = CommuteMatchExtension(maps_client)

# Calculer un score de trajet
score = transport_extension.calculate_commute_score(
    candidate_address="20 Rue de la Paix, 75002 Paris, France",
    job_address="Tour Montparnasse, 75015 Paris, France"
)
```

## Test

Pour tester le client hybride :

```bash
python test_simple_hybrid.py
```

Ce script effectue un test simple qui vérifie :
1. Le calcul des temps de trajet
2. Le calcul du score de transport
3. L'analyse de compatibilité

## Avantages

- **Fiabilité à 100%** : Fonctionne même si l'API Google Maps est indisponible
- **Compatibilité totale** : S'intègre parfaitement avec le code existant
- **Transparence** : Bascule automatiquement entre l'API et la simulation
- **Statistiques** : Collecte des données sur l'utilisation de l'API

## Données simulées

Le client hybride utilise :

1. Des données prédéfinies pour les trajets courants (Paris-Lyon, etc.)
2. Une génération intelligente pour les trajets inconnus

Vous pouvez facilement ajouter vos propres données prédéfinies en modifiant la méthode `_load_mock_data()`.

## Fonctionnement technique

Le client hybride suit un processus simple mais efficace :

1. Essaie d'utiliser l'API Google Maps réelle
2. En cas d'échec, bascule automatiquement vers la simulation
3. Retourne un résultat cohérent dans tous les cas

Cette approche garantit que votre système de matching fonctionnera toujours, même en cas de problèmes temporaires avec l'API.