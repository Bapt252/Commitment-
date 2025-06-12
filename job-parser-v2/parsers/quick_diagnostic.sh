#!/bin/bash

# 🔍 DIAGNOSTIC RAPIDE - Problème routing Nexten
# Compatible macOS

echo "🔍 === DIAGNOSTIC RAPIDE - PROBLÈME NEXTEN ==="

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📋 ÉTAPE 1: État des conteneurs...${NC}"

echo "Conteneurs en cours d'exécution:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

V2_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(supersmartmatch.*v2|v2.*unified|ssm.*v2)" | head -1)
NEXTEN_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(nexten|matching)" | head -1)

echo
if [ -n "$V2_CONTAINER" ]; then
    echo -e "${GREEN}✅ V2 Container: $V2_CONTAINER${NC}"
else
    echo -e "${RED}❌ Aucun conteneur V2 trouvé${NC}"
fi

if [ -n "$NEXTEN_CONTAINER" ]; then
    echo -e "${GREEN}✅ Nexten Container: $NEXTEN_CONTAINER${NC}"
else
    echo -e "${RED}❌ Aucun conteneur Nexten trouvé${NC}"
fi

echo
echo -e "${BLUE}📋 ÉTAPE 2: Test de connectivité...${NC}"

# Test V2
echo "🏥 Test V2 (http://localhost:5070/health):"
V2_STATUS=$(curl -s -w "%{http_code}" "http://localhost:5070/health" 2>/dev/null)
if echo "$V2_STATUS" | grep -q "200"; then
    echo -e "${GREEN}✅ V2 accessible (200)${NC}"
else
    echo -e "${RED}❌ V2 inaccessible ($V2_STATUS)${NC}"
fi

# Test Nexten
echo "🏥 Test Nexten (http://localhost:5052/health):"
NEXTEN_STATUS=$(curl -s -w "%{http_code}" "http://localhost:5052/health" 2>/dev/null)
if echo "$NEXTEN_STATUS" | grep -q "200"; then
    echo -e "${GREEN}✅ Nexten accessible (200)${NC}"
else
    echo -e "${YELLOW}⚠️  Nexten health inaccessible, test /match...${NC}"
    
    # Test direct /match
    MATCH_STATUS=$(curl -s -w "%{http_code}" -X POST "http://localhost:5052/match" -H "Content-Type: application/json" -d '{}' 2>/dev/null)
    if echo "$MATCH_STATUS" | grep -q -E "(200|400|422)"; then
        echo -e "${GREEN}✅ Nexten /match accessible ($MATCH_STATUS)${NC}"
    else
        echo -e "${RED}❌ Nexten complètement inaccessible ($MATCH_STATUS)${NC}"
    fi
fi

echo
echo -e "${BLUE}📋 ÉTAPE 3: Vérification configuration dans le conteneur...${NC}"

if [ -n "$V2_CONTAINER" ]; then
    echo "🔍 Configuration NEXTEN_ENDPOINT dans le conteneur:"
    
    # Chercher le fichier config dans le conteneur
    CONFIG_CHECK=$(docker exec "$V2_CONTAINER" find / -name "config.py" -type f 2>/dev/null | head -3)
    
    if [ -n "$CONFIG_CHECK" ]; then
        echo "Fichiers config trouvés:"
        echo "$CONFIG_CHECK"
        
        # Vérifier le contenu
        for config_file in $CONFIG_CHECK; do
            echo
            echo "📄 Contenu de $config_file:"
            NEXTEN_LINE=$(docker exec "$V2_CONTAINER" grep "NEXTEN_ENDPOINT" "$config_file" 2>/dev/null || echo "NOT_FOUND")
            echo "   $NEXTEN_LINE"
        done
    else
        echo -e "${RED}❌ Aucun fichier config.py trouvé dans le conteneur${NC}"
    fi
else
    echo -e "${RED}❌ Impossible de vérifier: conteneur V2 non trouvé${NC}"
fi

echo
echo -e "${BLUE}📋 ÉTAPE 4: Analyse des logs récents...${NC}"

if [ -n "$NEXTEN_CONTAINER" ]; then
    echo "📋 Logs récents Nexten (recherche d'appels):"
    NEXTEN_LOGS=$(docker logs --tail=30 "$NEXTEN_CONTAINER" 2>/dev/null | grep "POST")
    
    if [ -n "$NEXTEN_LOGS" ]; then
        echo "$NEXTEN_LOGS" | tail -10
        echo
        
        # Analyser les endpoints utilisés
        if echo "$NEXTEN_LOGS" | grep -q "POST /match"; then
            echo -e "${GREEN}✅ V2 utilise le bon endpoint: /match${NC}"
        fi
        
        if echo "$NEXTEN_LOGS" | grep -q "POST /api/v1/queue-matching"; then
            echo -e "${RED}❌ PROBLÈME: V2 utilise encore /api/v1/queue-matching${NC}"
            echo "   → Le conteneur n'utilise pas la configuration corrigée"
        fi
        
        if echo "$NEXTEN_LOGS" | grep -q "POST /api/match"; then
            echo -e "${YELLOW}⚠️  V2 utilise /api/match (devrait être /match)${NC}"
        fi
    else
        echo "Aucun appel POST récent trouvé"
    fi
fi

echo
echo -e "${BLUE}📋 ÉTAPE 5: Test simple...${NC}"

echo "🧪 Test rapide avec payload minimal:"
SIMPLE_TEST=$(curl -s -X POST "http://localhost:5070/api/v2/match" \
    -H "Content-Type: application/json" \
    -d '{"candidate": {"profile": {"skills": ["Python"]}}, "jobs": [{"id": "test", "title": "Test"}]}' 2>/dev/null)

if [ -n "$SIMPLE_TEST" ]; then
    if echo "$SIMPLE_TEST" | grep -q "detail"; then
        echo -e "${YELLOW}⚠️  Erreur de format de payload${NC}"
        echo "   $(echo "$SIMPLE_TEST" | head -c 150)..."
    elif echo "$SIMPLE_TEST" | grep -qi "nexten"; then
        echo -e "${GREEN}✅ Réponse contient 'nexten' !${NC}"
    else
        echo -e "${YELLOW}⚠️  Réponse reçue mais pas de 'nexten'${NC}"
        echo "   $(echo "$SIMPLE_TEST" | head -c 100)..."
    fi
else
    echo -e "${RED}❌ Aucune réponse du test${NC}"
fi

echo
echo -e "${BLUE}🏁 === RÉSUMÉ DU DIAGNOSTIC ===${NC}"

# Déterminer le problème principal
MAIN_ISSUE=""

if [ -z "$V2_CONTAINER" ]; then
    MAIN_ISSUE="Conteneur V2 non démarré"
elif [ -z "$NEXTEN_CONTAINER" ]; then
    MAIN_ISSUE="Conteneur Nexten non démarré"
elif ! echo "$V2_STATUS" | grep -q "200"; then
    MAIN_ISSUE="V2 inaccessible"
elif echo "$NEXTEN_LOGS" | grep -q "POST /api/v1/queue-matching"; then
    MAIN_ISSUE="Configuration non mise à jour dans le conteneur"
elif ! echo "$NEXTEN_STATUS$MATCH_STATUS" | grep -q -E "(200|400|422)"; then
    MAIN_ISSUE="Nexten inaccessible"
else
    MAIN_ISSUE="Format de payload incorrect"
fi

echo -e "${YELLOW}🎯 PROBLÈME PRINCIPAL: $MAIN_ISSUE${NC}"
echo

case "$MAIN_ISSUE" in
    *"non démarré"*)
        echo -e "${BLUE}💡 SOLUTION:${NC}"
        echo "docker-compose up -d"
        ;;
    *"inaccessible"*)
        echo -e "${BLUE}💡 SOLUTION:${NC}"
        echo "docker-compose restart $V2_CONTAINER $NEXTEN_CONTAINER"
        ;;
    *"Configuration non mise à jour"*)
        echo -e "${BLUE}💡 SOLUTION:${NC}"
        echo "1. Vérifier que supersmartmatch-v2/app/config.py contient NEXTEN_ENDPOINT = \"/match\""
        echo "2. Reconstruire le conteneur:"
        echo "   docker-compose build --no-cache $V2_CONTAINER"
        echo "   docker-compose up -d $V2_CONTAINER"
        ;;
    *"Format"*)
        echo -e "${BLUE}💡 SOLUTION:${NC}"
        echo "Utiliser le format correct de payload (voir scripts de test)"
        ;;
esac

echo
echo -e "${GREEN}🔧 SCRIPTS UTILES:${NC}"
echo "./fix_config_macos.sh     # Correction manuelle pour macOS"
echo "./test_correct_format.sh  # Test avec payload correct"

echo
echo -e "${GREEN}🚀 DIAGNOSTIC TERMINÉ !${NC}"