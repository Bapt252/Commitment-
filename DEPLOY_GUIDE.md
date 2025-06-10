# 🚀 SuperSmartMatch V2 - Guide de Déploiement Rapide

## ⚡ Déploiement en Une Commande

```bash
# Cloner et déployer
git clone https://github.com/Bapt252/Commitment-.git
cd Commitment-
git checkout microservices-refactor

# Déploiement automatisé complet
chmod +x scripts/deploy-automation.sh
./scripts/deploy-automation.sh
```

## 🎯 Ce que fait le script automatiquement

1. **Gère les conflits de fichiers** locaux avec options
2. **Génère des mots de passe sécurisés** pour la production
3. **Vérifie les prérequis** (Docker, Docker Compose)
4. **Déploie l'infrastructure complète** :
   - 7 microservices (API Gateway, CV Parser, Job Parser, Matching, User, Notification, Analytics)
   - Base de données PostgreSQL
   - Cache Redis
   - Stockage MinIO
   - Load balancer Nginx
   - Monitoring Prometheus + Grafana
5. **Exécute les tests de santé** automatiquement
6. **Affiche les informations d'accès**

## 🌐 Points d'accès après déploiement

| Service | URL | Description |
|---------|-----|-------------|
| **Application** | http://localhost | Point d'entrée principal |
| **API Gateway** | http://localhost/api | API REST sécurisée |
| **Grafana** | http://localhost:3000 | Monitoring (admin/[password]) |
| **Prometheus** | http://localhost:9090 | Métriques |
| **MinIO** | http://localhost:9001 | Console stockage |

## 🧪 Tests d'intégration complets

```bash
# Tests complets
chmod +x scripts/test-integration-complete.sh
./scripts/test-integration-complete.sh all

# Tests spécifiques
./scripts/test-integration-complete.sh auth
./scripts/test-integration-complete.sh matching
./scripts/test-integration-complete.sh cv
```

## 🔧 Gestion des services

```bash
# Voir l'état
docker-compose -f docker-compose.production.yml ps

# Logs en temps réel
docker-compose -f docker-compose.production.yml logs -f

# Arrêter
./scripts/deploy-production.sh stop

# Redémarrer
./scripts/deploy-production.sh restart
```

## 🚨 En cas de problème

1. **Vérifier les logs** : `docker-compose -f docker-compose.production.yml logs [service]`
2. **Tester la santé** : `curl http://localhost/health`
3. **Relancer le déploiement** : `./scripts/deploy-automation.sh`

---

## 🎉 Architecture déployée

- ✅ **7 Microservices** production-ready
- ✅ **Infrastructure complète** (DB, Cache, Storage, Monitoring)
- ✅ **Sécurité enterprise** (JWT, HTTPS, Secrets)
- ✅ **Tests automatisés** d'intégration
- ✅ **Monitoring temps réel** avec alertes

**Status** : 🟢 Production Ready
**Conformité** : 📋 100% Architecture Microservices V2