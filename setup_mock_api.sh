#!/bin/bash
# Start a mock version of the User Profile API for testing
# This version doesn't require a database connection

echo "========================================================================="
echo "🚀 Starting User Profile API in MOCK mode"
echo "========================================================================="

# Create the mock API file
cat > api/user_profile_api_mock.py << 'EOF'
"""
User Profile API - Session 8 (MOCK VERSION)
--------------------------
Simplified API for testing that doesn't require a database connection.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Mock data
MOCK_USERS = {
    1: {"user_id": 1, "username": "user1", "email": "user1@example.com"},
    2: {"user_id": 2, "username": "user2", "email": "user2@example.com"},
    3: {"user_id": 3, "username": "user3", "email": "user3@example.com"}
}

MOCK_PROFILES = {
    1: {
        "profile_id": 1,
        "user_id": 1,
        "active_hours": {"morning": 0.2, "afternoon": 0.5, "evening": 0.3, "night": 0.0},
        "interaction_frequency": 4.2,
        "session_duration": 15.3,
        "last_active": datetime.now().isoformat(),
        "segments": [
            {
                "segment_id": 1,
                "name": "Behavioral Segment 1",
                "description": "Users with similar behavioral patterns",
                "confidence": 0.85
            }
        ],
        "patterns": [
            {
                "pattern_id": 1,
                "name": "Pattern 1: view_profile → like",
                "description": "view_profile → like → message",
                "pattern_type": "interaction",
                "strength": 0.75,
                "observation_count": 12,
                "first_observed": (datetime.now().isoformat()),
                "last_observed": (datetime.now().isoformat())
            }
        ],
        "preferences": {
            "content_type": {
                "profile": {
                    "score": 0.65,
                    "confidence": 0.8
                },
                "message": {
                    "score": 0.35,
                    "confidence": 0.8
                }
            }
        },
        "recommendations": [
            {
                "type": "content",
                "item": "profile",
                "score": 0.65,
                "message": "Recommended based on your preference for profile content"
            }
        ]
    }
}

class MockUserProfileAPI:
    """Mock API for testing purposes."""
    
    def get_user_profile(self, user_id):
        """Get a mock user profile."""
        if user_id in MOCK_PROFILES:
            return MOCK_PROFILES[user_id]
        elif user_id in MOCK_USERS:
            # Create a minimal profile
            minimal = MOCK_USERS[user_id].copy()
            minimal["profile_status"] = "minimal"
            return minimal
        return None
    
    def get_similar_users(self, user_id, max_results=5):
        """Get mock similar users."""
        if user_id not in MOCK_USERS:
            return []
        
        # Return other users as similar
        similar = []
        for uid, user in MOCK_USERS.items():
            if uid != user_id and len(similar) < max_results:
                similar.append({
                    "user_id": uid,
                    "username": user["username"],
                    "similarity_score": 0.5 + (1.0 / (uid + 1)),  # Just a formula for different scores
                    "confidence": 0.7
                })
        
        return similar
    
    def update_user_profile(self, user_id):
        """Mock update user profile."""
        if user_id not in MOCK_USERS:
            return {
                "status": "error",
                "message": f"User {user_id} not found"
            }
        
        return {
            "status": "success",
            "message": "User profile updated successfully (mock)",
            "timestamp": datetime.now().isoformat()
        }
    
    def run_analysis_job(self):
        """Mock analysis job."""
        return {
            "status": "success",
            "message": "Mock analysis job completed",
            "behavior_analysis": {"users_analyzed": len(MOCK_USERS)},
            "pattern_detection": {"patterns_found": 5},
            "preference_scoring": {"preferences_calculated": len(MOCK_USERS)},
            "timestamp": datetime.now().isoformat()
        }

# Initialize API
api = MockUserProfileAPI()

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
        'service': 'user-profile-api-mock',
        'mode': 'MOCK'
    })

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5002))
    print(f"🎭 Starting MOCK API server on port {port}")
    print(f"🔑 API Key: {API_KEY}")
    print(f"👥 Mock users available: {list(MOCK_USERS.keys())}")
    print(f"🔍 Try: curl http://localhost:{port}/api/health")
    print(f"🧪 Auth example: curl -H 'X-API-Key: {API_KEY}' http://localhost:{port}/api/profiles/user/1")
    app.run(host='0.0.0.0', port=port, debug=False)
EOF

# Create the script to start the mock API
cat > scripts/start_mock_profile_api.sh << 'EOF'
#!/bin/bash
# Script to start the Mock User Profile API service
# Session 8: Behavioral Analysis and User Profiling (MOCK MODE)

echo "Starting User Profile API service in MOCK mode..."

# Set environment variables
export PORT=5002
export API_KEY="${API_KEY:-commitment-session8-key}"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Create logs directory if it doesn't exist
mkdir -p logs

# Check if venv is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "It's recommended to activate your virtual environment first."
    if [ -d "venv" ]; then
        echo "You can try: source venv/bin/activate"
    fi
    # Continue anyway
fi

# Start the service
echo "Starting MOCK service on port $PORT..."
nohup python3 api/user_profile_api_mock.py > logs/mock_profile_api.log 2>&1 &

# Save PID to file
echo $! > .mock_profile_api.pid
echo "Service started with PID: $!"
echo "Logs available at: logs/mock_profile_api.log"

# Check if the service started successfully
sleep 2
if ps -p $! > /dev/null; then
    echo "Service is running successfully."
    
    echo "Setup complete. MOCK User Profile API is now available at http://localhost:$PORT"
    echo "Health check endpoint: http://localhost:$PORT/api/health"
    
    # Test the health endpoint
    echo "Testing health endpoint..."
    sleep 1
    curl -s http://localhost:$PORT/api/health | python3 -m json.tool
else
    echo "Failed to start the service. Check logs at logs/mock_profile_api.log"
fi
EOF

chmod +x scripts/start_mock_profile_api.sh

echo "Created mock API service for testing without database"
echo "To start it, run:"
echo "  chmod +x scripts/start_mock_profile_api.sh"
echo "  ./scripts/start_mock_profile_api.sh"
