# Intégration du Module de Transport SmartMatch

Ce document explique comment intégrer et utiliser le module de calcul de temps de trajet dans le système SmartMatch.

## Architecture

Le système d'intégration des transports comporte deux composants principaux :

1. **`google_maps_client.py`** - Client pour l'API Google Maps qui calcule les temps de trajet
2. **`smartmatch_transport.py`** - Extension qui améliore les résultats de matching avec les données de transport

## Fonctionnalités

- Calcul des temps de trajet entre candidats et entreprises
- Prise en compte de divers modes de transport (voiture, transports en commun, vélo, marche)
- Ajustement des scores de matching en fonction des temps de trajet
- Prise en compte du travail à distance (score parfait pour les postes en "full remote")
- Génération d'insights sur les temps de trajet

## Utilisation

Voici comment utiliser l'extension de transport dans votre code :

```python
from app.smartmatch import SmartMatcher
from app.smartmatch_transport import enhance_smartmatch_with_transport

# Créer une instance standard du moteur de matching
matcher = SmartMatcher()

# Améliorer le matcher avec l'extension de transport
transport_matcher = enhance_smartmatch_with_transport(matcher, api_key="votre_cle_api_google_maps")

# Utiliser le matching amélioré
results = transport_matcher.match(candidates, companies)

# Générer des insights
insights = transport_matcher.generate_insights_extended(results)
```

## Données requises

Pour que l'extension fonctionne correctement, les données des candidats et des offres doivent contenir :

### Candidats
- `location` : Adresse du candidat
- `preferred_transport_mode` (optionnel) : Mode de transport préféré ("driving", "transit", "walking", "bicycling")
- `preferred_commute_time` (optionnel) : Temps de trajet maximum acceptable en minutes
- `remote_preference` (optionnel) : Préférence pour le travail à distance ("office_only", "hybrid", "full")

### Offres d'emploi / Entreprises
- `location` : Adresse de l'entreprise
- `remote_policy` (optionnel) : Politique de travail à distance ("office_only", "hybrid", "full")
- `transit_friendly` (optionnel) : Accessibilité en transport en commun
- `bicycle_facilities` (optionnel) : Présence d'installations pour vélos

## Client Google Maps minimal

Si vous rencontrez des problèmes avec le client Google Maps complet, une version minimale est disponible. Elle offre les fonctionnalités essentielles avec un code plus simple :

```python
# Exemple d'utilisation du client minimal
from app.google_maps_client_minimal import MinimalMapsClient

client = MinimalMapsClient(api_key="votre_cle_api")
travel_time = client.get_travel_time("Paris, France", "Lyon, France", mode="driving")
score = client.calculate_commute_score("Paris, France", "Lyon, France", max_time=60)

print(f"Temps de trajet: {travel_time} minutes")
print(f"Score de trajet: {score}")
```

## Améliorations

L'intégration avec Google Maps apporte plusieurs améliorations au système SmartMatch :

1. **Scores de matching plus pertinents** - Les candidats qui habitent plus près des entreprises (ou avec de bonnes options de transport) obtiennent de meilleurs scores
2. **Prise en compte des préférences individuelles** - Respecte le temps de trajet maximum acceptable pour chaque candidat
3. **Insights détaillés** - Fournit des informations sur les temps de trajet et leurs impacts sur le matching
4. **Support du travail hybride et distant** - Prend en compte les politiques de travail à distance des entreprises

## Configuration

Pour utiliser l'API Google Maps, vous devez définir une clé API :

1. Via une variable d'environnement : `GOOGLE_MAPS_API_KEY=votre_cle_api`
2. Dans un fichier `.env` dans le répertoire `matching-service`
3. En la passant directement lors de l'initialisation

## Test

Pour tester l'intégration du transport, utilisez le script suivant :

```bash
# Depuis le répertoire matching-service
python -c "
from app.smartmatch import SmartMatcher
from app.smartmatch_transport import enhance_smartmatch_with_transport

# Test avec des exemples simples
candidate = {
    'id': 'c1',
    'location': 'Paris, France',
    'preferred_transport_mode': 'transit',
    'preferred_commute_time': 45
}

job = {
    'id': 'j1',
    'location': 'Lyon, France',
    'remote_policy': 'hybrid'
}

# Créer et améliorer le matcher
matcher = SmartMatcher()
transport_matcher = enhance_smartmatch_with_transport(matcher)

# Calculer un matching
results = transport_matcher.match([candidate], [job])
print(results)
"
```

## Résolution de problèmes

Si vous rencontrez des erreurs avec l'API Google Maps :

1. Vérifiez que votre clé API est valide et possède les droits pour l'API Distance Matrix
2. Le système utilisera automatiquement un mode de secours avec estimation si l'API n'est pas disponible
3. Pour les tests sans API, initialisez avec `api_key=None` pour utiliser les estimations
