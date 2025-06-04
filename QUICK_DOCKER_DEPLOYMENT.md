# 🚀 SuperSmartMatch V2 - Quick Docker Deployment

## 🔧 **PROBLÈME RÉSOLU**

**Erreur originale :**
```bash
Error: pull access denied for nexten-matcher, repository does not exist
Error: pull access denied for supersmartmatch-v1, repository does not exist
```

**Solution :** Déploiement progressif avec infrastructure de base seulement.

---

## ⚡ **DÉPLOIEMENT IMMÉDIAT**

### 1. **Lancer l'Infrastructure de Base**
```bash
# Copier le fichier Docker Compose de base (déjà fait ✅)
# Lancer l'infrastructure de base
docker-compose -f docker-compose.basic.yml up -d

# Vérifier le statut
docker-compose -f docker-compose.basic.yml ps
```

### 2. **Déploiement Automatique avec Script**
```bash
# Rendre le script exécutable
chmod +x scripts/deploy_progressive.sh

# Déploiement automatique
./scripts/deploy_progressive.sh basic
```

---

## 📊 **SERVICES DISPONIBLES**

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana** | http://localhost:3000 | admin / supersmartmatch2024 |
| **Prometheus** | http://localhost:9090 | - |
| **MinIO** | http://localhost:9001 | supersmartmatch / supersmartmatch2024 |
| **PostgreSQL** | localhost:5432 | supersmartmatch_user / supersmartmatch_2024 |
| **Redis** | localhost:6379 | - |
| **Nginx** | http://localhost:80 | - |

---

## 🔍 **TESTS RAPIDES**

### Test Manuel des Services
```bash
# Test Redis
docker exec supersmartmatch-redis redis-cli ping
# Résultat attendu: PONG

# Test PostgreSQL  
docker exec supersmartmatch-postgres pg_isready -U supersmartmatch_user
# Résultat attendu: accepting connections

# Test MinIO
curl -f http://localhost:9000/minio/health/live
# Résultat attendu: 200 OK

# Test Prometheus
curl -f http://localhost:9090/-/healthy
# Résultat attendu: 200 OK

# Test Grafana
curl -f http://localhost:3000/api/health
# Résultat attendu: {"database": "ok"}

# Test Infrastructure générale
curl http://localhost/health
# Résultat attendu: healthy
```

---

## 🐛 **RÉSOLUTION DE PROBLÈMES**

### Problème : Port déjà utilisé
```bash
# Identifier les processus sur les ports
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :6379  # Redis
sudo lsof -i :3000  # Grafana
sudo lsof -i :9090  # Prometheus

# Arrêter les services existants
docker-compose -f docker-compose.basic.yml down
```

### Problème : Services ne démarrent pas
```bash
# Vérifier les logs
docker-compose -f docker-compose.basic.yml logs -f

# Logs spécifiques par service
docker-compose -f docker-compose.basic.yml logs postgres
docker-compose -f docker-compose.basic.yml logs redis
docker-compose -f docker-compose.basic.yml logs grafana
```

### Problème : Volumes persistants
```bash
# Nettoyer complètement (⚠️ ATTENTION: perte de données)
docker-compose -f docker-compose.basic.yml down -v
docker volume prune -f
```

---

## 🎯 **COMMANDES ESSENTIELLES**

### Démarrage
```bash
# Infrastructure de base
docker-compose -f docker-compose.basic.yml up -d
```

### Surveillance
```bash
# Logs en temps réel
docker-compose -f docker-compose.basic.yml logs -f

# Statut des services
docker-compose -f docker-compose.basic.yml ps

# Utilisation des ressources
docker stats
```

### Arrêt
```bash
# Arrêt propre
docker-compose -f docker-compose.basic.yml down

# Arrêt avec suppression des volumes (⚠️ perte de données)
docker-compose -f docker-compose.basic.yml down -v
```

---

## 🔄 **ÉTAPES SUIVANTES**

### 1. **Valider l'Infrastructure**
```bash
# Vérifier tous les services
./scripts/deploy_progressive.sh status

# Tests manuels
curl http://localhost:3000/api/health  # Grafana
curl http://localhost:9090/-/healthy   # Prometheus
curl http://localhost:9000/minio/health/live  # MinIO
```

### 2. **Construire les Images Applicatives**
Une fois l'infrastructure stable, vous pourrez :
```bash
# Construire les images manquantes (à implémenter)
# docker build -t supersmartmatch:v1 ./super-smart-match/
# docker build -t nexten-matcher:latest ./nexten/
```

### 3. **Déploiement Complet**
```bash
# Une fois les images construites
docker-compose -f supersmartmatch-v2/docker-compose.yml up -d
```

---

## ✅ **VALIDATION FINALE**

### Checklist de l'Infrastructure de Base
- [ ] PostgreSQL accessible (port 5432)
- [ ] Redis accessible (port 6379)
- [ ] MinIO accessible (ports 9000/9001)
- [ ] Prometheus accessible (port 9090)
- [ ] Grafana accessible (port 3000)
- [ ] Nginx accessible (port 80)
- [ ] Tous les services en état "Up"

### Commande de Validation Complète
```bash
# Validation automatique
./scripts/deploy_progressive.sh basic && echo "🎉 INFRASTRUCTURE PRÊTE !"
```

---

## 📁 **STRUCTURE CRÉÉE**

```
Commitment-/
├── docker-compose.basic.yml          # ✅ Créé
├── scripts/
│   └── deploy_progressive.sh         # ✅ Créé
├── config/                          # ✅ Auto-généré
│   ├── nginx/nginx.basic.conf
│   ├── prometheus/prometheus.yml
│   ├── grafana/datasources/
│   └── postgres/init.sql
└── logs/                           # ✅ Auto-généré
    └── deployment.log
```

---

## 🆘 **SUPPORT**

En cas de problème :

1. **Vérifier les logs :** `docker-compose -f docker-compose.basic.yml logs -f`
2. **Redémarrer un service :** `docker-compose -f docker-compose.basic.yml restart [service]`
3. **Reset complet :** `docker-compose -f docker-compose.basic.yml down -v && ./scripts/deploy_progressive.sh basic`

---

## 🚀 **RÉSULTAT ATTENDU**

Après exécution, vous devriez avoir :
- ✅ Infrastructure de base fonctionnelle
- ✅ PostgreSQL avec base de données initialisée
- ✅ Redis prêt pour cache
- ✅ MinIO pour stockage d'objets
- ✅ Monitoring Prometheus + Grafana
- ✅ Reverse proxy Nginx
- ✅ **Aucune dépendance aux images applicatives manquantes**

**Prochaine étape :** Tests infrastructure avec `./scripts/test-infrastructure.sh basic` (si disponible)
