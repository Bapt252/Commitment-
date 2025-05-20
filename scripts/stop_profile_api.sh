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
        
        # Wait for process to terminate
        while ps -p $PID > /dev/null; do
            echo "Waiting for service to stop..."
            sleep 1
        done
        
        echo "Service stopped successfully."
    else
        echo "No running service found with PID: $PID"
    fi
    
    # Remove PID file
    rm .profile_api.pid
else
    echo "No PID file found. Service may not be running."
    
    # Try to find process by name
    PIDS=$(pgrep -f "python3 api/user_profile_api.py")
    if [ -n "$PIDS" ]; then
        echo "Found running processes: $PIDS"
        echo "Stopping all matching processes..."
        
        for p in $PIDS; do
            echo "Killing process $p"
            kill $p
        done
        
        echo "All processes stopped."
    else
        echo "No running User Profile API processes found."
    fi
fi

echo "Service shutdown complete."
