#!/bin/bash

# Script pour rendre tous les scripts sh exécutables

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Rendre les scripts exécutables...${NC}"

# Liste des scripts à rendre exécutables
SCRIPTS=(
    "start-parser-with-api-key.sh"
    "compare-parsers.sh"
    "restart-cv-parser-real.sh"
    "test-real-parser.sh"
)

# Rendre chaque script exécutable
for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo -e "${GREEN}✓ $script est maintenant exécutable${NC}"
    else
        echo -e "Le script $script n'existe pas"
    fi
done

echo -e "${GREEN}Terminé!${NC}"
