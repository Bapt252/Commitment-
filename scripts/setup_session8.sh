#!/bin/bash
# Script for setup of Session 8: Behavioral Analysis and User Profiling

echo "Setting up Session 8: Behavioral Analysis and User Profiling..."

# Check prerequisites
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 is required but not installed. Aborting."; exit 1; }
command -v pip3 >/dev/null 2>&1 || { echo "❌ pip3 is required but not installed. Aborting."; exit 1; }

# Create environment file for Session 8
echo "Creating environment configuration..."
cat > .session8.env << EOF
# Environment configuration for Session 8
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/commitment}"
export PORT=4242
export API_KEY="${API_KEY:-commitment-session8-key}"
export PYTHONPATH="${PYTHONPATH:-$(pwd)}"
EOF

echo "✅ Environment configuration created: .session8.env"
echo "Use 'source .session8.env' to load these variables."

# Install required packages
echo "Installing required packages..."
pip3 install -q pandas numpy scikit-learn flask sqlalchemy

# Create database schema if database is available
if command -v psql >/dev/null 2>&1; then
    echo "Creating database schema..."
    
    # Create directory if it doesn't exist
    mkdir -p database
    
    # Create schema file if it doesn't exist
    if [ ! -f "database/15_behavioral_analysis_schema.sql" ]; then
        cat > database/15_behavioral_analysis_schema.sql << 'EOF'
-- Session 8: Schéma pour l'analyse comportementale

-- Table des profils utilisateur enrichis
CREATE TABLE IF NOT EXISTS user_profiles (
    profile_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    active_hours JSONB,
    interaction_frequency NUMERIC,
    session_duration NUMERIC,
    last_active TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des segments d'utilisateurs
CREATE TABLE IF NOT EXISTS user_segments (
    segment_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    parameters JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table d'appartenance aux segments
CREATE TABLE IF NOT EXISTS user_segment_memberships (
    user_id INTEGER NOT NULL,
    segment_id INTEGER NOT NULL,
    confidence_score NUMERIC DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, segment_id)
);

-- Table des patterns comportementaux
CREATE TABLE IF NOT EXISTS behavioral_patterns (
    pattern_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    pattern_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des patterns par utilisateur
CREATE TABLE IF NOT EXISTS user_patterns (
    user_id INTEGER NOT NULL,
    pattern_id INTEGER NOT NULL,
    strength NUMERIC DEFAULT 0.0,
    observation_count INTEGER DEFAULT 0,
    first_observed TIMESTAMP,
    last_observed TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, pattern_id)
);

-- Table des scores de préférence
CREATE TABLE IF NOT EXISTS preference_scores (
    user_id INTEGER NOT NULL,
    category VARCHAR(50) NOT NULL,
    item VARCHAR(50) NOT NULL,
    score NUMERIC DEFAULT 0.0,
    confidence NUMERIC DEFAULT 0.0,
    sample_size INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, category, item)
);

-- Création des index pour optimiser les performances
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_segment_memberships_user_id ON user_segment_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_user_segment_memberships_segment_id ON user_segment_memberships(segment_id);
CREATE INDEX IF NOT EXISTS idx_user_patterns_user_id ON user_patterns(user_id);
CREATE INDEX IF NOT EXISTS idx_user_patterns_pattern_id ON user_patterns(pattern_id);
CREATE INDEX IF NOT EXISTS idx_preference_scores_user_id ON preference_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_preference_scores_category ON preference_scores(category);

-- Trigger pour mise à jour automatique du champ updated_at
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Appliquer le trigger aux tables
CREATE TRIGGER update_user_profiles_modtime
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

CREATE TRIGGER update_user_segment_memberships_modtime
    BEFORE UPDATE ON user_segment_memberships
    FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

CREATE TRIGGER update_user_patterns_modtime
    BEFORE UPDATE ON user_patterns
    FOR EACH ROW EXECUTE PROCEDURE update_modified_column();

CREATE TRIGGER update_preference_scores_modtime
    BEFORE UPDATE ON preference_scores
    FOR EACH ROW EXECUTE PROCEDURE update_modified_column();
EOF
        echo "✅ Database schema file created"
    fi
    
    # Try to apply schema if PostgreSQL is available
    if [ -n "$DATABASE_URL" ]; then
        PGPASSWORD=${PGPASSWORD:-postgres} psql -d commitment -U postgres -f database/15_behavioral_analysis_schema.sql 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ Database schema applied successfully"
        else
            echo "⚠️ Could not apply database schema. You may need to run it manually."
        fi
    else
        echo "⚠️ DATABASE_URL not set. You may need to apply schema manually."
    fi
else
    echo "⚠️ PostgreSQL client not found. Skipping schema creation."
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x scripts/start_profile_api.sh scripts/stop_profile_api.sh
echo "✅ Scripts are now executable"

echo "✅ Session 8 setup complete!"
echo ""
echo "To start the User Profile API service:"
echo "  ./scripts/start_profile_api.sh"
echo ""
echo "To stop the service:"
echo "  ./scripts/stop_profile_api.sh"
echo ""
echo "To test the setup:"
echo "  ./test_session8.sh"
