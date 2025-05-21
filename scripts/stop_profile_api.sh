#!/bin/bash
# Script to stop the User Profile API service
# Session 8: Behavioral Analysis and User Profiling

echo "Stopping User Profile API service..."

# Check if PID file exists
if [ -f .profile_api.pid ]; then
    PID=$(cat .profile_api.pid)
    
    # Check if process is running
    if ps -p $PID > /dev/null; then
        echo "Stopping service with PID: $PID"
        kill $PID
        rm .profile_api.pid
        echo "Service stopped."
    else
        echo "Service is not running (PID: $PID)."
        rm .profile_api.pid
    fi
else
    echo "No PID file found. Service might not be running."
    
    # Try to find process by port
    PORT=${PORT:-4242}
    PID=$(lsof -ti:$PORT)
    
    if [ -n "$PID" ]; then
        echo "Found process using port $PORT with PID: $PID"
        echo "Stopping service..."
        kill $PID
        echo "Service stopped."
    fi
fi
