#!/bin/bash
# Master script for Session 8 testing
# This script makes the setup script executable and runs it

echo "Making Session 8 setup script executable..."
chmod +x scripts/setup_session8.sh

echo "Running setup verification..."
./scripts/setup_session8.sh

# Check result
if [ $? -eq 0 ]; then
    echo ""
    echo "Session 8 is viable and functional!"
    echo "You can now proceed with testing the behavioral analysis and user profiling features."
    
    # Ask if the user wants to start the API service
    read -p "Do you want to start the User Profile API service now? (y/n): " start_api
    
    if [ "$start_api" = "y" ] || [ "$start_api" = "Y" ]; then
        ./scripts/start_profile_api.sh
        
        # Ask if the user wants to test the API
        read -p "Do you want to test the API health endpoint? (y/n): " test_api
        
        if [ "$test_api" = "y" ] || [ "$test_api" = "Y" ]; then
            echo "Testing API health endpoint..."
            curl http://localhost:5002/api/health
            echo ""
            echo "You can now use the API for behavioral analysis and user profiling."
        fi
    else
        echo "You can start the service later by running: ./scripts/start_profile_api.sh"
    fi
else
    echo ""
    echo "Session 8 setup verification failed. Please check the output above for details."
    exit 1
fi
