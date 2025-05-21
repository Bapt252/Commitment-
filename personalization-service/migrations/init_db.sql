-- Migration SQL pour le service de personnalisation

-- Table pour stocker les préférences utilisateur
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    preferences JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Table pour stocker les interactions utilisateur
CREATE TABLE IF NOT EXISTS user_interactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_action_type (action_type),
    INDEX idx_created_at (created_at)
);

-- Table pour stocker les feedbacks utilisateur
CREATE TABLE IF NOT EXISTS user_feedback (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    job_id INTEGER,
    candidate_id INTEGER,
    action VARCHAR(100) NOT NULL,
    context JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_job_id (job_id),
    INDEX idx_candidate_id (candidate_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
);

-- Table pour stocker les résultats des expériences A/B
CREATE TABLE IF NOT EXISTS ab_test_results (
    id SERIAL PRIMARY KEY,
    test_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    group_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_test_id (test_id),
    INDEX idx_user_id (user_id),
    INDEX idx_group_name (group_name),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at)
);