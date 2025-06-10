#!/bin/bash

# 🔧 Script de redémarrage SuperSmartMatch V2 pour macOS
# Applique la correction de configuration et redémarre le service

echo "🎯 SuperSmartMatch V2 - Redémarrage pour appliquer la configuration corrigée"
echo "=================================================="

# Vérifier que Docker est en cours d'exécution
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker n'est pas en cours d'exécution"
    echo "   Veuillez démarrer Docker Desktop"
    exit 1
fi

echo "✅ Docker est accessible"

# Afficher l'état actuel des services
echo ""
echo "📊 État actuel des services :"
echo "------------------------------"
docker-compose ps

echo ""
echo "🔧 Redémarrage de SuperSmartMatch V2..."
echo "----------------------------------------"

# Redémarrer le service V2 pour appliquer la nouvelle configuration
echo "⏳ Arrêt du service SuperSmartMatch V2..."
docker-compose stop supersmartmatch-v2

echo "⏳ Redémarrage du service SuperSmartMatch V2..."
docker-compose up -d supersmartmatch-v2

# Attendre que le service soit prêt
echo "⏳ Attente du démarrage du service (15 secondes)..."
sleep 15

echo ""
echo "🧪 Tests de vérification :"
echo "-------------------------"

# Test 1: Health check de V2
echo "1️⃣ Test Health V2..."
V2_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5070/health)
if [ "$V2_HEALTH" = "200" ]; then
    echo "   ✅ SuperSmartMatch V2 accessible (HTTP $V2_HEALTH)"
else
    echo "   ❌ SuperSmartMatch V2 inaccessible (HTTP $V2_HEALTH)"
fi

# Test 2: Health check de Nexten
echo "2️⃣ Test Health Nexten..."
NEXTEN_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5052/health)
if [ "$NEXTEN_HEALTH" = "200" ]; then
    echo "   ✅ Nexten Matcher accessible (HTTP $NEXTEN_HEALTH)"
else
    echo "   ❌ Nexten Matcher inaccessible (HTTP $NEXTEN_HEALTH)"
fi

# Test 3: Test de routing avec le bon payload
echo "3️⃣ Test de routing V2 → Nexten..."

# Payload de test avec le format correct pour Nexten
TEST_PAYLOAD='{
  "candidate": {
    "name": "Test Candidat",
    "skills": ["Python", "FastAPI", "Docker"],
    "experience": "5 ans",
    "education": "Master Informatique",
    "location": "Paris"
  },
  "job": {
    "title": "Développeur Backend",
    "description": "Poste de développeur Python senior",
    "required_skills": ["Python", "API", "Docker"],
    "experience_required": "3-7 ans",
    "location": "Paris"
  }
}'

# Test du routing
RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$TEST_PAYLOAD" \
  http://localhost:5070/api/v1/queue-matching)

echo "   📝 Réponse complète :"
echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"

# Extraire l'algorithme utilisé
ALGORITHM=$(echo "$RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('algorithme_utilise', 'NOT_FOUND'))
except:
    print('PARSE_ERROR')
" 2>/dev/null)

echo ""
echo "🎯 Résultat du test de routing :"
echo "-------------------------------"
if [ "$ALGORITHM" = "nexten_matcher" ]; then
    echo "✅ SUCCESS! V2 route correctement vers Nexten Matcher"
    echo "   🎉 Algorithme utilisé: $ALGORITHM"
elif [ "$ALGORITHM" = "v2_routed_fallback_basic" ]; then
    echo "❌ PROBLÈME: V2 utilise encore le fallback"
    echo "   ⚠️  Algorithme utilisé: $ALGORITHM"
    echo "   📋 Actions possibles:"
    echo "      - Vérifier les logs: docker-compose logs supersmartmatch-v2"
    echo "      - Vérifier la configuration dans le conteneur"
    echo "      - S'assurer que Nexten répond sur /match (pas /api/match)"
else
    echo "❓ Résultat inattendu: $ALGORITHM"
fi

echo ""
echo "📋 Commandes utiles :"
echo "--------------------"
echo "• Voir les logs V2:     docker-compose logs -f supersmartmatch-v2"
echo "• Voir les logs Nexten: docker-compose logs -f nexten-matcher"
echo "• Redémarrer tout:      docker-compose restart"
echo "• État des services:    docker-compose ps"

echo ""
echo "🔍 Si le problème persiste :"
echo "----------------------------"
echo "• Vérifiez que la configuration est bien dans le conteneur"
echo "• Vérifiez que Nexten accepte le bon format de payload"
echo "• Consultez les logs pour plus de détails"

echo ""
echo "✅ Script terminé!"