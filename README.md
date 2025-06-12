# 🚀 SuperSmartMatch V2 - Migration Production

## Quick Start

```bash
# 1. Vérification prérequis
./scripts/migration-progressive.sh check

# 2. Déploiement staging
./scripts/deploy-staging.sh

# 3. Tests
./scripts/smoke-tests.sh all

# 4. Déploiement production (quand prêt)
./scripts/migration-progressive.sh deploy
```

## Monitoring

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **API**: http://localhost

## Support

- **Issues**: GitHub Issues
- **Docs**: docs/
- **Runbook**: docs/runbook-operations.md

## Architecture

```
[Load Balancer] → [V1] ← Migration progressive → [V2]
       ↓              ↓                           ↓
   [Monitoring] ← [Redis Cache] → [Nexten Fallback]
```

**Objectifs V2**:
- ✅ +13% précision matching
- ✅ 50ms temps de réponse constant  
- ✅ Migration zero-downtime
- ✅ Rollback automatique < 2min
