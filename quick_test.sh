#!/bin/bash

# SuperSmartMatch V2 - Quick Test Script
# =====================================
# Script de test rapide avec les bons formats de données

set -e

API_URL="http://localhost:8000"
API_ENDPOINT="$API_URL/api/matching/complete"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 SuperSmartMatch V2 - Test Rapide${NC}"
echo "========================================"

# Vérification que l'API est en ligne
echo -e "${YELLOW}🔍 Vérification de l'API...${NC}"
if ! curl -s "$API_URL/health" > /dev/null; then
    echo -e "${RED}❌ API non disponible sur $API_URL${NC}"
    echo -e "${YELLOW}💡 Démarrez l'API avec: python3 data-adapter/api_matching.py${NC}"
    exit 1
fi

echo -e "${GREEN}✅ API SuperSmartMatch V2 en ligne${NC}"

# Test 1: Match Excellent (Baptiste Coma profil)
echo -e "\n${BLUE}🎯 Test 1: Match Excellent${NC}"
echo "Candidat: Baptiste Coma (AI/Python Expert)"
echo "Job: Senior AI Developer"

RESPONSE1=$(curl -s -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "nom": "Baptiste",
      "prenom": "Coma",
      "email": "baptiste.coma@gmail.com",
      "competences": ["Python", "AI", "FastAPI", "Machine Learning", "Docker"],
      "annees_experience": 5,
      "formation": "Master Informatique"
    },
    "questionnaire_data": {
      "adresse": "Paris",
      "salaire_min": 55000,
      "contrats_recherches": ["CDI"],
      "temps_trajet_max": 45
    },
    "jobs_data": [{
      "id": "1",
      "titre": "Senior AI Developer",
      "entreprise": "TechCorp AI",
      "competences": ["Python", "AI", "Machine Learning"],
      "salaire": "65000",
      "localisation": "Paris",
      "type_contrat": "CDI"
    }]
  }')

# Extraction du score (approximative pour bash)
if echo "$RESPONSE1" | grep -q "success.*true"; then
    echo -e "${GREEN}✅ Test 1 réussi - Match trouvé${NC}"
    # Affichage simplifié du résultat
    echo "$RESPONSE1" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        matches = data.get('data', [])
        if matches:
            score = matches[0].get('matching_score', 'N/A')
            print(f'   🏆 Score: {score}%')
            if isinstance(score, (int, float)) and score >= 80:
                print('   🎉 EXCELLENT MATCH!')
            elif isinstance(score, (int, float)) and score >= 60:
                print('   👍 BON MATCH')
        stats = data.get('stats', {})
        if stats.get('processing_time'):
            print(f'   ⏱️  Temps: {stats[\"processing_time\"]}s')
except:
    print('   📊 Résultat OK (détails non parsés)')
"
else
    echo -e "${RED}❌ Test 1 échoué${NC}"
    echo "Réponse: $RESPONSE1"
fi

# Test 2: Match Partiel
echo -e "\n${BLUE}🎯 Test 2: Match Partiel${NC}"
echo "Candidat: Junior Frontend"  
echo "Job: Senior Backend"

RESPONSE2=$(curl -s -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["HTML", "CSS", "JavaScript"],
      "annees_experience": 1,
      "formation": "Bachelor"
    },
    "questionnaire_data": {
      "salaire_min": 35000,
      "adresse": "Lyon"
    },
    "jobs_data": [{
      "id": "2",
      "titre": "Senior Backend Developer",
      "competences": ["Python", "Django", "PostgreSQL"],
      "salaire": "60000",
      "localisation": "Paris",
      "type_contrat": "CDI"
    }]
  }')

if echo "$RESPONSE2" | grep -q "success.*true"; then
    echo -e "${GREEN}✅ Test 2 réussi - Match trouvé${NC}"
    echo "$RESPONSE2" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        matches = data.get('data', [])
        if matches:
            score = matches[0].get('matching_score', 'N/A')
            print(f'   🏆 Score: {score}%')
            if isinstance(score, (int, float)):
                if score >= 80:
                    print('   🎉 EXCELLENT MATCH!')
                elif score >= 60:
                    print('   👍 BON MATCH')
                elif score >= 40:
                    print('   🤔 MATCH PARTIEL')
                else:
                    print('   ❌ FAIBLE COMPATIBILITÉ')
except:
    print('   📊 Résultat OK')
"
else
    echo -e "${RED}❌ Test 2 échoué${NC}"
fi

# Test 3: Multiple Jobs
echo -e "\n${BLUE}🎯 Test 3: Multiple Jobs${NC}"
echo "Candidat: Full-Stack Developer"
echo "Jobs: 3 offres différentes"

RESPONSE3=$(curl -s -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["JavaScript", "React", "Node.js", "Python"],
      "annees_experience": 3,
      "formation": "Master"
    },
    "questionnaire_data": {
      "salaire_min": 45000,
      "adresse": "Paris"
    },
    "jobs_data": [
      {
        "id": "3a",
        "titre": "Frontend React Developer",
        "competences": ["React", "JavaScript", "CSS"],
        "salaire": "48000",
        "localisation": "Paris"
      },
      {
        "id": "3b", 
        "titre": "Full-Stack Developer",
        "competences": ["JavaScript", "React", "Node.js"],
        "salaire": "55000",
        "localisation": "Paris"
      },
      {
        "id": "3c",
        "titre": "Python Backend Developer", 
        "competences": ["Python", "Django", "PostgreSQL"],
        "salaire": "52000",
        "localisation": "Lyon"
      }
    ]
  }')

if echo "$RESPONSE3" | grep -q "success.*true"; then
    echo -e "${GREEN}✅ Test 3 réussi - Matches trouvés${NC}"
    echo "$RESPONSE3" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data.get('success'):
        matches = data.get('data', [])
        print(f'   📊 {len(matches)} résultat(s) trouvé(s)')
        for i, match in enumerate(matches[:3]):
            score = match.get('matching_score', 'N/A')
            title = match.get('job_title', 'N/A')
            print(f'   #{i+1}: {title} - {score}%')
except:
    print('   📊 Résultats OK')
"
else
    echo -e "${RED}❌ Test 3 échoué${NC}"
fi

# Statut API final
echo -e "\n${BLUE}📊 Statut API Final${NC}"
curl -s "$API_URL/status" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'🟢 Status: {data.get(\"status\", \"unknown\")}')
    components = data.get('components', {})
    for comp, status in components.items():
        print(f'   • {comp}: {status}')
except:
    print('📊 API opérationnelle')
"

echo -e "\n${GREEN}🎉 Tests terminés !${NC}"
echo -e "${YELLOW}📚 Pour plus de tests: ${NC}"
echo "   • Interface web: open test_matching_interface.html"
echo "   • Script Python: python3 test_matching_api.py"
echo "   • Documentation: open TESTING_GUIDE.md"
echo -e "${BLUE}   • API Docs: $API_URL/docs${NC}"
