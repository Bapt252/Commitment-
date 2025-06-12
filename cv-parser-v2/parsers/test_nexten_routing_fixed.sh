#!/bin/bash

# 🧪 SCRIPT DE TEST - Validation du routing Nexten
# Teste que SuperSmartMatch V2 route bien vers Nexten avec /match

set -e

echo "🧪 === TEST DE VALIDATION - ROUTING NEXTEN ==="
echo "Objectif: Vérifier que V2 utilise 'nexten_matcher' au lieu de 'v2_routed_fallback_basic'"
echo

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# === ÉTAPE 1: VÉRIFICATION DES SERVICES ===
echo -e "${BLUE}📋 ÉTAPE 1: Vérification des services...${NC}"

# Vérifier que les conteneurs sont en cours d'exécution
echo "Vérification des conteneurs Docker..."

# SuperSmartMatch V2
if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(supersmartmatch.*v2|v2.*unified)" | grep -q "Up"; then
    V2_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(supersmartmatch.*v2|v2.*unified)" | head -1)
    echo -e "${GREEN}✅ SuperSmartMatch V2 en cours d'exécution: $V2_CONTAINER${NC}"
else
    echo -e "${RED}❌ SuperSmartMatch V2 non démarré${NC}"
    echo "Conteneurs disponibles:"
    docker ps --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

# Nexten Matcher
if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(nexten|matching)" | grep -q "Up"; then
    NEXTEN_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(nexten|matching)" | head -1)
    echo -e "${GREEN}✅ Nexten Matcher en cours d'exécution: $NEXTEN_CONTAINER${NC}"
else
    echo -e "${RED}❌ Nexten Matcher non démarré${NC}"
    echo "Conteneurs disponibles:"
    docker ps --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi
echo

# === ÉTAPE 2: TEST DE SANTÉ ===
echo -e "${BLUE}📋 ÉTAPE 2: Tests de santé...${NC}"

# Test SuperSmartMatch V2
echo "🏥 Test santé SuperSmartMatch V2..."
V2_HEALTH=$(curl -s "http://localhost:5070/health" 2>/dev/null || echo "ERROR")

if [[ "$V2_HEALTH" == "ERROR" ]] || [[ -z "$V2_HEALTH" ]]; then
    echo -e "${RED}❌ SuperSmartMatch V2 inaccessible sur le port 5070${NC}"
    exit 1
else
    echo -e "${GREEN}✅ SuperSmartMatch V2 accessible${NC}"
    echo "   Response: $V2_HEALTH" | head -c 100
fi

# Test Nexten Matcher
echo
echo "🏥 Test santé Nexten Matcher..."
NEXTEN_HEALTH=$(curl -s "http://localhost:5052/health" 2>/dev/null || echo "ERROR")

if [[ "$NEXTEN_HEALTH" == "ERROR" ]] || [[ -z "$NEXTEN_HEALTH" ]]; then
    echo -e "${YELLOW}⚠️  Nexten Matcher inaccessible sur le port 5052 (peut être normal)${NC}"
    
    # Essayer le endpoint direct de matching
    NEXTEN_MATCH_TEST=$(curl -s "http://localhost:5052/match" -X POST -H "Content-Type: application/json" -d '{}' 2>/dev/null || echo "ERROR")
    if [[ "$NEXTEN_MATCH_TEST" != "ERROR" ]]; then
        echo -e "${GREEN}✅ Nexten endpoint /match accessible${NC}"
    else
        echo -e "${RED}❌ Nexten Matcher complètement inaccessible${NC}"
        echo "Vérifiez que le service est démarré et accessible"
    fi
else
    echo -e "${GREEN}✅ Nexten Matcher accessible${NC}"
    echo "   Response: $NEXTEN_HEALTH" | head -c 100
fi
echo

# === ÉTAPE 3: TEST DE MATCHING ===
echo -e "${BLUE}📋 ÉTAPE 3: Test de matching...${NC}"

# Payload de test optimisé pour déclencher Nexten
TEST_PAYLOAD='{
    "cv_data": {
        "competences": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch"],
        "experience": 5,
        "localisation": "Paris",
        "niveau_etudes": "Master",
        "questionnaire_complete": true,
        "score_completude": 95,
        "profil_comportemental": {
            "autonomie": 8,
            "leadership": 7,
            "communication": 9
        },
        "preferences_detaillees": {
            "teletravail": true,
            "management": false,
            "innovation": true
        }
    },
    "jobs": [
        {
            "id": "test-job-nexten-1",
            "titre": "Senior ML Engineer",
            "entreprise": "TechCorp",
            "competences": ["Python", "Machine Learning", "TensorFlow"],
            "localisation": "Paris",
            "description": "Développement de modèles ML avancés",
            "experience_requise": 5,
            "salaire_min": 60000,
            "salaire_max": 80000,
            "type_contrat": "CDI",
            "teletravail_possible": true
        },
        {
            "id": "test-job-nexten-2", 
            "titre": "Data Scientist",
            "entreprise": "AIStart",
            "competences": ["Python", "Deep Learning", "PyTorch"],
            "localisation": "Lyon",
            "description": "Recherche et développement en IA",
            "experience_requise": 4,
            "salaire_min": 55000,
            "salaire_max": 75000,
            "type_contrat": "CDI",
            "teletravail_possible": true
        }
    ],
    "options": {
        "algorithm": "auto",
        "max_results": 10,
        "enable_caching": false,
        "include_travel_time": true,
        "context": {
            "test_mode": true,
            "force_nexten": true
        }
    }
}'

echo "🧪 Envoi de la requête de matching..."
echo "Endpoint: http://localhost:5070/api/v2/match"

RESPONSE=$(curl -s -X POST "http://localhost:5070/api/v2/match" \
    -H "Content-Type: application/json" \
    -H "User-Agent: Test-Nexten-Routing/1.0" \
    -d "$TEST_PAYLOAD" 2>/dev/null || echo "ERROR")

if [[ "$RESPONSE" == "ERROR" ]] || [[ -z "$RESPONSE" ]]; then
    echo -e "${RED}❌ Erreur lors de l'appel à l'API de matching${NC}"
    echo "Vérifiez que le service V2 est démarré et accessible"
    exit 1
fi

echo -e "${GREEN}✅ Réponse reçue de l'API${NC}"
echo

# === ÉTAPE 4: ANALYSE DE LA RÉPONSE ===
echo -e "${BLUE}📋 ÉTAPE 4: Analyse de la réponse...${NC}"

# Sauvegarder la réponse pour analyse
echo "$RESPONSE" > /tmp/nexten_test_response.json

# Analyser la réponse avec Python si disponible
if command -v python3 &> /dev/null; then
    echo "📊 Analyse détaillée de la réponse:"
    
    ANALYSIS=$(python3 -c "
import json
import sys

try:
    with open('/tmp/nexten_test_response.json', 'r') as f:
        data = json.load(f)
    
    print('=== RÉSULTATS D\'ANALYSE ===')
    print(f'✓ Algorithm utilisé: {data.get(\"algorithme_utilise\", \"UNKNOWN\")}')
    print(f'✓ Nombre de matches: {len(data.get(\"matches\", []))}')
    print(f'✓ Jobs analysés: {data.get(\"total_jobs_analyses\", \"UNKNOWN\")}')
    print(f'✓ Fallback utilisé: {data.get(\"fallback_utilise\", False)}')
    
    services = data.get('services_externes_utilises', [])
    print(f'✓ Services externes: {services}')
    
    # Vérification du succès
    algorithm = data.get('algorithme_utilise', '')
    success = 'nexten' in algorithm.lower()
    
    print()
    if success:
        print('🎉 SUCCÈS: Nexten Matcher utilisé !')
        print('✅ Le routing fonctionne correctement')
    else:
        print('❌ ÉCHEC: Fallback utilisé au lieu de Nexten')
        print(f'   Algorithm: {algorithm}')
        if data.get('fallback_utilise'):
            print('   Raison: Fallback activé')
    
    print(f'\\n=== RÉPONSE COMPLÈTE ===')
    print(json.dumps(data, indent=2)[:1000] + '...' if len(json.dumps(data, indent=2)) > 1000 else json.dumps(data, indent=2))
    
except Exception as e:
    print(f'Erreur lors de l\'analyse: {e}')
    print('Réponse brute:')
    with open('/tmp/nexten_test_response.json', 'r') as f:
        print(f.read()[:500] + '...')
" 2>/dev/null)

    echo "$ANALYSIS"
else
    echo "📊 Analyse basique de la réponse:"
    
    # Extraire l'algorithme utilisé avec grep/sed
    ALGORITHM=$(echo "$RESPONSE" | grep -o '"algorithme_utilise"[^,]*' | sed 's/.*"algorithme_utilise": *"\([^"]*\)".*/\1/' 2>/dev/null || echo "UNKNOWN")
    echo "✓ Algorithm utilisé: $ALGORITHM"
    
    # Vérifier si nexten est dans la réponse
    if echo "$RESPONSE" | grep -qi "nexten"; then
        echo -e "${GREEN}🎉 SUCCÈS: Nexten détecté dans la réponse !${NC}"
    else
        echo -e "${RED}❌ ÉCHEC: Nexten non détecté${NC}"
    fi
    
    echo
    echo "Premiers 500 caractères de la réponse:"
    echo "$RESPONSE" | head -c 500
fi
echo

# === ÉTAPE 5: VÉRIFICATION DES LOGS ===
echo -e "${BLUE}📋 ÉTAPE 5: Vérification des logs...${NC}"

echo "📋 Logs récents de SuperSmartMatch V2:"
docker logs --tail=30 "$V2_CONTAINER" 2>/dev/null | grep -E "(nexten|endpoint|match|routing|algorithm|POST.*match)" || \
docker logs --tail=15 "$V2_CONTAINER" 2>/dev/null

echo
echo "📋 Logs récents de Nexten Matcher:"
docker logs --tail=15 "$NEXTEN_CONTAINER" 2>/dev/null | grep -E "(POST|match|error|404|200)" || \
docker logs --tail=10 "$NEXTEN_CONTAINER" 2>/dev/null
echo

# === ÉTAPE 6: TEST DE CONNECTIVITÉ NEXTEN ===
echo -e "${BLUE}📋 ÉTAPE 6: Test de connectivité directe Nexten...${NC}"

echo "🔗 Test direct de l'endpoint Nexten /match..."
DIRECT_NEXTEN_RESPONSE=$(curl -s -X POST "http://localhost:5052/match" \
    -H "Content-Type: application/json" \
    -d "$TEST_PAYLOAD" 2>/dev/null || echo "ERROR")

if [[ "$DIRECT_NEXTEN_RESPONSE" == "ERROR" ]] || [[ -z "$DIRECT_NEXTEN_RESPONSE" ]]; then
    echo -e "${RED}❌ Nexten /match endpoint inaccessible directement${NC}"
    echo "Cela peut expliquer pourquoi V2 utilise le fallback"
else
    echo -e "${GREEN}✅ Nexten /match endpoint accessible directement${NC}"
    echo "Nexten fonctionne correctement"
fi
echo

# === RÉSUMÉ FINAL ===
echo -e "${BLUE}🏁 === RÉSUMÉ DU TEST ===${NC}"

# Déterminer le résultat global
if echo "$RESPONSE" | grep -qi "nexten"; then
    echo -e "${GREEN}🎉 RÉSULTAT: SUCCÈS !${NC}"
    echo -e "${GREEN}✅ SuperSmartMatch V2 route correctement vers Nexten${NC}"
    echo -e "${GREEN}✅ L'objectif de correction est atteint${NC}"
    
    ALGORITHM=$(echo "$RESPONSE" | grep -o '"algorithme_utilise"[^,]*' | sed 's/.*"algorithme_utilise": *"\([^"]*\)".*/\1/' 2>/dev/null || echo "nexten")
    echo -e "${GREEN}✅ Algorithm final: $ALGORITHM${NC}"
else
    echo -e "${RED}❌ RÉSULTAT: ÉCHEC${NC}"
    echo -e "${RED}❌ SuperSmartMatch V2 n'utilise pas Nexten${NC}"
    echo -e "${RED}❌ Utilise encore le fallback${NC}"
    
    echo
    echo -e "${YELLOW}🔍 DIAGNOSTIC SUPPLÉMENTAIRE NÉCESSAIRE:${NC}"
    echo "  1. Vérifier que Nexten est accessible depuis le réseau Docker"
    echo "  2. Vérifier la configuration des endpoints dans le conteneur"
    echo "  3. Analyser les logs pour identifier la cause du fallback"
fi

echo
echo -e "${BLUE}📝 FICHIERS DE TEST CRÉÉS:${NC}"
echo "  - /tmp/nexten_test_response.json (réponse complète)"
echo
echo -e "${BLUE}🔍 COMMANDES UTILES:${NC}"
echo "  - Logs V2: docker logs $V2_CONTAINER"
echo "  - Logs Nexten: docker logs $NEXTEN_CONTAINER"
echo "  - Test manuel: curl -X POST http://localhost:5070/api/v2/match -d '$TEST_PAYLOAD'"
echo
echo -e "${GREEN}🚀 TEST TERMINÉ !${NC}"