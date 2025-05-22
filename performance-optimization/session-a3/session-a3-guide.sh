#!/bin/bash

# Session A3 - Guide rapide et assistant de commandes
# Aide à naviguer facilement dans les scripts et voir l'état actuel

set -euo pipefail

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${CYAN}🎯 SESSION A3 - GUIDE RAPIDE & ASSISTANT${NC}"
echo -e "${CYAN}=======================================${NC}"
echo ""
echo -e "${PURPLE}📚 Philosophy: \"Measure first, optimize second, validate always\"${NC}"
echo ""

# Fonction d'aide
show_usage() {
    echo -e "${YELLOW}Usage: $0 [option]${NC}"
    echo ""
    echo -e "${YELLOW}Options disponibles:${NC}"
    echo -e "  ${GREEN}status${NC}        - Afficher l'état actuel de la Session A3"
    echo -e "  ${GREEN}run${NC}           - Lancer la Session A3 complète"
    echo -e "  ${GREEN}validate${NC}      - Lancer uniquement la validation finale"
    echo -e "  ${GREEN}monitor${NC}       - Lancer le monitoring de performance"
    echo -e "  ${GREEN}check${NC}         - Vérifier le statut de validation"
    echo -e "  ${GREEN}report${NC}        - Afficher le dernier rapport"
    echo -e "  ${GREEN}clean${NC}         - Nettoyer les anciens résultats"
    echo -e "  ${GREEN}help${NC}          - Afficher cette aide"
    echo ""
    echo -e "${CYAN}Exemple: $0 status${NC}"
}

# Vérifier les arguments
ACTION="${1:-help}"

case "$ACTION" in
    "status")
        echo -e "${BLUE}📊 ÉTAT ACTUEL SESSION A3${NC}"
        echo -e "${BLUE}=========================${NC}"
        echo ""
        
        # Vérifier si validation en cours
        if pgrep -f "validation-final.sh" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Validation finale en cours d'exécution${NC}"
        else
            echo -e "${YELLOW}⏸️  Aucune validation en cours${NC}"
        fi
        
        # Vérifier les services
        echo -e "${BLUE}Services Status:${NC}"
        services=(
            "http://localhost:5050/health:API-Principal"
            "http://localhost:5051/health:CV-Parser"
            "http://localhost:5052/health:Matching-API"
        )
        
        for service in "${services[@]}"; do
            url=$(echo "$service" | cut -d: -f1-2)
            name=$(echo "$service" | cut -d: -f3)
            if curl -s -f "$url" --max-time 3 >/dev/null 2>&1; then
                echo -e "  ✅ $name"
            else
                echo -e "  ❌ $name"
            fi
        done
        
        # Derniers résultats
        echo ""
        echo -e "${BLUE}Derniers résultats:${NC}"
        validation_dirs=($(find . -maxdepth 1 -type d -name "validation-*" 2>/dev/null | sort -r | head -3))
        if [ ${#validation_dirs[@]} -gt 0 ]; then
            for dir in "${validation_dirs[@]}"; do
                echo -e "  📁 $(basename "$dir")"
            done
        else
            echo -e "  ${YELLOW}Aucun résultat de validation trouvé${NC}"
        fi
        
        # Rapport final
        if [ -d "final-report" ]; then
            latest_report=$(find final-report -name "session_a3_final_report_*.md" 2>/dev/null | sort -r | head -1)
            if [ -n "$latest_report" ]; then
                echo -e "  📄 Rapport final: $(basename "$latest_report")"
            fi
        fi
        ;;
        
    "run")
        echo -e "${GREEN}🚀 LANCEMENT SESSION A3 COMPLÈTE${NC}"
        echo -e "${GREEN}=================================${NC}"
        echo ""
        echo -e "${YELLOW}Cette opération va lancer toutes les phases de la Session A3:${NC}"
        echo -e "  Phase 0: Baseline Profiling"
        echo -e "  Phase 1: Database Optimization"
        echo -e "  Phase 2: Redis Optimization"
        echo -e "  Phase 3: Docker Optimization"
        echo -e "  Phase 4: Code Optimization"
        echo -e "  Phase 5: Validation Finale"
        echo ""
        read -p "Continuer? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${GREEN}Lancement de session-a3-master.sh...${NC}"
            ./session-a3-master.sh
        else
            echo -e "${YELLOW}Opération annulée${NC}"
        fi
        ;;
        
    "validate")
        echo -e "${GREEN}✅ LANCEMENT VALIDATION FINALE${NC}"
        echo -e "${GREEN}==============================${NC}"
        echo ""
        if pgrep -f "validation-final.sh" >/dev/null 2>&1; then
            echo -e "${YELLOW}⚠️  Une validation est déjà en cours!${NC}"
            echo -e "${YELLOW}Utilisez '$0 check' pour vérifier l'avancement${NC}"
        else
            echo -e "${GREEN}Lancement de validation-final.sh...${NC}"
            ./validation-final.sh
        fi
        ;;
        
    "monitor")
        echo -e "${GREEN}📊 LANCEMENT MONITORING PERFORMANCE${NC}"
        echo -e "${GREEN}===================================${NC}"
        echo ""
        if [ -f "monitor-performance.sh" ]; then
            ./monitor-performance.sh
        else
            echo -e "${RED}❌ Script monitor-performance.sh non trouvé${NC}"
        fi
        ;;
        
    "check")
        echo -e "${GREEN}🔍 VÉRIFICATION STATUT VALIDATION${NC}"
        echo -e "${GREEN}=================================${NC}"
        echo ""
        if [ -f "check-validation-status.sh" ]; then
            ./check-validation-status.sh
        else
            echo -e "${RED}❌ Script check-validation-status.sh non trouvé${NC}"
        fi
        ;;
        
    "report")
        echo -e "${GREEN}📄 AFFICHAGE DERNIER RAPPORT${NC}"
        echo -e "${GREEN}============================${NC}"
        echo ""
        if [ -d "final-report" ]; then
            latest_report=$(find final-report -name "session_a3_final_report_*.md" 2>/dev/null | sort -r | head -1)
            if [ -n "$latest_report" ]; then
                echo -e "${BLUE}Rapport: $(basename "$latest_report")${NC}"
                echo ""
                cat "$latest_report"
            else
                echo -e "${YELLOW}❌ Aucun rapport final trouvé${NC}"
            fi
        else
            echo -e "${YELLOW}❌ Dossier final-report non trouvé${NC}"
        fi
        ;;
        
    "clean")
        echo -e "${YELLOW}🧹 NETTOYAGE ANCIENS RÉSULTATS${NC}"
        echo -e "${YELLOW}==============================${NC}"
        echo ""
        echo -e "${YELLOW}Cette opération va supprimer:${NC}"
        echo -e "  - Tous les dossiers validation-*"
        echo -e "  - Le dossier final-report"
        echo ""
        read -p "Êtes-vous sûr? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${GREEN}Nettoyage en cours...${NC}"
            rm -rf validation-* final-report
            echo -e "${GREEN}✅ Nettoyage terminé${NC}"
        else
            echo -e "${YELLOW}Opération annulée${NC}"
        fi
        ;;
        
    "help"|*)
        show_usage
        echo ""
        echo -e "${BLUE}🎯 SESSION A3 OBJECTIFS:${NC}"
        echo -e "  🗄️  Database: -40% query time, +30% throughput"
        echo -e "  🚀 Redis: +50% hit rate, -30% memory usage"
        echo -e "  🐳 Containers: -30% image size, -20% runtime resources"
        echo -e "  💻 Code: -25% response time, async patterns"
        echo ""
        echo -e "${BLUE}📁 Structure Session A3:${NC}"
        echo -e "  baseline-profiling.sh      - Phase 0: Mesures initiales"
        echo -e "  database-optimization.sh   - Phase 1: Optimisation DB"
        echo -e "  redis-optimization.sh      - Phase 2: Optimisation Redis"
        echo -e "  docker-optimization.sh     - Phase 3: Optimisation containers"
        echo -e "  code-optimization.sh       - Phase 4: Optimisation code"
        echo -e "  validation-final.sh        - Phase 5: Validation complète"
        echo -e "  session-a3-master.sh       - Script maître (toutes phases)"
        echo -e "  monitor-performance.sh     - Monitoring continu"
        echo ""
        echo -e "${PURPLE}💡 Conseils:${NC}"
        echo -e "  1. Commencez par: $0 status"
        echo -e "  2. Si validation en cours: $0 check"
        echo -e "  3. Pour voir le rapport: $0 report"
        echo -e "  4. Pour monitoring: $0 monitor"
        ;;
esac

echo ""
echo -e "${CYAN}📚 Pour plus d'aide: $0 help${NC}"
echo -e "${CYAN}📁 Dossier Session A3: $(pwd)${NC}"
