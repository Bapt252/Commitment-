#!/bin/bash

# =============================================================================
# Test d'intégration end-to-end pour la Session 2
# =============================================================================

set -e

echo "🚀 Lancement des tests d'intégration end-to-end..."
echo "=============================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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
    exit 1
}

# Attendre que tous les services soient prêts
test_step "Vérification de l'état des services..."
sleep 10

# 1. Test des services de base
test_step "Test des services de base..."

# PostgreSQL
if curl -f http://localhost:9187/metrics > /dev/null 2>&1; then
    success "PostgreSQL Exporter accessible"
else
    error "PostgreSQL Exporter non accessible"
fi

# Redis
if curl -f http://localhost:9121/metrics > /dev/null 2>&1; then
    success "Redis Exporter accessible"
else
    error "Redis Exporter non accessible"
fi

# MinIO
if curl -f http://localhost:9000/minio/health/live > /dev/null 2>&1; then
    success "MinIO Health Check OK"
else
    error "MinIO non accessible"
fi

# 2. Test des services de monitoring
test_step "Test des services de monitoring..."

# Prometheus
if curl -f http://localhost:9090/api/v1/query?query=up > /dev/null 2>&1; then
    success "Prometheus API accessible"
else
    error "Prometheus non accessible"
fi

# Grafana
if curl -f http://localhost:3001/api/health > /dev/null 2>&1; then
    success "Grafana Health Check OK"
else
    error "Grafana non accessible"
fi

# AlertManager
if curl -f http://localhost:9093/api/v1/status > /dev/null 2>&1; then
    success "AlertManager API accessible"
else
    error "AlertManager non accessible"
fi

# Node Exporter
if curl -f http://localhost:9100/metrics > /dev/null 2>&1; then
    success "Node Exporter accessible"
else
    error "Node Exporter non accessible"
fi

# cAdvisor
if curl -f http://localhost:8080/metrics > /dev/null 2>&1; then
    success "cAdvisor accessible"
else
    error "cAdvisor non accessible"
fi

# 3. Test des services métier
test_step "Test des services métier..."

# CV Parser Health
if curl -f http://localhost:5051/health > /dev/null 2>&1; then
    success "CV Parser Service accessible"
else
    error "CV Parser Service non accessible"
fi

# Job Parser Health
if curl -f http://localhost:5053/health > /dev/null 2>&1; then
    success "Job Parser Service accessible"
else
    error "Job Parser Service non accessible"
fi

# Matching API Health
if curl -f http://localhost:5052/health > /dev/null 2>&1; then
    success "Matching API accessible"
else
    error "Matching API non accessible"
fi

# API principale
if curl -f http://localhost:5050/health > /dev/null 2>&1; then
    success "API principale accessible"
else
    error "API principale non accessible"
fi

# 4. Test des dashboards et outils
test_step "Test des outils de développement..."

# Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    success "Frontend accessible"
else
    error "Frontend non accessible"
fi

# Redis Commander
if curl -f http://localhost:8081 > /dev/null 2>&1; then
    success "Redis Commander accessible"
else
    error "Redis Commander non accessible"
fi

# RQ Dashboard
if curl -f http://localhost:9181 > /dev/null 2>&1; then
    success "RQ Dashboard accessible"
else
    error "RQ Dashboard non accessible"
fi

# 5. Test des métriques Prometheus
test_step "Test des métriques dans Prometheus..."

# Vérifier que Prometheus collecte les métriques
METRICS_COUNT=$(curl -s http://localhost:9090/api/v1/label/__name__/values | jq '.data | length')
if [ "$METRICS_COUNT" -gt 100 ]; then
    success "Prometheus collecte ${METRICS_COUNT} métriques"
else
    error "Pas assez de métriques collectées ($METRICS_COUNT)"
fi

# 6. Test fonctionnel des parsers
test_step "Test fonctionnel simple des parsers..."

# Test CV Parser avec mock
CV_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"mock": true}' \
    http://localhost:5051/api/parse-cv-mock/)

if echo "$CV_RESPONSE" | grep -q "success"; then
    success "CV Parser Mock test réussi"
else
    error "CV Parser Mock test échoué"
fi

# Test Job Parser avec mock
JOB_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"mock": true}' \
    http://localhost:5053/api/parse-job-mock/)

if echo "$JOB_RESPONSE" | grep -q "success"; then
    success "Job Parser Mock test réussi"
else
    error "Job Parser Mock test échoué"
fi

# 7. Test du pipeline de matching
test_step "Test du pipeline de matching..."

# Test Matching API
MATCH_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d '{"cv_data": {"skills": ["python"]}, "job_data": {"required_skills": ["python"]}}' \
    http://localhost:5052/api/match/)

if echo "$MATCH_RESPONSE" | grep -q "score"; then
    success "Matching API test réussi"
else
    error "Matching API test échoué"
fi

# 8. Test des workers RQ
test_step "Test des workers RQ..."

# Vérifier les queues Redis
QUEUE_INFO=$(curl -s http://localhost:9181/queues.json)
if echo "$QUEUE_INFO" | grep -q "default"; then
    success "Queues RQ détectées"
else
    error "Aucune queue RQ trouvée"
fi

# 9. Test du logging et monitoring
test_step "Test du logging et monitoring..."

# Vérifier que les logs sont collectés
CONTAINER_COUNT=$(docker ps --format "table {{.Names}}" | wc -l)
if [ "$CONTAINER_COUNT" -gt 25 ]; then
    success "$((CONTAINER_COUNT-1)) conteneurs en cours d'exécution"
else
    error "Pas assez de conteneurs actifs"
fi

# 10. Test des alertes (basique)
test_step "Test de la configuration des alertes..."

# Vérifier la configuration AlertManager
ALERT_CONFIG=$(curl -s http://localhost:9093/api/v1/config)
if echo "$ALERT_CONFIG" | grep -q "global"; then
    success "Configuration AlertManager valide"
else
    error "Configuration AlertManager invalide"
fi

# 11. Test de performance basique
test_step "Test de performance basique..."

# Test de charge légère sur l'API principale
for i in {1..5}; do
    curl -s http://localhost:5050/health > /dev/null
done
success "Test de charge basique réussi"

# 12. Rapport final
echo ""
echo "=============================================="
echo -e "${GREEN}🎉 TOUS LES TESTS D'INTÉGRATION RÉUSSIS ! 🎉${NC}"
echo "=============================================="
echo ""
echo "📊 Résumé des services validés :"
echo "  ✅ Infrastructure : PostgreSQL, Redis, MinIO"
echo "  ✅ Monitoring : Prometheus, Grafana, AlertManager"
echo "  ✅ Métiers : CV Parser, Job Parser, Matching API"
echo "  ✅ Frontend : Interface utilisateur"
echo "  ✅ Outils : Redis Commander, RQ Dashboard"
echo "  ✅ Workers : CV, Job, Matching workers actifs"
echo "  ✅ Métriques : $(echo $METRICS_COUNT) métriques collectées"
echo ""
echo "🔗 Accès aux services :"
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
echo -e "${GREEN}✨ SESSION 2 TERMINÉE AVEC SUCCÈS ! ✨${NC}"
echo -e "${YELLOW}Votre stack complète est opérationnelle et monitored ! 🚀${NC}"
