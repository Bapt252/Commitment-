#!/bin/sh

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "${BLUE}🔍 NexTen Requirements Consistency Checker${NC}\n"

# Fichiers requirements à vérifier
requirements_files="cv-parser-service/requirements.txt matching-service/requirements.txt backend/requirements.txt"

# Vérifier que tous les fichiers existent
for file in $requirements_files; do
    if [ ! -f "$file" ]; then
        echo "${RED}❌ $file not found!${NC}"
        exit 1
    fi
done

# Créer un fichier temporaire pour stocker les dépendances
tmp_file=$(mktemp)
tmp_versions=$(mktemp)

# Extraire les dépendances de chaque fichier
for file in $requirements_files; do
    service=$(echo "$file" | cut -d'/' -f1)
    
    # Extraire les packages et versions, en ignorant les commentaires et lignes vides
    grep -v '^#' "$file" | grep -v '^[[:space:]]*$' | while IFS= read -r line; do
        if echo "$line" | grep -q '=='; then
            package=$(echo "$line" | sed 's/\[.*\]//' | cut -d'=' -f1)
            version=$(echo "$line" | cut -d'=' -f3)
            echo "$package|$service|$version" >> "$tmp_file"
        fi
    done
done

# Analyser les incohérences
echo "${YELLOW}📊 Analyzing version inconsistencies...${NC}\n"

# Trouver les packages communs avec des versions différentes
cat "$tmp_file" | cut -d'|' -f1 | sort -u | while read -r package; do
    # Compter le nombre de versions différentes pour ce package
    version_count=$(grep "^$package|" "$tmp_file" | cut -d'|' -f3 | sort -u | wc -l | tr -d ' ')
    
    if [ "$version_count" -gt 1 ]; then
        if [ "$has_inconsistencies" != "true" ]; then
            echo "${RED}⚠️  Version inconsistencies found:${NC}"
            has_inconsistencies=true
        fi
        echo "${YELLOW}$package:${NC}"
        grep "^$package|" "$tmp_file" | while IFS='|' read -r pkg service version; do
            echo "  ${BLUE}$service:${NC} $version"
        done
        echo ""
    fi
done

# Si aucune incohérence n'a été trouvée
if [ "$has_inconsistencies" != "true" ]; then
    echo "${GREEN}✅ No version inconsistencies found!${NC}"
else
    echo "${YELLOW}💡 Suggestion: Consider aligning package versions across services${NC}"
    echo "${YELLOW}💡 This will help prevent compatibility issues${NC}"
fi

# Vérifier les dépendances redondantes
echo "\n${YELLOW}📦 Checking for redundant dependencies...${NC}\n"

# PyPDF2 vs pypdf
if grep -q "PyPDF2" "cv-parser-service/requirements.txt" && grep -q "pypdf" "cv-parser-service/requirements.txt"; then
    echo "${YELLOW}⚠️  cv-parser-service has both PyPDF2 and pypdf${NC}"
    echo "${BLUE}💡 pypdf is the new name for PyPDF2, consider using only one${NC}\n"
fi

# Flask vs FastAPI in matching-service
if grep -q "flask=" "matching-service/requirements.txt" && grep -q "fastapi=" "matching-service/requirements.txt"; then
    echo "${YELLOW}⚠️  matching-service has both Flask and FastAPI${NC}"
    echo "${BLUE}💡 Consider choosing one framework for consistency${NC}\n"
fi

# Vérifier les modèles spaCy
echo "${YELLOW}🧠 Checking spaCy models...${NC}\n"
if grep -q "spacy=" "backend/requirements.txt"; then
    # Vérifier dans requirements.txt
    fr_model_found=false
    en_model_found=false
    
    if grep -q "fr-core-news" "backend/requirements.txt" || grep -q "fr_core_news" "backend/requirements.txt"; then
        fr_model_found=true
    fi
    
    if grep -q "en-core-web" "backend/requirements.txt" || grep -q "en_core_web" "backend/requirements.txt"; then
        en_model_found=true
    fi
    
    # Vérifier dans requirements.docker.txt
    if [ -f "backend/requirements.docker.txt" ]; then
        if grep -q "fr-core-news" "backend/requirements.docker.txt" || grep -q "fr_core_news" "backend/requirements.docker.txt"; then
            fr_model_docker=true
        fi
        
        if grep -q "en-core-web" "backend/requirements.docker.txt" || grep -q "en_core_web" "backend/requirements.docker.txt"; then
            en_model_docker=true
        fi
    fi
    
    if [ "$fr_model_found" = "false" ] && [ "$en_model_found" = "false" ]; then
        echo "${YELLOW}⚠️  backend uses spaCy but doesn't include language models in requirements.txt${NC}"
        if [ "$fr_model_docker" = "true" ] || [ "$en_model_docker" = "true" ]; then
            echo "${BLUE}💡 Models are only in requirements.docker.txt - consider adding them to requirements.txt${NC}\n"
        else
            echo "${BLUE}💡 Consider adding language models to requirements.txt or requirements.docker.txt${NC}\n"
        fi
    fi
fi

# Nettoyer les fichiers temporaires
rm -f "$tmp_file" "$tmp_versions"

echo "${GREEN}✨ Analysis complete!${NC}"
