# Nexten SmartMatch - Intégration Google Maps avancée

Ce document décrit l'intégration de l'API Google Maps dans le système Nexten SmartMatch pour améliorer les fonctionnalités de matching géographique.

## Vue d'ensemble

L'intégration Google Maps avancée offre les améliorations suivantes :

1. **Calcul précis des temps de trajet** entre les candidats et les entreprises
2. **Support de plusieurs modes de transport** (voiture, transports en commun, vélo, marche)
3. **Mise en cache intelligente** pour optimiser les performances et limiter les appels API
4. **Gestion des quotas et limites d'API** pour éviter les dépassements et les coûts imprévus
5. **Mode hybride automatique** qui bascule entre l'API réelle et la simulation si nécessaire

## Installation

Pour installer et configurer l'intégration Google Maps, exécutez le script suivant :

```bash
cd matching-service
chmod +x install_maps_integration.sh
./install_maps_integration.sh
```

Ce script va :
- Installer les dépendances requises (googlemaps, redis)
- Mettre à jour le fichier requirements.txt
- Configurer la clé API Google Maps dans le fichier .env

## Configuration

### Configuration de la clé API Google Maps

Pour utiliser l'API Google Maps, vous devez obtenir une clé API auprès de Google Cloud Platform :

1. Créez ou utilisez un projet existant dans la [Console Google Cloud](https://console.cloud.google.com/)
2. Activez les APIs suivantes :
   - Directions API
   - Distance Matrix API
   - Geocoding API
3. Créez une clé API avec les restrictions appropriées
4. Ajoutez la clé à votre fichier .env :
   ```
   GOOGLE_MAPS_API_KEY=votre_clé_api_google_maps
   ```

Alternativement, utilisez le script `install_maps_integration.sh` ou `update_maps_key.sh` pour configurer la clé.

### Configuration avancée

L'intégration peut être configurée avec les paramètres suivants :

| Paramètre | Description | Valeur par défaut |
|-----------|-------------|-------------------|
| `rate_limit` | Limite quotidienne d'appels API | 500 |
| `redis_url` | URL de connexion Redis pour le cache | None (cache fichier) |
| `use_hybrid_mode` | Basculer automatiquement entre API et simulation | True |
| `use_mock_mode` | Utiliser uniquement la simulation (sans API) | False |

Ces paramètres peuvent être modifiés lors de l'initialisation du client :

```python
from app.google_maps_client import GoogleMapsClient

# Exemple avec configuration personnalisée
client = GoogleMapsClient(
    api_key="votre_clé_api",
    rate_limit=1000,  # Augmenter la limite d'appels
    redis_url="redis://localhost:6379/0",  # Utiliser Redis pour le cache
    use_hybrid_mode=True  # Activer le mode hybride
)
```

## Système de cache

L'intégration utilise un système de cache intelligent pour réduire les appels à l'API Google Maps :

- **Cache en mémoire vive** pour les requêtes fréquentes
- **Cache Redis** pour la persistance et le partage entre instances (optionnel)
- **Cache fichier** comme solution de secours

Le cache est configuré pour conserver les résultats pendant 7 jours par défaut, ce qui est un bon compromis entre fraîcheur des données et économie d'appels API.

## Mode hybride

Le mode hybride est une fonctionnalité clé qui permet de basculer automatiquement entre l'API réelle et la simulation dans les cas suivants :

- La clé API Google Maps n'est pas configurée
- Le quota quotidien d'appels est atteint
- L'API renvoie une erreur ou un résultat invalide
- Le module googlemaps n'est pas installé

Ce mode garantit que le système continue de fonctionner même en cas de problèmes avec l'API Google Maps, tout en privilégiant les données réelles quand elles sont disponibles.

## Utilisation dans le code

### Calcul de temps de trajet

```python
from app.google_maps_client import GoogleMapsClient

# Initialiser le client
client = GoogleMapsClient()

# Calculer le temps de trajet entre deux adresses
time = client.get_travel_time(
    origin="Tour Eiffel, Paris, France",
    destination="Arc de Triomphe, Paris, France",
    mode="driving"  # Options: driving, transit, bicycling, walking
)

print(f"Temps de trajet: {time} minutes")
```

### Géocodage d'adresses

```python
# Convertir une adresse en coordonnées
coords = client.geocode_address("20 Rue de la Paix, 75002 Paris, France")

if coords:
    lat, lng = coords
    print(f"Coordonnées: {lat}, {lng}")
```

### Matrice de distance

```python
# Calculer les temps de trajet entre plusieurs origines et destinations
origins = ["Paris, France", "Lyon, France"]
destinations = ["Marseille, France", "Bordeaux, France"]

matrix = client.get_distance_matrix(origins, destinations, mode="driving")

# Afficher les résultats
for i, origin in enumerate(origins):
    for j, destination in enumerate(destinations):
        element = matrix["rows"][i]["elements"][j]
        distance = element.get("distance", {}).get("text", "N/A")
        duration = element.get("duration", {}).get("text", "N/A")
        print(f"{origin} → {destination}: {distance} ({duration})")
```

### Statistiques d'utilisation

```python
# Obtenir les statistiques d'utilisation du client et du cache
stats = client.get_usage_stats()

print(f"Total d'appels: {stats['total_calls']}")
print(f"Appels API réels: {stats['real_api_calls']}")
print(f"Résultats en cache: {stats['cached_results']}")
print(f"Taux de succès: {stats['success_rate']}%")
print(f"Usage quotidien: {stats['daily_usage']}/{stats['rate_limit']}")
```

## Tests

Pour tester l'intégration Google Maps, exécutez les commandes suivantes :

```bash
# Test complet de l'API
python test_maps_api.py

# Tests unitaires avancés
python -m unittest test_smartmatch_transport.py
```

## Intégration avec SmartMatch

L'intégration est déjà incorporée dans le système SmartMatch via l'extension de transport. Pour l'utiliser :

```python
from app.smartmatch import SmartMatcher
from app.smartmatch_transport import enhance_smartmatch_with_transport

# Créer une instance de SmartMatcher
matcher = SmartMatcher()

# Améliorer avec l'extension de transport
enhanced_matcher = enhance_smartmatch_with_transport(matcher)

# Utiliser normalement pour le matching
matches = enhanced_matcher.match(candidates, companies)
```

## Statistiques et monitoring

L'intégration collecte automatiquement des statistiques sur l'utilisation de l'API et l'efficacité du cache. Ces statistiques sont accessibles via la méthode `get_usage_stats()` et peuvent être utilisées pour le monitoring et l'optimisation.

## Considérations de coût

L'API Google Maps est un service payant avec des limites de quotas. Voici quelques recommandations pour optimiser les coûts :

1. **Utiliser le cache** pour réduire le nombre d'appels API
2. **Activer le mode hybride** pour basculer sur la simulation en cas de besoin
3. **Configurer des alertes** dans Google Cloud Platform pour surveiller l'utilisation
4. **Ajuster la durée de vie du cache** selon vos besoins de fraîcheur des données
5. **Limiter les appels à la Distance Matrix API**, qui est plus coûteuse (O(n*m))

## Dépannage

### Problèmes courants

| Problème | Solution |
|----------|----------|
| "Client Google Maps non initialisé" | Vérifiez que le module googlemaps est installé et que la clé API est configurée |
| "Quota d'API dépassé" | Augmentez le paramètre `rate_limit` ou utilisez le mode hybride |
| "Erreur API Google Maps" | Vérifiez que les APIs nécessaires sont activées dans Google Cloud |
| "Mode de transport non disponible" | Certains modes (comme transit) ne sont pas disponibles partout |

### Logs et débogage

L'intégration utilise le module `logging` de Python pour fournir des informations détaillées. Pour augmenter le niveau de détail :

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributeurs

- Équipe Nexten
- Claude/Anthropic

## Versions

- **v1.0.0** (16/05/2025) : Implémentation initiale avec cache et mode hybride
