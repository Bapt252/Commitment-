#!/bin/bash
# Make Session 8 scripts executable

echo "Making Session 8 scripts executable..."

# Make setup script executable
chmod +x scripts/setup_session8.sh
echo "✅ Made scripts/setup_session8.sh executable"

# Make utility scripts executable
chmod +x scripts/start_profile_api.sh
chmod +x scripts/stop_profile_api.sh
echo "✅ Made utility scripts executable"

# Make test and demo scripts executable
chmod +x test_session8.sh
chmod +x demo_session8.sh
echo "✅ Made test and demo scripts executable"

echo "All Session 8 scripts are now executable!"
echo ""
echo "You can run the following commands:"
echo "  ./test_session8.sh    - Test if Session 8 is viable"
echo "  ./demo_session8.sh    - Run a demonstration of Session 8 features"
echo ""
