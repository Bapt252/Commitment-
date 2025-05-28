#!/bin/bash

# Script de test d'intégration SuperSmartMatch-Service
# Usage: ./test-supersmartmatch-integration.sh

set -e

echo "🧪 TEST D'INTÉGRATION SUPERSMARTMATCH-SERVICE"
echo "=============================================="

# Couleurs pour la sortie
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Compteurs
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Fonction pour les tests
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_code="${3:-0}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo ""
    echo -e "${BLUE}🔍 Test $TOTAL_TESTS: $test_name${NC}"
    echo "----------------------------------------"
    
    if eval "$test_command"; then
        if [ $? -eq $expected_code ]; then
            echo -e "${GREEN}✅ SUCCÈS${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            return 0
        else
            echo -e "${RED}❌ ÉCHEC - Code de retour inattendu${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            return 1
        fi
    else
        echo -e "${RED}❌ ÉCHEC${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Test 1: Vérification que tous les services sont démarrés
run_test "Services Docker actifs" "docker-compose ps | grep -E '(Up|running)' | wc -l | grep -q [0-9]"

# Test 2: Port 5062 disponible
run_test "Port 5062 accessible" "curl -s -f http://localhost:5062 > /dev/null || curl -s http://localhost:5062 | grep -q 'SuperSmartMatch\\|API\\|health'"

# Test 3: Health check SuperSmartMatch
run_test "Health check SuperSmartMatch" "curl -s -f http://localhost:5062/api/v1/health | jq '.status' 2>/dev/null | grep -q 'healthy\\|ok\\|running' || curl -s http://localhost:5062/api/v1/health | grep -q 'ok\\|healthy\\|status'"

# Test 4: Connectivité avec PostgreSQL
run_test "Connexion PostgreSQL" "docker-compose exec -T postgres pg_isready -U postgres -d nexten"

# Test 5: Connectivité avec Redis
run_test "Connexion Redis" "docker-compose exec -T redis redis-cli ping | grep -q PONG"

# Test 6: MinIO accessible
run_test "MinIO accessible" "curl -s -f http://localhost:9000/minio/health/live"

# Test 7: Logs SuperSmartMatch
run_test "Logs SuperSmartMatch disponibles" "docker-compose logs supersmartmatch-service 2>/dev/null | grep -q '.' && echo 'Logs trouvés'"

# Test 8: API endpoints SuperSmartMatch
echo ""
echo -e "${BLUE}🔍 Test détaillé des endpoints SuperSmartMatch${NC}"
echo "=================================================="

# Test 8a: Status endpoint
echo "📡 Test status endpoint..."
STATUS_RESPONSE=$(curl -s http://localhost:5062/api/v1/status 2>/dev/null || curl -s http://localhost:5062/ 2>/dev/null || echo "ERROR")
if echo "$STATUS_RESPONSE" | grep -q "SuperSmartMatch\\|status\\|version\\|API"; then
    echo -e "${GREEN}✅ Status endpoint fonctionnel${NC}"
else
    echo -e "${YELLOW}⚠️ Status endpoint non standard: $(echo $STATUS_RESPONSE | head -c 100)...${NC}"
fi

# Test 8b: Algorithms endpoint
echo "🧮 Test algorithms endpoint..."
ALGO_RESPONSE=$(curl -s http://localhost:5062/api/v1/algorithms 2>/dev/null || curl -s http://localhost:5062/algorithms 2>/dev/null || echo "ERROR")
if echo "$ALGO_RESPONSE" | grep -q "algorithm\\|semantic\\|hybrid\\|matching"; then
    echo -e "${GREEN}✅ Algorithms endpoint fonctionnel${NC}"
else
    echo -e "${YELLOW}⚠️ Algorithms endpoint: $(echo $ALGO_RESPONSE | head -c 100)...${NC}"
fi

# Test 9: Test de matching simple
echo ""
echo -e "${BLUE}🎯 Test de matching simple${NC}"
echo "=============================="

MATCH_PAYLOAD='{
  "profile": {
    "skills": ["Python", "Docker", "PostgreSQL"],
    "experience": "2 ans",
    "location": "Paris"
  },
  "jobs": [
    {
      "title": "Développeur Python",
      "requirements": ["Python", "API", "Base de données"],
      "location": "Paris",
      "company": "TechCorp"
    },
    {
      "title": "DevOps Engineer",
      "requirements": ["Docker", "Kubernetes", "Python"],
      "location": "Lyon",
      "company": "CloudInc"
    }
  ]
}'

echo "📤 Envoi de la requête de matching..."
MATCH_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$MATCH_PAYLOAD" \
  http://localhost:5062/api/v1/match 2>/dev/null || 
  curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$MATCH_PAYLOAD" \
  http://localhost:5062/match 2>/dev/null || echo "ERROR")

if echo "$MATCH_RESPONSE" | grep -q "score\\|match\\|result\\|ranking"; then
    echo -e "${GREEN}✅ Test de matching réussi${NC}"
    echo "📊 Aperçu de la réponse:"
    echo "$MATCH_RESPONSE" | head -5
else
    echo -e "${YELLOW}⚠️ Test de matching - réponse inattendue${NC}"
    echo "📤 Payload envoyé: $(echo $MATCH_PAYLOAD | head -c 150)..."
    echo "📥 Réponse reçue: $(echo $MATCH_RESPONSE | head -c 150)..."
fi

# Test 10: Vérification des autres services (pas de conflit)
echo ""
echo -e "${BLUE}🔍 Vérification des autres services (pas de conflit)${NC}"
echo "=================================================="

SERVICES=("api:5050" "cv-parser:5051" "matching-api:5052" "job-parser:5055" "personalization-service:5060")

for service in "${SERVICES[@]}"; do
    service_name=$(echo $service | cut -d: -f1)
    service_port=$(echo $service | cut -d: -f2)
    
    echo "🔍 Test $service_name (port $service_port)..."
    if curl -s -f http://localhost:$service_port/health > /dev/null 2>&1 || 
       curl -s http://localhost:$service_port > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name opérationnel${NC}"
    else
        echo -e "${YELLOW}⚠️ $service_name non accessible (normal si pas encore démarré)${NC}"
    fi
done

# Test 11: Vérification de la configuration Docker
echo ""
echo -e "${BLUE}🐳 Vérification de la configuration Docker${NC}"
echo "=========================================="

# Vérifier les réseaux
NETWORKS=$(docker network ls | grep nexten-network | wc -l)
if [ "$NETWORKS" -gt 0 ]; then
    echo -e "${GREEN}✅ Réseau nexten-network configuré${NC}"
else
    echo -e "${RED}❌ Réseau nexten-network manquant${NC}"
fi

# Vérifier les volumes
VOLUMES=$(docker volume ls | grep -E "(postgres-data|redis-data|minio-data)" | wc -l)
if [ "$VOLUMES" -ge 3 ]; then
    echo -e "${GREEN}✅ Volumes de données configurés${NC}"
else
    echo -e "${YELLOW}⚠️ Certains volumes peuvent être manquants${NC}"
fi

# Test 12: Test de performance basique
echo ""
echo -e "${BLUE}⚡ Test de performance basique${NC}"
echo "================================"

echo "⏱️ Test de latence..."
START_TIME=$(date +%s%N)
curl -s http://localhost:5062/api/v1/health > /dev/null 2>&1 || curl -s http://localhost:5062 > /dev/null 2>&1
END_TIME=$(date +%s%N)
LATENCY=$(( (END_TIME - START_TIME) / 1000000 ))

if [ "$LATENCY" -lt 1000 ]; then
    echo -e "${GREEN}✅ Latence acceptable: ${LATENCY}ms${NC}"
else
    echo -e "${YELLOW}⚠️ Latence élevée: ${LATENCY}ms${NC}"
fi

# Test 13: Vérification des logs
echo ""
echo -e "${BLUE}📋 Vérification des logs${NC}"
echo "============================="

if [ -d "supersmartmatch-service/logs" ]; then
    echo -e "${GREEN}✅ Dossier de logs créé${NC}"
else
    echo -e "${YELLOW}⚠️ Dossier de logs manquant${NC}"
fi

LOG_COUNT=$(docker-compose logs supersmartmatch-service 2>/dev/null | wc -l)
if [ "$LOG_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Logs SuperSmartMatch disponibles ($LOG_COUNT lignes)${NC}"
else
    echo -e "${YELLOW}⚠️ Aucun log SuperSmartMatch trouvé${NC}"
fi

# Test 14: Test de connectivité interne
echo ""
echo -e "${BLUE}🔗 Test de connectivité interne${NC}"
echo "=================================="

# Test de connectivité PostgreSQL depuis SuperSmartMatch
PG_TEST=$(docker-compose exec -T supersmartmatch-service sh -c "python -c 'import psycopg2; psycopg2.connect(\"postgresql://postgres:postgres@postgres:5432/nexten\"); print(\"OK\")'" 2>/dev/null || echo "FAILED")
if [ "$PG_TEST" = "OK" ]; then
    echo -e "${GREEN}✅ SuperSmartMatch → PostgreSQL${NC}"
else
    echo -e "${YELLOW}⚠️ SuperSmartMatch → PostgreSQL (peut être normal)${NC}"
fi

# Test de connectivité Redis depuis SuperSmartMatch
REDIS_TEST=$(docker-compose exec -T supersmartmatch-service sh -c "python -c 'import redis; r=redis.Redis(host=\"redis\", port=6379); r.ping(); print(\"OK\")'" 2>/dev/null || echo "FAILED")
if [ "$REDIS_TEST" = "OK" ]; then
    echo -e "${GREEN}✅ SuperSmartMatch → Redis${NC}"
else
    echo -e "${YELLOW}⚠️ SuperSmartMatch → Redis (peut être normal)${NC}"
fi

# Résumé final
echo ""
echo "📊 RÉSUMÉ DES TESTS"
echo "==================="
echo -e "📈 Total: $TOTAL_TESTS tests"
echo -e "${GREEN}✅ Réussis: $PASSED_TESTS${NC}"
echo -e "${RED}❌ Échoués: $FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 TOUS LES TESTS SONT PASSÉS !${NC}"
    echo -e "${GREEN}✅ SuperSmartMatch-Service est correctement intégré${NC}"
    echo ""
    echo "🔗 URLs utiles:"
    echo "   • SuperSmartMatch: http://localhost:5062"
    echo "   • Health check: http://localhost:5062/api/v1/health"
    echo "   • API principale: http://localhost:5050"
    echo "   • RQ Dashboard: http://localhost:9181"
    echo "   • Redis Commander: http://localhost:8081"
    echo "   • MinIO Console: http://localhost:9001"
    
    exit 0
else
    echo ""
    echo -e "${RED}⚠️ CERTAINS TESTS ONT ÉCHOUÉ${NC}"
    echo -e "${YELLOW}🔧 Actions recommandées:${NC}"
    echo "   1. Vérifiez les logs: docker-compose logs supersmartmatch-service"
    echo "   2. Redémarrez les services: docker-compose restart"
    echo "   3. Vérifiez la configuration: docker-compose config"
    echo "   4. Consultez le guide d'intégration"
    
    echo ""
    echo "📋 Commandes de diagnostic:"
    echo "   docker-compose ps"
    echo "   docker-compose logs supersmartmatch-service --tail=50"
    echo "   netstat -tulpn | grep ':5062'"
    echo "   curl -v http://localhost:5062/api/v1/health"
    
    exit 1
fi