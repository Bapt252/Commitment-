# 🛠️ SuperSmartMatch V2 - Corrections de Déploiement

## 🚨 Problèmes Résolus

### **1. Authentification Redis ✅**
- **Problème**: `NOAUTH Authentication required` - Services ne peuvent pas se connecter à Redis
- **Cause**: Redis configuré avec mot de passe mais URLs de connexion sans authentification
- **Solution**: Correction des REDIS_URL dans tous les services
  ```bash
  # Avant
  REDIS_URL=redis://redis:6379
  
  # Après  
  REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
  ```

### **2. PostgreSQL Redémarrages ✅**
- **Problème**: Container PostgreSQL redémarre constamment
- **Cause**: Variables d'environnement manquantes et health checks trop agressifs
- **Solution**: 
  - Création du fichier `.env.production` avec toutes les variables
  - Amélioration des health checks PostgreSQL
  - Ajout de paramètres d'initialisation PostgreSQL

### **3. Résolution DNS Services ✅**
- **Problème**: `getaddrinfo EAI_AGAIN postgres` - Services ne trouvent pas PostgreSQL
- **Cause**: Services démarrés avant que PostgreSQL soit prêt
- **Solution**: Ajout de `depends_on` avec conditions de santé

### **4. Port Prometheus ✅**
- **Problème**: Conflit de port avec documentation (9090 vs 9091)
- **Cause**: Port 9090 potentiellement utilisé par d'autres services
- **Solution**: Mapping port 9091:9090 pour Prometheus

## 🔧 Changements Techniques

### **Variables d'Environnement**
Ajout du fichier `.env.production` avec:
```bash
JWT_SECRET=supersmartmatch_jwt_secret_2025_production_512bits_secure_change_this_immediately
REDIS_PASSWORD=redis_secure_password_2025_change_this
POSTGRES_PASSWORD=postgres_secure_password_2025_change_this
MINIO_ACCESS_KEY=supersmartmatch_admin
MINIO_SECRET_KEY=minio_secure_secret_key_2025_change_this
# ... autres variables
```

### **Docker Compose Améliorations**
1. **Health Checks Robustes**:
   ```yaml
   # PostgreSQL
   healthcheck:
     test: ["CMD-SHELL", "pg_isready -U ssm_user -d supersmartmatch"]
     interval: 10s
     timeout: 5s
     retries: 5
     start_period: 30s
   
   # Redis  
   healthcheck:
     test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD}", "ping"]
     interval: 10s
     timeout: 3s
     retries: 3
     start_period: 10s
   ```

2. **Dépendances avec Conditions**:
   ```yaml
   depends_on:
     postgres:
       condition: service_healthy
     redis:
       condition: service_healthy
   ```

3. **Configuration Redis Sécurisée**:
   ```yaml
   command: >
     redis-server
     --requirepass ${REDIS_PASSWORD}
     --maxmemory 1gb
     --maxmemory-policy allkeys-lru
     --tcp-keepalive 300
     --timeout 0
   ```

### **Script de Déploiement Automatisé**
Création de `fix-deployment.sh` avec:
- ✅ Vérification des prérequis
- ✅ Déploiement étape par étape
- ✅ Diagnostics automatiques  
- ✅ Health checks complets
- ✅ Menu interactif
- ✅ Gestion des logs

## 🚀 Instructions de Déploiement

### **Méthode 1: Script Automatique (Recommandé)**
```bash
# 1. Récupérer les dernières modifications
git pull origin microservices-refactor

# 2. Rendre le script exécutable
chmod +x fix-deployment.sh

# 3. Lancer le script interactif
./fix-deployment.sh

# 4. Choisir "1) Redéploiement complet" dans le menu
```

### **Méthode 2: Manuelle**
```bash
# 1. Arrêter les services existants
docker-compose -f docker-compose.production.yml down

# 2. Nettoyer si nécessaire (optionnel - supprime les données)
docker-compose -f docker-compose.production.yml down -v
docker volume prune -f

# 3. Créer les répertoires nécessaires
mkdir -p logs/{api-gateway,cv-parser,job-parser,matching,user,notification,analytics,nginx}
mkdir -p temp/{cv-uploads,job-uploads}
mkdir -p monitoring/{prometheus,grafana}/{dashboards,datasources,rules}

# 4. Déploiement étape par étape
docker-compose -f docker-compose.production.yml up -d postgres redis minio
sleep 30  # Attendre que l'infrastructure soit prête

docker-compose -f docker-compose.production.yml up -d \
  cv-parser-service job-parser-service matching-service \
  user-service notification-service analytics-service
sleep 20

docker-compose -f docker-compose.production.yml up -d api-gateway
sleep 10

docker-compose -f docker-compose.production.yml up -d nginx prometheus grafana
```

## 🔍 Vérifications Post-Déploiement

### **1. Health Checks Services**
```bash
# Infrastructure
curl http://localhost:5432  # PostgreSQL
curl http://localhost:6379  # Redis  
curl http://localhost:9000  # MinIO

# Services métiers
curl http://localhost:5051/health  # CV Parser
curl http://localhost:5052/health  # Matching Service  
curl http://localhost:5053/health  # Job Parser
curl http://localhost:5054/health  # User Service
curl http://localhost:5055/health  # Notification Service
curl http://localhost:5056/health  # Analytics Service

# API Gateway et Monitoring
curl http://localhost:5050/health  # API Gateway
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:9091  # Prometheus
```

### **2. Connexions Base de Données**
```bash
# Test connexion PostgreSQL
docker-compose -f docker-compose.production.yml exec postgres \
  psql -U ssm_user -d supersmartmatch -c "SELECT version();"

# Vérifier les bases créées
docker-compose -f docker-compose.production.yml exec postgres \
  psql -U ssm_user -d supersmartmatch -c "\l"

# Test Redis
docker-compose -f docker-compose.production.yml exec redis \
  redis-cli -a ${REDIS_PASSWORD} ping
```

### **3. Logs en Temps Réel**
```bash
# Tous les services
docker-compose -f docker-compose.production.yml logs -f

# Service spécifique
docker-compose -f docker-compose.production.yml logs -f api-gateway
docker-compose -f docker-compose.production.yml logs -f postgres
docker-compose -f docker-compose.production.yml logs -f redis
```

## 🔧 Troubleshooting

### **Si PostgreSQL redémarre encore**
```bash
# Vérifier les logs
docker-compose -f docker-compose.production.yml logs postgres

# Vérifier l'espace disque
df -h

# Réinitialiser complètement
docker-compose -f docker-compose.production.yml down -v
docker volume rm $(docker volume ls -q | grep postgres)
docker-compose -f docker-compose.production.yml up -d postgres
```

### **Si Redis refuse les connexions**
```bash
# Vérifier la configuration Redis
docker-compose -f docker-compose.production.yml exec redis redis-cli

# Test avec mot de passe
docker-compose -f docker-compose.production.yml exec redis \
  redis-cli -a ${REDIS_PASSWORD} config get requirepass

# Redémarrer Redis
docker-compose -f docker-compose.production.yml restart redis
```

### **Si les services ne trouvent pas PostgreSQL**
```bash
# Vérifier le réseau Docker
docker network ls
docker network inspect supersmartmatch_microservices_network

# Test de connectivité réseau
docker-compose -f docker-compose.production.yml exec cv-parser-service \
  nc -zv postgres 5432
```

## 📊 Monitoring et Alertes

### **Accès aux Dashboards**
- **Grafana**: http://localhost:3000 (admin / grafana_secure_password_2025_change_this)
- **Prometheus**: http://localhost:9091
- **MinIO Console**: http://localhost:9001

### **Métriques Clés à Surveiller**
1. **Infrastructure**:
   - CPU et RAM de chaque service
   - Connexions PostgreSQL actives
   - Hit rate Redis
   - Espace disque MinIO

2. **Services**:
   - Latence des API (P95 < 100ms)
   - Taux d'erreur (< 1%)
   - Throughput par service
   - Santé des health checks

## 🚨 Sécurité Production

### **⚠️ IMPORTANT: Changer les Secrets**
Avant la production, modifiez dans `.env.production`:
```bash
# Génération de secrets sécurisés
JWT_SECRET=$(openssl rand -base64 64)
REDIS_PASSWORD=$(openssl rand -base64 32)  
POSTGRES_PASSWORD=$(openssl rand -base64 32)
MINIO_SECRET_KEY=$(openssl rand -base64 32)
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16)
```

### **Checklist Sécurité**
- [ ] Tous les mots de passe changés
- [ ] JWT secret unique (512 bits minimum)
- [ ] SSL/TLS activé pour la production
- [ ] Ports sensibles non exposés publiquement
- [ ] Logs d'audit activés
- [ ] Backups automatiques configurés

## 📈 Performance Optimisée

### **Ressources Allouées**
```yaml
# Configuration optimisée pour production
postgres: 2GB RAM, 1 CPU
redis: 1GB RAM, 0.5 CPU  
matching-service: 2GB RAM, 2 CPU (service le plus intensif)
api-gateway: 512MB RAM, 0.5 CPU
autres services: 512MB-1GB RAM, 0.5-1 CPU
```

### **Paramètres PostgreSQL Optimisés**
- `shared_buffers=256MB`
- `effective_cache_size=1GB`
- `max_connections=200`
- `work_mem=4MB`

---

## ✅ Validation Déploiement

Une fois le déploiement terminé, vous devriez avoir:
- ✅ 7 microservices opérationnels
- ✅ Infrastructure complète (PostgreSQL, Redis, MinIO)
- ✅ API Gateway avec authentification JWT
- ✅ Monitoring avec Prometheus et Grafana
- ✅ Reverse proxy Nginx configuré
- ✅ Health checks tous verts
- ✅ Logs centralisés accessibles

**🎉 SuperSmartMatch V2 est maintenant prêt pour la production !**
