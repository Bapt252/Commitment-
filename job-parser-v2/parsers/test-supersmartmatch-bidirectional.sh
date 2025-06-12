#!/bin/bash
echo "🏢 Test BIDIRECTIONNEL SuperSmartMatch v2.1..."
echo "🎯 Test Entreprise → Candidats avec pondération intelligente"

# Attendre un peu que le service soit prêt
sleep 2

# Test de santé bidirectionnel
echo "1️⃣ Health check bidirectionnel..."
curl -s http://localhost:5061/api/health | python3 -m json.tool 2>/dev/null || echo "Service non accessible"

echo -e "\n2️⃣ Algorithmes candidat ET entreprise..."
curl -s http://localhost:5061/api/algorithms | python3 -m json.tool 2>/dev/null || echo "Erreur algorithmes"

echo -e "\n3️⃣ Données de test bidirectionnelles..."
curl -s http://localhost:5061/api/test-data | python3 -m json.tool 2>/dev/null || echo "Erreur test-data"

echo -e "\n4️⃣ TEST ENTREPRISE → CANDIDATS - Startup cherche Lead avec évolution..."
curl -s -X POST http://localhost:5061/api/match-candidates \
  -H "Content-Type: application/json" \
  -d '{
    "job_data": {
      "id": "startup-lead-001",
      "titre": "Lead Developer",
      "entreprise": "TechStartup",
      "competences": ["Python", "Django", "React", "AWS"],
      "localisation": "Paris 2ème",
      "type_contrat": "CDI",
      "salaire_min": 65000,
      "salaire_max": 80000,
      "experience_requise": 5,
      "teletravail_possible": true,
      "type_entreprise": "startup",
      "niveau_poste": "senior",
      "description": "Lead une équipe de 4 développeurs, architecture technique, évolution vers CTO possible"
    },
    "candidates_data": [
      {
        "candidate_id": "cand-001",
        "cv_data": {
          "nom": "Marie Dupont",
          "competences": ["Python", "Django", "PostgreSQL", "AWS"],
          "annees_experience": 6,
          "niveau_etudes": "Master",
          "derniere_fonction": "Senior Developer"
        },
        "questionnaire_data": {
          "adresse": "Paris 11ème",
          "salaire_souhaite": 70000,
          "types_contrat": ["CDI"],
          "mode_transport": "metro",
          "temps_trajet_max": 60,
          "objectif": "evolution",
          "niveau_ambition": "élevé",
          "mobilite": "moyen",
          "accepte_teletravail": true
        }
      },
      {
        "candidate_id": "cand-002", 
        "cv_data": {
          "nom": "Jean Martin",
          "competences": ["JavaScript", "React", "Node.js"],
          "annees_experience": 3,
          "niveau_etudes": "Bachelor",
          "derniere_fonction": "Frontend Developer"
        },
        "questionnaire_data": {
          "adresse": "Boulogne-Billancourt",
          "salaire_souhaite": 50000,
          "types_contrat": ["CDI", "CDD"],
          "mode_transport": "voiture",
          "objectif": "stabilite",
          "niveau_ambition": "moyen",
          "mobilite": "faible"
        }
      },
      {
        "candidate_id": "cand-003",
        "cv_data": {
          "nom": "Sarah Cohen",
          "competences": ["Python", "Django", "React", "Docker"],
          "annees_experience": 4,
          "niveau_etudes": "Master",
          "derniere_fonction": "Full Stack Developer"
        },
        "questionnaire_data": {
          "adresse": "Paris 9ème",
          "salaire_souhaite": 65000,
          "types_contrat": ["CDI"],
          "mode_transport": "metro",
          "objectif": "evolution",
          "niveau_ambition": "élevé",
          "mobilite": "élevé",
          "accepte_teletravail": true
        }
      }
    ],
    "algorithm": "auto",
    "limit": 10
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test entreprise"

echo -e "\n5️⃣ TEST ENTREPRISE → CANDIDATS - Grande entreprise cherche profil stable..."
curl -s -X POST http://localhost:5061/api/match-candidates \
  -H "Content-Type: application/json" \
  -d '{
    "job_data": {
      "id": "corp-dev-001",
      "titre": "Développeur Senior",
      "entreprise": "BigCorp",
      "competences": ["Java", "Spring", "MySQL"],
      "localisation": "La Défense",
      "type_contrat": "CDI",
      "salaire_min": 55000,
      "salaire_max": 65000,
      "experience_requise": 5,
      "teletravail_possible": false,
      "type_entreprise": "grande_entreprise",
      "niveau_poste": "senior",
      "description": "Développement applications métier, environnement stable, processus établis"
    },
    "candidates_data": [
      {
        "candidate_id": "stable-001",
        "cv_data": {
          "nom": "Pierre Durand",
          "competences": ["Java", "Spring", "MySQL", "Oracle"],
          "annees_experience": 8,
          "niveau_etudes": "Master"
        },
        "questionnaire_data": {
          "adresse": "Neuilly-sur-Seine",
          "salaire_souhaite": 60000,
          "types_contrat": ["CDI"],
          "mode_transport": "voiture",
          "objectif": "stabilite",
          "niveau_ambition": "moyen",
          "mobilite": "faible"
        }
      },
      {
        "candidate_id": "startup-lover",
        "cv_data": {
          "nom": "Alex Startup",
          "competences": ["Python", "Django", "Node.js"],
          "annees_experience": 4,
          "niveau_etudes": "Bachelor"
        },
        "questionnaire_data": {
          "adresse": "Paris 10ème",
          "salaire_souhaite": 55000,
          "types_contrat": ["CDI", "CDD", "FREELANCE"],
          "mode_transport": "metro",
          "objectif": "innovation",
          "niveau_ambition": "élevé",
          "mobilite": "élevé"
        }
      }
    ],
    "algorithm": "reverse_advanced"
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test corp"

echo -e "\n6️⃣ TEST CANDIDAT → JOBS (mode classique pour comparaison)..."
curl -s -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {"competences": ["Python", "Django"], "annees_experience": 5},
    "questionnaire_data": {"adresse": "Paris", "objectif": "evolution"},
    "job_data": [
      {"id": "job1", "competences": ["Python"], "type_contrat": "CDI"},
      {"id": "job2", "competences": ["Django"], "type_contrat": "CDD"}
    ],
    "algorithm": "advanced"
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test candidat"

echo -e "\n7️⃣ Test algorithme auto bidirectionnel..."
curl -s -X POST http://localhost:5061/api/match-candidates \
  -H "Content-Type: application/json" \
  -d '{
    "job_data": {
      "titre": "Développeur Python",
      "competences": ["Python"],
      "type_entreprise": "startup"
    },
    "candidates_data": [
      {
        "candidate_id": "auto-test",
        "cv_data": {"competences": ["Python"], "annees_experience": 3},
        "questionnaire_data": {"objectif": "evolution"}
      }
    ],
    "algorithm": "auto"
  }' | python3 -m json.tool 2>/dev/null || echo "Erreur test auto"

echo -e "\n✅ Tests bidirectionnels terminés"
echo "🎯 Vérifiez les nouvelles fonctionnalités ENTREPRISE:"
echo "   - matching_mode: company_to_candidates"
echo "   - candidate_id, candidate_name dans results"
echo "   - career_goals et adaptability scores"
echo "   - Pondération intelligente selon type poste"
echo "   - candidate_info avec résumé pour RH"
echo ""
echo "ℹ️ SuperSmartMatch est maintenant BIDIRECTIONNEL !"
echo "   📊 /api/match = Candidat → Jobs"
echo "   🏢 /api/match-candidates = Entreprise → Candidats"
