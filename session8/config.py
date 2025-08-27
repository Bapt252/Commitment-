\"\"\"
Configuration pour le module d'analyse comportementale et de profiling utilisateur.

Ce fichier contient les paramètres de configuration par défaut pour tous les 
composants du module Session 8.
\"\"\"

# Configuration par défaut pour tout le système de profilage
default_config = {
    # Configuration pour le FeatureExtractor
    "feature_extractor": {
        "max_features": 20,
        "feature_weights": {
            "engagement_score": 1.0,
            "session_duration": 0.8,
            "active_days": 0.7,
            "click_frequency": 0.6,
            "search_depth": 0.5,
            "content_preference": 0.9,
            "interaction_patterns": 0.8
        },
        "default_timeframe_days": 30
    },
    
    # Configuration pour le ProfileManager
    "profile_manager": {
        "storage_path": "./data/session8/profiles",
        "backup_enabled": True,
        "backup_interval_hours": 24,
        "max_profile_history": 10
    },
    
    # Configuration pour le UserClustering
    "user_clustering": {
        "algorithm": "kmeans",
        "n_clusters": 5,
        "min_users_for_clustering": 10,
        "dimensions": 2,
        "features_to_use": [
            "engagement_score",
            "session_duration.avg_duration_seconds",
            "active_days.activity_ratio",
            "click_frequency.clicks_per_session",
            "search_depth.unique_queries_count"
        ],
        "weights": {
            "engagement_score": 1.0,
            "session_duration.avg_duration_seconds": 0.8,
            "active_days.activity_ratio": 0.7,
            "click_frequency.clicks_per_session": 0.6,
            "search_depth.unique_queries_count": 0.5
        },
        "auto_update_interval_hours": 12
    },
    
    # Configuration pour le PatternDetector
    "pattern_detector": {
        "min_sequence_length": 2,
        "max_sequence_length": 5,
        "min_sequence_support": 2,
        "max_patterns": 20,
        "time_window_days": 14,
        "storage_path": "./data/session8/patterns"
    },
    
    # Configuration pour le PreferenceCalculator
    "preference_calculator": {
        "preference_weights": {
            "content_preferences": 0.4,
            "interaction_preferences": 0.3,
            "time_preferences": 0.2,
            "feature_preferences": 0.1
        },
        "storage_path": "./data/session8/preferences",
        "update_threshold_hours": 24,
        "scoring_methods": {
            "content_similarity": "weighted_overlap",
            "time_similarity": "gaussian",
            "feature_similarity": "cosine"
        }
    },
    
    # Configuration pour le TrackingIntegration
    "tracking_integration": {
        "tracking_service_url": "http://localhost:8080/api/tracking",
        "auth_token": "",
        "batch_size": 100,
        "timeout_seconds": 30,
        "max_retries": 3,
        "retry_delay_seconds": 5,
        "polling_interval_seconds": 300,
        "auto_processing_enabled": True,
        "events_cache_path": "./data/session8/tracking_cache",
        "events_cache_enabled": True
    },
    
    # Configuration pour le EnrichedProfilesAPI
    "enriched_profiles_api": {
        "port": 5050,
        "host": "0.0.0.0",
        "debug": False,
        "secret_key": "commitment-session8-secret-key",
        "auth_enabled": True,
        "cors_origins": ["*"],
        "rate_limit": {
            "enabled": True,
            "limit": 100,
            "period": 60
        }
    },
    
    # Configuration pour le BehaviorVisualization
    "behavior_visualization": {
        "output_path": "./data/session8/visualizations",
        "chart_theme": "light",
        "color_scheme": "categorical",
        "plot_size": {
            "width": 800,
            "height": 600
        },
        "interactive": True,
        "export_formats": ["png", "svg", "html"],
        "max_cache_age_hours": 24,
        "use_cache": True
    }
}
