"""
Behavioral Analysis Module - Session 8
-------------------------------------
This module implements behavioral analysis tools for the Commitment project.
It processes user tracking data to extract behavioral patterns and create user profiles.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.stats import gaussian_kde

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection
DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/commitment')
engine = create_engine(DB_URL)

class BehavioralAnalyzer:
    """Main class for behavioral analysis of user data."""
    
    def __init__(self, lookback_days=30):
        """
        Initialize the behavioral analyzer.
        
        Args:
            lookback_days (int): Number of days to look back for analysis
        """
        self.lookback_days = lookback_days
        self.engine = engine
        
    def get_tracking_data(self, start_date=None, end_date=None):
        """
        Retrieve tracking data for analysis.
        
        Args:
            start_date (datetime): Start date for data retrieval
            end_date (datetime): End date for data retrieval
            
        Returns:
            pd.DataFrame: DataFrame containing tracking events
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=self.lookback_days)
        if not end_date:
            end_date = datetime.now()
            
        query = """
        SELECT 
            e.event_id,
            e.user_id,
            e.event_type,
            e.event_data,
            e.context,
            e.timestamp,
            e.session_id
        FROM 
            tracking_events e
        WHERE 
            e.timestamp BETWEEN :start_date AND :end_date
        ORDER BY 
            e.timestamp
        """
        
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        try:
            df = pd.read_sql(query, self.engine, params=params)
            logger.info(f"Retrieved {len(df)} tracking events for analysis")
            return df
        except Exception as e:
            logger.error(f"Error retrieving tracking data: {e}")
            raise
            
    def calculate_user_metrics(self, df):
        """
        Calculate basic user metrics from tracking data.
        
        Args:
            df (pd.DataFrame): DataFrame containing tracking events
            
        Returns:
            pd.DataFrame: DataFrame with user metrics
        """
        if df.empty:
            logger.warning("No tracking data available for metrics calculation")
            return pd.DataFrame()
            
        # Group events by user
        user_groups = df.groupby('user_id')
        
        # Calculate metrics
        metrics = []
        for user_id, group in user_groups:
            # Session analysis
            sessions = group.groupby('session_id')
            session_durations = []
            
            for session_id, session_data in sessions:
                if len(session_data) > 1:
                    # Calculate session duration in minutes
                    start_time = session_data['timestamp'].min()
                    end_time = session_data['timestamp'].max()
                    duration = (end_time - start_time).total_seconds() / 60
                    session_durations.append(duration)
            
            # Active hours analysis
            hour_counts = group['timestamp'].dt.hour.value_counts().sort_index()
            total_events = len(group)
            
            # Normalize to create a distribution
            hour_distribution = hour_counts / total_events if total_events > 0 else hour_counts * 0
            
            # Group hours into time periods
            morning = hour_distribution.loc[6:11].sum() if 6 in hour_distribution.index else 0
            afternoon = hour_distribution.loc[12:17].sum() if 12 in hour_distribution.index else 0
            evening = hour_distribution.loc[18:23].sum() if 18 in hour_distribution.index else 0
            night = hour_distribution.loc[[0,1,2,3,4,5]].sum() if 0 in hour_distribution.index else 0
            
            active_hours = {
                'morning': float(morning),
                'afternoon': float(afternoon),
                'evening': float(evening),
                'night': float(night)
            }
            
            # Calculate average metrics
            avg_session_duration = np.mean(session_durations) if session_durations else 0
            days_span = (group['timestamp'].max() - group['timestamp'].min()).days + 1
            interaction_frequency = len(group) / days_span if days_span > 0 else 0
            
            # Event type distribution
            event_counts = group['event_type'].value_counts()
            total_events = len(group)
            event_distribution = {
                event_type: float(count / total_events)
                for event_type, count in event_counts.items()
            }
            
            metrics.append({
                'user_id': user_id,
                'event_count': len(group),
                'session_count': len(sessions),
                'avg_session_duration': avg_session_duration,
                'interaction_frequency': interaction_frequency,
                'active_hours': json.dumps(active_hours),
                'event_distribution': json.dumps(event_distribution),
                'last_active': group['timestamp'].max()
            })
            
        return pd.DataFrame(metrics)
        
    def run_user_clustering(self, user_metrics, n_clusters=5):
        """
        Cluster users based on behavioral metrics.
        
        Args:
            user_metrics (pd.DataFrame): DataFrame with user metrics
            n_clusters (int): Number of clusters for KMeans
            
        Returns:
            pd.DataFrame: DataFrame with user metrics and cluster assignments
        """
        if user_metrics.empty or len(user_metrics) < n_clusters:
            logger.warning("Not enough data for clustering")
            return user_metrics
            
        # Prepare numerical features for clustering
        features = [
            'event_count',
            'session_count',
            'avg_session_duration',
            'interaction_frequency'
        ]
        
        # Additional features from JSON fields
        user_metrics['morning'] = user_metrics['active_hours'].apply(
            lambda x: json.loads(x).get('morning', 0) if x else 0
        )
        user_metrics['afternoon'] = user_metrics['active_hours'].apply(
            lambda x: json.loads(x).get('afternoon', 0) if x else 0
        )
        user_metrics['evening'] = user_metrics['active_hours'].apply(
            lambda x: json.loads(x).get('evening', 0) if x else 0
        )
        user_metrics['night'] = user_metrics['active_hours'].apply(
            lambda x: json.loads(x).get('night', 0) if x else 0
        )
        
        features.extend(['morning', 'afternoon', 'evening', 'night'])
        
        # Prepare feature matrix
        X = user_metrics[features].copy()
        
        # Handle missing values
        X.fillna(0, inplace=True)
        
        # Standardize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Reduce dimensionality for better clustering
        pca = PCA(n_components=min(len(features), len(X_scaled)))
        X_pca = pca.fit_transform(X_scaled)
        
        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(X_pca)
        
        # Add cluster assignments to user metrics
        user_metrics['cluster'] = clusters
        
        # Try another clustering method for comparison
        dbscan = DBSCAN(eps=1.0, min_samples=3)
        dbscan_clusters = dbscan.fit_predict(X_pca)
        user_metrics['dbscan_cluster'] = dbscan_clusters
        
        return user_metrics
        
    def save_user_profiles(self, user_metrics):
        """
        Save user profiles to the database.
        
        Args:
            user_metrics (pd.DataFrame): DataFrame with user metrics and clusters
            
        Returns:
            int: Number of profiles updated
        """
        if user_metrics.empty:
            logger.warning("No user metrics to save")
            return 0
            
        count = 0
        for _, row in user_metrics.iterrows():
            # Prepare data for insertion/update
            data = {
                'user_id': int(row['user_id']),
                'active_hours': row['active_hours'],
                'interaction_frequency': float(row['interaction_frequency']),
                'session_duration': float(row['avg_session_duration']),
                'last_active': row['last_active']
            }
            
            # Upsert the profile
            query = """
            INSERT INTO user_profiles 
                (user_id, active_hours, interaction_frequency, session_duration, last_active)
            VALUES 
                (:user_id, :active_hours, :interaction_frequency, :session_duration, :last_active)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                active_hours = :active_hours,
                interaction_frequency = :interaction_frequency,
                session_duration = :session_duration,
                last_active = :last_active,
                updated_at = CURRENT_TIMESTAMP
            """
            
            try:
                with self.engine.connect() as conn:
                    conn.execute(text(query), data)
                    conn.commit()
                count += 1
            except Exception as e:
                logger.error(f"Error saving profile for user {row['user_id']}: {e}")
                
        logger.info(f"Updated {count} user profiles")
        return count
        
    def save_user_segments(self, user_metrics):
        """
        Save user segment information to the database.
        
        Args:
            user_metrics (pd.DataFrame): DataFrame with user metrics and clusters
            
        Returns:
            int: Number of segment memberships updated
        """
        if user_metrics.empty or 'cluster' not in user_metrics.columns:
            logger.warning("No clustering data to save")
            return 0
            
        # Ensure segments exist
        segments = {}
        for cluster_id in user_metrics['cluster'].unique():
            if cluster_id < 0:  # Skip noise points from DBSCAN
                continue
                
            segment_name = f"Behavioral Segment {cluster_id}"
            segment_description = f"Users with similar behavioral patterns (Cluster {cluster_id})"
            
            query = """
            INSERT INTO user_segments (name, description)
            VALUES (:name, :description)
            ON CONFLICT (name) DO UPDATE 
            SET description = :description
            RETURNING segment_id
            """
            
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(
                        text(query), 
                        {'name': segment_name, 'description': segment_description}
                    )
                    segment_id = result.fetchone()[0]
                    conn.commit()
                    segments[cluster_id] = segment_id
            except Exception as e:
                logger.error(f"Error saving segment {segment_name}: {e}")
                
        # Save user segment memberships
        count = 0
        for _, row in user_metrics.iterrows():
            cluster_id = row['cluster']
            if cluster_id < 0 or cluster_id not in segments:  # Skip noise points
                continue
                
            segment_id = segments[cluster_id]
            
            # Calculate confidence score (distance to cluster center)
            confidence_score = 0.8  # Default confidence
            
            query = """
            INSERT INTO user_segment_memberships 
                (user_id, segment_id, confidence_score)
            VALUES 
                (:user_id, :segment_id, :confidence_score)
            ON CONFLICT (user_id, segment_id) 
            DO UPDATE SET 
                confidence_score = :confidence_score,
                updated_at = CURRENT_TIMESTAMP
            """
            
            try:
                with self.engine.connect() as conn:
                    conn.execute(
                        text(query), 
                        {
                            'user_id': int(row['user_id']), 
                            'segment_id': segment_id,
                            'confidence_score': confidence_score
                        }
                    )
                    conn.commit()
                count += 1
            except Exception as e:
                logger.error(f"Error saving segment membership for user {row['user_id']}: {e}")
                
        logger.info(f"Updated {count} user segment memberships")
        return count
        
    def run_analysis(self):
        """
        Run the complete behavioral analysis pipeline.
        
        Returns:
            dict: Summary of the analysis results
        """
        start_time = datetime.now()
        logger.info("Starting behavioral analysis pipeline")
        
        # Step 1: Retrieve tracking data
        tracking_data = self.get_tracking_data()
        if tracking_data.empty:
            logger.warning("No tracking data available for analysis")
            return {'status': 'completed', 'processed_users': 0, 'message': 'No data available'}
            
        # Step 2: Calculate user metrics
        user_metrics = self.calculate_user_metrics(tracking_data)
        
        # Step 3: Run clustering to segment users
        if len(user_metrics) >= 3:  # Need at least 3 users for meaningful clustering
            n_clusters = min(5, len(user_metrics) // 2)  # Dynamic cluster count
            user_metrics = self.run_user_clustering(user_metrics, n_clusters=n_clusters)
        
        # Step 4: Save user profiles
        profiles_updated = self.save_user_profiles(user_metrics)
        
        # Step 5: Save user segments
        segments_updated = self.save_user_segments(user_metrics)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'status': 'completed',
            'processed_users': len(user_metrics),
            'profiles_updated': profiles_updated,
            'segments_updated': segments_updated,
            'processing_time_seconds': processing_time,
            'timestamp': datetime.now().isoformat()
        }


if __name__ == "__main__":
    analyzer = BehavioralAnalyzer()
    results = analyzer.run_analysis()
    print(json.dumps(results, indent=2))
