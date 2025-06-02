#!/bin/bash

# SuperSmartMatch V2 - Script de validation système
# ================================================
# Valide que tous les composants fonctionnent correctement

set -e

echo "🚀 SuperSmartMatch V2 - Validation Système"
echo "=========================================="

# Configuration
SUPERSMARTMATCH_V2_URL="${SUPERSMARTMATCH_V2_URL:-http://localhost:5070}"
NEXTEN_MATCHER_URL="${NEXTEN_MATCHER_URL:-http://localhost:5052}"
SUPERSMARTMATCH_V1_URL="${SUPERSMARTMATCH_V1_URL:-http://localhost:5062}"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction de logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Fonction de test HTTP
test_endpoint() {
    local url="$1"
    local expected_status="$2"
    local description="$3"
    
    log_info "Test: $description"
    
    if command -v curl >/dev/null 2>&1; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" || echo "000")
        
        if [ "$response" = "$expected_status" ]; then
            log_success "✅ $description - Status: $response"
            return 0
        else
            log_error "❌ $description - Expected: $expected_status, Got: $response"
            return 1
        fi
    else
        log_error "❌ curl n'est pas installé"
        return 1
    fi
}

# Fonction de test JSON
test_json_endpoint() {
    local url="$1"
    local json_data="$2"
    local description="$3"
    
    log_info "Test: $description"
    
    response=$(curl -s -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$json_data" \
        -w "%{http_code}" \
        -o /tmp/supersmartmatch_test_response.json 2>/dev/null || echo "000")
    
    if [ "$response" = "200" ]; then
        log_success "✅ $description - Status: $response"
        if [ -f /tmp/supersmartmatch_test_response.json ]; then
            log_info "Réponse: $(cat /tmp/supersmartmatch_test_response.json | head -c 200)..."
        fi
        return 0
    else
        log_error "❌ $description - Status: $response"
        if [ -f /tmp/supersmartmatch_test_response.json ]; then
            log_error "Erreur: $(cat /tmp/supersmartmatch_test_response.json)"
        fi
        return 1
    fi
}

# Variables pour compter les résultats
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# Fonction pour exécuter un test
run_test() {
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    if "$@"; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

echo ""
log_info "🏥 1. Tests de santé des services"
echo "================================="

# Test de SuperSmartMatch V2
run_test test_endpoint "$SUPERSMARTMATCH_V2_URL/api/v2/health" "200" "SuperSmartMatch V2 Health Check"

# Test de la page d'accueil V2
run_test test_endpoint "$SUPERSMARTMATCH_V2_URL/" "200" "SuperSmartMatch V2 Root Endpoint"

# Test des métriques
run_test test_endpoint "$SUPERSMARTMATCH_V2_URL/api/v2/metrics" "200" "SuperSmartMatch V2 Metrics"

# Test du status des algorithmes
run_test test_endpoint "$SUPERSMARTMATCH_V2_URL/api/v2/algorithms/status" "200" "SuperSmartMatch V2 Algorithm Status"

echo ""
log_info "🧠 2. Tests des endpoints de matching"
echo "====================================="

# Données de test pour le matching
CV_DATA='{
  "cv_data": {
    "competences": ["Python", "FastAPI", "Machine Learning"],
    "experience": 5,
    "localisation": "Paris",
    "questionnaire_complete": true
  },
  "jobs": [
    {
      "id": "job-123",
      "titre": "Développeur Python Senior",
      "competences": ["Python", "Django"],
      "localisation": "Lyon",
      "type_contrat": "CDI"
    }
  ],
  "options": {
    "max_results": 5,
    "enable_fallback": true
  }
}'

# Test de l'endpoint V2
run_test test_json_endpoint "$SUPERSMARTMATCH_V2_URL/api/v2/match" "$CV_DATA" "SuperSmartMatch V2 Matching Endpoint"

# Test de l'endpoint de compatibilité V1
CV_DATA_V1='{
  "cv_data": {
    "competences": ["Python", "FastAPI"],
    "experience": 3,
    "localisation": "Paris"
  },
  "job_data": [
    {
      "id": "job-456",
      "competences": ["Python", "Django"],
      "localisation": "Paris"
    }
  ]
}'

run_test test_json_endpoint "$SUPERSMARTMATCH_V2_URL/api/v1/match" "$CV_DATA_V1" "SuperSmartMatch V2 Compatibility V1 Endpoint"

echo ""
log_info "🔗 3. Tests des services externes (optionnel)"
echo "=============================================="

# Test de Nexten Matcher (si disponible)
if curl -s "$NEXTEN_MATCHER_URL/health" >/dev/null 2>&1; then
    run_test test_endpoint "$NEXTEN_MATCHER_URL/health" "200" "Nexten Matcher Service"
else
    log_warning "⚠️ Nexten Matcher non accessible sur $NEXTEN_MATCHER_URL"
fi

# Test de SuperSmartMatch V1 (si disponible)
if curl -s "$SUPERSMARTMATCH_V1_URL/api/v1/health" >/dev/null 2>&1; then
    run_test test_endpoint "$SUPERSMARTMATCH_V1_URL/api/v1/health" "200" "SuperSmartMatch V1 Service"
else
    log_warning "⚠️ SuperSmartMatch V1 non accessible sur $SUPERSMARTMATCH_V1_URL"
fi

echo ""
log_info "🧪 4. Tests de charge légers"
echo "============================"

# Test de charge simple
log_info "Exécution de 5 requêtes simultanées..."
for i in {1..5}; do
    curl -s -X POST "$SUPERSMARTMATCH_V2_URL/api/v2/match" \
        -H "Content-Type: application/json" \
        -d "$CV_DATA" > /dev/null &
done

wait
log_success "✅ Tests de charge légers terminés"

echo ""
log_info "📊 5. Validation des métriques"
echo "=============================="

# Test que les métriques sont collectées
METRICS_RESPONSE=$(curl -s "$SUPERSMARTMATCH_V2_URL/api/v2/metrics")
if echo "$METRICS_RESPONSE" | grep -q "total_requests"; then
    log_success "✅ Métriques collectées correctement"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    log_error "❌ Problème avec la collecte de métriques"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

echo ""
log_info "🐳 6. Validation Docker (si applicable)"
echo "======================================="

# Vérification des containers Docker
if command -v docker >/dev/null 2>&1; then
    if docker ps | grep -q "supersmartmatch-v2"; then
        log_success "✅ Container SuperSmartMatch V2 en cours d'exécution"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        log_warning "⚠️ Container SuperSmartMatch V2 non trouvé"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
else
    log_warning "⚠️ Docker non installé - skip"
fi

echo ""
echo "=========================================="
log_info "📋 RÉSUMÉ DE LA VALIDATION"
echo "=========================================="

echo "Tests total: $TESTS_TOTAL"
echo "Tests réussis: $TESTS_PASSED"
echo "Tests échoués: $TESTS_FAILED"

if [ $TESTS_FAILED -eq 0 ]; then
    log_success "🎉 TOUS LES TESTS SONT PASSÉS!"
    log_success "SuperSmartMatch V2 est opérationnel et prêt pour la production."
    exit 0
else
    log_error "💥 $TESTS_FAILED test(s) ont échoué."
    log_error "Veuillez vérifier les logs et corriger les problèmes avant le déploiement."
    exit 1
fi

# Nettoyage
rm -f /tmp/supersmartmatch_test_response.json
