#!/bin/bash

# 🚀 SuperSmartMatch V2 - Quick Start PROMPT 2
# Script de démarrage rapide pour les parsers ultra-optimisés

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 SuperSmartMatch V2 - PROMPT 2 Quick Start${NC}"
echo "=============================================="

# Fonction pour vérifier Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker non installé${NC}"
        echo -e "${YELLOW}💡 Installez Docker: https://docs.docker.com/get-docker/${NC}"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker non démarré${NC}"
        echo -e "${YELLOW}💡 Démarrez Docker Desktop et réessayez${NC}"
        
        # Proposer test standalone
        echo ""
        echo -e "${BLUE}🧪 Option alternative: Test standalone (sans Docker)${NC}"
        read -p "Voulez-vous tester PROMPT 2 en mode simulation ? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${GREEN}🎯 Lancement du test standalone...${NC}"
            chmod +x test-prompt2-standalone.js
            node test-prompt2-standalone.js
            exit 0
        else
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ Docker OK${NC}"
}

# Fonction pour démarrer les services
start_services() {
    echo -e "${BLUE}🔧 Démarrage des services SuperSmartMatch...${NC}"
    
    # Arrêter les services existants
    docker-compose -f docker-compose.fixed.yml down 2>/dev/null || true
    
    # Construire et démarrer
    echo -e "${YELLOW}⏳ Construction des images Docker...${NC}"
    docker-compose -f docker-compose.fixed.yml build --parallel
    
    echo -e "${YELLOW}⏳ Démarrage des conteneurs...${NC}" 
    docker-compose -f docker-compose.fixed.yml up -d
    
    # Attendre que les services soient prêts
    echo -e "${YELLOW}⏳ Attente du démarrage des services...${NC}"
    sleep 15
}

# Fonction pour tester les services
test_services() {
    echo -e "${BLUE}🧪 Test des services...${NC}"
    
    local services=(
        "http://localhost:5062/health:SuperSmartMatch V1"
        "http://localhost:5070/health:SuperSmartMatch V2"
        "http://localhost:5052/health:Nexten Matcher"
    )
    
    local ready_count=0
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service_info"
        
        echo -n "   Testing $name... "
        
        if curl -s "$url" &>/dev/null; then
            echo -e "${GREEN}✅ OK${NC}"
            ((ready_count++))
        else
            echo -e "${YELLOW}⏳ En cours${NC}"
        fi
    done
    
    if [ $ready_count -eq 3 ]; then
        echo -e "${GREEN}🎉 Tous les services sont prêts!${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ ${ready_count}/3 services prêts${NC}"
        return 1
    fi
}

# Fonction pour lancer les tests PROMPT 2
run_prompt2_tests() {
    echo -e "${BLUE}📄 Lancement des tests PROMPT 2...${NC}"
    
    # Test avec le script officiel
    if [ -f "scripts/validate-prompt2-now.js" ]; then
        echo -e "${BLUE}🔍 Test officiel PROMPT 2...${NC}"
        node scripts/validate-prompt2-now.js
    fi
    
    echo ""
    echo -e "${BLUE}🧪 Tests avec données réelles...${NC}"
    
    # Tests CV et Job réels
    if [ -f "scripts/test_real_cv.sh" ]; then
        echo -e "${YELLOW}📄 Test parsing CV réel...${NC}"
        chmod +x scripts/test_real_cv.sh
        ./scripts/test_real_cv.sh
    fi
    
    if [ -f "scripts/test_real_job.sh" ]; then
        echo -e "${YELLOW}💼 Test parsing Job réel...${NC}"
        chmod +x scripts/test_real_job.sh  
        ./scripts/test_real_job.sh
    fi
}

# Fonction pour afficher les informations finales
show_info() {
    echo ""
    echo -e "${GREEN}🎉 SuperSmartMatch V2 - PROMPT 2 Ready!${NC}"
    echo ""
    echo -e "${BLUE}📊 Services disponibles:${NC}"
    echo "   • SuperSmartMatch V1: http://localhost:5062"
    echo "   • SuperSmartMatch V2: http://localhost:5070" 
    echo "   • Nexten Matcher: http://localhost:5052"
    echo "   • Grafana Dashboard: http://localhost:3001 (admin/admin)"
    echo "   • Prometheus: http://localhost:9091"
    echo ""
    echo -e "${BLUE}🧪 Commandes de test:${NC}"
    echo "   • Test PROMPT 2 complet: node scripts/validate-prompt2-now.js"
    echo "   • Test CV réel: ./scripts/test_real_cv.sh"
    echo "   • Test Job réel: ./scripts/test_real_job.sh" 
    echo "   • Test standalone: node test-prompt2-standalone.js"
    echo ""
    echo -e "${BLUE}🔧 Gestion:${NC}"
    echo "   • Voir logs: docker-compose -f docker-compose.fixed.yml logs"
    echo "   • Arrêter: docker-compose -f docker-compose.fixed.yml down"
    echo "   • Redémarrer: ./quick-start-prompt2.sh"
}

# Menu principal
main_menu() {
    echo ""
    echo -e "${BLUE}Choisissez une option:${NC}"
    echo "1. 🚀 Démarrage complet (Docker + Tests)"
    echo "2. 🧪 Test standalone uniquement (sans Docker)"
    echo "3. 🔧 Services seulement (sans tests)"
    echo "4. 📊 Afficher les informations"
    echo "5. 🛑 Arrêter les services"
    echo ""
    read -p "Votre choix (1-5): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            check_docker
            start_services
            if test_services; then
                run_prompt2_tests
            fi
            show_info
            ;;
        2)
            echo -e "${GREEN}🎯 Lancement du test standalone...${NC}"
            chmod +x test-prompt2-standalone.js
            node test-prompt2-standalone.js
            ;;
        3)
            check_docker
            start_services
            test_services
            show_info
            ;;
        4)
            show_info
            ;;
        5)
            echo -e "${YELLOW}🛑 Arrêt des services...${NC}"
            docker-compose -f docker-compose.fixed.yml down
            echo -e "${GREEN}✅ Services arrêtés${NC}"
            ;;
        *)
            echo -e "${RED}❌ Option invalide${NC}"
            main_menu
            ;;
    esac
}

# Arguments en ligne de commande
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Afficher cette aide"
        echo "  --standalone   Test standalone uniquement"
        echo "  --services     Démarrer services seulement"
        echo "  --test         Lancer tests seulement"
        echo "  --stop         Arrêter les services"
        echo "  --info         Afficher les informations"
        echo ""
        exit 0
        ;;
    --standalone)
        chmod +x test-prompt2-standalone.js
        node test-prompt2-standalone.js
        ;;
    --services)
        check_docker
        start_services
        test_services
        show_info
        ;;
    --test)
        run_prompt2_tests
        ;;
    --stop)
        docker-compose -f docker-compose.fixed.yml down
        echo -e "${GREEN}✅ Services arrêtés${NC}"
        ;;
    --info)
        show_info
        ;;
    *)
        main_menu
        ;;
esac
