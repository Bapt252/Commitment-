"""
Preference Scoring Module - Session 8
-----------------------------------
This module implements dynamic preference scoring for users based on their behavior.
It analyzes user interactions to calculate preference scores for different categories and items.
"""

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from collections import defaultdict
from sklearn.preprocessing import MinMaxScaler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection
DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/commitment')
engine = create_engine(DB_URL)

class PreferenceScorer:
    """Calculates dynamic preference scores for users."""
    
    def __init__(self, time_decay_factor=0.9, lookback_days=60):
        """
        Initialize the preference scorer.
        
        Args:
            time_decay_factor (float): Factor for time decay (0.0-1.0)
            lookback_days (int): Maximum days to look back for preference data
        """
        self.time_decay_factor = time_decay_factor
        self.lookback_days = lookback_days
        self.engine = engine
        self.categories = {
            'content_type': ['article', 'video', 'profile', 'message', 'event'],
            'feature': ['matching', 'messaging', 'search', 'profile_edit', 'notification'],
            'interaction': ['like', 'pass', 'message', 'block', 'report']
        }
        
    def get_user_events(self, user_id=None, days=None):
        """
        Retrieve user events for preference analysis.
        
        Args:
            user_id (int): Optional specific user ID to analyze
            days (int): Number of days to look back
            
        Returns:
            pd.DataFrame: DataFrame containing user events
        """
        if days is None:
            days = self.lookback_days
            
        start_date = datetime.now() - timedelta(days=days)
        
        user_filter = ""
        params = {'start_date': start_date}
        
        if user_id is not None:
            user_filter = "AND user_id = :user_id"
            params['user_id'] = user_id
            
        query = f"""
        SELECT 
            user_id,
            event_type,
            event_data,
            context,
            timestamp
        FROM 
            tracking_events
        WHERE 
            timestamp > :start_date
            AND user_id IS NOT NULL
            {user_filter}
        ORDER BY 
            user_id, timestamp
        """
        
        try:
            df = pd.read_sql(query, self.engine, params=params)
            logger.info(f"Retrieved {len(df)} events for preference analysis")
            return df
        except Exception as e:
            logger.error(f"Error retrieving user events: {e}")
            return pd.DataFrame()
            
    def extract_event_categories(self, df):
        """
        Extract category and item information from events.
        
        Args:
            df (pd.DataFrame): DataFrame of user events
            
        Returns:
            pd.DataFrame: DataFrame with extracted categories and items
        """
        if df.empty:
            return df
            
        # Add columns for each category
        result = df.copy()
        result['content_type'] = None
        result['feature'] = None
        result['interaction'] = None
        
        # Pattern matching for event types and data
        for idx, row in result.iterrows():
            event_type = row['event_type'].lower() if row['event_type'] else ''
            
            # Extract content type
            if 'article' in event_type or 'blog' in event_type:
                result.at[idx, 'content_type'] = 'article'
            elif 'video' in event_type or 'watch' in event_type:
                result.at[idx, 'content_type'] = 'video'
            elif 'profile' in event_type or 'user_view' in event_type:
                result.at[idx, 'content_type'] = 'profile'
            elif 'message' in event_type or 'chat' in event_type:
                result.at[idx, 'content_type'] = 'message'
            elif 'event' in event_type:
                result.at[idx, 'content_type'] = 'event'
                
            # Extract feature
            if 'match' in event_type or 'matching' in event_type:
                result.at[idx, 'feature'] = 'matching'
            elif 'message' in event_type or 'chat' in event_type:
                result.at[idx, 'feature'] = 'messaging'
            elif 'search' in event_type or 'find' in event_type:
                result.at[idx, 'feature'] = 'search'
            elif 'profile_edit' in event_type or 'update_profile' in event_type:
                result.at[idx, 'feature'] = 'profile_edit'
            elif 'notification' in event_type or 'alert' in event_type:
                result.at[idx, 'feature'] = 'notification'
                
            # Extract interaction
            if 'like' in event_type or 'favorite' in event_type:
                result.at[idx, 'interaction'] = 'like'
            elif 'pass' in event_type or 'skip' in event_type:
                result.at[idx, 'interaction'] = 'pass'
            elif 'message' in event_type or 'chat' in event_type:
                result.at[idx, 'interaction'] = 'message'
            elif 'block' in event_type:
                result.at[idx, 'interaction'] = 'block'
            elif 'report' in event_type:
                result.at[idx, 'interaction'] = 'report'
                
            # Check event_data for more information
            if row['event_data']:
                try:
                    event_data = json.loads(row['event_data'])
                    
                    if isinstance(event_data, dict):
                        # Extract content type from event_data
                        if 'content_type' in event_data:
                            content_type = event_data['content_type']
                            if content_type in self.categories['content_type']:
                                result.at[idx, 'content_type'] = content_type
                                
                        # Extract feature from event_data
                        if 'feature' in event_data:
                            feature = event_data['feature']
                            if feature in self.categories['feature']:
                                result.at[idx, 'feature'] = feature
                                
                        # Extract interaction from event_data
                        if 'action' in event_data:
                            action = event_data['action']
                            if action in self.categories['interaction']:
                                result.at[idx, 'interaction'] = action
                except:
                    pass
                    
        return result
        
    def calculate_category_scores(self, df, time_weight=True):
        """
        Calculate preference scores by category and item.
        
        Args:
            df (pd.DataFrame): DataFrame with extracted categories
            time_weight (bool): Whether to apply time weighting
            
        Returns:
            dict: Dictionary of user preference scores
        """
        if df.empty:
            return {}
            
        # Calculate time weights if needed
        if time_weight:
            now = pd.Timestamp(datetime.now())
            df['days_ago'] = (now - df['timestamp']).dt.total_seconds() / (24 * 3600)
            df['time_weight'] = df['days_ago'].apply(
                lambda x: self.time_decay_factor ** min(x, self.lookback_days)
            )
        else:
            df['time_weight'] = 1.0
            
        # Initialize preference scores
        user_preferences = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
        
        # Group by user
        for user_id, user_data in df.groupby('user_id'):
            user_id = int(user_id)
            
            # Process each category
            for category, items in self.categories.items():
                # Filter rows with valid values in this category
                category_data = user_data[user_data[category].notna()]
                
                if category_data.empty:
                    continue
                    
                # Count occurrences of each item, weighted by time
                item_weights = {}
                for item in items:
                    item_data = category_data[category_data[category] == item]
                    if not item_data.empty:
                        weight_sum = item_data['time_weight'].sum()
                        item_weights[item] = weight_sum
                        
                # Normalize scores (0.0-1.0)
                total_weight = sum(item_weights.values())
                if total_weight > 0:
                    confidence = min(1.0, len(category_data) / 10)  # Increase confidence with more data points
                    
                    for item, weight in item_weights.items():
                        score = weight / total_weight
                        user_preferences[user_id][category][item] = {
                            'score': float(score),
                            'confidence': float(confidence),
                            'raw_count': len(category_data[category_data[category] == item])
                        }
                        
        return user_preferences
        
    def save_preference_scores(self, preferences):
        """
        Save calculated preference scores to the database.
        
        Args:
            preferences (dict): Dictionary of user preference scores
            
        Returns:
            int: Number of preference scores saved
        """
        count = 0
        
        for user_id, categories in preferences.items():
            for category, items in categories.items():
                for item, scores in items.items():
                    score = scores['score']
                    confidence = scores['confidence']
                    
                    query = """
                    INSERT INTO preference_scores 
                        (user_id, category, item_key, score, confidence)
                    VALUES 
                        (:user_id, :category, :item_key, :score, :confidence)
                    ON CONFLICT (user_id, category, item_key) 
                    DO UPDATE SET 
                        score = :score,
                        confidence = :confidence,
                        updated_at = CURRENT_TIMESTAMP
                    """
                    
                    try:
                        with self.engine.connect() as conn:
                            conn.execute(
                                text(query), 
                                {
                                    'user_id': user_id, 
                                    'category': category,
                                    'item_key': item,
                                    'score': score,
                                    'confidence': confidence
                                }
                            )
                            conn.commit()
                        count += 1
                    except Exception as e:
                        logger.error(f"Error saving preference score for user {user_id}: {e}")
                        
        return count
        
    def calculate_user_preferences(self, user_id=None):
        """
        Calculate preference scores for one or all users.
        
        Args:
            user_id (int): Optional specific user ID to analyze
            
        Returns:
            dict: Summary of preference calculation results
        """
        start_time = datetime.now()
        logger.info(f"Starting preference calculation for {'user ' + str(user_id) if user_id else 'all users'}")
        
        # Step 1: Retrieve events
        events = self.get_user_events(user_id=user_id)
        
        if events.empty:
            logger.warning("No events found for preference analysis")
            return {
                'status': 'completed',
                'users_processed': 0,
                'preferences_saved': 0,
                'message': 'No data available'
            }
            
        # Step 2: Extract categories and items
        categorized_events = self.extract_event_categories(events)
        
        # Step 3: Calculate preference scores
        preferences = self.calculate_category_scores(categorized_events)
        
        # Step 4: Save preference scores
        scores_saved = self.save_preference_scores(preferences)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'status': 'completed',
            'users_processed': len(preferences),
            'preferences_saved': scores_saved,
            'processing_time_seconds': processing_time,
            'timestamp': datetime.now().isoformat()
        }
        
    def get_user_preference_scores(self, user_id):
        """
        Retrieve preference scores for a specific user.
        
        Args:
            user_id (int): User ID to retrieve preferences for
            
        Returns:
            dict: Dictionary of user preference scores by category
        """
        query = """
        SELECT 
            category, 
            item_key, 
            score, 
            confidence
        FROM 
            preference_scores
        WHERE 
            user_id = :user_id
        """
        
        try:
            df = pd.read_sql(query, self.engine, params={'user_id': user_id})
            
            if df.empty:
                return {}
                
            # Organize by category
            preferences = {}
            for category, group in df.groupby('category'):
                preferences[category] = {
                    row['item_key']: {
                        'score': float(row['score']),
                        'confidence': float(row['confidence'])
                    }
                    for _, row in group.iterrows()
                }
                
            return preferences
        except Exception as e:
            logger.error(f"Error retrieving preference scores for user {user_id}: {e}")
            return {}
            
    def generate_recommendations(self, user_id, count=5):
        """
        Generate simple recommendations based on user preferences.
        
        Args:
            user_id (int): User ID to generate recommendations for
            count (int): Number of recommendations to generate
            
        Returns:
            list: List of recommendations
        """
        preferences = self.get_user_preference_scores(user_id)
        
        if not preferences:
            return []
            
        recommendations = []
        
        # Simple content type based recommendations
        if 'content_type' in preferences:
            content_prefs = sorted(
                preferences['content_type'].items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )
            
            for content_type, scores in content_prefs[:2]:
                if scores['score'] > 0.2:
                    recommendations.append({
                        'type': 'content',
                        'item': content_type,
                        'score': scores['score'],
                        'confidence': scores['confidence'],
                        'message': f"Recommended based on your preference for {content_type} content"
                    })
                    
        # Feature based recommendations
        if 'feature' in preferences:
            feature_prefs = sorted(
                preferences['feature'].items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )
            
            for feature, scores in feature_prefs[:2]:
                if scores['score'] > 0.2:
                    recommendations.append({
                        'type': 'feature',
                        'item': feature,
                        'score': scores['score'],
                        'confidence': scores['confidence'],
                        'message': f"Recommended based on your usage of {feature} feature"
                    })
                    
        # Sort by score and confidence
        recommendations.sort(
            key=lambda x: x['score'] * x['confidence'],
            reverse=True
        )
        
        return recommendations[:count]

if __name__ == "__main__":
    scorer = PreferenceScorer()
    results = scorer.calculate_user_preferences()
    print(json.dumps(results, indent=2))
