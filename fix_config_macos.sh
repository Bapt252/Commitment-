#!/bin/bash

# 🔧 CORRECTION MANUELLE POUR MACOS - Endpoints Nexten
# Compatible avec BSD sed (macOS)

echo "🔧 === CORRECTION MANUELLE MACOS - ENDPOINTS NEXTEN ==="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Vérifier qu'on est à la racine
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Erreur: Exécutez depuis la racine du projet Commitment-${NC}"
    exit 1
fi

echo -e "${BLUE}📋 ÉTAPE 1: Correction du fichier config principal...${NC}"

CONFIG_FILE="supersmartmatch-v2/app/config.py"
if [ -f "$CONFIG_FILE" ]; then
    echo "📝 Correction de $CONFIG_FILE"
    
    # Sauvegarde
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup_$(date +%H%M%S)"
    
    # Correction compatible macOS (utilise un fichier temporaire)
    sed 's|NEXTEN_ENDPOINT = "/api/match"|NEXTEN_ENDPOINT = "/match"|g' "$CONFIG_FILE" > "$CONFIG_FILE.tmp"
    mv "$CONFIG_FILE.tmp" "$CONFIG_FILE"
    
    # Vérifier le changement
    if grep -q 'NEXTEN_ENDPOINT = "/match"' "$CONFIG_FILE"; then
        echo -e "${GREEN}✅ Configuration corrigée${NC}"
    else
        echo -e "${RED}❌ Correction échouée${NC}"
        echo "Contenu actuel:"
        grep "NEXTEN_ENDPOINT" "$CONFIG_FILE"
    fi
else
    echo -e "${RED}❌ Fichier $CONFIG_FILE non trouvé${NC}"
fi

echo
echo -e "${BLUE}📋 ÉTAPE 2: Vérification du service Docker...${NC}"

# Trouver le bon nom de service
echo "Services disponibles dans docker-compose.yml:"
grep -E "^  [a-zA-Z][^:]*:" docker-compose.yml | sed 's/://g' | head -10

# Essayer de trouver le service V2
V2_SERVICE=""
if grep -q "supersmartmatch-v2-unified" docker-compose.yml; then
    V2_SERVICE="supersmartmatch-v2-unified"
elif grep -q "supersmartmatch-v2" docker-compose.yml; then
    V2_SERVICE="supersmartmatch-v2"
elif grep -q "ssm_v2" docker-compose.yml; then
    V2_SERVICE="ssm_v2"
fi

if [ -n "$V2_SERVICE" ]; then
    echo -e "${GREEN}✅ Service V2 trouvé: $V2_SERVICE${NC}"
else
    echo -e "${YELLOW}⚠️  Service V2 non identifié automatiquement${NC}"
    echo "Veuillez identifier manuellement le service depuis la liste ci-dessus"
    read -p "Nom du service SuperSmartMatch V2: " V2_SERVICE
fi

echo
echo -e "${BLUE}📋 ÉTAPE 3: Reconstruction du conteneur...${NC}"

if [ -n "$V2_SERVICE" ]; then
    echo "🔨 Arrêt du service: $V2_SERVICE"
    docker-compose stop "$V2_SERVICE" 2>/dev/null || true
    
    echo "🗑️  Suppression du conteneur"
    docker-compose rm -f "$V2_SERVICE" 2>/dev/null || true
    
    echo "🔨 Reconstruction (cela peut prendre quelques minutes)..."
    if docker-compose build "$V2_SERVICE" --no-cache; then
        echo -e "${GREEN}✅ Build réussi${NC}"
        
        echo "🚀 Démarrage du service..."
        if docker-compose up -d "$V2_SERVICE"; then
            echo -e "${GREEN}✅ Service démarré${NC}"
        else
            echo -e "${RED}❌ Échec du démarrage${NC}"
        fi
    else
        echo -e "${RED}❌ Échec du build${NC}"
    fi
else
    echo -e "${RED}❌ Impossible de reconstruire sans nom de service${NC}"
fi

echo
echo -e "${BLUE}📋 ÉTAPE 4: Test rapide...${NC}"

echo "⏳ Attente de 20 secondes pour le démarrage..."
sleep 20

echo "🏥 Test de santé V2..."
V2_HEALTH=$(curl -s "http://localhost:5070/health" 2>/dev/null || echo "ERROR")

if [[ "$V2_HEALTH" != "ERROR" ]]; then
    echo -e "${GREEN}✅ V2 accessible${NC}"
else
    echo -e "${YELLOW}⚠️  V2 pas encore prêt${NC}"
fi

echo "🏥 Test Nexten..."
NEXTEN_HEALTH=$(curl -s "http://localhost:5052/health" 2>/dev/null || echo "ERROR")

if [[ "$NEXTEN_HEALTH" != "ERROR" ]]; then
    echo -e "${GREEN}✅ Nexten accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Nexten inaccessible${NC}"
fi

echo
echo -e "${GREEN}🎯 CORRECTION TERMINÉE !${NC}"
echo
echo -e "${YELLOW}📝 PROCHAINES ÉTAPES:${NC}"
echo "1. Testez avec le payload correct (voir ci-dessous)"
echo "2. Vérifiez les logs: docker logs $V2_SERVICE"
echo "3. Si le problème persiste, vérifiez la config dans le conteneur"

echo
echo -e "${BLUE}🧪 TEST MANUEL RECOMMANDÉ:${NC}"
echo 'curl -X POST http://localhost:5070/api/v2/match \'
echo '  -H "Content-Type: application/json" \'
echo '  -d "{"'
echo '    "candidate": {'
echo '      "skills": ["Python", "ML"],'
echo '      "experience": 5,'
echo '      "location": "Paris"'
echo '    },'
echo '    "jobs": ['
echo '      {'
echo '        "id": "test-1",'
echo '        "title": "Dev ML",'
echo '        "skills": ["Python"],'
echo '        "location": "Paris"'
echo '      }'
echo '    ]'
echo '  }"'

echo
echo -e "${GREEN}🚀 SCRIPT TERMINÉ !${NC}"