#!/bin/bash

CV_PATH="./cv.pdf"

if [ ! -f "$CV_PATH" ]; then
    echo "❌ Fichier $CV_PATH introuvable. Place un fichier 'cv.pdf' dans le dossier courant."
    exit 1
fi

echo "📤 Envoi du CV à l'API de parsing..."

RESPONSE=$(curl -s -X POST http://localhost:5051/api/queue \
    -F "file=@$CV_PATH" \
    -F "priority=premium")

JOB_ID=$(echo "$RESPONSE" | jq -r .job_id)

if [ "$JOB_ID" == "null" ] || [ -z "$JOB_ID" ]; then
    echo "❌ Erreur lors de l'envoi. Réponse : $RESPONSE"
    exit 1
fi

echo "✅ Job envoyé avec ID : $JOB_ID"

echo "⏳ Attente du résultat..."

for i in {1..10}; do
    echo "⌛ Vérification tentative $i..."
    RESULT=$(curl -s http://localhost:5051/api/result/$JOB_ID)
    STATUS=$(echo "$RESULT" | jq -r .status)
    
    if [[ "$STATUS" == "completed" ]]; then
        echo "✅ Résultat prêt !"
        echo "$RESULT" | jq
        exit 0
    fi
    
    sleep 2
done

echo "⏳ Résultat non disponible après 20 secondes. Réessaie plus tard."