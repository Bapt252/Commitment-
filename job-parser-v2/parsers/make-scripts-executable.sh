#!/bin/bash

# Script pour rendre tous les scripts sh exécutables
# Compatible avec macOS et Linux

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Rendre les scripts exécutables...${NC}"

# Liste des scripts à rendre exécutables
SCRIPTS=(
    "start-parser-with-api-key.sh"
    "compare-parsers.sh"
    "restart-cv-parser-real.sh"
    "test-real-parser.sh"
    "mac-test-cv.sh"
    "setup-openai-key.sh"
)

# Détection du système d'exploitation
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${YELLOW}Système macOS détecté${NC}"
else
    echo -e "${YELLOW}Système Linux détecté${NC}"
fi

# Vérifier les droits d'administrateur
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Note: Vous n'êtes pas en mode administrateur, utilisation de chmod pour modification des permissions${NC}"
    USE_SUDO=false
    # Vérifier si sudo est disponible
    if command -v sudo &> /dev/null; then
        echo -e "${YELLOW}sudo est disponible - utilisez sudo ./$0 pour exécuter avec des privilèges administrateur si nécessaire${NC}"
    fi
else
    USE_SUDO=true
    echo -e "${GREEN}Exécution avec privilèges administrateur${NC}"
fi

# Rendre chaque script exécutable
CHANGED=0
MISSING=0
for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if $USE_SUDO; then
            chmod +x "$script"
        else
            chmod +x "$script" 2>/dev/null || {
                echo -e "${RED}Échec de modification des permissions pour $script. Tentative avec sudo...${NC}"
                sudo chmod +x "$script" 2>/dev/null || {
                    echo -e "${RED}Impossible de rendre $script exécutable même avec sudo.${NC}"
                    continue
                }
            }
        fi
        echo -e "${GREEN}✓ $script est maintenant exécutable${NC}"
        CHANGED=$((CHANGED+1))
    else
        echo -e "${YELLOW}Le script $script n'existe pas${NC}"
        MISSING=$((MISSING+1))
    fi
done

# Rendre tous les autres scripts .sh exécutables
OTHER_SCRIPTS=$(find . -name "*.sh" | grep -v -E "$(echo "${SCRIPTS[@]}" | sed 's/ /|/g')")
OTHER_COUNT=0

if [ -n "$OTHER_SCRIPTS" ]; then
    echo -e "${BLUE}Détection d'autres scripts .sh...${NC}"
    for script in $OTHER_SCRIPTS; do
        if $USE_SUDO; then
            chmod +x "$script"
        else
            chmod +x "$script" 2>/dev/null || {
                sudo chmod +x "$script" 2>/dev/null || continue
            }
        fi
        echo -e "${GREEN}✓ $script est maintenant exécutable${NC}"
        OTHER_COUNT=$((OTHER_COUNT+1))
    done
fi

# Résumé
echo -e "\n${BLUE}=== Résumé ===${NC}"
echo -e "${GREEN}✓ $CHANGED scripts principaux rendus exécutables${NC}"
if [ $MISSING -gt 0 ]; then
    echo -e "${YELLOW}$MISSING scripts principaux non trouvés${NC}"
fi
if [ $OTHER_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓ $OTHER_COUNT scripts supplémentaires rendus exécutables${NC}"
fi

echo -e "${GREEN}Terminé!${NC}"
echo -e "${BLUE}Vous pouvez maintenant exécuter ./mac-test-cv.sh MonSuperCV.pdf pour tester votre CV${NC}"
