-- Indexes pour optimiser les recherches

-- 1. Indexation des tables identity
CREATE INDEX idx_users_email ON identity.users (email);
CREATE INDEX idx_users_type ON identity.users (user_type);

-- 2. Indexation des tables profiles
CREATE INDEX idx_candidates_user_id ON profiles.candidates (user_id);
CREATE INDEX idx_candidates_location ON profiles.candidates (location);
CREATE INDEX idx_companies_user_id ON profiles.companies (user_id);
CREATE INDEX idx_companies_location ON profiles.companies (location);
CREATE INDEX idx_candidate_skills_skill ON profiles.candidate_skills (skill_id, proficiency_level);

-- 3. Indexation des tables jobs
CREATE INDEX idx_jobs_company ON jobs.jobs (company_id);
CREATE INDEX idx_jobs_title_trgm ON jobs.jobs USING gin (title gin_trgm_ops);
CREATE INDEX idx_jobs_description_fts ON jobs.jobs USING gin (to_tsvector('french', description));
CREATE INDEX idx_jobs_location ON jobs.jobs (location);
CREATE INDEX idx_jobs_type_level_remote ON jobs.jobs (job_type, experience_level, is_remote);
CREATE INDEX idx_job_skills_importance ON jobs.job_skills (skill_id, importance_level);
CREATE INDEX idx_applications_candidate ON jobs.applications (candidate_id);
CREATE INDEX idx_applications_job ON jobs.applications (job_id);
CREATE INDEX idx_applications_status ON jobs.applications (status);

-- 4. Indexation des tables matching
CREATE INDEX idx_matches_candidate ON matching.matches (candidate_id);
CREATE INDEX idx_matches_job ON matching.matches (job_id);
CREATE INDEX idx_matches_score ON matching.matches (match_score DESC);
CREATE INDEX idx_matches_candidate_status ON matching.matches (candidate_id, status);
CREATE INDEX idx_matches_job_status ON matching.matches (job_id, status);

-- 5. Indexation sur les JSONB pour recherches avancées
CREATE INDEX idx_candidates_attributes ON profiles.candidates USING GIN (attributes);
CREATE INDEX idx_jobs_attributes ON jobs.jobs USING GIN (attributes);
CREATE INDEX idx_companies_attributes ON profiles.companies USING GIN (attributes);

-- 6. Indexation des tables de tags
CREATE INDEX idx_entity_tags_entity ON profiles.entity_tags (entity_type, entity_id);
CREATE INDEX idx_entity_tags_tag ON profiles.entity_tags (tag_id);

-- 7. Indexation des tables d'audit
CREATE INDEX idx_audit_entity ON audit.audit_logs (entity_type, entity_id);
CREATE INDEX idx_audit_time ON audit.audit_logs (created_at);
CREATE INDEX idx_audit_user ON audit.audit_logs (user_id);

-- 8. Indexation de tracking utilisateur
CREATE INDEX idx_user_events_user ON analytics.user_events (user_id, created_at);
CREATE INDEX idx_user_events_type ON analytics.user_events (event_type, created_at);

-- Partitionnement pour les grosses tables

-- 1. Table des matches partitionnée par date
CREATE TABLE matching.matches_partitioned (
    id SERIAL,
    candidate_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    match_score DECIMAL(5,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    match_details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_candidate_job_part UNIQUE (candidate_id, job_id)
) PARTITION BY RANGE (created_at);

-- Créer les partitions initiales par trimestre
CREATE TABLE matching.matches_2025_q1 PARTITION OF matching.matches_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
    
CREATE TABLE matching.matches_2025_q2 PARTITION OF matching.matches_partitioned
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
    
CREATE TABLE matching.matches_2025_q3 PARTITION OF matching.matches_partitioned
    FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
    
CREATE TABLE matching.matches_2025_q4 PARTITION OF matching.matches_partitioned
    FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');

-- 2. Table des applications partitionnée par hash (pour distribuer la charge)
CREATE TABLE jobs.applications_partitioned (
    id SERIAL,
    candidate_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    cover_letter TEXT,
    status VARCHAR(20) DEFAULT 'submitted',
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_application_part UNIQUE (candidate_id, job_id)
) PARTITION BY HASH (candidate_id);

-- Créer 8 partitions
CREATE TABLE jobs.applications_part_0 PARTITION OF jobs.applications_partitioned
    FOR VALUES WITH (MODULUS 8, REMAINDER 0);
    
CREATE TABLE jobs.applications_part_1 PARTITION OF jobs.applications_partitioned
    FOR VALUES WITH (MODULUS 8, REMAINDER 1);
    
CREATE TABLE jobs.applications_part_2 PARTITION OF jobs.applications_partitioned
    FOR VALUES WITH (MODULUS 8, REMAINDER 2);
    
CREATE TABLE jobs.applications_part_3 PARTITION OF jobs.applications_partitioned
    FOR VALUES WITH (MODULUS 8, REMAINDER 3);
    
CREATE TABLE jobs.applications_part_4 PARTITION OF jobs.applications_partitioned
    FOR VALUES WITH (MODULUS 8, REMAINDER 4);
    
CREATE TABLE jobs.applications_part_5 PARTITION OF jobs.applications_partitioned
    FOR VALUES WITH (MODULUS 8, REMAINDER 5);
    
CREATE TABLE jobs.applications_part_6 PARTITION OF jobs.applications_partitioned
    FOR VALUES WITH (MODULUS 8, REMAINDER 6);
    
CREATE TABLE jobs.applications_part_7 PARTITION OF jobs.applications_partitioned
    FOR VALUES WITH (MODULUS 8, REMAINDER 7);

-- 3. Vues matérialisées pour les requêtes complexes
CREATE MATERIALIZED VIEW profiles.candidate_skill_summary AS
SELECT 
    c.id AS candidate_id,
    c.first_name,
    c.last_name,
    array_agg(s.name) AS skills,
    avg(cs.proficiency_level) AS avg_skill_level
FROM profiles.candidates c
JOIN profiles.candidate_skills cs ON c.id = cs.candidate_id
JOIN profiles.skills s ON cs.skill_id = s.id
GROUP BY c.id, c.first_name, c.last_name
WITH DATA;

CREATE UNIQUE INDEX ON profiles.candidate_skill_summary (candidate_id);

-- 4. Vues pour l'isolation des données entre services
CREATE OR REPLACE VIEW matching.candidate_profiles AS
SELECT 
    c.id,
    c.user_id,
    c.first_name,
    c.last_name,
    c.experience_years,
    c.location,
    c.is_remote,
    c.is_relocated
FROM profiles.candidates c;

CREATE OR REPLACE VIEW matching.job_listings AS
SELECT 
    j.id,
    j.company_id,
    j.title,
    j.location,
    j.is_remote,
    j.experience_level,
    j.status
FROM jobs.jobs j
WHERE j.status = 'open';

CREATE OR REPLACE VIEW jobs.available_skills AS
SELECT id, name, category_id, description
FROM profiles.skills;

CREATE OR REPLACE VIEW analytics.public_stats AS
SELECT
    date,
    new_jobs,
    new_candidates,
    stats->'top_skills' AS top_skills,
    stats->'job_categories' AS job_categories
FROM analytics.daily_stats
WHERE date >= current_date - interval '30 days';