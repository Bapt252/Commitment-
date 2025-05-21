#!/bin/bash
# Script to start the User Profile API service
# Session 8: Behavioral Analysis and User Profiling

echo "Starting User Profile API service..."

# Set environment variables
export PORT=4242
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/commitment}"
export API_KEY="${API_KEY:-commitment-session8-key}"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the service
echo "Starting service on port $PORT..."
nohup python3 api/user_profile_api.py > logs/profile_api.log 2>&1 &

# Save PID to file
echo $! > .profile_api.pid
echo "Service started with PID: $!"
echo "Logs available at: logs/profile_api.log"

# Check if the service started successfully
sleep 2
if ps -p $! > /dev/null; then
    echo "Service is running successfully."
    
    # Trigger initial analysis
    echo "Triggering initial analysis job..."
    curl -X POST -H "X-API-Key: $API_KEY" http://localhost:$PORT/api/profiles/analyze
    
    echo "Setup complete. User Profile API is now available at http://localhost:$PORT"
    echo "Health check endpoint: http://localhost:$PORT/api/health"
else
    echo "Failed to start the service. Check logs at logs/profile_api.log"
fi
