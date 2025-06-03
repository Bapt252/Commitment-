#!/bin/bash

# Session A3 - Commandes rapides pendant l'attente de validation

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}🚀 SESSION A3 - COMMANDES RAPIDES${NC}"
echo -e "${CYAN}================================${NC}"

echo -e "\n${BLUE}1. 📊 ÉTAT DES SERVICES${NC}"
services=("5050:API-Principal" "5051:CV-Parser" "5052:Matching-API")

for service in "${services[@]}"; do
    port=$(echo "$service" | cut -d: -f1)
    name=$(echo "$service" | cut -d: -f2)
    
    if curl -s -f "http://localhost:$port/health" --max-time 2 >/dev/null 2>&1; then
        echo -e "  ✅ $name (port $port)"
    else
        echo -e "  ❌ $name (port $port)"
    fi
done

echo -e "\n${BLUE}2. 🔍 PROCESSUS VALIDATION${NC}"
validation_pid=$(pgrep -f "validation-final.sh" 2>/dev/null || echo "")
if [ -n "$validation_pid" ]; then
    echo -e "✅ Script validation-final.sh en cours (PID: $validation_pid)"
else
    echo -e "❌ Aucune validation en cours"
fi

echo -e "\n${BLUE}3. 💡 COMMANDES UTILES${NC}"
echo -e "${GREEN}Pendant l'attente de validation:${NC}"
echo -e "  ${CYAN}./check-validation-status.sh${NC}     - Vérifier l'avancement"
echo -e "  ${CYAN}docker-compose logs -f --tail 10${NC} - Logs en temps réel"

echo -e "\n${GREEN}Après la validation:${NC}"
echo -e "  ${CYAN}./monitor-performance.sh${NC}         - Monitoring post-optimisation"
echo -e "  ${CYAN}git add . && git commit -m 'Session A3 completed'${NC} - Commit des résultats"
