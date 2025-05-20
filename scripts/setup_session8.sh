#!/bin/bash
# Setup and verification script for Session 8
# Behavioral Analysis and User Profiling

echo "========================================================================"
echo "🔍 Session 8: Behavioral Analysis and User Profiling - Setup Verification"
echo "========================================================================"

# Check if Python is installed
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "✅ Python detected: $PYTHON_VERSION"
else
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check if pip is installed
if command -v pip3 &>/dev/null; then
    PIP_VERSION=$(pip3 --version 2>&1)
    echo "✅ pip detected: $PIP_VERSION"
else
    echo "❌ pip not found. Please install pip."
    exit 1
fi

# Check if PostgreSQL is installed
if command -v psql &>/dev/null; then
    PSQL_VERSION=$(psql --version 2>&1)
    echo "✅ PostgreSQL detected: $PSQL_VERSION"
else
    echo "⚠️ PostgreSQL not found. You may need to install PostgreSQL."
    echo "   The behavioral analysis requires a PostgreSQL database."
fi

# Create logs directory if it doesn't exist
mkdir -p logs
echo "✅ Created logs directory"

# Check if the required Python files exist
FILES_TO_CHECK=(
    "analysis/behavioral_analysis.py"
    "analysis/pattern_detection.py"
    "analysis/preference_scoring.py"
    "api/user_profile_api.py"
    "database/15_behavioral_analysis_schema.sql"
    "scripts/start_profile_api.sh"
    "scripts/stop_profile_api.sh"
)

all_files_exist=true
for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ Found: $file"
    else
        echo "❌ Missing: $file"
        all_files_exist=false
    fi
done

if [ "$all_files_exist" = true ]; then
    echo "✅ All required files are present"
else
    echo "❌ Some required files are missing. Please check the output above."
    exit 1
fi

# Make scripts executable
chmod +x scripts/start_profile_api.sh
chmod +x scripts/stop_profile_api.sh
echo "✅ Made utility scripts executable"

# Install Python dependencies
echo "Installing Python dependencies from requirements-session8.txt..."
pip3 install -r requirements-session8.txt
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Set up environment variables
export PORT=5002
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/commitment}"
export API_KEY="${API_KEY:-commitment-session8-key}"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "✅ Environment variables set"
echo "  - PORT: $PORT"
echo "  - DATABASE_URL: $DATABASE_URL"
echo "  - API_KEY: $API_KEY"

# Check database connection
echo "Checking database connection..."
if command -v psql &>/dev/null; then
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*\/\/[^:]*:[^@]*@\([^:]*\).*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
    DB_USER=$(echo $DATABASE_URL | sed -n 's/.*\/\/\([^:]*\):.*/\1/p')
    
    if PGPASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p') psql -h "$DB_HOST" -p "$DB_PORT" -d "$DB_NAME" -U "$DB_USER" -c "SELECT 1" &>/dev/null; then
        echo "✅ Database connection successful"
    else
        echo "⚠️ Could not connect to the database. You may need to check your database connection."
    fi
else
    echo "⚠️ Could not check database connection (psql not found)"
fi

echo ""
echo "========================================================================"
echo "✅ Session 8 verification complete"
echo ""
echo "To start the User Profile API service, run:"
echo "  ./scripts/start_profile_api.sh"
echo ""
echo "To stop the service, run:"
echo "  ./scripts/stop_profile_api.sh"
echo ""
echo "API Documentation:"
echo "  - GET /api/profiles/user/{user_id}"
echo "  - GET /api/profiles/user/{user_id}/similar"
echo "  - POST /api/profiles/user/{user_id}/update"
echo "  - POST /api/profiles/analyze"
echo "  - GET /api/health"
echo "========================================================================"
