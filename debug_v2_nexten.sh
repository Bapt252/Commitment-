#!/bin/bash

echo "🔍 DEBUG - Communication V2 ↔ Nexten"
echo "===================================="

# 1. Vérifier la configuration dans le conteneur V2
echo ""
echo "1️⃣ Configuration dans le conteneur V2..."
echo "----------------------------------------"
V2_CONTAINER=$(docker ps -q --filter name=.*v2.*smart.*)
if [ ! -z "$V2_CONTAINER" ]; then
    echo "🔍 Configuration NEXTEN_ENDPOINT dans le conteneur:"
    docker exec $V2_CONTAINER grep -n "NEXTEN_ENDPOINT" /app/app/config.py 2>/dev/null || \
    docker exec $V2_CONTAINER find /app -name "*.py" -exec grep -l "NEXTEN_ENDPOINT" {} \; 2>/dev/null
    
    echo ""
    echo "🔍 Variables d'environnement Nexten:"
    docker exec $V2_CONTAINER env | grep -i nexten 2>/dev/null || echo "   Aucune variable Nexten trouvée"
else
    echo "❌ Conteneur V2 non trouvé"
fi

# 2. Test communication directe depuis V2 vers Nexten
echo ""
echo "2️⃣ Test communication V2 → Nexten..."
echo "-----------------------------------"
if [ ! -z "$V2_CONTAINER" ]; then
    echo "🔍 Ping Nexten depuis V2:"
    docker exec $V2_CONTAINER ping -c 2 nexten_matcher 2>/dev/null || \
    docker exec $V2_CONTAINER ping -c 2 localhost 2>/dev/null || echo "   Ping failed"
    
    echo ""
    echo "🔍 Test HTTP depuis V2 vers Nexten (localhost:5052):"
    docker exec $V2_CONTAINER curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:5052/health 2>/dev/null || echo "   Connexion failed"
    
    echo ""
    echo "🔍 Test HTTP depuis V2 vers Nexten (nexten_matcher:5052):"
    docker exec $V2_CONTAINER curl -s -o /dev/null -w "Status: %{http_code}\n" http://nexten_matcher:5052/health 2>/dev/null || echo "   Connexion failed"
fi

# 3. Vérifier les réseaux Docker
echo ""
echo "3️⃣ Réseaux Docker..."
echo "-------------------"
echo "🔍 Réseaux des conteneurs:"
docker inspect $V2_CONTAINER | grep -A 10 "Networks" 2>/dev/null || echo "   Erreur inspection"

NEXTEN_CONTAINER=$(docker ps -q --filter name=nexten_matcher)
if [ ! -z "$NEXTEN_CONTAINER" ]; then
    echo ""
    echo "🔍 Réseau du conteneur Nexten:"
    docker inspect $NEXTEN_CONTAINER | grep -A 5 "NetworkMode\|Networks" 2>/dev/null
fi

# 4. Test direct de l'endpoint Nexten
echo ""
echo "4️⃣ Test direct endpoint Nexten..."
echo "--------------------------------"
echo "🔍 Test /health sur Nexten:"
curl -s http://localhost:5052/health | head -200

echo ""
echo "🔍 Test /match sur Nexten avec payload minimal:"
NEXTEN_TEST_PAYLOAD='{
  "candidate": {
    "name": "Test User",
    "skills": [{"name": "Python", "level": "Intermediate"}]
  },
  "jobs": [{
    "id": "test_job",
    "title": "Developer",
    "required_skills": ["Python"]
  }]
}'

NEXTEN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$NEXTEN_TEST_PAYLOAD" \
  http://localhost:5052/match 2>/dev/null)

if [ ! -z "$NEXTEN_RESPONSE" ]; then
    echo "✅ Nexten répond à /match"
    echo "$NEXTEN_RESPONSE" | head -200
else
    echo "❌ Nexten ne répond pas à /match"
fi

# 5. Logs récents de V2
echo ""
echo "5️⃣ Logs récents de V2..."
echo "-----------------------"
echo "🔍 Dernières lignes des logs V2:"
docker logs --tail 20 $V2_CONTAINER 2>/dev/null | tail -10

echo ""
echo "🔧 RECOMMANDATIONS BASÉES SUR LE DIAGNOSTIC:"
echo "==========================================="
echo "• Si la config n'est pas dans le conteneur → Rebuild l'image"
echo "• Si la communication échoue → Vérifier les réseaux Docker"
echo "• Si Nexten ne répond pas à /match → Problème côté Nexten"
echo "• Si tout semble OK → Augmenter les logs V2 en mode DEBUG"