-- Schéma de base de données pour la personnalisation des matchs (Session 10)

-- Table des attributs pour la personnalisation
CREATE TABLE IF NOT EXISTS personalization_attributes (
    id SERIAL PRIMARY KEY,
    attribute_name VARCHAR(50) NOT NULL UNIQUE,
    default_weight FLOAT NOT NULL DEFAULT 1.0,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des poids personnalisés par utilisateur
CREATE TABLE IF NOT EXISTS user_attribute_weights (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    attribute_id INTEGER NOT NULL REFERENCES personalization_attributes(id) ON DELETE CASCADE,
    weight FLOAT NOT NULL DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, attribute_id)
);

-- Table des catégories pour la personnalisation
CREATE TABLE IF NOT EXISTS personalization_categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL UNIQUE,
    default_modifier FLOAT NOT NULL DEFAULT 1.0,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des modificateurs de catégories par utilisateur
CREATE TABLE IF NOT EXISTS user_category_modifiers (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER NOT NULL REFERENCES personalization_categories(id) ON DELETE CASCADE,
    modifier FLOAT NOT NULL DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, category_id)
);

-- Table pour le suivi des interactions utilisateur (pour le filtrage collaboratif)
CREATE TABLE IF NOT EXISTS user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    candidate_id INTEGER NOT NULL,
    interaction_type VARCHAR(20) NOT NULL, -- 'view', 'like', 'dislike', 'match', etc.
    interaction_value FLOAT, -- Valeur numérique de l'interaction (ex: score, durée)
    metadata JSONB, -- Métadonnées supplémentaires sur l'interaction
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX idx_user_interactions_candidate_id ON user_interactions(candidate_id);
CREATE INDEX idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX idx_user_interactions_created_at ON user_interactions(created_at);

-- Table des sessions utilisateur (pour les ajustements temporels)
CREATE TABLE IF NOT EXISTS user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_start TIMESTAMP WITH TIME ZONE NOT NULL,
    session_end TIMESTAMP WITH TIME ZONE,
    device_type VARCHAR(50),
    ip_address VARCHAR(50),
    location VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_session_start ON user_sessions(session_start);

-- Table des patterns temporels utilisateur
CREATE TABLE IF NOT EXISTS user_temporal_patterns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    day_of_week INTEGER, -- 0-6 (Dimanche-Samedi)
    hour_of_day INTEGER, -- 0-23
    activity_level FLOAT NOT NULL, -- Niveau d'activité normalisé (0-1)
    pattern_type VARCHAR(30), -- 'login', 'messaging', 'browsing', etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_user_temporal_patterns_user_id ON user_temporal_patterns(user_id);
CREATE INDEX idx_user_temporal_patterns_day_hour ON user_temporal_patterns(day_of_week, hour_of_day);

-- Table des tests A/B
CREATE TABLE IF NOT EXISTS ab_tests (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table des variantes de test A/B
CREATE TABLE IF NOT EXISTS ab_test_variants (
    id SERIAL PRIMARY KEY,
    test_id INTEGER NOT NULL REFERENCES ab_tests(id) ON DELETE CASCADE,
    variant_name VARCHAR(50) NOT NULL,
    description TEXT,
    distribution_weight FLOAT NOT NULL DEFAULT 1.0, -- Poids pour la distribution des utilisateurs
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (test_id, variant_name)
);
CREATE INDEX idx_ab_test_variants_test_id ON ab_test_variants(test_id);

-- Table des assignations utilisateur aux tests A/B
CREATE TABLE IF NOT EXISTS user_ab_test_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    variant_id INTEGER NOT NULL REFERENCES ab_test_variants(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, variant_id)
);
CREATE INDEX idx_user_ab_test_assignments_user_id ON user_ab_test_assignments(user_id);
CREATE INDEX idx_user_ab_test_assignments_variant_id ON user_ab_test_assignments(variant_id);

-- Table des métriques de test A/B
CREATE TABLE IF NOT EXISTS ab_test_metrics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    variant_id INTEGER NOT NULL REFERENCES ab_test_variants(id) ON DELETE CASCADE,
    metric_name VARCHAR(50) NOT NULL,
    metric_value FLOAT NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_ab_test_metrics_user_id ON ab_test_metrics(user_id);
CREATE INDEX idx_ab_test_metrics_variant_id ON ab_test_metrics(variant_id);
CREATE INDEX idx_ab_test_metrics_metric_name ON ab_test_metrics(metric_name);

-- Table pour les données de similarité utilisateur (pré-calculées)
CREATE TABLE IF NOT EXISTS user_similarity (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    similar_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    similarity_score FLOAT NOT NULL,
    last_calculated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, similar_user_id)
);
CREATE INDEX idx_user_similarity_user_id ON user_similarity(user_id);
CREATE INDEX idx_user_similarity_score ON user_similarity(similarity_score);

-- Table des paramètres de cold start
CREATE TABLE IF NOT EXISTS cold_start_parameters (
    id SERIAL PRIMARY KEY,
    parameter_name VARCHAR(50) NOT NULL UNIQUE,
    parameter_value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Vue pour obtenir tous les poids personnalisés d'un utilisateur
CREATE OR REPLACE VIEW user_personalization_profile AS
SELECT 
    u.id AS user_id,
    u.name,
    jsonb_object_agg(pa.attribute_name, COALESCE(uaw.weight, pa.default_weight)) AS attribute_weights,
    jsonb_object_agg(pc.category_name, COALESCE(ucm.modifier, pc.default_modifier)) AS category_modifiers
FROM 
    users u
CROSS JOIN personalization_attributes pa
CROSS JOIN personalization_categories pc
LEFT JOIN user_attribute_weights uaw ON u.id = uaw.user_id AND pa.id = uaw.attribute_id
LEFT JOIN user_category_modifiers ucm ON u.id = ucm.user_id AND pc.id = ucm.category_id
GROUP BY 
    u.id, u.name;

-- Fonction pour initialiser les poids par défaut pour un nouvel utilisateur
CREATE OR REPLACE FUNCTION initialize_user_personalization()
RETURNS TRIGGER AS $$
BEGIN
    -- Aucune insertion nécessaire, la vue user_personalization_profile utilise les valeurs par défaut
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Déclencher l'initialisation lors de la création d'un nouvel utilisateur
CREATE TRIGGER trigger_initialize_user_personalization
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION initialize_user_personalization();

-- Fonction pour mettre à jour les poids en fonction du feedback utilisateur
CREATE OR REPLACE FUNCTION update_weights_from_feedback(
    p_user_id INTEGER,
    p_candidate_id INTEGER,
    p_feedback_type VARCHAR,
    p_feedback_value FLOAT
)
RETURNS VOID AS $$
BEGIN
    -- Enregistrer l'interaction
    INSERT INTO user_interactions (
        user_id, candidate_id, interaction_type, interaction_value
    ) VALUES (
        p_user_id, p_candidate_id, p_feedback_type, p_feedback_value
    );
    
    -- Logique de mise à jour des poids selon le type de feedback
    -- Cette implémentation simplifiée devrait être étendue selon les besoins
    IF p_feedback_type = 'like' AND p_feedback_value > 0 THEN
        -- Exemple: augmenter les poids des attributs pertinents
        -- Code spécifique à implémenter
    ELSIF p_feedback_type = 'dislike' AND p_feedback_value > 0 THEN
        -- Exemple: diminuer les poids des attributs pertinents
        -- Code spécifique à implémenter
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Index supplémentaires pour les performances
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_candidate ON user_interactions(user_id, candidate_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_type_value ON user_interactions(interaction_type, interaction_value);
CREATE INDEX IF NOT EXISTS idx_user_temporal_patterns_user_pattern ON user_temporal_patterns(user_id, pattern_type);
