#!/bin/bash

# Script to stop the User Profiling API service
# Part of Session 8: Behavioral Analysis and User Profiling

echo "=========================================================="
echo "Stopping User Profiling API Service"
echo "=========================================================="

# Check if PID file exists
PID_FILE="logs/user_profile_api.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "PID file not found. Service may not be running."
  
  # Try to find the process by name
  PID=$(ps aux | grep "api.user_profile_api" | grep -v grep | awk '{print $2}')
  
  if [ -z "$PID" ]; then
    echo "No User Profiling API process found."
    exit 0
  fi
  
  echo "Found User Profiling API process with PID $PID"
else
  PID=$(cat "$PID_FILE")
  echo "Found PID file with process ID $PID"
fi

# Check if process is running
if ! ps -p $PID > /dev/null; then
  echo "Process with PID $PID is not running."
  rm -f "$PID_FILE"
  exit 0
fi

# Stop the process
echo "Stopping User Profiling API process with PID $PID..."
kill $PID

# Wait for process to stop
echo "Waiting for process to stop..."
for i in {1..10}; do
  if ! ps -p $PID > /dev/null; then
    echo "Process stopped successfully."
    rm -f "$PID_FILE"
    echo "=========================================================="
    echo "User Profiling API has been stopped"
    echo "=========================================================="
    exit 0
  fi
  sleep 1
done

# Force kill if process doesn't stop
echo "Process didn't stop gracefully. Forcing termination..."
kill -9 $PID

if ! ps -p $PID > /dev/null; then
  echo "Process terminated."
  rm -f "$PID_FILE"
  echo "=========================================================="
  echo "User Profiling API has been forcefully terminated"
  echo "=========================================================="
  exit 0
else
  echo "Failed to terminate process. Please check manually."
  exit 1
fi
