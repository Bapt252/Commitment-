#!/bin/bash

# =============================================================================
# SUPERSMARTMATCH SETUP SCRIPT - Automatic Google Maps API Configuration
# =============================================================================

set -e  # Exit on any error

echo "🚀 SuperSmartMatch Setup Script"
echo "=============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    echo "Please run this script from the root directory of the Commitment project."
    exit 1
fi

print_status "Found .env file"

# Check if Google Maps API key is already configured
if grep -q "GOOGLE_MAPS_API_KEY=.*AIza" .env; then
    print_status "Google Maps API key already configured in .env"
    CURRENT_KEY=$(grep "GOOGLE_MAPS_API_KEY=" .env | grep -v "your-google-maps-api-key-here" | head -1 | cut -d'=' -f2)
    if [ ! -z "$CURRENT_KEY" ] && [ "$CURRENT_KEY" != "your-google-maps-api-key-here" ]; then
        print_info "Current key: $CURRENT_KEY"
        echo ""
        read -p "Do you want to update the existing key? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Keeping existing configuration"
            SKIP_KEY_UPDATE=true
        fi
    fi
fi

# Ask for Google Maps API key if not configured or user wants to update
if [ "$SKIP_KEY_UPDATE" != "true" ]; then
    echo ""
    print_info "Please enter your Google Maps API key:"
    print_info "Get your key at: https://console.cloud.google.com/apis/credentials"
    echo ""
    read -p "Google Maps API Key: " -r GOOGLE_MAPS_KEY
    
    if [ -z "$GOOGLE_MAPS_KEY" ]; then
        print_error "No API key provided. Exiting."
        exit 1
    fi
    
    # Validate API key format (basic check)
    if [[ ! $GOOGLE_MAPS_KEY =~ ^AIza[0-9A-Za-z_-]{35}$ ]]; then
        print_warning "API key format doesn't match expected pattern. Continuing anyway..."
    fi
    
    # Update .env file
    print_info "Updating .env file with your Google Maps API key..."
    
    # Remove existing Google Maps API key lines
    sed -i.bak '/^GOOGLE_MAPS_API_KEY=/d' .env
    
    # Add new Google Maps API key
    echo "GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_KEY" >> .env
    
    print_status "Google Maps API key updated in .env file"
else
    GOOGLE_MAPS_KEY=$(grep "GOOGLE_MAPS_API_KEY=" .env | grep -v "your-google-maps-api-key-here" | head -1 | cut -d'=' -f2)
fi

# Test the API key
echo ""
print_info "Testing Google Maps API key..."

# Test Geocoding API
GEOCODING_TEST=$(curl -s "https://maps.googleapis.com/maps/api/geocode/json?address=Paris,France&key=$GOOGLE_MAPS_KEY")
GEOCODING_STATUS=$(echo "$GEOCODING_TEST" | python3 -c "import json,sys; print(json.load(sys.stdin).get('status', 'ERROR'))" 2>/dev/null || echo "ERROR")

if [ "$GEOCODING_STATUS" = "OK" ]; then
    print_status "Geocoding API test: PASSED"
else
    print_error "Geocoding API test: FAILED (Status: $GEOCODING_STATUS)"
    print_warning "Please check your API key and ensure Geocoding API is enabled"
fi

# Test Distance Matrix API
DISTANCE_TEST=$(curl -s "https://maps.googleapis.com/maps/api/distancematrix/json?origins=Paris,France&destinations=Marseille,France&key=$GOOGLE_MAPS_KEY")
DISTANCE_STATUS=$(echo "$DISTANCE_TEST" | python3 -c "import json,sys; print(json.load(sys.stdin).get('status', 'ERROR'))" 2>/dev/null || echo "ERROR")

if [ "$DISTANCE_STATUS" = "OK" ]; then
    print_status "Distance Matrix API test: PASSED"
else
    print_error "Distance Matrix API test: FAILED (Status: $DISTANCE_STATUS)"
    print_warning "Please check your API key and ensure Distance Matrix API is enabled"
fi

# Check if Docker is running
echo ""
print_info "Checking Docker status..."
if ! docker ps > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

print_status "Docker is running"

# Check if SuperSmartMatch service is running
print_info "Checking SuperSmartMatch service..."
if docker ps | grep -q "nexten-supersmartmatch"; then
    print_status "SuperSmartMatch service is running"
    
    # Restart the service to apply new configuration
    print_info "Restarting SuperSmartMatch service to apply new configuration..."
    docker-compose restart supersmartmatch-service
    
    # Wait for service to start
    sleep 10
    
    # Check if Google Maps is now working
    print_info "Checking Google Maps integration in SuperSmartMatch..."
    LOGS=$(docker logs nexten-supersmartmatch 2>&1 | grep -i "google\|maps" | tail -5)
    
    if echo "$LOGS" | grep -q "Invalid API key"; then
        print_warning "Google Maps API key still appears to be invalid in the service"
        print_info "Try running: docker-compose down && docker-compose up -d"
    else
        print_status "SuperSmartMatch service restarted successfully"
    fi
else
    print_warning "SuperSmartMatch service is not running"
    print_info "Starting all services..."
    docker-compose up -d
    
    print_info "Waiting for services to start..."
    sleep 15
fi

# Final verification
echo ""
print_info "Final verification..."

# Check if service is accessible
if curl -s http://localhost:5062/api/v1/health > /dev/null; then
    print_status "SuperSmartMatch service is accessible at http://localhost:5062"
    
    # Test the smart-match algorithm
    print_info "Testing smart-match algorithm with geolocation..."
    TEST_RESULT=$(curl -s -X POST http://localhost:5062/api/v1/match \
        -H "Content-Type: application/json" \
        -d '{
            "cv_data": {"competences": ["Python"], "localisation": "Paris"},
            "job_data": [{"id": "1", "competences": ["Python"], "localisation": "Marseille"}],
            "algorithm": "smart-match"
        }' | python3 -c "import json,sys; data=json.load(sys.stdin); print('SUCCESS' if 'results' in data else 'ERROR')" 2>/dev/null || echo "ERROR")
    
    if [ "$TEST_RESULT" = "SUCCESS" ]; then
        print_status "Smart-match algorithm test: PASSED"
    else
        print_warning "Smart-match algorithm test: FAILED (service might still be starting)"
    fi
else
    print_error "SuperSmartMatch service is not accessible"
    print_info "Try running: docker-compose up -d"
fi

# Summary
echo ""
echo "🎉 SuperSmartMatch Setup Complete!"
echo "=================================="
echo ""
print_status "Configuration Summary:"
echo "  • Google Maps API Key: Configured"
echo "  • Service URL: http://localhost:5062"
echo "  • Health Check: http://localhost:5062/api/v1/health"
echo "  • Dashboard: http://localhost:5062/dashboard"
echo ""
print_info "Available Algorithms:"
echo "  • smart-match: Geographic matching with Google Maps"
echo "  • enhanced: Adaptive weighting algorithm"
echo "  • semantic: Semantic skill matching"
echo "  • hybrid: Combined multiple algorithms"
echo "  • auto: Automatic algorithm selection (recommended)"
echo ""
print_info "Next Steps:"
echo "  1. Test the service: curl http://localhost:5062/api/v1/health"
echo "  2. View dashboard: open http://localhost:5062/dashboard"
echo "  3. Run tests: ./test-supersmartmatch.sh"
echo ""
print_info "Documentation:"
echo "  • Setup Guide: GOOGLE_MAPS_SETUP_GUIDE.md"
echo "  • API Guide: GUIDE-SUPERSMARTMATCH.md"
echo "  • Integration: SUPERSMARTMATCH-INTEGRATION-GUIDE.md"
echo ""
