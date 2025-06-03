# 📚 Runbook Opérationnel - SuperSmartMatch V2

## 🚨 Procédures d'Urgence

### Rollback Immédiat
```bash
./scripts/migration-progressive.sh rollback
./scripts/smoke-tests.sh v1
```

### Status Services
```bash
docker-compose ps
./scripts/migration-progressive.sh status
```

### Logs Temps Réel
```bash
docker-compose logs -f --tail=100
```

## 📊 Monitoring

### Dashboards Critiques
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

### Métriques Clés
- Temps de réponse < 100ms
- Taux d'erreur < 5%
- Disponibilité > 99%

## �� Maintenance

### Restart Services
```bash
docker-compose restart supersmartmatch-v2
```

### Update Configuration
```bash
# Éditer nginx/nginx.conf
docker-compose exec nginx nginx -s reload
```

### Backup
```bash
docker-compose exec redis redis-cli BGSAVE
```
