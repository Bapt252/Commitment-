#!/bin/bash

# 🔍 SCRIPT DE DIAGNOSTIC - Configuration Conteneur SuperSmartMatch V2
# Analyse la configuration actuelle dans le conteneur Docker

set -e

echo "🔍 === DIAGNOSTIC CONTENEUR SUPERSMARTMATCH V2 ==="
echo "Objectif: Identifier la configuration exacte utilisée par le conteneur"
echo

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# === ÉTAPE 1: IDENTIFICATION DU CONTENEUR ===
echo -e "${BLUE}📋 ÉTAPE 1: Identification du conteneur...${NC}"

V2_CONTAINER=""
if docker ps --format "{{.Names}}" | grep -E "(supersmartmatch.*v2|v2.*unified)" | head -1 > /dev/null; then
    V2_CONTAINER=$(docker ps --format "{{.Names}}" | grep -E "(supersmartmatch.*v2|v2.*unified)" | head -1)
    echo -e "${GREEN}✅ Conteneur trouvé: $V2_CONTAINER${NC}"
else
    echo -e "${RED}❌ Aucun conteneur SuperSmartMatch V2 en cours d'exécution${NC}"
    echo "Conteneurs disponibles:"
    docker ps --format "table {{.Names}}\t{{.Status}}"
    exit 1
fi

# === ÉTAPE 2: INSPECTION DU CONTENEUR ===
echo
echo -e "${BLUE}📋 ÉTAPE 2: Inspection du conteneur...${NC}"

echo "🏷️  Informations du conteneur:"
docker inspect "$V2_CONTAINER" --format '
Image: {{.Config.Image}}
Created: {{.Created}}
Command: {{.Config.Cmd}}
WorkingDir: {{.Config.WorkingDir}}
' 2>/dev/null || echo "Erreur lors de l'inspection"

# === ÉTAPE 3: EXPLORATION DE L'ARBORESCENCE ===
echo
echo -e "${BLUE}📋 ÉTAPE 3: Exploration de l'arborescence...${NC}"

echo "📁 Structure des dossiers dans le conteneur:"
docker exec "$V2_CONTAINER" find /app -type d -name "*app*" 2>/dev/null | head -20 || \
docker exec "$V2_CONTAINER" ls -la / 2>/dev/null | head -10 || \
echo "Impossible d'explorer l'arborescence"

echo
echo "📁 Recherche des fichiers de configuration:"
docker exec "$V2_CONTAINER" find / -name "config.py" -type f 2>/dev/null | head -10 || \
echo "Aucun fichier config.py trouvé"

# === ÉTAPE 4: VÉRIFICATION DES ENDPOINTS ===
echo
echo -e "${BLUE}📋 ÉTAPE 4: Vérification des endpoints dans le conteneur...${NC}"

echo "🔍 Recherche de NEXTEN_ENDPOINT dans les fichiers:"
docker exec "$V2_CONTAINER" find / -name "*.py" -type f -exec grep -l "NEXTEN_ENDPOINT" {} \; 2>/dev/null | while read -r file; do
    echo "  📄 Fichier: $file"
    docker exec "$V2_CONTAINER" grep -n "NEXTEN_ENDPOINT" "$file" 2>/dev/null | head -5
done

echo
echo "🔍 Recherche de références à api/v1/queue-matching:"
docker exec "$V2_CONTAINER" find / -name "*.py" -type f -exec grep -l "api/v1/queue-matching" {} \; 2>/dev/null | while read -r file; do
    echo "  📄 Fichier problématique: $file"
    docker exec "$V2_CONTAINER" grep -n "api/v1/queue-matching" "$file" 2>/dev/null
done

# === ÉTAPE 5: CONTENU DES FICHIERS CLÉS ===
echo
echo -e "${BLUE}📋 ÉTAPE 5: Contenu des fichiers clés...${NC}"

# Fichiers de configuration potentiels
CONFIG_FILES=(
    "/app/config.py"
    "/app/app/config.py"
    "/supersmartmatch-v2/app/config.py"
    "/usr/src/app/config.py"
    "/code/app/config.py"
)

echo "📄 Vérification des fichiers de configuration:"
for config_file in "${CONFIG_FILES[@]}"; do
    if docker exec "$V2_CONTAINER" test -f "$config_file" 2>/dev/null; then
        echo "  ✅ Trouvé: $config_file"
        echo "     Contenu de NEXTEN_ENDPOINT:"
        docker exec "$V2_CONTAINER" grep -A 2 -B 2 "NEXTEN_ENDPOINT" "$config_file" 2>/dev/null || echo "     Pas de NEXTEN_ENDPOINT trouvé"
        echo
    else
        echo "  ❌ Non trouvé: $config_file"
    fi
done

# === ÉTAPE 6: VARIABLES D'ENVIRONNEMENT ===
echo
echo -e "${BLUE}📋 ÉTAPE 6: Variables d'environnement...${NC}"

echo "🌍 Variables d'environnement liées aux endpoints:"
docker exec "$V2_CONTAINER" env | grep -E "(NEXTEN|ENDPOINT|MATCH|URL)" 2>/dev/null || echo "Aucune variable trouvée"

# === ÉTAPE 7: PROCESSUS ET SERVICES ===
echo
echo -e "${BLUE}📋 ÉTAPE 7: Processus en cours d'exécution...${NC}"

echo "⚙️  Processus Python en cours:"
docker exec "$V2_CONTAINER" ps aux | grep python 2>/dev/null || echo "Aucun processus Python trouvé"

# === ÉTAPE 8: LOGS SPÉCIFIQUES ===
echo
echo -e "${BLUE}📋 ÉTAPE 8: Logs du démarrage...${NC}"

echo "📋 Logs de démarrage (recherche de configuration):"
docker logs "$V2_CONTAINER" 2>&1 | grep -E "(config|endpoint|nexten|matcher)" | tail -20 || \
docker logs "$V2_CONTAINER" 2>&1 | tail -10

# === ÉTAPE 9: TEST EN DIRECT ===
echo
echo -e "${BLUE}📋 ÉTAPE 9: Test de l'endpoint en direct...${NC}"

echo "🧪 Test de l'import de configuration depuis le conteneur:"
CONFIG_TEST=$(docker exec "$V2_CONTAINER" python3 -c "
try:
    import sys
    sys.path.append('/app')
    sys.path.append('/app/app')
    from config import AlgorithmConfig
    config = AlgorithmConfig()
    print('NEXTEN_ENDPOINT:', getattr(config, 'NEXTEN_ENDPOINT', 'NOT_FOUND'))
except Exception as e:
    print('Error importing config:', str(e))
    try:
        import os
        print('Working directory:', os.getcwd())
        print('Python path:', sys.path[:3])
    except:
        pass
" 2>/dev/null || echo "Erreur lors du test d'import")

echo "$CONFIG_TEST"

# === ÉTAPE 10: COMPARAISON AVEC LE CODE SOURCE ===
echo
echo -e "${BLUE}📋 ÉTAPE 10: Comparaison avec le code source...${NC}"

echo "🔄 Comparaison des fichiers entre conteneur et repository:"

# Comparer le fichier config.py si trouvé
if docker exec "$V2_CONTAINER" test -f "/app/config.py" 2>/dev/null; then
    echo "  📄 Comparaison de /app/config.py:"
    
    # Extraire NEXTEN_ENDPOINT du conteneur
    CONTAINER_ENDPOINT=$(docker exec "$V2_CONTAINER" grep "NEXTEN_ENDPOINT" "/app/config.py" 2>/dev/null || echo "NOT_FOUND")
    echo "     Conteneur: $CONTAINER_ENDPOINT"
    
    # Comparer avec le repository local s'il existe
    if [ -f "supersmartmatch-v2/app/config.py" ]; then
        LOCAL_ENDPOINT=$(grep "NEXTEN_ENDPOINT" "supersmartmatch-v2/app/config.py" 2>/dev/null || echo "NOT_FOUND")
        echo "     Repository: $LOCAL_ENDPOINT"
        
        if [ "$CONTAINER_ENDPOINT" = "$LOCAL_ENDPOINT" ]; then
            echo -e "     ${GREEN}✅ Identiques${NC}"
        else
            echo -e "     ${RED}❌ Différents${NC}"
        fi
    fi
fi

# === ÉTAPE 11: RECOMMANDATIONS ===
echo
echo -e "${BLUE}📋 ÉTAPE 11: Recommandations...${NC}"

echo "💡 Actions recommandées basées sur le diagnostic:"

# Analyser les résultats pour donner des recommandations
if docker exec "$V2_CONTAINER" find / -name "*.py" -type f -exec grep -l "api/v1/queue-matching" {} \; 2>/dev/null | head -1 > /dev/null; then
    echo -e "${RED}  ❌ Des références à api/v1/queue-matching trouvées dans le conteneur${NC}"
    echo "     → Le conteneur utilise une version non corrigée du code"
    echo "     → Recommandation: Reconstruire le conteneur avec le code corrigé"
else
    echo -e "${GREEN}  ✅ Aucune référence à api/v1/queue-matching trouvée${NC}"
    echo "     → Le conteneur semble utiliser la bonne configuration"
    echo "     → Le problème peut être ailleurs (connectivité, Nexten down, etc.)"
fi

# Vérifier si Nexten est accessible
if curl -s "http://localhost:5052/health" > /dev/null 2>&1 || curl -s "http://localhost:5052/match" -X POST -d '{}' > /dev/null 2>&1; then
    echo -e "${GREEN}  ✅ Nexten Matcher accessible${NC}"
else
    echo -e "${RED}  ❌ Nexten Matcher inaccessible${NC}"
    echo "     → Vérifier que le service Nexten est démarré"
    echo "     → Vérifier la connectivité réseau entre les conteneurs"
fi

# === RÉSUMÉ ===
echo
echo -e "${BLUE}🏁 === RÉSUMÉ DU DIAGNOSTIC ===${NC}"
echo "Conteneur analysé: $V2_CONTAINER"
echo "Fichiers de configuration trouvés dans le conteneur:"

docker exec "$V2_CONTAINER" find / -name "config.py" -type f 2>/dev/null | while read -r file; do
    echo "  📄 $file"
done

echo
echo -e "${YELLOW}📝 PROCHAINES ÉTAPES SUGGÉRÉES:${NC}"
echo "  1. Si api/v1/queue-matching trouvé → Reconstruire le conteneur"
echo "  2. Si Nexten inaccessible → Vérifier/redémarrer Nexten" 
echo "  3. Si configuration OK → Analyser les logs détaillés"
echo "  4. Tester manuellement le routing avec une requête"
echo
echo -e "${GREEN}🚀 DIAGNOSTIC TERMINÉ !${NC}"