# Changelog

Tous les changements notables de ce projet seront documentés dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Non publié]

### Ajouté
- Configuration complète de l'environnement de développement
- Stack de monitoring avec Prometheus, Grafana, et ELK
- Middleware de performance et métriques Prometheus
- Pipeline CI/CD avancé avec déploiements canary
- Tests de performance avec Locust
- Documentation complète avec MkDocs
- Scripts d'automatisation pour le développement
- Configuration pre-commit hooks
- Logging structuré avec correlation IDs
- Tracing distribué avec Jaeger
- Alertes automatiques avec AlertManager
- Dashboards Grafana pour API et ML
- Tests d'intégration complets
- Scripts de validation de déploiement
- Configuration multi-environnement

### Modifié
- Amélioration de l'architecture Docker Compose
- Optimisation des configurations de services
- Mise à jour des dépendances Python
- Refactoring des middlewares FastAPI

### Sécurité
- Scan automatique des vulnérabilités avec Trivy
- Détection de secrets avec GitGuardian
- Configuration sécurisée des conteneurs
- Chiffrement des secrets dans CI/CD

## [1.0.0] - 2024-01-15

### Ajouté
- Service de parsing de CV avec GPT-4o-mini
- Service de parsing de fiches de poste
- Service de matching avancé
- API REST avec FastAPI
- Interface utilisateur React
- Base de données PostgreSQL
- Cache Redis
- Stockage MinIO
- Documentation API avec Swagger
- Tests unitaires et d'intégration
- Containerisation Docker

### Fonctionnalités
- Parsing automatique de CV (PDF, DOCX, TXT)
- Extraction d'entités (nom, compétences, expérience)
- Analyse de fiches de poste
- Matching intelligent CV/poste
- Interface web intuitive
- API RESTful complète
- Gestion des fichiers sécurisée
- Traitement asynchrone

### Technique
- Architecture microservices
- FastAPI avec validation Pydantic
- ORM SQLAlchemy
- File d'attente RQ Redis
- Migrations Alembic
- Tests avec pytest
- Container multi-stage
- Monitoring basique

---

## Format des versions

### Types de changements

- **Ajouté** : nouvelles fonctionnalités
- **Modifié** : changements dans les fonctionnalités existantes
- **Déprécié** : fonctionnalités qui seront supprimées prochainement
- **Supprimé** : fonctionnalités supprimées
- **Corrigé** : corrections de bugs
- **Sécurité** : corrections de vulnérabilités

### Versioning

- **MAJOR** : changements incompatibles de l'API
- **MINOR** : ajout de fonctionnalités rétrocompatibles
- **PATCH** : corrections rétrocompatibles

### Liens

- [Non publié]: https://github.com/Bapt252/Commitment-/compare/v1.0.0...HEAD
- [1.0.0]: https://github.com/Bapt252/Commitment-/releases/tag/v1.0.0