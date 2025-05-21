#!/bin/bash

# Script de test pour le service de personnalisation

echo "========================================================"
echo "Test du service de personnalisation pour Commitment"
echo "========================================================"

# Configuration
API_URL="http://localhost:5060"
MATCHING_URL="http://localhost:5052"
USER_ID="test_user_$(date +%s)"
echo "Utilisation de l'ID utilisateur: $USER_ID"

# 1. Vérifier que le service est en marche
echo "\n1. Vérification de la santé du service..."
HEALTH_RESPONSE=$(curl -s $API_URL/health)
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo "✅ Service en bonne santé!"
else
    echo "❌ Le service ne répond pas correctement. Réponse: $HEALTH_RESPONSE"
    exit 1
fi

# 2. Création des préférences utilisateur
echo "\n2. Création des préférences utilisateur..."
PREF_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/preferences" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"preferences\": {
      \"job_type\": [\"CDI\", \"Freelance\"],
      \"location\": [\"Paris\", \"Remote\"],
      \"skills\": [\"Python\", \"JavaScript\", \"React\"],
      \"company_size\": [\"Startup\", \"PME\"],
      \"weights\": {
        \"skills\": 0.6,
        \"experience\": 0.2,
        \"education\": 0.1,
        \"certifications\": 0.1
      }
    }
  }")

if [[ $PREF_RESPONSE == *"success"* ]]; then
    echo "✅ Préférences créées avec succès!"
else
    echo "❌ Échec de la création des préférences. Réponse: $PREF_RESPONSE"
    exit 1
fi

# 3. Test de la personnalisation des résultats de recherche
echo "\n3. Test de la personnalisation des résultats de recherche..."
SEARCH_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/personalize/job-search" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"results\": [
      {\"job_id\": 1, \"score\": 0.75, \"title\": \"Développeur Python\", \"location\": \"Paris\", \"company\": \"Tech Corp\", \"skills\": [\"Python\", \"Django\", \"SQL\"]},
      {\"job_id\": 2, \"score\": 0.82, \"title\": \"Développeur Frontend\", \"location\": \"Lyon\", \"company\": \"Web Agency\", \"skills\": [\"JavaScript\", \"React\", \"CSS\"]},
      {\"job_id\": 3, \"score\": 0.68, \"title\": \"Data Scientist\", \"location\": \"Remote\", \"company\": \"AI Startup\", \"skills\": [\"Python\", \"SQL\", \"Machine Learning\"]}
    ],
    \"search_query\": \"développeur python\",
    \"context\": {\"location\": \"Paris\"}
  }")

echo "Résultats personnalisés: $SEARCH_RESPONSE"

if [[ $SEARCH_RESPONSE == *"personalized":true* ]]; then
    echo "✅ Personnalisation des résultats réussie!"
else
    echo "❌ Échec de la personnalisation des résultats."
fi

# 4. Test de la personnalisation des poids de matching
echo "\n4. Test de la personnalisation des poids de matching..."
WEIGHTS_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/personalize/matching" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"job_id\": 1,
    \"candidate_id\": 101,
    \"original_weights\": {
      \"skills\": 0.4,
      \"experience\": 0.3,
      \"education\": 0.2,
      \"certifications\": 0.1
    }
  }")

echo "Poids personnalisés: $WEIGHTS_RESPONSE"

if [[ $WEIGHTS_RESPONSE == *"personalized":true* ]]; then
    echo "✅ Personnalisation des poids réussie!"
else
    echo "❌ Échec de la personnalisation des poids."
fi

# 5. Test d'enregistrement de feedback
echo "\n5. Test d'enregistrement de feedback..."
FEEDBACK_RESPONSE=$(curl -s -X POST "$MATCHING_URL/api/v1/record-feedback" \
  -G \
  --data-urlencode "user_id=$USER_ID" \
  --data-urlencode "job_id=1" \
  --data-urlencode "action=like" \
  -H "Content-Type: application/json" \
  -d '{"source": "search_results", "position": 2}')

echo "Réponse de feedback: $FEEDBACK_RESPONSE"

if [[ $FEEDBACK_RESPONSE == *"success"* ]]; then
    echo "✅ Enregistrement du feedback réussi!"
else
    echo "❌ Échec de l'enregistrement du feedback."
fi

# 6. Test de l'intégration avec le service de matching (si disponible)
echo "\n6. Test de l'intégration avec le service de matching..."
if curl -s "$MATCHING_URL/health" > /dev/null; then
    MATCH_RESPONSE=$(curl -s -X POST "$MATCHING_URL/api/v1/queue-matching" \
      -H "Content-Type: application/json" \
      -d "{
        \"candidate_id\": 101,
        \"job_id\": 1,
        \"webhook_url\": \"http://example.com/webhook\"
      }" \
      -G --data-urlencode "user_id=$USER_ID")
    
    echo "Réponse de matching: $MATCH_RESPONSE"
    JOB_ID=$(echo $MATCH_RESPONSE | grep -o '"job_id":"[^"]*"' | sed 's/"job_id":"\([^"]*\)"/\1/')
    
    if [[ ! -z "$JOB_ID" ]]; then
        echo "✅ Requête de matching envoyée avec succès! Job ID: $JOB_ID"
        echo "Note: Le résultat du matching sera disponible après traitement. Vous pouvez le vérifier avec:"
        echo "curl $MATCHING_URL/api/v1/result/$JOB_ID"
    else
        echo "❌ Échec de la requête de matching."
    fi
else
    echo "⚠️ Service de matching non disponible, test d'intégration ignoré."
fi

echo "\n========================================================"
echo "Tests terminés pour l'utilisateur $USER_ID"
echo "========================================================"
