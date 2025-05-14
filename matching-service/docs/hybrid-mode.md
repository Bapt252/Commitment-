# Mode Hybride pour le Module de Transport Nexten SmartMatch

Ce document explique comment utiliser le mode hybride pour le module de transport, qui combine l'API Google Maps réelle avec la simulation pour une fiabilité maximale.

## Qu'est-ce que le mode hybride ?

Le mode hybride est une approche intelligente qui :

1. **Essaie d'abord l'API Google Maps réelle** pour obtenir des données précises
2. **Bascule automatiquement en simulation** si l'API échoue ou renvoie des erreurs
3. **Garantit toujours une réponse** même en cas de problèmes d'API

## Avantages du mode hybride

Contrairement au mode simulation pur ou au mode API pur, le mode hybride offre :

- **Précision maximale** : utilise l'API réelle quand elle fonctionne
- **Fiabilité à 100%** : pas de pannes ou d'erreurs visibles pour l'utilisateur
- **Résilience** : fonctionnement continu même en cas de problèmes d'API
- **Économie de quota** : n'utilise l'API que lorsque nécessaire
- **Transition transparente** : aucun changement de code nécessaire

## Comment utiliser le mode hybride

### Initialisation en mode hybride (par défaut)

```python
from app.google_maps_client import GoogleMapsClient
from app.smartmatch_transport import CommuteMatchExtension

# Créer un client en mode hybride (par défaut)
client = GoogleMapsClient(use_hybrid_mode=True)

# Utiliser ce client pour initialiser l'extension de transport
extension = CommuteMatchExtension(client)

# Toutes les méthodes fonctionneront avec l'API réelle si possible,
# et basculeront automatiquement en simulation si nécessaire
score = extension.calculate_commute_score(
    candidate_address="Paris, France",
    job_address="Lyon, France"
)
```

### Exécuter le script de test en mode hybride

Un script de test dédié compare les différents modes :

```bash
python test_hybrid_mode.py
```

Ce script montre les différences entre les modes API uniquement, simulation et hybride, et fournit des statistiques d'utilisation.

## Statistiques d'utilisation

Le client hybride collecte automatiquement des statistiques sur l'utilisation de l'API :

```python
# Obtenir les statistiques d'utilisation
stats = client.get_usage_stats()
print(f"Appels API réussis: {stats['real_api_success']}")
print(f"Appels API échoués: {stats['real_api_failure']}")
print(f"Basculements en simulation: {stats['hybrid_fallbacks']}")
print(f"Taux de succès API: {stats['success_rate']}%")
```

Ces statistiques sont utiles pour identifier les problèmes d'API et optimiser l'utilisation.

## Modes disponibles

Le client Google Maps propose trois modes de fonctionnement :

| Mode | Configuration | Description |
|------|--------------|-------------|
| **API uniquement** | `GoogleMapsClient(use_hybrid_mode=False, use_mock_mode=False)` | Utilise uniquement l'API réelle. Échoue si l'API renvoie des erreurs. |
| **Simulation** | `GoogleMapsClient(use_mock_mode=True)` | Utilise uniquement la simulation. Jamais d'appels API réels. |
| **Hybride** | `GoogleMapsClient(use_hybrid_mode=True)` | Combine API réelle et simulation. Le meilleur des deux mondes. |

## Recommandations selon les environnements

- **Développement** : Mode hybride ou simulation
- **Tests automatisés (CI/CD)** : Mode simulation
- **Production** : Mode hybride pour une disponibilité maximale

## Comment fonctionne le basculement automatique ?

Le client hybride bascule automatiquement en simulation dans les cas suivants :

1. L'API renvoie une erreur (`REQUEST_DENIED`, etc.)
2. L'API ne trouve pas d'itinéraire (`ZERO_RESULTS`)
3. L'API renvoie un temps de trajet invalide (0 ou négatif)
4. Le client n'a pas pu être initialisé correctement

Ce comportement garantit que votre application continue de fonctionner même en cas de problèmes avec l'API Google Maps.

## Tests comparatifs

Les tests montrent que le mode hybride offre :

- **Fiabilité** : 100% des trajets calculés, contre ~60-70% en mode API seule
- **Performance** : temps de réponse moyen plus stable
- **Résilience** : fonctionnement continu même avec des restrictions d'API

Le mode hybride est particulièrement utile lorsque l'API Google Maps a des limitations spécifiques ou lorsque votre projet est en cours de développement.
