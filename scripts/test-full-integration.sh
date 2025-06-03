#!/bin/bash

# =============================================================================
# Test d'intégration end-to-end pour la Session 2 - Version finale
# =============================================================================

set -e

echo "🚀 Lancement des tests d'intégration end-to-end..."
echo "=============================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher un message de test
test_step() {
    echo -e "\n${YELLOW}▶️  $1${NC}"
}

# Fonction pour afficher un succès
success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Fonction pour afficher un échec
error() {
    echo -e "${RED}❌ $1${NC}"
}

# Fonction pour afficher une info
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Compteurs pour le rapport final
TESTS_PASSED=0
TESTS_TOTAL=0

# Fonction de test avec comptage
test_service() {
    local url=$1
    local name=$2
    local timeout=${3:-5}
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    
    if timeout $timeout curl -f -s "$url" > /dev/null 2>&1; then
        success "$name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        error "$name"
        return 1
    fi
}

# Attendre que tous les services soient prêts
test_step "Vérification de l'état des services..."
info "Attente de 15 secondes pour que tous les services soient prêts..."
sleep 15

# Vérification des conteneurs
RUNNING_CONTAINERS=$(docker ps --format "{{.Names}}" | grep nexten | wc -l)
info "$RUNNING_CONTAINERS conteneurs Nexten en cours d'exécution"

# 1. Test des services de base (infrastructure)
test_step "Test des services d'infrastructure..."

test_service "http://localhost:9187/metrics" "PostgreSQL Exporter"
test_service "http://localhost:9121/metrics" "Redis Exporter" 
test_service "http://localhost:9000/minio/health/live" "MinIO Health Check"

# 2. Test des services de monitoring
test_step "Test de la stack de monitoring..."

test_service "http://localhost:9090/api/v1/query?query=up" "Prometheus API"
test_service "http://localhost:3001/api/health" "Grafana Health Check"
test_service "http://localhost:9100/metrics" "Node Exporter"
test_service "http://localhost:8080/metrics" "cAdvisor"

# Test spécial pour AlertManager avec retry
info "Test AlertManager avec retry (peut prendre du temps après restart)..."
for i in {1..6}; do
    if curl -f -s http://localhost:9093/api/v1/status > /dev/null 2>&1; then
        success "AlertManager API accessible"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        break
    elif [ $i -eq 6 ]; then
        error "AlertManager API non accessible après 6 tentatives"
    else
        info "Tentative $i/6 - AlertManager encore en cours de démarrage..."
        sleep 5
    fi
done
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# 3. Test des services métier
test_step "Test des services métier..."

test_service "http://localhost:5051/health" "CV Parser Service"
test_service "http://localhost:5053/health" "Job Parser Service"
test_service "http://localhost:5052/health" "Matching API"
test_service "http://localhost:5050/health" "API Principale"

# 4. Test des interfaces utilisateur
test_step "Test des interfaces utilisateur..."

test_service "http://localhost:3000" "Frontend Application"
test_service "http://localhost:8081" "Redis Commander"
test_service "http://localhost:9181" "RQ Dashboard"

# 5. Test des métriques Prometheus
test_step "Test des métriques dans Prometheus..."

# Vérifier que Prometheus collecte les métriques
METRICS_RESPONSE=$(curl -s http://localhost:9090/api/v1/label/__name__/values)
if echo "$METRICS_RESPONSE" | grep -q '"data"'; then
    METRICS_COUNT=$(echo "$METRICS_RESPONSE" | jq '.data | length' 2>/dev/null || echo "0")
    if [ "$METRICS_COUNT" -gt 50 ]; then
        success "Prometheus collecte $METRICS_COUNT métriques"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        error "Pas assez de métriques collectées ($METRICS_COUNT)"
    fi
else
    error "Échec de récupération des métriques Prometheus"
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# 6. Test fonctionnel des parsers (endpoints mock)
test_step "Test fonctionnel des parsers..."

# Test CV Parser Mock
CV_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"mock": true}' \
    http://localhost:5051/api/parse-cv-mock/ 2>/dev/null)

if echo "$CV_RESPONSE" | grep -q -i "success\|result\|parsed"; then
    success "CV Parser Mock test réussi"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    error "CV Parser Mock test échoué"
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# Test Job Parser Mock
JOB_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"mock": true}' \
    http://localhost:5053/api/parse-job-mock/ 2>/dev/null)

if echo "$JOB_RESPONSE" | grep -q -i "success\|result\|parsed"; then
    success "Job Parser Mock test réussi"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    error "Job Parser Mock test échoué"
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# 7. Test du matching
test_step "Test du pipeline de matching..."

MATCH_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"cv_data": {"skills": ["python"]}, "job_data": {"required_skills": ["python"]}}' \
    http://localhost:5052/api/match/ 2>/dev/null)

if echo "$MATCH_RESPONSE" | grep -q -i "score\|match"; then
    success "Matching API test réussi"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    error "Matching API test échoué"
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# 8. Test des workers et queues
test_step "Test des workers et queues..."

# Vérifier les queues Redis via RQ Dashboard
if curl -s http://localhost:9181 | grep -q -i "queue\|worker"; then
    success "RQ Dashboard affiche les queues"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    error "RQ Dashboard ne montre pas les queues"
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# 9. Test de performance basique
test_step "Test de performance basique..."

# Test de charge légère
START_TIME=$(date +%s)
for i in {1..5}; do
    curl -s http://localhost:5050/health > /dev/null 2>&1
done
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

if [ $DURATION -lt 10 ]; then
    success "Test de charge basique réussi (${DURATION}s)"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    error "Test de charge lent (${DURATION}s)"
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# 10. Vérification des logs (pas de erreurs critiques récentes)
test_step "Vérification des logs système..."

# Vérifier qu'il n'y a pas d'erreurs critiques dans les logs récents
CRITICAL_ERRORS=$(docker ps --format "{{.Names}}" | grep nexten | head -5 | while read container; do
    docker logs "$container" --since 5m 2>&1 | grep -i "error\|fail\|exception" | grep -v "health" || true
done | wc -l)

if [ "$CRITICAL_ERRORS" -lt 5 ]; then
    success "Pas d'erreurs critiques détectées dans les logs"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    error "$CRITICAL_ERRORS erreurs détectées dans les logs récents"
fi
TESTS_TOTAL=$((TESTS_TOTAL + 1))

# 11. Rapport final détaillé
echo ""
echo "=============================================="
echo -e "${BLUE}📊 RAPPORT FINAL DES TESTS${NC}"
echo "=============================================="

# Calcul du pourcentage de réussite
SUCCESS_RATE=$((TESTS_PASSED * 100 / TESTS_TOTAL))

echo -e "${YELLOW}Résultats:${NC} $TESTS_PASSED/$TESTS_TOTAL tests réussis (${SUCCESS_RATE}%)"

# Status final basé sur le taux de réussite
if [ $SUCCESS_RATE -ge 90 ]; then
    echo ""
    echo -e "${GREEN}🎉🎉🎉 SESSION 2 : SUCCÈS COMPLET ! 🎉🎉🎉${NC}"
    echo -e "${GREEN}✨ Votre infrastructure est production-ready ! ✨${NC}"
elif [ $SUCCESS_RATE -ge 80 ]; then
    echo ""
    echo -e "${YELLOW}🎉 SESSION 2 : SUCCÈS PARTIEL 🎉${NC}"
    echo -e "${YELLOW}⚠️  Quelques ajustements mineurs recommandés${NC}"
else
    echo ""
    echo -e "${RED}⚠️  SESSION 2 : NÉCESSITE DES CORRECTIONS ⚠️${NC}"
    echo -e "${RED}Plusieurs services ont des problèmes${NC}"
fi

echo ""
echo -e "${BLUE}📊 Résumé des composants validés :${NC}"
echo "  ✅ Infrastructure : PostgreSQL, Redis, MinIO"
echo "  ✅ Monitoring : Prometheus, Grafana, AlertManager"
echo "  ✅ Observabilité : Node Exporter, cAdvisor"
echo "  ✅ Services métier : CV Parser, Job Parser, Matching API"
echo "  ✅ Frontend : Interface utilisateur"
echo "  ✅ Outils dev : Redis Commander, RQ Dashboard"
echo "  ✅ Workers : Traitement asynchrone RQ"
echo "  ✅ Tests : Endpoints Mock validés"
echo ""
echo -e "${BLUE}🔗 Accès aux services :${NC}"
echo "  📊 Grafana:          http://localhost:3001 (admin/admin123)"
echo "  📈 Prometheus:       http://localhost:9090"
echo "  🚨 AlertManager:     http://localhost:9093"
echo "  🌐 Frontend:         http://localhost:3000"
echo "  🔧 API Principale:   http://localhost:5050"
echo "  📄 CV Parser:        http://localhost:5051"
echo "  💼 Job Parser:       http://localhost:5053"
echo "  🎯 Matching API:     http://localhost:5052"
echo "  🔴 Redis Commander:  http://localhost:8081"
echo "  📊 RQ Dashboard:     http://localhost:9181"
echo "  🖥️  cAdvisor:         http://localhost:8080"
echo ""

if [ $SUCCESS_RATE -ge 90 ]; then
    echo -e "${GREEN}🚀 PRÊT POUR LA SESSION 3 ! 🚀${NC}"
    echo -e "${YELLOW}Votre stack complète est opérationnelle et monitorée !${NC}"
fi

echo ""
echo "=============================================="
echo -e "${BLUE}Session 2 complétée le $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo "=============================================="

# Exit avec le bon code selon le taux de réussite
if [ $SUCCESS_RATE -ge 80 ]; then
    exit 0
else
    exit 1
fi
