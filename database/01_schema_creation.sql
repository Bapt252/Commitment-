-- 1. Création des schémas par domaine
CREATE SCHEMA IF NOT EXISTS identity;       -- Gestion des utilisateurs
CREATE SCHEMA IF NOT EXISTS profiles;       -- Profils candidats et entreprises
CREATE SCHEMA IF NOT EXISTS jobs;           -- Offres d'emploi et candidatures
CREATE SCHEMA IF NOT EXISTS matching;       -- Algorithmes et résultats de matching
CREATE SCHEMA IF NOT EXISTS analytics;      -- Tables d'analyse et agrégations
CREATE SCHEMA IF NOT EXISTS audit;          -- Audit et logs

-- 2. Table des utilisateurs (identity schema)
CREATE TABLE identity.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_type VARCHAR(20) NOT NULL CHECK (user_type IN ('candidate', 'company', 'admin')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    profile_complete BOOLEAN DEFAULT FALSE,
    attributes JSONB DEFAULT '{}'
);

-- 3. Tables de profils (profiles schema)
CREATE TABLE profiles.candidates (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES identity.users(id) ON DELETE CASCADE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    phone VARCHAR(20),
    location VARCHAR(100),
    current_title VARCHAR(100),
    experience_years INTEGER,
    bio TEXT,
    resume_url VARCHAR(255),
    desired_salary_min DECIMAL(10,2),
    desired_salary_max DECIMAL(10,2),
    availability_date DATE,
    is_remote BOOLEAN DEFAULT FALSE,
    is_relocated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    attributes JSONB DEFAULT '{}'
);

CREATE TABLE profiles.companies (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES identity.users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    industry VARCHAR(100),
    website VARCHAR(255),
    logo_url VARCHAR(255),
    founded_year INTEGER,
    size VARCHAR(20) CHECK (size IN ('small', 'medium', 'large')),
    location VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    attributes JSONB DEFAULT '{}'
);

-- 4. Tables de compétences (profiles schema)
CREATE TABLE profiles.skill_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INTEGER REFERENCES profiles.skill_categories(id),
    level INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE profiles.skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    category_id INTEGER REFERENCES profiles.skill_categories(id),
    description TEXT,
    aliases TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE profiles.candidate_skills (
    candidate_id INTEGER REFERENCES profiles.candidates(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES profiles.skills(id) ON DELETE CASCADE,
    proficiency_level INTEGER CHECK (proficiency_level BETWEEN 1 AND 5),
    years_experience INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (candidate_id, skill_id)
);

-- 5. Tables d'offres d'emploi (jobs schema)
CREATE TABLE jobs.jobs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES profiles.companies(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(100),
    is_remote BOOLEAN DEFAULT FALSE,
    job_type VARCHAR(20) CHECK (job_type IN ('full-time', 'part-time', 'contract', 'internship')),
    experience_level VARCHAR(20) CHECK (experience_level IN ('entry', 'mid', 'senior', 'executive')),
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    posted_date TIMESTAMPTZ DEFAULT NOW(),
    deadline_date TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('draft', 'open', 'closed', 'filled')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    attributes JSONB DEFAULT '{}'
);

CREATE TABLE jobs.job_skills (
    job_id INTEGER REFERENCES jobs.jobs(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES profiles.skills(id) ON DELETE CASCADE,
    importance_level INTEGER CHECK (importance_level BETWEEN 1 AND 5),
    is_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (job_id, skill_id)
);

CREATE TABLE jobs.applications (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES profiles.candidates(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES jobs.jobs(id) ON DELETE CASCADE,
    cover_letter TEXT,
    status VARCHAR(20) DEFAULT 'submitted' CHECK (status IN ('submitted', 'under_review', 'interview', 'offer', 'rejected')),
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_application UNIQUE (candidate_id, job_id)
);

-- 6. Tables de matching (matching schema)
CREATE TABLE matching.matching_algorithms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parameters JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE matching.matches (
    id SERIAL PRIMARY KEY,
    candidate_id INTEGER NOT NULL REFERENCES profiles.candidates(id) ON DELETE CASCADE,
    job_id INTEGER NOT NULL REFERENCES jobs.jobs(id) ON DELETE CASCADE,
    match_score DECIMAL(5,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'viewed', 'interested', 'not_interested')),
    match_details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_candidate_job UNIQUE (candidate_id, job_id)
);

-- 7. Système de tags universels
CREATE TABLE profiles.tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(name, category)
);

CREATE TABLE profiles.entity_tags (
    id SERIAL PRIMARY KEY,
    tag_id INTEGER REFERENCES profiles.tags(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL CHECK (entity_type IN ('candidate', 'job', 'company', 'skill')),
    entity_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES identity.users(id),
    UNIQUE (tag_id, entity_type, entity_id)
);

-- 8. Table d'audit
CREATE TABLE audit.audit_logs (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    action VARCHAR(10) NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data JSONB,
    new_data JSONB,
    changed_fields JSONB,
    user_id UUID,
    ip_address VARCHAR(45),
    app_user VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Historisation des données
CREATE TABLE jobs.job_versions (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs.jobs(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(100),
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    attributes JSONB DEFAULT '{}',
    version_number INTEGER NOT NULL,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ,
    created_by UUID REFERENCES identity.users(id),
    EXCLUDE USING gist (job_id WITH =, tstzrange(valid_from, valid_to) WITH &&)
);

-- 10. Statistiques et analytics
CREATE TABLE analytics.daily_stats (
    date DATE PRIMARY KEY,
    new_users INTEGER DEFAULT 0,
    new_candidates INTEGER DEFAULT 0,
    new_jobs INTEGER DEFAULT 0,
    new_applications INTEGER DEFAULT 0,
    new_matches INTEGER DEFAULT 0,
    stats JSONB DEFAULT '{}'
);

-- 11. Configuration système
CREATE TABLE analytics.system_config (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    updated_by UUID REFERENCES identity.users(id)
);

-- 12. Événements utilisateur pour tracking comportemental
CREATE TABLE analytics.user_events (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES identity.users(id),
    event_type VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    session_id VARCHAR(100)
);