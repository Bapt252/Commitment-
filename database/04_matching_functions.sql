-- 1. Fonction pour calculer le score des compétences
CREATE OR REPLACE FUNCTION calculate_skills_score(
    p_candidate_id INTEGER,
    p_job_id INTEGER,
    p_weights JSONB DEFAULT NULL
) RETURNS TABLE (
    score DECIMAL(5,2),
    details JSONB
) AS $$
DECLARE
    v_required_weight DECIMAL(3,2) := COALESCE((p_weights->>'required_weight')::DECIMAL, 1.0);
    v_optional_weight DECIMAL(3,2) := COALESCE((p_weights->>'optional_weight')::DECIMAL, 0.5);
    v_score DECIMAL(5,2) := 0;
    v_missing_required BOOLEAN := FALSE;
    v_details JSONB;
    v_matching_skills JSONB;
    v_missing_skills JSONB;
BEGIN
    -- Vérifier les compétences requises
    SELECT 
        COUNT(js.skill_id) = 0 INTO v_missing_required
    FROM jobs.job_skills js
    WHERE js.job_id = p_job_id 
        AND js.is_required = TRUE
        AND NOT EXISTS (
            SELECT 1 FROM profiles.candidate_skills cs 
            WHERE cs.candidate_id = p_candidate_id 
            AND cs.skill_id = js.skill_id
        );
    
    -- Si des compétences requises manquent, pénaliser fortement
    IF v_missing_required THEN
        v_score := 0;
        
        -- Collecter les compétences manquantes pour les détails
        SELECT 
            jsonb_agg(
                jsonb_build_object(
                    'skill_id', js.skill_id,
                    'skill_name', s.name,
                    'importance', js.importance_level,
                    'required', js.is_required
                )
            ) INTO v_missing_skills
        FROM jobs.job_skills js
        JOIN profiles.skills s ON js.skill_id = s.id
        WHERE js.job_id = p_job_id 
        AND js.is_required = TRUE
        AND NOT EXISTS (
            SELECT 1 FROM profiles.candidate_skills cs 
            WHERE cs.candidate_id = p_candidate_id 
            AND cs.skill_id = js.skill_id
        );
    ELSE
        -- Calculer le score pondéré des compétences
        SELECT 
            COALESCE(
                SUM(
                    CASE 
                        WHEN js.is_required THEN cs.proficiency_level * js.importance_level * v_required_weight
                        ELSE COALESCE(cs.proficiency_level, 0) * js.importance_level * v_optional_weight
                    END
                ) / NULLIF(
                    SUM(
                        js.importance_level * 
                        CASE WHEN js.is_required 
                            THEN v_required_weight 
                            ELSE v_optional_weight 
                        END
                    ), 0
                ) * 20, 0
            ) INTO v_score
        FROM jobs.job_skills js
        LEFT JOIN profiles.candidate_skills cs ON js.skill_id = cs.skill_id AND cs.candidate_id = p_candidate_id
        WHERE js.job_id = p_job_id;
        
        -- Score sur 100
        v_score := LEAST(v_score, 100);
        
        -- Collecter les correspondances de compétences pour les détails
        SELECT 
            jsonb_agg(
                jsonb_build_object(
                    'skill_id', js.skill_id,
                    'skill_name', s.name,
                    'job_importance', js.importance_level,
                    'required', js.is_required,
                    'candidate_level', COALESCE(cs.proficiency_level, 0),
                    'match_quality', 
                        CASE 
                            WHEN cs.proficiency_level IS NULL THEN 'missing'
                            WHEN cs.proficiency_level >= js.importance_level THEN 'excellent'
                            WHEN cs.proficiency_level >= js.importance_level * 0.7 THEN 'good'
                            ELSE 'partial'
                        END
                )
            ) INTO v_matching_skills
        FROM jobs.job_skills js
        JOIN profiles.skills s ON js.skill_id = s.id
        LEFT JOIN profiles.candidate_skills cs ON js.skill_id = cs.skill_id AND cs.candidate_id = p_candidate_id
        WHERE js.job_id = p_job_id;
    END IF;
    
    -- Construire les détails du score
    v_details := jsonb_build_object(
        'score', v_score,
        'missing_required', v_missing_required,
        'matching_skills', COALESCE(v_matching_skills, '[]'::jsonb),
        'missing_skills', COALESCE(v_missing_skills, '[]'::jsonb)
    );
    
    score := v_score;
    details := v_details;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- 2. Fonction pour calculer le score d'expérience
CREATE OR REPLACE FUNCTION calculate_experience_score(
    p_candidate_id INTEGER,
    p_job_id INTEGER,
    p_weights JSONB DEFAULT NULL
) RETURNS TABLE (
    score DECIMAL(5,2),
    details JSONB
) AS $$
DECLARE
    v_score DECIMAL(5,2);
    v_details JSONB;
    v_job_exp_level VARCHAR(20);
    v_candidate_exp_years INTEGER;
    v_required_years INTEGER;
BEGIN
    -- Obtenir les informations d'expérience
    SELECT j.experience_level, c.experience_years
    INTO v_job_exp_level, v_candidate_exp_years
    FROM jobs.jobs j, profiles.candidates c
    WHERE j.id = p_job_id AND c.id = p_candidate_id;
    
    -- Mapper le niveau d'expérience requis en années
    v_required_years := 
        CASE v_job_exp_level
            WHEN 'entry' THEN 0
            WHEN 'mid' THEN 2
            WHEN 'senior' THEN 5
            WHEN 'executive' THEN 8
            ELSE 0
        END;
    
    -- Calculer le score d'expérience
    IF v_candidate_exp_years >= v_required_years THEN
        v_score := 100;
    ELSE
        -- Formule progressive : % de l'expérience requise
        v_score := LEAST((v_candidate_exp_years::DECIMAL / NULLIF(v_required_years, 0)) * 100, 100);
    END IF;
    
    -- Construire les détails pour l'explicabilité
    v_details := jsonb_build_object(
        'job_level', v_job_exp_level,
        'required_years', v_required_years,
        'candidate_years', v_candidate_exp_years,
        'meets_requirement', v_candidate_exp_years >= v_required_years,
        'score', v_score
    );
    
    score := v_score;
    details := v_details;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- 3. Fonction pour calculer le score de localisation
CREATE OR REPLACE FUNCTION calculate_location_score(
    p_candidate_id INTEGER,
    p_job_id INTEGER,
    p_weights JSONB DEFAULT NULL
) RETURNS TABLE (
    score DECIMAL(5,2),
    details JSONB
) AS $$
DECLARE
    v_job_location VARCHAR(100);
    v_job_remote BOOLEAN;
    v_candidate_location VARCHAR(100);
    v_candidate_remote BOOLEAN;
    v_candidate_relocated BOOLEAN;
    v_score DECIMAL(5,2);
    v_details JSONB;
    v_reason VARCHAR(100);
BEGIN
    -- Obtenir les informations de localisation
    SELECT j.location, j.is_remote, c.location, c.is_remote, c.is_relocated
    INTO v_job_location, v_job_remote, v_candidate_location, v_candidate_remote, v_candidate_relocated
    FROM jobs.jobs j, profiles.candidates c
    WHERE j.id = p_job_id AND c.id = p_candidate_id;

    -- Calculer le score de localisation
    IF v_job_remote AND v_candidate_remote THEN
        v_score := 100;
        v_reason := 'remote_match';
    ELSIF v_job_location = v_candidate_location THEN
        v_score := 100;
        v_reason := 'location_exact_match';
    ELSIF v_candidate_relocated THEN
        v_score := 80;
        v_reason := 'candidate_willing_to_relocate';
    ELSE
        -- Calcul de distance possible ici avec PostGIS si les coordonnées sont disponibles
        v_score := 0;
        v_reason := 'location_mismatch';
    END IF;
    
    -- Construire les détails pour l'explicabilité
    v_details := jsonb_build_object(
        'job_location', v_job_location,
        'job_remote', v_job_remote,
        'candidate_location', v_candidate_location,
        'candidate_remote', v_candidate_remote,
        'candidate_relocated', v_candidate_relocated,
        'score', v_score,
        'reason', v_reason
    );
    
    score := v_score;
    details := v_details;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- 4. Fonction principale de matching qui utilise toutes les sous-fonctions
CREATE OR REPLACE FUNCTION calculate_match_score(
    p_candidate_id INTEGER,
    p_job_id INTEGER,
    p_algorithm_id INTEGER DEFAULT NULL
)
RETURNS TABLE (
    total_score DECIMAL(5,2),
    score_breakdown JSONB,
    match_quality VARCHAR(20)
) AS $$
DECLARE
    v_algorithm_params JSONB;
    v_skills_weight DECIMAL(3,2);
    v_experience_weight DECIMAL(3,2);
    v_location_weight DECIMAL(3,2);
    v_skills_score DECIMAL(5,2);
    v_experience_score DECIMAL(5,2);
    v_location_score DECIMAL(5,2);
    v_skills_details JSONB;
    v_experience_details JSONB;
    v_location_details JSONB;
    v_total_score DECIMAL(5,2);
    v_score_breakdown JSONB;
    v_match_quality VARCHAR(20);
BEGIN
    -- Récupérer les paramètres de l'algorithme
    SELECT parameters INTO v_algorithm_params
    FROM matching.matching_algorithms
    WHERE id = COALESCE(
        p_algorithm_id, 
        (SELECT id FROM matching.matching_algorithms WHERE is_active ORDER BY id LIMIT 1)
    );
    
    -- Valeurs par défaut si aucun algorithme trouvé
    IF v_algorithm_params IS NULL THEN
        v_algorithm_params := '{
            "skills_weight": 0.6,
            "experience_weight": 0.3,
            "location_weight": 0.1,
            "skills_params": {
                "required_weight": 1.0,
                "optional_weight": 0.5
            }
        }';
    END IF;
    
    -- Extraire les poids
    v_skills_weight := COALESCE((v_algorithm_params->>'skills_weight')::DECIMAL, 0.6);
    v_experience_weight := COALESCE((v_algorithm_params->>'experience_weight')::DECIMAL, 0.3);
    v_location_weight := COALESCE((v_algorithm_params->>'location_weight')::DECIMAL, 0.1);
    
    -- Calculer les scores individuels
    SELECT score, details INTO v_skills_score, v_skills_details
    FROM calculate_skills_score(
        p_candidate_id, 
        p_job_id, 
        v_algorithm_params->'skills_params'
    );
    
    SELECT score, details INTO v_experience_score, v_experience_details
    FROM calculate_experience_score(
        p_candidate_id, 
        p_job_id, 
        v_algorithm_params->'experience_params'
    );
    
    SELECT score, details INTO v_location_score, v_location_details
    FROM calculate_location_score(
        p_candidate_id, 
        p_job_id, 
        v_algorithm_params->'location_params'
    );
    
    -- Calculer le score total pondéré
    v_total_score := (v_skills_score * v_skills_weight) +
                     (v_experience_score * v_experience_weight) +
                     (v_location_score * v_location_weight);
    
    -- Déterminer la qualité du match
    v_match_quality := 
        CASE 
            WHEN v_total_score >= 90 THEN 'excellent'
            WHEN v_total_score >= 75 THEN 'very_good'
            WHEN v_total_score >= 60 THEN 'good'
            WHEN v_total_score >= 40 THEN 'moderate'
            ELSE 'poor'
        END;
    
    -- Construire le détail complet du score
    v_score_breakdown := jsonb_build_object(
        'skills', jsonb_build_object('score', v_skills_score, 'weight', v_skills_weight, 'details', v_skills_details),
        'experience', jsonb_build_object('score', v_experience_score, 'weight', v_experience_weight, 'details', v_experience_details),
        'location', jsonb_build_object('score', v_location_score, 'weight', v_location_weight, 'details', v_location_details)
    );
    
    -- Retourner les résultats
    total_score := v_total_score;
    score_breakdown := v_score_breakdown;
    match_quality := v_match_quality;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;