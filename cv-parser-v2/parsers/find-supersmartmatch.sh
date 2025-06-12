#!/bin/bash

echo "🔍 Recherche du vrai service SuperSmartMatch..."

# Test des endpoints classiques SuperSmartMatch
echo "1. Test des ports SuperSmartMatch courants:"
for port in 5062 5061 5060 5052 5051 5050; do
    echo "Port $port:"
    
    # Test health
    health=$(curl -s --connect-timeout 2 "http://localhost:$port/health" 2>/dev/null)
    if [[ $? -eq 0 ]] && [[ "$health" == *"healthy"* ]]; then
        echo "  ✅ Health: $health"
    fi
    
    # Test API docs
    docs=$(curl -s --connect-timeout 2 "http://localhost:$port/docs" 2>/dev/null)
    if [[ $? -eq 0 ]] && [[ "$docs" == *"swagger"* || "$docs" == *"OpenAPI"* ]]; then
        echo "  📚 Documentation API disponible"
    fi
    
    # Test endpoint /match
    match_test=$(curl -s --connect-timeout 2 "http://localhost:$port/match" -X POST \
        -H "Content-Type: application/json" \
        -d '{"test": "data"}' 2>/dev/null)
    if [[ $? -eq 0 ]] && [[ "$match_test" != *"Not Found"* ]] && [[ "$match_test" != *"404"* ]]; then
        echo "  🎯 Endpoint /match disponible: $(echo "$match_test" | head -c 100)..."
    fi
    
    # Test endpoint /api/v1/match  
    match_v1_test=$(curl -s --connect-timeout 2 "http://localhost:$port/api/v1/match" -X POST \
        -H "Content-Type: application/json" \
        -d '{"test": "data"}' 2>/dev/null)
    if [[ $? -eq 0 ]] && [[ "$match_v1_test" != *"Not Found"* ]] && [[ "$match_v1_test" != *"404"* ]]; then
        echo "  🎯 Endpoint /api/v1/match disponible: $(echo "$match_v1_test" | head -c 100)..."
    fi
    
    # Test endpoint /api/v2/match
    match_v2_test=$(curl -s --connect-timeout 2 "http://localhost:$port/api/v2/match" -X POST \
        -H "Content-Type: application/json" \
        -d '{"test": "data"}' 2>/dev/null)
    if [[ $? -eq 0 ]] && [[ "$match_v2_test" != *"Not Found"* ]] && [[ "$match_v2_test" != *"404"* ]]; then
        echo "  🎯 Endpoint /api/v2/match disponible: $(echo "$match_v2_test" | head -c 100)..."
    fi
    
    echo ""
done

echo "2. Vérification des conteneurs Docker SuperSmartMatch:"
docker ps | grep -i -E "(smart|match)" || echo "Aucun conteneur SuperSmartMatch trouvé"

echo ""
echo "3. Recherche dans les logs Docker:"
docker-compose logs 2>/dev/null | grep -i -E "(supersmartmatch|smart.*match)" | tail -5 || echo "Pas de logs SuperSmartMatch"

echo ""
echo "4. Test du service de matching sur 5052 avec les bons endpoints:"
echo "Service sur 5052:"
curl -s http://localhost:5052/health | python3 -m json.tool 2>/dev/null

echo ""
echo "Endpoints disponibles sur 5052:"
echo "- /health ✅"
echo "- /api/v1/queue-matching (matching asynchrone)"
echo "- /api/v1/result/{job_id}"
echo "- /api/v1/status/{job_id}"

echo ""
echo "🔍 Recherche de SuperSmartMatch dans les fichiers docker-compose:"
find . -name "docker-compose*.yml" -exec grep -l -i "supersmartmatch" {} \; 2>/dev/null || echo "Aucun fichier docker-compose avec SuperSmartMatch"
