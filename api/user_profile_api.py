"""
API de profil utilisateur pour la Session 8: Analyse comportementale
"""

import os
import json
import logging
from datetime import datetime, timedelta
import pandas as pd
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, text
from functools import wraps

# Import des modules d'analyse
try:
    # Importer d'abord depuis analysis_session8 (nouvelle structure)
    from analysis_session8.analyzer import BehavioralAnalyzer
    from analysis_session8.patterns import PatternDetector
    from analysis_session8.preferences import PreferenceScorer
    SESSION8_IMPORTS = True
except ImportError:
    try:
        # Fallback sur analysis (ancienne structure)
        from analysis.behavioral_analysis import BehavioralAnalyzer
        from analysis.pattern_detection import PatternDetector
        from analysis.preference_scoring import PreferenceScorer
        SESSION8_IMPORTS = False
        logging.warning("Utilisation des modules d'analyse de l'ancienne structure")
    except ImportError:
        logging.error("Impossible d'importer les modules d'analyse")
        # Fallback sur des stubs pour la démonstration
        from analysis_session8.analyzer import BehavioralAnalyzer
        from analysis_session8.patterns import PatternDetector
        from analysis_session8.preferences import PreferenceScorer
        SESSION8_IMPORTS = True

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database connection
DB_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/commitment')
try:
    engine = create_engine(DB_URL)
    logger.info(f"Connexion à la base de données établie: {DB_URL}")
except Exception as e:
    logger.error(f"Erreur de connexion à la base de données: {e}")
    engine = None

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
        self.analyzer = BehavioralAnalyzer(db_url=DB_URL)
        self.detector = PatternDetector(db_url=DB_URL)
        self.scorer = PreferenceScorer(db_url=DB_URL)
        
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
        try:
            # Mode démo si pas de moteur de BD
            if self.engine is None:
                return self._get_demo_profile(user_id)
                
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
            
            with self.engine.connect() as conn:
                result = conn.execute(text(query), {'user_id': user_id})
                row = result.fetchone()
                
                if not row:
                    # Try to get just the user
                    user_query = "SELECT id, username, email FROM users WHERE id = :user_id"
                    user_result = conn.execute(text(user_query), {'user_id': user_id})
                    user_row = user_result.fetchone()
                    
                    if not user_row:
                        return self._get_demo_profile(user_id)
                        
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
            return self._get_demo_profile(user_id)
    
    def _get_demo_profile(self, user_id):
        """
        Get a demo profile for simulation.
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: Demo profile
        """
        # Default active hours
        active_hours = {
            'morning': 0.2,
            'afternoon': 0.5,
            'evening': 0.3,
            'night': 0.0
        }
        
        # Default username based on user_id
        username = f"user{user_id}"
        
        return {
            'profile_id': 1000 + int(user_id),
            'user_id': int(user_id),
            'active_hours': active_hours,
            'interaction_frequency': 4.2,
            'session_duration': 15.3,
            'last_active': datetime.now().isoformat(),
            'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
            'updated_at': datetime.now().isoformat(),
            'username': username,
            'email': f"{username}@example.com",
            'profile_status': 'demo'
        }
            
    def _get_user_segments(self, user_id):
        """
        Get segments for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of user segments
        """
        if user_id == 1:
            return [
                {
                    'segment_id': 1,
                    'name': "Utilisateurs actifs quotidiens",
                    'description': "Utilisateurs qui se connectent quotidiennement",
                    'confidence': 0.85
                },
                {
                    'segment_id': 3,
                    'name': "Préférence de contenu: profils",
                    'description': "Utilisateurs qui préfèrent consulter des profils",
                    'confidence': 0.75
                }
            ]
        elif user_id == 2:
            return [
                {
                    'segment_id': 2,
                    'name': "Utilisateurs actifs hebdomadaires",
                    'description': "Utilisateurs qui se connectent au moins une fois par semaine",
                    'confidence': 0.92
                },
                {
                    'segment_id': 4,
                    'name': "Préférence de contenu: messages",
                    'description': "Utilisateurs qui préfèrent échanger des messages",
                    'confidence': 0.88
                }
            ]
        else:
            return [
                {
                    'segment_id': 5,
                    'name': "Nouveaux utilisateurs",
                    'description': "Utilisateurs récemment inscrits",
                    'confidence': 0.95
                }
            ]
            
    def _get_user_patterns(self, user_id):
        """
        Get behavioral patterns for a user.
        
        Args:
            user_id (int): User ID
            
        Returns:
            list: List of user patterns
        """
        if user_id == 1:
            return [
                {
                    'pattern_id': 1,
                    'name': "Pattern: view → like",
                    'description': "Consulte puis aime le contenu",
                    'pattern_type': "interaction",
                    'strength': 0.75,
                    'observation_count': 12,
                    'first_observed': (datetime.now() - timedelta(days=15)).isoformat(),
                    'last_observed': datetime.now().isoformat()
                },
                {
                    'pattern_id': 3,
                    'name': "Pattern: view → message",
                    'description': "Consulte puis envoie un message",
                    'pattern_type': "interaction",
                    'strength': 0.45,
                    'observation_count': 5,
                    'first_observed': (datetime.now() - timedelta(days=10)).isoformat(),
                    'last_observed': (datetime.now() - timedelta(days=2)).isoformat()
                }
            ]
        elif user_id == 2:
            return [
                {
                    'pattern_id': 2,
                    'name': "Pattern: message → like",
                    'description': "Envoie un message puis aime le contenu",
                    'pattern_type': "interaction",
                    'strength': 0.82,
                    'observation_count': 9,
                    'first_observed': (datetime.now() - timedelta(days=8)).isoformat(),
                    'last_observed': datetime.now().isoformat()
                }
            ]
        else:
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
        # Simulation pour la démo
        if user_id == 1:
            return [
                {
                    'user_id': 4,
                    'username': "user4",
                    'similarity_score': 0.85,
                    'confidence': 0.75
                },
                {
                    'user_id': 7,
                    'username': "user7",
                    'similarity_score': 0.72,
                    'confidence': 0.68
                }
            ]
        elif user_id == 2:
            return [
                {
                    'user_id': 5,
                    'username': "user5",
                    'similarity_score': 0.91,
                    'confidence': 0.82
                }
            ]
        else:
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
            user_data = self.analyzer.get_tracking_data(user_id=user_id)
            
            if user_data.empty:
                return {
                    'status': 'warning',
                    'message': 'No recent tracking data available for this user'
                }
                
            # Calculate user metrics
            user_metrics = self.analyzer.calculate_user_metrics(user_data)
            
            if not user_metrics.empty:
                self.analyzer.save_user_profiles(user_metrics)
                
            # Update preference scores
            self.scorer.calculate_user_preferences(user_id=user_id)
            
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
            behavior_results = self.analyzer.run_analysis()
            
            # Step 2: Run pattern detection
            pattern_results = self.detector.run_detection()
            
            # Step 3: Run preference scoring
            preference_results = self.scorer.calculate_user_preferences()
            
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
        'service': 'user-profile-api',
        'session8_imports': SESSION8_IMPORTS
    })

if __name__ == "__main__":
    port = int(os.getenv('PORT', 4242))
    logger.info(f"Démarrage de l'API de profils utilisateur sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
