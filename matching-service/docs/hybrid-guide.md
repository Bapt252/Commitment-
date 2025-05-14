# Guide pratique du client hybride simplifié

Ce guide explique comment utiliser le client Google Maps hybride simplifié pour le module de transport Nexten SmartMatch.

## Installation

1. Placez le fichier `hybrid_maps_client.py` dans votre répertoire `app/`
2. Aucune modification supplémentaire n'est nécessaire

## Utilisation

```python
# Importer le client hybride
from app.hybrid_maps_client import HybridGoogleMapsClient

# L'utiliser comme remplacement direct pour GoogleMapsClient
client = HybridGoogleMapsClient()

# L'utiliser avec l'extension de transport
from app.smartmatch_transport import CommuteMatchExtension
extension = CommuteMatchExtension(client)

# Calculer des scores de trajet
score = extension.calculate_commute_score(
    candidate_address="Paris, France",
    job_address="Lyon, France"
)
```

## Avantages

1. **Compatibilité totale** avec l'API existante - aucun changement nécessaire dans votre code
2. **Résilience aux erreurs** - le client bascule automatiquement en simulation si l'API échoue
3. **Simplicité** - une seule classe légère sans dépendances complexes
4. **Statistiques** - suivi des appels API vs simulation

## Comment ça fonctionne

Le client hybride essaie d'abord d'utiliser l'API Google Maps réelle. Si celle-ci échoue (erreur d'API, quota dépassé, restriction, etc.), il bascule automatiquement vers une simulation :

1. Il utilise des données prédéfinies pour les trajets courants
2. Pour les trajets inconnus, il génère des temps cohérents basés sur le mode de transport

## Test

Pour vérifier que tout fonctionne :

```bash
python test_simple_hybrid.py
```

## Dépannage

Si vous rencontrez des problèmes :

1. Vérifiez que votre clé API est correctement configurée dans le fichier `.env`
2. Vérifiez les logs pour identifier les erreurs spécifiques
3. Assurez-vous que le module `googlemaps` est installé : `pip install googlemaps`

## Personnalisation

Vous pouvez facilement ajouter des données prédéfinies pour des trajets spécifiques :

```python
# Dans hybrid_maps_client.py, ajoutez des trajets prédéfinis
self.predefined_routes = {
    # Trajets existants...
    "Nouvelle Adresse|Autre Adresse": {
        "driving": 30,
        "transit": 45,
        "bicycling": 90,
        "walking": 180
    }
}
```