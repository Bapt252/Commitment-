# 🚀 SuperSmartMatch V2 - Plateforme de Recrutement IA Intégrée

> **Solution Complète** : Résolution des problèmes de connectivité réseau et intégration unifiée des microservices

## 🎯 Problèmes Résolus

✅ **Connectivité réseau Docker** : API Gateway peut maintenant communiquer avec tous les services  
✅ **Services en restart** : Configuration stable avec dépendances appropriées  
✅ **Port unifié** : API Gateway sur port 5055 avec configuration cohérente  
✅ **Architecture intégrée** : Tous les services dans un réseau Docker unifié  

## 🏗️ Architecture SuperSmartMatch V2

```
🌟 SuperSmartMatch V2 Unified Platform
├── 🌟 API Gateway (Port 5055) ← Point d'entrée unifié ✅
├── 🌐 Frontend NexTen (Port 3000) ← Interface utilisateur ✅  
├── 📊 Nexten API (Port 5000) ← Services backend existants ✅
├── 📊 Nexten Data Adapter (Port 5052) ← Adaptateur de données ✅
├── 🎯 CV Parser Service (Port 5051) ← Parsing de CV ✅
├── 💼 Job Parser Service (Port 5053) ← Parsing d'offres ✅  
├── 🤖 Matching Service (Port 5060) ← 9 algorithmes ML ✅
└── 📊 Infrastructure (Redis, PostgreSQL) ← Base de données ✅
```

## 🚀 Démarrage Rapide (2 minutes)

### Option 1 : Script Automatique (Recommandé)
```bash
# 1. Configuration initiale
./quick-setup.sh

# 2. Diagnostic et démarrage automatique
./diagnostic-and-fix.sh
```

### Option 2 : Démarrage Manuel
```bash
# 1. Prérequis
git clone https://github.com/Bapt252/Nexten-Project.git
git clone https://github.com/Bapt252/SuperSmartMatch-Service.git ../SuperSmartMatch-Service

# 2. Démarrage des services essentiels
docker-compose -f docker-compose-integrated.yml up -d redis postgres api-gateway-simple nexten-frontend

# 3. Vérification
curl http://localhost:5055/api/gateway/health
```

## 📋 Services Disponibles

### 🌟 API Gateway Unifié
- **URL** : http://localhost:5055/api/gateway/
- **Status** : http://localhost:5055/api/gateway/status  
- **Health** : http://localhost:5055/api/gateway/health
- **Docs** : http://localhost:5055/api/gateway/docs
- **Metrics** : http://localhost:5055/api/gateway/metrics

### 🌐 Frontend & Interface
- **Frontend NexTen** : http://localhost:3000
- **Nginx Status** : http://localhost:3000/nginx-status

### 🔧 Services Métier (Profiles)
```bash
# Services de parsing
docker-compose -f docker-compose-integrated.yml --profile parsing up -d

# Services Nexten
docker-compose -f docker-compose-integrated.yml --profile nexten up -d

# Service de matching ML
docker-compose -f docker-compose-integrated.yml --profile matching up -d

# Monitoring complet
docker-compose -f docker-compose-integrated.yml --profile monitoring up -d
```

## 🎯 Endpoints Intégrés

### Parsing de Documents
```bash
# Parser un CV
curl -X POST http://localhost:5055/api/gateway/parse-cv \
  -F "file=@mon-cv.pdf"

# Parser une offre d'emploi
curl -X POST http://localhost:5055/api/gateway/parse-job \
  -H "Content-Type: application/json" \
  -d '{"job_description": "Développeur Python..."}'
```

### Matching IA
```bash
# Lancer un matching
curl -X POST http://localhost:5055/api/gateway/match \
  -H "Content-Type: application/json" \
  -d '{"cv_id": "123", "job_id": "456"}'

# Lister les algorithmes
curl http://localhost:5055/api/gateway/match/algorithms
```

### Services Nexten (Proxy)
```bash
# Health check des services Nexten
curl http://localhost:5055/api/gateway/nexten/health

# Proxy vers Nexten API
curl http://localhost:5055/api/gateway/nexten/users
```

## 🔍 Monitoring et Diagnostic

### Commandes Utiles
```bash
# Status des containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Logs en temps réel
docker-compose -f docker-compose-integrated.yml logs -f api-gateway-simple

# Test de connectivité réseau
docker exec api-gateway-simple nslookup nexten-api
docker exec api-gateway-simple curl http://cv-parser:5051/health

# Monitoring continu
watch 'docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"'
```

### Health Checks
```bash
# Vérification complète du système
curl -s http://localhost:5055/api/gateway/health | jq

# Status simple
curl http://localhost:5055/api/gateway/status

# Métriques Prometheus
curl http://localhost:5055/api/gateway/metrics
```

## 🔧 Résolution de Problèmes

### Services en Restart
```bash
# Identifier les services qui redémarrent
docker ps --filter "status=restarting"

# Voir les logs d'erreur
docker logs --tail 50 <nom-du-container>

# Redémarrer un service spécifique
docker-compose -f docker-compose-integrated.yml restart api-gateway-simple
```

### Problèmes de Réseau
```bash
# Vérifier le réseau Docker
docker network inspect supersmartmatch

# Test DNS depuis l'API Gateway
docker exec api-gateway-simple nslookup cv-parser

# Test de connectivité TCP
docker exec api-gateway-simple nc -z nexten-api 5000
```

### Problèmes de Ports
```bash
# Vérifier les ports utilisés
netstat -tuln | grep -E "(3000|5000|5051|5052|5053|5055|5060)"

# Libérer un port si nécessaire
sudo lsof -ti:5055 | xargs sudo kill -9
```

## 📊 Configuration Avancée

### Variables d'Environnement
```bash
# Créer un fichier .env
cat > .env << EOF
POSTGRES_PASSWORD=mot_de_passe_securise
JWT_SECRET=cle_jwt_super_securise
OPENAI_API_KEY=votre_cle_openai
GRAFANA_PASSWORD=admin_password
EOF
```

### Scaling Horizontal
```bash
# Scaler les services de parsing
docker-compose -f docker-compose-integrated.yml up -d --scale cv-parser=3 --scale job-parser=2

# Scaler le matching service
docker-compose -f docker-compose-integrated.yml up -d --scale matching-service=2
```

### Monitoring avec Grafana
```bash
# Démarrer le monitoring complet
docker-compose -f docker-compose-integrated.yml --profile monitoring up -d

# Accéder à Grafana
open http://localhost:3001  # admin/admin
```

## 🧹 Maintenance

### Nettoyage
```bash
# Arrêt propre
docker-compose -f docker-compose-integrated.yml down

# Nettoyage complet (⚠️ supprime les données)
docker-compose -f docker-compose-integrated.yml down -v --rmi all

# Nettoyage sélectif
docker container prune -f
docker network prune -f
docker volume prune -f
```

### Mise à Jour
```bash
# Mettre à jour les images
docker-compose -f docker-compose-integrated.yml pull

# Reconstruire les images custom
docker-compose -f docker-compose-integrated.yml build --no-cache

# Redémarrage avec nouvelles images
docker-compose -f docker-compose-integrated.yml up -d --force-recreate
```

## 🎉 Validation de l'Installation

L'installation est réussie si tous ces endpoints répondent :

- ✅ `http://localhost:5055/api/gateway/health` → Status "healthy"
- ✅ `http://localhost:3000` → Frontend NexTen chargé
- ✅ `http://localhost:5055/api/gateway/docs` → Documentation Swagger
- ✅ Aucun container en status "restarting" dans `docker ps`

## 📚 Documentation

- **API Gateway** : http://localhost:5055/api/gateway/docs
- **Métriques** : http://localhost:5055/api/gateway/metrics  
- **Guide Complet** : Voir les artifacts dans le chat Claude

## 🆘 Support

En cas de problème :

1. **Exécuter le diagnostic** : `./diagnostic-and-fix.sh`
2. **Vérifier les logs** : `docker-compose -f docker-compose-integrated.yml logs -f`
3. **Nettoyer et recommencer** : `docker-compose -f docker-compose-integrated.yml down && docker container prune -f`

---

**🎯 SuperSmartMatch V2 est maintenant complètement intégré et opérationnel !** 🚀
