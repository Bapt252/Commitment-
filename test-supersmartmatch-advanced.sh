#!/bin/bash
echo "🧪 Test AVANCÉ de SuperSmartMatch v2.0..."
echo "🎯 Test avec temps de trajet et pondération intelligente"

# Attendre un peu que le service soit prêt
sleep 2

# Test de santé avec nouvelles fonctionnalités
echo "1️⃣ Health check v2.0..."
curl -s http://localhost:5061/api/health | python3 -m json.tool 2>/dev/null || echo "Service non accessible"

echo -e "\n2️⃣ Liste des algorithmes (avec advanced)..."
curl -s http://localhost:5061/api/algorithms | python3 -m json.tool 2>/dev/null || echo "Erreur algorithmes"

echo -e "\n3️⃣ Données de test disponibles..."
curl -s http://localhost:5061/api/test-data | python3 -m json.tool 2>/dev/null || echo "Erreur test-data"

echo -e "\n4️⃣ Test AVANCÉ - Candidat ayant quitté pour le salaire..."
curl -s -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["Python", "Django", "PostgreSQL", "React"],
      "annees_experience": 5,
      "niveau_etudes": "Master",
      "derniere_fonction": "Développeur Full Stack"
    },
    "questionnaire_data": {
      "adresse": "Paris 15ème",
      "salaire_souhaite": 55000,
      "types_contrat": ["CDI"],
      "mode_transport": "metro",
      "temps_trajet_max": 45,
      "date_disponibilite": "2025-06-01",
      "raison_changement": "salaire",
      "priorite": "equilibre",
      "objectif": "competences"
    },
    "job_data": [
      {
        "id": "job-001",
        "titre": "Développeur Python Senior",
        "entreprise": "TechCorp",
        "competences": ["Python", "Django", "PostgreSQL"],
        "localisation": "Paris 8ème",
        "type_contrat": "CDI",
        "salaire_min": 60000,
        "salaire_max": 70000,
        "experience_requise": 3,
        "date_debut_souhaitee": "2025-06-15",
        "teletravail_possible": false
      },
      {
        "id": "job-002",
        "titre": "Full Stack Developer",
        "entreprise": "StartupInc", 
        "competences": ["Python", "React", "MySQL"],
        "localisation": "Levallois-Perret",
        "type_contrat": "CDI",
        "salaire_min": 45000,
        "salaire_max": 50000,
        "experience_requise": 4,
        "date_debut_souhaitee": "2025-07-01",
        "teletravail_possible": true,
        "politique_remote": "Télétravail 2j/semaine"
      },
      {
        "id": "job-003",
        "titre": "Lead Developer",
        "entreprise": "BigCorp",
        "competences": ["Python", "Django", "AWS"],
        "localisation": "Lyon",
        "type_contrat": "CDI",
        "salaire_min": 65000,
        "salaire_max": 75000,
        "experience_requise": 6,
        "date_debut_souhaitee": "2025-06-01"
      }
    ],
    "algorithm": "advanced",
    "limit": 10
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test avancé"

echo -e "\n5️⃣ Test AVANCÉ - Candidat privilégiant localisation..."
curl -s -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["JavaScript", "React", "Node.js"],
      "annees_experience": 3
    },
    "questionnaire_data": {
      "adresse": "Paris 3ème",
      "salaire_souhaite": 45000,
      "types_contrat": ["CDI", "CDD"],
      "mode_transport": "pied",
      "temps_trajet_max": 20,
      "raison_changement": "localisation",
      "priorite": "equilibre",
      "objectif": "equilibre"
    },
    "job_data": [
      {
        "id": "job-proche",
        "titre": "Dev Frontend",
        "competences": ["JavaScript", "React"],
        "localisation": "Paris 3ème",
        "type_contrat": "CDI",
        "salaire_min": 42000,
        "salaire_max": 48000
      },
      {
        "id": "job-loin",
        "titre": "Senior React Dev",
        "competences": ["React", "Node.js"],
        "localisation": "Boulogne-Billancourt", 
        "type_contrat": "CDI",
        "salaire_min": 50000,
        "salaire_max": 60000
      }
    ],
    "algorithm": "advanced"
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test localisation"

echo -e "\n6️⃣ Test modes de transport..."
curl -s -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {"competences": ["Java"]},
    "questionnaire_data": {
      "adresse": "Paris 1er",
      "mode_transport": "voiture",
      "temps_trajet_max": 60
    },
    "job_data": [
      {
        "id": "job-voiture-ok",
        "competences": ["Java"],
        "localisation": "Paris 16ème",
        "type_contrat": "CDI"
      }
    ],
    "algorithm": "advanced"
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test transport"

echo -e "\n7️⃣ Test avec algorithme auto (doit choisir advanced)..."
curl -s -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {"competences": ["Python"]},
    "questionnaire_data": {"adresse": "Paris"},
    "job_data": [{"id": "test", "competences": ["Python"], "localisation": "Paris"}],
    "algorithm": "auto"
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test auto"

echo -e "\n✅ Tests avancés terminés"
echo "🎯 Vérifiez les nouvelles fonctionnalités:"
echo "   - travel_time scores"
echo "   - matching_explanations" 
echo "   - travel_info détaillé"
echo "   - Pondération intelligente selon questionnaire"
echo ""
echo "ℹ️ Pour tester à grande échelle, utilisez l'endpoint /api/test-data"
