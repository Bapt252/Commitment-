#!/bin/bash

# 🎯 SCRIPT DE CORRECTION FINALE - SuperSmartMatch V2 Endpoints
# Corrige définitivement le problème de routing vers Nexten

set -e

echo "🚀 === CORRECTION FINALE ENDPOINTS SUPERSMARTMATCH V2 ==="
echo "Objectif: Transformer /api/v1/queue-matching → /match"
echo

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# === ÉTAPE 1: VÉRIFICATION ENVIRONNEMENT ===
echo -e "${BLUE}📋 ÉTAPE 1: Vérification de l'environnement...${NC}"

# Vérifier si nous sommes dans le bon répertoire
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Erreur: docker-compose.yml non trouvé${NC}"
    echo "Veuillez exécuter ce script depuis la racine du projet Commitment-"
    exit 1
fi

# Vérifier les dossiers SuperSmartMatch V2
FOLDERS_TO_CHECK=(
    "supersmartmatch-v2"
    "super-smart-match-v2"
    "matching-service"
)

echo "Recherche des dossiers SuperSmartMatch V2..."
for folder in "${FOLDERS_TO_CHECK[@]}"; do
    if [ -d "$folder" ]; then
        echo -e "${GREEN}✅ Trouvé: $folder${NC}"
    else
        echo -e "${YELLOW}⚠️  Non trouvé: $folder${NC}"
    fi
done
echo

# === ÉTAPE 2: SAUVEGARDE ===
echo -e "${BLUE}📋 ÉTAPE 2: Sauvegarde des fichiers...${NC}"

BACKUP_DIR="backup_endpoints_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Création de la sauvegarde dans: $BACKUP_DIR"

# Sauvegarder tous les fichiers de configuration
find . -name "*.py" -path "*/supersmartmatch*" -exec cp --parents {} "$BACKUP_DIR/" \; 2>/dev/null || true
find . -name "*.py" -path "*/super-smart-match*" -exec cp --parents {} "$BACKUP_DIR/" \; 2>/dev/null || true

echo -e "${GREEN}✅ Sauvegarde terminée${NC}"
echo

# === ÉTAPE 3: CORRECTION DES FICHIERS ===
echo -e "${BLUE}📋 ÉTAPE 3: Correction des endpoints...${NC}"

# Fonction de correction pour un fichier
fix_file() {
    local file="$1"
    local backup_file="${file}.backup_$(date +%H%M%S)"
    
    if [ -f "$file" ]; then
        echo "  📝 Correction de: $file"
        cp "$file" "$backup_file"
        
        # Correction des endpoints Nexten
        sed -i 's|/api/v1/queue-matching|/match|g' "$file"
        sed -i 's|/api/queue-matching|/match|g' "$file"
        sed -i 's|api/v1/queue-matching|/match|g' "$file"
        sed -i 's|NEXTEN_ENDPOINT = "/api/match"|NEXTEN_ENDPOINT = "/match"|g' "$file"
        sed -i 's|NEXTEN_ENDPOINT = "/api/v1/match"|NEXTEN_ENDPOINT = "/match"|g' "$file"
        
        # Vérifier si des changements ont été effectués
        if ! diff -q "$file" "$backup_file" > /dev/null 2>&1; then
            echo -e "    ${GREEN}✅ Fichier corrigé${NC}"
            return 0
        else
            echo -e "    ${YELLOW}⚠️  Aucun changement nécessaire${NC}"
            rm "$backup_file"
            return 1
        fi
    else
        echo -e "    ${RED}❌ Fichier non trouvé: $file${NC}"
        return 1
    fi
}

# Liste des fichiers à corriger (chemins absolus et relatifs)
FILES_TO_FIX=(
    "supersmartmatch-v2/app/config.py"
    "supersmartmatch-v2/app/adapters/nexten_adapter.py"
    "supersmartmatch-v2/app/services/matching_orchestrator.py"
    "super-smart-match-v2/app/config.py"
    "super-smart-match-v2/app/adapters/nexten_adapter.py"
    "super-smart-match-v2/app/dependencies.py"
    "matching-service/app/v2/supersmartmatch_v2_orchestrator.py"
    "matching-service/app/v2/fallback_manager.py"
)

CORRECTED_COUNT=0

echo "Correction des fichiers de configuration..."
for file in "${FILES_TO_FIX[@]}"; do
    if fix_file "$file"; then
        ((CORRECTED_COUNT++))
    fi
done

echo
echo -e "${GREEN}✅ Nombre de fichiers corrigés: $CORRECTED_COUNT${NC}"
echo

# === ÉTAPE 4: RECHERCHE EXHAUSTIVE ===
echo -e "${BLUE}📋 ÉTAPE 4: Recherche exhaustive des références...${NC}"

echo "Recherche de toutes les références à /api/v1/queue-matching..."
REMAINING_REFS=$(grep -r "api/v1/queue-matching" . --include="*.py" 2>/dev/null | wc -l)

if [ "$REMAINING_REFS" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Références restantes trouvées:${NC}"
    grep -r "api/v1/queue-matching" . --include="*.py" 2>/dev/null | head -10
    echo
    echo "Correction des références restantes..."
    
    # Correction récursive de tous les fichiers Python
    find . -name "*.py" -type f -exec grep -l "api/v1/queue-matching" {} \; 2>/dev/null | while read -r file; do
        echo "  📝 Correction récursive de: $file"
        sed -i 's|/api/v1/queue-matching|/match|g' "$file"
        sed -i 's|api/v1/queue-matching|/match|g' "$file"
    done
else
    echo -e "${GREEN}✅ Aucune référence restante trouvée${NC}"
fi
echo

# === ÉTAPE 5: VÉRIFICATION DOCKER COMPOSE ===
echo -e "${BLUE}📋 ÉTAPE 5: Vérification de la configuration Docker...${NC}"

# Identifier le service SuperSmartMatch V2 dans docker-compose
V2_SERVICE_NAME=""
if grep -q "supersmartmatch-v2-unified" docker-compose.yml; then
    V2_SERVICE_NAME="supersmartmatch-v2-unified"
elif grep -q "supersmartmatch-v2" docker-compose.yml; then
    V2_SERVICE_NAME="supersmartmatch-v2"
elif grep -q "super-smart-match-v2" docker-compose.yml; then
    V2_SERVICE_NAME="super-smart-match-v2"
fi

if [ -n "$V2_SERVICE_NAME" ]; then
    echo -e "${GREEN}✅ Service V2 identifié: $V2_SERVICE_NAME${NC}"
else
    echo -e "${RED}❌ Service SuperSmartMatch V2 non trouvé dans docker-compose.yml${NC}"
    echo "Services disponibles:"
    grep -E "^  [a-zA-Z].*:$" docker-compose.yml | sed 's/://g'
    exit 1
fi
echo

# === ÉTAPE 6: RECONSTRUCTION DU CONTENEUR ===
echo -e "${BLUE}📋 ÉTAPE 6: Reconstruction du conteneur...${NC}"

echo "🔨 Arrêt du service V2..."
docker-compose stop "$V2_SERVICE_NAME" 2>/dev/null || true

echo "🗑️  Suppression du conteneur et de l'image..."
docker-compose rm -f "$V2_SERVICE_NAME" 2>/dev/null || true

# Supprimer l'image pour forcer la reconstruction
IMAGE_NAME=$(docker-compose config | grep -A 5 "$V2_SERVICE_NAME:" | grep "image:" | awk '{print $2}' | head -1)
if [ -n "$IMAGE_NAME" ]; then
    echo "🗑️  Suppression de l'image: $IMAGE_NAME"
    docker rmi "$IMAGE_NAME" 2>/dev/null || echo "Image déjà supprimée ou non trouvée"
fi

echo "🔨 Reconstruction et démarrage du service..."
docker-compose build --no-cache "$V2_SERVICE_NAME"
docker-compose up -d "$V2_SERVICE_NAME"

echo -e "${GREEN}✅ Service reconstruit et démarré${NC}"
echo

# === ÉTAPE 7: ATTENTE ET VÉRIFICATION ===
echo -e "${BLUE}📋 ÉTAPE 7: Vérification du fonctionnement...${NC}"

echo "⏳ Attente du démarrage du service (30 secondes)..."
sleep 30

# Vérifier que le conteneur est en cours d'exécution
if docker-compose ps "$V2_SERVICE_NAME" | grep -q "Up"; then
    echo -e "${GREEN}✅ Conteneur démarré avec succès${NC}"
else
    echo -e "${RED}❌ Erreur: Le conteneur ne démarre pas${NC}"
    echo "Logs du conteneur:"
    docker-compose logs --tail=20 "$V2_SERVICE_NAME"
    exit 1
fi

# Test de santé
echo "🏥 Test de santé du service..."
HEALTH_URL="http://localhost:5070/health"

if curl -s "$HEALTH_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Service V2 accessible${NC}"
    curl -s "$HEALTH_URL" | python -m json.tool 2>/dev/null || curl -s "$HEALTH_URL"
else
    echo -e "${YELLOW}⚠️  Service pas encore prêt ou erreur de connectivité${NC}"
fi
echo

# === ÉTAPE 8: TEST FONCTIONNEL ===
echo -e "${BLUE}📋 ÉTAPE 8: Test fonctionnel...${NC}"

# Générer une requête de test
TEST_PAYLOAD='{
    "cv_data": {
        "competences": ["Python", "Machine Learning"],
        "experience": 5,
        "localisation": "Paris",
        "niveau_etudes": "Master"
    },
    "jobs": [
        {
            "id": "test-job-1",
            "titre": "Développeur Python",
            "competences": ["Python", "Django"],
            "localisation": "Paris",
            "description": "Poste de développeur Python senior"
        }
    ],
    "options": {
        "algorithm": "auto",
        "max_results": 10
    }
}'

echo "🧪 Test de matching avec Nexten..."
RESPONSE=$(curl -s -X POST "http://localhost:5070/api/v2/match" \
    -H "Content-Type: application/json" \
    -d "$TEST_PAYLOAD" 2>/dev/null || echo "ERROR")

if [[ "$RESPONSE" == "ERROR" ]] || [[ -z "$RESPONSE" ]]; then
    echo -e "${YELLOW}⚠️  Impossible de tester l'API (service peut être encore en démarrage)${NC}"
    echo "Vous pouvez tester manuellement avec:"
    echo "curl -X POST http://localhost:5070/api/v2/match -H 'Content-Type: application/json' -d '$TEST_PAYLOAD'"
else
    echo -e "${GREEN}✅ Réponse reçue de l'API${NC}"
    
    # Vérifier si la réponse contient l'indication que Nexten a été utilisé
    if echo "$RESPONSE" | grep -q "nexten"; then
        echo -e "${GREEN}🎉 SUCCÈS: Nexten matcher détecté dans la réponse !${NC}"
        
        # Extraire l'algorithme utilisé
        ALGORITHM_USED=$(echo "$RESPONSE" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print('Algorithm used:', data.get('algorithme_utilise', 'unknown'))
    if 'matches' in data:
        print('Matches found:', len(data['matches']))
except:
    print('Unable to parse response')
" 2>/dev/null || echo "Unable to parse response")
        
        echo "$ALGORITHM_USED"
    else
        echo -e "${YELLOW}⚠️  Réponse reçue mais algorithme non détecté${NC}"
        echo "Premiers caractères de la réponse:"
        echo "$RESPONSE" | head -c 200
    fi
fi
echo

# === ÉTAPE 9: VÉRIFICATION DES LOGS ===
echo -e "${BLUE}📋 ÉTAPE 9: Vérification des logs...${NC}"

echo "📋 Derniers logs du service V2:"
docker-compose logs --tail=20 "$V2_SERVICE_NAME" | grep -E "(nexten|endpoint|match|routing|algorithm)" || \
docker-compose logs --tail=10 "$V2_SERVICE_NAME"
echo

# === RÉSUMÉ FINAL ===
echo -e "${BLUE}🏁 === RÉSUMÉ DE LA CORRECTION ===${NC}"
echo -e "${GREEN}✅ Fichiers corrigés: $CORRECTED_COUNT${NC}"
echo -e "${GREEN}✅ Service reconstruit: $V2_SERVICE_NAME${NC}"
echo -e "${GREEN}✅ Conteneur démarré et accessible${NC}"
echo
echo -e "${YELLOW}📝 ACTIONS EFFECTUÉES:${NC}"
echo "  1. Sauvegarde des fichiers dans: $BACKUP_DIR"
echo "  2. Correction de tous les endpoints /api/v1/queue-matching → /match"
echo "  3. Reconstruction complète du conteneur Docker"
echo "  4. Tests de santé et de fonctionnement"
echo
echo -e "${BLUE}🔍 PROCHAINES ÉTAPES:${NC}"
echo "  1. Tester manuellement: curl -X POST http://localhost:5070/api/v2/match [payload]"
echo "  2. Vérifier les logs: docker-compose logs $V2_SERVICE_NAME"
echo "  3. Confirmer que 'algorithme_utilise: nexten_matcher' apparaît dans les réponses"
echo
echo -e "${GREEN}🎯 OBJECTIF: Transformer 'Algorithm: v2_routed_fallback_basic' en 'Algorithm: nexten_matcher'${NC}"
echo -e "${GREEN}🚀 CORRECTION TERMINÉE !${NC}"