#!/bin/bash

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔍 NexTen Requirements Consistency Checker${NC}\n"

# Array des fichiers requirements à vérifier
declare -a requirements_files=(
    "cv-parser-service/requirements.txt"
    "matching-service/requirements.txt" 
    "backend/requirements.txt"
)

# Vérifier que tous les fichiers existent
for file in "${requirements_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ $file not found!${NC}"
        exit 1
    fi
done

# Extraire les dépendances de chaque fichier
declare -A deps_by_service
for file in "${requirements_files[@]}"; do
    service=$(echo "$file" | cut -d'/' -f1)
    while IFS= read -r line; do
        # Ignorer les commentaires et lignes vides
        if [[ ! $line =~ ^#.*$ ]] && [[ ! -z $line ]]; then
            # Extraire le nom du package et la version
            if [[ $line =~ ^([a-zA-Z0-9_-]+)(\[.*\])?==(.+)$ ]]; then
                package="${BASH_REMATCH[1]}"
                version="${BASH_REMATCH[3]}"
                deps_by_service["$service:$package"]="$version"
            fi
        fi
    done < "$file"
done

# Analyser les incohérences
echo -e "${YELLOW}📊 Analyzing version inconsistencies...${NC}\n"

# Trouver les packages communs avec des versions différentes
declare -A packages
for key in "${!deps_by_service[@]}"; do
    service="${key%%:*}"
    package="${key#*:}"
    version="${deps_by_service[$key]}"
    
    if [ -z "${packages[$package]}" ]; then
        packages[$package]="$service=$version"
    else
        packages[$package]="${packages[$package]} $service=$version"
    fi
done

# Afficher les incohérences
has_inconsistencies=false
for package in "${!packages[@]}"; do
    versions="${packages[$package]}"
    version_count=$(echo "$versions" | tr ' ' '\n' | cut -d'=' -f2 | sort -u | wc -l)
    
    if [ "$version_count" -gt 1 ]; then
        if [ "$has_inconsistencies" = false ]; then
            echo -e "${RED}⚠️  Version inconsistencies found:${NC}"
            has_inconsistencies=true
        fi
        echo -e "${YELLOW}$package:${NC}"
        echo "$versions" | tr ' ' '\n' | while read -r entry; do
            service=$(echo "$entry" | cut -d'=' -f1)
            version=$(echo "$entry" | cut -d'=' -f2)
            echo -e "  ${BLUE}$service:${NC} $version"
        done
        echo ""
    fi
done

if [ "$has_inconsistencies" = false ]; then
    echo -e "${GREEN}✅ No version inconsistencies found!${NC}"
else
    echo -e "${YELLOW}💡 Suggestion: Consider aligning package versions across services${NC}"
    echo -e "${YELLOW}💡 This will help prevent compatibility issues${NC}"
fi

# Vérifier les dépendances redondantes
echo -e "\n${YELLOW}📦 Checking for redundant dependencies...${NC}\n"

# PyPDF2 vs pypdf
if grep -q "PyPDF2" "cv-parser-service/requirements.txt" && grep -q "pypdf" "cv-parser-service/requirements.txt"; then
    echo -e "${YELLOW}⚠️  cv-parser-service has both PyPDF2 and pypdf${NC}"
    echo -e "${BLUE}💡 pypdf is the new name for PyPDF2, consider using only one${NC}\n"
fi

# Flask vs FastAPI in matching-service
if grep -q "flask=" "matching-service/requirements.txt" && grep -q "fastapi=" "matching-service/requirements.txt"; then
    echo -e "${YELLOW}⚠️  matching-service has both Flask and FastAPI${NC}"
    echo -e "${BLUE}💡 Consider choosing one framework for consistency${NC}\n"
fi

# Vérifier les modèles spaCy
echo -e "${YELLOW}🧠 Checking spaCy models...${NC}\n"
if grep -q "spacy=" "backend/requirements.txt"; then
    if ! grep -q "fr-core-news" "backend/requirements.txt" && ! grep -q "en-core-web" "backend/requirements.txt"; then
        echo -e "${YELLOW}⚠️  backend uses spaCy but doesn't include language models in requirements.txt${NC}"
        echo -e "${BLUE}💡 Models are only in requirements.docker.txt - consider adding them to requirements.txt${NC}\n"
    fi
fi

echo -e "${GREEN}✨ Analysis complete!${NC}"
