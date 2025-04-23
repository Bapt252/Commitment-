-- 1. Fonction pour le contexte d'audit
CREATE OR REPLACE FUNCTION set_app_context(
    p_user_id UUID,
    p_ip_address VARCHAR DEFAULT NULL,
    p_app_user VARCHAR DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    -- Stocker les informations dans une variable de session
    PERFORM set_config('app.user_id', COALESCE(p_user_id::TEXT, ''), FALSE);
    PERFORM set_config('app.ip_address', COALESCE(p_ip_address, 'unknown'), FALSE);
    PERFORM set_config('app.app_user', COALESCE(p_app_user, 'system'), FALSE);
END;
$$ LANGUAGE plpgsql;

-- 2. Fonction trigger générique pour l'audit
CREATE OR REPLACE FUNCTION audit_trigger_func()
RETURNS TRIGGER AS $$
DECLARE
    v_old_data JSONB;
    v_new_data JSONB;
    v_changed_fields JSONB;
    v_entity_id INTEGER;
    v_user_id UUID;
    v_app_user VARCHAR;
    v_ip_address VARCHAR;
    v_include_row BOOLEAN := TRUE;
BEGIN
    -- Récupérer le contexte d'application
    v_user_id := NULLIF(current_setting('app.user_id', TRUE), '')::UUID;
    v_app_user := NULLIF(current_setting('app.app_user', TRUE), '');
    v_ip_address := NULLIF(current_setting('app.ip_address', TRUE), '');
    
    -- Déterminer le type d'opération
    IF (TG_OP = 'INSERT') THEN
        v_entity_id := NEW.id;
        v_old_data := NULL;
        v_new_data := to_jsonb(NEW);
        v_changed_fields := v_new_data;
    ELSIF (TG_OP = 'UPDATE') THEN
        v_entity_id := NEW.id;
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        
        -- Calculer les champs modifiés
        v_changed_fields := jsonb_object_agg(
            key,
            v_new_data->key
        ) FROM jsonb_each(v_new_data)
        WHERE v_old_data->key IS DISTINCT FROM v_new_data->key;
        
        -- Ne pas enregistrer si aucun changement réel (sauf updated_at)
        IF (v_changed_fields ?& ARRAY['updated_at'] AND jsonb_array_length(jsonb_object_keys(v_changed_fields)) = 1) THEN
            v_include_row := FALSE;
        END IF;
    ELSIF (TG_OP = 'DELETE') THEN
        v_entity_id := OLD.id;
        v_old_data := to_jsonb(OLD);
        v_new_data := NULL;
        v_changed_fields := NULL;
    END IF;
    
    -- Insérer dans audit_logs si nécessaire
    IF v_include_row THEN
        INSERT INTO audit.audit_logs (
            entity_type,
            entity_id,
            action,
            old_data,
            new_data,
            changed_fields,
            user_id,
            ip_address,
            app_user
        ) VALUES (
            TG_TABLE_NAME::VARCHAR,
            v_entity_id,
            TG_OP,
            v_old_data,
            v_new_data,
            v_changed_fields,
            v_user_id,
            v_ip_address,
            v_app_user
        );
    END IF;

    IF (TG_OP = 'DELETE') THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 3. Fonction pour configurer les triggers d'audit
CREATE OR REPLACE FUNCTION setup_audit_triggers() RETURNS VOID AS $$
DECLARE
    tables TEXT[] := ARRAY[
        'identity.users', 
        'profiles.candidates', 
        'profiles.companies', 
        'jobs.jobs', 
        'jobs.applications', 
        'matching.matches'
    ];
    table_name TEXT;
BEGIN
    FOREACH table_name IN ARRAY tables
    LOOP
        -- Supprimer le trigger s'il existe déjà
        EXECUTE format('DROP TRIGGER IF EXISTS audit_trigger ON %I', table_name);
        
        -- Créer le nouveau trigger
        EXECUTE format('
            CREATE TRIGGER audit_trigger
            AFTER INSERT OR UPDATE OR DELETE ON %I
            FOR EACH ROW EXECUTE FUNCTION audit_trigger_func()
        ', table_name);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 4. Fonction de mise à jour automatique de updated_at
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 5. Fonction pour ajouter facilement des tags
CREATE OR REPLACE FUNCTION add_entity_tag(
    p_entity_type VARCHAR(50),
    p_entity_id INTEGER,
    p_tag_name VARCHAR(100),
    p_tag_category VARCHAR(50),
    p_user_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    v_tag_id INTEGER;
BEGIN
    -- Créer le tag s'il n'existe pas
    INSERT INTO profiles.tags (name, category)
    VALUES (p_tag_name, p_tag_category)
    ON CONFLICT (name, category) DO NOTHING;
    
    -- Récupérer l'ID du tag
    SELECT id INTO v_tag_id FROM profiles.tags 
    WHERE name = p_tag_name AND category = p_tag_category;
    
    -- Ajouter le tag à l'entité
    INSERT INTO profiles.entity_tags (tag_id, entity_type, entity_id, created_by)
    VALUES (v_tag_id, p_entity_type, p_entity_id, p_user_id)
    ON CONFLICT (tag_id, entity_type, entity_id) DO NOTHING;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- 6. Fonction pour récupérer les tags d'une entité
CREATE OR REPLACE FUNCTION get_entity_tags(
    p_entity_type VARCHAR(50),
    p_entity_id INTEGER
) RETURNS TABLE (
    tag_id INTEGER,
    tag_name VARCHAR(100),
    tag_category VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT t.id, t.name, t.category
    FROM profiles.entity_tags et
    JOIN profiles.tags t ON et.tag_id = t.id
    WHERE et.entity_type = p_entity_type
    AND et.entity_id = p_entity_id;
END;
$$ LANGUAGE plpgsql;

-- 7. Fonction pour consulter l'historique d'une entité
CREATE OR REPLACE FUNCTION get_entity_history(
    p_entity_type VARCHAR,
    p_entity_id INTEGER
) RETURNS TABLE (
    action VARCHAR,
    changed_data JSONB,
    user_id UUID,
    user_email VARCHAR,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        al.action,
        al.changed_fields,
        al.user_id,
        u.email AS user_email,
        al.created_at
    FROM audit.audit_logs al
    LEFT JOIN identity.users u ON al.user_id = u.id
    WHERE al.entity_type = p_entity_type
    AND al.entity_id = p_entity_id
    ORDER BY al.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- 8. Fonction pour mettre à jour les statistiques quotidiennes
CREATE OR REPLACE FUNCTION update_daily_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_TABLE_NAME = 'users' AND TG_OP = 'INSERT') THEN
        INSERT INTO analytics.daily_stats (date, new_users)
        VALUES (CURRENT_DATE, 1)
        ON CONFLICT (date) DO UPDATE
        SET new_users = analytics.daily_stats.new_users + 1;
    ELSIF (TG_TABLE_NAME = 'candidates' AND TG_OP = 'INSERT') THEN
        INSERT INTO analytics.daily_stats (date, new_candidates)
        VALUES (CURRENT_DATE, 1)
        ON CONFLICT (date) DO UPDATE
        SET new_candidates = analytics.daily_stats.new_candidates + 1;
    ELSIF (TG_TABLE_NAME = 'jobs' AND TG_OP = 'INSERT') THEN
        INSERT INTO analytics.daily_stats (date, new_jobs)
        VALUES (CURRENT_DATE, 1)
        ON CONFLICT (date) DO UPDATE
        SET new_jobs = analytics.daily_stats.new_jobs + 1;
    ELSIF (TG_TABLE_NAME = 'applications' AND TG_OP = 'INSERT') THEN
        INSERT INTO analytics.daily_stats (date, new_applications)
        VALUES (CURRENT_DATE, 1)
        ON CONFLICT (date) DO UPDATE
        SET new_applications = analytics.daily_stats.new_applications + 1;
    ELSIF (TG_TABLE_NAME = 'matches' AND TG_OP = 'INSERT') THEN
        INSERT INTO analytics.daily_stats (date, new_matches)
        VALUES (CURRENT_DATE, 1)
        ON CONFLICT (date) DO UPDATE
        SET new_matches = analytics.daily_stats.new_matches + 1;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;