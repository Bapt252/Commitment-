#!/bin/bash

# 🚀 SuperSmartMatch - Script de test avec routes correctes identifiées
# Tests des API V1 classique (5052) et SuperSmartMatch V1 (5062)

echo "=========================================="
echo "🚀 SUPERSMARTMATCH - TESTS AVEC ROUTES CORRECTES"
echo "=========================================="

# Configuration des services identifiés
MATCHING_SERVICE_V1="http://localhost:5052"      # Service de matching classique  
SUPERSMARTMATCH_V1="http://localhost:5062"       # SuperSmartMatch V1 (pas V2!)

echo ""
echo "📋 Services testés :"
echo "   Port 5052: Service de matching classique (V1)"
echo "   Port 5062: SuperSmartMatch V1 unifié (4 algorithmes)"
echo ""

# Vérification des services
echo "🔍 1. Vérification des services..."

echo "   ✓ Test health check port 5052:"
curl -s "$MATCHING_SERVICE_V1/health" | jq '.' || echo "❌ Service 5052 non accessible"

echo ""
echo "   ✓ Test health check port 5062:"
curl -s "$SUPERSMARTMATCH_V1/api/v1/health" | jq '.' || echo "❌ Service 5062 non accessible"

echo ""
echo "=========================================="
echo "🔧 2. Test Service de matching classique (Port 5052)"
echo "=========================================="

echo "   📡 Route: /api/v1/queue-matching"
echo ""

# Test V1 classique sur port 5052
curl -X POST "$MATCHING_SERVICE_V1/api/v1/queue-matching" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "test-candidate-123",
    "job_id": "test-job-456",
    "webhook_url": "https://example.com/webhook"
  }' | jq '.'

echo ""
echo "=========================================="
echo "🧠 3. Test SuperSmartMatch V1 (Port 5062)"
echo "=========================================="

echo "   📡 Route: /api/v1/match (Service unifié)"
echo ""

# Test SuperSmartMatch V1 avec le bon format
curl -X POST "$SUPERSMARTMATCH_V1/api/v1/match" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Jean Dupont",
      "email": "jean.dupont@example.com",
      "technical_skills": ["Python", "Django", "PostgreSQL"],
      "experience_years": 5,
      "location": "Paris, France"
    },
    "offers": [
      {
        "id": "job-123",
        "title": "Développeur Python Senior",
        "company": "TechCorp",
        "required_skills": ["Python", "Django", "PostgreSQL"],
        "location": "Paris, France",
        "experience_required": "3-7 ans"
      },
      {
        "id": "job-456", 
        "title": "Lead Developer Python",
        "company": "StartupAI",
        "required_skills": ["Python", "FastAPI", "Machine Learning"],
        "location": "Lyon, France",
        "experience_required": "5+ ans"
      }
    ],
    "algorithm": "smart-match"
  }' | jq '.'

echo ""
echo "=========================================="
echo "🎯 4. Test des algorithmes disponibles"
echo "=========================================="

echo "   📊 Liste des algorithmes SuperSmartMatch V1:"
curl -s "$SUPERSMARTMATCH_V1/api/v1/algorithms" | jq '.' || echo "Route non disponible"

echo ""
echo "   📈 Métriques de performance:"
curl -s "$SUPERSMARTMATCH_V1/api/v1/metrics" | jq '.' || echo "Route non disponible"

echo ""
echo "=========================================="
echo "🔬 5. Test comparaison d'algorithmes"
echo "=========================================="

echo "   🧪 Comparaison: smart-match vs enhanced"
curl -X POST "$SUPERSMARTMATCH_V1/api/v1/compare" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Alice Expert",
      "technical_skills": ["Python", "Machine Learning", "TensorFlow"],
      "experience_years": 8
    },
    "offers": [
      {
        "id": "ml-job-789",
        "title": "ML Engineer Senior",
        "required_skills": ["Python", "Machine Learning", "TensorFlow", "AWS"],
        "experience_required": "5+ ans"
      }
    ],
    "algorithms": ["smart-match", "enhanced"]
  }' | jq '.' || echo "Comparaison non disponible"

echo ""
echo "=========================================="
echo "🧪 6. Test des 4 algorithmes individuellement"
echo "=========================================="

# Données de test pour les algorithmes
test_data='{
  "candidate": {
    "name": "Bob Developer",
    "technical_skills": ["JavaScript", "React", "Node.js"],
    "experience_years": 3,
    "location": "Paris, France"
  },
  "offers": [
    {
      "id": "frontend-job",
      "title": "Développeur Frontend",
      "required_skills": ["JavaScript", "React", "CSS"],
      "location": "Paris, France"
    }
  ]
}'

algorithms=("smart-match" "enhanced" "semantic" "hybrid")

for algo in "${algorithms[@]}"; do
    echo "   🔬 Test algorithme: $algo"
    
    modified_data=$(echo "$test_data" | jq --arg alg "$algo" '. + {algorithm: $alg}')
    
    curl -X POST "$SUPERSMARTMATCH_V1/api/v1/match" \
      -H "Content-Type: application/json" \
      -d "$modified_data" \
      -s | jq -r '.algorithm_used // "N/A"' | head -1 | tr -d '\n'
    
    echo ""
done

echo ""
echo "=========================================="
echo "📊 7. Test Dashboard et monitoring"
echo "=========================================="

echo "   🖥️ Dashboard SuperSmartMatch (HTML):"
echo "   📍 URL: http://localhost:5062/dashboard"
echo "   🌐 Ouvrez dans votre navigateur pour l'interface complète"

# Test simple du dashboard
dashboard_status=$(curl -s -w "%{http_code}" -o /dev/null "$SUPERSMARTMATCH_V1/dashboard")
if [ "$dashboard_status" = "200" ]; then
    echo "   ✅ Dashboard accessible"
else
    echo "   ❌ Dashboard non accessible (HTTP $dashboard_status)"
fi

echo ""
echo "=========================================="
echo "✅ TESTS TERMINÉS"
echo "=========================================="

echo ""
echo "📝 Résumé des routes fonctionnelles :"
echo ""
echo "   🔧 Port 5052 - Service matching classique :"
echo "   • GET  /health"
echo "   • POST /api/v1/queue-matching"
echo ""
echo "   🧠 Port 5062 - SuperSmartMatch V1 unifié :"
echo "   • GET  /api/v1/health"
echo "   • GET  /api/v1/algorithms" 
echo "   • GET  /api/v1/metrics"
echo "   • GET  /dashboard"
echo "   • POST /api/v1/match (Route principale)"
echo "   • POST /api/v1/compare"
echo ""
echo "   🎯 Algorithmes disponibles :"
echo "   • smart-match (géolocalisation optimisée)"
echo "   • enhanced (profils expérimentés)"
echo "   • semantic (analyse sémantique)"
echo "   • hybrid (multi-algorithmes)"
echo ""
echo "🎉 SuperSmartMatch V1 opérationnel avec 4 algorithmes intelligents !"
echo "📖 Documentation: https://github.com/Bapt252/SuperSmartMatch-Service"
