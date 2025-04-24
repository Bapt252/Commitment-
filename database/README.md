# Base de données Nexten

Ce répertoire contient tous les scripts SQL nécessaires pour créer et maintenir la base de données PostgreSQL de la plateforme Nexten.

## Structure de la base de données

La base de données est organisée en plusieurs schémas pour une séparation claire des préoccupations :

- **identity** : Gestion des utilisateurs et authentification
- **profiles** : Profils candidats, entreprises et compétences
- **jobs** : Offres d'emploi et candidatures
- **matching** : Algorithmes et résultats de matching
- **analytics** : Tables d'analyse et agrégations
- **audit** : Traces d'audit et logs

## Architecture et optimisations

### 1. Structure des fichiers

- **01_schema_creation.sql** : Création des schémas et tables principales
- **02_indexes_and_optimizations.sql** : Index et optimisations de base
- **03_functions_and_procedures.sql** : Fonctions et procédures utilitaires
- **04_matching_functions.sql** : Logique de matching avancée
- **05_security_and_roles.sql** : Sécurité et contrôle d'accès
- **06_initial_data.sql** : Données initiales
- **07_advanced_optimizations.sql** : Optimisations avancées pour performances et scalabilité

### 2. Principales caractéristiques

#### Modèle relationnel optimisé

Le système utilise un modèle relationnel complet avec des relations bien définies entre :
- Utilisateurs, candidats et recruteurs
- Compétences et catégories de compétences
- Offres d'emploi et compétences requises
- Candidatures et résultats de matching

#### Recherche full-text et filtrage

- Utilisation de `pg_trgm` pour les recherches textuelles approximatives
- Index GIN pour recherche full-text dans les descriptions et compétences
- Index composites pour les filtres combinés (localisation, niveau, type de poste)
- Indexation conditionnelle pour les offres actives

#### Optimisations géographiques

- Intégration de PostGIS pour les recherches géospatiales
- Stockage des coordonnées sous forme de points géographiques
- Possibilité de recherches par rayon (distance)

#### Partitionnement

Plusieurs tables sont partitionnées pour optimiser les performances :
- Matching par date (trimestrielle) et par score
- Applications par hash (distribution)
- Logs d'audit par date

#### Vues matérialisées

Vues matérialisées pour accélérer les tableaux de bord et analyses :
- Statistiques par compétence
- Statistiques par entreprise
- Meilleurs candidats par compétence
- Offres d'emploi par zone géographique

### 3. Optimisations de performances

#### Index spécialisés

- Index GIST pour données géospatiales
- Index GIN pour les champs JSONB et full-text
- Index B-tree pour les recherches exactes
- Index partiels pour les données fréquemment interrogées

#### Partitionnement automatique

- Procédure automatisée pour créer les partitions du prochain trimestre
- Partitionnement des résultats de matching par date et par score
- Partitionnement des logs pour une meilleure rétention

#### Procédures de maintenance

- Rafraîchissement automatique des vues matérialisées
- Analyse statistique des tables critiques
- Création automatique des partitions à venir

### 4. Sécurité et conformité

#### Protection des données sensibles

- Chiffrement des données sensibles avec `pgcrypto`
- Vues anonymisées pour l'analyse des données
- Row Level Security (RLS) pour contrôler l'accès aux données
- Audit complet de toutes les modifications

#### Gestion des droits

- Rôles et droits d'accès bien définis
- Politiques de sécurité au niveau des lignes
- Isolation des données entre services

## Installation et configuration

### Prérequis

- PostgreSQL 14+ 
- Extensions : postgis, pg_trgm, pgcrypto, pg_stat_statements

### Configuration recommandée

La configuration PostgreSQL recommandée est documentée dans le commentaire de la base de données. Les principaux paramètres à ajuster sont :

```
# Mémoire et performances
shared_buffers = 4GB                # 25% de la RAM totale
effective_cache_size = 12GB         # 75% de la RAM totale
work_mem = 64MB                     # Pour tris et hash joins
maintenance_work_mem = 1GB          # Pour maintenance
```

### Ordre d'exécution des scripts

Pour une installation complète, exécutez les scripts dans l'ordre suivant :

```bash
psql -U postgres -d nexten -f 01_schema_creation.sql
psql -U postgres -d nexten -f 02_indexes_and_optimizations.sql
psql -U postgres -d nexten -f 03_functions_and_procedures.sql
psql -U postgres -d nexten -f 04_matching_functions.sql
psql -U postgres -d nexten -f 05_security_and_roles.sql
psql -U postgres -d nexten -f 06_initial_data.sql
psql -U postgres -d nexten -f 07_advanced_optimizations.sql
```

## Maintenance

### Tâches régulières

- **Quotidien** : Analyse des tables critiques (`maintenance.analyze_critical_tables()`)
- **Hebdomadaire** : Rafraîchissement des vues matérialisées (`maintenance.refresh_materialized_views()`)
- **Trimestriel** : Création des partitions pour le prochain trimestre (`maintenance.create_partitions_for_next_quarter()`)

### Monitoring

Utilisez pg_stat_statements pour identifier les requêtes lentes :

```sql
SELECT query, calls, total_exec_time, rows, mean_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

## Extensibilité

Le schéma est conçu pour être extensible :
- Support multilingue intégré
- Attributs dynamiques via champs JSONB
- Partitionnement préconfiguré pour la montée en charge
- Structures optimisées pour le matching intelligent

## Structure des tables principales

### Utilisateurs

```
identity.users
├── id (UUID, PK)
├── email (VARCHAR, unique)
├── password_hash (VARCHAR)
├── user_type (VARCHAR)
└── ... (autres attributs)
```

### Candidats

```
profiles.candidates
├── id (SERIAL, PK)
├── user_id (UUID, FK -> identity.users)
├── first_name, last_name
├── experience_years
├── location_id (FK -> profiles.locations)
└── ... (autres attributs)
```

### Compétences

```
profiles.skills
├── id (SERIAL, PK)
├── name (VARCHAR, unique)
├── category_id (FK -> profiles.skill_categories)
└── ... (autres attributs)

profiles.candidate_skills
├── candidate_id + skill_id (PK composite)
├── proficiency_level (1-5)
├── years_experience
└── ... (autres attributs)
```

### Offres d'emploi

```
jobs.jobs
├── id (SERIAL, PK)
├── company_id (FK -> profiles.companies)
├── title, description
├── location_id (FK -> profiles.locations)
├── job_type, experience_level
├── status
└── ... (autres attributs)

jobs.job_skills
├── job_id + skill_id (PK composite)
├── importance_level (1-5)
├── is_required (BOOLEAN)
└── ... (autres attributs)
```

### Matching

```
matching.matches
├── id (SERIAL, PK)
├── candidate_id (FK -> profiles.candidates)
├── job_id (FK -> jobs.jobs)
├── match_score (DECIMAL)
├── skill_match_score, experience_match_score, ...
├── match_details (JSONB)
└── ... (autres attributs)
```

## Crédits

Cette structure de base de données a été conçue pour la plateforme Nexten, un système de matching intelligent entre candidats et offres d'emploi.
