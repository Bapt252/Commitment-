# Client Hybride Adapté pour le Module de Transport

Ce document explique l'utilisation du client hybride adapté pour le module de transport Nexten SmartMatch.

## Problème résolu

Le client hybride adapté résout un problème de compatibilité entre notre nouveau système hybride et l'API existante utilisée par le module `CommuteMatchExtension`. Cette solution garantit un fonctionnement optimal même avec des restrictions sur l'API Google Maps.

## Comment utiliser le client hybride adapté

### Test rapide

Pour tester rapidement le client hybride, exécutez :

```bash
python test_simple_hybrid.py
```

Ce script effectue un test simple de l'intégration entre le client hybride et l'extension de transport.

### Dans votre code

Pour utiliser le client hybride dans votre code :

```python
from app.hybrid_maps_client import HybridGoogleMapsClient
from app.smartmatch_transport import CommuteMatchExtension

# Initialiser le client hybride
maps_client = HybridGoogleMapsClient()

# Utiliser le client hybride avec l'extension de transport
transport_extension = CommuteMatchExtension(maps_client)

# Calculer un score de trajet
score = transport_extension.calculate_commute_score(
    candidate_address="Paris, France",
    job_address="Lyon, France"
)
```

## Avantages du client hybride adapté

1. **Compatibilité totale** avec l'API existante de `CommuteMatchExtension`
2. **Résilience face aux erreurs d'API** grâce au basculement automatique en simulation
3. **Simplicité d'utilisation** - aucun changement requis dans le code existant
4. **Statistiques d'utilisation** pour surveiller les performances de l'API

## Fonctionnement technique

Le client hybride adapté suit une approche simple mais efficace :

1. Il tente d'abord d'utiliser l'API Google Maps réelle
2. En cas d'échec, il bascule automatiquement vers une simulation basée sur des données prédéfinies
3. Il conserve une interface compatible avec le code existant

## Comparaison avec l'implémentation précédente

| Fonctionnalité | Client original | Client hybride adapté |
|----------------|----------------|----------------------|
| Compatibilité API | ✅ | ✅ |
| Résilience aux erreurs | ❌ | ✅ |
| Fonctionnement sans API | ❌ | ✅ |
| Statistiques d'utilisation | ❌ | ✅ |
| Mode dégradé intelligent | ❌ | ✅ |

## Exemple d'intégration complet

Pour voir un exemple d'intégration complet avec l'algorithme de matching, exécutez :

```bash
python example_integration.py
```

Ce script montre comment le client hybride s'intègre parfaitement dans un système de matching bidirectionnel avec pondération des scores de compétences et de transport.

## Que faire en cas de problème

Si vous rencontrez des problèmes avec le client hybride :

1. Vérifiez les logs pour voir quels appels API échouent
2. Consultez les statistiques d'utilisation pour identifier les points faibles
3. Si nécessaire, ajoutez des données prédéfinies supplémentaires pour les trajets couramment utilisés

## Recommandation pour le déploiement

Pour le déploiement en production, nous recommandons d'utiliser le client hybride pour garantir un fonctionnement continu, même en cas de problèmes temporaires avec l'API Google Maps.
