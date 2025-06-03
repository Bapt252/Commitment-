#!/bin/bash

CANDIDATE_ID=$1
JOB_ID=$2

if [ -z "$CANDIDATE_ID" ] || [ -z "$JOB_ID" ]; then
    echo "❌ Utilisation : ./test_matching.sh <candidate_id> <job_id>"
    exit 1
fi

echo "📤 Lancement du matching entre candidat $CANDIDATE_ID et offre $JOB_ID..."

RESPONSE=$(curl -s -X POST http://localhost:5052/api/v1/queue-matching \
    -H "Content-Type: application/json" \
    -d "{\"candidate_id\": $CANDIDATE_ID, \"job_id\": $JOB_ID}")

MATCH_JOB_ID=$(echo "$RESPONSE" | jq -r .job_id)

if [ "$MATCH_JOB_ID" == "null" ] || [ -z "$MATCH_JOB_ID" ]; then
    echo "❌ Erreur lors de l'envoi. Réponse : $RESPONSE"
    exit 1
fi

echo "✅ Matching lancé avec Job ID : $MATCH_JOB_ID"

for i in {1..10}; do
    echo "⌛ Vérification tentative $i..."
    RESULT=$(curl -s http://localhost:5052/api/v1/status/$MATCH_JOB_ID)
    STATUS=$(echo "$RESULT" | jq -r .status)
    
    if [[ "$STATUS" == "completed" ]]; then
        echo "✅ Résultat du matching prêt !"
        echo "$RESULT" | jq
        exit 0
    fi
    
    sleep 2
done

echo "⏳ Résultat non disponible après 20 secondes. Réessaie plus tard."