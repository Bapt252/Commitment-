# Guide d'Intégration SuperSmartMatch-Service

## 🎯 Objectif

Ce guide vous accompagne dans l'intégration de **SuperSmartMatch-Service** dans votre écosystème **Commitment**. SuperSmartMatch sera déployé sur le **port 5062** et partagera les mêmes ressources PostgreSQL et Redis que vos autres services.

## 📋 Prérequis

- Docker et Docker Compose installés
- Git configuré
- Projet Commitment fonctionnel
- Accès aux repositories GitHub

## 🗺️ Architecture après intégration

```
Commitment Ecosystem
├── Port 5050: API principale
├── Port 5051: CV Parser
├── Port 5052: Matching service existant
├── Port 5055: Job Parser
├── Port 5060: Service de personnalisation
└── Port 5062: SuperSmartMatch-Service (NOUVEAU)

Ressources partagées:
├── PostgreSQL (postgres:5432)
├── Redis (redis:6379)
├── MinIO (storage:9000)
└── Réseau Docker: nexten-network
```

## 🚀 Méthode 1: Intégration automatique (Recommandée)

### 1. Utilisation du script automatisé

Le script `quick-supersmartmatch-integration.sh` automatise toute la procédure :

```bash
# Rendre le script exécutable
chmod +x quick-supersmartmatch-integration.sh

# Lancer l'intégration
./quick-supersmartmatch-integration.sh
```

Le script va :
- ✅ Cloner SuperSmartMatch-Service
- ✅ Configurer le port 5062
- ✅ Créer le Dockerfile adapté
- ✅ Mettre à jour les variables d'environnement
- ✅ Valider la configuration
- ✅ Proposer le démarrage des services

### 2. Validation de l'intégration

Après l'intégration automatique, testez avec :

```bash
# Rendre le script de test exécutable
chmod +x test-supersmartmatch-integration.sh

# Lancer les tests
./test-supersmartmatch-integration.sh
```

## 🛠️ Méthode 2: Intégration manuelle

### Étape 1: Clonage de SuperSmartMatch-Service

```bash
cd votre-projet-commitment
git clone https://github.com/Bapt252/SuperSmartMatch-Service.git supersmartmatch-service
```

### Étape 2: Configuration du port

Modifiez le port dans `supersmartmatch-service/app.py` :

```python
# Remplacer toutes les occurrences de 5060 par 5062
# Exemple:
app.run(host='0.0.0.0', port=5062, debug=False)
```

### Étape 3: Création du Dockerfile adapté

Créez `supersmartmatch-service/Dockerfile` :

```dockerfile
FROM python:3.11-slim

LABEL maintainer="Nexten Team"
LABEL description="SuperSmartMatch - Service unifié de matching intégré"
LABEL version="1.0.1"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=app.py
ENV PORT=5062

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/logs

RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5062

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5062/api/v1/health || exit 1

CMD ["python", "app.py"]
```

### Étape 4: Mise à jour du docker-compose.yml

Le service SuperSmartMatch a déjà été ajouté au `docker-compose.yml` :

```yaml
supersmartmatch-service:
  build:
    context: ./supersmartmatch-service
    dockerfile: Dockerfile
  container_name: nexten-supersmartmatch
  ports:
    - "5062:5062"
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
    storage:
      condition: service_healthy
  environment:
    # Variables partagées avec les autres services
    DATABASE_URL: postgresql://postgres:postgres@postgres:5432/nexten
    REDIS_URL: redis://redis:6379/0
    # Variables spécifiques SuperSmartMatch
    PORT: 5062
    SECRET_KEY: ${SECRET_KEY:-your-secret-key-here}
    # ... autres variables
  networks:
    - nexten-network
  restart: unless-stopped
```

### Étape 5: Configuration des variables d'environnement

Ajoutez ces variables à votre fichier `.env` :

```bash
# SuperSmartMatch Service Configuration
SECRET_KEY=your-super-secret-key-here-for-supersmartmatch
SUPERSMARTMATCH_SERVICE_URL=http://supersmartmatch-service:5062
DEFAULT_ALGORITHM=auto
ENABLE_CACHING=true
CACHE_TTL=3600
MAX_JOBS_PER_REQUEST=100
DEFAULT_RESULT_LIMIT=10
ENABLE_METRICS=true
METRICS_RETENTION_DAYS=30
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_PER_HOUR=1000
```

## 🚢 Déploiement

### Démarrage des services

```bash
# Arrêter les services existants
docker-compose down

# Construire SuperSmartMatch
docker-compose build supersmartmatch-service

# Démarrer tous les services
docker-compose up -d

# Vérifier le statut
docker-compose ps
```

### Vérification de l'intégration

```bash
# Test de santé SuperSmartMatch
curl http://localhost:5062/api/v1/health

# Test de l'API
curl -X POST http://localhost:5062/api/v1/match \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {"skills": ["Python", "Docker"]},
    "jobs": [{"title": "Dev Python", "requirements": ["Python"]}]
  }'
```

## 🔍 Monitoring et Surveillance

### URLs de monitoring disponibles

- **SuperSmartMatch**: http://localhost:5062
- **Health Check**: http://localhost:5062/api/v1/health
- **API Principale**: http://localhost:5050
- **RQ Dashboard**: http://localhost:9181
- **Redis Commander**: http://localhost:8081
- **MinIO Console**: http://localhost:9001

### Surveillance des logs

```bash
# Logs SuperSmartMatch
docker-compose logs supersmartmatch-service

# Logs en temps réel
docker-compose logs -f supersmartmatch-service

# Logs de tous les services
docker-compose logs
```

## 🧪 Tests et Validation

### Tests automatisés

Utilisez le script de test complet :

```bash
./test-supersmartmatch-integration.sh
```

### Tests manuels

```bash
# Test de base
curl http://localhost:5062/api/v1/health

# Test des algorithmes disponibles
curl http://localhost:5062/api/v1/algorithms

# Test de matching simple
curl -X POST http://localhost:5062/api/v1/match \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "skills": ["Python", "Docker", "PostgreSQL"],
      "experience": "2 ans",
      "location": "Paris"
    },
    "jobs": [
      {
        "title": "Développeur Python",
        "requirements": ["Python", "API", "Base de données"],
        "location": "Paris",
        "company": "TechCorp"
      }
    ]
  }'
```

## 🔧 Dépannage

### Problèmes courants

#### Port 5062 déjà utilisé

```bash
# Vérifier les ports utilisés
netstat -tulpn | grep :5062

# Arrêter le processus si nécessaire
sudo kill -9 $(lsof -t -i:5062)
```

#### Service ne démarre pas

```bash
# Vérifier les logs
docker-compose logs supersmartmatch-service

# Reconstruire l'image
docker-compose build --no-cache supersmartmatch-service

# Redémarrer le service
docker-compose restart supersmartmatch-service
```

#### Problèmes de connectivité base de données

```bash
# Tester la connexion PostgreSQL
docker-compose exec supersmartmatch-service python -c \
  "import psycopg2; psycopg2.connect('postgresql://postgres:postgres@postgres:5432/nexten'); print('OK')"

# Tester la connexion Redis
docker-compose exec supersmartmatch-service python -c \
  "import redis; redis.Redis(host='redis', port=6379).ping(); print('OK')"
```

### Commandes de diagnostic

```bash
# État des services
docker-compose ps

# Configuration complète
docker-compose config

# Ressources utilisées
docker stats

# Réseaux Docker
docker network ls | grep nexten

# Volumes Docker
docker volume ls | grep -E "(postgres|redis|minio)"
```

## 📚 Référence API

### Endpoints SuperSmartMatch

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/v1/health` | GET | Health check |
| `/api/v1/status` | GET | Statut du service |
| `/api/v1/algorithms` | GET | Algorithmes disponibles |
| `/api/v1/match` | POST | Matching profil/emplois |

### Format de réponse standard

```json
{
  "status": "success",
  "data": {
    "matches": [
      {
        "job_id": "1",
        "score": 0.85,
        "algorithm": "hybrid",
        "details": {...}
      }
    ]
  },
  "metadata": {
    "total": 1,
    "processing_time": "0.124s"
  }
}
```

## 🔄 Mise à jour

### Mise à jour de SuperSmartMatch

```bash
cd supersmartmatch-service
git pull origin main
cd ..
docker-compose build supersmartmatch-service
docker-compose restart supersmartmatch-service
```

### Sauvegarde avant mise à jour

```bash
# Sauvegarde de la configuration
cp docker-compose.yml docker-compose.yml.backup
cp .env .env.backup

# Sauvegarde des données
docker-compose exec postgres pg_dump -U postgres nexten > backup.sql
```

## 🚨 Sécurité

### Variables sensibles

Assurez-vous que les variables suivantes sont sécurisées :

- `SECRET_KEY`: Clé secrète unique
- `OPENAI`: Clé API OpenAI
- `GOOGLE_MAPS_API_KEY`: Clé Google Maps
- `WEBHOOK_SECRET`: Secret pour les webhooks

### Bonnes pratiques

- Ne jamais committer le fichier `.env`
- Utiliser des clés secrètes fortes
- Limiter l'accès aux ports externes
- Surveiller les logs d'accès

## 📞 Support

### En cas de problème

1. **Vérifiez les logs** : `docker-compose logs supersmartmatch-service`
2. **Testez la connectivité** : `./test-supersmartmatch-integration.sh`
3. **Consultez la documentation** : Ce guide et le README de SuperSmartMatch
4. **Contactez l'équipe** : Créez une issue sur GitHub

### Ressources utiles

- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [SuperSmartMatch-Service Repository](https://github.com/Bapt252/SuperSmartMatch-Service)
- [Commitment Repository](https://github.com/Bapt252/Commitment-)

---

**🎉 Félicitations !** SuperSmartMatch-Service est maintenant intégré dans votre écosystème Commitment sur le port 5062, avec accès partagé à PostgreSQL et Redis.