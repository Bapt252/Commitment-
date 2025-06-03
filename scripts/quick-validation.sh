#!/bin/bash
# Validation rapide SuperSmartMatch V2

set -e

echo "🚀 SuperSmartMatch V2 - Validation Express"
echo "========================================="

V1_URL=${V1_URL:-"http://localhost:5062"}
NEXTEN_URL=${NEXTEN_URL:-"http://localhost:5052"}
V2_URL=${V2_URL:-"http://localhost:5070"}

test_service() {
    local name=$1
    local url=$2
    
    echo -n "Testing $name... "
    
    for endpoint in "/health" "/api/health" "/" "/status"; do
        if curl -s -f "${url}${endpoint}" > /dev/null 2>&1; then
            echo "✅ OK"
            return 0
        fi
    done
    
    echo "❌ FAILED"
    return 1
}

echo "🔍 Test de connectivité"
test_service "V1" "$V1_URL"
test_service "Nexten" "$NEXTEN_URL"
test_service "V2" "$V2_URL" || {
    echo "❌ V2 non accessible - Arrêt"
    exit 1
}

echo ""
echo "🧪 Test fonctionnel V2"
response=$(curl -s -w "%{http_code}" -X POST "${V2_URL}/api/v2/match" \
  -H "Content-Type: application/json" \
  -d '{"user_profile": {"age": 28}, "jobs": [{"title": "Test"}]}' 2>/dev/null)

http_code=$(echo "$response" | tail -c 4)
if [ "$http_code" = "200" ]; then
    echo "✅ Test fonctionnel OK"
else
    echo "❌ Test fonctionnel échoué (HTTP $http_code)"
    exit 1
fi

echo ""
echo "🔄 Test compatibilité V1"
response=$(curl -s -w "%{http_code}" -X POST "${V2_URL}/api/v1/match" \
  -H "Content-Type: application/json" \
  -d '{"user_profile": {"age": 25}, "jobs": [{"title": "Dev"}]}' 2>/dev/null)

http_code=$(echo "$response" | tail -c 4)
if [ "$http_code" = "200" ]; then
    echo "✅ Compatibilité V1 OK"
else
    echo "❌ Compatibilité V1 échouée (HTTP $http_code)"
fi

echo ""
echo "✅ Validation terminée!"
