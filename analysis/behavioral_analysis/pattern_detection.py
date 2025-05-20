"""
Pattern Detection Module for Behavioral Analysis

This module provides algorithms for detecting behavioral patterns in user
interactions and engagement data. It identifies recurring patterns and
significant events in user behavior to improve matching quality.

Part of the Session 8 implementation: Behavioral Analysis and User Profiling.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
from datetime import datetime, timedelta
from collections import Counter
import networkx as nx
from sklearn.ensemble import IsolationForest
from sklearn.metrics import silhouette_score
import json

logger = logging.getLogger(__name__)

class PatternDetectionEngine:
    """
    Engine for detecting patterns in user behavior data.
    
    Implements various algorithms to identify behavioral patterns such as:
    - Recurring interaction sequences
    - Time-based patterns (session timing, periodic behaviors)
    - Preference shifts and behavioral changes
    - Outlier behaviors and anomalies
    """
    
    def __init__(self, db_connection=None, config: Dict = None):
        """
        Initialize the pattern detection engine with connection to the database
        and optional configuration.
        
        Args:
            db_connection: Connection to the tracking database
            config: Configuration parameters for pattern detection algorithms
        """
        self.db_connection = db_connection
        self.config = config or {
            'min_pattern_support': 0.05,  # Minimum support for a pattern (fraction of sessions)
            'min_pattern_length': 2,      # Minimum length of event sequences
            'max_pattern_length': 10,     # Maximum length of event sequences
            'time_window': 30,            # Time window in minutes for sequential patterns
            'anomaly_contamination': 0.05 # Expected proportion of outliers in the dataset
        }
        self.detected_patterns = {}
        self.user_pattern_mapping = {}
        self.anomaly_detector = None
        
    def fetch_user_events_sequences(self, days_lookback: int = 30) -> pd.DataFrame:
        """
        Fetch user event sequences from the tracking database.
        
        Args:
            days_lookback: Number of days to look back for data
            
        Returns:
            DataFrame with user event sequences
        """
        if self.db_connection is None:
            logger.warning("No database connection available. Using mock data.")
            return self._generate_mock_event_sequences()
            
        # SQL query to extract user event sequences with timestamps
        query = f"""
        SELECT 
            user_id,
            session_id,
            event_id,
            event_type,
            event_timestamp,
            metadata
        FROM 
            tracking.events
        WHERE 
            event_timestamp >= NOW() - INTERVAL '{days_lookback} days'
        ORDER BY 
            user_id, session_id, event_timestamp
        """
        
        try:
            df = pd.read_sql(query, self.db_connection)
            return df
        except Exception as e:
            logger.error(f"Error fetching user event sequences: {e}")
            return self._generate_mock_event_sequences()
            
    def _generate_mock_event_sequences(self, num_users: int = 100, 
                                      sessions_per_user: int = 5, 
                                      events_per_session: int = 15) -> pd.DataFrame:
        """Generate mock user event sequence data for testing"""
        np.random.seed(42)
        
        event_types = [
            'page_view', 'match_proposed', 'match_viewed', 'match_accepted', 
            'match_rejected', 'profile_viewed', 'message_sent', 'message_received',
            'feedback_submitted', 'search_performed', 'filter_applied', 'notification_clicked'
        ]
        
        # Generate patterns for some users - same users will tend to follow similar sequences
        patterns = {
            'quick_matcher': ['page_view', 'match_proposed', 'match_viewed', 'match_accepted'],
            'careful_reviewer': ['page_view', 'match_proposed', 'match_viewed', 'profile_viewed', 
                               'match_viewed', 'match_accepted'],
            'active_communicator': ['page_view', 'message_received', 'message_sent', 
                                  'profile_viewed', 'message_sent'],
            'selective_matcher': ['page_view', 'match_proposed', 'match_viewed', 'match_rejected',
                                'match_proposed', 'match_viewed', 'match_rejected'],
            'feedback_giver': ['page_view', 'match_viewed', 'match_accepted', 'feedback_submitted']
        }
        
        user_types = np.random.choice(list(patterns.keys()), num_users)
        
        data = []
        now = datetime.now()
        
        for i in range(num_users):
            user_id = f"user_{i}"
            user_type = user_types[i]
            user_pattern = patterns[user_type]
            
            for j in range(sessions_per_user):
                session_id = f"session_{i}_{j}"
                session_start = now - timedelta(days=np.random.randint(1, 30), 
                                              hours=np.random.randint(0, 23),
                                              minutes=np.random.randint(0, 59))
                
                # Sometimes follow the pattern
                if np.random.random() < 0.7:
                    # Insert the pattern with some noise
                    session_events = []
                    pattern_pos = np.random.randint(0, events_per_session - len(user_pattern) + 1)
                    
                    for k in range(events_per_session):
                        if k >= pattern_pos and k < pattern_pos + len(user_pattern):
                            # Add pattern event
                            event_type = user_pattern[k - pattern_pos]
                        else:
                            # Add random event
                            event_type = np.random.choice(event_types)
                        
                        event_time = session_start + timedelta(minutes=k * np.random.randint(1, 5))
                        
                        session_events.append({
                            'user_id': user_id,
                            'session_id': session_id,
                            'event_id': f"event_{i}_{j}_{k}",
                            'event_type': event_type,
                            'event_timestamp': event_time,
                            'metadata': json.dumps({
                                'device_type': np.random.choice(['mobile', 'desktop', 'tablet']),
                                'browser': np.random.choice(['chrome', 'firefox', 'safari']),
                                'screen_size': np.random.choice(['small', 'medium', 'large']),
                            })
                        })
                    
                    data.extend(session_events)
                else:
                    # Completely random events
                    for k in range(events_per_session):
                        event_time = session_start + timedelta(minutes=k * np.random.randint(1, 5))
                        
                        data.append({
                            'user_id': user_id,
                            'session_id': session_id,
                            'event_id': f"event_{i}_{j}_{k}",
                            'event_type': np.random.choice(event_types),
                            'event_timestamp': event_time,
                            'metadata': json.dumps({
                                'device_type': np.random.choice(['mobile', 'desktop', 'tablet']),
                                'browser': np.random.choice(['chrome', 'firefox', 'safari']),
                                'screen_size': np.random.choice(['small', 'medium', 'large']),
                            })
                        })
        
        return pd.DataFrame(data)
    
    def detect_sequential_patterns(self, 
                                  df: pd.DataFrame,
                                  min_support: Optional[float] = None,
                                  max_pattern_length: Optional[int] = None) -> List[Dict]:
        """
        Detect sequential patterns in user event sequences.
        
        Args:
            df: DataFrame with user event sequences
            min_support: Minimum support for pattern detection
            max_pattern_length: Maximum pattern length to consider
            
        Returns:
            List of detected patterns with metadata
        """
        min_support = min_support or self.config.get('min_pattern_support', 0.05)
        max_pattern_length = max_pattern_length or self.config.get('max_pattern_length', 10)
        min_pattern_length = self.config.get('min_pattern_length', 2)
        
        # Extract event sequences by session
        session_sequences = {}
        for session_id, group in df.groupby('session_id'):
            events = group.sort_values('event_timestamp')['event_type'].tolist()
            session_sequences[session_id] = events
        
        # Use a simplified sequential pattern mining approach
        patterns = []
        total_sessions = len(session_sequences)
        
        # Count all event n-grams across sessions
        for length in range(min_pattern_length, max_pattern_length + 1):
            n_gram_counts = Counter()
            
            for sequence in session_sequences.values():
                if len(sequence) >= length:
                    for i in range(len(sequence) - length + 1):
                        n_gram = tuple(sequence[i:i+length])
                        n_gram_counts[n_gram] += 1
            
            # Filter by minimum support
            min_count = int(total_sessions * min_support)
            frequent_patterns = {pattern: count for pattern, count in n_gram_counts.items() 
                               if count >= min_count}
            
            for pattern, count in frequent_patterns.items():
                patterns.append({
                    'pattern': list(pattern),
                    'support': count / total_sessions,
                    'count': count,
                    'length': length
                })
        
        # Sort patterns by support
        patterns.sort(key=lambda x: x['support'], reverse=True)
        
        self.detected_patterns['sequential'] = patterns
        logger.info(f"Detected {len(patterns)} sequential patterns")
        
        return patterns
    
    def detect_time_based_patterns(self, df: pd.DataFrame) -> Dict:
        """
        Detect time-based patterns in user activities.
        
        Args:
            df: DataFrame with user event sequences
            
        Returns:
            Dictionary of detected time-based patterns
        """
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_dtype(df['event_timestamp']):
            df['event_timestamp'] = pd.to_datetime(df['event_timestamp'])
        
        patterns = {}
        
        # Add time components
        df['hour'] = df['event_timestamp'].dt.hour
        df['day_of_week'] = df['event_timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Activity by hour
        hourly_activity = df.groupby('hour').size()
        patterns['hourly_activity'] = hourly_activity.to_dict()
        
        # Peak activity hours
        peak_hours = hourly_activity.nlargest(3).index.tolist()
        patterns['peak_hours'] = peak_hours
        
        # Activity by day of week
        daily_activity = df.groupby('day_of_week').size()
        patterns['daily_activity'] = daily_activity.to_dict()
        
        # Weekend vs weekday activity
        weekend_ratio = df['is_weekend'].mean()
        patterns['weekend_ratio'] = weekend_ratio
        
        # Session duration analysis
        session_durations = {}
        for session_id, group in df.groupby('session_id'):
            if len(group) > 1:
                start_time = group['event_timestamp'].min()
                end_time = group['event_timestamp'].max()
                duration_minutes = (end_time - start_time).total_seconds() / 60
                session_durations[session_id] = duration_minutes
        
        if session_durations:
            duration_series = pd.Series(session_durations)
            patterns['session_duration'] = {
                'mean': duration_series.mean(),
                'median': duration_series.median(),
                'p90': duration_series.quantile(0.9),
                'min': duration_series.min(),
                'max': duration_series.max()
            }
        
        # Time between sessions (for same user)
        time_between_sessions = []
        for user_id, user_df in df.groupby('user_id'):
            sessions = user_df['session_id'].unique()
            
            if len(sessions) < 2:
                continue
                
            session_times = {}
            for session_id in sessions:
                session_start = user_df[user_df['session_id'] == session_id]['event_timestamp'].min()
                session_times[session_id] = session_start
            
            sorted_sessions = sorted(session_times.items(), key=lambda x: x[1])
            
            for i in range(1, len(sorted_sessions)):
                time_diff = (sorted_sessions[i][1] - sorted_sessions[i-1][1]).total_seconds() / 3600  # hours
                time_between_sessions.append(time_diff)
        
        if time_between_sessions:
            tbs_series = pd.Series(time_between_sessions)
            patterns['time_between_sessions'] = {
                'mean': tbs_series.mean(),
                'median': tbs_series.median(),
                'p90': tbs_series.quantile(0.9),
                'min': tbs_series.min(),
                'max': tbs_series.max()
            }
            
            # Detect potential periodic usage patterns
            if len(time_between_sessions) > 10:
                from scipy import signal
                import matplotlib.pyplot as plt
                
                # Check for daily pattern
                if tbs_series.median() > 12:  # If median time between sessions > 12 hours
                    daily_visits = len([t for t in tbs_series if 20 <= t <= 28]) / len(tbs_series)
                    patterns['periodicity'] = {
                        'daily_pattern_strength': daily_visits
                    }
        
        self.detected_patterns['time_based'] = patterns
        logger.info(f"Detected time-based patterns")
        
        return patterns
    
    def detect_behavioral_shifts(self, df: pd.DataFrame, window_size: int = 10) -> Dict:
        """
        Detect shifts in user behavior over time.
        
        Args:
            df: DataFrame with user event sequences
            window_size: Size of the rolling window for shift detection
            
        Returns:
            Dictionary of detected behavioral shifts
        """
        # Convert to datetime if not already
        if not pd.api.types.is_datetime64_dtype(df['event_timestamp']):
            df['event_timestamp'] = pd.to_datetime(df['event_timestamp'])
        
        shifts = {}
        
        # Group by user and analyze behavior over time
        for user_id, user_df in df.groupby('user_id'):
            if len(user_df) < window_size * 2:
                continue
                
            user_df = user_df.sort_values('event_timestamp')
            
            # Calculate event type distribution over time
            event_counts = user_df.groupby(['event_type', 
                                          pd.Grouper(key='event_timestamp', freq='D')]).size().unstack(0, fill_value=0)
            
            # Calculate rolling proportions
            if len(event_counts) >= window_size:
                event_props = event_counts.div(event_counts.sum(axis=1), axis=0)
                rolling_props = event_props.rolling(window=window_size).mean()
                
                # Detect significant shifts
                prop_shifts = {}
                for event_type in event_props.columns:
                    # Check for significant changes in event proportion
                    shifts_detected = []
                    for i in range(window_size, len(rolling_props)):
                        prev_window = rolling_props.iloc[i-window_size:i]
                        current_val = rolling_props.iloc[i][event_type]
                        
                        prev_mean = prev_window[event_type].mean()
                        prev_std = prev_window[event_type].std() or 0.01  # Avoid division by zero
                        
                        z_score = (current_val - prev_mean) / prev_std
                        
                        if abs(z_score) > 2:  # Significant shift (>2 std dev)
                            shifts_detected.append({
                                'timestamp': rolling_props.index[i],
                                'change': (current_val - prev_mean) / prev_mean if prev_mean > 0 else float('inf'),
                                'z_score': z_score
                            })
                    
                    if shifts_detected:
                        prop_shifts[event_type] = shifts_detected
                
                if prop_shifts:
                    shifts[user_id] = prop_shifts
        
        self.detected_patterns['behavioral_shifts'] = shifts
        logger.info(f"Detected behavioral shifts for {len(shifts)} users")
        
        return shifts
    
    def detect_anomalies(self, df: pd.DataFrame) -> Dict:
        """
        Detect anomalous behavior patterns in user activity.
        
        Args:
            df: DataFrame with user event sequences
            
        Returns:
            Dictionary of detected anomalies
        """
        # Extract features for anomaly detection
        features = self._extract_anomaly_features(df)
        
        if features.empty:
            return {}
        
        # Initialize and fit anomaly detector
        contamination = self.config.get('anomaly_contamination', 0.05)
        self.anomaly_detector = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        
        # Remove user_id for prediction but keep it for reference
        user_ids = features['user_id'].values
        X = features.drop('user_id', axis=1).values
        
        # Fit and predict
        y_pred = self.anomaly_detector.fit_predict(X)
        
        # Extract anomalies (where prediction == -1)
        anomaly_indices = np.where(y_pred == -1)[0]
        anomaly_users = user_ids[anomaly_indices]
        
        # Calculate anomaly scores
        anomaly_scores = self.anomaly_detector.decision_function(X)
        
        # Create anomaly results
        anomalies = {}
        for i, user_id in enumerate(user_ids):
            score = anomaly_scores[i]
            is_anomaly = y_pred[i] == -1
            
            if is_anomaly:
                features_dict = {col: features.iloc[i][col] for col in features.columns if col != 'user_id'}
                
                anomalies[user_id] = {
                    'anomaly_score': float(score),
                    'features': features_dict,
                    'description': self._generate_anomaly_description(features.iloc[i])
                }
        
        self.detected_patterns['anomalies'] = anomalies
        logger.info(f"Detected {len(anomalies)} users with anomalous behavior patterns")
        
        return anomalies
    
    def _extract_anomaly_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features for anomaly detection from user event data.
        
        Args:
            df: DataFrame with user event sequences
            
        Returns:
            DataFrame with features for anomaly detection
        """
        # Group by user
        user_stats = []
        
        for user_id, user_df in df.groupby('user_id'):
            if len(user_df) < 5:  # Skip users with very few events
                continue
            
            # Basic event counts
            event_counts = user_df['event_type'].value_counts()
            total_events = len(user_df)
            
            # Session statistics
            num_sessions = user_df['session_id'].nunique()
            events_per_session = total_events / max(num_sessions, 1)
            
            # Extract time features
            if pd.api.types.is_datetime64_dtype(user_df['event_timestamp']):
                time_span = (user_df['event_timestamp'].max() - user_df['event_timestamp'].min()).total_seconds() / 3600
                events_per_hour = total_events / max(time_span, 1)
                
                # Hour distribution entropy
                hours = user_df['event_timestamp'].dt.hour
                hour_counts = hours.value_counts()
                hour_probs = hour_counts / hour_counts.sum()
                hour_entropy = -np.sum(hour_probs * np.log2(hour_probs))
            else:
                time_span = 0
                events_per_hour = 0
                hour_entropy = 0
            
            # Event type diversity
            event_diversity = len(event_counts) / len(df['event_type'].unique())
            
            # Event type entropy
            event_probs = event_counts / event_counts.sum()
            event_entropy = -np.sum(event_probs * np.log2(event_probs))
            
            # Sequential pattern features
            transitions = {}
            prev_event = None
            
            sorted_events = user_df.sort_values('event_timestamp')
            for _, row in sorted_events.iterrows():
                event = row['event_type']
                
                if prev_event is not None:
                    transition = (prev_event, event)
                    transitions[transition] = transitions.get(transition, 0) + 1
                
                prev_event = event
            
            # Transition entropy
            if transitions:
                transition_counts = np.array(list(transitions.values()))
                transition_probs = transition_counts / transition_counts.sum()
                transition_entropy = -np.sum(transition_probs * np.log2(transition_probs))
            else:
                transition_entropy = 0
            
            # Combine features
            user_stats.append({
                'user_id': user_id,
                'total_events': total_events,
                'num_sessions': num_sessions,
                'events_per_session': events_per_session,
                'events_per_hour': events_per_hour,
                'time_span_hours': time_span,
                'hour_entropy': hour_entropy,
                'event_diversity': event_diversity,
                'event_entropy': event_entropy,
                'transition_entropy': transition_entropy
            })
            
            # Add most common event proportions
            most_common_events = event_counts.nlargest(min(3, len(event_counts)))
            for event_type, count in most_common_events.items():
                col_name = f"prop_{event_type}"
                user_stats[-1][col_name] = count / total_events
        
        if not user_stats:
            return pd.DataFrame()
            
        features_df = pd.DataFrame(user_stats)
        
        # Handle NaN values
        features_df.fillna(0, inplace=True)
        
        return features_df
    
    def _generate_anomaly_description(self, user_features: pd.Series) -> str:
        """
        Generate a textual description of why a user's behavior is anomalous.
        
        Args:
            user_features: Series with user features used for anomaly detection
            
        Returns:
            String description of anomalous behavior
        """
        anomaly_reasons = []
        
        # Check various anomaly indicators
        if user_features['events_per_session'] > 100:
            anomaly_reasons.append("unusually high number of events per session")
        
        if user_features['events_per_hour'] > 200:
            anomaly_reasons.append("extremely high event frequency")
        
        if user_features['event_entropy'] < 0.5:
            anomaly_reasons.append("very low event type diversity")
        
        if user_features['transition_entropy'] < 0.3:
            anomaly_reasons.append("unusually repetitive event sequences")
        
        # Check for dominant event types
        event_props = {col: user_features[col] for col in user_features.index 
                     if col.startswith('prop_')}
        
        for event_type, prop in event_props.items():
            event_name = event_type.replace('prop_', '')
            if prop > 0.8:
                anomaly_reasons.append(f"behavior dominated by '{event_name}' events ({prop:.0%})")
        
        if not anomaly_reasons:
            anomaly_reasons.append("combination of unusual behavioral metrics")
        
        return "User exhibits " + ", ".join(anomaly_reasons)
    
    def analyze_user_patterns(self, user_id: str, df: pd.DataFrame = None) -> Dict:
        """
        Analyze patterns for a specific user.
        
        Args:
            user_id: User ID to analyze
            df: Optional DataFrame with user event data
            
        Returns:
            Dictionary with user pattern analysis results
        """
        if df is None:
            # If no data provided, fetch it
            query = f"""
            SELECT 
                user_id, session_id, event_id, event_type, 
                event_timestamp, metadata
            FROM 
                tracking.events
            WHERE 
                user_id = '{user_id}'
                AND event_timestamp >= NOW() - INTERVAL '90 days'
            ORDER BY 
                session_id, event_timestamp
            """
            
            try:
                if self.db_connection:
                    df = pd.read_sql(query, self.db_connection)
                else:
                    # Generate mock data for the specific user
                    all_mock_data = self._generate_mock_event_sequences()
                    df = all_mock_data[all_mock_data['user_id'] == user_id]
                    
                    if df.empty:
                        return {'error': f"User {user_id} not found"}
            except Exception as e:
                logger.error(f"Error fetching data for user {user_id}: {e}")
                return {'error': f"Error fetching data: {e}"}
        else:
            # Filter the provided DataFrame for the specific user
            df = df[df['user_id'] == user_id].copy()
        
        if df.empty:
            return {'error': f"No data found for user {user_id}"}
        
        # Ensure datetime
        if not pd.api.types.is_datetime64_dtype(df['event_timestamp']):
            df['event_timestamp'] = pd.to_datetime(df['event_timestamp'])
        
        # Basic statistics
        num_events = len(df)
        num_sessions = df['session_id'].nunique()
        event_counts = df['event_type'].value_counts()
        first_activity = df['event_timestamp'].min()
        last_activity = df['event_timestamp'].max()
        activity_span = (last_activity - first_activity).total_seconds() / 86400  # days
        
        # Most frequent sequences
        sequences = []
        for session_id, session_df in df.groupby('session_id'):
            sequence = session_df.sort_values('event_timestamp')['event_type'].tolist()
            sequences.append(sequence)
        
        # Find n-grams in sequences
        n_grams = Counter()
        for sequence in sequences:
            for n in range(2, min(6, len(sequence) + 1)):
                for i in range(len(sequence) - n + 1):
                    n_gram = tuple(sequence[i:i+n])
                    n_grams[n_gram] += 1
        
        # Time-based patterns
        df['hour'] = df['event_timestamp'].dt.hour
        df['day_of_week'] = df['event_timestamp'].dt.dayofweek
        hourly_activity = df.groupby('hour').size()
        daily_activity = df.groupby('day_of_week').size()
        
        # Session durations
        session_durations = {}
        for session_id, session_df in df.groupby('session_id'):
            if len(session_df) > 1:
                start = session_df['event_timestamp'].min()
                end = session_df['event_timestamp'].max()
                duration_minutes = (end - start).total_seconds() / 60
                session_durations[session_id] = duration_minutes
        
        # Result dictionary
        results = {
            'user_id': user_id,
            'basic_stats': {
                'num_events': num_events,
                'num_sessions': num_sessions,
                'first_activity': first_activity.isoformat(),
                'last_activity': last_activity.isoformat(),
                'activity_span_days': activity_span,
                'events_per_session': num_events / max(num_sessions, 1)
            },
            'event_distribution': event_counts.to_dict(),
            'frequent_sequences': [
                {'sequence': list(sequence), 'count': count}
                for sequence, count in n_grams.most_common(5)
            ],
            'time_patterns': {
                'hourly_activity': hourly_activity.to_dict(),
                'daily_activity': daily_activity.to_dict(),
                'peak_hours': hourly_activity.nlargest(3).index.tolist(),
                'peak_days': daily_activity.nlargest(3).index.tolist()
            }
        }
        
        if session_durations:
            dur_series = pd.Series(session_durations)
            results['session_durations'] = {
                'mean_minutes': dur_series.mean(),
                'median_minutes': dur_series.median(),
                'min_minutes': dur_series.min(),
                'max_minutes': dur_series.max()
            }
        
        # Check for anomalies if they have been detected
        if 'anomalies' in self.detected_patterns and user_id in self.detected_patterns['anomalies']:
            results['anomaly'] = self.detected_patterns['anomalies'][user_id]
        
        # Check for behavioral shifts if they have been detected
        if 'behavioral_shifts' in self.detected_patterns and user_id in self.detected_patterns['behavioral_shifts']:
            results['behavioral_shifts'] = self.detected_patterns['behavioral_shifts'][user_id]
        
        return results
    
    def detect_all_patterns(self, days_lookback: int = 90) -> Dict:
        """
        Run all pattern detection algorithms and return results.
        
        Args:
            days_lookback: Number of days to look back for data
            
        Returns:
            Dictionary with all detected patterns
        """
        # Fetch data
        df = self.fetch_user_events_sequences(days_lookback)
        
        if df.empty:
            return {'error': 'No user data available for pattern detection'}
        
        # Run individual pattern detection algorithms
        sequential_patterns = self.detect_sequential_patterns(df)
        time_patterns = self.detect_time_based_patterns(df)
        behavioral_shifts = self.detect_behavioral_shifts(df)
        anomalies = self.detect_anomalies(df)
        
        # Combine results
        results = {
            'sequential_patterns': sequential_patterns,
            'time_patterns': time_patterns,
            'behavioral_shifts': behavioral_shifts,
            'anomalies': anomalies,
            'summary': {
                'num_users': df['user_id'].nunique(),
                'num_sessions': df['session_id'].nunique(),
                'num_events': len(df),
                'event_types': df['event_type'].unique().tolist(),
                'date_range': [
                    df['event_timestamp'].min().isoformat() if pd.api.types.is_datetime64_dtype(df['event_timestamp']) else None,
                    df['event_timestamp'].max().isoformat() if pd.api.types.is_datetime64_dtype(df['event_timestamp']) else None
                ],
                'num_sequential_patterns': len(sequential_patterns),
                'num_users_with_shifts': len(behavioral_shifts),
                'num_anomalous_users': len(anomalies)
            }
        }
        
        return results
