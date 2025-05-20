"""
Module de visualisations pour l'analyse comportementale et le profilage utilisateur.

Ce module fournit des visualisations pour les clusters d'utilisateurs et les patterns comportementaux
détectés, à la fois sous forme de graphiques statiques et de tableaux de bord interactifs.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import base64
from io import BytesIO
import tempfile

# Import des composants et de la configuration
from session8.config import CONFIG
from session8.profile_manager import ProfileManager
from session8.user_clustering import UserClustering
from session8.pattern_detector import PatternDetector
from session8.feature_extractor import FeatureExtractor
from session8.preference_calculator import PreferenceCalculator

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class Visualizations:
    """
    Classe pour la génération de visualisations des données de profilage utilisateur.
    """
    
    def __init__(self, profile_manager: Optional[ProfileManager] = None,
                user_clustering: Optional[UserClustering] = None,
                pattern_detector: Optional[PatternDetector] = None,
                feature_extractor: Optional[FeatureExtractor] = None,
                preference_calculator: Optional[PreferenceCalculator] = None,
                config: Dict[str, Any] = None,
                output_path: Optional[str] = None):
        """
        Initialise le module de visualisations.
        
        Args:
            profile_manager: Gestionnaire de profils utilisateurs
            user_clustering: Module de clustering d'utilisateurs
            pattern_detector: Détecteur de patterns comportementaux
            feature_extractor: Extracteur de caractéristiques comportementales
            preference_calculator: Calculateur de préférences
            config: Configuration spécifique (si None, utilise CONFIG["visualization"])
            output_path: Chemin pour sauvegarder les visualisations
        """
        self.profile_manager = profile_manager
        self.user_clustering = user_clustering
        self.pattern_detector = pattern_detector
        self.feature_extractor = feature_extractor
        self.preference_calculator = preference_calculator
        
        self.config = config or CONFIG["visualization"]
        self.output_path = output_path or CONFIG["storage"]["visualizations_path"]
        
        # S'assurer que le répertoire de sortie existe
        os.makedirs(self.output_path, exist_ok=True)
        
        # Configurer le style des visualisations
        self.setup_visualization_style()
        
        logger.info("Visualizations module initialized")
    
    def setup_visualization_style(self) -> None:
        """
        Configure le style global des visualisations.
        """
        # Utiliser le thème par défaut
        theme = self.config["default_theme"]
        if theme == "dark":
            plt.style.use('dark_background')
        else:
            plt.style.use('seaborn-whitegrid')
        
        # Configurer la taille par défaut des figures
        plt.rcParams["figure.figsize"] = (
            self.config["default_plot_size"]["width"] / 100,
            self.config["default_plot_size"]["height"] / 100
        )
        
        # Configurer la police et la taille du texte
        plt.rcParams.update({
            'font.size': 10,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16
        })
    
    def generate_user_clustering_visualization(self, method: str = 'pca', 
                                             cluster_algo: str = 'kmeans',
                                             save_path: Optional[str] = None,
                                             show_plot: bool = False,
                                             return_base64: bool = False) -> Optional[str]:
        """
        Génère une visualisation des clusters d'utilisateurs.
        
        Args:
            method: Méthode de réduction de dimension ('pca', 'tsne')
            cluster_algo: Algorithme de clustering ('kmeans', 'dbscan', 'hierarchical')
            save_path: Chemin pour sauvegarder la visualisation
            show_plot: Si True, affiche le graphique
            return_base64: Si True, retourne l'image encodée en base64
            
        Returns:
            Chemin vers l'image ou chaîne base64 si return_base64=True
        """
        if not self.user_clustering:
            logger.error("User clustering module not available")
            return None
        
        try:
            # Récupérer les données des clusters
            clusters_data = self.user_clustering.get_clusters_data(method=method, algorithm=cluster_algo)
            
            if not clusters_data or 'points' not in clusters_data or not clusters_data['points']:
                logger.warning(f"No cluster data available for {method} with {cluster_algo}")
                return None
            
            # Préparer les données pour la visualisation
            points = np.array(clusters_data['points'])
            labels = np.array(clusters_data['labels'])
            
            # Créer la figure
            plt.figure(figsize=(10, 8))
            
            # Palette de couleurs pour les clusters
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
            palette = self.config["color_schemes"]["categorical"]
            colors = sns.color_palette(palette, n_clusters)
            
            # Tracer les clusters
            unique_labels = set(labels)
            for k, col in zip(unique_labels, colors):
                if k == -1:
                    # Valeurs -1 pour les outliers (DBSCAN)
                    col = [0.7, 0.7, 0.7]  # gris
                
                class_member_mask = (labels == k)
                
                cluster_points = points[class_member_mask]
                plt.scatter(
                    cluster_points[:, 0], cluster_points[:, 1],
                    s=50, c=[col], label=f'Cluster {k}',
                    alpha=0.8, edgecolors='w', linewidths=0.5
                )
            
            # Ajouter les centroïdes si disponibles
            if 'centroids' in clusters_data and clusters_data['centroids']:
                centroids = np.array(clusters_data['centroids'])
                plt.scatter(
                    centroids[:, 0], centroids[:, 1],
                    s=200, c='black', marker='X',
                    alpha=0.8, edgecolors='w', linewidths=1.5,
                    label='Centroids'
                )
            
            plt.title(f'User Clusters using {method.upper()} and {cluster_algo.capitalize()}')
            plt.xlabel(f'Dimension 1')
            plt.ylabel(f'Dimension 2')
            plt.legend(loc='best')
            plt.tight_layout()
            
            # Sauvegarder le graphique
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(
                    self.output_path, 
                    f'user_clusters_{method}_{cluster_algo}_{timestamp}.png'
                )
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"User clustering visualization saved to {save_path}")
            
            # Retourner en base64 si demandé
            if return_base64:
                buffer = BytesIO()
                plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                plt.close()
                return image_base64
            
            # Afficher si demandé
            if show_plot:
                plt.show()
            else:
                plt.close()
            
            return save_path
            
        except Exception as e:
            logger.error(f"Error generating user clustering visualization: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def generate_feature_importance_visualization(self, save_path: Optional[str] = None,
                                               show_plot: bool = False,
                                               return_base64: bool = False,
                                               top_n: int = 15) -> Optional[str]:
        """
        Génère une visualisation de l'importance des caractéristiques.
        
        Args:
            save_path: Chemin pour sauvegarder la visualisation
            show_plot: Si True, affiche le graphique
            return_base64: Si True, retourne l'image encodée en base64
            top_n: Nombre de caractéristiques à afficher
            
        Returns:
            Chemin vers l'image ou chaîne base64 si return_base64=True
        """
        if not self.feature_extractor:
            logger.error("Feature extractor not available")
            return None
        
        try:
            # Récupérer les importances des caractéristiques
            feature_importance = self.feature_extractor.get_feature_importance()
            
            if not feature_importance:
                logger.warning("No feature importance data available")
                return None
            
            # Convertir en DataFrame pour faciliter la manipulation
            df = pd.DataFrame({
                'Feature': list(feature_importance.keys()),
                'Importance': list(feature_importance.values())
            })
            
            # Trier par importance et prendre les N plus importantes
            df = df.sort_values('Importance', ascending=False).head(top_n)
            
            # Créer la figure
            plt.figure(figsize=(10, 8))
            
            # Palette de couleurs
            colors = sns.color_palette(
                self.config["color_schemes"]["sequential"],
                len(df)
            )
            
            # Créer le graphique à barres horizontales
            bars = plt.barh(df['Feature'], df['Importance'], color=colors)
            
            # Ajouter les valeurs sur les barres
            for bar in bars:
                width = bar.get_width()
                plt.text(
                    width + 0.01, bar.get_y() + bar.get_height()/2,
                    f'{width:.4f}', ha='left', va='center'
                )
            
            plt.title('Feature Importance')
            plt.xlabel('Importance')
            plt.ylabel('Feature')
            plt.gca().invert_yaxis()  # Pour que la plus importante soit en haut
            plt.tight_layout()
            
            # Sauvegarder le graphique
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join(
                    self.output_path, 
                    f'feature_importance_{timestamp}.png'
                )
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Feature importance visualization saved to {save_path}")
            
            # Retourner en base64 si demandé
            if return_base64:
                buffer = BytesIO()
                plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
                buffer.seek(0)
                image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                plt.close()
                return image_base64
            
            # Afficher si demandé
            if show_plot:
                plt.show()
            else:
                plt.close()
            
            return save_path
            
        except Exception as e:
            logger.error(f"Error generating feature importance visualization: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def generate_pattern_visualization(self, pattern_type: str = 'sequence',
                                     save_path: Optional[str] = None,
                                     show_plot: bool = False,
                                     return_base64: bool = False,
                                     top_n: int = 10) -> Optional[str]:
        """
        Génère une visualisation des patterns comportementaux.
        
        Args:
            pattern_type: Type de pattern ('sequence', 'temporal', 'recurrent')
            save_path: Chemin pour sauvegarder la visualisation
            show_plot: Si True, affiche le graphique
            return_base64: Si True, retourne l'image encodée en base64
            top_n: Nombre de patterns à afficher
            
        Returns:
            Chemin vers l'image ou chaîne base64 si return_base64=True
        """
        if not self.pattern_detector:
            logger.error("Pattern detector not available")
            return None
        
        try:
            # Récupérer les patterns
            patterns = self.pattern_detector.get_patterns_by_type(pattern_type)
            
            if not patterns:
                logger.warning(f"No {pattern_type} patterns available")
                return None
            
            # Préparer les données selon le type de pattern
            if pattern_type == 'sequence':
                return self._generate_sequence_pattern_visualization(
                    patterns, save_path, show_plot, return_base64, top_n
                )
            elif pattern_type == 'temporal':
                return self._generate_temporal_pattern_visualization(
                    patterns, save_path, show_plot, return_base64
                )
            elif pattern_type == 'recurrent':
                return self._generate_recurrent_pattern_visualization(
                    patterns, save_path, show_plot, return_base64, top_n
                )
            else:
                logger.error(f"Unsupported pattern type: {pattern_type}")
                return None
            
        except Exception as e:
            logger.error(f"Error generating {pattern_type} pattern visualization: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _generate_sequence_pattern_visualization(self, patterns: List[Dict[str, Any]],
                                              save_path: Optional[str] = None,
                                              show_plot: bool = False,
                                              return_base64: bool = False,
                                              top_n: int = 10) -> Optional[str]:
        """
        Génère une visualisation des patterns de séquence.
        """
        # Filtrer et trier les patterns par support
        sorted_patterns = sorted(patterns, key=lambda p: p.get('support', 0), reverse=True)
        top_patterns = sorted_patterns[:top_n]
        
        # Préparer les données pour le graphique
        pattern_labels = []
        pattern_supports = []
        
        for pattern in top_patterns:
            # Formater la séquence comme une chaîne pour l'affichage
            sequence = pattern.get('sequence', [])
            sequence_str = ' → '.join(sequence)
            
            if len(sequence_str) > 40:
                sequence_str = sequence_str[:37] + '...'
            
            pattern_labels.append(sequence_str)
            pattern_supports.append(pattern.get('support', 0))
        
        # Créer la figure
        plt.figure(figsize=(12, 8))
        
        # Palette de couleurs
        colors = sns.color_palette(
            self.config["color_schemes"]["categorical"],
            len(pattern_labels)
        )
        
        # Créer le graphique à barres horizontales
        bars = plt.barh(pattern_labels, pattern_supports, color=colors)
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            width = bar.get_width()
            plt.text(
                width + 0.01, bar.get_y() + bar.get_height()/2,
                f'{width:.4f}', ha='left', va='center'
            )
        
        plt.title('Top Sequence Patterns')
        plt.xlabel('Support')
        plt.ylabel('Sequence')
        plt.gca().invert_yaxis()  # Pour que le pattern le plus supporté soit en haut
        plt.tight_layout()
        
        # Sauvegarder et retourner comme les autres méthodes
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(
                self.output_path, 
                f'sequence_patterns_{timestamp}.png'
            )
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Sequence pattern visualization saved to {save_path}")
        
        # Retourner en base64 si demandé
        if return_base64:
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            return image_base64
        
        # Afficher si demandé
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return save_path
    
    def _generate_temporal_pattern_visualization(self, patterns: List[Dict[str, Any]],
                                              save_path: Optional[str] = None,
                                              show_plot: bool = False,
                                              return_base64: bool = False) -> Optional[str]:
        """
        Génère une visualisation des patterns temporels.
        """
        # Chercher les distributions par heure si disponibles
        hour_distribution = None
        for pattern in patterns:
            if pattern.get('type') == 'hour_distribution':
                hour_distribution = pattern.get('distribution', {})
                break
        
        if not hour_distribution:
            logger.warning("No hourly distribution found in temporal patterns")
            return None
        
        # Convertir en format adapté pour la visualisation
        hours = []
        values = []
        
        for hour in range(24):
            hour_str = str(hour)
            hours.append(hour)
            values.append(hour_distribution.get(hour_str, 0))
        
        # Normaliser les valeurs
        total = sum(values)
        if total > 0:
            values = [v / total for v in values]
        
        # Créer la figure
        plt.figure(figsize=(12, 6))
        
        # Palette de couleurs
        colors = sns.color_palette(
            self.config["color_schemes"]["sequential"],
            24
        )
        
        # Créer le graphique à barres
        plt.bar(hours, values, color=colors, width=0.8)
        
        # Améliorer l'apparence
        plt.title('User Activity by Hour of Day')
        plt.xlabel('Hour of Day')
        plt.ylabel('Activity Proportion')
        plt.xticks(range(0, 24, 2))
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Ajouter des zones pour les périodes de la journée
        plt.axvspan(5, 12, alpha=0.2, color='yellow', label='Morning')
        plt.axvspan(12, 18, alpha=0.2, color='orange', label='Afternoon')
        plt.axvspan(18, 22, alpha=0.2, color='blue', label='Evening')
        plt.axvspan(22, 24, alpha=0.2, color='purple', label='Night')
        plt.axvspan(0, 5, alpha=0.2, color='purple')
        
        plt.legend()
        plt.tight_layout()
        
        # Sauvegarder et retourner comme les autres méthodes
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(
                self.output_path, 
                f'temporal_patterns_{timestamp}.png'
            )
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Temporal pattern visualization saved to {save_path}")
        
        # Retourner en base64 si demandé
        if return_base64:
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            return image_base64
        
        # Afficher si demandé
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return save_path
    
    def _generate_recurrent_pattern_visualization(self, patterns: List[Dict[str, Any]],
                                               save_path: Optional[str] = None,
                                               show_plot: bool = False,
                                               return_base64: bool = False,
                                               top_n: int = 10) -> Optional[str]:
        """
        Génère une visualisation des patterns récurrents.
        """
        # Filtrer et trier les patterns par fréquence
        sorted_patterns = sorted(patterns, key=lambda p: p.get('frequency', 0), reverse=True)
        top_patterns = sorted_patterns[:top_n]
        
        # Préparer les données pour le graphique
        pattern_labels = []
        pattern_frequencies = []
        
        for pattern in top_patterns:
            description = pattern.get('description', 'Unknown Pattern')
            
            if len(description) > 40:
                description = description[:37] + '...'
            
            pattern_labels.append(description)
            pattern_frequencies.append(pattern.get('frequency', 0))
        
        # Créer la figure
        plt.figure(figsize=(12, 8))
        
        # Palette de couleurs
        colors = sns.color_palette(
            self.config["color_schemes"]["categorical"],
            len(pattern_labels)
        )
        
        # Créer le graphique à barres horizontales
        bars = plt.barh(pattern_labels, pattern_frequencies, color=colors)
        
        # Ajouter les valeurs sur les barres
        for bar in bars:
            width = bar.get_width()
            plt.text(
                width + 0.01, bar.get_y() + bar.get_height()/2,
                f'{width:.4f}', ha='left', va='center'
            )
        
        plt.title('Top Recurrent Patterns')
        plt.xlabel('Frequency')
        plt.ylabel('Pattern')
        plt.gca().invert_yaxis()  # Pour que le pattern le plus fréquent soit en haut
        plt.tight_layout()
        
        # Sauvegarder et retourner comme les autres méthodes
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(
                self.output_path, 
                f'recurrent_patterns_{timestamp}.png'
            )
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Recurrent pattern visualization saved to {save_path}")
        
        # Retourner en base64 si demandé
        if return_base64:
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            return image_base64
        
        # Afficher si demandé
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return save_path
    
    def generate_preference_visualization(self, preference_type: str = 'content',
                                       user_id: Optional[str] = None,
                                       save_path: Optional[str] = None,
                                       show_plot: bool = False,
                                       return_base64: bool = False) -> Optional[str]:
        """
        Génère une visualisation des préférences utilisateur.
        
        Args:
            preference_type: Type de préférence ('content', 'interaction', 'time', 'feature')
            user_id: Identifiant de l'utilisateur (si None, utilise des données agrégées)
            save_path: Chemin pour sauvegarder la visualisation
            show_plot: Si True, affiche le graphique
            return_base64: Si True, retourne l'image encodée en base64
            
        Returns:
            Chemin vers l'image ou chaîne base64 si return_base64=True
        """
        if not self.preference_calculator:
            logger.error("Preference calculator not available")
            return None
        
        try:
            # Récupérer les préférences
            if user_id:
                preferences = self.preference_calculator.get_preferences(user_id)
                title_suffix = f" for User {user_id}"
            else:
                # Pour les données agrégées, il faudrait une méthode spécifique
                # Simulons des données agrégées pour l'exemple
                preferences = self._get_aggregate_preferences()
                title_suffix = " (Aggregate)"
            
            if not preferences:
                logger.warning(f"No preference data available for {preference_type}")
                return None
            
            # Créer la visualisation selon le type de préférence
            if preference_type == 'content':
                return self._generate_content_preference_visualization(
                    preferences.get('content_preferences', {}),
                    save_path, show_plot, return_base64, title_suffix
                )
            elif preference_type == 'time':
                return self._generate_time_preference_visualization(
                    preferences.get('time_preferences', {}),
                    save_path, show_plot, return_base64, title_suffix
                )
            elif preference_type == 'interaction':
                return self._generate_interaction_preference_visualization(
                    preferences.get('interaction_preferences', {}),
                    save_path, show_plot, return_base64, title_suffix
                )
            elif preference_type == 'feature':
                return self._generate_feature_preference_visualization(
                    preferences.get('feature_preferences', {}),
                    save_path, show_plot, return_base64, title_suffix
                )
            else:
                logger.error(f"Unsupported preference type: {preference_type}")
                return None
            
        except Exception as e:
            logger.error(f"Error generating preference visualization: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _get_aggregate_preferences(self) -> Dict[str, Any]:
        """
        Récupère des préférences agrégées pour tous les utilisateurs.
        Dans une implémentation réelle, cela viendrait de l'agrégation des données réelles.
        """
        # Simulation de données agrégées
        return {
            'content_preferences': {
                'categories': {
                    'engineering': 0.35,
                    'marketing': 0.25,
                    'sales': 0.15,
                    'design': 0.15,
                    'finance': 0.1
                },
                'locations': {
                    'paris': 0.45,
                    'lyon': 0.2,
                    'marseille': 0.15,
                    'bordeaux': 0.1,
                    'toulouse': 0.1
                }
            },
            'time_preferences': {
                'hour_distribution': {str(h): max(0.01, 0.1 * np.sin(h / 24 * 2 * np.pi) + 0.1) for h in range(24)},
                'day_distribution': {
                    'Monday': 0.15,
                    'Tuesday': 0.2,
                    'Wednesday': 0.25,
                    'Thursday': 0.2,
                    'Friday': 0.15,
                    'Saturday': 0.03,
                    'Sunday': 0.02
                }
            },
            'interaction_preferences': {
                'element_types': {
                    'button': 0.4,
                    'link': 0.35,
                    'card': 0.25
                }
            },
            'feature_preferences': {
                'feature_usage': {
                    'search': 0.3,
                    'filter': 0.25,
                    'download': 0.2,
                    'apply': 0.1,
                    'recommendations': 0.1,
                    'notifications': 0.03,
                    'messaging': 0.01,
                    'profile': 0.01
                }
            }
        }
    
    def _generate_content_preference_visualization(self, content_prefs: Dict[str, Any],
                                               save_path: Optional[str] = None,
                                               show_plot: bool = False,
                                               return_base64: bool = False,
                                               title_suffix: str = "") -> Optional[str]:
        """
        Génère une visualisation des préférences de contenu.
        """
        if not content_prefs:
            logger.warning("No content preference data available")
            return None
        
        # Créer une figure avec deux subplots côte à côte
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # 1. Graphique des catégories
        categories = content_prefs.get('categories', {})
        if categories:
            labels = list(categories.keys())
            sizes = list(categories.values())
            
            colors = plt.cm.tab10(np.arange(len(labels)) % 10)
            
            ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                   shadow=True, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            ax1.set_title(f'Category Preferences{title_suffix}')
        
        # 2. Graphique des localisations
        locations = content_prefs.get('locations', {})
        if locations:
            loc_labels = list(locations.keys())
            loc_sizes = list(locations.values())
            
            colors = plt.cm.Paired(np.arange(len(loc_labels)) % 12)
            
            ax2.pie(loc_sizes, labels=loc_labels, colors=colors, autopct='%1.1f%%',
                  shadow=True, startangle=90)
            ax2.axis('equal')
            ax2.set_title(f'Location Preferences{title_suffix}')
        
        plt.tight_layout()
        
        # Sauvegarder et retourner comme les autres méthodes
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(
                self.output_path, 
                f'content_preferences_{timestamp}.png'
            )
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Content preference visualization saved to {save_path}")
        
        # Retourner en base64 si demandé
        if return_base64:
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            return image_base64
        
        # Afficher si demandé
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return save_path
    
    def _generate_time_preference_visualization(self, time_prefs: Dict[str, Any],
                                           save_path: Optional[str] = None,
                                           show_plot: bool = False,
                                           return_base64: bool = False,
                                           title_suffix: str = "") -> Optional[str]:
        """
        Génère une visualisation des préférences temporelles.
        """
        if not time_prefs:
            logger.warning("No time preference data available")
            return None
        
        # Créer une figure avec deux subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 1. Distribution par heure
        hour_distribution = time_prefs.get('hour_distribution', {})
        if hour_distribution:
            hours = [int(h) for h in sorted(hour_distribution.keys(), key=int)]
            values = [hour_distribution[str(h)] for h in hours]
            
            # Créer un heatmap circulaire représentant les 24 heures
            N = 24
            angles = np.linspace(0, 2*np.pi, N, endpoint=False)
            values = np.array(values)
            width = 2*np.pi / N
            
            ax1.bar(angles, values, width=width, bottom=0.0)
            
            # Configurer l'axe pour qu'il soit circulaire
            ax1.set_xticks(angles)
            ax1.set_xticklabels([f"{h}h" for h in hours])
            ax1.set_theta_zero_location("N")  # Minuit en haut
            ax1.set_theta_direction(-1)  # Sens horaire
            
            ax1.set_title(f'Activity by Hour of Day{title_suffix}')
        
        # 2. Distribution par jour
        day_distribution = time_prefs.get('day_distribution', {})
        if day_distribution:
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            day_values = [day_distribution.get(day, 0) for day in days]
            
            # Convertir en deux catégories: semaine et weekend
            weekday_val = sum(day_values[:5])
            weekend_val = sum(day_values[5:])
            
            # Barres pour la semaine vs. weekend
            ax2.bar(['Weekdays', 'Weekend'], [weekday_val, weekend_val], 
                   color=['skyblue', 'salmon'])
            
            for i, day in enumerate(days):
                ax2.text(0 if i < 5 else 1, 
                        sum(day_values[:i]) + day_values[i]/2 if i < 5 else 
                        weekday_val + (day_values[i-5]/2 if i == 5 else sum(day_values[5:i]) + day_values[i]/2), 
                        day, ha='center')
            
            ax2.set_title(f'Activity by Day Type{title_suffix}')
            ax2.set_ylabel('Activity Proportion')
        
        plt.tight_layout()
        
        # Sauvegarder et retourner comme les autres méthodes
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(
                self.output_path, 
                f'time_preferences_{timestamp}.png'
            )
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Time preference visualization saved to {save_path}")
        
        # Retourner en base64 si demandé
        if return_base64:
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            return image_base64
        
        # Afficher si demandé
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return save_path
    
    def _generate_interaction_preference_visualization(self, interaction_prefs: Dict[str, Any],
                                                   save_path: Optional[str] = None,
                                                   show_plot: bool = False,
                                                   return_base64: bool = False,
                                                   title_suffix: str = "") -> Optional[str]:
        """
        Génère une visualisation des préférences d'interaction.
        """
        if not interaction_prefs:
            logger.warning("No interaction preference data available")
            return None
        
        # Créer la figure
        plt.figure(figsize=(10, 6))
        
        # Graphique pour les types d'éléments
        element_types = interaction_prefs.get('element_types', {})
        if element_types:
            labels = list(element_types.keys())
            sizes = list(element_types.values())
            
            colors = plt.cm.Accent(np.arange(len(labels)) % 8)
            
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                   shadow=True, startangle=90, explode=[0.1 if i == 0 else 0 for i in range(len(labels))])
            plt.axis('equal')
            plt.title(f'Interaction Element Type Preferences{title_suffix}')
        
        plt.tight_layout()
        
        # Sauvegarder et retourner comme les autres méthodes
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(
                self.output_path, 
                f'interaction_preferences_{timestamp}.png'
            )
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Interaction preference visualization saved to {save_path}")
        
        # Retourner en base64 si demandé
        if return_base64:
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            return image_base64
        
        # Afficher si demandé
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return save_path
    
    def _generate_feature_preference_visualization(self, feature_prefs: Dict[str, Any],
                                               save_path: Optional[str] = None,
                                               show_plot: bool = False,
                                               return_base64: bool = False,
                                               title_suffix: str = "") -> Optional[str]:
        """
        Génère une visualisation des préférences de fonctionnalités.
        """
        if not feature_prefs:
            logger.warning("No feature preference data available")
            return None
        
        # Créer la figure
        plt.figure(figsize=(12, 8))
        
        # Utilisation des fonctionnalités
        feature_usage = feature_prefs.get('feature_usage', {})
        if feature_usage:
            labels = list(feature_usage.keys())
            sizes = list(feature_usage.values())
            
            # Trier par utilisation décroissante
            sorted_indices = np.argsort(sizes)[::-1]
            sorted_labels = [labels[i] for i in sorted_indices]
            sorted_sizes = [sizes[i] for i in sorted_indices]
            
            # Palette de couleurs
            colors = plt.cm.viridis(np.linspace(0, 1, len(sorted_labels)))
            
            # Créer le graphique à barres horizontales
            bars = plt.barh(sorted_labels, sorted_sizes, color=colors)
            
            # Ajouter les valeurs sur les barres
            for bar in bars:
                width = bar.get_width()
                plt.text(
                    width + 0.01, bar.get_y() + bar.get_height()/2,
                    f'{width:.2f}', ha='left', va='center'
                )
            
            plt.title(f'Feature Usage Preferences{title_suffix}')
            plt.xlabel('Usage Proportion')
            plt.ylabel('Feature')
            plt.xlim(0, max(sorted_sizes) * 1.2)  # Laisser de l'espace pour les étiquettes
            plt.grid(axis='x', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        
        # Sauvegarder et retourner comme les autres méthodes
        if save_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(
                self.output_path, 
                f'feature_preferences_{timestamp}.png'
            )
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Feature preference visualization saved to {save_path}")
        
        # Retourner en base64 si demandé
        if return_base64:
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close()
            return image_base64
        
        # Afficher si demandé
        if show_plot:
            plt.show()
        else:
            plt.close()
        
        return save_path
    
    def generate_dashboard(self, output_path: Optional[str] = None) -> Optional[str]:
        """
        Génère un tableau de bord HTML combinant plusieurs visualisations.
        
        Args:
            output_path: Chemin pour sauvegarder le tableau de bord
            
        Returns:
            Chemin vers le fichier HTML généré
        """
        try:
            # Générer toutes les visualisations nécessaires en base64
            visualizations = {}
            
            # Visualisation des clusters
            visualizations['clusters'] = self.generate_user_clustering_visualization(
                return_base64=True
            ) or ""
            
            # Visualisation des patterns
            for pattern_type in ['sequence', 'temporal', 'recurrent']:
                visualizations[f'pattern_{pattern_type}'] = self.generate_pattern_visualization(
                    pattern_type=pattern_type,
                    return_base64=True
                ) or ""
            
            # Visualisation des préférences
            for pref_type in ['content', 'time', 'interaction', 'feature']:
                visualizations[f'preference_{pref_type}'] = self.generate_preference_visualization(
                    preference_type=pref_type,
                    return_base64=True
                ) or ""
            
            # Visualisation de l'importance des caractéristiques
            visualizations['feature_importance'] = self.generate_feature_importance_visualization(
                return_base64=True
            ) or ""
            
            # Créer le fichier HTML
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(
                    self.output_path, 
                    f'dashboard_{timestamp}.html'
                )
            
            # Générer le contenu HTML
            html_content = self._generate_dashboard_html(visualizations)
            
            # Sauvegarder le fichier
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Dashboard generated and saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating dashboard: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def _generate_dashboard_html(self, visualizations: Dict[str, str]) -> str:
        """
        Génère le contenu HTML pour le tableau de bord.
        
        Args:
            visualizations: Dictionnaire des visualisations en base64
            
        Returns:
            Contenu HTML du tableau de bord
        """
        # Modèle HTML basique pour le tableau de bord
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>User Profiling Dashboard</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                header {
                    background-color: #333;
                    color: white;
                    padding: 20px;
                    text-align: center;
                }
                .dashboard-section {
                    background-color: white;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                    padding: 20px;
                }
                .dashboard-section h2 {
                    border-bottom: 1px solid #eee;
                    padding-bottom: 10px;
                    color: #333;
                }
                .visualization {
                    text-align: center;
                    margin: 20px 0;
                }
                .visualization img {
                    max-width: 100%;
                    height: auto;
                }
                .row {
                    display: flex;
                    flex-wrap: wrap;
                    margin: 0 -10px;
                }
                .col {
                    flex: 1;
                    padding: 0 10px;
                    min-width: 300px;
                }
                footer {
                    background-color: #333;
                    color: white;
                    text-align: center;
                    padding: 10px;
                    font-size: 0.8em;
                }
                @media (max-width: 768px) {
                    .col {
                        flex: 100%;
                    }
                }
            </style>
        </head>
        <body>
            <header>
                <h1>User Profiling Dashboard</h1>
                <p>Behavioral Analysis and User Profiling</p>
            </header>
            
            <div class="container">
                <!-- User Clusters Section -->
                <section class="dashboard-section">
                    <h2>User Clusters</h2>
                    <div class="visualization">
                        <img src="data:image/png;base64,{clusters}" alt="User Clusters">
                    </div>
                </section>
                
                <!-- Patterns Section -->
                <section class="dashboard-section">
                    <h2>Behavioral Patterns</h2>
                    <div class="row">
                        <div class="col">
                            <h3>Sequence Patterns</h3>
                            <div class="visualization">
                                <img src="data:image/png;base64,{pattern_sequence}" alt="Sequence Patterns">
                            </div>
                        </div>
                        <div class="col">
                            <h3>Temporal Patterns</h3>
                            <div class="visualization">
                                <img src="data:image/png;base64,{pattern_temporal}" alt="Temporal Patterns">
                            </div>
                        </div>
                    </div>
                    <div class="visualization">
                        <h3>Recurrent Patterns</h3>
                        <img src="data:image/png;base64,{pattern_recurrent}" alt="Recurrent Patterns">
                    </div>
                </section>
                
                <!-- Preferences Section -->
                <section class="dashboard-section">
                    <h2>User Preferences</h2>
                    <div class="row">
                        <div class="col">
                            <h3>Content Preferences</h3>
                            <div class="visualization">
                                <img src="data:image/png;base64,{preference_content}" alt="Content Preferences">
                            </div>
                        </div>
                        <div class="col">
                            <h3>Time Preferences</h3>
                            <div class="visualization">
                                <img src="data:image/png;base64,{preference_time}" alt="Time Preferences">
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col">
                            <h3>Interaction Preferences</h3>
                            <div class="visualization">
                                <img src="data:image/png;base64,{preference_interaction}" alt="Interaction Preferences">
                            </div>
                        </div>
                        <div class="col">
                            <h3>Feature Preferences</h3>
                            <div class="visualization">
                                <img src="data:image/png;base64,{preference_feature}" alt="Feature Preferences">
                            </div>
                        </div>
                    </div>
                </section>
                
                <!-- Feature Importance Section -->
                <section class="dashboard-section">
                    <h2>Feature Importance</h2>
                    <div class="visualization">
                        <img src="data:image/png;base64,{feature_importance}" alt="Feature Importance">
                    </div>
                </section>
            </div>
            
            <footer>
                <p>Generated on {timestamp} | Commitment Project - Session 8</p>
            </footer>
        </body>
        </html>
        """
        
        # Remplacer les placeholders par les visuels
        html_content = html_template.format(
            clusters=visualizations.get('clusters', ''),
            pattern_sequence=visualizations.get('pattern_sequence', ''),
            pattern_temporal=visualizations.get('pattern_temporal', ''),
            pattern_recurrent=visualizations.get('pattern_recurrent', ''),
            preference_content=visualizations.get('preference_content', ''),
            preference_time=visualizations.get('preference_time', ''),
            preference_interaction=visualizations.get('preference_interaction', ''),
            preference_feature=visualizations.get('preference_feature', ''),
            feature_importance=visualizations.get('feature_importance', ''),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return html_content
