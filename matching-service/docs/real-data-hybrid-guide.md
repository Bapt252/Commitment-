# Guide: Client hybride Google Maps avec données réelles

Ce guide explique comment utiliser le client hybride Google Maps amélioré qui utilise des données réelles pour le module de transport Nexten SmartMatch.

## Présentation

Le client hybride avec données réelles est une solution avancée qui :

1. Utilise l'API Google Maps quand elle est disponible
2. Stocke les résultats dans un cache de données réelles
3. Utilise les données mises en cache lors des appels suivants
4. Bascule sur la simulation basée sur des données réelles en cas d'indisponibilité de l'API

Cette approche garantit des résultats précis, même quand l'API Google Maps n'est pas disponible.

## Installation

### 1. Installation des fichiers

```bash
# Créer les répertoires nécessaires
mkdir -p app data docs

# Télécharger les fichiers
curl -o app/real_data_hybrid_client.py https://raw.githubusercontent.com/Bapt252/Commitment-/simple-hybrid-solution/matching-service/app/real_data_hybrid_client.py
curl -o preload_maps_data.py https://raw.githubusercontent.com/Bapt252/Commitment-/simple-hybrid-solution/matching-service/preload_maps_data.py
curl -o test_real_data_hybrid.py https://raw.githubusercontent.com/Bapt252/Commitment-/simple-hybrid-solution/matching-service/test_real_data_hybrid.py
```

### 2. Préchargement des données

Préchargez des données réelles pour les adresses fréquemment utilisées :

```bash
# Précharger des adresses spécifiques
python preload_maps_data.py -a "Paris, France" "Lyon, France" "Marseille, France"

# Précharger des adresses depuis un fichier
python preload_maps_data.py -f addresses.txt

# Précharger des adresses depuis un fichier JSON
python preload_maps_data.py -j candidates.json
```

## Utilisation

### 1. Import et initialisation

```python
from app.real_data_hybrid_client import RealDataHybridClient
from app.smartmatch_transport import CommuteMatchExtension

# Initialiser le client
client = RealDataHybridClient()

# Utiliser avec l'extension de transport
extension = CommuteMatchExtension(client)
```

### 2. Calcul des temps de trajet

```python
# Calculer un temps de trajet
time = client.get_travel_time(
    origin="20 Rue de la Paix, 75002 Paris, France",
    destination="Tour Montparnasse, 75015 Paris, France",
    mode="driving"
)

print(f"Temps de trajet: {time} minutes")
```

### 3. Géocodage d'adresses

```python
# Géocoder une adresse
coords = client.geocode_address("Tour Eiffel, Paris, France")
if coords:
    lat, lng = coords
    print(f"Coordonnées: {lat}, {lng}")
```

## Avantages

1. **Précision** : Utilise des données réelles issues de l'API Google Maps
2. **Fiabilité** : Continue de fonctionner même en cas d'indisponibilité de l'API
3. **Performance** : Les données mises en cache sont récupérées instantanément
4. **Économie** : Réduit le nombre d'appels à l'API (économise les quotas)
5. **Compatibilité** : Fonctionne avec le code existant sans modification

## Fonctionnement technique

Le client hybride suit une stratégie en plusieurs étapes :

1. **Vérifier le cache** : Essayer d'abord de récupérer les données depuis le cache local
2. **Interroger l'API** : Si pas en cache, interroger l'API Google Maps et mettre en cache le résultat
3. **Simulation réaliste** : En cas d'échec, générer une estimation basée sur la distance géographique
4. **Fallback ultime** : En dernier recours, générer une estimation simple basée sur le mode de transport

## Configuration avancée

### Structure du fichier de cache

Le cache est stocké dans un fichier JSON avec le format suivant :

```json
{
  "routes": {
    "paris, france|lyon, france|driving": 273,
    "paris, france|lyon, france|transit": 119
  },
  "geocodes": {
    "paris, france": {"lat": 48.856614, "lng": 2.3522219},
    "lyon, france": {"lat": 45.764043, "lng": 4.835659}
  }
}
```

### Personnalisation du cache

Vous pouvez spécifier un fichier de cache personnalisé :

```python
client = RealDataHybridClient(cache_file="data/my_custom_cache.json")
```

## Dépannage

Si vous rencontrez des problèmes :

1. **Vérifiez le fichier de cache** : Assurez-vous qu'il est accessible en lecture/écriture
2. **Préchargez plus d'adresses** : Utilisez `preload_maps_data.py` pour précharger plus d'adresses
3. **Examinez les logs** : Le client enregistre des informations utiles pour le débogage
4. **Vérifiez les statistiques** : Les statistiques d'utilisation peuvent aider à identifier les problèmes

```python
print(client.stats)
```

## Tests

Pour tester le client hybride :

```bash
python test_real_data_hybrid.py
```

Ce script effectue une série de tests pour vérifier le bon fonctionnement du client hybride avec données réelles.