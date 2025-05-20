"""
Module de visualisation des clusters et patterns comportementaux.

Ce module permet de générer des visualisations interactives pour les clusters
d'utilisateurs et les patterns comportementaux détectés.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Utiliser le backend Agg pour éviter les problèmes avec les serveurs sans GUI
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple
import json
import os
import logging
from datetime import datetime, timedelta
import base64
from io import BytesIO
import re

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class BehaviorVisualization:
    """
    Visualisation des clusters d'utilisateurs et des patterns comportementaux.
    """
    
    def __init__(self, user_clustering=None, pattern_detector=None, profile_manager=None, 
                 preference_calculator=None, config=None):
        """
        Initialise le module de visualisation.
        
        Args:
            user_clustering: Module de clustering d'utilisateurs
            pattern_detector: Détecteur de patterns comportementaux
            profile_manager: Gestionnaire de profils utilisateurs
            preference_calculator: Calculateur de préférences
            config: Configuration de la visualisation
        """
        self.user_clustering = user_clustering
        self.pattern_detector = pattern_detector
        self.profile_manager = profile_manager
        self.preference_calculator = preference_calculator
        
        # Configuration par défaut
        self.config = {
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
        
        # Mise à jour de la configuration si fournie
        if config:
            self.config.update(config)
        
        # S'assurer que le chemin de sortie existe
        os.makedirs(self.config["output_path"], exist_ok=True)
        
        # Configurer le style des plots
        if self.config["chart_theme"] == "dark":
            plt.style.use("dark_background")
        else:
            plt.style.use("seaborn-v0_8-whitegrid")
        
        # Liste des méthodes de visualisation disponibles
        self.visualization_methods = {
            "cluster_scatter": self.create_cluster_scatter_plot,
            "user_cluster_radar": self.create_user_cluster_radar_chart,
            "behavior_patterns_heatmap": self.create_behavior_patterns_heatmap,
            "activity_timeline": self.create_activity_timeline,
            "preference_radar": self.create_preference_radar_chart,
            "user_engagement_bar": self.create_user_engagement_bar_chart,
            "content_preferences_breakdown": self.create_content_preferences_breakdown,
            "hourly_activity_heatmap": self.create_hourly_activity_heatmap,
            "feature_usage_pie": self.create_feature_usage_pie_chart,
            "cluster_comparison": self.create_cluster_comparison_chart
        }
        
        logger.info("BehaviorVisualization initialized")
    
    def create_visualization(self, vis_type: str, user_id: Optional[str] = None, 
                           cluster_id: Optional[str] = None, 
                           params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crée une visualisation spécifique.
        
        Args:
            vis_type: Type de visualisation à créer
            user_id: Identifiant de l'utilisateur (pour les visualisations spécifiques à un utilisateur)
            cluster_id: Identifiant du cluster (pour les visualisations spécifiques à un cluster)
            params: Paramètres supplémentaires pour la visualisation
            
        Returns:
            Dict contenant les métadonnées et les URLs des visualisations générées
        """
        if vis_type not in self.visualization_methods:
            logger.error(f"Unknown visualization type: {vis_type}")
            return {"error": f"Unknown visualization type: {vis_type}"}
        
        if not params:
            params = {}
        
        # Créer un identifiant unique pour cette visualisation
        vis_id = self._generate_visualization_id(vis_type, user_id, cluster_id, params)
        
        # Vérifier si la visualisation existe déjà en cache
        if self.config["use_cache"]:
            cached_vis = self._check_visualization_cache(vis_id)
            if cached_vis:
                logger.info(f"Returning cached visualization {vis_id}")
                return cached_vis
        
        # Créer la visualisation
        try:
            vis_result = self.visualization_methods[vis_type](user_id, cluster_id, params)
            
            # Sauvegarder les métadonnées
            self._save_visualization_metadata(vis_id, vis_type, user_id, cluster_id, params, vis_result)
            
            logger.info(f"Created visualization {vis_id} of type {vis_type}")
            return vis_result
        except Exception as e:
            logger.error(f"Error creating visualization: {str(e)}")
            return {"error": f"Error creating visualization: {str(e)}"}
    
    def create_all_visualizations(self, user_id: str) -> Dict[str, Any]:
        """
        Crée toutes les visualisations disponibles pour un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Dict contenant toutes les visualisations générées
        """
        results = {}
        
        # Récupérer le cluster de l'utilisateur
        cluster_id = None
        if self.user_clustering:
            cluster_info = self.user_clustering.get_user_cluster(user_id)
            if cluster_info:
                cluster_id = cluster_info.get("cluster_id")
        
        # Créer chaque type de visualisation
        for vis_type in self.visualization_methods:
            try:
                results[vis_type] = self.create_visualization(vis_type, user_id, cluster_id)
            except Exception as e:
                logger.error(f"Error creating {vis_type} visualization: {str(e)}")
                results[vis_type] = {"error": str(e)}
        
        return results
    
    def create_cluster_dashboard(self, cluster_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Crée un tableau de bord complet pour un cluster.
        
        Args:
            cluster_id: Identifiant du cluster (si None, utilise tous les clusters)
            
        Returns:
            Dict contenant les visualisations générées pour le tableau de bord
        """
        dashboard = {
            "id": f"cluster_dashboard_{cluster_id if cluster_id else 'all'}",
            "timestamp": datetime.now().isoformat(),
            "visualizations": {}
        }
        
        # Sélectionner les visualisations à inclure dans le tableau de bord
        dashboard_visualizations = [
            "cluster_scatter",
            "behavior_patterns_heatmap",
            "content_preferences_breakdown",
            "hourly_activity_heatmap",
            "cluster_comparison"
        ]
        
        # Créer chaque visualisation
        for vis_type in dashboard_visualizations:
            try:
                dashboard["visualizations"][vis_type] = self.create_visualization(
                    vis_type, cluster_id=cluster_id
                )
            except Exception as e:
                logger.error(f"Error creating {vis_type} visualization: {str(e)}")
                dashboard["visualizations"][vis_type] = {"error": str(e)}
        
        return dashboard
    
    def create_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Crée un tableau de bord complet pour un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Dict contenant les visualisations générées pour le tableau de bord
        """
        dashboard = {
            "id": f"user_dashboard_{user_id}",
            "timestamp": datetime.now().isoformat(),
            "visualizations": {}
        }
        
        # Récupérer le cluster de l'utilisateur
        cluster_id = None
        if self.user_clustering:
            cluster_info = self.user_clustering.get_user_cluster(user_id)
            if cluster_info:
                cluster_id = cluster_info.get("cluster_id")
        
        # Sélectionner les visualisations à inclure dans le tableau de bord
        dashboard_visualizations = [
            "user_cluster_radar",
            "preference_radar",
            "activity_timeline",
            "user_engagement_bar",
            "feature_usage_pie"
        ]
        
        # Créer chaque visualisation
        for vis_type in dashboard_visualizations:
            try:
                dashboard["visualizations"][vis_type] = self.create_visualization(
                    vis_type, user_id=user_id, cluster_id=cluster_id
                )
            except Exception as e:
                logger.error(f"Error creating {vis_type} visualization: {str(e)}")
                dashboard["visualizations"][vis_type] = {"error": str(e)}
        
        return dashboard
    
    def create_cluster_scatter_plot(self, user_id: Optional[str] = None, 
                                   cluster_id: Optional[str] = None,
                                   params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crée un scatter plot des clusters d'utilisateurs.
        
        Args:
            user_id: Identifiant de l'utilisateur (pour surligner)
            cluster_id: Identifiant du cluster (pour filtrer)
            params: Paramètres supplémentaires
            
        Returns:
            Dict contenant les métadonnées et les URLs des visualisations générées
        """
        if not self.user_clustering:
            return {"error": "User clustering module not available"}
        
        # Récupérer les données de clustering
        clusters_data = self.user_clustering.get_clusters_data()
        if not clusters_data:
            return {"error": "No clustering data available"}
        
        # Convertir les données en DataFrame
        users = []
        for cluster_info in clusters_data.get("clusters", []):
            current_cluster_id = cluster_info.get("cluster_id")
            for member in cluster_info.get("members", []):
                user = {
                    "user_id": member.get("user_id"),
                    "cluster_id": current_cluster_id,
                    "x": member.get("coordinates", {}).get("x", 0),
                    "y": member.get("coordinates", {}).get("y", 0)
                }
                users.append(user)
        
        df = pd.DataFrame(users)
        if df.empty:
            return {"error": "No user data available for visualization"}
        
        # Filtrer par cluster si spécifié
        if cluster_id:
            df = df[df["cluster_id"] == cluster_id]
            if df.empty:
                return {"error": f"No users found in cluster {cluster_id}"}
        
        # Créer le plot
        plt.figure(figsize=(self.config["plot_size"]["width"]/100, self.config["plot_size"]["height"]/100), dpi=100)
        
        # Définir un colormap pour les clusters
        unique_clusters = df["cluster_id"].unique()
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_clusters)))
        
        # Tracer les points pour chaque cluster
        for i, cluster in enumerate(unique_clusters):
            cluster_data = df[df["cluster_id"] == cluster]
            plt.scatter(cluster_data["x"], cluster_data["y"], s=50, c=[colors[i]], label=f"Cluster {cluster}")
            
            # Ajouter le centre du cluster
            center_x = cluster_data["x"].mean()
            center_y = cluster_data["y"].mean()
            plt.scatter(center_x, center_y, s=200, c=[colors[i]], marker="X", edgecolors="white", linewidths=2)
        
        # Surligner l'utilisateur spécifié si présent
        if user_id:
            user_data = df[df["user_id"] == user_id]
            if not user_data.empty:
                plt.scatter(user_data["x"], user_data["y"], s=100, c="red", marker="*", edgecolors="white", linewidths=2, label=f"User {user_id}")
        
        plt.title("User Clusters Visualization", fontsize=16)
        plt.xlabel("Dimension 1", fontsize=12)
        plt.ylabel("Dimension 2", fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Sauvegarder le plot
        vis_id = self._generate_visualization_id("cluster_scatter", user_id, cluster_id, params)
        file_paths = self._save_visualization(plt, vis_id)
        
        plt.close()
        
        return {
            "id": vis_id,
            "type": "cluster_scatter",
            "timestamp": datetime.now().isoformat(),
            "files": file_paths,
            "data_summary": {
                "clusters_count": len(unique_clusters),
                "users_count": len(df)
            }
        }
    
    def create_user_cluster_radar_chart(self, user_id: Optional[str] = None, 
                                      cluster_id: Optional[str] = None,
                                      params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crée un radar chart des caractéristiques d'un utilisateur par rapport à son cluster.
        
        Args:
            user_id: Identifiant de l'utilisateur
            cluster_id: Identifiant du cluster (optionnel, utilisé si user_id non fourni)
            params: Paramètres supplémentaires
            
        Returns:
            Dict contenant les métadonnées et les URLs des visualisations générées
        """
        if not user_id:
            return {"error": "User ID is required for this visualization"}
        
        if not self.user_clustering or not self.profile_manager:
            return {"error": "Required modules not available"}
        
        # Récupérer le profil de l'utilisateur
        user_profile = self.profile_manager.get_profile(user_id)
        if not user_profile:
            return {"error": "User profile not found"}
        
        # Récupérer le cluster de l'utilisateur si pas spécifié
        if not cluster_id and self.user_clustering:
            cluster_info = self.user_clustering.get_user_cluster(user_id)
            if cluster_info:
                cluster_id = cluster_info.get("cluster_id")
        
        if not cluster_id:
            return {"error": "Cluster ID not found for the user"}
        
        # Récupérer les données du cluster
        cluster_data = self.user_clustering.get_cluster_data(cluster_id)
        if not cluster_data:
            return {"error": f"Cluster data not found for cluster {cluster_id}"}
        
        # Extraire les caractéristiques principales pour la comparaison
        features = [
            "engagement_score",
            "session_duration",
            "active_days",
            "click_frequency",
            "search_depth"
        ]
        
        # Récupérer les valeurs pour l'utilisateur et le cluster
        user_values = []
        cluster_values = []
        
        for feature in features:
            user_value = self._extract_feature_value(user_profile, feature)
            user_values.append(user_value)
            
            cluster_value = self._extract_feature_value(cluster_data.get("average_profile", {}), feature)
            cluster_values.append(cluster_value)
        
        # Normaliser les valeurs
        user_values, cluster_values = self._normalize_radar_values(user_values, cluster_values)
        
        # Créer le radar chart
        plt.figure(figsize=(self.config["plot_size"]["width"]/100, self.config["plot_size"]["height"]/100), dpi=100)
        
        # Configurations du radar chart
        angles = np.linspace(0, 2*np.pi, len(features), endpoint=False).tolist()
        angles += angles[:1]  # Fermer le cercle
        
        user_values += user_values[:1]  # Fermer le cercle
        cluster_values += cluster_values[:1]  # Fermer le cercle
        
        feature_labels = [f.replace("_", " ").title() for f in features]
        feature_labels += feature_labels[:1]  # Fermer le cercle
        
        ax = plt.subplot(111, polar=True)
        
        # Tracer les lignes
        ax.plot(angles, user_values, 'o-', linewidth=2, label=f"User {user_id}")
        ax.fill(angles, user_values, alpha=0.25)
        
        ax.plot(angles, cluster_values, 'o-', linewidth=2, label=f"Cluster {cluster_id}")
        ax.fill(angles, cluster_values, alpha=0.1)
        
        # Configurer les étiquettes
        ax.set_thetagrids(np.degrees(angles[:-1]), feature_labels[:-1])
        
        plt.title(f"User vs Cluster Profile Comparison", fontsize=16)
        plt.legend(loc="upper right", bbox_to_anchor=(0.1, 0.1))
        
        # Sauvegarder le plot
        vis_id = self._generate_visualization_id("user_cluster_radar", user_id, cluster_id, params)
        file_paths = self._save_visualization(plt, vis_id)
        
        plt.close()
        
        return {
            "id": vis_id,
            "type": "user_cluster_radar",
            "timestamp": datetime.now().isoformat(),
            "files": file_paths,
            "data_summary": {
                "user_id": user_id,
                "cluster_id": cluster_id,
                "features": features,
                "user_values": user_values[:-1],  # Exclure la valeur dupliquée
                "cluster_values": cluster_values[:-1]  # Exclure la valeur dupliquée
            }
        }
    
    def create_behavior_patterns_heatmap(self, user_id: Optional[str] = None, 
                                       cluster_id: Optional[str] = None,
                                       params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crée une heatmap des patterns comportementaux.
        
        Args:
            user_id: Identifiant de l'utilisateur (pour un utilisateur spécifique)
            cluster_id: Identifiant du cluster (pour un cluster spécifique)
            params: Paramètres supplémentaires
            
        Returns:
            Dict contenant les métadonnées et les URLs des visualisations générées
        """
        if not self.pattern_detector:
            return {"error": "Pattern detector module not available"}
        
        # Récupérer les patterns
        patterns = None
        if user_id:
            # Patterns pour un utilisateur spécifique
            patterns = self.pattern_detector.get_user_patterns(user_id)
            if not patterns:
                return {"error": f"No patterns found for user {user_id}"}
        elif cluster_id and self.user_clustering:
            # Patterns agrégés pour un cluster
            cluster_data = self.user_clustering.get_cluster_data(cluster_id)
            if not cluster_data:
                return {"error": f"Cluster data not found for cluster {cluster_id}"}
            
            patterns = cluster_data.get("aggregate_patterns")
            if not patterns:
                return {"error": f"No aggregate patterns found for cluster {cluster_id}"}
        else:
            # Patterns généraux (tous utilisateurs)
            patterns = self.pattern_detector.get_global_patterns()
            if not patterns:
                return {"error": "No global patterns available"}
        
        # Extraire les données pour la heatmap
        if "sequence_patterns" not in patterns:
            return {"error": "No sequence patterns found in the data"}
        
        # Convertir les patterns de séquence en matrice de transition
        event_types = ["page_view", "click", "search", "filter", "download", "apply"]
        transition_matrix = np.zeros((len(event_types), len(event_types)))
        
        for pattern in patterns["sequence_patterns"]:
            sequence = pattern.get("sequence", [])
            for i in range(len(sequence) - 1):
                if sequence[i] in event_types and sequence[i+1] in event_types:
                    from_idx = event_types.index(sequence[i])
                    to_idx = event_types.index(sequence[i+1])
                    transition_matrix[from_idx, to_idx] += pattern.get("count", 1)
        
        # Normaliser la matrice
        row_sums = transition_matrix.sum(axis=1)
        transition_matrix_norm = np.zeros_like(transition_matrix)
        for i in range(len(row_sums)):
            if row_sums[i] > 0:
                transition_matrix_norm[i, :] = transition_matrix[i, :] / row_sums[i]
        
        # Créer la heatmap
        plt.figure(figsize=(self.config["plot_size"]["width"]/100, self.config["plot_size"]["height"]/100), dpi=100)
        
        sns.heatmap(
            transition_matrix_norm, 
            annot=True, 
            cmap="YlGnBu", 
            xticklabels=[e.capitalize() for e in event_types],
            yticklabels=[e.capitalize() for e in event_types],
            linewidths=0.5,
            fmt=".2f"
        )
        
        title = "Behavior Pattern Transition Heatmap"
        if user_id:
            title += f" - User {user_id}"
        elif cluster_id:
            title += f" - Cluster {cluster_id}"
        else:
            title += " - All Users"
            
        plt.title(title, fontsize=16)
        plt.xlabel("Next Event", fontsize=12)
        plt.ylabel("Current Event", fontsize=12)
        
        # Sauvegarder le plot
        vis_id = self._generate_visualization_id("behavior_patterns_heatmap", user_id, cluster_id, params)
        file_paths = self._save_visualization(plt, vis_id)
        
        plt.close()
        
        return {
            "id": vis_id,
            "type": "behavior_patterns_heatmap",
            "timestamp": datetime.now().isoformat(),
            "files": file_paths,
            "data_summary": {
                "event_types": event_types,
                "transition_matrix": transition_matrix.tolist(),
                "normalized_matrix": transition_matrix_norm.tolist()
            }
        }
    
    def create_activity_timeline(self, user_id: Optional[str] = None, 
                               cluster_id: Optional[str] = None,
                               params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crée une timeline d'activité pour un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            cluster_id: Non utilisé pour cette visualisation
            params: Paramètres supplémentaires
            
        Returns:
            Dict contenant les métadonnées et les URLs des visualisations générées
        """
        if not user_id:
            return {"error": "User ID is required for this visualization"}
        
        if not self.pattern_detector:
            return {"error": "Pattern detector module not available"}
        
        # Récupérer les patterns temporels de l'utilisateur
        patterns = self.pattern_detector.get_user_patterns(user_id)
        if not patterns or "time_based_patterns" not in patterns:
            return {"error": f"No time-based patterns found for user {user_id}"}
        
        time_patterns = patterns["time_based_patterns"]
        
        # Extraire la distribution par jour
        if "day_distribution" not in time_patterns:
            return {"error": "Day distribution not found in patterns"}
        
        day_distribution = time_patterns["day_distribution"]
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_values = [day_distribution.get(day, 0) for day in days]
        
        # Extraire la distribution par heure
        if "hour_distribution" not in time_patterns:
            return {"error": "Hour distribution not found in patterns"}
        
        hour_distribution = time_patterns["hour_distribution"]
        hours = [str(h) for h in range(24)]
        hour_values = [hour_distribution.get(hour, 0) for hour in hours]
        
        # Créer le plot
        plt.figure(figsize=(self.config["plot_size"]["width"]/100, self.config["plot_size"]["height"]/100), dpi=100)
        
        # Plot des jours (barres)
        ax1 = plt.subplot(2, 1, 1)
        bars = ax1.bar(days, day_values, color=plt.cm.tab10(0))
        ax1.set_title(f"Activity by Day of Week - User {user_id}", fontsize=14)
        ax1.set_ylabel("Activity Level", fontsize=12)
        ax1.grid(axis="y", alpha=0.3)
        
        # Ajouter des étiquettes de valeur
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01, 
                    f"{height:.2f}", ha="center", va="bottom", fontsize=9)
        
        # Plot des heures (ligne)
        ax2 = plt.subplot(2, 1, 2)
        ax2.plot(hours, hour_values, marker="o", linewidth=2, color=plt.cm.tab10(1))
        ax2.set_title(f"Activity by Hour of Day - User {user_id}", fontsize=14)
        ax2.set_xlabel("Hour of Day", fontsize=12)
        ax2.set_ylabel("Activity Level", fontsize=12)
        ax2.set_xticks(range(0, 24, 2))
        ax2.grid(True, alpha=0.3)
        
        # Mettre en évidence les heures de pointe
        max_hour_value = max(hour_values)
        for i, value in enumerate(hour_values):
            if value > max_hour_value * 0.8:  # Heures avec au moins 80% de l'activité maximale
                ax2.axvspan(i-0.5, i+0.5, alpha=0.2, color=plt.cm.tab10(3))
        
        plt.tight_layout()
        
        # Sauvegarder le plot
        vis_id = self._generate_visualization_id("activity_timeline", user_id, cluster_id, params)
        file_paths = self._save_visualization(plt, vis_id)
        
        plt.close()
        
        return {
            "id": vis_id,
            "type": "activity_timeline",
            "timestamp": datetime.now().isoformat(),
            "files": file_paths,
            "data_summary": {
                "user_id": user_id,
                "day_distribution": dict(zip(days, day_values)),
                "hour_distribution": dict(zip(hours, hour_values)),
                "peak_hours": [int(hours[i]) for i, v in enumerate(hour_values) if v > max_hour_value * 0.8],
                "most_active_day": days[day_values.index(max(day_values))]
            }
        }
    
    def create_preference_radar_chart(self, user_id: Optional[str] = None, 
                                    cluster_id: Optional[str] = None,
                                    params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crée un radar chart des préférences d'un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            cluster_id: Non utilisé pour cette visualisation
            params: Paramètres supplémentaires
            
        Returns:
            Dict contenant les métadonnées et les URLs des visualisations générées
        """
        if not user_id:
            return {"error": "User ID is required for this visualization"}
        
        if not self.preference_calculator:
            return {"error": "Preference calculator module not available"}
        
        # Récupérer les préférences de l'utilisateur
        preferences = self.preference_calculator.get_preferences(user_id)
        if not preferences:
            return {"error": f"No preferences found for user {user_id}"}
        
        # Extraire les valeurs pour les différentes catégories de préférences
        categories = []
        values = []
        
        # Préférences de contenu
        if "content_preferences" in preferences and "top_preferences" in preferences["content_preferences"]:
            top_categories = preferences["content_preferences"]["top_preferences"].get("categories", {})
            if top_categories:
                best_category = max(top_categories.items(), key=lambda x: x[1])
                categories.append("Content")
                values.append(best_category[1])
        
        # Préférences d'interaction
        if "interaction_preferences" in preferences:
            interaction_mode = preferences["interaction_preferences"].get("interaction_mode")
            if interaction_mode:
                categories.append("Interaction")
                # Convertir le mode d'interaction en score (direct=0.8, visual=0.6, explorer=0.4)
                if interaction_mode == "direct":
                    values.append(0.8)
                elif interaction_mode == "visual":
                    values.append(0.6)
                else:
                    values.append(0.4)
        
        # Préférences temporelles
        if "time_preferences" in preferences and "time_scores" in preferences["time_preferences"]:
            time_scores = preferences["time_preferences"]["time_scores"]
            if time_scores:
                categories.append("Time")
                # Utiliser le score de la période préférée
                preferred_time = preferences["time_preferences"].get("preferred_time", "afternoon")
                values.append(time_scores.get(preferred_time, 0.5))
        
        # Préférences de fonctionnalités
        if "feature_preferences" in preferences:
            feature_score = preferences["feature_preferences"].get("sophistication_score")
            if feature_score is not None:
                categories.append("Features")
                values.append(feature_score)
        
        # Engagement global
        if "overall_score" in preferences and "global_score" in preferences["overall_score"]:
            categories.append("Engagement")
            values.append(preferences["overall_score"]["global_score"])
        
        if not categories:
            return {"error": "No preference data available for visualization"}
        
        # Normaliser les valeurs
        max_value = max(values)
        if max_value > 0:
            values = [v / max_value for v in values]
        
        # Créer le radar chart
        plt.figure(figsize=(self.config["plot_size"]["width"]/100, self.config["plot_size"]["height"]/100), dpi=100)
        
        # Configurations du radar chart
        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Fermer le cercle
        
        values += values[:1]  # Fermer le cercle
        categories += categories[:1]  # Fermer le cercle
        
        ax = plt.subplot(111, polar=True)
        
        # Tracer les lignes
        ax.plot(angles, values, 'o-', linewidth=2, label=f"User {user_id}")
        ax.fill(angles, values, alpha=0.25)
        
        # Configurer les étiquettes
        ax.set_thetagrids(np.degrees(angles[:-1]), categories[:-1])
        
        plt.title(f"User Preference Profile - User {user_id}", fontsize=16)
        
        # Sauvegarder le plot
        vis_id = self._generate_visualization_id("preference_radar", user_id, cluster_id, params)
        file_paths = self._save_visualization(plt, vis_id)
        
        plt.close()
        
        return {
            "id": vis_id,
            "type": "preference_radar",
            "timestamp": datetime.now().isoformat(),
            "files": file_paths,
            "data_summary": {
                "user_id": user_id,
                "categories": categories[:-1],  # Exclure la valeur dupliquée
                "values": values[:-1]  # Exclure la valeur dupliquée
            }
        }
    
    def create_user_engagement_bar_chart(self, user_id: Optional[str] = None, 
                                       cluster_id: Optional[str] = None,
                                       params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crée un bar chart de l'engagement d'un utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            cluster_id: Identifiant du cluster (pour comparaison)
            params: Paramètres supplémentaires
            
        Returns:
            Dict contenant les métadonnées et les URLs des visualisations générées
        """
        if not user_id:
            return {"error": "User ID is required for this visualization"}
        
        if not self.profile_manager:
            return {"error": "Profile manager module not available"}
        
        # Récupérer le profil de l'utilisateur
        user_profile = self.profile_manager.get_profile(user_id)
        if not user_profile or "features" not in user_profile:
            return {"error": f"No features found in profile for user {user_id}"}
        
        features = user_profile["features"]
        
        # Récupérer le score d'engagement
        engagement_score = features.get("engagement_score", 0)
        
        # Récupérer les statistiques de session
        session_stats = features.get("session_duration", {})
        avg_duration = session_stats.get("avg_duration_seconds", 0) / 60  # Convertir en minutes
        total_sessions = session_stats.get("total_sessions", 0)
        
        # Récupérer les statistiques de jours actifs
        active_days = features.get("active_days", {})
        active_days_count = active_days.get("active_days_count", 0)
        activity_ratio = active_days.get("activity_ratio", 0)
        
        # Récupérer les statistiques de clics
        click_stats = features.get("click_frequency", {})
        click_count = click_stats.get("click_count", 0)
        clicks_per_session = click_stats.get("clicks_per_session", 0)
        
        # Créer le bar chart
        plt.figure(figsize=(self.config["plot_size"]["width"]/100, self.config["plot_size"]["height"]/100), dpi=100)
        
        metrics = [
            "Engagement Score", 
            "Session Duration (min)", 
            "Total Sessions", 
            "Active Days", 
            "Activity Ratio", 
            "Total Clicks", 
            "Clicks/Session"
        ]
        values = [
            engagement_score, 
            avg_duration, 
            total_sessions, 
            active_days_count, 
            activity_ratio * 100,  # En pourcentage
            click_count, 
            clicks_per_session
        ]
        
        # Normaliser les valeurs pour l'affichage
        max_values = [100, 60, 30, 30, 100, 1000, 50]  # Valeurs maximales typiques
        normalized_values = [min(v / max_v, 1) for v, max_v in zip(values, max_values)]
        
        # Créer les barres
        bars = plt.bar(metrics, normalized_values, color=plt.cm.tab10.colors)
        
        # Ajouter les valeurs réelles comme annotations
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            if i == 1:  # Session Duration
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.02, 
                        f"{value:.1f} min", ha="center", va="bottom", fontsize=9)
            elif i == 4:  # Activity Ratio
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.02, 
                        f"{value:.1f}%", ha="center", va="bottom", fontsize=9)
            else:
                plt.text(bar.get_x() + bar.get_width()/2., height + 0.02, 
                        f"{value:.1f}", ha="center", va="bottom", fontsize=9)
        
        plt.title(f"User Engagement Metrics - User {user_id}", fontsize=16)
        plt.ylabel("Normalized Score", fontsize=12)
        plt.ylim(0, 1.1)  # Laisser de l'espace pour les annotations
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()
        
        # Sauvegarder le plot
        vis_id = self._generate_visualization_id("user_engagement_bar", user_id, cluster_id, params)
        file_paths = self._save_visualization(plt, vis_id)
        
        plt.close()
        
        return {
            "id": vis_id,
            "type": "user_engagement_bar",
            "timestamp": datetime.now().isoformat(),
            "files": file_paths,
            "data_summary": {
                "user_id": user_id,
                "metrics": metrics,
                "values": values,
                "normalized_values": normalized_values
            }
        }
    
    def create_content_preferences_breakdown(self, user_id: Optional[str] = None, 
                                           cluster_id: Optional[str] = None,
                                           params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crée un breakdown des préférences de contenu.
        
        Args:
            user_id: Identifiant de l'utilisateur (pour un utilisateur spécifique)
            cluster_id: Identifiant du cluster (pour un cluster spécifique)
            params: Paramètres supplémentaires
            
        Returns:
            Dict contenant les métadonnées et les URLs des visualisations générées
        """
        # Récupérer les préférences de contenu
        preferences = None
        if user_id and self.preference_calculator:
            # Préférences pour un utilisateur spécifique
            user_preferences = self.preference_calculator.get_preferences(user_id)
            if user_preferences and "content_preferences" in user_preferences:
                preferences = user_preferences["content_preferences"]
        elif cluster_id and self.user_clustering:
            # Préférences agrégées pour un cluster
            cluster_data = self.user_clustering.get_cluster_data(cluster_id)
            if cluster_data and "aggregate_preferences" in cluster_data:
                preferences = cluster_data["aggregate_preferences"].get("content_preferences")
        
        if not preferences:
            return {"error": "No content preferences found"}
        
        # Créer les plots
        plt.figure(figsize=(self.config["plot_size"]["width"]/100, self.config["plot_size"]["height"]/100), dpi=100)
        
        # Plot 1: Catégories préférées (haut gauche)
        ax1 = plt.subplot(2, 2, 1)
        categories = preferences.get("categories", {})
        if categories:
            sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            cat_names, cat_values = zip(*sorted_categories[:5])  # Top 5 catégories
            
            bars = ax1.bar(cat_names, cat_values, color=plt.cm.tab10.colors)
            ax1.set_title("Top Categories", fontsize=12)
            ax1.set_xticklabels([c.capitalize() for c in cat_names], rotation=45, ha="right")
            ax1.grid(axis="y", alpha=0.3)
            
            # Ajouter des étiquettes de valeur
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01, 
                        f"{height:.2f}", ha="center", va="bottom", fontsize=8)
        
        # Plot 2: Localisations préférées (haut droit)
        ax2 = plt.subplot(2, 2, 2)
        locations = preferences.get("locations", {})
        if locations:
            sorted_locations = sorted(locations.items(), key=lambda x: x[1], reverse=True)
            loc_names, loc_values = zip(*sorted_locations[:5])  # Top 5 localisations
            
            bars = ax2.bar(loc_names, loc_values, color=plt.cm.tab10.colors[1:])
            ax2.set_title("Top Locations", fontsize=12)
            ax2.set_xticklabels([l.capitalize() for l in loc_names], rotation=45, ha="right")
            ax2.grid(axis="y", alpha=0.3)
            
            # Ajouter des étiquettes de valeur
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.01, 
                        f"{height:.2f}", ha="center", va="bottom", fontsize=8)
        
        # Plot 3: Types d'emploi préférés (bas gauche)
        ax3 = plt.subplot(2, 2, 3)
        job_types = preferences.get("job_types", {})
        if job_types:
            sorted_job_types = sorted(job_types.items(), key=lambda x: x[1], reverse=True)
            jt_names, jt_values = zip(*sorted_job_types[:5])  # Top 5 types d'emploi
            
            bars = ax3.bar(jt_names, jt_values, color=plt.cm.tab10.colors[2:])
            ax3.set_title("Job Types", fontsize=12)
            ax3.set_xticklabels([jt.replace("_", " ").capitalize() for jt in jt_names], rotation=45, ha="right")
            ax3.grid(axis="y", alpha=0.3)
            
            # Ajouter des étiquettes de valeur
            for bar in bars:
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height + 0.01, 
                        f"{height:.2f}", ha="center", va="bottom", fontsize=8)
        
        # Plot 4: Compétences préférées (bas droit)
        ax4 = plt.subplot(2, 2, 4)
        skills = preferences.get("skills", {})
        if skills:
            sorted_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)
            skill_names, skill_values = zip(*sorted_skills[:5])  # Top 5 compétences
            
            bars = ax4.bar(skill_names, skill_values, color=plt.cm.tab10.colors[3:])
            ax4.set_title("Top Skills", fontsize=12)
            ax4.set_xticklabels([s.capitalize() for s in skill_names], rotation=45, ha="right")
            ax4.grid(axis="y", alpha=0.3)
            
            # Ajouter des étiquettes de valeur
            for bar in bars:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height + 0.01, 
                        f"{height:.2f}", ha="center", va="bottom", fontsize=8)
        
        # Titre global
        title = "Content Preferences Breakdown"
        if user_id:
            title += f" - User {user_id}"
        elif cluster_id:
            title += f" - Cluster {cluster_id}"
        plt.suptitle(title, fontsize=16)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Laisser de l'espace pour le titre
        
        # Sauvegarder le plot
        vis_id = self._generate_visualization_id("content_preferences_breakdown", user_id, cluster_id, params)
        file_paths = self._save_visualization(plt, vis_id)
        
        plt.close()
        
        return {
            "id": vis_id,
            "type": "content_preferences_breakdown",
            "timestamp": datetime.now().isoformat(),
            "files": file_paths,
            "data_summary": {
                "user_id": user_id,
                "cluster_id": cluster_id,
                "top_categories": dict(sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]) if categories else {},
                "top_locations": dict(sorted(locations.items(), key=lambda x: x[1], reverse=True)[:5]) if locations else {},
                "top_job_types": dict(sorted(job_types.items(), key=lambda x: x[1], reverse=True)[:5]) if job_types else {},
                "top_skills": dict(sorted(skills.items(), key=lambda x: x[1], reverse=True)[:5]) if skills else {}
            }
        }
    
    def create_hourly_activity_heatmap(self, user_id: Optional[str] = None, 
                                     cluster_id: Optional[str] = None,
                                     params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crée une heatmap de l'activité par heure et jour de la semaine.
        
        Args:
            user_id: Identifiant de l'utilisateur (pour un utilisateur spécifique)
            cluster_id: Identifiant du cluster (pour un cluster spécifique)
            params: Paramètres supplémentaires
            
        Returns:
            Dict contenant les métadonnées et les URLs des visualisations générées
        """
        # Récupérer les patterns temporels
        time_patterns = None
        if user_id and self.pattern_detector:
            # Patterns pour un utilisateur spécifique
            patterns = self.pattern_detector.get_user_patterns(user_id)
            if patterns and "time_based_patterns" in patterns:
                time_patterns = patterns["time_based_patterns"]
        elif cluster_id and self.user_clustering:
            # Patterns agrégés pour un cluster
            cluster_data = self.user_clustering.get_cluster_data(cluster_id)
            if cluster_data and "aggregate_patterns" in cluster_data:
                patterns = cluster_data["aggregate_patterns"]
                if patterns and "time_based_patterns" in patterns:
                    time_patterns = patterns["time_based_patterns"]
        
        if not time_patterns:
            return {"error": "No time-based patterns found"}
        
        # Extraire les données pour la heatmap
        hourly_activity = time_patterns.get("hourly_activity_by_day")
        if not hourly_activity:
            # Simuler les données si elles ne sont pas disponibles directement
            hour_distribution = time_patterns.get("hour_distribution", {})
            day_distribution = time_patterns.get("day_distribution", {})
            
            days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            hours = [str(h) for h in range(24)]
            
            # Créer une matrice de distribution horaire par jour
            hourly_activity = {}
            for day in days:
                day_factor = day_distribution.get(day, 0)
                hourly_activity[day] = {}
                for hour in hours:
                    hour_factor = hour_distribution.get(hour, 0)
                    # Simuler une distribution en combinant les facteurs jour et heure
                    hourly_activity[day][hour] = day_factor * hour_factor
        
        # Convertir en format compatible avec la heatmap
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        hours = [str(h) for h in range(24)]
        
        activity_matrix = np.zeros((len(days), len(hours)))
        for i, day in enumerate(days):
            day_data = hourly_activity.get(day, {})
            for j, hour in enumerate(hours):
                activity_matrix[i, j] = day_data.get(hour, 0)
        
        # Normaliser la matrice
        if np.max(activity_matrix) > 0:
            activity_matrix = activity_matrix / np.max(activity_matrix)
        
        # Créer la heatmap
        plt.figure(figsize=(self.config["plot_size"]["width"]/100, self.config["plot_size"]["height"]/100), dpi=100)
        
        sns.heatmap(
            activity_matrix, 
            cmap="YlGnBu", 
            xticklabels=hours,
            yticklabels=days,
            linewidths=0.5,
            cbar_kws={"label": "Activity Level (normalized)"}
        )
        
        title = "Hourly Activity Heatmap"
        if user_id:
            title += f" - User {user_id}"
        elif cluster_id:
            title += f" - Cluster {cluster_id}"
            
        plt.title(title, fontsize=16)
        plt.xlabel("Hour of Day", fontsize=12)
        plt.ylabel("Day of Week", fontsize=12)
        
        # Sauvegarder le plot
        vis_id = self._generate_visualization_id("hourly_activity_heatmap", user_id, cluster_id, params)
        file_paths = self._save_visualization(plt, vis_id)
        
        plt.close()
        
        return {
            "id": vis_id,
            "type": "hourly_activity_heatmap",
            "timestamp": datetime.now().isoformat(),
            "files": file_paths,
            "data_summary": {
                "user_id": user_id,
                "cluster_id": cluster_id,
                "days": days,
                "hours": hours,
                "activity_matrix": activity_matrix.tolist()
            }
        }
    
    def create_feature_usage_pie_chart(self, user_id: Optional[str] = None, 
                                     cluster_id: Optional[str] = None,
                                     params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crée un pie chart de l'utilisation des fonctionnalités par l'utilisateur.
        
        Args:
            user_id: Identifiant de l'utilisateur
            cluster_id: Non utilisé pour cette visualisation
            params: Paramètres supplémentaires
            
        Returns:
            Dict contenant les métadonnées et les URLs des visualisations générées
        """
        if not user_id:
            return {"error": "User ID is required for this visualization"}
        
        if not self.preference_calculator:
            return {"error": "Preference calculator module not available"}
        
        # Récupérer les préférences de fonctionnalités
        preferences = self.preference_calculator.get_preferences(user_id)
        if not preferences or "feature_preferences" not in preferences:
            return {"error": f"No feature preferences found for user {user_id}"}
        
        feature_prefs = preferences["feature_preferences"]
        feature_usage = feature_prefs.get("feature_usage", {})
        
        if not feature_usage:
            return {"error": "No feature usage data available"}
        
        # Préparer les données pour le pie chart
        features = list(feature_usage.keys())
        values = list(feature_usage.values())
        
        # Filtrer les fonctionnalités non utilisées
        filtered_features = []
        filtered_values = []
        for feature, value in zip(features, values):
            if value > 0:
                filtered_features.append(feature.replace("_", " ").capitalize())
                filtered_values.append(value)
        
        if not filtered_features:
            return {"error": "No feature usage data available"}
        
        # Créer le pie chart
        plt.figure(figsize=(self.config["plot_size"]["width"]/100, self.config["plot_size"]["height"]/100), dpi=100)
        
        # Utiliser des couleurs attractives
        colors = plt.cm.tab10.colors[:len(filtered_features)]
        
        # Créer le pie chart
        wedges, texts, autotexts = plt.pie(
            filtered_values, 
            labels=filtered_features, 
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            shadow=False,
            wedgeprops={'edgecolor': 'w', 'linewidth': 1}
        )
        
        # Personnaliser les textes
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_weight('bold')
        
        plt.title(f"Feature Usage Distribution - User {user_id}", fontsize=16)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
        # Sauvegarder le plot
        vis_id = self._generate_visualization_id("feature_usage_pie", user_id, cluster_id, params)
        file_paths = self._save_visualization(plt, vis_id)
        
        plt.close()
        
        return {
            "id": vis_id,
            "type": "feature_usage_pie",
            "timestamp": datetime.now().isoformat(),
            "files": file_paths,
            "data_summary": {
                "user_id": user_id,
                "features": filtered_features,
                "values": filtered_values,
                "sophistication_score": feature_prefs.get("sophistication_score", 0)
            }
        }
    
    def create_cluster_comparison_chart(self, user_id: Optional[str] = None, 
                                      cluster_id: Optional[str] = None,
                                      params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Crée un graphique comparatif entre les différents clusters.
        
        Args:
            user_id: Non utilisé pour cette visualisation
            cluster_id: Cluster à mettre en évidence (optionnel)
            params: Paramètres supplémentaires
            
        Returns:
            Dict contenant les métadonnées et les URLs des visualisations générées
        """
        if not self.user_clustering:
            return {"error": "User clustering module not available"}
        
        # Récupérer les données de tous les clusters
        clusters_data = self.user_clustering.get_clusters_data()
        if not clusters_data or "clusters" not in clusters_data:
            return {"error": "No cluster data available"}
        
        clusters = clusters_data["clusters"]
        if not clusters:
            return {"error": "No clusters found"}
        
        # Préparer les données pour la visualisation
        cluster_ids = []
        member_counts = []
        engagement_scores = []
        avg_session_durations = []
        
        for cluster in clusters:
            cluster_id_val = cluster.get("cluster_id")
            cluster_ids.append(cluster_id_val)
            
            # Nombre de membres
            members = cluster.get("members", [])
            member_counts.append(len(members))
            
            # Score d'engagement moyen
            avg_profile = cluster.get("average_profile", {})
            features = avg_profile.get("features", {})
            engagement_scores.append(features.get("engagement_score", 0))
            
            # Durée moyenne de session
            session_stats = features.get("session_duration", {})
            avg_duration = session_stats.get("avg_duration_seconds", 0) / 60  # Convertir en minutes
            avg_session_durations.append(avg_duration)
        
        # Créer le graphique de comparaison
        plt.figure(figsize=(self.config["plot_size"]["width"]/100, self.config["plot_size"]["height"]/100), dpi=100)
        
        # Plot 1: Taille des clusters (barres)
        ax1 = plt.subplot(3, 1, 1)
        bars = ax1.bar(cluster_ids, member_counts, color=plt.cm.tab10.colors)
        
        # Mettre en évidence le cluster spécifié
        if cluster_id:
            for i, c_id in enumerate(cluster_ids):
                if c_id == cluster_id:
                    bars[i].set_color('red')
        
        ax1.set_title("Cluster Size Comparison", fontsize=14)
        ax1.set_ylabel("Number of Users", fontsize=12)
        ax1.grid(axis="y", alpha=0.3)
        
        # Ajouter des étiquettes de valeur
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5, 
                    str(int(height)), ha="center", va="bottom", fontsize=9)
        
        # Plot 2: Score d'engagement moyen (barres)
        ax2 = plt.subplot(3, 1, 2)
        bars = ax2.bar(cluster_ids, engagement_scores, color=plt.cm.tab10.colors[1:])
        
        # Mettre en évidence le cluster spécifié
        if cluster_id:
            for i, c_id in enumerate(cluster_ids):
                if c_id == cluster_id:
                    bars[i].set_color('red')
        
        ax2.set_title("Average Engagement Score Comparison", fontsize=14)
        ax2.set_ylabel("Engagement Score", fontsize=12)
        ax2.grid(axis="y", alpha=0.3)
        
        # Ajouter des étiquettes de valeur
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 2, 
                    f"{height:.1f}", ha="center", va="bottom", fontsize=9)
        
        # Plot 3: Durée moyenne de session (barres)
        ax3 = plt.subplot(3, 1, 3)
        bars = ax3.bar(cluster_ids, avg_session_durations, color=plt.cm.tab10.colors[2:])
        
        # Mettre en évidence le cluster spécifié
        if cluster_id:
            for i, c_id in enumerate(cluster_ids):
                if c_id == cluster_id:
                    bars[i].set_color('red')
        
        ax3.set_title("Average Session Duration Comparison", fontsize=14)
        ax3.set_xlabel("Cluster ID", fontsize=12)
        ax3.set_ylabel("Duration (minutes)", fontsize=12)
        ax3.grid(axis="y", alpha=0.3)
        
        # Ajouter des étiquettes de valeur
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 1, 
                    f"{height:.1f}", ha="center", va="bottom", fontsize=9)
        
        plt.suptitle("Cluster Comparison", fontsize=16)
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Laisser de l'espace pour le titre
        
        # Sauvegarder le plot
        vis_id = self._generate_visualization_id("cluster_comparison", user_id, cluster_id, params)
        file_paths = self._save_visualization(plt, vis_id)
        
        plt.close()
        
        return {
            "id": vis_id,
            "type": "cluster_comparison",
            "timestamp": datetime.now().isoformat(),
            "files": file_paths,
            "data_summary": {
                "highlighted_cluster": cluster_id,
                "cluster_ids": cluster_ids,
                "member_counts": member_counts,
                "engagement_scores": engagement_scores,
                "avg_session_durations": avg_session_durations
            }
        }
    
    def _save_visualization(self, plt, vis_id: str) -> Dict[str, str]:
        """
        Sauvegarde une visualisation dans les formats spécifiés.
        
        Args:
            plt: Instance matplotlib.pyplot
            vis_id: Identifiant de la visualisation
            
        Returns:
            Dict contenant les chemins des fichiers sauvegardés
        """
        file_paths = {}
        
        for format in self.config["export_formats"]:
            file_name = f"{vis_id}.{format}"
            file_path = os.path.join(self.config["output_path"], file_name)
            
            try:
                plt.savefig(file_path, format=format, bbox_inches="tight", dpi=300 if format == "png" else None)
                file_paths[format] = file_path
                logger.info(f"Saved visualization to {file_path}")
            except Exception as e:
                logger.error(f"Error saving visualization to {format}: {str(e)}")
        
        return file_paths
    
    def _generate_visualization_id(self, vis_type: str, user_id: Optional[str] = None, 
                                 cluster_id: Optional[str] = None, 
                                 params: Optional[Dict[str, Any]] = None) -> str:
        """
        Génère un identifiant unique pour une visualisation.
        
        Args:
            vis_type: Type de visualisation
            user_id: Identifiant de l'utilisateur
            cluster_id: Identifiant du cluster
            params: Paramètres supplémentaires
            
        Returns:
            Identifiant unique
        """
        import hashlib
        
        # Créer une chaîne représentant les paramètres de la visualisation
        id_parts = [vis_type]
        
        if user_id:
            id_parts.append(f"user_{user_id}")
        
        if cluster_id:
            id_parts.append(f"cluster_{cluster_id}")
        
        if params:
            for key, value in sorted(params.items()):
                id_parts.append(f"{key}_{value}")
        
        id_str = "_".join(id_parts)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Créer un hash MD5 pour éviter les conflits de noms
        hash_val = hashlib.md5(id_str.encode()).hexdigest()[:8]
        
        return f"{vis_type}_{hash_val}_{timestamp}"
    
    def _check_visualization_cache(self, vis_id: str) -> Optional[Dict[str, Any]]:
        """
        Vérifie si une visualisation existe déjà en cache.
        
        Args:
            vis_id: Identifiant de la visualisation
            
        Returns:
            Dict contenant les métadonnées de la visualisation ou None si non trouvée
        """
        if not self.config["use_cache"]:
            return None
        
        # Vérifier les fichiers de métadonnées dans le dossier de sortie
        metadata_path = os.path.join(self.config["output_path"], f"{vis_id}.json")
        if not os.path.exists(metadata_path):
            return None
        
        try:
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            
            # Vérifier l'âge du cache
            if "timestamp" in metadata:
                cache_time = datetime.fromisoformat(metadata["timestamp"])
                cache_age = datetime.now() - cache_time
                max_age = timedelta(hours=self.config["max_cache_age_hours"])
                
                if cache_age > max_age:
                    logger.info(f"Cache for visualization {vis_id} is too old ({cache_age.total_seconds()/3600:.1f} hours)")
                    return None
            
            # Vérifier que les fichiers existent toujours
            if "files" in metadata:
                for format, file_path in metadata["files"].items():
                    if not os.path.exists(file_path):
                        logger.warning(f"Cache file {file_path} does not exist")
                        return None
            
            logger.info(f"Found cached visualization {vis_id}")
            return metadata
        except Exception as e:
            logger.error(f"Error checking visualization cache: {str(e)}")
            return None
    
    def _save_visualization_metadata(self, vis_id: str, vis_type: str, user_id: Optional[str], 
                                    cluster_id: Optional[str], params: Optional[Dict[str, Any]], 
                                    result: Dict[str, Any]) -> None:
        """
        Sauvegarde les métadonnées d'une visualisation.
        
        Args:
            vis_id: Identifiant de la visualisation
            vis_type: Type de visualisation
            user_id: Identifiant de l'utilisateur
            cluster_id: Identifiant du cluster
            params: Paramètres supplémentaires
            result: Résultat de la génération de la visualisation
        """
        metadata = {
            "id": vis_id,
            "type": vis_type,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "cluster_id": cluster_id,
            "params": params,
            "files": result.get("files", {}),
            "data_summary": result.get("data_summary", {})
        }
        
        metadata_path = os.path.join(self.config["output_path"], f"{vis_id}.json")
        
        try:
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Saved visualization metadata to {metadata_path}")
        except Exception as e:
            logger.error(f"Error saving visualization metadata: {str(e)}")
    
    def _extract_feature_value(self, profile: Dict[str, Any], feature: str) -> float:
        """
        Extrait une valeur de caractéristique d'un profil.
        
        Args:
            profile: Profil utilisateur
            feature: Nom de la caractéristique
            
        Returns:
            Valeur de la caractéristique
        """
        features = profile.get("features", {})
        
        if feature == "engagement_score":
            return features.get(feature, 0)
        elif feature == "session_duration":
            session = features.get(feature, {})
            return session.get("avg_duration_seconds", 0) / 60  # Convertir en minutes
        elif feature == "active_days":
            active_days = features.get(feature, {})
            return active_days.get("active_days_count", 0)
        elif feature == "click_frequency":
            clicks = features.get(feature, {})
            return clicks.get("clicks_per_session", 0)
        elif feature == "search_depth":
            search = features.get(feature, {})
            return search.get("unique_queries_count", 0)
        else:
            return 0
    
    def _normalize_radar_values(self, user_values: List[float], 
                              cluster_values: List[float]) -> Tuple[List[float], List[float]]:
        """
        Normalise les valeurs pour un radar chart.
        
        Args:
            user_values: Valeurs de l'utilisateur
            cluster_values: Valeurs du cluster
            
        Returns:
            Tuple contenant les valeurs normalisées (utilisateur, cluster)
        """
        # Trouver le maximum de chaque caractéristique
        max_values = []
        for i in range(len(user_values)):
            max_val = max(user_values[i], cluster_values[i])
            max_values.append(max_val if max_val > 0 else 1.0)  # Éviter la division par zéro
        
        # Normaliser les valeurs
        norm_user_values = [val / max_val for val, max_val in zip(user_values, max_values)]
        norm_cluster_values = [val / max_val for val, max_val in zip(cluster_values, max_values)]
        
        return norm_user_values, norm_cluster_values
