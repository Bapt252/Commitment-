-- Schéma de base de données pour le système de tracking et collecte de données
-- Ce script crée les tables nécessaires pour le stockage des événements utilisateur,
-- des feedbacks et des données de consentement, tout en respectant les principes GDPR.

-- Création du schéma dédié aux données de tracking
CREATE SCHEMA IF NOT EXISTS tracking;

-- Table des consentements utilisateur
CREATE TABLE IF NOT EXISTS tracking.user_consents (
    consent_id SERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL, -- Identifiant anonymisé de l'utilisateur
    consent_type VARCHAR(50) NOT NULL, -- Type de consentement (analytics, marketing, etc.)
    is_granted BOOLEAN NOT NULL DEFAULT FALSE,
    granted_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE, -- Date d'expiration du consentement
    consent_version VARCHAR(20) NOT NULL, -- Version de la politique de confidentialité acceptée
    ip_address VARCHAR(45), -- IPv4/IPv6 de l'octroi du consentement
    user_agent TEXT, -- User-Agent du navigateur
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, consent_type)
);

-- Index pour accélérer les recherches de consentement
CREATE INDEX IF NOT EXISTS idx_user_consents_user_id ON tracking.user_consents(user_id);
CREATE INDEX IF NOT EXISTS idx_user_consents_expires_at ON tracking.user_consents(expires_at);

-- Table principale des événements utilisateur
CREATE TABLE IF NOT EXISTS tracking.events (
    event_id VARCHAR(64) PRIMARY KEY, -- UUID généré par l'application
    user_id VARCHAR(64) NOT NULL, -- Identifiant anonymisé de l'utilisateur
    session_id VARCHAR(64), -- Identifiant de session pour grouper les événements
    event_type VARCHAR(50) NOT NULL, -- Type d'événement (match_proposed, match_viewed, etc.)
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    client_timestamp TIMESTAMP WITH TIME ZONE, -- Timestamp côté client pour tracking de latence
    ip_address VARCHAR(45), -- IPv4/IPv6 anonymisé
    device_type VARCHAR(20), -- mobile, desktop, tablet
    os_name VARCHAR(30), -- Système d'exploitation
    browser_name VARCHAR(30), -- Navigateur utilisé
    app_version VARCHAR(20), -- Version de l'application
    referrer_url TEXT, -- URL de provenance (si applicable)
    user_agent TEXT, -- User-Agent du navigateur
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    metadata JSONB -- Données supplémentaires spécifiques à l'événement
);

-- Index pour accélérer les requêtes courantes
CREATE INDEX IF NOT EXISTS idx_events_user_id ON tracking.events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON tracking.events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_event_timestamp ON tracking.events(event_timestamp);
CREATE INDEX IF NOT EXISTS idx_events_session_id ON tracking.events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_metadata ON tracking.events USING GIN (metadata jsonb_path_ops);

-- Partitionnement de la table events par mois pour améliorer les performances
-- Nécessite PostgreSQL 10+
CREATE TABLE IF NOT EXISTS tracking.events_partitioned (
    LIKE tracking.events INCLUDING ALL
) PARTITION BY RANGE (event_timestamp);

-- Création des partitions initiales (6 mois à l'avance)
DO $$
DECLARE
    start_date DATE := DATE_TRUNC('month', CURRENT_DATE);
    end_date DATE;
BEGIN
    FOR i IN 0..5 LOOP
        start_date := DATE_TRUNC('month', CURRENT_DATE) + (i || ' month')::INTERVAL;
        end_date := DATE_TRUNC('month', CURRENT_DATE) + ((i+1) || ' month')::INTERVAL;
        
        EXECUTE format('CREATE TABLE IF NOT EXISTS tracking.events_%s PARTITION OF tracking.events_partitioned
                       FOR VALUES FROM (%L) TO (%L)',
                       TO_CHAR(start_date, 'YYYY_MM'),
                       start_date,
                       end_date);
    END LOOP;
END $$;

-- Table des événements de matching
CREATE TABLE IF NOT EXISTS tracking.match_events (
    event_id VARCHAR(64) PRIMARY KEY REFERENCES tracking.events(event_id),
    match_id VARCHAR(64) NOT NULL, -- Identifiant du match
    match_score NUMERIC(5,2), -- Score global du match (0-100)
    constraint_satisfaction JSONB, -- Détails sur la satisfaction des contraintes
    parameters JSONB, -- Paramètres utilisés pour ce match
    alternatives_count INTEGER, -- Nombre d'alternatives considérées
    view_duration_seconds NUMERIC(10,2), -- Durée de visualisation (pour events de type view)
    decision_time_seconds NUMERIC(10,2), -- Temps pris pour décider (pour events de décision)
    reasons TEXT[] -- Raisons données par l'utilisateur (acceptation/refus)
);

CREATE INDEX IF NOT EXISTS idx_match_events_match_id ON tracking.match_events(match_id);

-- Table des événements de feedback
CREATE TABLE IF NOT EXISTS tracking.feedback_events (
    event_id VARCHAR(64) PRIMARY KEY REFERENCES tracking.events(event_id),
    match_id VARCHAR(64) NOT NULL, -- Identifiant du match
    rating INTEGER CHECK (rating BETWEEN 1 AND 5), -- Note de 1 à 5
    feedback_text TEXT, -- Texte libre du feedback
    specific_aspects JSONB -- Notes par aspect spécifique
);

CREATE INDEX IF NOT EXISTS idx_feedback_events_match_id ON tracking.feedback_events(match_id);
CREATE INDEX IF NOT EXISTS idx_feedback_events_rating ON tracking.feedback_events(rating);

-- Table des événements d'interaction après matching
CREATE TABLE IF NOT EXISTS tracking.interaction_events (
    event_id VARCHAR(64) PRIMARY KEY REFERENCES tracking.events(event_id),
    match_id VARCHAR(64) NOT NULL, -- Identifiant du match
    interaction_type VARCHAR(50) NOT NULL, -- Type d'interaction (message, activité, etc.)
    interaction_count INTEGER, -- Nombre d'interactions dans cette session
    details JSONB -- Détails spécifiques à l'interaction
);

CREATE INDEX IF NOT EXISTS idx_interaction_events_match_id ON tracking.interaction_events(match_id);
CREATE INDEX IF NOT EXISTS idx_interaction_events_type ON tracking.interaction_events(interaction_type);

-- Table des événements de complétion d'engagement
CREATE TABLE IF NOT EXISTS tracking.completion_events (
    event_id VARCHAR(64) PRIMARY KEY REFERENCES tracking.events(event_id),
    match_id VARCHAR(64) NOT NULL, -- Identifiant du match
    duration_days NUMERIC(10,2), -- Durée de l'engagement en jours
    completion_rate NUMERIC(5,2), -- 0-100, niveau d'achèvement des objectifs
    success_indicators JSONB -- Indicateurs objectifs de succès
);

CREATE INDEX IF NOT EXISTS idx_completion_events_match_id ON tracking.completion_events(match_id);

-- Table des métriques agrégées quotidiennes
CREATE TABLE IF NOT EXISTS tracking.daily_metrics (
    metric_date DATE PRIMARY KEY,
    total_matches INTEGER NOT NULL DEFAULT 0,
    viewed_matches INTEGER NOT NULL DEFAULT 0,
    accepted_matches INTEGER NOT NULL DEFAULT 0,
    rejected_matches INTEGER NOT NULL DEFAULT 0,
    average_decision_time NUMERIC(10,2),
    average_match_score NUMERIC(5,2),
    average_feedback_rating NUMERIC(5,2),
    details JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Fonction pour supprimer les données anciennes (respect GDPR - droit à l'oubli)
CREATE OR REPLACE FUNCTION tracking.delete_user_data(p_user_id VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
    event_ids VARCHAR[];
BEGIN
    -- Récupérer tous les IDs d'événements de cet utilisateur
    SELECT ARRAY_AGG(event_id) INTO event_ids
    FROM tracking.events
    WHERE user_id = p_user_id;
    
    -- Supprimer les données liées dans les tables spécifiques
    DELETE FROM tracking.match_events WHERE event_id = ANY(event_ids);
    DELETE FROM tracking.feedback_events WHERE event_id = ANY(event_ids);
    DELETE FROM tracking.interaction_events WHERE event_id = ANY(event_ids);
    DELETE FROM tracking.completion_events WHERE event_id = ANY(event_ids);
    
    -- Supprimer les événements principaux
    DELETE FROM tracking.events WHERE user_id = p_user_id;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Supprimer les consentements
    DELETE FROM tracking.user_consents WHERE user_id = p_user_id;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour anonymiser les données utilisateur (alternative à la suppression)
CREATE OR REPLACE FUNCTION tracking.anonymize_user_data(p_user_id VARCHAR)
RETURNS INTEGER AS $$
DECLARE
    updated_count INTEGER := 0;
    anonymous_id VARCHAR := 'anon_' || MD5(p_user_id || RANDOM()::TEXT);
BEGIN
    -- Anonymiser l'ID utilisateur dans les événements
    UPDATE tracking.events
    SET user_id = anonymous_id,
        ip_address = NULL,
        user_agent = NULL,
        metadata = jsonb_strip_nulls(metadata - 'personal_data')
    WHERE user_id = p_user_id;
    GET DIAGNOSTICS updated_count = ROW_COUNT;
    
    -- Supprimer les consentements (ils ne sont plus nécessaires après anonymisation)
    DELETE FROM tracking.user_consents WHERE user_id = p_user_id;
    
    RETURN updated_count;
END;
$$ LANGUAGE plpgsql;

-- Vues pour faciliter l'analyse des données

-- Vue pour les métriques de matching
CREATE OR REPLACE VIEW tracking.match_metrics AS
SELECT
    e.event_timestamp::DATE AS date,
    e.event_type,
    COUNT(*) AS event_count,
    AVG(me.match_score) AS avg_match_score,
    AVG(me.decision_time_seconds) AS avg_decision_time
FROM tracking.events e
JOIN tracking.match_events me ON e.event_id = me.event_id
GROUP BY e.event_timestamp::DATE, e.event_type;

-- Vue pour les métriques de feedback
CREATE OR REPLACE VIEW tracking.feedback_metrics AS
SELECT
    e.event_timestamp::DATE AS date,
    AVG(fe.rating) AS avg_rating,
    COUNT(*) AS feedback_count,
    jsonb_object_agg(r.rating_value, r.rating_count) AS rating_distribution
FROM tracking.events e
JOIN tracking.feedback_events fe ON e.event_id = fe.event_id
CROSS JOIN LATERAL (
    SELECT 
        rating AS rating_value,
        COUNT(*) AS rating_count
    FROM tracking.feedback_events
    WHERE event_timestamp::DATE = e.event_timestamp::DATE
    GROUP BY rating
) r
GROUP BY e.event_timestamp::DATE;

-- Vue pour le suivi des sessions utilisateur
CREATE OR REPLACE VIEW tracking.user_sessions AS
SELECT
    session_id,
    user_id,
    MIN(event_timestamp) AS session_start,
    MAX(event_timestamp) AS session_end,
    MAX(event_timestamp) - MIN(event_timestamp) AS session_duration,
    COUNT(*) AS event_count,
    STRING_AGG(event_type, ' -> ' ORDER BY event_timestamp) AS event_flow
FROM tracking.events
WHERE session_id IS NOT NULL
GROUP BY session_id, user_id;

-- Création d'un rôle avec droits restreints pour l'API
CREATE ROLE tracking_api WITH LOGIN PASSWORD 'changeme_in_prod';

-- Octroi des droits minimum nécessaires
GRANT USAGE ON SCHEMA tracking TO tracking_api;
GRANT SELECT, INSERT ON tracking.events TO tracking_api;
GRANT SELECT, INSERT ON tracking.user_consents TO tracking_api;
GRANT SELECT, INSERT ON tracking.match_events TO tracking_api;
GRANT SELECT, INSERT ON tracking.feedback_events TO tracking_api;
GRANT SELECT, INSERT ON tracking.interaction_events TO tracking_api;
GRANT SELECT, INSERT ON tracking.completion_events TO tracking_api;
GRANT SELECT ON tracking.daily_metrics TO tracking_api;
GRANT EXECUTE ON FUNCTION tracking.delete_user_data TO tracking_api;
GRANT EXECUTE ON FUNCTION tracking.anonymize_user_data TO tracking_api;

-- Commentaire final
COMMENT ON SCHEMA tracking IS 'Schéma pour le système de tracking des événements utilisateur';
