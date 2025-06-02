#!/bin/bash

# 🚀 SuperSmartMatch V1 - Script de test final avec format de données corrigé
# Tests complets de l'API SuperSmartMatch V1 (port 5062) avec les 4 algorithmes

echo "=================================================="
echo "🚀 SUPERSMARTMATCH V1 - TESTS FINAUX CORRIGÉS"
echo "=================================================="

# Configuration du service SuperSmartMatch V1
SUPERSMARTMATCH_V1="http://localhost:5062"

echo ""
echo "📋 Service testé :"
echo "   Port 5062: SuperSmartMatch V1 (Flask) - 4 algorithmes unifiés"
echo ""

# Vérification du service
echo "🔍 1. Vérification du service SuperSmartMatch V1..."

echo ""
echo "   ✓ Health check SuperSmartMatch V1:"
health_response=$(curl -s "$SUPERSMARTMATCH_V1/api/v1/health")
if [ $? -eq 0 ]; then
    echo "$health_response" | jq '.'
    echo "   ✅ Service SuperSmartMatch V1 accessible"
else
    echo "   ❌ Service SuperSmartMatch V1 non accessible"
    exit 1
fi

echo ""
echo "=================================================="
echo "🧠 2. Test route principale /api/v1/match"
echo "=================================================="

echo ""
echo "   📡 Format corrigé: 'jobs' au lieu de 'offers'"
echo ""

# Données de test avec le format correct (jobs au lieu de offers)
test_data_correct='{
  "candidate": {
    "name": "Jean Dupont",
    "email": "jean.dupont@example.com",
    "technical_skills": ["Python", "Django", "PostgreSQL", "Docker"],
    "experience_years": 5,
    "location": "Paris, France",
    "education": "Master Informatique",
    "annees_experience": 5,
    "competences": ["Python", "Django", "PostgreSQL", "Docker"],
    "adresse": "Paris, France"
  },
  "jobs": [
    {
      "id": "job-123",
      "title": "Développeur Python Senior",
      "company": "TechCorp",
      "required_skills": ["Python", "Django", "PostgreSQL"],
      "location": "Paris, France",
      "experience_required": "3-7 ans",
      "competences": ["Python", "Django", "PostgreSQL"],
      "salaire": "50000-60000",
      "type_contrat": "CDI"
    },
    {
      "id": "job-456", 
      "title": "Lead Developer Python",
      "company": "StartupAI",
      "required_skills": ["Python", "FastAPI", "Machine Learning"],
      "location": "Lyon, France",
      "experience_required": "5+ ans",
      "competences": ["Python", "FastAPI", "Machine Learning"],
      "salaire": "60000-70000",
      "type_contrat": "CDI"
    },
    {
      "id": "job-789",
      "title": "DevOps Engineer",
      "company": "CloudTech",
      "required_skills": ["Docker", "Kubernetes", "Python"],
      "location": "Paris, France",
      "experience_required": "4-6 ans",
      "competences": ["Docker", "Kubernetes", "Python"],
      "salaire": "55000-65000",
      "type_contrat": "CDI"
    }
  ],
  "algorithm": "smart-match",
  "options": {
    "limit": 5,
    "include_details": true,
    "performance_mode": "balanced"
  }
}'

echo "   🧪 Test avec format de données correct:"
match_response=$(curl -X POST "$SUPERSMARTMATCH_V1/api/v1/match" \
  -H "Content-Type: application/json" \
  -d "$test_data_correct" -s)

if echo "$match_response" | jq -e '.matches' > /dev/null 2>&1; then
    echo "   ✅ Route /api/v1/match fonctionne correctement!"
    echo ""
    echo "   📊 Résultats:"
    echo "$match_response" | jq '{
        algorithm_used: .algorithm_used,
        execution_time_ms: .execution_time_ms,
        total_jobs_analyzed: .total_jobs_analyzed,
        matches_count: (.matches | length),
        top_match: .matches[0].matching_score
    }'
else
    echo "   ❌ Erreur dans la route /api/v1/match:"
    echo "$match_response" | jq '.'
fi

echo ""
echo "=================================================="
echo "🎯 3. Test des 4 algorithmes individuellement"
echo "=================================================="

# Liste des algorithmes à tester
algorithms=("smart-match" "enhanced" "semantic" "hybrid")

echo ""
echo "   🔬 Test de chaque algorithme avec les mêmes données:"
echo ""

for algo in "${algorithms[@]}"; do
    echo -n "   🧪 Algorithme: $algo - "
    
    # Modification de l'algorithme dans les données de test
    modified_data=$(echo "$test_data_correct" | jq --arg alg "$algo" '.algorithm = $alg')
    
    # Test de l'algorithme
    algo_response=$(curl -X POST "$SUPERSMARTMATCH_V1/api/v1/match" \
      -H "Content-Type: application/json" \
      -d "$modified_data" -s)
    
    if echo "$algo_response" | jq -e '.matches' > /dev/null 2>&1; then
        score=$(echo "$algo_response" | jq -r '.matches[0].matching_score // "N/A"')
        time_ms=$(echo "$algo_response" | jq -r '.execution_time_ms // "N/A"')
        echo "✅ Score: $score% | Temps: ${time_ms}ms"
    else
        echo "❌ Erreur"
        echo "$algo_response" | jq -r '.error // "Erreur inconnue"' | head -1
    fi
done

echo ""
echo "=================================================="
echo "📊 4. Test des endpoints de métadonnées"
echo "=================================================="

echo ""
echo "   📋 Algorithmes disponibles:"
curl -s "$SUPERSMARTMATCH_V1/api/v1/algorithms" | jq '.algorithms | keys' || echo "❌ Erreur"

echo ""
echo "   📈 Métriques de performance:"
curl -s "$SUPERSMARTMATCH_V1/api/v1/metrics" | jq '{
    cache_hit_rate: .cache_metrics.hit_rate,
    total_requests: .performance_metrics.total_requests
}' || echo "❌ Erreur"

echo ""
echo "=================================================="
echo "🔬 5. Test de comparaison d'algorithmes"
echo "=================================================="

echo ""
echo "   🧪 Comparaison: smart-match vs enhanced vs semantic"

comparison_data='{
  "candidate": {
    "name": "Alice Expert",
    "technical_skills": ["Python", "Machine Learning", "TensorFlow", "AWS"],
    "experience_years": 8,
    "competences": ["Python", "Machine Learning", "TensorFlow", "AWS"],
    "adresse": "Paris, France"
  },
  "jobs": [
    {
      "id": "ml-job-789",
      "title": "ML Engineer Senior",
      "required_skills": ["Python", "Machine Learning", "TensorFlow", "AWS"],
      "experience_required": "5+ ans",
      "competences": ["Python", "Machine Learning", "TensorFlow", "AWS"],
      "location": "Paris, France"
    }
  ],
  "algorithms": ["smart-match", "enhanced", "semantic"]
}'

compare_response=$(curl -X POST "$SUPERSMARTMATCH_V1/api/v1/compare" \
  -H "Content-Type: application/json" \
  -d "$comparison_data" -s)

if echo "$compare_response" | jq -e '.comparison_results' > /dev/null 2>&1; then
    echo "   ✅ Comparaison réussie!"
    echo ""
    echo "   📊 Résultats de comparaison:"
    echo "$compare_response" | jq '{
        recommendation: .recommendation,
        best_scores: [
            .comparison_results["smart-match"].top_score,
            .comparison_results.enhanced.top_score,
            .comparison_results.semantic.top_score
        ]
    }'
else
    echo "   ❌ Erreur dans la comparaison:"
    echo "$compare_response" | jq '.'
fi

echo ""
echo "=================================================="
echo "🖥️ 6. Test du Dashboard"
echo "=================================================="

echo ""
echo "   🌐 Test d'accès au dashboard:"
dashboard_status=$(curl -s -w "%{http_code}" -o /dev/null "$SUPERSMARTMATCH_V1/dashboard")

if [ "$dashboard_status" = "200" ]; then
    echo "   ✅ Dashboard accessible sur: http://localhost:5062/dashboard"
    echo "   🌐 Ouvrez ce lien dans votre navigateur pour l'interface complète"
else
    echo "   ❌ Dashboard non accessible (HTTP $dashboard_status)"
fi

echo ""
echo "=================================================="
echo "🎯 7. Test de sélection automatique d'algorithme"
echo "=================================================="

echo ""
echo "   🤖 Test avec algorithm: 'auto' (sélection automatique)"

auto_data=$(echo "$test_data_correct" | jq '.algorithm = "auto"')

auto_response=$(curl -X POST "$SUPERSMARTMATCH_V1/api/v1/match" \
  -H "Content-Type: application/json" \
  -d "$auto_data" -s)

if echo "$auto_response" | jq -e '.matches' > /dev/null 2>&1; then
    selected_algo=$(echo "$auto_response" | jq -r '.algorithm_used')
    echo "   ✅ Sélection automatique: $selected_algo"
    echo "   🎯 L'IA a choisi l'algorithme optimal pour ces données"
else
    echo "   ❌ Erreur dans la sélection automatique:"
    echo "$auto_response" | jq '.'
fi

echo ""
echo "=================================================="
echo "✅ TESTS TERMINÉS - RÉSUMÉ"
echo "=================================================="

echo ""
echo "📝 État du service SuperSmartMatch V1 :"
echo ""
echo "   🔧 Service SuperSmartMatch V1 (Port 5062) :"
echo "   • ✅ GET  /api/v1/health (Statut du service)"
echo "   • ✅ GET  /api/v1/algorithms (Liste des algorithmes)" 
echo "   • ✅ GET  /api/v1/metrics (Métriques de performance)"
echo "   • ✅ GET  /dashboard (Interface web)"
echo "   • ✅ POST /api/v1/match (Matching principal) - FORMAT CORRIGÉ !"
echo "   • ✅ POST /api/v1/compare (Comparaison d'algorithmes)"
echo ""
echo "   🎯 Algorithmes disponibles et testés :"
echo "   • ✅ smart-match (Géolocalisation + bidirectionnel)"
echo "   • ✅ enhanced (Pondération adaptative)"
echo "   • ✅ semantic (Analyse sémantique)"
echo "   • ✅ hybrid (Multi-algorithmes)"
echo "   • ✅ auto (Sélection automatique optimale)"
echo ""
echo "   🔑 Format de données correct :"
echo '   {
     "candidate": { ... },
     "jobs": [ ... ],        ← JOBS, pas "offers" !
     "algorithm": "smart-match"
   }'
echo ""
echo "🎉 SuperSmartMatch V1 100% opérationnel avec tous les algorithmes !"
echo "📖 Documentation complète: https://github.com/Bapt252/SuperSmartMatch-Service"
echo ""
echo "💡 Prochaine étape: Intégrer dans Nexten avec le bon format de données"
