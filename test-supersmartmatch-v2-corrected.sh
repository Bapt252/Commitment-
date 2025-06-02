#!/bin/bash

# 🚀 SuperSmartMatch V2 - Script de test corrigé
# Tests des API V1 et V2 avec les bonnes routes identifiées

echo "=========================================="
echo "🚀 SUPERSMARTMATCH V2 - TESTS CORRIGES"
echo "=========================================="

# Configuration
MATCHING_SERVICE_PORT_5052="http://localhost:5052"
SUPERSMARTMATCH_V2_PORT_5062="http://localhost:5062"

echo ""
echo "📋 Tests des services disponibles:"
echo "   Port 5052: Service de matching classique (V1)"
echo "   Port 5062: SuperSmartMatch V2"
echo ""

# Vérification des services
echo "🔍 1. Vérification des services..."

echo "   ✓ Test health check port 5052:"
curl -s "$MATCHING_SERVICE_PORT_5052/health" | jq '.' || echo "❌ Service 5052 non accessible"

echo ""
echo "   ✓ Test health check port 5062:"
curl -s "$SUPERSMARTMATCH_V2_PORT_5062/health" | jq '.' || echo "❌ Service 5062 non accessible"

echo ""
echo "=========================================="
echo "🔧 2. Test API V1 classique (Port 5052)"
echo "=========================================="

echo "   📡 Route: /api/v1/queue-matching"
echo ""

# Test V1 sur port 5052 avec la bonne route
curl -X POST "$MATCHING_SERVICE_PORT_5052/api/v1/queue-matching" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_id": "test-candidate-123",
    "job_id": "test-job-456",
    "webhook_url": "https://example.com/webhook"
  }' | jq '.'

echo ""
echo "=========================================="
echo "🚀 3. Test SuperSmartMatch V2 (Port 5062)"
echo "=========================================="

echo "   📡 Route: /api/v2/match (Format V2 complet)"
echo ""

# Test V2 avec format complet
curl -X POST "$SUPERSMARTMATCH_V2_PORT_5062/api/v2/match" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Jean Dupont",
      "email": "jean.dupont@example.com",
      "location": {
        "city": "Paris",
        "country": "France"
      },
      "technical_skills": [
        {
          "name": "Python",
          "level": "Expert",
          "years": 5
        },
        {
          "name": "Django",
          "level": "Advanced",
          "years": 3
        }
      ],
      "experiences": [
        {
          "title": "Développeur Senior",
          "company": "TechCorp",
          "duration_months": 24,
          "skills": ["Python", "Django", "PostgreSQL"]
        }
      ],
      "mobility_preferences": "flexible"
    },
    "candidate_questionnaire": {
      "work_style": "collaborative",
      "culture_preferences": "innovation_focused",
      "remote_preference": "hybrid"
    },
    "offers": [
      {
        "id": "job-123",
        "title": "Développeur Python Senior",
        "company": "StartupIA",
        "location": {
          "city": "Paris",
          "country": "France"
        },
        "required_skills": ["Python", "Django", "Machine Learning"],
        "experience_level": "senior",
        "remote_policy": "hybrid",
        "salary_range": {
          "min": 55000,
          "max": 75000,
          "currency": "EUR"
        }
      }
    ],
    "company_questionnaires": [
      {
        "culture": "innovation_focused",
        "team_size": "small",
        "work_methodology": "agile"
      }
    ],
    "algorithm": "auto"
  }' | jq '.'

echo ""
echo "=========================================="
echo "🔄 4. Test Compatibilité V1 sur V2 (Port 5062)"
echo "=========================================="

echo "   📡 Route: /match (Format V1 compatible)"
echo ""

# Test format V1 sur SuperSmartMatch V2
curl -X POST "$SUPERSMARTMATCH_V2_PORT_5062/match" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Marie Martin",
      "technical_skills": ["Python", "Django", "React"],
      "experiences": [
        {
          "title": "Développeuse Full Stack",
          "company": "WebAgency",
          "duration": "2 ans"
        }
      ]
    },
    "offers": [
      {
        "id": "job-456",
        "title": "Développeuse Full Stack",
        "required_skills": ["Python", "Django", "JavaScript"],
        "company": "TechStartup"
      }
    ]
  }' | jq '.'

echo ""
echo "=========================================="
echo "📊 5. Tests de monitoring et santé"
echo "=========================================="

echo "   🔍 Health check détaillé V2:"
curl -s "$SUPERSMARTMATCH_V2_PORT_5062/api/v2/health?detailed=true" | jq '.'

echo ""
echo "   🧠 Recommandations d'algorithmes:"
curl -s "$SUPERSMARTMATCH_V2_PORT_5062/api/v2/algorithm/recommendations?candidate_experience=5&questionnaire_completeness=0.8&has_geo_constraints=true" | jq '.'

echo ""
echo "=========================================="
echo "✅ TESTS TERMINÉS"
echo "=========================================="

echo ""
echo "📝 Résumé des routes identifiées :"
echo "   Port 5052 - Service classique :"
echo "   • /health"
echo "   • /api/v1/queue-matching"
echo ""
echo "   Port 5062 - SuperSmartMatch V2 :"
echo "   • /health"
echo "   • /api/v2/health"
echo "   • /api/v2/match (Format V2 complet)"
echo "   • /match (Compatible V1)"
echo "   • /api/v2/algorithm/recommendations"
echo ""
echo "🎯 Utilisez ces routes pour vos tests !"
