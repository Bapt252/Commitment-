#!/bin/bash

# 🧪 TEST AVEC PAYLOAD CORRECT - Format Nexten
# Teste avec le bon format de données

echo "🧪 === TEST AVEC PAYLOAD CORRECT - FORMAT NEXTEN ==="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📋 Test avec le format correct pour Nexten...${NC}"

# Payload correct basé sur l'erreur 422 (il faut "candidate" pas "cv_data")
CORRECT_PAYLOAD='{
  "candidate": {
    "id": "test-candidate-1",
    "profile": {
      "skills": ["Python", "Machine Learning", "TensorFlow"],
      "experience_years": 5,
      "education_level": "Master",
      "location": "Paris",
      "salary_expectation": 70000,
      "contract_type_preference": "CDI",
      "mobility_km": 50,
      "remote_work_accepted": true
    },
    "questionnaire": {
      "completed": true,
      "behavioral_profile": {
        "autonomie": 8,
        "leadership": 7,
        "communication": 9
      },
      "detailed_preferences": {
        "teletravail": true,
        "management": false,
        "innovation": true
      },
      "completeness_score": 95
    }
  },
  "jobs": [
    {
      "id": "test-job-nexten-1",
      "title": "Senior ML Engineer",
      "company": "TechCorp",
      "location": "Paris",
      "description": "Développement de modèles ML avancés",
      "requirements": {
        "skills": ["Python", "Machine Learning", "TensorFlow"],
        "experience_years": 5,
        "education_level": "Master"
      },
      "conditions": {
        "salary_min": 60000,
        "salary_max": 80000,
        "contract_type": "CDI",
        "remote_work_possible": true
      },
      "metadata": {
        "sector": "Tech",
        "company_size": "Medium",
        "urgency": "Normal",
        "attractiveness_score": 85,
        "priority": 1
      }
    }
  ],
  "matching_options": {
    "max_results": 10,
    "min_score": 0.0,
    "include_travel_time": true,
    "max_distance_km": 50,
    "context": {
      "test_mode": true,
      "force_nexten": true
    }
  },
  "algorithm": "nexten_ml_advanced",
  "version": "2.0"
}'

echo "🚀 Envoi de la requête avec le format correct..."
echo "Endpoint: http://localhost:5070/api/v2/match"

RESPONSE=$(curl -s -X POST "http://localhost:5070/api/v2/match" \
    -H "Content-Type: application/json" \
    -H "User-Agent: Test-Nexten-Correct-Format/1.0" \
    -d "$CORRECT_PAYLOAD" 2>/dev/null)

if [[ -z "$RESPONSE" ]]; then
    echo -e "${RED}❌ Aucune réponse reçue${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Réponse reçue${NC}"
echo

# Analyser la réponse
echo -e "${BLUE}📊 Analyse de la réponse:${NC}"

# Sauvegarder pour analyse
echo "$RESPONSE" > /tmp/nexten_correct_test.json

# Vérifier si c'est une erreur ou un succès
if echo "$RESPONSE" | grep -q '"detail"'; then
    echo -e "${RED}❌ Erreur dans la réponse:${NC}"
    echo "$RESPONSE" | head -c 500
    echo
    echo -e "${YELLOW}💡 Le format peut encore être incorrect ou le service a un problème${NC}"
elif echo "$RESPONSE" | grep -qi "nexten"; then
    echo -e "${GREEN}🎉 SUCCÈS: Nexten détecté dans la réponse !${NC}"
    
    # Extraire l'algorithme si possible
    if command -v python3 &> /dev/null; then
        ALGO=$(python3 -c "
import json, sys
try:
    data = json.loads('''$RESPONSE''')
    print('Algorithm:', data.get('algorithme_utilise', data.get('algorithm_used', 'UNKNOWN')))
    print('Matches:', len(data.get('matches', [])))
    print('Services:', data.get('services_externes_utilises', data.get('external_services', [])))
except Exception as e:
    print('Parse error:', e)
" 2>/dev/null)
        echo "$ALGO"
    fi
    
    echo
    echo "Réponse complète (premiers 800 caractères):"
    echo "$RESPONSE" | head -c 800
else
    echo -e "${YELLOW}⚠️  Réponse reçue mais pas de Nexten détecté${NC}"
    echo "Premiers 300 caractères:"
    echo "$RESPONSE" | head -c 300
fi

echo
echo -e "${BLUE}🔍 Vérification des logs récents...${NC}"

# Vérifier les logs pour voir si l'endpoint est maintenant correct
V2_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(supersmartmatch.*v2|v2.*unified|ssm.*v2)" | head -1)
NEXTEN_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(nexten|matching)" | head -1)

if [ -n "$V2_CONTAINER" ]; then
    echo "📋 Logs récents V2 ($V2_CONTAINER):"
    docker logs --tail=10 "$V2_CONTAINER" 2>/dev/null | grep -E "(POST|nexten|endpoint|match)" || \
    docker logs --tail=5 "$V2_CONTAINER" 2>/dev/null
fi

echo

if [ -n "$NEXTEN_CONTAINER" ]; then
    echo "📋 Logs récents Nexten ($NEXTEN_CONTAINER):"
    docker logs --tail=10 "$NEXTEN_CONTAINER" 2>/dev/null | grep -E "(POST|/match|/api)" || \
    docker logs --tail=5 "$NEXTEN_CONTAINER" 2>/dev/null
fi

echo
echo -e "${BLUE}🎯 VALIDATION:${NC}"

# Vérifier dans les logs si on voit encore /api/v1/queue-matching
if [ -n "$NEXTEN_CONTAINER" ]; then
    RECENT_LOGS=$(docker logs --tail=20 "$NEXTEN_CONTAINER" 2>/dev/null)
    
    if echo "$RECENT_LOGS" | grep -q "POST /match HTTP"; then
        echo -e "${GREEN}✅ SUCCÈS: V2 utilise maintenant /match !${NC}"
    elif echo "$RECENT_LOGS" | grep -q "POST /api/v1/queue-matching"; then
        echo -e "${RED}❌ PROBLÈME: V2 utilise encore /api/v1/queue-matching${NC}"
        echo "   → Le conteneur n'a pas été reconstruit avec la nouvelle config"
    else
        echo -e "${YELLOW}⚠️  Pas d'activité récente détectée dans les logs${NC}"
    fi
fi

echo
echo -e "${YELLOW}📝 PROCHAINES ÉTAPES:${NC}"

if echo "$RESPONSE" | grep -qi "nexten" && ! echo "$RESPONSE" | grep -q '"detail"'; then
    echo -e "${GREEN}🎉 OBJECTIF ATTEINT !${NC}"
    echo "  ✅ SuperSmartMatch V2 route vers Nexten"
    echo "  ✅ Plus de fallback utilisé"
    echo "  ✅ Endpoint /match fonctionne"
else
    echo "1. Si erreur 422 → Vérifier le format du payload"
    echo "2. Si logs montrent encore /api/v1/queue-matching → Reconstruire le conteneur"
    echo "3. Si Nexten inaccessible → Vérifier le service Nexten"
    echo
    echo "Commande de reconstruction manuelle:"
    echo "docker-compose stop \$SERVICE_NAME"
    echo "docker-compose build --no-cache \$SERVICE_NAME"
    echo "docker-compose up -d \$SERVICE_NAME"
fi

echo
echo -e "${GREEN}🚀 TEST TERMINÉ !${NC}"
echo "Fichier de réponse sauvé: /tmp/nexten_correct_test.json"