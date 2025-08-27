"""
Module de clustering d'utilisateurs.

Ce module est responsable du regroupement des utilisateurs en clusters
basés sur leurs caractéristiques comportementales similaires.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import logging
from typing import Dict, List, Any, Optional, Tuple
import json
import os
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class UserClustering:
    """
    Module de clustering d'utilisateurs qui regroupe les utilisateurs
    en fonction de leurs caractéristiques comportementales.
    """
    
    def __init__(self, profile_manager=None, storage_path: str = "./clusters", 
                 n_clusters: int = 5, random_state: int = 42):
        """
        Initialise le module de clustering.
        
        Args:
            profile_manager: Gestionnaire de profils utilisateurs
            storage_path: Chemin vers le dossier de stockage des clusters
            n_clusters: Nombre de clusters pour KMeans
            random_state: Graine aléatoire pour la reproductibilité
        """
        self.profile_manager = profile_manager
        self.storage_path = storage_path
        self.n_clusters = n_clusters
        self.random_state = random_state
        
        # Créer le dossier de stockage s'il n'existe pas
        os.makedirs(storage_path, exist_ok=True)
        
        # Liste des caractéristiques numériques à utiliser pour le clustering
        self.numeric_features = [
            "engagement_score",
            "session_duration.avg_duration_seconds",
            "session_duration.total_sessions",
            "active_days.active_days_count",
            "active_days.activity_ratio",
            "click_frequency.click_count",
            "click_frequency.clicks_per_session",
            "search_depth.search_count",
            "search_depth.unique_queries_count",
            "search_depth.avg_results_count",
            "content_preference.downloads_count",
            "content_preference.applications_count"
        ]
        
        # Modèles de clustering
        self.kmeans_model = None
        self.dbscan_model = None
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=3)  # Pour la visualisation
        
        # Métadonnées des clusters
        self.cluster_metadata = {
            "last_updated": None,
            "n_clusters": n_clusters,
            "cluster_sizes": {},
            "cluster_centers": {},
            "cluster_descriptions": {}
        }
        
        logger.info(f"UserClustering initialized with {n_clusters} clusters")
    
    def prepare_data(self, profiles: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Prépare les données pour le clustering en extrayant les caractéristiques pertinentes.
        
        Args:
            profiles: Liste des profils utilisateurs
            
        Returns:
            DataFrame avec les caractéristiques numériques pour le clustering
        """
        if not profiles:
            logger.warning("No profiles provided for clustering")
            return pd.DataFrame()
        
        logger.info(f"Preparing data for clustering from {len(profiles)} profiles")
        
        # Extraire les caractéristiques de chaque profil
        data = []
        for profile in profiles:
            user_id = profile.get("user_id")
            if not user_id:
                continue
                
            features = profile.get("behavioral_features", {})
            if not features:
                continue
            
            # Créer un dictionnaire pour stocker les caractéristiques de cet utilisateur
            user_data = {"user_id": user_id}
            
            # Extraire les caractéristiques numériques simples
            for feature in ["engagement_score"]:
                if feature in features:
                    user_data[feature] = features[feature]
            
            # Extraire les caractéristiques numériques imbriquées
            for feature in ["session_duration", "active_days", "click_frequency", "search_depth", "content_preference"]:
                if feature in features:
                    for subfeature, value in features[feature].items():
                        if isinstance(value, (int, float)):
                            user_data[f"{feature}.{subfeature}"] = value
            
            data.append(user_data)
        
        if not data:
            logger.warning("No valid data extracted from profiles")
            return pd.DataFrame()
        
        # Créer un DataFrame
        df = pd.DataFrame(data)
        df.set_index("user_id", inplace=True)
        
        # Garder uniquement les colonnes numériques qui existent dans les données
        numeric_features = [f for f in self.numeric_features if f in df.columns]
        if not numeric_features:
            logger.warning("No valid numeric features found in profiles")
            return pd.DataFrame()
        
        # Sélectionner les colonnes numériques et remplacer les valeurs manquantes
        df_numeric = df[numeric_features].copy()
        df_numeric.fillna(0, inplace=True)
        
        logger.info(f"Prepared data with {len(df_numeric)} users and {len(numeric_features)} features")
        return df_numeric
    
    def update_clusters(self, profiles: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Met à jour les clusters en utilisant les derniers profils utilisateurs.
        
        Args:
            profiles: Liste des profils utilisateurs (optionnel, sinon utilise le profile_manager)
            
        Returns:
            Métadonnées des clusters mis à jour
        """
        # Si aucun profil n'est fourni, essayer de les récupérer via le profile_manager
        if not profiles and self.profile_manager:
            profiles = self.profile_manager.get_all_profiles()
        
        if not profiles:
            logger.warning("No profiles available for clustering")
            return self.cluster_metadata
        
        logger.info(f"Updating clusters with {len(profiles)} profiles")
        
        # Préparer les données
        df = self.prepare_data(profiles)
        if df.empty:
            logger.warning("No valid data for clustering")
            return self.cluster_metadata
        
        # Mettre à l'échelle les données
        scaled_data = self.scaler.fit_transform(df)
        
        # KMeans clustering
        self.kmeans_model = KMeans(
            n_clusters=self.n_clusters,
            random_state=self.random_state,
            n_init=10
        )
        kmeans_labels = self.kmeans_model.fit_predict(scaled_data)
        
        # DBSCAN clustering (détection d'anomalies)
        self.dbscan_model = DBSCAN(eps=0.5, min_samples=5)
        dbscan_labels = self.dbscan_model.fit_predict(scaled_data)
        
        # Ajouter les étiquettes des clusters aux données
        df["kmeans_cluster"] = kmeans_labels
        df["dbscan_cluster"] = dbscan_labels
        
        # Mettre à jour les métadonnées des clusters
        self.cluster_metadata["last_updated"] = datetime.now().isoformat()
        self.cluster_metadata["n_clusters"] = self.n_clusters
        
        # Taille des clusters KMeans
        kmeans_sizes = df["kmeans_cluster"].value_counts().to_dict()
        self.cluster_metadata["cluster_sizes"]["kmeans"] = {
            str(k): v for k, v in kmeans_sizes.items()
        }
        
        # Taille des clusters DBSCAN
        dbscan_sizes = df["dbscan_cluster"].value_counts().to_dict()
        self.cluster_metadata["cluster_sizes"]["dbscan"] = {
            str(k): v for k, v in dbscan_sizes.items()
        }
        
        # Centres des clusters KMeans
        cluster_centers = self.kmeans_model.cluster_centers_
        feature_names = df.columns.tolist()[:-2]  # Exclure les colonnes de cluster
        
        centers_dict = {}
        for i, center in enumerate(cluster_centers):
            centers_dict[str(i)] = dict(zip(feature_names, center.tolist()))
        
        self.cluster_metadata["cluster_centers"] = centers_dict
        
        # Calculer les moyennes des caractéristiques pour chaque cluster
        cluster_descriptions = {}
        for cluster_id in range(self.n_clusters):
            cluster_data = df[df["kmeans_cluster"] == cluster_id]
            if not cluster_data.empty:
                description = {}
                
                # Calculer les moyennes des caractéristiques numériques
                for feature in feature_names:
                    description[feature] = cluster_data[feature].mean()
                
                # Définir un nom abstrait et une description pour le cluster
                description["name"] = self._generate_cluster_name(cluster_id, description)
                description["description"] = self._generate_cluster_description(description)
                
                # Ajouter au dictionnaire des descriptions
                cluster_descriptions[str(cluster_id)] = description
        
        self.cluster_metadata["cluster_descriptions"] = cluster_descriptions
        
        # Sauvegarder les clusters et métadonnées
        self._save_clusters(df)
        self._save_metadata()
        
        logger.info(f"Clusters updated with {len(df)} users")
        return self.cluster_metadata
    
    def get_user_cluster(self, user_id: str) -> Dict[str, Any]:
        """
        Récupère le cluster d'un utilisateur spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Informations sur le cluster de l'utilisateur
        """
        # Vérifier si les clusters existent
        clusters_path = os.path.join(self.storage_path, "user_clusters.json")
        if not os.path.exists(clusters_path):
            logger.warning("No clusters available, run update_clusters first")
            return {}
        
        # Charger les données des clusters
        try:
            with open(clusters_path, 'r') as file:
                clusters_data = json.load(file)
        except Exception as e:
            logger.error(f"Failed to load clusters data: {str(e)}")
            return {}
        
        # Récupérer les informations de cluster pour l'utilisateur
        user_cluster = clusters_data.get(user_id, {})
        
        if not user_cluster:
            logger.warning(f"No cluster information found for user {user_id}")
            return {}
        
        # Enrichir avec les métadonnées du cluster
        kmeans_cluster_id = user_cluster.get("kmeans_cluster")
        if kmeans_cluster_id is not None:
            cluster_id_str = str(kmeans_cluster_id)
            user_cluster["description"] = self.cluster_metadata.get("cluster_descriptions", {}).get(cluster_id_str, {})
            user_cluster["size"] = self.cluster_metadata.get("cluster_sizes", {}).get("kmeans", {}).get(cluster_id_str, 0)
        
        logger.info(f"Retrieved cluster information for user {user_id}")
        return user_cluster
    
    def get_similar_users(self, user_id: str, limit: int = 10) -> List[str]:
        """
        Récupère les utilisateurs similaires à un utilisateur spécifique.
        
        Args:
            user_id: Identifiant de l'utilisateur
            limit: Nombre maximum d'utilisateurs similaires à retourner
            
        Returns:
            Liste des utilisateurs similaires
        """
        # Récupérer le cluster de l'utilisateur
        user_cluster_info = self.get_user_cluster(user_id)
        
        if not user_cluster_info:
            logger.warning(f"No cluster information found for user {user_id}")
            return []
        
        kmeans_cluster_id = user_cluster_info.get("kmeans_cluster")
        if kmeans_cluster_id is None:
            logger.warning(f"No KMeans cluster found for user {user_id}")
            return []
        
        # Charger les données des clusters
        clusters_path = os.path.join(self.storage_path, "user_clusters.json")
        if not os.path.exists(clusters_path):
            logger.warning("No clusters available, run update_clusters first")
            return []
        
        try:
            with open(clusters_path, 'r') as file:
                clusters_data = json.load(file)
        except Exception as e:
            logger.error(f"Failed to load clusters data: {str(e)}")
            return []
        
        # Trouver les utilisateurs dans le même cluster
        similar_users = []
        
        for other_id, other_cluster in clusters_data.items():
            if other_id == user_id:
                continue
                
            if other_cluster.get("kmeans_cluster") == kmeans_cluster_id:
                similar_users.append(other_id)
                
                if len(similar_users) >= limit:
                    break
        
        logger.info(f"Found {len(similar_users)} similar users for user {user_id}")
        return similar_users
    
    def get_cluster_stats(self, cluster_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Récupère les statistiques d'un cluster spécifique ou de tous les clusters.
        
        Args:
            cluster_id: Identifiant du cluster (optionnel, sinon retourne tous les clusters)
            
        Returns:
            Statistiques du cluster ou de tous les clusters
        """
        if self.cluster_metadata["last_updated"] is None:
            logger.warning("No clusters available, run update_clusters first")
            return {}
            
        if cluster_id is not None:
            cluster_id_str = str(cluster_id)
            
            # Vérifier si le cluster existe
            if cluster_id_str not in self.cluster_metadata.get("cluster_descriptions", {}):
                logger.warning(f"Cluster {cluster_id} not found")
                return {}
            
            # Récupérer les statistiques du cluster spécifique
            stats = {
                "size": self.cluster_metadata.get("cluster_sizes", {}).get("kmeans", {}).get(cluster_id_str, 0),
                "center": self.cluster_metadata.get("cluster_centers", {}).get(cluster_id_str, {}),
                "description": self.cluster_metadata.get("cluster_descriptions", {}).get(cluster_id_str, {})
            }
            
            logger.info(f"Retrieved statistics for cluster {cluster_id}")
            return stats
        else:
            # Récupérer les statistiques de tous les clusters
            stats = {
                "last_updated": self.cluster_metadata["last_updated"],
                "n_clusters": self.cluster_metadata["n_clusters"],
                "sizes": self.cluster_metadata.get("cluster_sizes", {}).get("kmeans", {}),
                "descriptions": self.cluster_metadata.get("cluster_descriptions", {})
            }
            
            logger.info("Retrieved statistics for all clusters")
            return stats
    
    def classify_user(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classifie un utilisateur dans un cluster existant.
        
        Args:
            features: Caractéristiques comportementales de l'utilisateur
            
        Returns:
            Informations sur le cluster attribué
        """
        if self.kmeans_model is None:
            logger.warning("No clusters model available, run update_clusters first")
            return {}
        
        # Préparer les données
        user_data = {}
        
        # Extraire les caractéristiques numériques simples
        for feature in ["engagement_score"]:
            if feature in features:
                user_data[feature] = features[feature]
        
        # Extraire les caractéristiques numériques imbriquées
        for feature in ["session_duration", "active_days", "click_frequency", "search_depth", "content_preference"]:
            if feature in features:
                for subfeature, value in features[feature].items():
                    if isinstance(value, (int, float)):
                        user_data[f"{feature}.{subfeature}"] = value
        
        # Créer un DataFrame
        user_df = pd.DataFrame([user_data])
        
        # Vérifier les caractéristiques nécessaires
        missing_features = [f for f in self.numeric_features if f not in user_df.columns]
        for feature in missing_features:
            user_df[feature] = 0
            
        # Sélectionner les caractéristiques dans le bon ordre
        user_df = user_df[self.numeric_features]
        
        # Mettre à l'échelle les données
        scaled_data = self.scaler.transform(user_df)
        
        # Prédire le cluster KMeans
        kmeans_cluster = int(self.kmeans_model.predict(scaled_data)[0])
        
        # Prédire le cluster DBSCAN (anomalie ou non)
        dbscan_cluster = self.dbscan_model.fit_predict(scaled_data)[0]
        
        # Récupérer les informations sur le cluster
        cluster_id_str = str(kmeans_cluster)
        cluster_info = {
            "kmeans_cluster": kmeans_cluster,
            "dbscan_cluster": int(dbscan_cluster),
            "is_anomaly": dbscan_cluster == -1,
            "description": self.cluster_metadata.get("cluster_descriptions", {}).get(cluster_id_str, {}),
            "size": self.cluster_metadata.get("cluster_sizes", {}).get("kmeans", {}).get(cluster_id_str, 0)
        }
        
        logger.info(f"Classified user into cluster {kmeans_cluster}")
        return cluster_info
    
    def _generate_cluster_name(self, cluster_id: int, features: Dict[str, float]) -> str:
        """
        Génère un nom abstrait pour un cluster basé sur ses caractéristiques.
        
        Args:
            cluster_id: Identifiant du cluster
            features: Caractéristiques moyennes du cluster
            
        Returns:
            Nom du cluster
        """
        # Caractéristiques clés à considérer
        engagement = features.get("engagement_score", 0)
        session_duration = features.get("session_duration.avg_duration_seconds", 0)
        activity_ratio = features.get("active_days.activity_ratio", 0)
        click_count = features.get("click_frequency.click_count", 0)
        search_count = features.get("search_depth.search_count", 0)
        
        # Définir des seuils pour caractériser les clusters
        if engagement > 70 and activity_ratio > 0.7:
            return "Super Utilisateurs"
        elif engagement > 50 and search_count > 10:
            return "Chercheurs Actifs"
        elif session_duration > 300 and click_count > 20:
            return "Explorateurs Engagés"
        elif engagement < 30 and activity_ratio < 0.3:
            return "Visiteurs Occasionnels"
        elif search_count < 3 and click_count < 10:
            return "Observateurs Passifs"
        else:
            return f"Groupe {cluster_id + 1}"
    
    def _generate_cluster_description(self, features: Dict[str, float]) -> str:
        """
        Génère une description pour un cluster basé sur ses caractéristiques.
        
        Args:
            features: Caractéristiques moyennes du cluster
            
        Returns:
            Description du cluster
        """
        # Caractéristiques clés à considérer
        engagement = features.get("engagement_score", 0)
        session_duration = features.get("session_duration.avg_duration_seconds", 0)
        activity_ratio = features.get("active_days.activity_ratio", 0)
        click_count = features.get("click_frequency.click_count", 0)
        search_count = features.get("search_depth.search_count", 0)
        downloads = features.get("content_preference.downloads_count", 0)
        applications = features.get("content_preference.applications_count", 0)
        
        # Générer une description basée sur les caractéristiques
        descriptions = []
        
        if engagement > 70:
            descriptions.append("Utilisateurs très engagés sur la plateforme")
        elif engagement > 50:
            descriptions.append("Utilisateurs moyennement engagés")
        else:
            descriptions.append("Utilisateurs peu engagés")
            
        if session_duration > 600:
            descriptions.append("sessions très longues")
        elif session_duration > 300:
            descriptions.append("sessions de durée moyenne")
        else:
            descriptions.append("sessions courtes")
            
        if activity_ratio > 0.7:
            descriptions.append("visitent régulièrement le site")
        elif activity_ratio > 0.3:
            descriptions.append("visitent occasionnellement le site")
        else:
            descriptions.append("visitent rarement le site")
            
        if click_count > 30:
            descriptions.append("très interactifs")
        elif click_count > 15:
            descriptions.append("modérément interactifs")
        else:
            descriptions.append("peu interactifs")
            
        if search_count > 10:
            descriptions.append("effectuent beaucoup de recherches")
        elif search_count > 5:
            descriptions.append("effectuent quelques recherches")
        else:
            descriptions.append("effectuent peu de recherches")
            
        if downloads > 5 or applications > 2:
            descriptions.append("montrent un fort intérêt pour le contenu")
        elif downloads > 2 or applications > 0:
            descriptions.append("montrent un intérêt modéré pour le contenu")
        else:
            descriptions.append("montrent peu d'intérêt pour le contenu")
        
        # Combiner les descriptions
        return "Ces " + descriptions[0] + " avec des " + descriptions[1] + ", " + descriptions[2] + ", " + descriptions[3] + ", " + descriptions[4] + " et " + descriptions[5] + "."
    
    def _save_clusters(self, df: pd.DataFrame) -> None:
        """
        Sauvegarde les données des clusters.
        
        Args:
            df: DataFrame avec les données et les étiquettes de cluster
        """
        # Créer un dictionnaire des clusters par utilisateur
        user_clusters = {}
        
        for user_id, row in df.iterrows():
            user_clusters[user_id] = {
                "kmeans_cluster": int(row["kmeans_cluster"]),
                "dbscan_cluster": int(row["dbscan_cluster"]),
                "is_anomaly": row["dbscan_cluster"] == -1
            }
        
        # Sauvegarder dans un fichier JSON
        clusters_path = os.path.join(self.storage_path, "user_clusters.json")
        try:
            with open(clusters_path, 'w') as file:
                json.dump(user_clusters, file, indent=2)
            logger.info(f"Saved clusters data to {clusters_path}")
        except Exception as e:
            logger.error(f"Failed to save clusters data: {str(e)}")
    
    def _save_metadata(self) -> None:
        """
        Sauvegarde les métadonnées des clusters.
        """
        metadata_path = os.path.join(self.storage_path, "cluster_metadata.json")
        try:
            with open(metadata_path, 'w') as file:
                json.dump(self.cluster_metadata, file, indent=2)
            logger.info(f"Saved cluster metadata to {metadata_path}")
        except Exception as e:
            logger.error(f"Failed to save cluster metadata: {str(e)}")
    
    def load_models(self) -> bool:
        """
        Charge les modèles et métadonnées des clusters précédemment sauvegardés.
        
        Returns:
            True si le chargement a réussi, False sinon
        """
        metadata_path = os.path.join(self.storage_path, "cluster_metadata.json")
        if not os.path.exists(metadata_path):
            logger.warning("No cluster metadata found, run update_clusters first")
            return False
        
        try:
            with open(metadata_path, 'r') as file:
                self.cluster_metadata = json.load(file)
            logger.info(f"Loaded cluster metadata from {metadata_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load cluster metadata: {str(e)}")
            return False
