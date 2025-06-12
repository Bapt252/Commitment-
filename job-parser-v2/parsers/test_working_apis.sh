#!/bin/bash

# =============================================================================
# Test des APIs Fonctionnelles - SuperSmartMatch V2
# Basé sur la découverte des vrais endpoints
# =============================================================================

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${BLUE}🧪 Test des APIs Fonctionnelles SuperSmartMatch V2${NC}"
echo "=================================================="

# Test de santé des services
test_service_health() {
    local url=$1
    local name=$2
    
    if curl -f -s "$url" > /dev/null 2>&1; then
        log_success "$name - Service UP"
        return 0
    else
        log_error "$name - Service DOWN"
        return 1
    fi
}

# 1. Test de santé de base
log_info "🔍 Vérification de l'état des services..."

test_service_health "http://localhost:5053/health" "Job Parser"
test_service_health "http://localhost:5052/health" "Matching Service"
test_service_health "http://localhost:3001/api/health" "Grafana"
test_service_health "http://localhost:9090" "Prometheus"

echo ""

# 2. Exploration Job Parser via FastAPI docs
log_info "📖 Exploration de la documentation Job Parser..."

echo "🌐 Documentation FastAPI disponible sur: http://localhost:5053/docs"
echo "🌐 JSON Schema disponible sur: http://localhost:5053/openapi.json"

# Récupérer le schéma OpenAPI pour voir les endpoints
OPENAPI_SCHEMA=$(curl -s http://localhost:5053/openapi.json 2>/dev/null)
if [ $? -eq 0 ]; then
    log_success "Schéma OpenAPI récupéré"
    echo "📋 Endpoints disponibles dans Job Parser:"
    echo "$OPENAPI_SCHEMA" | jq '.paths | keys[]' 2>/dev/null || echo "   (Utilisez http://localhost:5053/docs pour voir l'interface)"
else
    log_warning "Impossible de récupérer le schéma OpenAPI"
fi

echo ""

# 3. Test Matching Service avec différentes méthodes
log_info "🎯 Test du Matching Service..."

# Test GET sur /api/match
echo "🔍 Test GET /api/match:"
GET_RESPONSE=$(curl -s -w "HTTP %{http_code}" http://localhost:5052/api/match 2>/dev/null)
echo "   Réponse: $GET_RESPONSE"

# Test POST sur /api/match  
echo "🔍 Test POST /api/match:"
POST_RESPONSE=$(curl -s -w "HTTP %{http_code}" -X POST \
    -H "Content-Type: application/json" \
    -d '{"test": "data"}' \
    http://localhost:5052/api/match 2>/dev/null)
echo "   Réponse: $POST_RESPONSE"

# Test root endpoint du matching
echo "🔍 Test GET /:"
ROOT_RESPONSE=$(curl -s http://localhost:5052/ 2>/dev/null)
if echo "$ROOT_RESPONSE" | grep -q -i "matching\|nexten\|api"; then
    log_success "Service Matching répond avec informations utiles"
    echo "   Réponse: $ROOT_RESPONSE"
else
    log_warning "Réponse du service Matching peu informative"
fi

echo ""

# 4. Test Grafana API
log_info "📊 Test des APIs Grafana..."

# Test authentification
GRAFANA_AUTH=$(curl -s -u admin:admin123 http://localhost:3001/api/health 2>/dev/null)
if echo "$GRAFANA_AUTH" | grep -q "ok"; then
    log_success "Authentification Grafana réussie"
    echo "   Version: $(echo "$GRAFANA_AUTH" | jq -r '.version' 2>/dev/null || echo 'N/A')"
else
    log_error "Problème d'authentification Grafana"
fi

# Test des datasources
DATASOURCES=$(curl -s -u admin:admin123 http://localhost:3001/api/datasources 2>/dev/null)
if [ $? -eq 0 ]; then
    log_success "API Datasources accessible"
    echo "   Datasources configurées: $(echo "$DATASOURCES" | jq 'length' 2>/dev/null || echo 'N/A')"
else
    log_warning "Problème d'accès aux datasources"
fi

echo ""

# 5. Test Prometheus
log_info "📈 Test des APIs Prometheus..."

# Test des métriques
PROMETHEUS_METRICS=$(curl -s "http://localhost:9090/api/v1/label/__name__/values" 2>/dev/null)
if echo "$PROMETHEUS_METRICS" | grep -q "data"; then
    METRICS_COUNT=$(echo "$PROMETHEUS_METRICS" | jq '.data | length' 2>/dev/null || echo "0")
    log_success "Prometheus collecte $METRICS_COUNT métriques"
else
    log_warning "Problème de récupération des métriques Prometheus"
fi

# Test des targets
PROMETHEUS_TARGETS=$(curl -s "http://localhost:9090/api/v1/targets" 2>/dev/null)
if echo "$PROMETHEUS_TARGETS" | grep -q "activeTargets"; then
    log_success "Prometheus monitoring des targets actif"
else
    log_warning "Problème de monitoring des targets"
fi

echo ""

# 6. Résumé et recommandations
log_info "📋 Résumé pour l'intégration frontend..."

echo ""
echo -e "${GREEN}✅ APIs Prêtes pour l'intégration:${NC}"
echo "  🎯 Matching Service:    http://localhost:5052/"
echo "  💼 Job Parser:          http://localhost:5053/ (voir /docs)"
echo "  📊 Grafana:             http://localhost:3001/ (admin/admin123)"
echo "  📈 Prometheus:          http://localhost:9090/"

echo ""
echo -e "${YELLOW}⚠️  APIs à corriger:${NC}"
echo "  📄 CV Parser:           Service détecté mais endpoints non trouvés"
echo "  🔗 API Gateway:         Service non démarré"

echo ""
echo -e "${BLUE}🔗 Endpoints pour votre frontend:${NC}"
cat << 'EOL'
const API_CONFIG = {
  MATCHING_SERVICE: 'http://localhost:5052',
  JOB_PARSER: 'http://localhost:5053',
  GRAFANA: 'http://localhost:3001',
  PROMETHEUS: 'http://localhost:9090',
  
  // Endpoints de test
  HEALTH_CHECKS: {
    matching: '/health',
    jobParser: '/health',
    grafana: '/api/health'
  },
  
  // Documentation
  JOB_PARSER_DOCS: '/docs',
  JOB_PARSER_SCHEMA: '/openapi.json'
};
EOL

echo ""
echo -e "${GREEN}🚀 Prochaines étapes:${NC}"
echo "  1. Ouvrir http://localhost:5053/docs pour voir les endpoints Job Parser"
echo "  2. Tester l'intégration avec les APIs fonctionnelles"
echo "  3. Réparer CV Parser et Gateway si nécessaire"
echo "  4. Utiliser Grafana pour monitorer les performances"

echo ""
echo "✅ Test terminé - $(date)"
