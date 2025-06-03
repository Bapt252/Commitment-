#!/bin/bash

# 🚀 SuperSmartMatch V2 - Installation et Test Express
# Script d'installation et de test en une seule commande

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 SuperSmartMatch V2 - Installation et Test Express${NC}"
echo "=================================================="

# 1. Vérifier les dépendances
echo -e "${BLUE}🔍 Vérification des dépendances...${NC}"

if ! command -v curl &> /dev/null; then
    echo "❌ curl requis mais non installé"
    exit 1
fi

if ! command -v jq &> /dev/null; then
    echo "⚠️  jq non trouvé, installation recommandée pour de meilleurs résultats"
fi

echo -e "${GREEN}✅ Dépendances vérifiées${NC}"

# 2. Rendre les scripts exécutables
echo -e "${BLUE}🔧 Configuration des scripts...${NC}"

chmod +x test-supersmartmatch-v2-enhanced.sh 2>/dev/null || echo "⚠️  Script enhanced non trouvé"
chmod +x test-supersmartmatch-v2-complete.sh 2>/dev/null || echo "⚠️  Script complete non trouvé"
chmod +x deploy-supersmartmatch-v2.sh 2>/dev/null || echo "⚠️  Script deploy non trouvé"

# Rendre tous les scripts de test exécutables
find . -name "test-*.sh" -exec chmod +x {} \; 2>/dev/null

echo -e "${GREEN}✅ Scripts configurés${NC}"

# 3. Vérifier si les services sont déjà actifs
echo -e "${BLUE}🔍 Vérification des services...${NC}"

services_running=0

if curl -s http://localhost:5070/health >/dev/null 2>&1; then
    echo "✅ SuperSmartMatch V2 (port 5070) actif"
    ((services_running++))
fi

if curl -s http://localhost:5052/health >/dev/null 2>&1; then
    echo "✅ Nexten Matcher (port 5052) actif"
    ((services_running++))
fi

if curl -s http://localhost:5062/health >/dev/null 2>&1; then
    echo "✅ SuperSmartMatch V1 (port 5062) actif"
    ((services_running++))
fi

# 4. Proposer le déploiement si services non actifs
if [[ $services_running -eq 0 ]]; then
    echo -e "${YELLOW}⚠️  Aucun service actif détecté${NC}"
    echo "Voulez-vous déployer SuperSmartMatch V2 ? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        if [[ -f "deploy-supersmartmatch-v2.sh" ]]; then
            echo -e "${BLUE}🚀 Déploiement en cours...${NC}"
            ./deploy-supersmartmatch-v2.sh --type docker
        else
            echo "❌ Script de déploiement non trouvé"
            echo "Veuillez déployer manuellement les services sur les ports 5070, 5052, 5062"
        fi
    fi
fi

# 5. Lancer le test enhanced si disponible
echo
echo -e "${BLUE}🧪 Lancement des tests...${NC}"

if [[ -f "test-supersmartmatch-v2-enhanced.sh" ]]; then
    echo -e "${GREEN}🔥 Utilisation du script Enhanced V2.0 (recommandé)${NC}"
    ./test-supersmartmatch-v2-enhanced.sh
elif [[ -f "test-supersmartmatch-v2-complete.sh" ]]; then
    echo -e "${YELLOW}⚠️  Utilisation du script complete (basique)${NC}"
    ./test-supersmartmatch-v2-complete.sh
else
    echo -e "${YELLOW}⚠️  Aucun script de test automatisé trouvé${NC}"
    echo "Tests manuels rapides :"
    
    echo "1. Test santé SuperSmartMatch V2 :"
    curl -s http://localhost:5070/health | jq . 2>/dev/null || curl -s http://localhost:5070/health
    
    echo
    echo "2. Test API V2 basique :"
    curl -s -X POST http://localhost:5070/api/v2/match \
        -H "Content-Type: application/json" \
        -d '{"candidate":{"name":"Test"},"offers":[{"id":"1"}],"algorithm":"auto"}' \
        | jq . 2>/dev/null || echo "JSON response received"
fi

echo
echo -e "${GREEN}🎉 Installation et tests terminés !${NC}"
echo
echo "📚 Documentation disponible :"
echo "  - QUICKSTART-SUPERSMARTMATCH-V2-TESTING.md"
echo "  - TESTING-GUIDE-SUPERSMARTMATCH-V2-ENHANCED.md" 
echo "  - README-SUPERSMARTMATCH-V2.md"
echo
echo "🔗 URLs utiles :"
echo "  - Health Check: http://localhost:5070/health"
echo "  - Métriques: http://localhost:5070/metrics"
echo "  - API V2: http://localhost:5070/api/v2/match"
echo
echo -e "${BLUE}🚀 SuperSmartMatch V2 prêt à être utilisé !${NC}"
