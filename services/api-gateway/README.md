# SuperSmartMatch V2 API Gateway 🌟

**Point d'entrée unifié pour la plateforme de recrutement IA la plus avancée techniquement du marché**

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/Bapt252/Commitment-)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

## 🎯 Vue d'ensemble

L'API Gateway SuperSmartMatch V2 est le cerveau central qui orchestre intelligemment :

- **🎯 CV Parser Service** (Port 5051) - 8 formats universels supportés
- **💼 Job Parser Service** (Port 5053) - Parsing d'offres temps réel  
- **🤖 Matching Service** (Port 5060) - 9 algorithmes ML auto-sélectionnés
- **🔐 Authentification JWT** centralisée avec gestion des rôles
- **⚡ Rate Limiting** intelligent par utilisateur/endpoint
- **🔄 Proxy HTTP** avec circuit breaker et load balancing
- **📊 Monitoring** complet avec métriques Prometheus

## 🏗️ Architecture

```
SuperSmartMatch V2 Unified Platform
├── API Gateway (Port 5050) ← Point d'entrée unique
│   ├── Authentification JWT
│   ├── Rate limiting
│   ├── Load balancing
│   └── Monitoring centralisé
│
├── CV Parser Service (Port 5051) ✅ EXISTANT
│   └── 8 formats universels supportés
│
├── Job Parser Service (Port 5053) ✅ EXISTANT  
│   └── Parsing offres emploi temps réel
│
└── Matching Service (Port 5060) ✅ EXISTANT
    └── 9 algorithmes ML auto-sélectionnés
```

## 🚀 Démarrage rapide

### 1. Prérequis

- Docker & Docker Compose
- Python 3.11+ (pour développement local)
- PostgreSQL 15+
- Redis 7+

### 2. Configuration

```bash
# Cloner le repository
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-

# Copier la configuration d'exemple
cp .env.example .env

# Éditer les variables d'environnement
nano .env
```

### 3. Démarrage avec Docker (Recommandé)

```bash
# Démarrage complet de la plateforme
docker-compose up -d

# Démarrage des services core uniquement
docker-compose up -d api-gateway cv-parser job-parser matching-service redis postgres

# Vérifier le statut
curl http://localhost:5050/api/gateway/health
```

### 4. Démarrage local (Développement)

```bash
cd services/api-gateway

# Installation des dépendances
pip install -r requirements.txt

# Variables d'environnement
export DATABASE_URL="postgresql://user:pass@localhost:5432/supersmartmatch"
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET="your-super-secure-secret"

# Démarrage
python app.py
```

## 📋 Endpoints principaux

### 🌟 API Gateway Unifié (Port 5050)

| Endpoint | Méthode | Description | Auth |
|----------|---------|-------------|------|
| `/api/gateway/` | GET | Informations gateway | ❌ |
| `/api/gateway/health` | GET | Health check global | ❌ |
| `/api/gateway/docs` | GET | Documentation Swagger | ❌ |

### 🔐 Authentification

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/gateway/auth/register` | POST | Inscription utilisateur |
| `/api/gateway/auth/login` | POST | Connexion |
| `/api/gateway/auth/refresh` | POST | Renouveler token |
| `/api/gateway/auth/logout` | POST | Déconnexion |
| `/api/gateway/auth/me` | GET | Profil utilisateur |

### 📄 Parsing de CV

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/gateway/parse-cv` | POST | Parser un CV (8 formats) |
| `/api/gateway/parse-cv/formats` | GET | Formats supportés |

### 💼 Parsing d'offres d'emploi

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/gateway/parse-job` | POST | Parser une offre |
| `/api/gateway/parse-job/url` | POST | Parser depuis URL |
| `/api/gateway/parse-job/batch` | POST | Parsing en lot |

### 🎯 Matching IA

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/gateway/match` | POST | Matching candidat-poste |
| `/api/gateway/match/batch` | POST | Matching en lot |
| `/api/gateway/match/algorithms` | GET | Algorithmes disponibles |
| `/api/gateway/match/explain` | POST | Explication du matching |
| `/api/gateway/match/recommendations` | POST | Recommandations |

## 🔐 Authentification

### Inscription

```bash
curl -X POST http://localhost:5050/api/gateway/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "John Doe",
    "role": "candidat"
  }'
```

### Connexion

```bash
curl -X POST http://localhost:5050/api/gateway/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com", 
    "password": "SecurePassword123!"
  }'
```

### Utilisation du token

```bash
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5050/api/gateway/auth/me
```

## 📄 Parsing de CV

### Upload et parsing

```bash
curl -X POST http://localhost:5050/api/gateway/parse-cv \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@cv.pdf" \
  -F "extract_skills=true" \
  -F "extract_experience=true"
```

### Formats supportés

- **PDF** - Extraction de texte et OCR
- **DOCX/DOC** - Documents Word
- **Images** - JPG, PNG avec OCR
- **TXT** - Texte brut
- **CSV** - Données structurées
- **HTML** - Pages web
- **RTF** - Rich Text Format
- **ODT** - OpenDocument

## 💼 Parsing d'offres d'emploi

### Parser une offre

```bash
curl -X POST http://localhost:5050/api/gateway/parse-job \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Développeur Python Senior",
    "description": "Nous recherchons un développeur Python...",
    "company": "TechCorp",
    "location": "Paris, France"
  }'
```

### Parser depuis une URL

```bash
curl -X POST http://localhost:5050/api/gateway/parse-job/url \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://company.com/jobs/python-developer"
  }'
```

## 🎯 Matching IA

### Matching simple

```bash
curl -X POST http://localhost:5050/api/gateway/match \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_profile": {
      "skills": ["Python", "FastAPI", "ML"],
      "experience": 5,
      "education": "Master Computer Science"
    },
    "job_offer": {
      "required_skills": ["Python", "FastAPI"],
      "experience_required": 3,
      "job_title": "Senior Python Developer"
    }
  }'
```

### Algorithmes disponibles

- **Cosine Similarity** - Similarité vectorielle
- **TF-IDF Matching** - Fréquence des termes
- **BERT Semantic** - Compréhension sémantique
- **Skills Exact Match** - Correspondance exacte compétences
- **Experience Weighted** - Pondération par expérience
- **Education Match** - Correspondance formation
- **Location Proximity** - Proximité géographique
- **Hybrid Ensemble** - Combinaison d'algorithmes
- **Neural Network** - Réseau de neurones

## 📊 Monitoring et métriques

### Health check global

```bash
curl http://localhost:5050/api/gateway/health
```

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "cv_parser": {"status": "healthy", "response_time": 0.045},
    "job_parser": {"status": "healthy", "response_time": 0.032},
    "matching_service": {"status": "healthy", "response_time": 0.123}
  },
  "gateway_info": {
    "version": "2.1.0",
    "environment": "production"
  }
}
```

### Métriques Prometheus

```bash
curl http://localhost:5050/api/gateway/metrics
```

## ⚡ Rate Limiting

### Limites par défaut

| Endpoint | Limite | Window |
|----------|--------|---------|
| `/auth/login` | 10 req/min | 60s |
| `/auth/register` | 5 req/min | 60s |
| `/parse-cv` | 20 req/min | 60s |
| `/parse-job` | 30 req/min | 60s |
| `/match` | 50 req/min | 60s |

### Limites par rôle

| Rôle | Limite globale |
|------|----------------|
| `candidat` | 50 req/min |
| `recruteur` | 200 req/min |
| `admin` | 1000 req/min |

### Headers de réponse

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
X-RateLimit-Window: 60
```

## 🔧 Configuration

### Variables d'environnement

```bash
# Général
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info

# Services
CV_PARSER_URL=http://cv-parser:5051
JOB_PARSER_URL=http://job-parser:5053
MATCHING_SERVICE_URL=http://matching-service:5060

# Sécurité
JWT_SECRET=supersecure-jwt-secret-change-in-production
JWT_EXPIRE_HOURS=24

# Infrastructure
REDIS_URL=redis://redis:6379
DATABASE_URL=postgresql://user:pass@postgres:5432/supersmartmatch

# Rate limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=20

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

## 🐳 Docker

### Build et run

```bash
# Build de l'image
docker build -t supersmartmatch/api-gateway:v2.1 .

# Run container
docker run -p 5050:5050 \
  -e JWT_SECRET=your-secret \
  -e DATABASE_URL=postgresql://... \
  supersmartmatch/api-gateway:v2.1
```

### Docker Compose

```bash
# Démarrage complet
docker-compose up -d

# Démarrage avec monitoring
docker-compose --profile monitoring up -d

# Scaling horizontal
docker-compose up -d --scale api-gateway=3
```

## 🔍 Tests

### Tests unitaires

```bash
cd services/api-gateway
pytest tests/ -v
```

### Tests d'intégration

```bash
pytest tests/test_integration.py -v
```

### Tests de charge

```bash
# wrk
wrk -t12 -c400 -d30s http://localhost:5050/api/gateway/health

# Artillery
artillery quick --count 100 --num 10 http://localhost:5050/api/gateway/health
```

## 🚀 Déploiement en production

### 1. Configuration sécurisée

```bash
# Générer un secret JWT fort
openssl rand -hex 32

# Configurer les variables d'environnement
export JWT_SECRET="votre-secret-super-securise"
export POSTGRES_PASSWORD="mot-de-passe-fort"
export REDIS_PASSWORD="mot-de-passe-redis"
```

### 2. SSL/TLS avec Nginx

```bash
# Démarrage avec Nginx
docker-compose --profile production up -d
```

### 3. Monitoring avancé

```bash
# Démarrage avec Prometheus/Grafana
docker-compose --profile monitoring up -d

# Accès Grafana
open http://localhost:3000
```

### 4. Sauvegarde automatique

```bash
# Script de backup
./scripts/backup.sh
```

## 🔒 Sécurité

### Fonctionnalités

- **JWT Authentication** avec refresh tokens
- **Rate limiting** par IP et utilisateur
- **CORS** configuré
- **Validation** stricte des entrées
- **Logging** sécurisé sans données sensibles
- **Circuit breakers** pour la résilience
- **Health checks** automatiques

### Bonnes pratiques

1. **Secrets** : Utiliser des variables d'environnement
2. **HTTPS** : Obligatoire en production
3. **Firewall** : Exposer uniquement les ports nécessaires
4. **Monitoring** : Surveiller les tentatives d'intrusion
5. **Updates** : Maintenir les dépendances à jour

## 📈 Performance

### Métriques typiques

| Métrique | Valeur |
|----------|---------|
| Latence moyenne | < 50ms |
| Throughput | > 1000 req/s |
| CPU usage | < 70% |
| Memory usage | < 512MB |
| Uptime | > 99.9% |

### Optimisations

- **Connection pooling** pour PostgreSQL
- **Cache Redis** pour les sessions
- **Compression** des réponses
- **Load balancing** automatique
- **Circuit breakers** pour éviter les cascades

## 🛠️ Développement

### Structure du projet

```
services/api-gateway/
├── app.py                 # Application FastAPI principale
├── config/
│   └── settings.py        # Configuration centralisée
├── routes/
│   ├── auth.py           # Authentification JWT
│   ├── parsers.py        # Routage parsers
│   ├── matching.py       # Routage matching
│   └── health.py         # Health checks
├── middleware/
│   ├── auth_middleware.py # Middleware JWT
│   ├── rate_limiting.py   # Rate limiting
│   └── logging.py         # Logging détaillé
├── utils/
│   ├── proxy.py          # Proxy HTTP intelligent
│   └── database.py       # Utilitaires DB
├── tests/                # Tests automatisés
├── requirements.txt      # Dépendances Python
├── Dockerfile           # Image Docker
└── README.md           # Cette documentation
```

### Commandes utiles

```bash
# Formater le code
black . && isort .

# Linter
flake8 . && mypy .

# Tests avec coverage
pytest --cov=. --cov-report=html

# Build Docker
docker build -t api-gateway:dev .

# Hot reload
uvicorn app:app --reload --port 5050
```

## 🤝 Contribution

1. Fork le repository
2. Créer une branche feature (`git checkout -b feature/amazing-feature`)
3. Commit les changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

## 📝 Changelog

### v2.1.0 (2024-01-15)
- ✨ API Gateway unifié
- 🔐 Authentification JWT centralisée
- ⚡ Rate limiting intelligent
- 🔄 Proxy HTTP avec circuit breaker
- 📊 Monitoring complet
- 🐳 Docker optimisé

### v2.0.0
- 🎯 CV Parser universel
- 💼 Job Parser temps réel
- 🤖 9 algorithmes ML

## 📧 Support

- **Documentation** : [GitHub Wiki](https://github.com/Bapt252/Commitment-/wiki)
- **Issues** : [GitHub Issues](https://github.com/Bapt252/Commitment-/issues)
- **Email** : baptiste.coma@gmail.com

## 📜 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

**SuperSmartMatch V2** - Révolutionner le recrutement avec l'IA 🚀
