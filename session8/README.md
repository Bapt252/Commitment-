# Session 8 - Analyse comportementale et profiling utilisateur

Ce module contient les composants pour l'analyse comportementale et le profilage des utilisateurs, 
intégrés avec le système de tracking existant.

## Composants

### Composants implémentés
1. **FeatureExtractor** : Module d'extraction de caractéristiques comportementales
2. **ProfileManager** : Gestionnaire de profils utilisateurs
3. **UserClustering** : Module de clustering d'utilisateurs
4. **PatternDetector** : Détecteur de patterns comportementaux
5. **PreferenceCalculator** : Calculateur de scores de préférence dynamiques
6. **EnrichedProfilesAPI** : API pour accéder aux profils utilisateurs enrichis
7. **TrackingIntegration** : Intégration avec le système de tracking existant
8. **BehaviorVisualization** : Visualisations des clusters et patterns comportementaux

## Architecture

Le module d'analyse comportementale et de profilage utilisateur s'intègre dans l'architecture existante
du projet Commitment et communique avec le système de tracking pour récupérer les données utilisateurs
et enrichir les profils.

## Utilisation

### Extraction des caractéristiques et gestion des profils

```python
# Exemple d'utilisation du module de profilage utilisateur
from session8.feature_extractor import FeatureExtractor
from session8.profile_manager import ProfileManager
from session8.user_clustering import UserClustering
from session8.pattern_detector import PatternDetector
from session8.preference_calculator import PreferenceCalculator

# Initialisation des composants
feature_extractor = FeatureExtractor()
profile_manager = ProfileManager()
user_clustering = UserClustering()
pattern_detector = PatternDetector()
preference_calculator = PreferenceCalculator()

# Extraction des caractéristiques à partir des données de tracking
user_features = feature_extractor.extract_features(user_id="12345")

# Mise à jour du profil utilisateur
profile_manager.update_profile(user_id="12345", features=user_features)

# Analyse des clusters d'utilisateurs
clusters = user_clustering.update_clusters()

# Détection de patterns comportementaux
patterns = pattern_detector.detect_patterns(user_id="12345")

# Calcul des scores de préférence
preferences = preference_calculator.calculate_preferences(user_id="12345")
```

### Intégration avec le système de tracking

```python
from session8.tracking_integration import TrackingIntegration

# Initialisation avec les composants existants
tracking_integration = TrackingIntegration(
    profile_manager=profile_manager,
    feature_extractor=feature_extractor,
    pattern_detector=pattern_detector,
    preference_calculator=preference_calculator,
    user_clustering=user_clustering
)

# Démarrer le traitement automatique des événements
tracking_integration.start_auto_processing()

# Traiter manuellement les événements récents
stats = tracking_integration.process_recent_events()
print(f"Traité {stats['processed']} événements, mis à jour {stats['profiles_updated']} profils")

# Envoyer un événement de tracking
tracking_integration.track_event(
    user_id="12345",
    event_type="click",
    properties={
        "element_id": "apply_button",
        "element_type": "button",
        "page": "/job/123"
    }
)
```

### API de profils enrichis

```python
from session8.enriched_profiles_api import EnrichedProfilesAPI

# Initialisation avec les composants existants
api = EnrichedProfilesAPI(
    profile_manager=profile_manager,
    preference_calculator=preference_calculator,
    user_clustering=user_clustering,
    pattern_detector=pattern_detector
)

# Démarrer le serveur d'API
api.start()

# Pour intégrer avec un serveur existant (ex. Flask)
app = api.get_app()
# Puis utiliser l'app Flask comme d'habitude
```

#### Routes de l'API

- `GET /api/profile/health` - Vérifier l'état de l'API
- `POST /api/profile/auth` - Authentification (simulation)
- `GET /api/profile/<user_id>` - Obtenir le profil utilisateur
- `GET /api/profile/<user_id>/preferences` - Obtenir les préférences calculées
- `GET /api/profile/<user_id>/patterns` - Obtenir les patterns comportementaux
- `GET /api/profile/<user_id>/cluster` - Obtenir les informations de clustering
- `GET /api/profile/<user_id>/enriched` - Obtenir toutes les données enrichies
- `GET /api/profile/<user_id>/recommendations` - Obtenir des recommandations
- `PUT /api/profile/<user_id>` - Mettre à jour le profil utilisateur
- `POST /api/profile/<user_id>/recalculate` - Recalculer les données enrichies

### Visualisations comportementales

```python
from session8.behavior_visualization import BehaviorVisualization

# Initialisation avec les composants existants
visualizer = BehaviorVisualization(
    user_clustering=user_clustering,
    pattern_detector=pattern_detector,
    profile_manager=profile_manager,
    preference_calculator=preference_calculator
)

# Créer une visualisation spécifique
vis_result = visualizer.create_visualization(
    vis_type="cluster_scatter",
    user_id="12345"
)
print(f"Visualisation générée: {vis_result['files']}")

# Créer un tableau de bord complet pour un utilisateur
dashboard = visualizer.create_user_dashboard(user_id="12345")

# Créer un tableau de bord pour un cluster
cluster_dashboard = visualizer.create_cluster_dashboard(cluster_id="cluster_1")
```

#### Types de visualisations disponibles

1. `cluster_scatter` - Scatter plot des clusters d'utilisateurs
2. `user_cluster_radar` - Radar chart comparant un utilisateur à son cluster
3. `behavior_patterns_heatmap` - Heatmap des patterns comportementaux
4. `activity_timeline` - Timeline d'activité par jour et heure
5. `preference_radar` - Radar chart des préférences utilisateur
6. `user_engagement_bar` - Bar chart des métriques d'engagement
7. `content_preferences_breakdown` - Breakdown des préférences de contenu
8. `hourly_activity_heatmap` - Heatmap d'activité par heure et jour
9. `feature_usage_pie` - Pie chart de l'utilisation des fonctionnalités
10. `cluster_comparison` - Comparaison des différents clusters

## Configuration

La configuration du module de profilage utilisateur se fait via le fichier `config.py`.

Chaque composant peut être configuré individuellement en passant un dictionnaire de configuration lors de l'initialisation :

```python
# Configuration personnalisée pour le module de visualisation
visualization_config = {
    "output_path": "./custom_visualizations",
    "chart_theme": "dark",
    "plot_size": {
        "width": 1200,
        "height": 800
    }
}

# Initialisation avec la configuration personnalisée
visualizer = BehaviorVisualization(
    user_clustering=user_clustering,
    config=visualization_config
)
```

## Démarrage rapide

Pour démarrer rapidement avec l'ensemble du module de profilage utilisateur :

```python
from session8 import setup_profiling_system

# Initialiser tous les composants avec la configuration par défaut
components = setup_profiling_system()

# Accéder aux composants individuels
feature_extractor = components["feature_extractor"]
profile_manager = components["profile_manager"]
user_clustering = components["user_clustering"]
pattern_detector = components["pattern_detector"]
preference_calculator = components["preference_calculator"]
tracking_integration = components["tracking_integration"]
api = components["api"]
visualizer = components["visualizer"]

# Démarrer le traitement automatique et l'API
tracking_integration.start_auto_processing()
api.start()
```

## Dépendances

Ce module dépend des packages Python suivants :
- numpy
- pandas
- matplotlib
- seaborn
- flask
- jwt
- requests
- scikit-learn

Installez les dépendances avec pip :

```bash
pip install numpy pandas matplotlib seaborn flask pyjwt requests scikit-learn
```
