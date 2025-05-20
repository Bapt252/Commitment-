-- Session 8: Behavioral Analysis Schema
-- This schema defines tables needed for user behavioral analysis and profiling

-- User Profiles Table - Stores enriched user profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    profile_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    active_hours JSONB, -- Store active hours distribution (e.g., {"morning": 0.7, "afternoon": 0.2, "evening": 0.1})
    interaction_frequency FLOAT, -- Average number of interactions per day
    session_duration FLOAT, -- Average session duration in minutes
    last_active TIMESTAMP WITH TIME ZONE
);

-- User Segments Table - Stores user segment information
CREATE TABLE IF NOT EXISTS user_segments (
    segment_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Segment Memberships - Maps users to segments
CREATE TABLE IF NOT EXISTS user_segment_memberships (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    segment_id INTEGER REFERENCES user_segments(segment_id) ON DELETE CASCADE,
    confidence_score FLOAT, -- Score indicating confidence of segment membership (0.0-1.0)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, segment_id)
);

-- Behavioral Patterns - Stores identified behavioral patterns
CREATE TABLE IF NOT EXISTS behavioral_patterns (
    pattern_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    pattern_type VARCHAR(50), -- E.g., 'navigation', 'engagement', 'conversion'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Patterns - Maps users to identified behavioral patterns
CREATE TABLE IF NOT EXISTS user_patterns (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    pattern_id INTEGER REFERENCES behavioral_patterns(pattern_id) ON DELETE CASCADE,
    strength FLOAT, -- Pattern strength for this user (0.0-1.0)
    first_observed TIMESTAMP WITH TIME ZONE,
    last_observed TIMESTAMP WITH TIME ZONE,
    observation_count INTEGER DEFAULT 1,
    PRIMARY KEY (user_id, pattern_id)
);

-- Preference Scores - Stores dynamic user preference scores
CREATE TABLE IF NOT EXISTS preference_scores (
    score_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    category VARCHAR(100) NOT NULL, -- Preference category (e.g., 'content_type', 'feature')
    item_key VARCHAR(100) NOT NULL, -- Specific item within category (e.g., 'video', 'chat')
    score FLOAT, -- Preference score (0.0-1.0)
    confidence FLOAT, -- Confidence in the score (0.0-1.0)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, category, item_key)
);

-- Create indexes for performance
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX idx_user_segment_memberships_user_id ON user_segment_memberships(user_id);
CREATE INDEX idx_user_segment_memberships_segment_id ON user_segment_memberships(segment_id);
CREATE INDEX idx_user_patterns_user_id ON user_patterns(user_id);
CREATE INDEX idx_user_patterns_pattern_id ON user_patterns(pattern_id);
CREATE INDEX idx_preference_scores_user_id ON preference_scores(user_id);
CREATE INDEX idx_preference_scores_category_item ON preference_scores(category, item_key);

-- Create function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update the updated_at columns
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_segment_memberships_updated_at
    BEFORE UPDATE ON user_segment_memberships
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_preference_scores_updated_at
    BEFORE UPDATE ON preference_scores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
