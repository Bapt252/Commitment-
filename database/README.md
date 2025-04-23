# Schéma PostgreSQL pour Nexten

Ce dossier contient les scripts SQL pour créer et initialiser la base de données PostgreSQL utilisée par la plateforme Nexten.

## Structure des fichiers

- `01_schema_creation.sql` : Définition des schémas et tables principales
- `02_indexes_and_optimizations.sql` : Index, partitionnement et optimisations
- `03_functions_and_procedures.sql` : Fonctions utilitaires et triggers
- `04_matching_functions.sql` : Algorithmes de matching modulaires
- `05_security_and_roles.sql` : Configuration des rôles et permissions
- `06_initial_data.sql` : Données initiales pour le système

## Organisation des schémas

La base de données est organisée en schémas correspondant aux domaines fonctionnels :

- `identity` : Gestion des utilisateurs et authentification
- `profiles` : Profils candidats, entreprises et compétences
- `jobs` : Offres d'emploi et candidatures
- `matching` : Algorithmes et résultats de matching
- `analytics` : Tables d'analyse et statistiques
- `audit` : Logs et traçabilité

## Installation

1. Créer une base de données PostgreSQL :
   ```bash
   createdb nexten
   ```

2. Exécuter les scripts dans l'ordre :
   ```bash
   psql -d nexten -f 01_schema_creation.sql
   psql -d nexten -f 02_indexes_and_optimizations.sql
   psql -d nexten -f 03_functions_and_procedures.sql
   psql -d nexten -f 04_matching_functions.sql
   psql -d nexten -f 05_security_and_roles.sql
   psql -d nexten -f 06_initial_data.sql
   ```

## Caractéristiques principales

- **Système de tags universel** : Permet d'associer des tags à n'importe quelle entité
- **Algorithme de matching modulaire** : Décomposé en fonctions spécialisées pour les compétences, l'expérience et la localisation
- **Audit automatique** : Traçabilité complète des modifications via triggers
- **Isolation par service** : Contrôle d'accès fin via rôles et vues spécifiques
- **Optimisations de performance** : Indexation avancée, partitionnement et vues matérialisées

## Modèle de sécurité

Chaque service du backend dispose de son propre rôle PostgreSQL avec des permissions limitées :

- `identity_service` : Accès complet au schéma `identity`
- `profiles_service` : Accès complet au schéma `profiles` et lecture seule sur `identity.users`
- `jobs_service` : Accès complet au schéma `jobs` et lecture seule sur certaines tables de `profiles`
- `matching_service` : Accès complet au schéma `matching` et lecture seule sur les tables nécessaires
- `analytics_service` : Accès complet au schéma `analytics` et lecture seule sur les autres schémas
- `audit_service` : Accès complet au schéma `audit`