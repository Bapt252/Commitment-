"""
Configuration pour le module d'analyse comportementale et de profilage utilisateur.

Ce fichier contient les paramètres de configuration pour les différents composants
du module de profilage utilisateur de la Session 8.
"""

import os
from typing import Dict, Any

# Chemins de stockage
STORAGE_BASE_PATH = os.environ.get("STORAGE_BASE_PATH", "./data/session8")
PROFILES_PATH = os.path.join(STORAGE_BASE_PATH, "profiles")
FEATURES_PATH = os.path.join(STORAGE_BASE_PATH, "features")
PREFERENCES_PATH = os.path.join(STORAGE_BASE_PATH, "preferences")
PATTERNS_PATH = os.path.join(STORAGE_BASE_PATH, "patterns")
CLUSTERS_PATH = os.path.join(STORAGE_BASE_PATH, "clusters")
VISUALIZATIONS_PATH = os.path.join(STORAGE_BASE_PATH, "visualizations")

# S'assurer que les chemins existent
for path in [PROFILES_PATH, FEATURES_PATH, PREFERENCES_PATH, PATTERNS_PATH, CLUSTERS_PATH, VISUALIZATIONS_PATH]:
    os.makedirs(path, exist_ok=True)

# Configuration de l'extraction de caractéristiques
FEATURE_EXTRACTION_CONFIG = {
    "time_window_days": 30,  # Période d'analyse par défaut (en jours)
    "min_events_count": 10,  # Nombre minimum d'événements requis pour l'analyse
    "feature_groups": ["activity", "content", "temporal", "engagement"],  # Groupes de caractéristiques à extraire
    "use_cache": True,  # Utiliser le cache pour les caractéristiques extraites
    "cache_ttl_hours": 24,  # Durée de vie du cache en heures
}

# Configuration du gestionnaire de profils
PROFILE_MANAGER_CONFIG = {
    "update_frequency_hours": 24,  # Fréquence de mise à jour des profils (en heures)
    "auto_create_profiles": True,  # Créer automatiquement des profils pour les nouveaux utilisateurs
    "profile_ttl_days": 90,  # Durée de vie des profils (en jours)
    "profile_version": "1.0",  # Version du schéma de profil
    "secure_fields": ["personal_info", "contact_details"],  # Champs sécurisés nécessitant des permissions
}

# Configuration du clustering d'utilisateurs
USER_CLUSTERING_CONFIG = {
    "algorithms": {
        "kmeans": {
            "n_clusters": 5,
            "random_state": 42
        },
        "dbscan": {
            "eps": 0.5,
            "min_samples": 5
        },
        "hierarchical": {
            "n_clusters": 5,
            "linkage": "ward"
        }
    },
    "default_algorithm": "kmeans",
    "feature_scaling": "standard",  # Options: "standard", "minmax", "robust", None
    "update_frequency_hours": 24,
    "min_users_for_clustering": 10,
    "dimensionality_reduction": {
        "method": "pca",  # Options: "pca", "tsne", None
        "n_components": 2
    }
}

# Configuration du détecteur de patterns
PATTERN_DETECTOR_CONFIG = {
    "sequence_pattern_min_support": 0.1,  # Support minimum pour les patterns de séquence
    "sequence_pattern_max_length": 5,  # Longueur maximum pour les patterns de séquence
    "time_based_pattern_intervals": ["hourly", "daily", "weekly"],  # Intervalles pour les patterns temporels
    "recurrent_pattern_min_occurrences": 3,  # Occurrences minimales pour les patterns récurrents
    "correlation_threshold": 0.3,  # Seuil de corrélation entre éléments
}

# Configuration du calculateur de préférences
PREFERENCE_CALCULATOR_CONFIG = {
    "update_frequency_hours": 24,  # Fréquence de mise à jour des préférences (en heures)
    "preference_categories": ["content", "interaction", "time", "feature"],  # Catégories de préférences
    "time_window_days": 30,  # Fenêtre temporelle pour l'analyse (en jours)
    "cache_ttl_hours": 24,  # Durée de vie du cache en heures
}

# Configuration de l'intégration avec le système de tracking
TRACKING_INTEGRATION_CONFIG = {
    "tracking_service_url": os.environ.get("TRACKING_SERVICE_URL", "http://localhost:8080/api/tracking"),
    "auth_token": os.environ.get("TRACKING_AUTH_TOKEN", ""),
    "batch_size": 100,  # Taille des lots pour les requêtes batch
    "timeout_seconds": 30,  # Timeout pour les requêtes
    "max_retries": 3,  # Nombre maximal de tentatives en cas d'échec
    "retry_delay_seconds": 5,  # Délai entre les tentatives (en secondes)
}

# Configuration de l'API
API_CONFIG = {
    "port": int(os.environ.get("API_PORT", 5000)),
    "host": os.environ.get("API_HOST", "0.0.0.0"),
    "debug": os.environ.get("API_DEBUG", "False").lower() == "true",
    "secret_key": os.environ.get("API_SECRET_KEY", "your-secret-key-here"),
    "auth_enabled": os.environ.get("API_AUTH_ENABLED", "True").lower() == "true",
    "cors_origins": os.environ.get("API_CORS_ORIGINS", "*").split(","),
    "rate_limit": {
        "enabled": True,
        "limit": 100,  # Nombre de requêtes
        "period": 60   # Période en secondes
    }
}

# Configuration des visualisations
VISUALIZATION_CONFIG = {
    "chart_themes": ["light", "dark"],
    "default_theme": "light",
    "color_schemes": {
        "categorical": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"],
        "sequential": ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6"],
        "diverging": ["#d73027", "#f46d43", "#fdae61", "#fee090", "#e0f3f8", "#abd9e9"]
    },
    "default_plot_size": {
        "width": 800,
        "height": 600
    },
    "interactive": True,
    "export_formats": ["png", "svg", "pdf"]
}

# Configuration globale
CONFIG: Dict[str, Any] = {
    "feature_extraction": FEATURE_EXTRACTION_CONFIG,
    "profile_manager": PROFILE_MANAGER_CONFIG,
    "user_clustering": USER_CLUSTERING_CONFIG,
    "pattern_detector": PATTERN_DETECTOR_CONFIG,
    "preference_calculator": PREFERENCE_CALCULATOR_CONFIG,
    "tracking_integration": TRACKING_INTEGRATION_CONFIG,
    "api": API_CONFIG,
    "visualization": VISUALIZATION_CONFIG,
    "storage": {
        "profiles_path": PROFILES_PATH,
        "features_path": FEATURES_PATH,
        "preferences_path": PREFERENCES_PATH,
        "patterns_path": PATTERNS_PATH,
        "clusters_path": CLUSTERS_PATH,
        "visualizations_path": VISUALIZATIONS_PATH
    }
}
