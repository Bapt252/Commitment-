#!/bin/bash
# Script de test pour SmartMatch
# Auteur: Claude/Anthropic
# Date: 14/05/2025

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Test du système Nexten SmartMatch ===${NC}"
echo "Ce script exécute les tests unitaires et un test complet du système SmartMatch."

# Vérifier si la clé API Google Maps est définie
if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
    echo -e "${YELLOW}Aucune clé API Google Maps n'est définie. Utilisation de la clé par défaut.${NC}"
    export GOOGLE_MAPS_API_KEY="AIzaSyC5cpNgAXN1U0L14pB4HmD7BvP8pD6K8t8"
fi

# Fonction pour vérifier la présence des dépendances
check_dependencies() {
    echo -e "${BLUE}Vérification des dépendances...${NC}"
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python 3 n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
        exit 1
    fi
    
    # Vérifier pip
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}pip3 n'est pas installé. Veuillez l'installer avant de continuer.${NC}"
        exit 1
    fi
    
    # Vérifier les dépendances Python
    echo "Vérification des packages Python requis..."
    required_packages=(
        "numpy"
        "pandas"
        "scikit-learn"
        "matplotlib"
        "nltk"
        "requests"
    )
    
    missing_packages=()
    for package in "${required_packages[@]}"; do
        if ! pip3 list | grep -q "$package"; then
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -gt 0 ]; then
        echo -e "${YELLOW}Packages manquants: ${missing_packages[*]}${NC}"
        echo "Installation des packages manquants..."
        pip3 install ${missing_packages[@]}
    else
        echo -e "${GREEN}Toutes les dépendances sont installées.${NC}"
    fi
}

# Fonction pour exécuter les tests unitaires
run_unit_tests() {
    echo -e "${BLUE}Exécution des tests unitaires...${NC}"
    cd matching-service
    python3 test_smartmatch_unit.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Tests unitaires réussis!${NC}"
    else
        echo -e "${RED}Échec des tests unitaires. Veuillez consulter les messages d'erreur ci-dessus.${NC}"
        exit 1
    fi
}

# Fonction pour exécuter le test complet
run_comprehensive_test() {
    echo -e "${BLUE}Exécution du test complet...${NC}"
    cd matching-service
    python3 test_smartmatch.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Test complet réussi!${NC}"
        echo -e "Les résultats ont été sauvegardés dans les fichiers suivants:"
        echo -e "- matching_results.csv: Données brutes des résultats"
        echo -e "- match_radar_*.png: Graphiques radar des meilleurs matchs"
        echo -e "- category_comparison.png: Comparaison des scores par catégorie"
        echo -e "- matching_heatmap.png: Heatmap des scores de matching"
    else
        echo -e "${RED}Échec du test complet. Veuillez consulter les messages d'erreur ci-dessus.${NC}"
        exit 1
    fi
}

# Menu principal
show_menu() {
    echo -e "${BLUE}=== Menu de test SmartMatch ===${NC}"
    echo "1. Vérifier les dépendances"
    echo "2. Exécuter les tests unitaires"
    echo "3. Exécuter le test complet"
    echo "4. Exécuter tous les tests"
    echo "5. Quitter"
    echo ""
    echo -n "Votre choix: "
    read choice
    
    case $choice in
        1)
            check_dependencies
            ;;
        2)
            check_dependencies
            run_unit_tests
            ;;
        3)
            check_dependencies
            run_comprehensive_test
            ;;
        4)
            check_dependencies
            run_unit_tests
            run_comprehensive_test
            ;;
        5)
            echo -e "${GREEN}Au revoir!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Choix invalide. Veuillez réessayer.${NC}"
            ;;
    esac
    
    echo ""
    show_menu
}

# Démarrer le script
show_menu
