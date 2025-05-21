import numpy as np
from sklearn.cluster import KMeans
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class UserClusterer:
    """Classe pour regrouper les utilisateurs en clusters basés sur leur comportement."""
    
    def __init__(self, n_clusters=5, random_state=42):
        """
        Initialise le clusterer avec les paramètres spécifiés.
        
        Args:
            n_clusters (int): Nombre de clusters à créer
            random_state (int): Seed pour la reproductibilité
        """
        self.n_clusters = n_clusters
        self.model = KMeans(n_clusters=n_clusters, random_state=random_state)
        self.fitted = False
        
    def prepare_data(self, user_profiles):
        """
        Prépare les données pour le clustering.
        
        Args:
            user_profiles (list): Liste de dictionnaires contenant les profils utilisateur
            
        Returns:
            tuple: (DataFrame des caractéristiques, liste des IDs utilisateur)
        """
        user_ids = []
        features = []
        
        for profile in user_profiles:
            user_ids.append(profile['user_id'])
            # Extraction des caractéristiques importantes pour le clustering
            feature_vector = [
                profile.get('session_count', 0),
                profile.get('avg_session_duration', 0),
                profile.get('job_view_count', 0),
                profile.get('application_count', 0),
                profile.get('profile_completion', 0),
                profile.get('recency_score', 0),
                profile.get('engagement_score', 0),
                # Autres caractéristiques pertinentes
            ]
            features.append(feature_vector)
        
        # Convertir en DataFrame pour faciliter la manipulation
        feature_names = [
            'session_count', 'avg_session_duration', 'job_view_count',
            'application_count', 'profile_completion', 'recency_score',
            'engagement_score'
        ]
        
        df = pd.DataFrame(features, columns=feature_names)
        
        # Normalisation des caractéristiques
        for col in df.columns:
            if df[col].std() > 0:
                df[col] = (df[col] - df[col].mean()) / df[col].std()
        
        return df, user_ids
    
    def fit(self, user_profiles):
        """
        Entraîne le modèle de clustering sur les profils utilisateur.
        
        Args:
            user_profiles (list): Liste de dictionnaires contenant les profils utilisateur
            
        Returns:
            self: Le modèle entraîné
        """
        df, self.user_ids = self.prepare_data(user_profiles)
        self.model.fit(df)
        self.fitted = True
        self.cluster_centers = self.model.cluster_centers_
        
        # Log des résultats
        logger.info(f"Modèle K-means entraîné avec {self.n_clusters} clusters")
        for i, center in enumerate(self.cluster_centers):
            logger.info(f"Centre du cluster {i}: {center}")
            
        return self
    
    def predict(self, user_profiles):
        """
        Prédit les clusters pour les profils utilisateur.
        
        Args:
            user_profiles (list): Liste de dictionnaires contenant les profils utilisateur
            
        Returns:
            dict: Mapping des IDs utilisateur aux labels de cluster
        """
        if not self.fitted:
            raise ValueError("Le modèle doit être entraîné avant de faire des prédictions")
            
        df, user_ids = self.prepare_data(user_profiles)
        cluster_labels = self.model.predict(df)
        
        return {user_id: int(label) for user_id, label in zip(user_ids, cluster_labels)}
    
    def get_cluster_profiles(self):
        """
        Génère des descriptions pour chaque cluster basées sur leurs centres.
        
        Returns:
            list: Liste de dictionnaires décrivant chaque cluster
        """
        if not self.fitted:
            raise ValueError("Le modèle doit être entraîné avant de générer des profils de cluster")
            
        cluster_profiles = []
        feature_names = [
            'session_count', 'avg_session_duration', 'job_view_count',
            'application_count', 'profile_completion', 'recency_score',
            'engagement_score'
        ]
        
        for i, center in enumerate(self.cluster_centers):
            profile = {
                'cluster_id': i,
                'size': (np.array(self.model.labels_) == i).sum(),
                'center': {name: value for name, value in zip(feature_names, center)}
            }
            
            # Détermination des caractéristiques dominantes
            sorted_features = sorted(
                zip(feature_names, center),
                key=lambda x: abs(x[1]),
                reverse=True
            )
            
            # Génération d'une description du cluster
            description = self._generate_cluster_description(sorted_features)
            profile['description'] = description
            
            cluster_profiles.append(profile)
            
        return cluster_profiles
    
    def _generate_cluster_description(self, sorted_features):
        """
        Génère une description textuelle du cluster basée sur ses caractéristiques.
        
        Args:
            sorted_features (list): Liste de tuples (nom_caractéristique, valeur) triée
            
        Returns:
            str: Description du cluster
        """
        top_features = sorted_features[:3]  # Top 3 caractéristiques
        descriptions = []
        
        for feature, value in top_features:
            if value > 1.0:
                descriptions.append(f"très haut niveau de {feature}")
            elif value > 0.5:
                descriptions.append(f"haut niveau de {feature}")
            elif value < -1.0:
                descriptions.append(f"très bas niveau de {feature}")
            elif value < -0.5:
                descriptions.append(f"bas niveau de {feature}")
        
        if descriptions:
            return "Utilisateurs avec " + ", ".join(descriptions)
        else:
            return "Utilisateurs avec des comportements moyens"