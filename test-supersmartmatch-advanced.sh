#!/bin/bash
echo "🧪 Test AVANCÉ de SuperSmartMatch v2.0..."
echo "🎯 Test avec format de données corrigé (candidate/offers)"

# Attendre un peu que le service soit prêt
sleep 2

# Test de santé avec nouvelles fonctionnalités
echo "1️⃣ Health check v2.0..."
curl -s http://localhost:5062/health | python3 -m json.tool 2>/dev/null || echo "Service non accessible"

echo -e "\n2️⃣ Test V1 API Compatible..."
curl -s -X POST http://localhost:5062/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "John Doe",
      "technical_skills": ["Python", "Django", "PostgreSQL", "React"],
      "experiences": [
        {
          "title": "Développeur Full Stack",
          "company": "TechCorp",
          "duration_months": 60,
          "skills": ["Python", "Django"]
        }
      ]
    },
    "offers": [
      {
        "id": "job-001",
        "title": "Développeur Python Senior",
        "company": "TechCorp",
        "required_skills": ["Python", "Django", "PostgreSQL"],
        "location": {"city": "Paris", "country": "France"}
      }
    ]
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test basique"

echo -e "\n3️⃣ Test avec géolocalisation (Paris -> Marseille)..."
curl -s -X POST http://localhost:5062/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Marie Martin",
      "technical_skills": ["JavaScript", "React", "Node.js"],
      "experiences": [
        {
          "title": "Frontend Developer",
          "duration_months": 36
        }
      ]
    },
    "offers": [
      {
        "id": "job-geo-001",
        "title": "React Developer",
        "required_skills": ["React", "JavaScript"],
        "location": {"city": "Paris", "country": "France"}
      },
      {
        "id": "job-geo-002",
        "title": "Full Stack Developer",
        "required_skills": ["React", "Node.js"],
        "location": {"city": "Marseille", "country": "France"}
      }
    ],
    "algorithm": "smart-match"
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test géolocalisation"

echo -e "\n4️⃣ Test algorithme enhanced..."
curl -s -X POST http://localhost:5062/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Pierre Dubois",
      "technical_skills": ["Java", "Spring", "Microservices"],
      "experiences": [
        {
          "title": "Senior Java Developer",
          "duration_months": 48,
          "skills": ["Java", "Spring Boot"]
        }
      ]
    },
    "offers": [
      {
        "id": "job-enhanced-001",
        "title": "Java Architect",
        "required_skills": ["Java", "Spring", "Architecture"],
        "location": {"city": "Lyon", "country": "France"}
      }
    ],
    "algorithm": "enhanced"
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test enhanced"

echo -e "\n5️⃣ Test V2 Enhanced API (si disponible)..."
curl -s -X POST http://localhost:5062/api/v2/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Sophie Laurent",
      "email": "sophie@example.com",
      "technical_skills": [
        {"name": "Python", "level": "Expert", "years": 5},
        {"name": "Machine Learning", "level": "Advanced", "years": 3}
      ],
      "experiences": [
        {
          "title": "Senior Developer",
          "company": "TechCorp",
          "duration_months": 36,
          "skills": ["Python", "Django", "PostgreSQL"]
        }
      ]
    },
    "candidate_questionnaire": {
      "work_style": "collaborative",
      "culture_preferences": "innovation_focused",
      "remote_preference": "hybrid"
    },
    "offers": [
      {
        "id": "job_ml_001",
        "title": "ML Engineer",
        "company": "AI Startup",
        "required_skills": ["Python", "TensorFlow", "MLOps"],
        "location": {"city": "Paris", "country": "France"},
        "remote_policy": "hybrid"
      }
    ],
    "algorithm": "auto"
  }' | python3 -m json.tool 2>/dev/null || echo "V2 API non disponible"

echo -e "\n6️⃣ Test algorithme auto..."
curl -s -X POST http://localhost:5062/match \
  -H "Content-Type: application/json" \
  -d '{
    "candidate": {
      "name": "Lucas Bernard",
      "technical_skills": ["C#", ".NET", "Azure"],
      "experiences": [
        {
          "title": "Backend Developer",
          "duration_months": 30
        }
      ]
    },
    "offers": [
      {
        "id": "job-auto-001",
        "title": ".NET Developer",
        "required_skills": ["C#", ".NET Core"],
        "location": {"city": "Toulouse", "country": "France"}
      }
    ],
    "algorithm": "auto"
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test auto"

echo -e "\n✅ Tests avancés terminés"
echo "🎯 Format de données corrigé utilisé:"
echo "   - candidate: {name, technical_skills, experiences}"
echo "   - offers: [{id, title, required_skills, location}]"
echo "   - algorithm: smart-match, enhanced, auto"
echo ""
echo "ℹ️ Si les tests fonctionnent maintenant, le problème était le format de données !"
echo "📚 Consultez la documentation V2 pour les fonctionnalités avancées"