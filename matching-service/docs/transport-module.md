# Module de Transport Nexten SmartMatch

Ce module étend le système de matching Commitment avec une fonctionnalité de calcul des temps de trajet entre les candidats et les entreprises.

## Configuration

### Prérequis

1. Une clé API Google Maps avec les APIs suivantes activées :
   - Directions API
   - Distance Matrix API
   - Geocoding API

2. Les dépendances Python suivantes :
   ```
   googlemaps
   flask-limiter
   prometheus-flask-exporter
   python-dotenv
   ```

### Configuration de l'environnement

Créez un fichier `.env` à la racine du projet avec votre clé API :

```
GOOGLE_MAPS_API_KEY=votre_clé_api_ici
```

## Utilisation

### Test du module

Pour tester que votre configuration est correcte :

```bash
# Test minimal
./test-transport-minimal.sh

# Test détaillé de l'API
python test_maps_api.py
```

### Intégration dans votre code

```python
from app.google_maps_client import GoogleMapsClient
from app.smartmatch_transport import CommuteMatchExtension

# Initialisation
maps_client = GoogleMapsClient()
commute_extension = CommuteMatchExtension(maps_client)

# Calcul du score de trajet
score = commute_extension.calculate_commute_score(
    candidate_address="10 Rue de Rivoli, 75004 Paris, France",
    job_address="Tour Montparnasse, 75015 Paris, France"
)

# Analyse détaillée
analysis = commute_extension.analyze_commute_compatibility(
    candidate_address="10 Rue de Rivoli, 75004 Paris, France",
    job_address="Tour Montparnasse, 75015 Paris, France",
    candidate_preferences={
        "max_commute_minutes": 30,
        "preferred_mode": "transit",
        "accepts_remote": True
    },
    job_requirements={
        "is_remote": False,
        "is_hybrid": True,
        "days_in_office": 3
    }
)
```

## Fonctionnalités

- **Calcul multi-modal** : Prend en compte différents modes de transport (voiture, transports en commun, vélo, marche)
- **Préférences personnalisées** : Respecte les contraintes de temps de trajet maximum
- **Support du télétravail** : Gestion intelligente des emplois hybrides et remote
- **Dégradation gracieuse** : Continue de fonctionner même en cas d'erreur API

## Développement futur

- [ ] Cache Redis pour les résultats de temps de trajet
- [ ] Optimisation des requêtes API avec batching
- [ ] Support des zones géographiques préférées
- [ ] Visualisation des résultats sur carte
