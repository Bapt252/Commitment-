# SuperSmartMatch V2 - Architecture Microservices

## 📋 Table des Matières
- [Vue d'ensemble](#vue-densemble)
- [Architecture des Services](#architecture-des-services)
- [Infrastructure](#infrastructure)
- [Sécurité](#sécurité)
- [Monitoring & Observabilité](#monitoring--observabilité)
- [Déploiement](#déploiement)
- [Performance](#performance)
- [Évolutivité](#évolutivité)

## 🎯 Vue d'ensemble

SuperSmartMatch V2 adopte une architecture microservices complète pour résoudre les problèmes identifiés dans l'audit technique :
- ✅ Architecture cohérente et documentée
- ✅ 7 microservices déployés et fonctionnels
- ✅ Infrastructure complète (PostgreSQL, Redis, MinIO)
- ✅ Configuration sécurisée pour la production
- ✅ Élimination des duplications de code

## 🏗️ Architecture des Services

### API Gateway (Port 5050)
**Rôle :** Point d'entrée unique avec authentification JWT
- **Technologies :** Node.js, Express, JWT, Redis
- **Responsabilités :**
  - Authentification et autorisation
  - Rate limiting et sécurité
  - Routage vers les microservices
  - Gestion des sessions
  - Validation des requêtes

### CV Parser Service (Port 5051)
**Rôle :** Parsing de CV en temps réel avec OCR et NLP
- **Technologies :** Node.js, Tesseract.js, Natural, PostgreSQL
- **Responsabilités :**
  - Extraction de texte (PDF, DOC, images)
  - Reconnaissance optique de caractères (OCR)
  - Analyse NLP pour extraction de compétences
  - Stockage des données parsées
  - Interface MinIO pour fichiers

### Job Parser Service (Port 5053)
**Rôle :** Parsing d'offres d'emploi avec NLP avancé
- **Technologies :** Node.js, Compromise, Natural, PostgreSQL
- **Responsabilités :**
  - Parsing de descriptions de poste
  - Extraction des exigences et compétences
  - Classification des offres d'emploi
  - Analyse sémantique du contenu
  - Standardisation des données

### Matching Service (Port 5052)
**Rôle :** Algorithme de matching unique et optimisé
- **Technologies :** Node.js, TensorFlow, ML-Matrix, PostgreSQL
- **Responsabilités :**
  - Algorithme de matching unifié (plus de duplications)
  - Machine Learning pour l'optimisation
  - Calcul de scores de compatibilité
  - Cache intelligent des résultats
  - Analytics des performances

### User Service (Port 5054)
**Rôle :** Gestion complète des utilisateurs
- **Technologies :** Node.js, PostgreSQL, Redis, Bcrypt
- **Responsabilités :**
  - Gestion des comptes utilisateurs
  - Profils et préférences
  - Authentification et sessions
  - Validation des données
  - Audit des activités

### Notification Service (Port 5055)
**Rôle :** Notifications temps réel multi-canal
- **Technologies :** Node.js, Socket.IO, Redis, Nodemailer
- **Responsabilités :**
  - WebSockets pour temps réel
  - Notifications email
  - Push notifications
  - Gestion des préférences
  - File d'attente des messages

### Analytics Service (Port 5056)
**Rôle :** Métriques et monitoring business
- **Technologies :** Node.js, Prometheus, PostgreSQL, Redis
- **Responsabilités :**
  - Collecte de métriques business
  - Tableau de bord en temps réel
  - Rapports d'utilisation
  - Optimisation des performances
  - Export de données

## 🛠️ Infrastructure

### Base de Données - PostgreSQL
- **Configuration :** Bases séparées par microservice
- **Optimisations :** Index, partitioning, connexions poolées
- **Sauvegardes :** Automatisées avec rétention 30 jours
- **Monitoring :** Métriques de performance et requêtes lentes

### Cache - Redis
- **Usage :** Sessions, cache applicatif, file d'attente
- **Configuration :** Persistance + LRU eviction
- **Clustering :** Prêt pour le clustering Redis
- **Monitoring :** Métriques de hit rate et mémoire

### Stockage Objet - MinIO
- **Buckets :** `cv-documents`, `job-descriptions`
- **Sécurité :** Chiffrement, access control
- **Sauvegarde :** Réplication automatique
- **API :** Compatible S3 pour l'évolutivité

### Reverse Proxy - Nginx
- **Load Balancing :** Distribution intelligente
- **SSL/TLS :** Termination SSL avec certificats
- **Compression :** Gzip pour optimisation
- **Rate Limiting :** Protection DDoS
- **Health Checks :** Monitoring automatique

## 🔒 Sécurité

### Authentification & Autorisation
- **JWT Tokens :** Signature sécurisée avec rotation
- **RBAC :** Contrôle d'accès basé sur les rôles
- **Session Management :** Redis avec expiration
- **Password Security :** Bcrypt avec salt rounds élevés

### Sécurité Réseau
- **Docker Network :** Isolation des services
- **Firewall Rules :** Ports exposés minimaux
- **HTTPS :** Chiffrement en transit obligatoire
- **CORS :** Configuration restrictive

### Sécurité des Données
- **Encryption at Rest :** PostgreSQL + MinIO
- **Validation :** Express-validator sur tous les endpoints
- **SQL Injection :** Protection avec requêtes préparées
- **XSS Protection :** Headers de sécurité

### Monitoring Sécurité
- **Audit Logs :** Traçabilité complète
- **Failed Attempts :** Détection des tentatives d'intrusion
- **Rate Limiting :** Protection contre les attaques
- **Vulnerability Scanning :** Containers sécurisés

## 📊 Monitoring & Observabilité

### Métriques Système
- **Prometheus :** Collecte de toutes les métriques
- **Grafana :** Dashboards temps réel
- **Node Exporter :** Métriques système
- **cAdvisor :** Métriques containers

### Métriques Business
- **Utilisateurs Actifs :** Tracking en temps réel
- **Taux de Matching :** Performance algorithmes
- **Temps de Traitement :** CV et Jobs parsing
- **Taux de Conversion :** Funnel utilisateur

### Logging Centralisé
- **Winston :** Logs structurés JSON
- **Log Levels :** DEBUG, INFO, WARN, ERROR
- **Log Rotation :** Gestion automatique
- **Correlation IDs :** Traçage des requêtes

### Alerting
- **Critical Alerts :** Disponibilité < 99.5%
- **Performance Alerts :** Latence > 1s
- **Business Alerts :** Baisse performances matching
- **Security Alerts :** Tentatives d'intrusion

## 🚀 Déploiement

### Environnements
- **Development :** Docker Compose local
- **Staging :** Infrastructure identique à production
- **Production :** Configuration sécurisée complète

### CI/CD Pipeline
- **Tests :** Unit + Integration + E2E
- **Security Scanning :** Vulnerabilités + Secrets
- **Build :** Images Docker optimisées
- **Deploy :** Blue-Green deployment

### Scripts Automation
- `scripts/deploy-production.sh` - Déploiement complet
- `scripts/test-integration.sh` - Tests d'intégration
- `scripts/backup-restore.sh` - Sauvegarde/restauration
- `scripts/health-check.sh` - Vérifications système

### Health Checks
- **Liveness Probes :** Détection des services morts
- **Readiness Probes :** Services prêts à recevoir du trafic
- **Startup Probes :** Démarrage des services lents
- **Business Health :** Vérification des fonctionnalités

## ⚡ Performance

### Optimisations Microservices
- **Connection Pooling :** PostgreSQL et Redis
- **Caching Strategy :** Multi-niveau avec TTL
- **Async Processing :** File d'attente pour tâches lourdes
- **Resource Limits :** CPU et mémoire par service

### Load Balancing
- **Algorithm :** Least connections avec health checks
- **Session Affinity :** Sticky sessions si nécessaire
- **Circuit Breaker :** Protection contre les cascades
- **Retry Logic :** Resilience automatique

### Monitoring Performance
- **Response Times :** P50, P95, P99 par endpoint
- **Throughput :** Requêtes/seconde par service
- **Error Rates :** Taux d'erreur en temps réel
- **Resource Usage :** CPU, mémoire, I/O

## 📈 Évolutivité

### Scalabilité Horizontale
- **Stateless Services :** Scaling automatique
- **Load Balancing :** Distribution traffic
- **Database Sharding :** Préparé pour partition
- **Cache Distribution :** Redis Cluster ready

### Microservices Patterns
- **API Gateway Pattern :** Point d'entrée unique
- **Database per Service :** Isolation des données
- **Event-Driven :** Communication asynchrone
- **Circuit Breaker :** Resilience pattern

### Monitoring Scaling
- **Auto-scaling Metrics :** CPU, mémoire, latence
- **Capacity Planning :** Prédiction des besoins
- **Performance Testing :** Load testing régulier
- **Cost Optimization :** Monitoring des ressources

## 🔧 Configuration

### Variables d'Environnement
Voir `.env.production.template` pour la configuration complète des :
- Secrets de sécurité (JWT, passwords)
- Connexions base de données
- Configuration SMTP
- Paramètres de performance

### Fichiers de Configuration
- `docker-compose.production.yml` - Infrastructure complète
- `nginx/nginx.conf` - Configuration reverse proxy
- `monitoring/prometheus/prometheus.yml` - Monitoring
- `database/init/` - Schémas base de données

## 📚 Documentation Supplémentaire

- [API Documentation](./api-documentation.md)
- [Deployment Guide](./deployment-guide.md)
- [Security Guidelines](./security-guidelines.md)
- [Monitoring Runbook](./monitoring-runbook.md)
- [Troubleshooting Guide](./troubleshooting.md)
