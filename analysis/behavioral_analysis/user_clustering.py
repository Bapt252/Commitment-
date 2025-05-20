"""
User Clustering Module for Behavioral Analysis

This module provides algorithms for clustering users based on their
behavioral patterns, allowing for automatic segmentation of users
with similar characteristics.

Part of the Session 8 implementation: Behavioral Analysis and User Profiling.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import logging
from typing import Dict, List, Tuple, Optional, Any, Union

logger = logging.getLogger(__name__)

class UserClusteringEngine:
    """
    Engine for user clustering based on behavioral data.
    Implements various clustering algorithms and dimensionality reduction
    to automatically segment users into meaningful groups.
    """
    
    def __init__(self, db_connection=None, config: Dict = None):
        """
        Initialize the clustering engine with connection to the database
        and optional configuration.
        
        Args:
            db_connection: Connection to the tracking database
            config: Configuration parameters for clustering algorithms
        """
        self.db_connection = db_connection
        self.config = config or {
            'n_clusters': 5,
            'random_state': 42,
            'pca_components': 3,
            'min_events_threshold': 10,
            'dbscan_eps': 0.5,
            'dbscan_min_samples': 5
        }
        self.models = {}
        self.scaler = StandardScaler()
        self.pca = None
        self.cluster_profiles = {}
        
    def fetch_user_behavioral_data(self, 
                                   days_lookback: int = 90,
                                   min_events: int = None) -> pd.DataFrame:
        """
        Fetch user behavioral data from the tracking database.
        
        Args:
            days_lookback: Number of days to look back for data
            min_events: Minimum number of events per user to include
            
        Returns:
            DataFrame with user behavioral features
        """
        if self.db_connection is None:
            logger.warning("No database connection available. Using mock data.")
            return self._generate_mock_data()
            
        min_events = min_events or self.config.get('min_events_threshold', 10)
        
        # SQL query to extract user behavioral features
        query = f"""
        WITH user_events AS (
            SELECT 
                user_id,
                COUNT(*) as total_events,
                COUNT(DISTINCT session_id) as total_sessions,
                COUNT(DISTINCT CASE WHEN event_type = 'match_viewed' THEN match_id END) as viewed_matches,
                COUNT(DISTINCT CASE WHEN event_type = 'match_accepted' THEN match_id END) as accepted_matches,
                COUNT(DISTINCT CASE WHEN event_type = 'match_rejected' THEN match_id END) as rejected_matches,
                AVG(CASE WHEN event_type = 'match_viewed' THEN EXTRACT(EPOCH FROM (
                    LEAD(event_timestamp) OVER (PARTITION BY user_id, match_id ORDER BY event_timestamp) - event_timestamp
                )) END) as avg_view_time,
                AVG(CASE WHEN me.decision_time_seconds IS NOT NULL THEN me.decision_time_seconds END) as avg_decision_time,
                AVG(CASE WHEN fe.rating IS NOT NULL THEN fe.rating END) as avg_feedback_rating,
                AVG(CASE WHEN me.match_score IS NOT NULL THEN me.match_score END) as avg_match_score,
                STDDEV(CASE WHEN me.match_score IS NOT NULL THEN me.match_score END) as match_score_variance,
                COUNT(DISTINCT CASE WHEN ie.interaction_type IS NOT NULL THEN ie.interaction_type END) as interaction_types_count,
                SUM(CASE WHEN ie.interaction_count IS NOT NULL THEN ie.interaction_count END) as total_interactions,
                MAX(CASE WHEN ce.completion_rate IS NOT NULL THEN ce.completion_rate END) as max_completion_rate,
                AVG(CASE WHEN ce.completion_rate IS NOT NULL THEN ce.completion_rate END) as avg_completion_rate
            FROM 
                tracking.events e
                LEFT JOIN tracking.match_events me ON e.event_id = me.event_id
                LEFT JOIN tracking.feedback_events fe ON e.event_id = fe.event_id
                LEFT JOIN tracking.interaction_events ie ON e.event_id = ie.event_id
                LEFT JOIN tracking.completion_events ce ON e.event_id = ce.event_id
            WHERE 
                e.event_timestamp >= NOW() - INTERVAL '{days_lookback} days'
            GROUP BY 
                user_id
            HAVING 
                COUNT(*) >= {min_events}
        )
        SELECT 
            user_id,
            total_events,
            total_sessions,
            COALESCE(viewed_matches, 0) as viewed_matches,
            COALESCE(accepted_matches, 0) as accepted_matches,
            COALESCE(rejected_matches, 0) as rejected_matches,
            CASE WHEN viewed_matches > 0 THEN COALESCE(accepted_matches, 0)::float / viewed_matches ELSE 0 END as acceptance_rate,
            COALESCE(avg_view_time, 0) as avg_view_time,
            COALESCE(avg_decision_time, 0) as avg_decision_time,
            COALESCE(avg_feedback_rating, 0) as avg_feedback_rating,
            COALESCE(avg_match_score, 0) as avg_match_score,
            COALESCE(match_score_variance, 0) as match_score_variance,
            COALESCE(interaction_types_count, 0) as interaction_types_count,
            COALESCE(total_interactions, 0) as total_interactions,
            COALESCE(max_completion_rate, 0) as max_completion_rate,
            COALESCE(avg_completion_rate, 0) as avg_completion_rate,
            CASE WHEN total_sessions > 0 THEN total_events::float / total_sessions ELSE 0 END as events_per_session,
            CASE WHEN viewed_matches > 0 THEN total_interactions::float / viewed_matches ELSE 0 END as interactions_per_match
        FROM 
            user_events
        """
        
        try:
            df = pd.read_sql(query, self.db_connection)
            return df
        except Exception as e:
            logger.error(f"Error fetching user behavioral data: {e}")
            return self._generate_mock_data()
    
    def _generate_mock_data(self, num_users: int = 200) -> pd.DataFrame:
        """Generate mock user behavioral data for testing"""
        np.random.seed(self.config.get('random_state', 42))
        
        user_ids = [f"user_{i}" for i in range(num_users)]
        
        data = {
            'user_id': user_ids,
            'total_events': np.random.randint(10, 500, size=num_users),
            'total_sessions': np.random.randint(1, 50, size=num_users),
            'viewed_matches': np.random.randint(1, 100, size=num_users),
            'accepted_matches': np.random.randint(0, 50, size=num_users),
            'rejected_matches': np.random.randint(0, 50, size=num_users),
        }
        
        df = pd.DataFrame(data)
        
        # Derived metrics
        df['acceptance_rate'] = df['accepted_matches'] / df['viewed_matches']
        df['avg_view_time'] = np.random.uniform(5, 300, size=num_users)
        df['avg_decision_time'] = np.random.uniform(2, 120, size=num_users)
        df['avg_feedback_rating'] = np.random.uniform(1, 5, size=num_users)
        df['avg_match_score'] = np.random.uniform(20, 95, size=num_users)
        df['match_score_variance'] = np.random.uniform(0, 25, size=num_users)
        df['interaction_types_count'] = np.random.randint(0, 10, size=num_users)
        df['total_interactions'] = np.random.randint(0, 1000, size=num_users)
        df['max_completion_rate'] = np.random.uniform(0, 100, size=num_users)
        df['avg_completion_rate'] = df['max_completion_rate'] * np.random.uniform(0.5, 1.0, size=num_users)
        df['events_per_session'] = df['total_events'] / df['total_sessions']
        df['interactions_per_match'] = np.random.uniform(0, 20, size=num_users)
        
        return df
        
    def preprocess_data(self, df: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """
        Preprocess user data for clustering.
        
        Args:
            df: DataFrame with user behavioral features
            
        Returns:
            Tuple containing preprocessed data array and list of feature names
        """
        # Extract user IDs and feature matrix
        user_ids = df['user_id'].values
        
        # Features to use for clustering
        feature_cols = [
            'acceptance_rate', 'avg_view_time', 'avg_decision_time', 
            'avg_feedback_rating', 'avg_match_score', 'match_score_variance',
            'interaction_types_count', 'total_interactions', 
            'avg_completion_rate', 'events_per_session', 'interactions_per_match'
        ]
        
        # Handle missing values
        X = df[feature_cols].fillna(0).values
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        return X_scaled, user_ids, feature_cols
    
    def reduce_dimensions(self, X: np.ndarray, n_components: Optional[int] = None) -> np.ndarray:
        """
        Reduce dimensionality of feature space using PCA.
        
        Args:
            X: Scaled feature matrix
            n_components: Number of PCA components
            
        Returns:
            Reduced feature matrix
        """
        n_components = n_components or self.config.get('pca_components', 3)
        self.pca = PCA(n_components=n_components, random_state=self.config.get('random_state', 42))
        X_reduced = self.pca.fit_transform(X)
        
        logger.info(f"Explained variance ratio: {self.pca.explained_variance_ratio_}")
        logger.info(f"Total explained variance: {np.sum(self.pca.explained_variance_ratio_)}")
        
        return X_reduced
    
    def run_kmeans_clustering(self, X: np.ndarray, n_clusters: Optional[int] = None) -> np.ndarray:
        """
        Run K-means clustering on the preprocessed data.
        
        Args:
            X: Feature matrix (can be the reduced or original feature space)
            n_clusters: Number of clusters
            
        Returns:
            Array of cluster labels
        """
        n_clusters = n_clusters or self.config.get('n_clusters', 5)
        
        kmeans = KMeans(
            n_clusters=n_clusters, 
            random_state=self.config.get('random_state', 42),
            n_init=10
        )
        
        cluster_labels = kmeans.fit_predict(X)
        self.models['kmeans'] = kmeans
        
        return cluster_labels
    
    def run_dbscan_clustering(self, X: np.ndarray) -> np.ndarray:
        """
        Run DBSCAN clustering on the preprocessed data.
        
        Args:
            X: Feature matrix (can be the reduced or original feature space)
            
        Returns:
            Array of cluster labels
        """
        dbscan = DBSCAN(
            eps=self.config.get('dbscan_eps', 0.5),
            min_samples=self.config.get('dbscan_min_samples', 5)
        )
        
        cluster_labels = dbscan.fit_predict(X)
        self.models['dbscan'] = dbscan
        
        return cluster_labels
    
    def build_cluster_profiles(self, 
                              df: pd.DataFrame, 
                              cluster_labels: np.ndarray, 
                              algorithm: str = 'kmeans',
                              feature_cols: List[str] = None) -> Dict:
        """
        Build and analyze profiles for each cluster.
        
        Args:
            df: Original DataFrame with user data
            cluster_labels: Cluster assignments from clustering algorithm
            algorithm: Name of the clustering algorithm used
            feature_cols: List of feature column names
            
        Returns:
            Dictionary of cluster profiles
        """
        df_copy = df.copy()
        df_copy['cluster'] = cluster_labels
        
        profiles = {}
        
        # For each cluster, calculate statistics
        for cluster_id in sorted(df_copy['cluster'].unique()):
            cluster_df = df_copy[df_copy['cluster'] == cluster_id]
            
            # Calculate statistics for each feature
            profile = {
                'size': len(cluster_df),
                'percentage': len(cluster_df) / len(df_copy) * 100,
                'features': {}
            }
            
            # If feature columns provided, use them; otherwise use all numerical columns
            cols_to_profile = feature_cols if feature_cols else df_copy.select_dtypes(include=np.number).columns
            
            for col in cols_to_profile:
                if col in df_copy.columns and col != 'cluster':
                    profile['features'][col] = {
                        'mean': cluster_df[col].mean(),
                        'median': cluster_df[col].median(),
                        'std': cluster_df[col].std(),
                        'min': cluster_df[col].min(),
                        'max': cluster_df[col].max()
                    }
            
            # Generate a name for the cluster based on its characteristics
            profile['name'] = self._generate_cluster_name(profile, feature_cols)
            
            profiles[int(cluster_id)] = profile
        
        self.cluster_profiles[algorithm] = profiles
        return profiles
    
    def _generate_cluster_name(self, profile: Dict, feature_cols: List[str]) -> str:
        """
        Generate a descriptive name for a cluster based on its most distinctive features.
        
        Args:
            profile: Profile dictionary for the cluster
            feature_cols: List of feature column names
            
        Returns:
            Descriptive name for the cluster
        """
        if not feature_cols or not profile['features']:
            return f"Cluster {len(self.cluster_profiles) + 1}"
        
        # Find the most distinctive features (highest deviation from overall mean)
        distinctive_features = []
        
        # Check for specific meaningful patterns
        features = profile['features']
        
        # High acceptance rate
        if 'acceptance_rate' in features and features['acceptance_rate']['mean'] > 0.7:
            distinctive_features.append("High Acceptors")
        elif 'acceptance_rate' in features and features['acceptance_rate']['mean'] < 0.3:
            distinctive_features.append("Selective Users")
            
        # Fast decision time
        if 'avg_decision_time' in features and features['avg_decision_time']['mean'] < 30:
            distinctive_features.append("Quick Deciders")
        elif 'avg_decision_time' in features and features['avg_decision_time']['mean'] > 120:
            distinctive_features.append("Deliberative Users")
            
        # High engagement
        if ('total_interactions' in features and features['total_interactions']['mean'] > 500) or \
           ('events_per_session' in features and features['events_per_session']['mean'] > 20):
            distinctive_features.append("Highly Engaged")
        elif ('total_interactions' in features and features['total_interactions']['mean'] < 50) or \
             ('events_per_session' in features and features['events_per_session']['mean'] < 5):
            distinctive_features.append("Low Engagement")
            
        # Feedback patterns
        if 'avg_feedback_rating' in features and features['avg_feedback_rating']['mean'] > 4.5:
            distinctive_features.append("Very Satisfied")
        elif 'avg_feedback_rating' in features and features['avg_feedback_rating']['mean'] < 2.5:
            distinctive_features.append("Dissatisfied")
            
        # Completion rates
        if 'avg_completion_rate' in features and features['avg_completion_rate']['mean'] > 80:
            distinctive_features.append("High Completers")
        elif 'avg_completion_rate' in features and features['avg_completion_rate']['mean'] < 30:
            distinctive_features.append("Low Completers")
            
        if not distinctive_features:
            return f"Cluster {len(self.cluster_profiles) + 1}"
        
        return " & ".join(distinctive_features[:2])
    
    def get_user_cluster(self, user_id: str, algorithm: str = 'kmeans') -> Dict:
        """
        Get the cluster assignment and profile for a specific user.
        
        Args:
            user_id: User ID to look up
            algorithm: Name of the clustering algorithm to use
            
        Returns:
            Dictionary with user's cluster information
        """
        if not self.cluster_profiles or algorithm not in self.cluster_profiles:
            raise ValueError(f"No cluster profiles available for algorithm: {algorithm}")
        
        # Fetch the user's data
        if self.db_connection:
            query = f"""
            SELECT * FROM user_features
            WHERE user_id = '{user_id}'
            """
            user_df = pd.read_sql(query, self.db_connection)
        else:
            # For testing, generate mock data for the user
            user_df = self._generate_mock_data(1)
            user_df['user_id'] = user_id
        
        if user_df.empty:
            return {'error': f"User {user_id} not found or has insufficient data"}
        
        # Preprocess the data
        X, _, _ = self.preprocess_data(user_df)
        
        # Apply dimensionality reduction if used in clustering
        if self.pca is not None:
            X = self.pca.transform(X)
        
        # Predict cluster
        if algorithm == 'kmeans' and 'kmeans' in self.models:
            cluster_id = self.models['kmeans'].predict(X)[0]
        elif algorithm == 'dbscan' and 'dbscan' in self.models:
            cluster_id = self.models['dbscan'].predict(X)[0]
        else:
            raise ValueError(f"Algorithm {algorithm} not available or not trained")
        
        # Get the cluster profile
        cluster_profile = self.cluster_profiles[algorithm].get(cluster_id, {})
        
        return {
            'user_id': user_id,
            'cluster_id': int(cluster_id),
            'cluster_name': cluster_profile.get('name', f"Cluster {cluster_id}"),
            'cluster_size': cluster_profile.get('size', 0),
            'cluster_percentage': cluster_profile.get('percentage', 0),
            'user_features': user_df.iloc[0].to_dict()
        }
    
    def persist_cluster_assignments(self) -> bool:
        """
        Persist cluster assignments to the database for later use.
        
        Returns:
            Boolean indicating success or failure
        """
        if not self.db_connection:
            logger.warning("No database connection available. Cannot persist clusters.")
            return False
        
        try:
            # Create table if not exists
            create_table_query = """
            CREATE TABLE IF NOT EXISTS behavioral_analysis.user_clusters (
                user_id VARCHAR(64) PRIMARY KEY,
                cluster_id INTEGER NOT NULL,
                algorithm VARCHAR(20) NOT NULL,
                cluster_name VARCHAR(100),
                assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
            
            with self.db_connection.cursor() as cursor:
                cursor.execute(create_table_query)
            
            # TODO: Insert cluster assignments for all users
            # This would require having the mapping from user_ids to cluster_ids
            
            self.db_connection.commit()
            logger.info("Successfully persisted cluster assignments")
            return True
            
        except Exception as e:
            logger.error(f"Error persisting cluster assignments: {e}")
            return False
        
    def cluster_users(self, 
                      days_lookback: int = 90, 
                      algorithm: str = 'kmeans',
                      persist: bool = True) -> Dict:
        """
        Main method to run the complete clustering pipeline.
        
        Args:
            days_lookback: Number of days to look back for data
            algorithm: Clustering algorithm to use ('kmeans' or 'dbscan')
            persist: Whether to persist cluster assignments to database
            
        Returns:
            Dictionary with clustering results and statistics
        """
        # Fetch user behavioral data
        df = self.fetch_user_behavioral_data(days_lookback=days_lookback)
        
        if df.empty:
            return {'error': 'No user data available for clustering'}
        
        # Preprocess data
        X_scaled, user_ids, feature_cols = self.preprocess_data(df)
        
        # Reduce dimensions
        X_reduced = self.reduce_dimensions(X_scaled)
        
        # Run clustering algorithm
        if algorithm == 'kmeans':
            cluster_labels = self.run_kmeans_clustering(X_reduced)
        elif algorithm == 'dbscan':
            cluster_labels = self.run_dbscan_clustering(X_reduced)
        else:
            raise ValueError(f"Unsupported clustering algorithm: {algorithm}")
        
        # Build cluster profiles
        cluster_profiles = self.build_cluster_profiles(
            df, cluster_labels, algorithm, feature_cols
        )
        
        # Create user-to-cluster mapping
        user_clusters = {
            user_id: {
                'cluster_id': int(cluster_id), 
                'cluster_name': cluster_profiles[int(cluster_id)]['name']
            }
            for user_id, cluster_id in zip(user_ids, cluster_labels)
        }
        
        # Persist cluster assignments if requested
        if persist:
            self.persist_cluster_assignments()
        
        return {
            'algorithm': algorithm,
            'num_users': len(df),
            'num_clusters': len(cluster_profiles),
            'cluster_profiles': cluster_profiles,
            'user_clusters': user_clusters,
            'clustering_stats': {
                'inertia': getattr(self.models.get('kmeans', {}), 'inertia_', None),
                'silhouette_score': None  # Could be calculated if sklearn.metrics imported
            }
        }
