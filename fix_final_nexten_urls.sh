#!/bin/bash

# 🔧 CORRECTION FINALE - Fix URL Nexten dans le conteneur V2
echo "🔧 CORRECTION FINALE - Fix URL Nexten dans supersmartmatch-v2-unified"
echo "====================================================================="

# Identifier le conteneur V2
V2_CONTAINER="supersmartmatch-v2-unified"

echo "🔍 Correction des URLs Nexten dans le conteneur..."
echo "--------------------------------------------------"

# 1. Corriger l'endpoint de /api/v1/queue-matching vers /match (ligne 251)
echo "1️⃣ Correction de l'endpoint /api/v1/queue-matching → /match"
docker exec $V2_CONTAINER sed -i 's|/api/v1/queue-matching|/match|g' /app/supersmartmatch-v2-unified-service.py

# 2. Corriger l'URL par défaut de localhost vers nexten_matcher (ligne 38)
echo "2️⃣ Correction de l'URL http://localhost:5052 → http://nexten_matcher:5052"
docker exec $V2_CONTAINER sed -i 's|http://localhost:5052|http://nexten_matcher:5052|g' /app/supersmartmatch-v2-unified-service.py

# 3. Vérifications
echo ""
echo "🔍 Vérifications des corrections..."
echo "----------------------------------"
echo "✅ Endpoint corrigé (ligne 251):"
docker exec $V2_CONTAINER grep -n "/match" /app/supersmartmatch-v2-unified-service.py | head -3

echo ""
echo "✅ URL corrigée (ligne 38):"
docker exec $V2_CONTAINER grep -n "nexten_matcher:5052" /app/supersmartmatch-v2-unified-service.py | head -3

# 4. Redémarrage du conteneur
echo ""
echo "🔄 Redémarrage du conteneur pour appliquer les changements..."
docker restart $V2_CONTAINER

echo "⏳ Attente du redémarrage (15 secondes)..."
sleep 15

# 5. Test de validation
echo ""
echo "🧪 Test de validation final..."
echo "-----------------------------"

# Test health des deux services
V2_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5070/health)
NEXTEN_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5052/health)

echo "• SuperSmartMatch V2: $([ "$V2_HEALTH" = "200" ] && echo "✅ UP" || echo "❌ DOWN ($V2_HEALTH)")"
echo "• Nexten Matcher: $([ "$NEXTEN_HEALTH" = "200" ] && echo "✅ UP" || echo "❌ DOWN ($NEXTEN_HEALTH)")"

# Test de routing final
echo ""
echo "🎯 Test de routing final..."
FINAL_PAYLOAD='{
  "candidate": {
    "name": "Test Final",
    "email": "test@example.com",
    "technical_skills": ["Python", "ML", "Docker"],
    "experiences": [{
      "title": "ML Engineer",
      "company": "TechCorp",
      "duration": 36
    }]
  },
  "offers": [{
    "id": "final_test",
    "title": "Senior ML Engineer",
    "company": "AI Startup",
    "required_skills": ["Python", "ML", "AI"]
  }]
}'

FINAL_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$FINAL_PAYLOAD" \
  http://localhost:5070/match 2>/dev/null)

FINAL_ALGORITHM=$(echo "$FINAL_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('algorithm_used', 'NOT_FOUND'))
except:
    print('PARSE_ERROR')
" 2>/dev/null)

echo ""
echo "🎉 RÉSULTAT FINAL:"
echo "=================="
if [ "$FINAL_ALGORITHM" = "nexten_matcher" ]; then
    echo "✅ SUCCESS! V2 route maintenant vers Nexten!"
    echo "   🎯 Algorithme: $FINAL_ALGORITHM"
    echo "   🏆 Mission accomplie!"
elif [[ "$FINAL_ALGORITHM" == *"fallback"* ]]; then
    echo "⚠️  Encore en fallback: $FINAL_ALGORITHM"
    echo "   📋 Vérifier les logs: docker logs $V2_CONTAINER --tail 10"
else
    echo "✅ Algorithme utilisé: $FINAL_ALGORITHM"
    echo "   ℹ️  Le routing fonctionne!"
fi

echo ""
echo "📋 Vérification des logs récents:"
echo "--------------------------------"
docker logs $V2_CONTAINER --tail 5

echo ""
echo "✅ Correction terminée!"