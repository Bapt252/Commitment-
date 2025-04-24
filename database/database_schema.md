# Schéma visuel de la base de données Nexten

Ce fichier fournit une représentation visuelle des tables principales et leurs relations dans la base de données Nexten, utilisant la syntaxe Mermaid pour générer un diagramme ER (Entité-Relation).

```mermaid
erDiagram
    %% Schéma Identity
    USERS ||--o{ CANDIDATES : "possède"
    USERS ||--o{ RECRUITERS : "possède"
    USERS {
        uuid id PK
        varchar email
        varchar password_hash
        varchar user_type
        timestamp created_at
        boolean is_active
    }
    
    %% Schéma Profiles
    CANDIDATES ||--o{ CANDIDATE_SKILLS : "a"
    CANDIDATES ||--o{ APPLICATIONS : "soumet"
    CANDIDATES ||--o{ MATCHES : "reçoit"
    CANDIDATES {
        int id PK
        uuid user_id FK
        varchar first_name
        varchar last_name
        date date_of_birth
        int experience_years
        int location_id FK
        decimal desired_salary_min
        decimal desired_salary_max
        boolean is_remote
    }
    
    COMPANIES ||--o{ JOBS : "publie"
    COMPANIES {
        int id PK
        uuid user_id FK
        varchar name
        varchar industry
        int location_id FK
        varchar size
    }
    
    RECRUITERS }|--|| COMPANIES : "appartient à"
    RECRUITERS {
        int id PK
        uuid user_id FK
        int company_id FK
        varchar job_title
    }
    
    SKILLS ||--o{ CANDIDATE_SKILLS : "utilisée dans"
    SKILLS ||--o{ JOB_SKILLS : "requise dans"
    SKILLS {
        int id PK
        varchar name UK
        int category_id FK
        varchar description
        text[] aliases
    }
    
    SKILL_CATEGORIES ||--o{ SKILLS : "contient"
    SKILL_CATEGORIES {
        int id PK
        varchar name
        int parent_id FK
        int level
    }
    
    CANDIDATE_SKILLS {
        int candidate_id PK,FK
        int skill_id PK,FK
        int proficiency_level
        int years_experience
    }
    
    LOCATIONS ||--o{ CANDIDATES : "localisation de"
    LOCATIONS ||--o{ COMPANIES : "siège de"
    LOCATIONS ||--o{ JOBS : "lieu de"
    LOCATIONS {
        int id PK
        varchar city
        varchar country
        varchar postal_code
        point geo_point
    }
    
    %% Schéma Jobs
    JOBS ||--o{ JOB_SKILLS : "requiert"
    JOBS ||--o{ APPLICATIONS : "reçoit"
    JOBS ||--o{ MATCHES : "associé à"
    JOBS {
        int id PK
        int company_id FK
        varchar title
        text description
        int location_id FK
        varchar job_type
        varchar experience_level
        decimal salary_min
        decimal salary_max
        timestamp posted_date
        varchar status
    }
    
    JOB_SKILLS {
        int job_id PK,FK
        int skill_id PK,FK
        int importance_level
        boolean is_required
    }
    
    APPLICATIONS {
        int id PK
        int candidate_id FK
        int job_id FK
        varchar status
        text cover_letter
        timestamp submitted_at
    }
    
    %% Schéma Matching
    MATCHES {
        int id PK
        int candidate_id FK
        int job_id FK
        decimal match_score
        decimal skill_match_score
        decimal experience_match_score
        varchar status
        jsonb match_details
    }
    
    MATCHING_ALGORITHMS ||--o{ MATCHES : "génère"
    MATCHING_ALGORITHMS {
        int id PK
        varchar name
        text description
        jsonb parameters
        boolean is_active
    }
    
    %% Schéma Analytics
    DAILY_STATS {
        date date PK
        int new_users
        int new_candidates
        int new_jobs
        int new_applications
        jsonb stats
    }
    
    USER_EVENTS {
        int id PK
        uuid user_id FK
        varchar event_type
        varchar entity_type
        int entity_id
        jsonb metadata
        timestamp created_at
    }
    
    %% Schéma Audit
    AUDIT_LOGS {
        int id PK
        varchar entity_type
        int entity_id
        varchar action
        jsonb old_data
        jsonb new_data
        uuid user_id FK
        timestamp created_at
    }
```

## Description des relations principales

### Utilisateurs et profils
- Un **UTILISATEUR** peut être un candidat ou un recruteur (ou les deux)
- Un **CANDIDAT** est associé à un utilisateur et possède plusieurs compétences
- Un **RECRUTEUR** est associé à un utilisateur et appartient à une entreprise
- Une **ENTREPRISE** peut avoir plusieurs recruteurs et publier plusieurs offres d'emploi

### Compétences
- Une **COMPÉTENCE** appartient à une catégorie
- Les **CATÉGORIES DE COMPÉTENCES** peuvent être hiérarchiques (avec parent_id)
- Un **CANDIDAT** possède plusieurs compétences avec un niveau de maîtrise
- Une **OFFRE D'EMPLOI** requiert plusieurs compétences avec un niveau d'importance

### Offres d'emploi et candidatures
- Une **ENTREPRISE** publie des offres d'emploi
- Une **OFFRE D'EMPLOI** spécifie plusieurs compétences requises
- Un **CANDIDAT** peut soumettre des candidatures à plusieurs offres
- Une **CANDIDATURE** représente la relation entre un candidat et une offre

### Matching
- Un **ALGORITHME DE MATCHING** génère des correspondances entre candidats et offres
- Un **MATCH** représente la compatibilité entre un candidat et une offre avec un score

### Éléments transversaux
- **LOCALISATIONS** utilisées par les candidats, entreprises et offres d'emploi
- **AUDIT_LOGS** enregistre toutes les modifications sur les entités principales
- **DAILY_STATS** agrège les statistiques quotidiennes pour les tableaux de bord
- **USER_EVENTS** suit les interactions utilisateurs pour l'analyse comportementale

## Notes sur l'implémentation

Le diagramme ci-dessus représente les tables conceptuelles principales. Dans l'implémentation réelle:

1. Les tables sont organisées dans différents schémas (identity, profiles, jobs, matching, analytics, audit)
2. Plusieurs tables sont partitionnées pour optimiser les performances
3. De nombreux index sont définis pour accélérer les requêtes fréquentes
4. Des vues matérialisées sont utilisées pour les rapports et tableaux de bord
5. Des contraintes d'intégrité référentielle garantissent la cohérence des données
