#!/bin/bash

# Script de test du service de personnalisation
# Auteur: Claude
# Date: Mai 2025

# Couleurs pour les logs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Test du service de personnalisation ===${NC}"

# Vérification de la santé du service
echo -e "${YELLOW}[TEST] Vérification de la santé du service...${NC}"
response=$(curl -s http://localhost:5060/health)

if [[ $response == *"status"*"ok"* ]]; then
  echo -e "${GREEN}[SUCCESS] Le service est en bonne santé !${NC}"
else
  echo -e "${RED}[ERROR] Le service n'est pas accessible ou n'est pas en bonne santé.${NC}"
  echo "Réponse: $response"
  exit 1
fi

# Test de personnalisation des poids
echo -e "${YELLOW}[TEST] Test de la personnalisation des poids de matching...${NC}"
response=$(curl -s -X POST http://localhost:5060/api/v1/personalize/matching \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "job_id": 456,
    "original_weights": {
      "skills": 0.4,
      "experience": 0.3,
      "education": 0.2,
      "certifications": 0.1
    }
  }')

echo "Réponse: $response"

if [[ $response == *"success"* ]]; then
  echo -e "${GREEN}[SUCCESS] Test de personnalisation des poids réussi !${NC}"
else
  echo -e "${RED}[ERROR] Échec du test de personnalisation des poids.${NC}"
fi

# Test d'enregistrement de feedback
echo -e "${YELLOW}[TEST] Test d'enregistrement de feedback...${NC}"
response=$(curl -s -X POST http://localhost:5060/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "job_id": 456,
    "action": "like",
    "context": {
      "source": "test",
      "position": 1
    }
  }')

echo "Réponse: $response"

if [[ $response == *"success"* ]]; then
  echo -e "${GREEN}[SUCCESS] Test d'enregistrement de feedback réussi !${NC}"
else
  echo -e "${RED}[ERROR] Échec du test d'enregistrement de feedback.${NC}"
fi

# Test de récupération des préférences
echo -e "${YELLOW}[TEST] Test de récupération des préférences utilisateur...${NC}"
response=$(curl -s http://localhost:5060/api/v1/preferences/test-user-123)

echo "Réponse: $response"

if [[ $response == *"success"* ]]; then
  echo -e "${GREEN}[SUCCESS] Test de récupération des préférences réussi !${NC}"
else
  echo -e "${RED}[ERROR] Échec du test de récupération des préférences.${NC}"
fi

# Test de personnalisation des résultats de recherche
echo -e "${YELLOW}[TEST] Test de personnalisation des résultats de recherche...${NC}"
response=$(curl -s -X POST http://localhost:5060/api/v1/personalize/job-search \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test-user-123",
    "results": [
      {
        "job_id": 123,
        "score": 0.85,
        "title": "Développeur Full Stack",
        "category": "Development"
      },
      {
        "job_id": 456,
        "score": 0.75,
        "title": "Data Scientist",
        "category": "Data Science"
      }
    ],
    "search_query": "développeur",
    "context": {
      "source": "test"
    }
  }')

echo "Réponse: $response"

if [[ $response == *"success"* ]]; then
  echo -e "${GREEN}[SUCCESS] Test de personnalisation des résultats de recherche réussi !${NC}"
else
  echo -e "${RED}[ERROR] Échec du test de personnalisation des résultats de recherche.${NC}"
fi

echo -e "${BLUE}=== Tests terminés ===${NC}"
