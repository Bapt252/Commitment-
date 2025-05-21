-- Schéma de base de données pour la personnalisation utilisateur (Session 10)

-- Table des poids de matching personnalisés par utilisateur
CREATE TABLE IF NOT EXISTS user_matching_weights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    skills_weight FLOAT NOT NULL DEFAULT 0.30,
    contract_weight FLOAT NOT NULL DEFAULT 0.15,
    location_weight FLOAT NOT NULL DEFAULT 0.20,
    date_weight FLOAT NOT NULL DEFAULT 0.10,
    salary_weight FLOAT NOT NULL DEFAULT 0.15,
    experience_weight FLOAT NOT NULL DEFAULT 0.10,
    soft_skills_weight FLOAT NOT NULL DEFAULT 0.0,
    culture_weight FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_weights_user_id_unique UNIQUE (user_id)
);

-- Table d'historique des poids pour chaque utilisateur
CREATE TABLE IF NOT EXISTS user_matching_weights_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    skills_weight FLOAT NOT NULL,
    contract_weight FLOAT NOT NULL,
    location_weight FLOAT NOT NULL,
    date_weight FLOAT NOT NULL,
    salary_weight FLOAT NOT NULL,
    experience_weight FLOAT NOT NULL,
    soft_skills_weight FLOAT NOT NULL,
    culture_weight FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) NOT NULL -- 'user', 'system', 'ab_test', etc.
);

-- Table des similitudes entre utilisateurs (pour filtrage collaboratif)
CREATE TABLE IF NOT EXISTS user_similarities (
    id SERIAL PRIMARY KEY,
    user_id_1 INTEGER NOT NULL,
    user_id_2 INTEGER NOT NULL,
    similarity_score FLOAT NOT NULL,
    last_computed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_similarities_unique UNIQUE (user_id_1, user_id_2)
);

-- Table des préférences temporelles (importance du facteur temps)
CREATE TABLE IF NOT EXISTS user_temporal_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    recency_factor FLOAT NOT NULL DEFAULT 0.8, -- Facteur d'importance de la récence (0-1)
    change_rate FLOAT NOT NULL DEFAULT 0.5, -- Taux de changement estimé des préférences (0-1)
    stability_score FLOAT NOT NULL DEFAULT 0.5, -- Stabilité des préférences dans le temps (0-1)
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT user_temporal_prefs_unique UNIQUE (user_id)
);

-- Table de configuration des stratégies de cold start
CREATE TABLE IF NOT EXISTS cold_start_profiles (
    id SERIAL PRIMARY KEY,
    profile_name VARCHAR(100) NOT NULL,
    description TEXT,
    skills_weight FLOAT NOT NULL DEFAULT 0.30,
    contract_weight FLOAT NOT NULL DEFAULT 0.15,
    location_weight FLOAT NOT NULL DEFAULT 0.20,
    date_weight FLOAT NOT NULL DEFAULT 0.10,
    salary_weight FLOAT NOT NULL DEFAULT 0.15,
    experience_weight FLOAT NOT NULL DEFAULT 0.10,
    soft_skills_weight FLOAT NOT NULL DEFAULT 0.0,
    culture_weight FLOAT NOT NULL DEFAULT 0.0,
    conditions JSONB, -- Conditions d'application (ex: {"experience_level": "junior"})
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT cold_start_profile_unique UNIQUE (profile_name)
);

-- Table des tests A/B de personnalisation
CREATE TABLE IF NOT EXISTS personalization_ab_tests (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(100) NOT NULL,
    description TEXT,
    variants JSONB NOT NULL, -- Ex: ["historical", "recency_biased"]
    start_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'canceled'
    results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ab_test_name_unique UNIQUE (test_name)
);

-- Table d'assignation des utilisateurs aux variantes de test A/B
CREATE TABLE IF NOT EXISTS personalization_ab_test_assignments (
    id SERIAL PRIMARY KEY,
    test_id INTEGER NOT NULL REFERENCES personalization_ab_tests(id),
    user_id INTEGER NOT NULL,
    variant VARCHAR(100) NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ab_test_assignment_unique UNIQUE (test_id, user_id)
);

-- Table des feedbacks sur la personnalisation
CREATE TABLE IF NOT EXISTS personalization_feedback (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    job_id INTEGER,
    match_score FLOAT,
    user_rating FLOAT, -- Note donnée par l'utilisateur (1-5)
    feedback_text TEXT,
    context JSONB, -- Contexte de la personnalisation appliquée
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des matrices de factorisation pour la recommandation collaborative
CREATE TABLE IF NOT EXISTS collaborative_matrices (
    id SERIAL PRIMARY KEY,
    matrix_type VARCHAR(50) NOT NULL, -- 'user_factors', 'item_factors'
    dimensions INTEGER NOT NULL, -- Nombre de dimensions latentes
    data BYTEA NOT NULL, -- Matrice sérialisée
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indices pour optimiser les performances
CREATE INDEX IF NOT EXISTS idx_user_weights_user_id ON user_matching_weights(user_id);
CREATE INDEX IF NOT EXISTS idx_user_similarities_user_id_1 ON user_similarities(user_id_1);
CREATE INDEX IF NOT EXISTS idx_user_similarities_user_id_2 ON user_similarities(user_id_2);
CREATE INDEX IF NOT EXISTS idx_user_similarities_score ON user_similarities(similarity_score DESC);
CREATE INDEX IF NOT EXISTS idx_personalization_feedback_user_id ON personalization_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_personalization_feedback_job_id ON personalization_feedback(job_id);
CREATE INDEX IF NOT EXISTS idx_ab_test_assignments_user_id ON personalization_ab_test_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_ab_test_assignments_test_id ON personalization_ab_test_assignments(test_id);

-- Fonction pour mettre à jour la date de modification
CREATE OR REPLACE FUNCTION update_modified_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour la date de modification
CREATE TRIGGER update_user_weights_timestamp
BEFORE UPDATE ON user_matching_weights
FOR EACH ROW
EXECUTE PROCEDURE update_modified_timestamp();

-- Créer des profils cold start par défaut
INSERT INTO cold_start_profiles 
(profile_name, description, skills_weight, location_weight, contract_weight, salary_weight, experience_weight, conditions)
VALUES
('default', 'Profil par défaut pour les nouveaux utilisateurs', 0.30, 0.20, 0.15, 0.15, 0.20, '{}'),
('junior', 'Profil pour les débutants', 0.25, 0.15, 0.15, 0.20, 0.25, '{"experience_level": "junior", "years_experience_max": 3}'),
('senior', 'Profil pour les seniors', 0.35, 0.15, 0.10, 0.25, 0.15, '{"experience_level": "senior", "years_experience_min": 7}'),
('remote', 'Profil pour ceux qui préfèrent le télétravail', 0.30, 0.30, 0.15, 0.15, 0.10, '{"remote_preference": true}')
ON CONFLICT (profile_name) DO NOTHING;