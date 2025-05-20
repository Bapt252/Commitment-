"""
User Profile API - Session 8
--------------------------
API for accessing enriched user profiles with behavioral analysis and preferences.
Provides endpoints for retrieving and using user profile data.
"""

import os
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from functools import wraps

# Import our analysis modules
from analysis.behavioral_analysis import BehavioralAnalyzer
from analysis.pattern_detection import PatternDetector
from analysis.preference_scoring import PreferenceScorer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection
DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/commitment')
engine = create_engine(DB_URL)

# Initialize Flask app
app = Flask(__name__)

# API key authentication
API_KEY = os.getenv('API_KEY', 'commitment-session8-key')

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        provided_key = request.headers.get('X-API-Key')
        if provided_key and provided_key == API_KEY:
            return f(*args, **kwargs)
        return jsonify({'error': 'Unauthorized. Valid API key required.'}), 401
    return decorated_function

class UserProfileAPI:
    """API for accessing and managing user profiles."""
    
    def __init__(self, engine):
        """
        Initialize the API.
        
        Args:
            engine: SQLAlchemy engine for database access
        """
        self.engine = engine
        self.analyzer = BehavioralAnalyzer()
        self.detector = PatternDetector()
        self.scorer = PreferenceScorer()
        
    def get_user_profile(self, user_id):
        """
        Get complete enriched profile for a user.
        
        Args:
            user_id (int): User ID to retrieve profile for
            
        Returns:
            dict: Complete user profile
        """
        profile = self._get_basic_profile(user_id)
        
        if not profile:
            return None
            
        # Add segments
        profile['segments'] = self._get_user_segments(user_id)
        
        # Add behavioral patterns
        profile['patterns'] = self._get_user_patterns(user_id)
        
        # Add preference scores
        profile['preferences'] = self.scorer.get_user_preference_scores(user_id)
        
        # Add recommendations
        profile['recommendations'] = self.scorer.generate_recommendations(user_id)
        
        return profile
        
    def _get_basic_profile(self, user_id):
        """
        Get basic profile information for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: Basic profile or None if not found
        """
        # Query user profile
        query = """
        SELECT 
            p.profile_id,
            p.user_id,
            p.active_hours,
            p.interaction_frequency,
            p.session_duration,
            p.last_active,
            p.created_at,
            p.updated_at,
            u.username,
            u.email
        FROM 
            user_profiles p
        JOIN 
            users u ON p.user_id = u.id
        WHERE 
            p.user_id = :user_id
        """
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {'user_id': user_id})
                row = result.fetchone()
                
                if not row:
                    # Try to get just the user
                    user_query = "SELECT id, username, email FROM users WHERE id = :user_id"
                    user_result = conn.execute(text(user_query), {'user_id': user_id})
                    user_row = user_result.fetchone()
                    
                    if not user_row:
                        return None
                        
                    # Return minimal profile
                    return {
                        'user_id': user_row[0],
                        'username': user_row[1],
                        'email': user_row[2],
                        'profile_status': 'minimal'
                    }
                    
                # Return full profile
                active_hours = json.loads(row[2]) if row[2] else {}
                
                return {
                    'profile_id': row[0],
                    'user_id': row[1],
                    'active_hours': active_hours,
                    'interaction_frequency': float(row[3]) if row[3] is not None else 0.0,
                    'session_duration': float(row[4]) if row[4] is not None else 0.0,
                    'last_active': row[5].isoformat() if row[5] else None,
                    'created_at': row[6].isoformat() if row[6] else None,
                    'updated_at': row[7].isoformat() if row[7] else None,
                    'username': row[8],
                    'email': row[9],
                    'profile_status': 'full'
                }
        except Exception as e:
            logger.error(f"Error retrieving basic profile for user {user_id}: {e}")
            return None
            
    def _get_user_segments(self, user_id):
        """
        Get segments for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of user segments
        """
        query = """
        SELECT 
            m.segment_id,
            s.name,
            s.description,
            m.confidence_score
        FROM 
            user_segment_memberships m
        JOIN 
            user_segments s ON m.segment_id = s.segment_id
        WHERE 
            m.user_id = :user_id
        """
        
        try:
            df = pd.read_sql(query, self.engine, params={'user_id': user_id})
            
            if df.empty:
                return []
                
            return [
                {
                    'segment_id': int(row['segment_id']),
                    'name': row['name'],
                    'description': row['description'],
                    'confidence': float(row['confidence_score'])
                }
                for _, row in df.iterrows()
            ]
        except Exception as e:
            logger.error(f"Error retrieving segments for user {user_id}: {e}")
            return []
            
    def _get_user_patterns(self, user_id):
        """
        Get behavioral patterns for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of user patterns
        """
        query = """
        SELECT 
            up.pattern_id,
            bp.name,
            bp.description,
            bp.pattern_type,
            up.strength,
            up.observation_count,
            up.first_observed,
            up.last_observed
        FROM 
            user_patterns up
        JOIN 
            behavioral_patterns bp ON up.pattern_id = bp.pattern_id
        WHERE 
            up.user_id = :user_id
        ORDER BY
            up.strength DESC
        """
        
        try:
            df = pd.read_sql(query, self.engine, params={'user_id': user_id})
            
            if df.empty:
                return []
                
            return [
                {
                    'pattern_id': int(row['pattern_id']),
                    'name': row['name'],
                    'description': row['description'],
                    'pattern_type': row['pattern_type'],
                    'strength': float(row['strength']),
                    'observation_count': int(row['observation_count']),
                    'first_observed': row['first_observed'].isoformat() if row['first_observed'] else None,
                    'last_observed': row['last_observed'].isoformat() if row['last_observed'] else None
                }
                for _, row in df.iterrows()
            ]
        except Exception as e:
            logger.error(f"Error retrieving patterns for user {user_id}: {e}")
            return []
            
    def get_similar_users(self, user_id, max_results=5):
        """
        Find users similar to the given user.
        
        Args:
            user_id (int): Reference user ID
            max_results (int): Maximum number of similar users to return
            
        Returns:
            list: List of similar users
        """
        # Get user's segments
        segments = self._get_user_segments(user_id)
        
        if not segments:
            return []
            
        # Use segments to find similar users
        segment_ids = [s['segment_id'] for s in segments]
        segment_placeholders = ','.join(f':segment_id_{i}' for i in range(len(segment_ids)))
        
        query = f"""
        SELECT 
            m.user_id,
            u.username,
            COUNT(*) as segment_matches,
            AVG(m.confidence_score) as avg_confidence
        FROM 
            user_segment_memberships m
        JOIN 
            users u ON m.user_id = u.id
        WHERE 
            m.segment_id IN ({segment_placeholders})
            AND m.user_id != :user_id
        GROUP BY 
            m.user_id, u.username
        ORDER BY 
            segment_matches DESC,
            avg_confidence DESC
        LIMIT :max_results
        """
        
        params = {'user_id': user_id, 'max_results': max_results}
        for i, segment_id in enumerate(segment_ids):
            params[f'segment_id_{i}'] = segment_id
            
        try:
            df = pd.read_sql(query, self.engine, params=params)
            
            if df.empty:
                return []
                
            return [
                {
                    'user_id': int(row['user_id']),
                    'username': row['username'],
                    'similarity_score': float(row['segment_matches']) / len(segments),
                    'confidence': float(row['avg_confidence'])
                }
                for _, row in df.iterrows()
            ]
        except Exception as e:
            logger.error(f"Error finding similar users for user {user_id}: {e}")
            return []
            
    def update_user_profile(self, user_id):
        """
        Trigger an immediate update of a user's profile.
        
        Args:
            user_id (int): User ID to update
            
        Returns:
            dict: Update status
        """
        try:
            # Run behavioral analysis
            analyzer = BehavioralAnalyzer()
            tracking_data = analyzer.get_tracking_data(
                start_date=datetime.now() - timedelta(days=30)
            )
            
            if tracking_data.empty:
                return {
                    'status': 'warning',
                    'message': 'No recent tracking data available for this user'
                }
                
            # Filter for this user
            user_data = tracking_data[tracking_data['user_id'] == user_id]
            
            if user_data.empty:
                return {
                    'status': 'warning',
                    'message': 'No recent activity for this user'
                }
                
            # Calculate user metrics
            user_metrics = analyzer.calculate_user_metrics(user_data)
            
            if not user_metrics.empty:
                analyzer.save_user_profiles(user_metrics)
                
            # Update preference scores
            scorer = PreferenceScorer()
            scorer.calculate_user_preferences(user_id=user_id)
            
            # Update patterns
            detector = PatternDetector()
            user_sequences = detector.get_user_sequences()
            
            if user_id in user_sequences:
                patterns = detector.find_sequential_patterns({user_id: user_sequences[user_id]})
                pattern_ids = detector.save_behavioral_patterns(patterns)
                user_patterns = detector.find_user_patterns({user_id: user_sequences[user_id]}, patterns)
                detector.save_user_patterns(user_patterns, pattern_ids)
                
            return {
                'status': 'success',
                'message': 'User profile updated successfully',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {e}")
            return {
                'status': 'error',
                'message': f"Error updating user profile: {str(e)}"
            }
            
    def run_analysis_job(self):
        """
        Run a complete analysis job for all users.
        
        Returns:
            dict: Job status
        """
        try:
            # Step 1: Run behavioral analysis
            analyzer = BehavioralAnalyzer()
            behavior_results = analyzer.run_analysis()
            
            # Step 2: Run pattern detection
            detector = PatternDetector()
            pattern_results = detector.run_detection()
            
            # Step 3: Run preference scoring
            scorer = PreferenceScorer()
            preference_results = scorer.calculate_user_preferences()
            
            return {
                'status': 'success',
                'behavior_analysis': behavior_results,
                'pattern_detection': pattern_results,
                'preference_scoring': preference_results,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error running analysis job: {e}")
            return {
                'status': 'error',
                'message': f"Error running analysis job: {str(e)}"
            }


# Initialize API
api = UserProfileAPI(engine)

@app.route('/api/profiles/user/<int:user_id>', methods=['GET'])
@require_api_key
def get_user_profile(user_id):
    """API endpoint to get a user's profile."""
    profile = api.get_user_profile(user_id)
    
    if profile:
        return jsonify(profile)
    return jsonify({'error': 'User profile not found'}), 404
    
@app.route('/api/profiles/user/<int:user_id>/similar', methods=['GET'])
@require_api_key
def get_similar_users(user_id):
    """API endpoint to get users similar to the specified user."""
    max_results = request.args.get('max_results', 5, type=int)
    similar_users = api.get_similar_users(user_id, max_results=max_results)
    
    return jsonify({'similar_users': similar_users})
    
@app.route('/api/profiles/user/<int:user_id>/update', methods=['POST'])
@require_api_key
def update_user_profile(user_id):
    """API endpoint to trigger a profile update for a user."""
    result = api.update_user_profile(user_id)
    return jsonify(result)
    
@app.route('/api/profiles/analyze', methods=['POST'])
@require_api_key
def run_analysis_job():
    """API endpoint to run a complete analysis job."""
    result = api.run_analysis_job()
    return jsonify(result)
    
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'service': 'user-profile-api'
    })

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)
