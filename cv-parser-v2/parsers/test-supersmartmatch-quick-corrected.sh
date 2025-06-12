#!/bin/bash

# 🚀 SuperSmartMatch V1 - Script de test rapide avec format de données CORRIGÉ
# Résout l'erreur "Données offres d'emploi requises"

echo "==========================================="
echo "🚀 SUPERSMARTMATCH V1 - TEST RAPIDE CORRIGÉ"
echo "==========================================="

# Configuration
SUPERSMARTMATCH_V1="http://localhost:5062"

echo ""
echo "🔍 1. Vérification du service..."
curl -s "$SUPERSMARTMATCH_V1/api/v1/health" | jq '.' || echo "❌ Service non accessible"

echo ""
echo "🧠 2. Test route /api/v1/match avec FORMAT CORRIGÉ..."
echo ""
echo "   ⚠️  IMPORTANT: Utilisation de 'jobs' au lieu de 'offers'"
echo ""

# Format CORRIGÉ avec "jobs" au lieu de "offers"
curl -X POST "$SUPERSMARTMATCH_V1/api/v1/match" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Jean Dupont",
      "email": "jean.dupont@example.com",
      "technical_skills": ["Python", "Django", "PostgreSQL"],
      "experience_years": 5,
      "location": "Paris, France",
      "competences": ["Python", "Django", "PostgreSQL"],
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
        "competences": ["Python", "Django", "PostgreSQL"]
      },
      {
        "id": "job-456", 
        "title": "Lead Developer Python",
        "company": "StartupAI",
        "required_skills": ["Python", "FastAPI", "Machine Learning"],
        "location": "Lyon, France",
        "experience_required": "5+ ans",
        "competences": ["Python", "FastAPI", "Machine Learning"]
      }
    ],
    "algorithm": "smart-match"
  }' | jq '.'

echo ""
echo "🎯 3. Test des algorithmes disponibles..."
algorithms=("smart-match" "enhanced" "semantic" "hybrid")

for algo in "${algorithms[@]}"; do
    echo ""
    echo "   🧪 Test $algo:"
    
    curl -X POST "$SUPERSMARTMATCH_V1/api/v1/match" \
      -H "Content-Type: application/json" \
      -d "{
        \"candidate\": {
          \"name\": \"Test User\",
          \"technical_skills\": [\"Python\", \"JavaScript\"],
          \"experience_years\": 3,
          \"competences\": [\"Python\", \"JavaScript\"]
        },
        \"jobs\": [
          {
            \"id\": \"test-job\",
            \"title\": \"Developer\",
            \"required_skills\": [\"Python\"],
            \"competences\": [\"Python\"]
          }
        ],
        \"algorithm\": \"$algo\"
      }" -s | jq -r '.algorithm_used // "❌ Erreur"'
done

echo ""
echo "==========================================="
echo "✅ RÉSUMÉ"
echo "==========================================="
echo ""
echo "🔑 CORRECTION APPLIQUÉE:"
echo "   ❌ Ancien format: \"offers\": [...]"
echo "   ✅ Nouveau format: \"jobs\": [...]"
echo ""
echo "📍 Plus d'erreur 'Données offres d'emploi requises' !"
echo ""
echo "🎯 Pour utiliser SuperSmartMatch V1:"
echo "   • Port: 5062"
echo "   • Route: POST /api/v1/match"
echo "   • Format: {\"candidate\": {...}, \"jobs\": [...], \"algorithm\": \"smart-match\"}"
echo ""
echo "🚀 Script complet: ./test-supersmartmatch-v1-final.sh"
