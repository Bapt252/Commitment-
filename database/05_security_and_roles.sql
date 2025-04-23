-- 1. Rôles principaux par domaine
CREATE ROLE nexten_base;
CREATE ROLE nexten_identity;
CREATE ROLE nexten_profiles;
CREATE ROLE nexten_jobs;
CREATE ROLE nexten_matching;
CREATE ROLE nexten_analytics;
CREATE ROLE nexten_audit;

-- 2. Permissions de base pour tous les services
GRANT USAGE ON SCHEMA public TO nexten_base;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO nexten_base;

-- 3. Permissions pour le service d'identité
GRANT USAGE ON SCHEMA identity TO nexten_identity;
GRANT ALL ON ALL TABLES IN SCHEMA identity TO nexten_identity;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA identity TO nexten_identity;

-- 4. Permissions pour le service de profils
GRANT USAGE ON SCHEMA profiles TO nexten_profiles;
GRANT ALL ON ALL TABLES IN SCHEMA profiles TO nexten_profiles;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA profiles TO nexten_profiles;
GRANT USAGE ON SCHEMA identity TO nexten_profiles;
GRANT SELECT ON identity.users TO nexten_profiles;

-- 5. Permissions pour le service d'offres d'emploi
GRANT USAGE ON SCHEMA jobs TO nexten_jobs;
GRANT ALL ON ALL TABLES IN SCHEMA jobs TO nexten_jobs;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA jobs TO nexten_jobs;
GRANT USAGE ON SCHEMA profiles TO nexten_jobs;
GRANT SELECT ON profiles.companies TO nexten_jobs;
GRANT SELECT ON profiles.candidates TO nexten_jobs;
GRANT SELECT ON profiles.skills TO nexten_jobs;

-- 6. Permissions pour le service de matching
GRANT USAGE ON SCHEMA matching TO nexten_matching;
GRANT ALL ON ALL TABLES IN SCHEMA matching TO nexten_matching;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA matching TO nexten_matching;
GRANT USAGE ON SCHEMA profiles TO nexten_matching;
GRANT USAGE ON SCHEMA jobs TO nexten_matching;
GRANT SELECT ON profiles.candidates TO nexten_matching;
GRANT SELECT ON profiles.candidate_skills TO nexten_matching;
GRANT SELECT ON jobs.jobs TO nexten_matching;
GRANT SELECT ON jobs.job_skills TO nexten_matching;

-- 7. Permissions pour le service d'analytics
GRANT USAGE ON SCHEMA analytics TO nexten_analytics;
GRANT ALL ON ALL TABLES IN SCHEMA analytics TO nexten_analytics;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA analytics TO nexten_analytics;
GRANT USAGE ON SCHEMA profiles TO nexten_analytics;
GRANT USAGE ON SCHEMA jobs TO nexten_analytics;
GRANT USAGE ON SCHEMA matching TO nexten_analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA profiles TO nexten_analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA jobs TO nexten_analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA matching TO nexten_analytics;

-- 8. Permissions pour le service d'audit
GRANT USAGE ON SCHEMA audit TO nexten_audit;
GRANT ALL ON ALL TABLES IN SCHEMA audit TO nexten_audit;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA audit TO nexten_audit;

-- 9. Création des utilisateurs de base de données pour chaque service
CREATE USER identity_service WITH PASSWORD 'identity_password';
CREATE USER profiles_service WITH PASSWORD 'profiles_password';
CREATE USER jobs_service WITH PASSWORD 'jobs_password';
CREATE USER matching_service WITH PASSWORD 'matching_password';
CREATE USER analytics_service WITH PASSWORD 'analytics_password';
CREATE USER audit_service WITH PASSWORD 'audit_password';

-- 10. Attribution des rôles aux utilisateurs
GRANT nexten_base, nexten_identity TO identity_service;
GRANT nexten_base, nexten_profiles TO profiles_service;
GRANT nexten_base, nexten_jobs TO jobs_service;
GRANT nexten_base, nexten_matching TO matching_service;
GRANT nexten_base, nexten_analytics TO analytics_service;
GRANT nexten_base, nexten_audit TO audit_service;