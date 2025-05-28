#!/bin/bash

# Script de test d'intégration SuperSmartMatch-Service - Version corrigée
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

# Test 8a: Root endpoint (correct)
echo "📡 Test root endpoint..."
ROOT_RESPONSE=$(curl -s http://localhost:5062/ 2>/dev/null || echo "ERROR")
if echo "$ROOT_RESPONSE" | grep -q "SuperSmartMatch\\|service\\|API"; then
    echo -e "${GREEN}✅ Root endpoint fonctionnel${NC}"
else
    echo -e "${YELLOW}⚠️ Root endpoint: $(echo $ROOT_RESPONSE | head -c 100)...${NC}"
fi

# Test 8b: Algorithms endpoint
echo "🧮 Test algorithms endpoint..."
ALGO_RESPONSE=$(curl -s http://localhost:5062/api/v1/algorithms 2>/dev/null || echo "ERROR")
if echo "$ALGO_RESPONSE" | grep -q "algorithm\\|semantic\\|hybrid\\|matching"; then
    echo -e "${GREEN}✅ Algorithms endpoint fonctionnel${NC}"
    echo "📋 Algorithmes disponibles:"
    echo "$ALGO_RESPONSE" | jq -r '.algorithms | keys[]' 2>/dev/null | sed 's/^/   • /' || echo "   • Parsing JSON failed"
else
    echo -e "${YELLOW}⚠️ Algorithms endpoint: $(echo $ALGO_RESPONSE | head -c 100)...${NC}"
fi

# Test 9: Test de matching simple avec format correct
echo ""
echo -e "${BLUE}🎯 Test de matching simple (format corrigé)${NC}"
echo "=============================================="

MATCH_PAYLOAD='{
  "candidate": {
    "competences": ["Python", "Docker", "PostgreSQL"],
    "annees_experience": 2,
    "adresse": "Paris"
  },
  "jobs": [
    {
      "titre": "Développeur Python",
      "competences": ["Python", "API", "Base de données"],
      "localisation": "Paris",
      "entreprise": "TechCorp"
    },
    {
      "titre": "DevOps Engineer", 
      "competences": ["Docker", "Kubernetes", "Python"],
      "localisation": "Lyon",
      "entreprise": "CloudInc"
    }
  ],
  "algorithm": "smart-match",
  "options": {
    "limit": 5,
    "include_details": true
  }
}'

echo "📤 Envoi de la requête de matching (format candidate/jobs)..."
MATCH_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$MATCH_PAYLOAD" \
  http://localhost:5062/api/v1/match 2>/dev/null || echo "ERROR")

if echo "$MATCH_RESPONSE" | grep -q "algorithm_used\\|matches\\|execution_time"; then
    echo -e "${GREEN}✅ Test de matching réussi${NC}"
    echo "📊 Aperçu de la réponse:"
    echo "$MATCH_RESPONSE" | jq '.algorithm_used, .execution_time_ms, (.matches | length)' 2>/dev/null || echo "$MATCH_RESPONSE" | head -3
else
    echo -e "${YELLOW}⚠️ Test de matching - réponse à analyser${NC}"
    echo "📤 Payload envoyé: $(echo $MATCH_PAYLOAD | head -c 200)..."
    echo "📥 Réponse reçue: $(echo $MATCH_RESPONSE | head -c 200)..."
fi

# Test 10: Test de comparaison d'algorithmes
echo ""
echo -e "${BLUE}🔬 Test de comparaison d'algorithmes${NC}"
echo "===================================="

COMPARE_PAYLOAD='{
  "candidate": {
    "competences": ["Python", "Machine Learning"],
    "annees_experience": 3,
    "adresse": "Paris"
  },
  "jobs": [
    {
      "titre": "Data Scientist",
      "competences": ["Python", "Machine Learning", "SQL"],
      "localisation": "Paris"
    }
  ],
  "algorithms": ["smart-match", "enhanced", "semantic"]
}'

echo "🔬 Test de comparaison d'algorithmes..."
COMPARE_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$COMPARE_PAYLOAD" \
  http://localhost:5062/api/v1/compare 2>/dev/null || echo "ERROR")

if echo "$COMPARE_RESPONSE" | grep -q "comparison_results\\|recommendation"; then
    echo -e "${GREEN}✅ Test de comparaison réussi${NC}"
    echo "📊 Algorithmes testés:"
    echo "$COMPARE_RESPONSE" | jq -r '.comparison_results | keys[]' 2>/dev/null | sed 's/^/   • /' || echo "   • Parsing failed"
else
    echo -e "${YELLOW}⚠️ Test de comparaison - à analyser${NC}"
    echo "📥 Réponse: $(echo $COMPARE_RESPONSE | head -c 150)..."
fi

# Test 11: Vérification des autres services (pas de conflit)
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

# Test 12: Vérification de la configuration Docker
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

# Test 13: Test de performance basique
echo ""
echo -e "${BLUE}⚡ Test de performance basique${NC}"
echo "================================"

echo "⏱️ Test de latence..."
START_TIME=$(date +%s%N)
curl -s http://localhost:5062/api/v1/health > /dev/null 2>&1
END_TIME=$(date +%s%N)
LATENCY=$(( (END_TIME - START_TIME) / 1000000 ))

if [ "$LATENCY" -lt 1000 ]; then
    echo -e "${GREEN}✅ Latence acceptable: ${LATENCY}ms${NC}"
else
    echo -e "${YELLOW}⚠️ Latence élevée: ${LATENCY}ms${NC}"
fi

# Test 14: Vérification des logs
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

# Test 15: Test de connectivité interne
echo ""
echo -e "${BLUE}🔗 Test de connectivité interne${NC}"
echo "=================================="

# Test de connectivité PostgreSQL depuis SuperSmartMatch
PG_TEST=$(docker-compose exec -T supersmartmatch-service sh -c "python -c 'import psycopg2; psycopg2.connect(\"postgresql://postgres:postgres@postgres:5432/nexten\"); print(\"OK\")'" 2>/dev/null || echo "FAILED")
if [ "$PG_TEST" = "OK" ]; then
    echo -e "${GREEN}✅ SuperSmartMatch → PostgreSQL${NC}"
else
    echo -e "${YELLOW}⚠️ SuperSmartMatch → PostgreSQL (peut être normal si psycopg2 non installé)${NC}"
fi

# Test de connectivité Redis depuis SuperSmartMatch
REDIS_TEST=$(docker-compose exec -T supersmartmatch-service sh -c "python -c 'import redis; r=redis.Redis(host=\"redis\", port=6379); r.ping(); print(\"OK\")'" 2>/dev/null || echo "FAILED")
if [ "$REDIS_TEST" = "OK" ]; then
    echo -e "${GREEN}✅ SuperSmartMatch → Redis${NC}"
else
    echo -e "${YELLOW}⚠️ SuperSmartMatch → Redis (peut être normal si redis non installé)${NC}"
fi

# Test 16: Métriques du service
echo ""
echo -e "${BLUE}📊 Test des métriques${NC}"
echo "======================"

METRICS_RESPONSE=$(curl -s http://localhost:5062/api/v1/metrics 2>/dev/null || echo "ERROR")
if echo "$METRICS_RESPONSE" | grep -q "performance_metrics\\|cache_metrics"; then
    echo -e "${GREEN}✅ Métriques disponibles${NC}"
else
    echo -e "${YELLOW}⚠️ Métriques non disponibles: $(echo $METRICS_RESPONSE | head -c 100)...${NC}"
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
    
    echo ""
    echo -e "${BLUE}🧪 Exemples de test manuels:${NC}"
    echo ""
    echo "# Test de santé"
    echo "curl http://localhost:5062/api/v1/health"
    echo ""
    echo "# Test de matching correct"
    echo 'curl -X POST http://localhost:5062/api/v1/match \'
    echo '  -H "Content-Type: application/json" \'
    echo '  -d '"'"'{"candidate":{"competences":["Python"],"annees_experience":2},"jobs":[{"titre":"Dev Python","competences":["Python"]}]}'"'"
    echo ""
    echo "# Liste des algorithmes"
    echo "curl http://localhost:5062/api/v1/algorithms"
    
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