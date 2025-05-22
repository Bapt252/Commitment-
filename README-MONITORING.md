# 🚀 Commitment- Monitoring Stack

## 📊 Session A2 - Production Monitoring

Stack de monitoring complète pour surveiller les 21 services de la plateforme Commitment-.

### 🎯 Services Critiques Surveillés

**Performances Session A1 (Benchmarks):**
- ✅ **CV Parser** (port 5051) - Latence: 1.9ms, 100% succès
- ✅ **Personalization** (port 5060) - Latence: 1.8ms, 100% succès  
- ✅ **Frontend** (port 3000) - Latence: 53ms, très rapide
- ⚠️ **Job Parser** (port 5055) - En cours de correction
- ⚠️ **Matching API** (port 5052) - En cours de correction

### 🚀 Déploiement Rapide

```bash
# Déploiement en 1 commande
chmod +x deploy-monitoring.sh
./deploy-monitoring.sh
```

### 📈 Stack Technique

- **Prometheus** (9090) - Collecte de métriques
- **Grafana** (3001) - Dashboards et visualisation
- **Alertmanager** (9093) - Gestion des alertes
- **Node Exporter** (9100) - Métriques système
- **cAdvisor** (8080) - Métriques conteneurs
- **Redis Exporter** (9121) - Métriques Redis
- **Postgres Exporter** (9187) - Métriques PostgreSQL

### 🎯 Dashboards Configurés

1. **🖥️ System Overview** - CPU, RAM, Disk, Network
2. **🚀 Services Performance** - Latences, erreurs, disponibilité
3. **📊 Business Metrics** - Matching success, volumes

### 🚨 Alertes Critiques

**Seuils basés sur Session A1:**
- 🔥 **RAM > 85%** (seuil actuel: 84%)
- ⚠️ **CPU > 80%** (niveau actuel: 8.2%)
- 💥 **Services critiques DOWN** (30s délai)
- 🐌 **Latences élevées** (>200ms)

### 🔔 Notifications

- **Email** - Alertes groupées par criticité
- **Escalation** - Critiques répétées toutes les 5min
- **Slack** - Prêt à configurer

### 📊 Accès aux Interfaces

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/commitment2025)
- **Alertmanager**: http://localhost:9093
- **cAdvisor**: http://localhost:8080

### 🛠️ Configuration Manuelle

```bash
# Démarrage manuel
docker network create nexten-network
docker-compose -f docker-compose.monitoring.yml up -d

# Vérification
docker ps | grep nexten-
curl http://localhost:9090
curl http://localhost:3001
```

### 📋 Métriques Collectées

**Système:**
- CPU, RAM, Disk, Network
- Processus, Load Average
- Container stats

**Applications:**
- Health checks tous les services
- Latences et erreurs HTTP
- Redis et PostgreSQL stats
- RQ workers et queues

**Business:**
- Taux de matching
- Volume de parsing CV/Job
- Succès des recommandations

---

🚀 **Session A2 validée** - Monitoring production opérationnel !