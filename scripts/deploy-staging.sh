#!/bin/bash
set -euo pipefail

log() { echo -e "\033[0;34m[$(date +'%H:%M:%S')]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[$(date +'%H:%M:%S')] ✅ $1\033[0m"; }

log "🚀 Déploiement staging..."

# Staging avec ports différents pour éviter conflits
docker-compose -f docker-compose.yml up -d
sleep 30

# Tests automatiques
if ./scripts/smoke-tests.sh all; then
    log_success "🎉 Staging déployé avec succès"
    log "📊 Grafana: http://localhost:3000 (admin/admin)"
    log "🔗 API: http://localhost"
else
    log_error "Déploiement staging échoué"
    exit 1
fi
