#!/bin/bash
# Script de diagnostic pour SuperSmartMatch V2
# Teste différents formats de données pour identifier le bon schéma

set -e

echo "🔍 DIAGNOSTIC SUPERSMARTMATCH V2"
echo "==============================="

V2_URL="http://localhost:5070"

# Fonction pour tester un payload avec diagnostic détaillé
test_payload() {
    local test_name="$1"
    local payload="$2"
    
    echo ""
    echo "🧪 Test: $test_name"
    echo "Payload: $payload"
    echo "Response:"
    
    response=$(curl -s -w "\nHTTP_CODE:%{http_code}\nTIME:%{time_total}" \
        -X POST "${V2_URL}/api/v2/match" \
        -H "Content-Type: application/json" \
        -d "$payload" 2>/dev/null)
    
    echo "$response"
    echo "----------------------------------------"
}

# Test 1: Format minimal actuel (qui échoue)
test_payload "Format minimal actuel" \
'{"user_profile": {"age": 28}, "jobs": [{"title": "Test"}]}'

# Test 2: Format plus complet
test_payload "Format complet" \
'{
  "user_profile": {
    "age": 28,
    "skills": ["Python"],
    "location": "Paris"
  },
  "jobs": [
    {
      "title": "Python Developer",
      "company": "TechCorp",
      "location": "Paris"
    }
  ]
}'

# Test 3: Format avec questionnaire (pour Nexten)
test_payload "Format questionnaire Nexten" \
'{
  "user_profile": {
    "age": 28,
    "questionnaire_complete": true,
    "skills": ["Python", "Machine Learning"],
    "experience_years": 3
  },
  "jobs": [
    {
      "title": "Data Scientist",
      "required_skills": ["Python", "ML"]
    }
  ]
}'

# Test 4: Format alternatif avec "offers" (cas Nexten)
test_payload "Format offers (Nexten style)" \
'{
  "user_profile": {
    "age": 28,
    "skills": ["Python"]
  },
  "offers": [
    {
      "title": "Python Developer"
    }
  ]
}'

# Test 5: Format avec profile/candidate
test_payload "Format profile/candidate" \
'{
  "profile": {
    "age": 28,
    "skills": ["Python"]
  },
  "jobs": [
    {
      "title": "Python Developer"
    }
  ]
}'

# Test 6: Check des endpoints disponibles
echo ""
echo "🔍 ENDPOINTS DISPONIBLES:"
echo "========================"

for endpoint in "/api/v2/match" "/api/v1/match" "/match" "/api/match"; do
    echo -n "Testing endpoint $endpoint... "
    
    status=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "${V2_URL}${endpoint}" \
        -H "Content-Type: application/json" \
        -d '{}' 2>/dev/null)
    
    if [ "$status" != "404" ]; then
        echo "✅ EXISTS (HTTP $status)"
    else
        echo "❌ NOT FOUND"
    fi
done

echo ""
echo "🎯 DIAGNOSTIC TERMINÉ"
echo "Analysez les réponses ci-dessus pour identifier:"
echo "1. Le format de données attendu"
echo "2. Les champs obligatoires"  
echo "3. Le bon endpoint à utiliser"
