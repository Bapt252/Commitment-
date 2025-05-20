#!/bin/bash

# Script to start the User Profiling API service
# Part of Session 8: Behavioral Analysis and User Profiling

echo "=========================================================="
echo "Starting User Profiling API Service"
echo "=========================================================="

# Source environment variables if available
if [ -f .env ]; then
  echo "Loading environment variables from .env file"
  export $(grep -v '^#' .env | xargs)
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
  echo "Error: python3 is required but not installed."
  exit 1
fi

# Check if required packages are installed
echo "Checking required packages..."
REQUIRED_PACKAGES="fastapi uvicorn pandas scikit-learn numpy"
MISSING_PACKAGES=""

for package in $REQUIRED_PACKAGES; do
  if ! python3 -c "import $package" 2>/dev/null; then
    MISSING_PACKAGES="$MISSING_PACKAGES $package"
  fi
done

if [ ! -z "$MISSING_PACKAGES" ]; then
  echo "Installing missing packages:$MISSING_PACKAGES"
  pip install $MISSING_PACKAGES
fi

# Check if API port is already in use
PORT=${USER_PROFILE_API_PORT:-5060}
if netstat -tuln | grep -q ":$PORT "; then
  echo "Warning: Port $PORT is already in use. The service might not start correctly."
fi

# Create log directory if it doesn't exist
LOG_DIR="logs"
mkdir -p $LOG_DIR

# Start the API service
echo "Starting User Profiling API on port $PORT..."
cd "$(dirname "$0")/../" # Move to project root

# Run with nohup to allow the process to continue after the script exits
nohup python3 -m api.user_profile_api > $LOG_DIR/user_profile_api.log 2>&1 &
PID=$!

# Check if process started successfully
sleep 2
if ps -p $PID > /dev/null; then
  echo "User Profiling API started successfully with PID $PID"
  echo "Logs available at $LOG_DIR/user_profile_api.log"
  echo "API is accessible at http://localhost:$PORT"
  echo "Health check at http://localhost:$PORT/health"
  
  # Save PID to file for later management
  echo $PID > $LOG_DIR/user_profile_api.pid
  
  echo "=========================================================="
  echo "User Profiling API is now running"
  echo "Run './stop-user-profile-api.sh' to stop the service"
  echo "=========================================================="
else
  echo "Failed to start User Profiling API. Check logs at $LOG_DIR/user_profile_api.log"
  exit 1
fi
