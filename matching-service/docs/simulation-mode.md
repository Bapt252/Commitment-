# Mode Simulation pour le Module de Transport Nexten SmartMatch

Ce document explique comment utiliser le mode simulation pour développer et tester le module de transport sans dépendre de l'API Google Maps.

## Pourquoi utiliser le mode simulation ?

Plusieurs raisons peuvent justifier l'utilisation du mode simulation :

1. **Problèmes d'accès à l'API** :
   - Clé API non configurée ou non disponible
   - Problèmes de restriction d'accès à l'API
   - Quotas d'API limités

2. **Développement et tests** :
   - Développement sans connexion Internet
   - Tests automatisés reproductibles
   - CI/CD sans accès à des API externes

3. **Performances** :
   - Exécution plus rapide des tests
   - Pas de latence réseau

## Comment utiliser le mode simulation

### Initialisation avec le mode simulation

```python
from app.google_maps_client import GoogleMapsClient
from app.smartmatch_transport import CommuteMatchExtension

# Créer un client en mode simulation
client = GoogleMapsClient(use_mock_mode=True)

# Utiliser ce client pour initialiser l'extension de transport
extension = CommuteMatchExtension(client)

# Toutes les méthodes fonctionneront avec des données simulées
score = extension.calculate_commute_score(
    candidate_address="Paris, France",
    job_address="Lyon, France"
)
```

### Exécuter le script de test en mode simulation

Un script de test dédié au mode simulation est disponible :

```bash
python test_simulation.py
```

Ce script exécute plusieurs requêtes en utilisant le mode simulation et affiche les résultats.

## Données simulées

Le mode simulation utilise :

1. **Données prédéfinies** pour les trajets courants :
   - Paris → Lyon
   - Paris → Versailles
   - Nantes → Saint-Nazaire
   - etc.

2. **Génération aléatoire intelligente** pour les trajets inconnus :
   - Temps de trajet cohérents avec le mode de transport
   - Coordonnées géographiques vraisemblables

3. **Intégration avec les données de test** :
   - Utilise les adresses définies dans `test/data/sample_addresses.py`
   - Génère des temps de trajet réalistes pour les paires de matching

## Comparaison avec l'API réelle

### Avantages du mode simulation

- Pas de dépendance externe
- Résultats déterministes pour les tests
- Aucun coût d'API
- Pas de problèmes de quota ou de restrictions

### Limitations du mode simulation

- Données moins précises
- Pas de prise en compte des conditions de trafic réelles
- Pas de chemins réels calculés

## Quand revenir à l'API réelle

Une fois les développements terminés et que l'API Google Maps est correctement configurée :

1. Désactiver le mode simulation :
   ```python
   client = GoogleMapsClient(use_mock_mode=False)
   ```

2. Vérifier que les restrictions d'API sont correctement configurées dans la console Google Cloud :
   - Directions API
   - Routes API
   - Geocoding API

3. Tester avec l'API réelle pour vérifier les résultats
