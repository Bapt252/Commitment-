-- Schema for Behavioral Analysis and User Profiling
-- Part of Session 8 implementation

-- Create schema for behavioral analysis
CREATE SCHEMA IF NOT EXISTS behavioral_analysis;

-- User clusters table - stores cluster assignments for users
CREATE TABLE IF NOT EXISTS behavioral_analysis.user_clusters (
    user_id VARCHAR(64) PRIMARY KEY,
    cluster_id INTEGER NOT NULL,
    algorithm VARCHAR(20) NOT NULL,  -- 'kmeans', 'dbscan', etc.
    cluster_name VARCHAR(100),      -- Descriptive name of the cluster
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Cluster profiles table - stores characteristics of clusters
CREATE TABLE IF NOT EXISTS behavioral_analysis.cluster_profiles (
    cluster_id INTEGER NOT NULL,
    algorithm VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    size INTEGER NOT NULL,
    percentage NUMERIC(5, 2) NOT NULL,
    features JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (cluster_id, algorithm)
);

-- Behavioral patterns table - stores detected patterns for users
CREATE TABLE IF NOT EXISTS behavioral_analysis.behavioral_patterns (
    pattern_id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,  -- 'sequential', 'time_based', 'shift', etc.
    pattern_data JSONB NOT NULL,
    confidence NUMERIC(5, 2) NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- User preferences table - stores preference models for users
CREATE TABLE IF NOT EXISTS behavioral_analysis.user_preferences (
    user_id VARCHAR(64) PRIMARY KEY,
    preference_model JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- User profile summary table - aggregates profile data for quick access
CREATE TABLE IF NOT EXISTS behavioral_analysis.user_profile_summary (
    user_id VARCHAR(64) PRIMARY KEY,
    profile_status VARCHAR(20) NOT NULL DEFAULT 'active',
    cluster_id INTEGER,
    cluster_name VARCHAR(100),
    profile_completeness NUMERIC(5, 2) NOT NULL DEFAULT 0,
    key_characteristics JSONB,
    last_activity TIMESTAMP WITH TIME ZONE,
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Global patterns table - stores patterns across all users
CREATE TABLE IF NOT EXISTS behavioral_analysis.global_patterns (
    pattern_id VARCHAR(64) PRIMARY KEY,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_data JSONB NOT NULL,
    support NUMERIC(5, 4) NOT NULL,
    confidence NUMERIC(5, 2) NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Pattern metrics table - stores metrics for pattern evaluation
CREATE TABLE IF NOT EXISTS behavioral_analysis.pattern_metrics (
    metric_id SERIAL PRIMARY KEY,
    pattern_type VARCHAR(50) NOT NULL,
    metric_date DATE NOT NULL,
    pattern_count INTEGER NOT NULL,
    avg_support NUMERIC(5, 4) NOT NULL,
    avg_confidence NUMERIC(5, 2) NOT NULL,
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Match scoring history - stores historical match scores
CREATE TABLE IF NOT EXISTS behavioral_analysis.match_scoring_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    match_id VARCHAR(64) NOT NULL,
    score NUMERIC(5, 2) NOT NULL,
    category_scores JSONB,
    scored_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- User behavior aggregates - pre-aggregated behavioral metrics
CREATE TABLE IF NOT EXISTS behavioral_analysis.user_behavior_aggregates (
    user_id VARCHAR(64) PRIMARY KEY,
    interaction_count INTEGER NOT NULL DEFAULT 0,
    viewed_matches INTEGER NOT NULL DEFAULT 0,
    accepted_matches INTEGER NOT NULL DEFAULT 0,
    rejected_matches INTEGER NOT NULL DEFAULT 0,
    acceptance_rate NUMERIC(5, 2),
    avg_view_time NUMERIC(10, 2),
    avg_decision_time NUMERIC(10, 2),
    avg_feedback_rating NUMERIC(3, 2),
    feedback_count INTEGER NOT NULL DEFAULT 0,
    last_active_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Relevance feedback table - explicit feedback about match relevance
CREATE TABLE IF NOT EXISTS behavioral_analysis.relevance_feedback (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    match_id VARCHAR(64) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comments TEXT,
    categories JSONB,  -- Category-specific ratings
    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_clusters_cluster_id 
    ON behavioral_analysis.user_clusters(cluster_id);
CREATE INDEX IF NOT EXISTS idx_behavioral_patterns_user_id 
    ON behavioral_analysis.behavioral_patterns(user_id);
CREATE INDEX IF NOT EXISTS idx_behavioral_patterns_pattern_type 
    ON behavioral_analysis.behavioral_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_global_patterns_pattern_type 
    ON behavioral_analysis.global_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_match_scoring_history_user_id 
    ON behavioral_analysis.match_scoring_history(user_id);
CREATE INDEX IF NOT EXISTS idx_match_scoring_history_match_id 
    ON behavioral_analysis.match_scoring_history(match_id);
CREATE INDEX IF NOT EXISTS idx_relevance_feedback_user_id 
    ON behavioral_analysis.relevance_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_relevance_feedback_match_id 
    ON behavioral_analysis.relevance_feedback(match_id);

-- Functions for aggregating user behavior
CREATE OR REPLACE FUNCTION behavioral_analysis.update_user_behavior_aggregates(p_user_id VARCHAR)
RETURNS VOID AS $$
DECLARE
    v_interaction_count INTEGER;
    v_viewed_matches INTEGER;
    v_accepted_matches INTEGER;
    v_rejected_matches INTEGER;
    v_acceptance_rate NUMERIC(5, 2);
    v_avg_view_time NUMERIC(10, 2);
    v_avg_decision_time NUMERIC(10, 2);
    v_avg_feedback_rating NUMERIC(3, 2);
    v_feedback_count INTEGER;
    v_last_active_at TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Get metrics from tracking events
    SELECT 
        COUNT(*) as interaction_count,
        COUNT(DISTINCT CASE WHEN e.event_type = 'match_viewed' THEN me.match_id END) as viewed_matches,
        COUNT(DISTINCT CASE WHEN e.event_type = 'match_accepted' THEN me.match_id END) as accepted_matches,
        COUNT(DISTINCT CASE WHEN e.event_type = 'match_rejected' THEN me.match_id END) as rejected_matches,
        AVG(CASE WHEN e.event_type = 'match_viewed' THEN EXTRACT(EPOCH FROM (
            LEAD(e.event_timestamp) OVER (PARTITION BY e.user_id, me.match_id ORDER BY e.event_timestamp) - e.event_timestamp
        )) END) as avg_view_time,
        AVG(CASE WHEN me.decision_time_seconds IS NOT NULL THEN me.decision_time_seconds END) as avg_decision_time,
        COUNT(DISTINCT CASE WHEN e.event_type = 'feedback_submitted' THEN fe.event_id END) as feedback_count,
        AVG(CASE WHEN fe.rating IS NOT NULL THEN fe.rating END) as avg_feedback_rating,
        MAX(e.event_timestamp) as last_active_at
    INTO 
        v_interaction_count,
        v_viewed_matches,
        v_accepted_matches,
        v_rejected_matches,
        v_avg_view_time,
        v_avg_decision_time,
        v_feedback_count,
        v_avg_feedback_rating,
        v_last_active_at
    FROM 
        tracking.events e
        LEFT JOIN tracking.match_events me ON e.event_id = me.event_id
        LEFT JOIN tracking.feedback_events fe ON e.event_id = fe.event_id
    WHERE 
        e.user_id = p_user_id;
    
    -- Calculate acceptance rate
    IF v_viewed_matches > 0 THEN
        v_acceptance_rate := ROUND((v_accepted_matches::NUMERIC / v_viewed_matches), 2);
    ELSE
        v_acceptance_rate := NULL;
    END IF;
    
    -- Insert or update aggregates
    INSERT INTO behavioral_analysis.user_behavior_aggregates (
        user_id,
        interaction_count,
        viewed_matches,
        accepted_matches,
        rejected_matches,
        acceptance_rate,
        avg_view_time,
        avg_decision_time,
        avg_feedback_rating,
        feedback_count,
        last_active_at,
        updated_at
    ) VALUES (
        p_user_id,
        COALESCE(v_interaction_count, 0),
        COALESCE(v_viewed_matches, 0),
        COALESCE(v_accepted_matches, 0),
        COALESCE(v_rejected_matches, 0),
        v_acceptance_rate,
        v_avg_view_time,
        v_avg_decision_time,
        v_avg_feedback_rating,
        COALESCE(v_feedback_count, 0),
        v_last_active_at,
        NOW()
    )
    ON CONFLICT (user_id) DO UPDATE SET
        interaction_count = COALESCE(v_interaction_count, 0),
        viewed_matches = COALESCE(v_viewed_matches, 0),
        accepted_matches = COALESCE(v_accepted_matches, 0),
        rejected_matches = COALESCE(v_rejected_matches, 0),
        acceptance_rate = v_acceptance_rate,
        avg_view_time = v_avg_view_time,
        avg_decision_time = v_avg_decision_time,
        avg_feedback_rating = v_avg_feedback_rating,
        feedback_count = COALESCE(v_feedback_count, 0),
        last_active_at = v_last_active_at,
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to update user profile summary
CREATE OR REPLACE FUNCTION behavioral_analysis.update_user_profile_summary(p_user_id VARCHAR)
RETURNS VOID AS $$
DECLARE
    v_cluster_id INTEGER;
    v_cluster_name VARCHAR(100);
    v_profile_completeness NUMERIC(5, 2) := 0;
    v_key_characteristics JSONB := '{}';
    v_last_activity TIMESTAMP WITH TIME ZONE;
    v_completeness_factors INTEGER := 0;
    v_completeness_sum NUMERIC(5, 2) := 0;
BEGIN
    -- Get cluster info
    SELECT uc.cluster_id, uc.cluster_name
    INTO v_cluster_id, v_cluster_name
    FROM behavioral_analysis.user_clusters uc
    WHERE uc.user_id = p_user_id
    ORDER BY uc.assigned_at DESC
    LIMIT 1;
    
    -- If cluster exists, add to completeness
    IF v_cluster_id IS NOT NULL THEN
        v_completeness_sum := v_completeness_sum + 1;
        v_completeness_factors := v_completeness_factors + 1;
        
        -- Get key characteristics from cluster profile
        SELECT cp.features->>'key_characteristics'
        INTO v_key_characteristics
        FROM behavioral_analysis.cluster_profiles cp
        WHERE cp.cluster_id = v_cluster_id
        LIMIT 1;
    END IF;
    
    -- Check if user has behavioral patterns
    IF EXISTS (
        SELECT 1 FROM behavioral_analysis.behavioral_patterns
        WHERE user_id = p_user_id
    ) THEN
        v_completeness_sum := v_completeness_sum + 1;
        v_completeness_factors := v_completeness_factors + 1;
    END IF;
    
    -- Check if user has preference model
    IF EXISTS (
        SELECT 1 FROM behavioral_analysis.user_preferences
        WHERE user_id = p_user_id
    ) THEN
        v_completeness_sum := v_completeness_sum + 1;
        v_completeness_factors := v_completeness_factors + 1;
    END IF;
    
    -- Get last activity
    SELECT uba.last_active_at
    INTO v_last_activity
    FROM behavioral_analysis.user_behavior_aggregates uba
    WHERE uba.user_id = p_user_id;
    
    -- Calculate overall completeness
    IF v_completeness_factors > 0 THEN
        v_profile_completeness := v_completeness_sum / v_completeness_factors;
    END IF;
    
    -- Insert or update profile summary
    INSERT INTO behavioral_analysis.user_profile_summary (
        user_id,
        profile_status,
        cluster_id,
        cluster_name,
        profile_completeness,
        key_characteristics,
        last_activity,
        last_updated
    ) VALUES (
        p_user_id,
        'active',
        v_cluster_id,
        v_cluster_name,
        v_profile_completeness,
        v_key_characteristics,
        v_last_activity,
        NOW()
    )
    ON CONFLICT (user_id) DO UPDATE SET
        profile_status = 'active',
        cluster_id = v_cluster_id,
        cluster_name = v_cluster_name,
        profile_completeness = v_profile_completeness,
        key_characteristics = v_key_characteristics,
        last_activity = v_last_activity,
        last_updated = NOW();
END;
$$ LANGUAGE plpgsql;

-- Grant appropriate permissions
GRANT USAGE ON SCHEMA behavioral_analysis TO user_profile_api;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA behavioral_analysis TO user_profile_api;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA behavioral_analysis TO user_profile_api;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA behavioral_analysis TO user_profile_api;

-- Comment
COMMENT ON SCHEMA behavioral_analysis IS 'Schema for storing user behavioral analysis and profiling data';
