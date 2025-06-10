#!/bin/bash
set -e

# SuperSmartMatch V2 - Database Initialization Script
# Creates separate databases for each microservice

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create databases for each microservice
    CREATE DATABASE cv_parser_db;
    CREATE DATABASE job_parser_db;
    CREATE DATABASE matching_db;
    CREATE DATABASE user_db;
    CREATE DATABASE notification_db;
    CREATE DATABASE analytics_db;

    -- Grant permissions
    GRANT ALL PRIVILEGES ON DATABASE cv_parser_db TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE job_parser_db TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE matching_db TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE user_db TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE notification_db TO $POSTGRES_USER;
    GRANT ALL PRIVILEGES ON DATABASE analytics_db TO $POSTGRES_USER;

    -- Connect to each database and create initial schemas
    \c cv_parser_db;
    
    -- CV Parser Database Schema
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    CREATE TABLE parsed_cvs (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL,
        filename VARCHAR(255) NOT NULL,
        file_size INTEGER NOT NULL,
        file_type VARCHAR(50) NOT NULL,
        storage_path TEXT NOT NULL,
        parsed_data JSONB NOT NULL,
        extracted_text TEXT,
        skills TEXT[],
        experience_years INTEGER,
        education_level VARCHAR(100),
        languages TEXT[],
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX idx_parsed_cvs_user_id ON parsed_cvs(user_id);
    CREATE INDEX idx_parsed_cvs_skills ON parsed_cvs USING GIN(skills);
    CREATE INDEX idx_parsed_cvs_text ON parsed_cvs USING GIN(to_tsvector('french', extracted_text));
    CREATE INDEX idx_parsed_cvs_created_at ON parsed_cvs(created_at);

    \c job_parser_db;
    
    -- Job Parser Database Schema
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    CREATE TABLE parsed_jobs (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        company_id UUID NOT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        parsed_data JSONB NOT NULL,
        required_skills TEXT[],
        optional_skills TEXT[],
        experience_min INTEGER,
        experience_max INTEGER,
        salary_min INTEGER,
        salary_max INTEGER,
        location VARCHAR(255),
        remote_allowed BOOLEAN DEFAULT FALSE,
        employment_type VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX idx_parsed_jobs_company_id ON parsed_jobs(company_id);
    CREATE INDEX idx_parsed_jobs_skills ON parsed_jobs USING GIN(required_skills);
    CREATE INDEX idx_parsed_jobs_title ON parsed_jobs USING GIN(to_tsvector('french', title));
    CREATE INDEX idx_parsed_jobs_location ON parsed_jobs(location);
    CREATE INDEX idx_parsed_jobs_created_at ON parsed_jobs(created_at);

    \c matching_db;
    
    -- Matching Database Schema
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    CREATE TABLE match_results (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        cv_id UUID NOT NULL,
        job_id UUID NOT NULL,
        score DECIMAL(5,2) NOT NULL,
        algorithm_version VARCHAR(50) NOT NULL,
        match_details JSONB NOT NULL,
        skills_match JSONB,
        experience_match JSONB,
        location_match JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(cv_id, job_id, algorithm_version)
    );
    
    CREATE INDEX idx_match_results_cv_id ON match_results(cv_id);
    CREATE INDEX idx_match_results_job_id ON match_results(job_id);
    CREATE INDEX idx_match_results_score ON match_results(score DESC);
    CREATE INDEX idx_match_results_created_at ON match_results(created_at);

    CREATE TABLE algorithm_performance (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        algorithm_version VARCHAR(50) NOT NULL,
        total_matches INTEGER DEFAULT 0,
        avg_score DECIMAL(5,2),
        processing_time_ms INTEGER,
        success_rate DECIMAL(5,2),
        date DATE DEFAULT CURRENT_DATE,
        UNIQUE(algorithm_version, date)
    );

    \c user_db;
    
    -- User Database Schema
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    CREATE TABLE users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        role VARCHAR(50) DEFAULT 'user',
        email_verified BOOLEAN DEFAULT FALSE,
        profile_data JSONB,
        last_login TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX idx_users_email ON users(email);
    CREATE INDEX idx_users_role ON users(role);
    CREATE INDEX idx_users_created_at ON users(created_at);

    CREATE TABLE user_sessions (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        session_token VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        ip_address INET,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
    CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
    CREATE INDEX idx_user_sessions_expires ON user_sessions(expires_at);

    \c notification_db;
    
    -- Notification Database Schema
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    CREATE TABLE notifications (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL,
        type VARCHAR(50) NOT NULL,
        title VARCHAR(255) NOT NULL,
        message TEXT NOT NULL,
        data JSONB,
        read BOOLEAN DEFAULT FALSE,
        sent BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        read_at TIMESTAMP,
        sent_at TIMESTAMP
    );
    
    CREATE INDEX idx_notifications_user_id ON notifications(user_id);
    CREATE INDEX idx_notifications_type ON notifications(type);
    CREATE INDEX idx_notifications_read ON notifications(read);
    CREATE INDEX idx_notifications_created_at ON notifications(created_at);

    CREATE TABLE notification_preferences (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL,
        email_enabled BOOLEAN DEFAULT TRUE,
        push_enabled BOOLEAN DEFAULT TRUE,
        sms_enabled BOOLEAN DEFAULT FALSE,
        preferences JSONB,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    \c analytics_db;
    
    -- Analytics Database Schema
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    CREATE TABLE user_events (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID,
        event_type VARCHAR(100) NOT NULL,
        event_data JSONB NOT NULL,
        session_id VARCHAR(255),
        ip_address INET,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX idx_user_events_user_id ON user_events(user_id);
    CREATE INDEX idx_user_events_type ON user_events(event_type);
    CREATE INDEX idx_user_events_created_at ON user_events(created_at);

    CREATE TABLE system_metrics (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        service_name VARCHAR(100) NOT NULL,
        metric_name VARCHAR(100) NOT NULL,
        metric_value DECIMAL(10,2) NOT NULL,
        metric_unit VARCHAR(50),
        tags JSONB,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX idx_system_metrics_service ON system_metrics(service_name);
    CREATE INDEX idx_system_metrics_name ON system_metrics(metric_name);
    CREATE INDEX idx_system_metrics_timestamp ON system_metrics(timestamp);

    -- Performance optimization
    CREATE TABLE daily_aggregates (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        date DATE NOT NULL,
        total_matches INTEGER DEFAULT 0,
        avg_match_score DECIMAL(5,2),
        total_cv_uploads INTEGER DEFAULT 0,
        total_job_posts INTEGER DEFAULT 0,
        active_users INTEGER DEFAULT 0,
        system_performance JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date)
    );

EOSQL

echo "✅ All databases and schemas created successfully!"
