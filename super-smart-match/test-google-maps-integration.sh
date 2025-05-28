#!/bin/bash

# 🧪 Script de test pour SuperSmartMatch v2.2 avec Google Maps
# Usage: ./test-google-maps-integration.sh

echo "🧪 === TEST SUPERSMARTMATCH v2.2 AVEC GOOGLE MAPS ==="
echo

# Vérifier que le serveur SuperSmartMatch est démarré
if ! curl -s http://localhost:5061/api/health > /dev/null; then
    echo "❌ Erreur: SuperSmartMatch n'est pas démarré sur le port 5061"
    echo "   Démarrez d'abord le serveur: cd super-smart-match && python app.py"
    exit 1
fi

echo "✅ SuperSmartMatch v2.2 détecté sur le port 5061"
echo

# Test 1: Vérifier les informations de l'algorithme
echo "📊 Test 1: Informations de l'algorithme"
curl -s http://localhost:5061/api/algorithms | jq '.supersmartmatch.google_maps_config' 2>/dev/null || echo "⚠️ jq non installé - réponse brute:"
echo

# Test 2: Matching avec priorité PROXIMITÉ élevée + transport en commun
echo "🚇 Test 2: Candidat transport en commun (Paris 15ème → Paris 2ème)"

curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["Python", "React", "Node.js"],
      "annees_experience": 5,
      "adresse": "Paris 15ème",
      "salaire_souhaite": 55000
    },
    "questionnaire_data": {
      "priorites_candidat": {
        "proximite": 10,
        "evolution": 6,
        "remuneration": 7,
        "flexibilite": 5
      },
      "transport_preferences": {
        "transport_prefere": "transit",
        "heure_depart_travail": "08:30"
      }
    },
    "job_data": [{
      "id": "job-transit-test",
      "titre": "Développeur Full Stack",
      "localisation": "Paris 2ème",
      "salaire": "50-60K€",
      "competences": ["Python", "React"]
    }],
    "algorithm": "supersmartmatch",
    "limit": 1
  }' \
  -s | jq '.results[0].scores_detailles.proximite' 2>/dev/null || echo "Réponse reçue (jq non disponible)"

echo
echo "---"
echo

# Test 3: Matching avec priorité PROXIMITÉ élevée + voiture
echo "🚗 Test 3: Candidat voiture (Boulogne → La Défense)"

curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["Java", "Spring", "Angular"],
      "annees_experience": 3,
      "adresse": "Boulogne-Billancourt",
      "salaire_souhaite": 48000
    },
    "questionnaire_data": {
      "priorites_candidat": {
        "proximite": 9,
        "evolution": 8,
        "remuneration": 6,
        "flexibilite": 4
      },
      "transport_preferences": {
        "transport_prefere": "driving",
        "heure_depart_travail": "09:00"
      }
    },
    "job_data": [{
      "id": "job-driving-test",
      "titre": "Développeur Backend",
      "localisation": "La Défense",
      "salaire": "45-55K€",
      "competences": ["Java", "Spring"]
    }],
    "algorithm": "supersmartmatch",
    "limit": 1
  }' \
  -s | jq '.results[0].scores_detailles.proximite.travel_info' 2>/dev/null || echo "Réponse reçue (détails dans les logs du serveur)"

echo
echo "---"
echo

# Test 4: Comparaison télétravail vs présentiel
echo "🏠 Test 4: Poste télétravail partiel"

curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["Vue.js", "Laravel", "MySQL"],
      "annees_experience": 4,
      "adresse": "Lyon 3ème",
      "salaire_souhaite": 50000
    },
    "questionnaire_data": {
      "priorites_candidat": {
        "proximite": 8,
        "flexibilite": 9,
        "evolution": 6,
        "remuneration": 7
      },
      "transport_preferences": {
        "transport_prefere": "bicycling"
      },
      "flexibilite_attendue": {
        "teletravail": "partiel",
        "horaires_flexibles": true
      }
    },
    "job_data": [{
      "id": "job-remote-test",
      "titre": "Développeur Frontend",
      "localisation": "Lyon 6ème", 
      "salaire": "48-55K€",
      "politique_remote": "télétravail partiel 2j/semaine",
      "horaires_flexibles": true,
      "competences": ["Vue.js", "Laravel"]
    }],
    "algorithm": "supersmartmatch",
    "limit": 1
  }' \
  -s | jq '.results[0] | {score: .matching_score_entreprise, proximite: .scores_detailles.proximite.pourcentage, flexibilite: .scores_detailles.flexibilite.pourcentage}' 2>/dev/null || echo "Réponse reçue"

echo
echo "---"
echo

# Test 5: Test de fallback (adresses inexistantes)
echo "❓ Test 5: Test fallback avec adresses inexistantes"

curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["Python"],
      "adresse": "Ville-Inexistante-123"
    },
    "questionnaire_data": {
      "priorites_candidat": {
        "proximite": 8
      }
    },
    "job_data": [{
      "id": "job-fallback-test",
      "titre": "Test Fallback",
      "localisation": "Autre-Ville-Inexistante-456"
    }],
    "algorithm": "supersmartmatch",
    "limit": 1
  }' \
  -s | jq '.results[0].scores_detailles.proximite.details' 2>/dev/null || echo "Test fallback terminé"

echo
echo "---"
echo

# Test 6: Vérification du cache
echo "🗄️ Test 6: Test du cache (même requête répétée)"

echo "Première requête (création cache):"
time curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "adresse": "Marseille"
    },
    "job_data": [{
      "id": "cache-test",
      "localisation": "Nice"
    }],
    "algorithm": "supersmartmatch",
    "limit": 1
  }' \
  -s > /dev/null

echo "Deuxième requête (utilisation cache):"
time curl -X POST http://localhost:5061/api/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "adresse": "Marseille"
    },
    "job_data": [{
      "id": "cache-test",
      "localisation": "Nice"
    }],
    "algorithm": "supersmartmatch",
    "limit": 1
  }' \
  -s > /dev/null

echo "✅ La deuxième requête devrait être plus rapide (cache)"
echo

# Résumé des tests
echo "📋 === RÉSUMÉ DES TESTS ==="
echo
echo "✅ Tests SuperSmartMatch v2.2 avec Google Maps terminés"
echo
echo "🔍 Pour voir les détails des réponses:"
echo "   - Consultez les logs du serveur SuperSmartMatch"
echo "   - Installez jq pour un formatage JSON: sudo apt install jq"
echo
echo "🗺️ Fonctionnalités testées:"
echo "   - Calcul temps de trajet en transport en commun"
echo "   - Calcul temps de trajet en voiture"  
echo "   - Gestion télétravail partiel"
echo "   - Fallback automatique si adresses invalides"
echo "   - Cache des requêtes Google Maps"
echo "   - Pondération dynamique selon priorités candidat"
echo
echo "📊 Pour analyser les performances:"
echo "   - Temps de réponse (avec vs sans cache)"
echo "   - Précision des temps de trajet vs estimation"
echo "   - Impact sur les scores de matching"
echo

if [[ "${GOOGLE_MAPS_API_KEY}" ]]; then
    echo "✅ Variable GOOGLE_MAPS_API_KEY détectée"
else
    echo "⚠️ Variable GOOGLE_MAPS_API_KEY non détectée"
    echo "   Export: export GOOGLE_MAPS_API_KEY='votre_cle'"
fi

echo
echo "🚀 SuperSmartMatch v2.2 avec Google Maps testé!"
