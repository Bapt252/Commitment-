#!/bin/bash
echo "🧪 Test de SuperSmartMatch..."

# Attendre un peu que le service soit prêt
sleep 2

# Test de santé
echo "1️⃣ Health check..."
curl -s http://localhost:5061/api/health | python3 -m json.tool 2>/dev/null || echo "Service non accessible - vérifiez qu'il est démarré"

echo -e "\n2️⃣ Liste des algorithmes..."
curl -s http://localhost:5061/api/algorithms | python3 -m json.tool 2>/dev/null || echo "Erreur récupération algorithmes"

echo -e "\n3️⃣ Test de matching..."
curl -s -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["Python", "JavaScript"],
      "annees_experience": 3
    },
    "questionnaire_data": {
      "adresse": "Paris",
      "salaire_souhaite": 45000
    },
    "job_data": [
      {
        "id": "job1",
        "titre": "Développeur Python",
        "competences": ["Python", "Django"],
        "localisation": "Paris"
      },
      {
        "id": "job2",
        "titre": "Développeur JavaScript",
        "competences": ["JavaScript", "React"],
        "localisation": "Lyon"
      }
    ],
    "algorithm": "auto",
    "limit": 5
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test matching"

echo -e "\n4️⃣ Test avec algorithme spécifique..."
curl -s -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {"competences": ["Python"]},
    "questionnaire_data": {},
    "job_data": [{"id": "test", "titre": "Test Job", "competences": ["Python"]}],
    "algorithm": "fallback"
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test fallback"

echo -e "\n✅ Tests terminés"
echo "ℹ️ Pour arrêter le service, utilisez Ctrl+C dans le terminal où il s'exécute"
