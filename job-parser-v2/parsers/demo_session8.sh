#!/bin/bash
# Script for a quick demo of Session 8 features
# This script demonstrates the key features of the behavioral analysis system

echo "========================================================================"
echo "🚀 Session 8: Behavioral Analysis and User Profiling - Quick Demo"
echo "========================================================================"

# Check if API is running
if ! curl -s http://localhost:5002/api/health > /dev/null; then
    echo "⚠️ The User Profile API doesn't seem to be running."
    echo "Would you like to start it now? (y/n): "
    read start_api
    
    if [ "$start_api" = "y" ] || [ "$start_api" = "Y" ]; then
        ./scripts/start_profile_api.sh
        sleep 2
    else
        echo "❌ Demo cannot continue without the API running. Exiting."
        exit 1
    fi
fi

echo ""
echo "🔍 Demonstrating API Endpoints..."
echo ""

API_KEY="${API_KEY:-commitment-session8-key}"

echo "1️⃣ Health Check:"
echo "-----------------"
curl -s http://localhost:5002/api/health | python3 -m json.tool
echo ""

echo "2️⃣ User Profile Retrieval:"
echo "-------------------------"
echo "Fetching profile for User ID: 1..."
curl -s -H "X-API-Key: $API_KEY" http://localhost:5002/api/profiles/user/1 | python3 -m json.tool
echo ""

echo "3️⃣ Similar Users:"
echo "----------------"
echo "Finding users similar to User ID: 1..."
curl -s -H "X-API-Key: $API_KEY" http://localhost:5002/api/profiles/user/1/similar | python3 -m json.tool
echo ""

echo "4️⃣ Update User Profile:"
echo "---------------------"
echo "Triggering update for User ID: 1..."
curl -s -X POST -H "X-API-Key: $API_KEY" http://localhost:5002/api/profiles/user/1/update | python3 -m json.tool
echo ""

echo "5️⃣ Full Analysis Job:"
echo "-------------------"
echo "Would you like to run a full analysis job? This may take some time. (y/n): "
read run_analysis

if [ "$run_analysis" = "y" ] || [ "$run_analysis" = "Y" ]; then
    echo "Running full analysis job..."
    curl -s -X POST -H "X-API-Key: $API_KEY" http://localhost:5002/api/profiles/analyze | python3 -m json.tool
    echo ""
fi

echo ""
echo "========================================================================"
echo "✅ Session 8 Demo Complete"
echo ""
echo "Key Components Demonstrated:"
echo "  - User Profile API"
echo "  - Behavioral Analysis Engine"
echo "  - Pattern Detection"
echo "  - Preference Scoring"
echo "  - User Segmentation"
echo ""
echo "To stop the User Profile API service, run:"
echo "  ./scripts/stop_profile_api.sh"
echo "========================================================================"
