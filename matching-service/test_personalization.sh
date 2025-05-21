#!/bin/bash

# Script de test pour la fonctionnalité de personnalisation intégrée au service de matching
# Ce script permet de tester l'intégration entre le service de matching et le service de personnalisation

set -e  # Exit on any error

# Configuration
MATCHING_API="http://localhost:5052"
PERSONALIZATION_API="http://localhost:5060"
AUTH_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjEyMyIsInVzZXJfdHlwZSI6ImNhbmRpZGF0ZSJ9.3Zb8xDxRYGkMcwG9lBh5Zz5-TXcUG6NlRXJNGK1BZLA"  # Token de test

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Fonction d'aide pour les requêtes HTTP
function call_api() {
    local method=$1
    local url=$2
    local data=$3
    
    if [ -n "$data" ]; then
        curl -s -X $method -H "Content-Type: application/json" -H "Authorization: Bearer $AUTH_TOKEN" -d "$data" $url
    else
        curl -s -X $method -H "Content-Type: application/json" -H "Authorization: Bearer $AUTH_TOKEN" $url
    fi
}

# Vérifier si les services sont en fonctionnement
echo -e "${BLUE}Vérification de l'état des services...${NC}"

# Test de santé du service de matching
matching_health=$(call_api GET "$MATCHING_API/health")
if [[ $matching_health == *"ok"* ]]; then
    echo -e "${GREEN}Service de matching opérationnel${NC}"
else
    echo -e "${RED}Service de matching non disponible${NC}"
    exit 1
fi

# Test de santé du service de personnalisation
personalization_health=$(call_api GET "$PERSONALIZATION_API/health")
if [[ $personalization_health == *"ok"* ]]; then
    echo -e "${GREEN}Service de personnalisation opérationnel${NC}"
else
    echo -e "${RED}Service de personnalisation non disponible${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}==== Test 1: Calcul de matching sans personnalisation ====${NC}"

# Calculer un score de matching sans personnalisation
result=$(call_api POST "$MATCHING_API/matches/calculate" '{
    "job_id": 1,
    "candidate_id": 2,
    "personalized": false
}')

echo "Résultat sans personnalisation:"
echo $result | jq .

echo ""
echo -e "${BLUE}==== Test 2: Calcul de matching avec personnalisation ====${NC}"

# Calculer un score de matching avec personnalisation
result_personalized=$(call_api POST "$MATCHING_API/matches/calculate" '{
    "job_id": 1,
    "candidate_id": 2,
    "personalized": true
}')

echo "Résultat avec personnalisation:"
echo $result_personalized | jq .

# Vérifier si les résultats sont différents
score1=$(echo $result | jq -r '.score')
score2=$(echo $result_personalized | jq -r '.score')

if [[ "$score1" != "$score2" ]]; then
    echo -e "${GREEN}Test réussi! Les scores sont différents grâce à la personnalisation.${NC}"
else
    echo -e "${YELLOW}Les scores sont identiques. La personnalisation pourrait ne pas être active.${NC}"
fi

echo ""
echo -e "${BLUE}==== Test 3: Recherche de candidats pour un job ====${NC}"

# Obtenir des candidats pour un job sans personnalisation
candidates=$(call_api POST "$MATCHING_API/matches/calculate" '{
    "job_id": 1,
    "personalized": false
}')

echo "Premiers candidats sans personnalisation:"
echo $candidates | jq '.matches[0:2]'

# Obtenir des candidats pour un job avec personnalisation
candidates_personalized=$(call_api POST "$MATCHING_API/matches/calculate" '{
    "job_id": 1,
    "personalized": true
}')

echo "Premiers candidats avec personnalisation:"
echo $candidates_personalized | jq '.matches[0:2]'

echo ""
echo -e "${BLUE}==== Test 4: Enregistrement d'un feedback pour améliorer les recommandations ====${NC}"

# Simuler un clic sur un match (feedback)
feedback_response=$(call_api POST "$PERSONALIZATION_API/api/v1/feedback" '{
    "user_id": "123",
    "job_id": 1,
    "candidate_id": 2,
    "action": "interested",
    "context": {
        "source": "search_results",
        "position": 1
    }
}')

if [[ $feedback_response == *"success"* ]]; then
    echo -e "${GREEN}Feedback enregistré avec succès${NC}"
else
    echo -e "${RED}Erreur lors de l'enregistrement du feedback${NC}"
    echo $feedback_response
fi

echo ""
echo -e "${BLUE}==== Test 5: Mise à jour du statut d'un match ====${NC}"

# Simuler une mise à jour de statut
status_update=$(call_api PUT "$MATCHING_API/matches/1/status" '{
    "status": "interested"
}')

echo "Résultat de la mise à jour du statut:"
echo $status_update | jq .

echo ""
echo -e "${GREEN}Tests terminés.${NC}"
echo "Pour une démonstration complète, vous devriez:"
echo "1. Créer plusieurs utilisateurs et leur faire interagir avec des offres"
echo "2. Observer comment les recommandations évoluent avec le temps"
echo "3. Vérifier les données dans Redis et dans la base de données"
