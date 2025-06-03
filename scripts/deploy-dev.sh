#!/bin/bash
set -euo pipefail

log() { echo -e "\033[0;34m[$(date +'%H:%M:%S')]\033[0m $1"; }
log_success() { echo -e "\033[0;32m[$(date +'%H:%M:%S')] ✅ $1\033[0m"; }
log_error() { echo -e "\033[0;31m[$(date +'%H:%M:%S')] ❌ $1\033[0m"; }

log "🚀 Déploiement développement SuperSmartMatch V2..."

# Nettoyage préventif
log "🧹 Nettoyage préventif..."
docker-compose -f docker-compose.dev.yml down --remove-orphans 2>/dev/null || true

# Déploiement propre
log "📦 Démarrage services mockés..."
docker-compose -f docker-compose.dev.yml up -d --build

# Attente démarrage
log "⏳ Attente démarrage services (45s)..."
sleep 45

# Tests de santé
log "🧪 Tests de santé..."
if curl -sf http://localhost/health > /dev/null 2>&1; then
    log_success "🎉 Déploiement réussi!"
    
    echo ""
    echo "📊 SuperSmartMatch V2 - Services Déployés:"
    echo "  ✅ Load Balancer: http://localhost/health"
    echo "  ✅ API V1: http://localhost:5062/health"
    echo "  ✅ API V2: http://localhost:5070/health"
    echo "  ✅ Nexten: http://localhost:5052/health"
    echo "  ✅ Grafana: http://localhost:3000 (admin/admin)"
    echo "  ✅ Prometheus: http://localhost:9090"
    echo ""
    echo "🧪 Test A/B Matching:"
    echo '  V1: curl -X POST http://localhost/api/match?version=v1 -H "Content-Type: application/json" -d '"'"'{"candidate":{"name":"Test","skills":["Python"],"experience":3},"jobs":[{"id":1,"title":"Dev","required_skills":["Python"]}]}'"'"''
    echo '  V2: curl -X POST http://localhost/api/match?version=v2 -H "Content-Type: application/json" -d '"'"'{"candidate":{"name":"Test","skills":["Python"],"experience":3},"jobs":[{"id":1,"title":"Dev","required_skills":["Python"]}]}'"'"''
    
else
    log_error "❌ Déploiement échoué"
    echo "🔍 Logs des services:"
    docker-compose -f docker-compose.dev.yml logs --tail=20
    exit 1
fi
