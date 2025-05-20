-- Extensions au schéma de base de données pour le système de tracking
-- Contient des fonctions et tables additionnelles pour la gestion des partitions,
-- l'agrégation des données et l'analyse des comportements utilisateurs.

-- Tables additionnelles pour le tracking avancé et l'apprentissage automatique

-- Table pour stocker les statistiques sur les contraintes
CREATE TABLE IF NOT EXISTS tracking.constraint_stats (
    constraint_name VARCHAR(50) NOT NULL,
    value_bucket NUMERIC(3,1) NOT NULL, -- Bucket de 0.1 en 0.1 (0.0, 0.1, ..., 1.0)
    acceptances INTEGER NOT NULL DEFAULT 0,
    rejections INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    PRIMARY KEY (constraint_name, value_bucket)
);

-- Table pour stocker les corrélations entre scores de match et feedback
CREATE TABLE IF NOT EXISTS tracking.feedback_correlation (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    match_score NUMERIC(5,2) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_correlation_match_id ON tracking.feedback_correlation(match_id);
CREATE INDEX IF NOT EXISTS idx_feedback_correlation_user_id ON tracking.feedback_correlation(user_id);

-- Table pour stocker les aspects spécifiques du feedback
CREATE TABLE IF NOT EXISTS tracking.feedback_aspects (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    aspect VARCHAR(50) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_feedback_aspects_match_id ON tracking.feedback_aspects(match_id);
CREATE INDEX IF NOT EXISTS idx_feedback_aspects_aspect ON tracking.feedback_aspects(aspect);

-- Table pour stocker les raisons de rejet
CREATE TABLE IF NOT EXISTS tracking.rejection_reasons (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    reason TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rejection_reasons_match_id ON tracking.rejection_reasons(match_id);

-- Table pour stocker les métriques de visualisation des matches
CREATE TABLE IF NOT EXISTS tracking.match_view_metrics (
    id SERIAL PRIMARY KEY,
    match_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    view_duration NUMERIC(10,2) NOT NULL,
    view_complete BOOLEAN NOT NULL DEFAULT FALSE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_match_view_metrics_match_id ON tracking.match_view_metrics(match_id);
CREATE INDEX IF NOT EXISTS idx_match_view_metrics_user_id ON tracking.match_view_metrics(user_id);

-- Table pour stocker les poids du modèle
CREATE TABLE IF NOT EXISTS tracking.model_weights (
    id SERIAL PRIMARY KEY,
    weights_json JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_model_weights_created_at ON tracking.model_weights(created_at);
CREATE INDEX IF NOT EXISTS idx_model_weights_is_active ON tracking.model_weights(is_active);

-- Fonction pour la gestion automatique des partitions mensuelles
CREATE OR REPLACE FUNCTION tracking.create_monthly_partition()
RETURNS void AS $$
DECLARE
    partition_date DATE := DATE_TRUNC('month', CURRENT_DATE + interval '1 month');
    partition_name TEXT;
BEGIN
    partition_name := 'events_' || TO_CHAR(partition_date, 'YYYY_MM');
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS tracking.%I PARTITION OF tracking.events_partitioned
         FOR VALUES FROM (%L) TO (%L)',
        partition_name,
        partition_date,
        partition_date + interval '1 month'
    );
    
    RAISE NOTICE 'Created partition %', partition_name;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour supprimer les partitions anciennes (rétention des données)
CREATE OR REPLACE FUNCTION tracking.cleanup_old_partitions(retention_months INTEGER DEFAULT 24)
RETURNS void AS $$
DECLARE
    old_date DATE := DATE_TRUNC('month', CURRENT_DATE - (retention_months || ' month')::INTERVAL);
    partition_name TEXT;
BEGIN
    partition_name := 'events_' || TO_CHAR(old_date, 'YYYY_MM');
    
    EXECUTE format('DROP TABLE IF EXISTS tracking.%I', partition_name);
    
    RAISE NOTICE 'Dropped partition %', partition_name;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour agréger les métriques quotidiennes
CREATE OR REPLACE FUNCTION tracking.aggregate_daily_metrics(p_date DATE DEFAULT CURRENT_DATE - INTERVAL '1 day')
RETURNS void AS $$
DECLARE
    v_total_matches INTEGER;
    v_viewed_matches INTEGER;
    v_accepted_matches INTEGER;
    v_rejected_matches INTEGER;
    v_avg_decision_time NUMERIC(10,2);
    v_avg_match_score NUMERIC(5,2);
    v_avg_feedback_rating NUMERIC(5,2);
    v_details JSONB;
BEGIN
    -- Événements de matching
    SELECT COUNT(*) INTO v_total_matches
    FROM tracking.events
    WHERE event_type = 'match_proposed'
    AND event_timestamp::DATE = p_date;

    SELECT COUNT(*) INTO v_viewed_matches
    FROM tracking.events
    WHERE event_type = 'match_viewed'
    AND event_timestamp::DATE = p_date;

    SELECT COUNT(*) INTO v_accepted_matches
    FROM tracking.events
    WHERE event_type = 'match_accepted'
    AND event_timestamp::DATE = p_date;

    SELECT COUNT(*) INTO v_rejected_matches
    FROM tracking.events
    WHERE event_type = 'match_rejected'
    AND event_timestamp::DATE = p_date;

    -- Temps moyen de décision
    SELECT AVG(me.decision_time_seconds) INTO v_avg_decision_time
    FROM tracking.events e
    JOIN tracking.match_events me ON e.event_id = me.event_id
    WHERE e.event_type IN ('match_accepted', 'match_rejected')
    AND e.event_timestamp::DATE = p_date;

    -- Score moyen des matches
    SELECT AVG(me.match_score) INTO v_avg_match_score
    FROM tracking.events e
    JOIN tracking.match_events me ON e.event_id = me.event_id
    WHERE e.event_type = 'match_proposed'
    AND e.event_timestamp::DATE = p_date;

    -- Note moyenne des feedbacks
    SELECT AVG(fe.rating) INTO v_avg_feedback_rating
    FROM tracking.events e
    JOIN tracking.feedback_events fe ON e.event_id = fe.event_id
    WHERE e.event_type = 'match_feedback'
    AND e.event_timestamp::DATE = p_date;

    -- Détails additionnels (distribution des notes, etc.)
    SELECT jsonb_build_object(
        'rating_distribution', COALESCE(jsonb_object_agg(r.rating, r.count), '{}'),
        'constraint_satisfaction', COALESCE(jsonb_object_agg(c.constraint_name, c.avg_satisfaction), '{}'),
        'event_count_by_hour', COALESCE(jsonb_object_agg(h.hour, h.count), '{}')
    ) INTO v_details
    FROM (
        -- Distribution des notes de feedback
        SELECT rating, COUNT(*) as count
        FROM tracking.events e
        JOIN tracking.feedback_events fe ON e.event_id = fe.event_id
        WHERE e.event_timestamp::DATE = p_date
        GROUP BY rating
    ) r,
    LATERAL (
        -- Satisfaction moyenne des contraintes
        SELECT 
            key as constraint_name, 
            AVG((value::text)::numeric) as avg_satisfaction
        FROM tracking.events e
        JOIN tracking.match_events me ON e.event_id = me.event_id,
        jsonb_each(me.constraint_satisfaction)
        WHERE e.event_timestamp::DATE = p_date
        GROUP BY key
    ) c,
    LATERAL (
        -- Nombre d'événements par heure
        SELECT 
            EXTRACT(HOUR FROM event_timestamp) as hour,
            COUNT(*) as count
        FROM tracking.events
        WHERE event_timestamp::DATE = p_date
        GROUP BY EXTRACT(HOUR FROM event_timestamp)
    ) h;

    -- Insérer ou mettre à jour les métriques
    INSERT INTO tracking.daily_metrics (
        metric_date, 
        total_matches, 
        viewed_matches,
        accepted_matches, 
        rejected_matches,
        average_decision_time,
        average_match_score,
        average_feedback_rating,
        details,
        updated_at
    ) VALUES (
        p_date,
        COALESCE(v_total_matches, 0),
        COALESCE(v_viewed_matches, 0),
        COALESCE(v_accepted_matches, 0),
        COALESCE(v_rejected_matches, 0),
        v_avg_decision_time,
        v_avg_match_score,
        v_avg_feedback_rating,
        COALESCE(v_details, '{}'),
        NOW()
    )
    ON CONFLICT (metric_date) DO UPDATE
    SET 
        total_matches = COALESCE(v_total_matches, 0),
        viewed_matches = COALESCE(v_viewed_matches, 0),
        accepted_matches = COALESCE(v_accepted_matches, 0),
        rejected_matches = COALESCE(v_rejected_matches, 0),
        average_decision_time = v_avg_decision_time,
        average_match_score = v_avg_match_score,
        average_feedback_rating = v_avg_feedback_rating,
        details = COALESCE(v_details, '{}'),
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Fonction pour récupérer les événements non traités
CREATE OR REPLACE FUNCTION tracking.get_unprocessed_events(max_events INTEGER DEFAULT 1000)
RETURNS SETOF tracking.events AS $$
BEGIN
    RETURN QUERY
    SELECT e.*
    FROM tracking.events e
    LEFT JOIN tracking.events_processed ep ON e.event_id = ep.event_id
    WHERE ep.event_id IS NULL
    ORDER BY e.event_timestamp
    LIMIT max_events;
END;
$$ LANGUAGE plpgsql;

-- Table pour suivre les événements déjà traités
CREATE TABLE IF NOT EXISTS tracking.events_processed (
    event_id VARCHAR(64) PRIMARY KEY,
    processed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Index pour améliorer les performances des requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_events_type_timestamp ON tracking.events(event_type, event_timestamp);

-- Création d'un trigger pour la création automatique des partitions mensuelles
CREATE OR REPLACE FUNCTION tracking.create_next_partition_trigger()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM tracking.create_monthly_partition();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Déclenchement du trigger chaque premier jour du mois
DROP TRIGGER IF EXISTS create_next_partition_trigger ON tracking.events;
CREATE TRIGGER create_next_partition_trigger
    AFTER INSERT ON tracking.events
    EXECUTE PROCEDURE tracking.create_next_partition_trigger();

-- Octroi des droits sur les nouvelles tables et fonctions
GRANT SELECT, INSERT ON tracking.constraint_stats TO tracking_api;
GRANT SELECT, INSERT ON tracking.feedback_correlation TO tracking_api;
GRANT SELECT, INSERT ON tracking.feedback_aspects TO tracking_api;
GRANT SELECT, INSERT ON tracking.rejection_reasons TO tracking_api;
GRANT SELECT, INSERT ON tracking.match_view_metrics TO tracking_api;
GRANT SELECT, INSERT ON tracking.model_weights TO tracking_api;
GRANT SELECT, INSERT ON tracking.events_processed TO tracking_api;
GRANT EXECUTE ON FUNCTION tracking.create_monthly_partition TO tracking_api;
GRANT EXECUTE ON FUNCTION tracking.cleanup_old_partitions TO tracking_api;
GRANT EXECUTE ON FUNCTION tracking.aggregate_daily_metrics TO tracking_api;
GRANT EXECUTE ON FUNCTION tracking.get_unprocessed_events TO tracking_api;
