-- 07_advanced_optimizations.sql
-- Optimisations avancées pour Nexten - Structure, Performance, et Sécurité

-------------------------------------------
-- 1. Extensions PostgreSQL supplémentaires
-------------------------------------------

-- Extension pour les fonctionnalités géospatiales
CREATE EXTENSION IF NOT EXISTS postgis;

-- Extension pour la recherche textuelle avancée
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Extension pour le chiffrement des données sensibles
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Extension pour le monitoring des requêtes
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Extension pour l'analyse des performances
CREATE EXTENSION IF NOT EXISTS auto_explain;

-------------------------------------------
-- 2. Améliorations du modèle de données
-------------------------------------------

-- Amélioration de la structure des localisations avec PostGIS
CREATE TABLE profiles.locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    country VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    geo_point GEOGRAPHY(POINT),  -- Point géographique (latitude, longitude)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_locations_geo ON profiles.locations USING GIST (geo_point);
CREATE INDEX idx_locations_city_country ON profiles.locations (city, country);

-- Mise à jour des tables utilisant des localisations
ALTER TABLE profiles.candidates 
    ADD COLUMN location_id INTEGER REFERENCES profiles.locations(id),
    ADD COLUMN preferred_locations INTEGER[] DEFAULT '{}';  -- Array d'IDs de locations préférées

ALTER TABLE profiles.companies 
    ADD COLUMN location_id INTEGER REFERENCES profiles.locations(id);

ALTER TABLE jobs.jobs 
    ADD COLUMN location_id INTEGER REFERENCES profiles.locations(id);

-- Structure améliorée pour la gestion des langues
CREATE TABLE profiles.languages (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL UNIQUE,  -- ISO code (fr, en, de, etc.)
    name VARCHAR(100) NOT NULL
);

CREATE TABLE profiles.candidate_languages (
    candidate_id INTEGER REFERENCES profiles.candidates(id) ON DELETE CASCADE,
    language_id INTEGER REFERENCES profiles.languages(id) ON DELETE CASCADE,
    proficiency_level VARCHAR(2) NOT NULL CHECK (proficiency_level IN ('A1', 'A2', 'B1', 'B2', 'C1', 'C2')),
    is_native BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (candidate_id, language_id)
);

-- Table pour les préférences et paramètres utilisateurs 
CREATE TABLE identity.user_preferences (
    user_id UUID PRIMARY KEY REFERENCES identity.users(id) ON DELETE CASCADE,
    email_notifications JSONB DEFAULT '{"job_matches": true, "applications": true, "messages": true}'::jsonb,
    visibility_settings JSONB DEFAULT '{"profile": "public", "resume": "private"}'::jsonb,
    interface_settings JSONB DEFAULT '{"theme": "light", "language": "fr"}'::jsonb,
    matching_preferences JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-------------------------------------------
-- 3. Optimisations pour le matching
-------------------------------------------

-- Structure enrichie pour les résultats de matching
ALTER TABLE matching.matches
    ADD COLUMN skill_match_score DECIMAL(5,2),
    ADD COLUMN experience_match_score DECIMAL(5,2),
    ADD COLUMN education_match_score DECIMAL(5,2),
    ADD COLUMN location_match_score DECIMAL(5,2),
    ADD COLUMN algorithm_version VARCHAR(20);

-- Partitionnement avancé de la table de matching par score
CREATE TABLE matching.matches_by_score (
    id SERIAL,
    candidate_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    match_score DECIMAL(5,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    match_details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_candidate_job_score UNIQUE (candidate_id, job_id)
) PARTITION BY RANGE (match_score);

-- Partitions pour les différentes plages de scores
CREATE TABLE matching.matches_score_low PARTITION OF matching.matches_by_score
    FOR VALUES FROM (0) TO (50);
    
CREATE TABLE matching.matches_score_medium PARTITION OF matching.matches_by_score
    FOR VALUES FROM (50) TO (75);
    
CREATE TABLE matching.matches_score_high PARTITION OF matching.matches_by_score
    FOR VALUES FROM (75) TO (90);
    
CREATE TABLE matching.matches_score_excellent PARTITION OF matching.matches_by_score
    FOR VALUES FROM (90) TO (101);

-- Indexes pour optimiser les recherches sur les partitions
CREATE INDEX idx_matches_score_low_candidate ON matching.matches_score_low (candidate_id, match_score DESC);
CREATE INDEX idx_matches_score_medium_candidate ON matching.matches_score_medium (candidate_id, match_score DESC);
CREATE INDEX idx_matches_score_high_candidate ON matching.matches_score_high (candidate_id, match_score DESC);
CREATE INDEX idx_matches_score_excellent_candidate ON matching.matches_score_excellent (candidate_id, match_score DESC);

-- Vue matérialisée pour les candidats les mieux notés par compétence
CREATE MATERIALIZED VIEW matching.top_candidates_by_skill AS
SELECT 
    s.id AS skill_id,
    s.name AS skill_name,
    cs.candidate_id,
    c.first_name,
    c.last_name,
    cs.proficiency_level,
    cs.years_experience,
    RANK() OVER (PARTITION BY s.id ORDER BY cs.proficiency_level DESC, cs.years_experience DESC) as skill_rank
FROM profiles.skills s
JOIN profiles.candidate_skills cs ON s.id = cs.skill_id
JOIN profiles.candidates c ON cs.candidate_id = c.id
WHERE cs.proficiency_level >= 4
WITH DATA;

CREATE UNIQUE INDEX idx_top_candidates_by_skill ON matching.top_candidates_by_skill (skill_id, candidate_id);

-- Vue matérialisée pour les offres d'emploi par zone géographique
CREATE MATERIALIZED VIEW jobs.jobs_by_location AS
SELECT 
    l.id AS location_id,
    l.city,
    l.country,
    COUNT(j.id) AS job_count,
    ARRAY_AGG(j.id) AS job_ids,
    ST_Centroid(ST_Collect(l.geo_point::geometry)) AS center_point
FROM profiles.locations l
JOIN jobs.jobs j ON l.id = j.location_id
WHERE j.status = 'open'
GROUP BY l.id, l.city, l.country
WITH DATA;

CREATE UNIQUE INDEX idx_jobs_by_location ON jobs.jobs_by_location (location_id);

-------------------------------------------
-- 4. Sécurité et chiffrement des données
-------------------------------------------

-- Table pour stocker les données sensibles chiffrées
CREATE TABLE identity.encrypted_data (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES identity.users(id) ON DELETE CASCADE,
    data_type VARCHAR(50) NOT NULL,  -- 'ssn', 'tax_id', 'salary_history', etc.
    encrypted_data BYTEA NOT NULL,
    iv BYTEA NOT NULL,  -- Vecteur d'initialisation
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (user_id, data_type)
);

CREATE INDEX idx_encrypted_data_user ON identity.encrypted_data (user_id);

-- Fonction pour chiffrer des données sensibles
CREATE OR REPLACE FUNCTION identity.encrypt_sensitive_data(
    p_plain_text TEXT,
    p_key TEXT
) RETURNS TABLE(encrypted_value BYTEA, initialization_vector BYTEA) AS $$
DECLARE
    v_iv BYTEA;
    v_encrypted BYTEA;
BEGIN
    -- Générer un vecteur d'initialisation aléatoire
    v_iv := gen_random_bytes(16);
    
    -- Chiffrer avec AES-256 en mode CBC
    v_encrypted := encrypt_iv(
        p_plain_text::BYTEA,
        digest(p_key, 'sha256'),
        v_iv,
        'aes-cbc'
    );
    
    RETURN QUERY SELECT v_encrypted, v_iv;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Fonction pour déchiffrer des données sensibles
CREATE OR REPLACE FUNCTION identity.decrypt_sensitive_data(
    p_encrypted_value BYTEA,
    p_iv BYTEA,
    p_key TEXT
) RETURNS TEXT AS $$
DECLARE
    v_decrypted TEXT;
BEGIN
    -- Déchiffrer la valeur
    v_decrypted := convert_from(
        decrypt_iv(
            p_encrypted_value,
            digest(p_key, 'sha256'),
            p_iv,
            'aes-cbc'
        ),
        'UTF8'
    );
    
    RETURN v_decrypted;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Créer des politiques RLS (Row Level Security) pour les tables sensibles
ALTER TABLE identity.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles.candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE identity.encrypted_data ENABLE ROW LEVEL SECURITY;

-- Politique pour les utilisateurs (accès à leurs propres données uniquement)
CREATE POLICY user_self_access ON identity.users
    USING (id = current_setting('app.user_id', TRUE)::UUID);

-- Politique pour les candidats
CREATE POLICY candidate_self_access ON profiles.candidates
    USING (user_id = current_setting('app.user_id', TRUE)::UUID);

-- Politique pour les données chiffrées
CREATE POLICY encrypted_data_self_access ON identity.encrypted_data
    USING (user_id = current_setting('app.user_id', TRUE)::UUID);

-- Vue anonymisée pour les analyses statistiques
CREATE VIEW analytics.anonymous_candidate_data AS
SELECT
    -- Utiliser un hash comme identifiant
    encode(digest(c.id::text, 'sha256'), 'hex') AS candidate_hash,
    -- Données générales non sensibles
    c.experience_years,
    l.country,
    l.city,
    -- Tranche d'âge plutôt que date de naissance
    CASE 
        WHEN EXTRACT(YEAR FROM AGE(NOW(), c.date_of_birth)) < 25 THEN '18-25'
        WHEN EXTRACT(YEAR FROM AGE(NOW(), c.date_of_birth)) BETWEEN 25 AND 34 THEN '25-34'
        WHEN EXTRACT(YEAR FROM AGE(NOW(), c.date_of_birth)) BETWEEN 35 AND 44 THEN '35-44'
        WHEN EXTRACT(YEAR FROM AGE(NOW(), c.date_of_birth)) BETWEEN 45 AND 54 THEN '45-54'
        ELSE '55+'
    END AS age_range,
    -- Tranche salariale plutôt que salaire exact
    CASE
        WHEN c.desired_salary_min < 30000 THEN 'below_30k'
        WHEN c.desired_salary_min BETWEEN 30000 AND 50000 THEN '30k_50k'
        WHEN c.desired_salary_min BETWEEN 50001 AND 70000 THEN '50k_70k'
        WHEN c.desired_salary_min BETWEEN 70001 AND 100000 THEN '70k_100k'
        ELSE 'above_100k'
    END AS salary_range,
    -- Statistiques d'activité
    COUNT(DISTINCT a.id) AS application_count,
    AVG(m.match_score) AS avg_match_score
FROM profiles.candidates c
LEFT JOIN profiles.locations l ON c.location_id = l.id
LEFT JOIN jobs.applications a ON c.id = a.candidate_id
LEFT JOIN matching.matches m ON c.id = m.candidate_id
GROUP BY 
    c.id,
    c.experience_years,
    l.country,
    l.city,
    c.date_of_birth,
    c.desired_salary_min;

-------------------------------------------
-- 5. Optimisations de performances
-------------------------------------------

-- Améliorations des index existants

-- Index composites optimisés pour les recherches fréquentes
CREATE INDEX idx_candidates_location_experience ON profiles.candidates 
    (location_id, experience_years);

CREATE INDEX idx_candidates_skill_proficiency ON profiles.candidate_skills 
    (candidate_id, skill_id, proficiency_level DESC);

-- Index GIN pour les recherches textuelles avec poids différents
CREATE INDEX idx_candidates_fulltext ON profiles.candidates USING GIN (
    setweight(to_tsvector('french', COALESCE(first_name, '')), 'A') || 
    setweight(to_tsvector('french', COALESCE(last_name, '')), 'A') || 
    setweight(to_tsvector('french', COALESCE(current_title, '')), 'B') ||
    setweight(to_tsvector('french', COALESCE(bio, '')), 'C')
);

CREATE INDEX idx_jobs_fulltext ON jobs.jobs USING GIN (
    setweight(to_tsvector('french', COALESCE(title, '')), 'A') || 
    setweight(to_tsvector('french', COALESCE(description, '')), 'B')
);

-- Index conditionnels pour les offres actives uniquement
CREATE INDEX idx_active_jobs ON jobs.jobs (company_id, title) 
    WHERE status = 'open';

-- Index pour l'optimisation des requêtes d'applications récentes
CREATE INDEX idx_recent_applications ON jobs.applications (job_id, submitted_at DESC)
    WHERE submitted_at > (CURRENT_DATE - INTERVAL '30 days');

-- Vues matérialisées pour les statistiques et dashboards

-- Stats par compétence
CREATE MATERIALIZED VIEW analytics.skill_stats AS
SELECT 
    s.id AS skill_id,
    s.name AS skill_name,
    s.category_id,
    COUNT(DISTINCT cs.candidate_id) AS candidate_count,
    AVG(cs.proficiency_level) AS avg_proficiency,
    COUNT(DISTINCT js.job_id) AS job_count,
    COUNT(DISTINCT js.job_id) FILTER (WHERE j.status = 'open') AS active_job_count
FROM profiles.skills s
LEFT JOIN profiles.candidate_skills cs ON s.id = cs.skill_id
LEFT JOIN jobs.job_skills js ON s.id = js.skill_id
LEFT JOIN jobs.jobs j ON js.job_id = j.id
GROUP BY s.id, s.name, s.category_id
WITH DATA;

CREATE UNIQUE INDEX idx_skill_stats ON analytics.skill_stats (skill_id);

-- Stats pour les recruteurs (dashboard entreprise)
CREATE MATERIALIZED VIEW analytics.company_stats AS
SELECT 
    c.id AS company_id,
    c.name AS company_name,
    COUNT(DISTINCT j.id) AS total_jobs,
    COUNT(DISTINCT j.id) FILTER (WHERE j.status = 'open') AS active_jobs,
    COUNT(DISTINCT a.id) AS total_applications,
    COUNT(DISTINCT a.id) FILTER (WHERE a.status = 'submitted') AS new_applications,
    COUNT(DISTINCT a.id) FILTER (WHERE a.status = 'interview') AS in_interview,
    COUNT(DISTINCT a.id) FILTER (WHERE a.status = 'offer') AS offers_sent,
    COUNT(DISTINCT a.id) FILTER (WHERE a.status = 'rejected') AS rejected,
    ROUND(AVG(j.salary_min)) AS avg_salary_min,
    ROUND(AVG(j.salary_max)) AS avg_salary_max
FROM profiles.companies c
LEFT JOIN jobs.jobs j ON c.id = j.company_id
LEFT JOIN jobs.applications a ON j.id = a.job_id
GROUP BY c.id, c.name
WITH DATA;

CREATE UNIQUE INDEX idx_company_stats ON analytics.company_stats (company_id);

-------------------------------------------
-- 6. Procédure de maintenance automatisée
-------------------------------------------

CREATE OR REPLACE PROCEDURE maintenance.refresh_materialized_views() 
LANGUAGE plpgsql
AS $$
BEGIN
    -- Rafraîchir les vues matérialisées
    REFRESH MATERIALIZED VIEW CONCURRENTLY profiles.candidate_skill_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY matching.top_candidates_by_skill;
    REFRESH MATERIALIZED VIEW CONCURRENTLY jobs.jobs_by_location;
    REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.skill_stats;
    REFRESH MATERIALIZED VIEW CONCURRENTLY analytics.company_stats;
END;
$$;

CREATE OR REPLACE PROCEDURE maintenance.create_partitions_for_next_quarter() 
LANGUAGE plpgsql
AS $$
DECLARE
    next_quarter_start DATE;
    next_quarter_end DATE;
    partition_name TEXT;
    table_name TEXT;
BEGIN
    -- Calculer la date de début du prochain trimestre
    next_quarter_start := DATE_TRUNC('quarter', CURRENT_DATE + INTERVAL '3 months')::DATE;
    next_quarter_end := next_quarter_start + INTERVAL '3 months';
    
    -- Nommer la partition 
    partition_name := 'matching_results_' || 
                      TO_CHAR(next_quarter_start, 'YYYY') || '_q' || 
                      TO_CHAR(EXTRACT(QUARTER FROM next_quarter_start), '9');
    
    -- Créer partition pour matching_results
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS matching.%I PARTITION OF matching.matches_partitioned
        FOR VALUES FROM (%L) TO (%L)
    ', partition_name, next_quarter_start, next_quarter_end);
    
    -- Créer indexes sur la nouvelle partition
    EXECUTE format('
        CREATE INDEX IF NOT EXISTS idx_%I_candidate ON matching.%I (candidate_id, match_score DESC);
        CREATE INDEX IF NOT EXISTS idx_%I_job ON matching.%I (job_id, match_score DESC);
    ', partition_name, partition_name, partition_name, partition_name);
    
    -- Faire de même pour la table d'audit
    partition_name := 'audit_logs_' || 
                      TO_CHAR(next_quarter_start, 'YYYY') || '_q' || 
                      TO_CHAR(EXTRACT(QUARTER FROM next_quarter_start), '9');
                      
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS audit.%I PARTITION OF audit.audit_logs
        FOR VALUES FROM (%L) TO (%L)
    ', partition_name, next_quarter_start, next_quarter_end);
    
    -- Créer indexes sur la nouvelle partition d'audit
    EXECUTE format('
        CREATE INDEX IF NOT EXISTS idx_%I_entity ON audit.%I (entity_type, entity_id);
        CREATE INDEX IF NOT EXISTS idx_%I_created ON audit.%I (created_at);
    ', partition_name, partition_name, partition_name, partition_name);
    
    -- Log l'opération
    RAISE NOTICE 'Created partitions for % to %', next_quarter_start, next_quarter_end;
END;
$$;

-- Procédure pour mettre à jour les statistiques PostgreSQL pour les tables principales
CREATE OR REPLACE PROCEDURE maintenance.analyze_critical_tables()
LANGUAGE plpgsql
AS $$
BEGIN
    ANALYZE VERBOSE identity.users;
    ANALYZE VERBOSE profiles.candidates;
    ANALYZE VERBOSE profiles.candidate_skills;
    ANALYZE VERBOSE jobs.jobs;
    ANALYZE VERBOSE jobs.job_skills;
    ANALYZE VERBOSE jobs.applications;
    ANALYZE VERBOSE matching.matches;
END;
$$;

-------------------------------------------
-- 7. Configuration PostgreSQL recommandée
-------------------------------------------

COMMENT ON DATABASE nexten IS 'Configuration PostgreSQL recommandée:

# Mémoire et ressources
shared_buffers = 4GB                     # 25% de la RAM totale
effective_cache_size = 12GB              # 75% de la RAM totale
work_mem = 64MB                          # Pour les tris et les hash joins
maintenance_work_mem = 1GB               # Pour les opérations de maintenance
max_worker_processes = 8                 # Nombre de cœurs disponibles
max_parallel_workers_per_gather = 4      # Parallélisme pour les scans séquentiels

# WAL et journalisation
wal_level = replica                      # Minimum requis pour la réplication
checkpoint_timeout = 15min               # Intervalle entre les checkpoints
max_wal_size = 16GB                      # Taille maximum des WAL
min_wal_size = 2GB                       # Taille minimum des WAL

# Optimisations pour SSD
random_page_cost = 1.1                   # Coût d''accès aléatoire réduit pour SSD
effective_io_concurrency = 200           # IO parallèles pour SSD

# Vacuum et maintenance
autovacuum = on                          # Activé
autovacuum_max_workers = 5               # Nombre de processus autovacuum
autovacuum_vacuum_scale_factor = 0.05    # Seuil de déclenchement
autovacuum_analyze_scale_factor = 0.025  # Seuil d''analyse
autovacuum_naptime = 10s                 # Période d''attente entre deux passages

# Statistiques et monitoring
track_activities = on                    # Suivi des requêtes actives
track_counts = on                        # Statistiques pour autovacuum
track_io_timing = on                     # Mesure des temps d''IO
track_functions = all                    # Suivi des fonctions
log_statement = ''ddl''                  # Enregistrer les opérations DDL
log_min_duration_statement = 1000        # Enregistrer les requêtes lentes (1s)

# Extensions
shared_preload_libraries = ''pg_stat_statements,auto_explain''  # Monitoring avancé
';

-- Créer un index finalisé pour le README
COMMENT ON SCHEMA matching IS 'Schéma contenant les algorithmes et résultats de matching. Ces tables sont optimisées pour:
1. Recherches rapides par candidat ou offre
2. Filtrage par score de matching
3. Partitionnement par date et par score
4. Stockage des détails de matching au format JSONB indexé';
