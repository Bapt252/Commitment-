"""
Preference Scoring Module for Behavioral Analysis

This module calculates dynamic preference scores for users based on their
behavioral patterns and interactions. It helps improve match quality by
incorporating implicit and explicit user preferences.

Part of the Session 8 implementation: Behavioral Analysis and User Profiling.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
import logging
from datetime import datetime, timedelta
import json
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)

class PreferenceScoringEngine:
    """
    Engine for calculating dynamic preference scores based on user behavior.
    
    This engine analyzes user interactions and behavioral patterns to infer preferences
    and calculate dynamic preference scores that can be used to improve match quality.
    """
    
    def __init__(self, db_connection=None, config: Dict = None):
        """
        Initialize the preference scoring engine with connection to the database
        and optional configuration.
        
        Args:
            db_connection: Connection to the tracking database
            config: Configuration parameters for preference scoring algorithms
        """
        self.db_connection = db_connection
        self.config = config or {
            'explicit_weight': 0.7,        # Weight for explicit preferences
            'implicit_weight': 0.3,        # Weight for implicit preferences
            'recency_decay_factor': 0.1,   # Decay factor for older interactions
            'min_interactions': 5,         # Minimum interactions required for scoring
            'max_lookback_days': 90,       # Maximum days to look back for data
            'preference_categories': [     # Categories to analyze
                'skills', 'industry', 'job_type', 'location', 'company_size'
            ]
        }
        self.preference_scores = {}
        self.category_weights = {}
        self.scaler = MinMaxScaler()
        
    def fetch_user_preference_data(self, user_id: str = None, days_lookback: int = None) -> pd.DataFrame:
        """
        Fetch user preference data from the tracking database.
        
        Args:
            user_id: Optional specific user ID to fetch data for
            days_lookback: Number of days to look back for data
            
        Returns:
            DataFrame with user preference data
        """
        days_lookback = days_lookback or self.config.get('max_lookback_days', 90)
        
        if self.db_connection is None:
            logger.warning("No database connection available. Using mock data.")
            return self._generate_mock_preference_data(user_id)
        
        # Base query to extract preference data
        query = f"""
        WITH match_interactions AS (
            SELECT 
                e.user_id,
                me.match_id,
                e.event_type,
                e.event_timestamp,
                me.match_score,
                me.constraint_satisfaction,
                CASE 
                    WHEN e.event_type = 'match_accepted' THEN 1
                    WHEN e.event_type = 'match_rejected' THEN -1
                    ELSE 0 
                END as decision_value,
                fe.rating as feedback_rating,
                fe.specific_aspects as feedback_aspects,
                e.metadata
            FROM 
                tracking.events e
                LEFT JOIN tracking.match_events me ON e.event_id = me.event_id
                LEFT JOIN tracking.feedback_events fe ON e.event_id = fe.event_id
            WHERE 
                e.event_timestamp >= NOW() - INTERVAL '{days_lookback} days'
                AND e.event_type IN ('match_proposed', 'match_viewed', 'match_accepted', 'match_rejected', 'feedback_submitted')
                {f"AND e.user_id = '{user_id}'" if user_id else ""}
        )
        SELECT * FROM match_interactions
        ORDER BY user_id, event_timestamp
        """
        
        try:
            df = pd.read_sql(query, self.db_connection)
            
            # Parse JSON fields
            for json_field in ['constraint_satisfaction', 'feedback_aspects', 'metadata']:
                if json_field in df.columns:
                    df[json_field] = df[json_field].apply(lambda x: json.loads(x) if x else {})
            
            return df
        except Exception as e:
            logger.error(f"Error fetching user preference data: {e}")
            return self._generate_mock_preference_data(user_id)
            
    def _generate_mock_preference_data(self, user_id: str = None, num_users: int = 100, 
                                     interactions_per_user: int = 50) -> pd.DataFrame:
        """Generate mock user preference data for testing"""
        np.random.seed(42)
        
        if user_id:
            user_ids = [user_id]
            num_users = 1
        else:
            user_ids = [f"user_{i}" for i in range(num_users)]
        
        data = []
        now = datetime.now()
        
        # Define preference categories and possible values
        categories = self.config.get('preference_categories', [])
        category_values = {
            'skills': ['python', 'java', 'javascript', 'sql', 'aws', 'devops', 'machine_learning', 
                     'data_science', 'frontend', 'backend', 'fullstack'],
            'industry': ['tech', 'finance', 'healthcare', 'retail', 'education', 'manufacturing', 
                       'media', 'energy', 'consulting'],
            'job_type': ['full_time', 'part_time', 'contract', 'freelance', 'internship'],
            'location': ['remote', 'hybrid', 'onsite'],
            'company_size': ['startup', 'small', 'medium', 'large', 'enterprise']
        }
        
        # Make sure we're only using categories that are configured
        category_values = {k: v for k, v in category_values.items() if k in categories}
        
        # Generate a specific pattern of preferences for each user
        user_preferences = {}
        for user_id in user_ids:
            preferences = {}
            for category, values in category_values.items():
                # For each category, assign preference weights to each value
                if len(values) > 0:
                    weights = np.random.dirichlet(np.ones(len(values)) * 0.5)  # Generate skewed weights
                    preferences[category] = {value: weight for value, weight in zip(values, weights)}
            
            user_preferences[user_id] = preferences
        
        match_id_counter = 0
        
        # Generate interactions based on user preferences
        for user_id in user_ids:
            preferences = user_preferences[user_id]
            
            for i in range(interactions_per_user):
                match_id = f"match_{match_id_counter}"
                match_id_counter += 1
                
                # Generate randomly weighted match attributes
                match_attributes = {}
                for category, values in category_values.items():
                    if len(values) > 0:
                        selected_values = np.random.choice(values, size=np.random.randint(1, 4), replace=False)
                        match_attributes[category] = selected_values.tolist()
                
                # Calculate match alignment with user preferences (implicit match quality)
                match_quality = 0
                constraint_satisfaction = {}
                
                for category, values in match_attributes.items():
                    if category in preferences:
                        category_quality = sum(preferences[category].get(value, 0) for value in values)
                        match_quality += category_quality / len(categories)
                        constraint_satisfaction[category] = category_quality
                
                # Decide if user will accept or reject based on match quality
                accept_prob = 0.2 + match_quality * 0.6  # Base chance + quality influence
                event_type = np.random.choice(
                    ['match_proposed', 'match_viewed', 'match_accepted', 'match_rejected'], 
                    p=[0.25, 0.25, accept_prob * 0.25, (1 - accept_prob) * 0.25]
                )
                
                # Decision value
                decision_value = 1 if event_type == 'match_accepted' else (-1 if event_type == 'match_rejected' else 0)
                
                # Generate timestamp within lookback period with recency bias
                days_ago = np.random.gamma(2, 10) % self.config.get('max_lookback_days', 90)
                event_time = now - timedelta(days=days_ago)
                
                # Only add feedback for accepted matches sometimes
                feedback_rating = None
                feedback_aspects = {}
                
                if event_type == 'match_accepted' and np.random.random() < 0.3:
                    # Feedback more likely to be positive for high-quality matches
                    feedback_base = 3
                    feedback_rating = min(5, max(1, int(feedback_base + match_quality * 2 + np.random.normal(0, 0.5))))
                    
                    # Generate specific feedback aspects
                    for category in np.random.choice(list(categories), size=3, replace=False):
                        aspect_rating = min(5, max(1, int(feedback_base + match_quality * 2 + np.random.normal(0, 1))))
                        feedback_aspects[category] = aspect_rating
                
                # Add the interaction to our dataset
                data.append({
                    'user_id': user_id,
                    'match_id': match_id,
                    'event_type': event_type,
                    'event_timestamp': event_time,
                    'match_score': round(match_quality * 100),  # Convert to 0-100 scale
                    'constraint_satisfaction': constraint_satisfaction,
                    'decision_value': decision_value,
                    'feedback_rating': feedback_rating,
                    'feedback_aspects': feedback_aspects,
                    'metadata': {
                        'match_attributes': match_attributes,
                        'source': 'recommendation',
                        'view_duration_seconds': np.random.gamma(3, 10) if event_type in ['match_viewed', 'match_accepted', 'match_rejected'] else None
                    }
                })
        
        df = pd.DataFrame(data)
        
        # Sort by timestamp
        df.sort_values('event_timestamp', inplace=True)
        
        return df
    
    def extract_match_attributes(self, row: pd.Series) -> Dict:
        """
        Extract match attributes from event data.
        
        Args:
            row: Series with event data
            
        Returns:
            Dictionary with match attributes
        """
        attributes = {}
        
        # Try to extract from metadata
        if isinstance(row.get('metadata'), dict) and 'match_attributes' in row['metadata']:
            attributes = row['metadata']['match_attributes']
        
        # Also check constraint satisfaction for additional attributes
        if isinstance(row.get('constraint_satisfaction'), dict):
            for category, value in row['constraint_satisfaction'].items():
                if isinstance(value, dict) and 'attributes' in value:
                    attributes[category] = value['attributes']
        
        return attributes
    
    def calculate_implicit_preferences(self, df: pd.DataFrame, user_id: str = None) -> Dict:
        """
        Calculate implicit preferences based on user interactions.
        
        Args:
            df: DataFrame with user preference data
            user_id: Optional specific user ID to calculate preferences for
            
        Returns:
            Dictionary of implicit preferences by category
        """
        # Filter for specific user if provided
        if user_id:
            user_df = df[df['user_id'] == user_id].copy()
        else:
            user_df = df.copy()
        
        if user_df.empty:
            return {}
        
        # Weight recent interactions more
        now = pd.Timestamp.now() if 'now' in dir(pd.Timestamp) else datetime.now()
        
        if pd.api.types.is_datetime64_dtype(user_df['event_timestamp']):
            user_df['days_ago'] = (now - user_df['event_timestamp']).dt.total_seconds() / (24 * 3600)
        else:
            user_df['days_ago'] = 0
            
        decay_factor = self.config.get('recency_decay_factor', 0.1)
        user_df['recency_weight'] = np.exp(-decay_factor * user_df['days_ago'])
        
        # Adjust weight based on event type
        event_weights = {
            'match_proposed': 0.1,
            'match_viewed': 0.3,
            'match_accepted': 1.0,
            'match_rejected': -1.0,
            'feedback_submitted': 0.5
        }
        
        user_df['event_weight'] = user_df['event_type'].map(event_weights).fillna(0)
        
        # Combine weights
        user_df['weight'] = user_df['recency_weight'] * user_df['event_weight']
        
        # Include decision value for accepted/rejected events
        user_df['combined_weight'] = user_df['weight']
        mask = user_df['event_type'].isin(['match_accepted', 'match_rejected'])
        user_df.loc[mask, 'combined_weight'] = user_df.loc[mask, 'weight'] * user_df.loc[mask, 'decision_value']
        
        # Process feedback ratings
        feedback_mask = user_df['feedback_rating'].notna()
        if feedback_mask.any():
            # Scale ratings to -1 to 1 range (1-5 -> -1 to 1)
            user_df.loc[feedback_mask, 'combined_weight'] = (
                user_df.loc[feedback_mask, 'combined_weight'] * 
                ((user_df.loc[feedback_mask, 'feedback_rating'] - 3) / 2)
            )
        
        # Iterate through interactions and calculate category preferences
        categories = self.config.get('preference_categories', [])
        preferences = {category: {} for category in categories}
        
        for _, row in user_df.iterrows():
            weight = row['combined_weight']
            
            # Skip if weight is zero (no meaningful preference signal)
            if weight == 0:
                continue
                
            attributes = self.extract_match_attributes(row)
            
            for category in categories:
                if category in attributes:
                    category_attrs = attributes[category]
                    
                    # Handle different formats of category attributes
                    if isinstance(category_attrs, list):
                        # List of values
                        for value in category_attrs:
                            if value not in preferences[category]:
                                preferences[category][value] = 0
                            preferences[category][value] += weight
                    elif isinstance(category_attrs, dict):
                        # Dictionary with values and weights/scores
                        for value, score in category_attrs.items():
                            if value not in preferences[category]:
                                preferences[category][value] = 0
                            preferences[category][value] += weight * score
                    else:
                        # Single value
                        value = str(category_attrs)
                        if value not in preferences[category]:
                            preferences[category][value] = 0
                        preferences[category][value] += weight
        
        # Normalize preference scores within each category
        for category, values in preferences.items():
            if values:
                scores = np.array(list(values.values()))
                min_score, max_score = np.min(scores), np.max(scores)
                
                # Only normalize if we have a range of values
                if max_score > min_score:
                    for value in values:
                        values[value] = (values[value] - min_score) / (max_score - min_score)
        
        return preferences
    
    def calculate_explicit_preferences(self, df: pd.DataFrame, user_id: str = None) -> Dict:
        """
        Calculate explicit preferences based on user feedback.
        
        Args:
            df: DataFrame with user preference data
            user_id: Optional specific user ID to calculate preferences for
            
        Returns:
            Dictionary of explicit preferences by category
        """
        # Filter for specific user if provided
        if user_id:
            user_df = df[df['user_id'] == user_id].copy()
        else:
            user_df = df.copy()
        
        if user_df.empty:
            return {}
        
        # Filter for feedback events
        feedback_df = user_df[user_df['feedback_aspects'].notna()]
        
        if feedback_df.empty:
            return {}
        
        # Weight recent feedback more
        now = pd.Timestamp.now() if 'now' in dir(pd.Timestamp) else datetime.now()
        
        if pd.api.types.is_datetime64_dtype(feedback_df['event_timestamp']):
            feedback_df['days_ago'] = (now - feedback_df['event_timestamp']).dt.total_seconds() / (24 * 3600)
        else:
            feedback_df['days_ago'] = 0
            
        decay_factor = self.config.get('recency_decay_factor', 0.1)
        feedback_df['recency_weight'] = np.exp(-decay_factor * feedback_df['days_ago'])
        
        # Collect explicit preferences from feedback
        categories = self.config.get('preference_categories', [])
        preferences = {category: {} for category in categories}
        
        for _, row in feedback_df.iterrows():
            weight = row['recency_weight']
            feedback_aspects = row.get('feedback_aspects', {})
            
            if not isinstance(feedback_aspects, dict):
                continue
                
            # Extract category ratings from feedback aspects
            for category, rating in feedback_aspects.items():
                if category not in categories:
                    continue
                    
                # Convert rating to preference score (-1 to 1 scale)
                if isinstance(rating, (int, float)):
                    score = (rating - 3) / 2  # 1-5 -> -1 to 1
                else:
                    continue
                
                # Get match attributes for this category
                attributes = self.extract_match_attributes(row)
                
                if category in attributes:
                    category_attrs = attributes[category]
                    
                    # Handle different formats of category attributes
                    if isinstance(category_attrs, list):
                        # List of values
                        for value in category_attrs:
                            if value not in preferences[category]:
                                preferences[category][value] = 0
                            preferences[category][value] += weight * score
                    elif isinstance(category_attrs, dict):
                        # Dictionary with values and weights/scores
                        for value, attr_score in category_attrs.items():
                            if value not in preferences[category]:
                                preferences[category][value] = 0
                            preferences[category][value] += weight * score * attr_score
                    else:
                        # Single value
                        value = str(category_attrs)
                        if value not in preferences[category]:
                            preferences[category][value] = 0
                        preferences[category][value] += weight * score
        
        # Normalize preference scores within each category
        for category, values in preferences.items():
            if values:
                scores = np.array(list(values.values()))
                min_score, max_score = np.min(scores), np.max(scores)
                
                # Only normalize if we have a range of values
                if max_score > min_score:
                    for value in values:
                        values[value] = (values[value] - min_score) / (max_score - min_score)
        
        return preferences
    
    def calculate_category_weights(self, df: pd.DataFrame, user_id: str = None) -> Dict:
        """
        Calculate the importance weight of each preference category.
        
        Args:
            df: DataFrame with user preference data
            user_id: Optional specific user ID to calculate weights for
            
        Returns:
            Dictionary of category importance weights
        """
        # Filter for specific user if provided
        if user_id:
            user_df = df[df['user_id'] == user_id].copy()
        else:
            user_df = df.copy()
        
        if user_df.empty:
            return {}
        
        categories = self.config.get('preference_categories', [])
        
        # Start with equal weights for all categories
        weights = {category: 1.0 for category in categories}
        
        # Look at decision patterns
        decision_df = user_df[user_df['event_type'].isin(['match_accepted', 'match_rejected'])]
        
        if decision_df.empty:
            return weights
        
        # Calculate decision correlations with category attributes
        correlations = {}
        
        for category in categories:
            category_decisions = []
            
            for _, row in decision_df.iterrows():
                decision = 1 if row['event_type'] == 'match_accepted' else -1
                attributes = self.extract_match_attributes(row)
                
                if category in attributes:
                    category_decisions.append({
                        'decision': decision,
                        'attributes': attributes[category]
                    })
            
            if category_decisions:
                # Calculate how strongly this category correlates with decisions
                correlation = 0
                
                # Check if the presence of any value in this category consistently
                # correlates with accept/reject decisions
                values_count = {}
                values_decision_sum = {}
                
                for item in category_decisions:
                    attrs = item['attributes']
                    decision = item['decision']
                    
                    # Handle different formats of category attributes
                    if isinstance(attrs, list):
                        # List of values
                        for value in attrs:
                            values_count[value] = values_count.get(value, 0) + 1
                            values_decision_sum[value] = values_decision_sum.get(value, 0) + decision
                    elif isinstance(attrs, dict):
                        # Dictionary with values and weights/scores
                        for value in attrs.keys():
                            values_count[value] = values_count.get(value, 0) + 1
                            values_decision_sum[value] = values_decision_sum.get(value, 0) + decision
                    else:
                        # Single value
                        value = str(attrs)
                        values_count[value] = values_count.get(value, 0) + 1
                        values_decision_sum[value] = values_decision_sum.get(value, 0) + decision
                
                # Calculate the average absolute correlation across values in this category
                if values_count:
                    value_correlations = [abs(values_decision_sum[value] / count) 
                                        for value, count in values_count.items() 
                                        if count > 2]  # Minimum count threshold
                    
                    if value_correlations:
                        correlation = np.mean(value_correlations)
                
                correlations[category] = correlation
        
        # Normalize correlations to weights
        if correlations:
            correlation_values = np.array(list(correlations.values()))
            
            # Check if we have meaningful correlations
            if np.sum(correlation_values) > 0:
                normalized_weights = correlation_values / np.sum(correlation_values)
                
                for i, category in enumerate(correlations.keys()):
                    weights[category] = normalized_weights[i]
        
        self.category_weights = weights
        return weights
    
    def combine_preferences(self, implicit_prefs: Dict, explicit_prefs: Dict, 
                           category_weights: Dict = None) -> Dict:
        """
        Combine implicit and explicit preferences into a unified preference model.
        
        Args:
            implicit_prefs: Dictionary of implicit preferences by category
            explicit_prefs: Dictionary of explicit preferences by category
            category_weights: Optional dictionary of category importance weights
            
        Returns:
            Dictionary of combined preference scores
        """
        categories = self.config.get('preference_categories', [])
        implicit_weight = self.config.get('implicit_weight', 0.3)
        explicit_weight = self.config.get('explicit_weight', 0.7)
        
        if not category_weights:
            category_weights = self.category_weights or {category: 1.0 for category in categories}
        
        # Combine preferences
        combined_preferences = {}
        
        for category in categories:
            cat_implicit = implicit_prefs.get(category, {})
            cat_explicit = explicit_prefs.get(category, {})
            cat_weight = category_weights.get(category, 1.0)
            
            # Merge value sets
            all_values = set(cat_implicit.keys()) | set(cat_explicit.keys())
            
            if not all_values:
                continue
            
            combined_preferences[category] = {
                'weight': cat_weight,
                'values': {}
            }
            
            for value in all_values:
                implicit_score = cat_implicit.get(value, 0)
                explicit_score = cat_explicit.get(value, 0)
                
                # Weighted combination
                combined_score = (implicit_weight * implicit_score + 
                                 explicit_weight * explicit_score)
                
                combined_preferences[category]['values'][value] = combined_score
        
        return combined_preferences
    
    def score_match_attributes(self, user_preferences: Dict, match_attributes: Dict) -> Dict:
        """
        Score a potential match against user preferences.
        
        Args:
            user_preferences: Dictionary of user preferences
            match_attributes: Dictionary of match attributes to score
            
        Returns:
            Dictionary with category and overall match scores
        """
        category_scores = {}
        category_weights = []
        weighted_scores = []
        
        # Score each category
        for category, prefs in user_preferences.items():
            if category not in match_attributes:
                continue
            
            cat_weight = prefs.get('weight', 1.0)
            cat_values = prefs.get('values', {})
            
            if not cat_values:
                continue
            
            match_values = match_attributes[category]
            
            # Handle different formats of match values
            if isinstance(match_values, list):
                # List of values
                value_scores = [cat_values.get(value, 0) for value in match_values]
                cat_score = np.mean(value_scores) if value_scores else 0
            elif isinstance(match_values, dict):
                # Dictionary with values and weights/scores
                weighted_value_scores = [
                    cat_values.get(value, 0) * weight
                    for value, weight in match_values.items()
                    if value in cat_values
                ]
                total_weight = sum(weight for value, weight in match_values.items() if value in cat_values)
                cat_score = sum(weighted_value_scores) / total_weight if total_weight > 0 else 0
            else:
                # Single value
                value = str(match_values)
                cat_score = cat_values.get(value, 0)
            
            category_scores[category] = cat_score
            category_weights.append(cat_weight)
            weighted_scores.append(cat_weight * cat_score)
        
        # Calculate overall score
        if weighted_scores:
            overall_score = sum(weighted_scores) / sum(category_weights)
        else:
            overall_score = 0
        
        return {
            'overall_score': overall_score,
            'category_scores': category_scores
        }
    
    def calculate_user_preferences(self, user_id: str, days_lookback: int = None) -> Dict:
        """
        Calculate comprehensive preference model for a user.
        
        Args:
            user_id: User ID to calculate preferences for
            days_lookback: Number of days to look back for data
            
        Returns:
            Dictionary with user preference model
        """
        # Fetch user preference data
        df = self.fetch_user_preference_data(user_id, days_lookback)
        
        if df.empty:
            return {'error': f"No preference data available for user {user_id}"}
        
        # Check if we have enough data
        min_interactions = self.config.get('min_interactions', 5)
        if len(df) < min_interactions:
            return {
                'user_id': user_id,
                'status': 'insufficient_data',
                'interactions_count': len(df),
                'min_interactions_required': min_interactions
            }
        
        # Calculate implicit and explicit preferences
        implicit_prefs = self.calculate_implicit_preferences(df, user_id)
        explicit_prefs = self.calculate_explicit_preferences(df, user_id)
        
        # Calculate category weights
        category_weights = self.calculate_category_weights(df, user_id)
        
        # Combine preferences
        combined_prefs = self.combine_preferences(implicit_prefs, explicit_prefs, category_weights)
        
        # Store preference scores for this user
        self.preference_scores[user_id] = combined_prefs
        
        return {
            'user_id': user_id,
            'status': 'success',
            'interactions_count': len(df),
            'implicit_preferences': implicit_prefs,
            'explicit_preferences': explicit_prefs, 
            'category_weights': category_weights,
            'preference_model': combined_prefs,
            'timestamp': datetime.now().isoformat()
        }
    
    def score_match_for_user(self, user_id: str, match_attributes: Dict, 
                            recalculate: bool = False) -> Dict:
        """
        Score a potential match for a specific user.
        
        Args:
            user_id: User ID to score match for
            match_attributes: Attributes of the potential match
            recalculate: Whether to recalculate user preferences
            
        Returns:
            Dictionary with match score details
        """
        # Get or calculate user preferences
        if recalculate or user_id not in self.preference_scores:
            result = self.calculate_user_preferences(user_id)
            
            if 'error' in result or result.get('status') != 'success':
                return {
                    'user_id': user_id,
                    'status': result.get('status', 'error'),
                    'error': result.get('error', 'Failed to calculate user preferences'),
                    'overall_score': 0
                }
        
        user_prefs = self.preference_scores.get(user_id, {})
        
        # Score the match
        score_result = self.score_match_attributes(user_prefs, match_attributes)
        
        return {
            'user_id': user_id,
            'status': 'success',
            'overall_score': score_result['overall_score'],
            'category_scores': score_result['category_scores'],
            'timestamp': datetime.now().isoformat()
        }
    
    def persist_preference_model(self, user_id: str) -> bool:
        """
        Persist user preference model to the database.
        
        Args:
            user_id: User ID to persist preferences for
            
        Returns:
            Boolean indicating success
        """
        if not self.db_connection:
            logger.warning("No database connection available. Cannot persist preferences.")
            return False
        
        if user_id not in self.preference_scores:
            logger.warning(f"No preference scores available for user {user_id}")
            return False
        
        try:
            # Create table if not exists
            create_table_query = """
            CREATE TABLE IF NOT EXISTS behavioral_analysis.user_preferences (
                user_id VARCHAR(64) PRIMARY KEY,
                preference_model JSONB NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )
            """
            
            with self.db_connection.cursor() as cursor:
                cursor.execute(create_table_query)
            
            # Insert or update preference model
            upsert_query = """
            INSERT INTO behavioral_analysis.user_preferences (
                user_id, preference_model, updated_at
            ) VALUES (%s, %s, NOW())
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                preference_model = EXCLUDED.preference_model,
                updated_at = NOW()
            """
            
            with self.db_connection.cursor() as cursor:
                cursor.execute(
                    upsert_query, 
                    (user_id, json.dumps(self.preference_scores[user_id]))
                )
            
            self.db_connection.commit()
            logger.info(f"Successfully persisted preference model for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error persisting preference model: {e}")
            return False
    
    def load_preference_model(self, user_id: str) -> Dict:
        """
        Load user preference model from the database.
        
        Args:
            user_id: User ID to load preferences for
            
        Returns:
            Dictionary with user preference model
        """
        if not self.db_connection:
            logger.warning("No database connection available. Cannot load preferences.")
            return {}
        
        try:
            query = """
            SELECT preference_model, updated_at
            FROM behavioral_analysis.user_preferences
            WHERE user_id = %s
            """
            
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
            
            if result:
                preference_model, updated_at = result
                self.preference_scores[user_id] = json.loads(preference_model)
                
                return {
                    'user_id': user_id,
                    'status': 'success',
                    'preference_model': self.preference_scores[user_id],
                    'last_updated': updated_at.isoformat(),
                    'source': 'database'
                }
            else:
                logger.info(f"No stored preference model found for user {user_id}")
                return {}
                
        except Exception as e:
            logger.error(f"Error loading preference model: {e}")
            return {'error': str(e)}
    
    def get_user_preferences(self, user_id: str, recalculate: bool = False) -> Dict:
        """
        Get user preferences, either from cache, database, or by calculating.
        
        Args:
            user_id: User ID to get preferences for
            recalculate: Whether to force recalculation
            
        Returns:
            Dictionary with user preference model
        """
        # Check if already in memory
        if not recalculate and user_id in self.preference_scores:
            return {
                'user_id': user_id,
                'status': 'success',
                'preference_model': self.preference_scores[user_id],
                'source': 'memory'
            }
        
        # Try loading from database
        if not recalculate:
            db_result = self.load_preference_model(user_id)
            if db_result and 'error' not in db_result:
                return db_result
        
        # Calculate preferences
        result = self.calculate_user_preferences(user_id)
        
        if 'error' not in result and result.get('status') == 'success':
            # Persist to database
            self.persist_preference_model(user_id)
            result['source'] = 'calculated'
        
        return result
