#!/bin/bash

# Couleurs pour une meilleure lisibilité
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Vérification des fichiers sensibles suivis par Git...${NC}\n"

# Liste des motifs de fichiers sensibles
SENSITIVE_PATTERNS=(
  "\.env$"
  "\.env\."
  "secret"
  "password"
  "\.key$"
  "\.pem$"
  "\.cert$"
  "\.crt$"
  "credentials"
  "token"
  "api_key"
  "apikey"
  "auth"
)

# Initialiser un drapeau pour suivre si des fichiers sensibles ont été trouvés
SENSITIVE_FILES_FOUND=0

# Vérifier chaque motif
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
  # Rechercher des fichiers correspondant au motif
  files=$(git ls-files | grep -E "$pattern")
  
  # Si des fichiers sont trouvés, les afficher
  if [ -n "$files" ]; then
    echo -e "${RED}Fichiers sensibles potentiels (motif: $pattern) :${NC}"
    echo "$files"
    echo ""
    SENSITIVE_FILES_FOUND=1
  fi
done

# Vérification des fichiers potentiellement sensibles récemment ajoutés
echo -e "${YELLOW}Vérification des nouveaux fichiers potentiellement sensibles...${NC}\n"

# Obtenir les fichiers ajoutés mais pas encore commités
STAGED_FILES=$(git diff --cached --name-only)

# Si des fichiers sont en attente de commit
if [ -n "$STAGED_FILES" ]; then
  # Vérifier chaque motif
  for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    # Rechercher des fichiers correspondant au motif
    staged_sensitive=$(echo "$STAGED_FILES" | grep -E "$pattern")
    
    # Si des fichiers sont trouvés, les afficher
    if [ -n "$staged_sensitive" ]; then
      echo -e "${RED}ATTENTION: Fichiers sensibles potentiels sur le point d'être commit (motif: $pattern) :${NC}"
      echo "$staged_sensitive"
      echo ""
      SENSITIVE_FILES_FOUND=1
    fi
  done
fi

# Message final
if [ $SENSITIVE_FILES_FOUND -eq 0 ]; then
  echo -e "${GREEN}Aucun fichier sensible détecté dans le dépôt Git.${NC}"
  echo ""
  echo -e "${YELLOW}Rappel: Continuez à utiliser .gitignore pour éviter de commiter des fichiers sensibles.${NC}"
else
  echo -e "${RED}Des fichiers potentiellement sensibles ont été détectés!${NC}"
  echo ""
  echo -e "${YELLOW}Pour retirer un fichier du suivi Git sans le supprimer localement:${NC}"
  echo "  git rm --cached FICHIER"
  echo ""
  echo -e "${YELLOW}Puis assurez-vous que le fichier est listé dans .gitignore avant de commiter.${NC}"
fi

echo ""
echo -e "${YELLOW}Terminé.${NC}"