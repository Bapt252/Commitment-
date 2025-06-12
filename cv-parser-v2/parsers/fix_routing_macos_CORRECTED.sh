#!/bin/bash

# 🔧 Script de diagnostic et correction SuperSmartMatch V2 pour macOS
# Détecte automatiquement les services et utilise les bons endpoints

echo "🎯 SuperSmartMatch V2 - Diagnostic et correction automatique"
echo "============================================================"

# Vérifier que Docker est en cours d'exécution
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker n'est pas en cours d'exécution"
    echo "   Veuillez démarrer Docker Desktop"
    exit 1
fi

echo "✅ Docker est accessible"

# Auto-détection des services Docker en cours
echo ""
echo "🔍 Détection automatique des services..."
echo "----------------------------------------"

# Chercher les conteneurs SuperSmartMatch V2
V2_CONTAINERS=$(docker ps --format "table {{.Names}}" --filter "name=.*v2.*" --filter "name=.*smartmatch.*" | tail -n +2)
NEXTEN_CONTAINERS=$(docker ps --format "table {{.Names}}" --filter "name=.*nexten.*" --filter "name=.*match.*" | tail -n +2)

echo "🔍 Conteneurs V2 détectés: $V2_CONTAINERS"
echo "🔍 Conteneurs Nexten détectés: $NEXTEN_CONTAINERS"

# Fonction pour redémarrer le service détecté
restart_v2_service() {
    local service_name="$1"
    echo ""
    echo "🔧 Redémarrage du service: $service_name"
    echo "----------------------------------------"
    
    # Arrêter et redémarrer le service
    echo "⏳ Arrêt de $service_name..."
    docker stop "$service_name" 2>/dev/null || docker-compose stop "$service_name" 2>/dev/null
    
    echo "⏳ Redémarrage de $service_name..."
    docker start "$service_name" 2>/dev/null || docker-compose up -d "$service_name" 2>/dev/null
    
    echo "⏳ Attente du démarrage (10 secondes)..."
    sleep 10
}

# Si un service V2 est trouvé, le redémarrer
if [ ! -z "$V2_CONTAINERS" ]; then
    for container in $V2_CONTAINERS; do
        restart_v2_service "$container"
    done
else
    echo "⚠️  Aucun conteneur V2 trouvé, tentative avec docker-compose..."
    docker-compose up -d supersmartmatch-v2-unified 2>/dev/null || docker-compose up -d supersmartmatch-v2 2>/dev/null
    sleep 10
fi

echo ""
echo "🧪 Tests de vérification automatiques :"
echo "----------------------------------------"

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

# Test 3: Découverte des endpoints
echo "3️⃣ Découverte des endpoints disponibles..."
SERVICE_INFO=$(curl -s http://localhost:5070/ 2>/dev/null)
echo "   📋 Endpoints découverts:"
echo "$SERVICE_INFO" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'endpoints' in data:
        for key, value in data['endpoints'].items():
            print(f'      • {key}: {value}')
    else:
        print('      ℹ️  Structure de réponse inattendue')
except:
    print('      ❌ Impossible de parser la réponse du service')
" 2>/dev/null

# Test 4: Test des endpoints V2 et V1 avec les bons formats
echo "4️⃣ Test du routing avec les VRAIS endpoints..."

# Format pour l'endpoint V1 compatible (/match)
V1_PAYLOAD='{
  "candidate": {
    "name": "Test Candidat",
    "email": "test@example.com",
    "technical_skills": ["Python", "FastAPI", "Docker"],
    "experiences": [{
      "title": "Développeur Python",
      "company": "TechCorp",
      "duration": 24
    }]
  },
  "offers": [{
    "id": "job_1",
    "title": "Développeur Backend",
    "company": "StartupCorp",
    "required_skills": ["Python", "API", "Docker"]
  }],
  "algorithm": "auto"
}'

echo "   🔄 Test endpoint V1 compatible (/match)..."
V1_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "$V1_PAYLOAD" \
  http://localhost:5070/match 2>/dev/null)

echo "   📝 Réponse V1 (/match):"
echo "$V1_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$V1_RESPONSE"

# Vérifier l'algorithme utilisé
ALGORITHM=$(echo "$V1_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(data.get('algorithm_used', 'NOT_FOUND'))
except:
    print('PARSE_ERROR')
" 2>/dev/null)

echo ""
echo "🎯 Résultat du diagnostic :"
echo "---------------------------"
if [ "$ALGORITHM" = "nexten" ]; then
    echo "✅ SUCCESS! V2 route correctement vers Nexten Matcher"
    echo "   🎉 Algorithme utilisé: $ALGORITHM"
    echo "   🔧 La correction de l'endpoint NEXTEN_ENDPOINT = '/match' fonctionne !"
elif [[ "$ALGORITHM" == *"fallback"* ]]; then
    echo "⚠️  V2 utilise encore un fallback: $ALGORITHM"
    echo "   📋 Actions recommandées:"
    echo "      - Vérifier que Nexten est bien accessible sur port 5052"
    echo "      - Vérifier les logs pour les erreurs de connexion"
    echo "      - S'assurer que la configuration a été appliquée dans le conteneur"
elif [ "$ALGORITHM" = "PARSE_ERROR" ] || [ "$ALGORITHM" = "NOT_FOUND" ]; then
    echo "❓ Réponse inattendue du service"
    echo "   📝 Réponse brute: $V1_RESPONSE"
    echo "   📋 Vérifications:"
    echo "      - Le service V2 fonctionne-t-il correctement ?"
    echo "      - Les logs montrent-ils des erreurs ?"
else
    echo "✅ Algorithme utilisé: $ALGORITHM"
    echo "   ℹ️  Le routing fonctionne (même si ce n'est pas Nexten)"
fi

echo ""
echo "📊 Diagnostic des services :"
echo "----------------------------"
echo "• SuperSmartMatch V2 (5070): $([ "$V2_HEALTH" = "200" ] && echo "✅ UP" || echo "❌ DOWN")"
echo "• Nexten Matcher (5052): $([ "$NEXTEN_HEALTH" = "200" ] && echo "✅ UP" || echo "❌ DOWN")"

echo ""
echo "📋 Commandes de diagnostic :"
echo "----------------------------"
echo "• Logs V2:              docker logs \$(docker ps -q --filter name=.*v2.*smart.*) -f"
echo "• Logs Nexten:          docker logs \$(docker ps -q --filter name=.*nexten.*) -f"
echo "• Status des services:  docker ps | grep -E '(smart|nexten)'"
echo "• Restart tout:         docker-compose restart"

echo ""
echo "🔧 Si le routage vers Nexten ne fonctionne pas :"
echo "-----------------------------------------------"
echo "• Vérifiez: curl http://localhost:5052/health"
echo "• Config V2: La variable NEXTEN_ENDPOINT doit être '/match' (pas '/api/match')"
echo "• Réseau:    Les conteneurs peuvent-ils communiquer ?"

echo ""
echo "✅ Diagnostic terminé!"