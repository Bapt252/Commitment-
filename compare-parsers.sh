#!/bin/bash
# Script pour comparer les résultats du mock parser et du parser réel

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Créer un dossier temporaire pour les résultats
TEMP_DIR=$(mktemp -d)
MOCK_OUTPUT="$TEMP_DIR/mock_output.json"
REAL_OUTPUT="$TEMP_DIR/real_output.json"
CV_FILE="$1"

# Vérifier si un fichier CV est fourni en argument
if [ -z "$CV_FILE" ]; then
    echo -e "${YELLOW}Aucun fichier CV fourni. Utilisation de l'exemple par défaut.${NC}"
    
    # Créer un CV exemple si aucun n'est fourni
    CV_FILE="$TEMP_DIR/example_cv.txt"
    cat << EOF > "$CV_FILE"
JOHN DOE
Software Engineer
john.doe@example.com | +33 6 12 34 56 78 | Paris, France | LinkedIn: linkedin.com/in/johndoe

COMPÉTENCES
- Langages: Python, JavaScript, Java, C++
- Frameworks: React, Django, Spring Boot
- DevOps: Docker, Kubernetes, AWS, CI/CD
- Bases de données: PostgreSQL, MongoDB, Redis
- Outils: Git, JIRA, Confluence

EXPÉRIENCE PROFESSIONNELLE
Senior Software Engineer | TechCorp | Mars 2020 - Avril 2023
- Développement d'applications web scalables avec React et Django
- Mise en place d'une architecture microservices avec Docker et Kubernetes
- Optimisation des performances frontend, réduction de 40% du temps de chargement

Software Developer | InnoSoft | Janvier 2018 - Février 2020
- Développement de fonctionnalités backend avec Java et Spring Boot
- Conception et implémentation d'une API REST pour l'intégration mobile
- Collaboration avec l'équipe UX pour améliorer l'expérience utilisateur

FORMATION
Master en Informatique, spécialité IA | Université de Paris | 2016-2018
Licence en Informatique | Université de Lyon | 2013-2016

LANGUES
Français (natif), Anglais (courant), Espagnol (intermédiaire)

PROJETS PERSONNELS
- Développement d'une application mobile de partage de recettes (React Native)
- Contribution open-source à plusieurs projets Python
EOF

    echo -e "${GREEN}✓ CV exemple créé avec succès${NC}"
fi

echo -e "${BLUE}=== Comparaison des parsers de CV ===${NC}"

# 1. Configurer pour utiliser le mock parser
echo -e "${BLUE}Configuration du mock parser...${NC}"
sed -i "s/USE_MOCK_PARSER=false/USE_MOCK_PARSER=true/" "cv-parser-service/.env"
docker-compose -f docker-compose.yml restart nexten-cv-parser
sleep 5
echo -e "${GREEN}✓ Mock parser configuré${NC}"

# 2. Tester le mock parser
echo -e "${BLUE}Test du mock parser...${NC}"
curl -s -X POST \
  http://localhost:8000/api/parse-cv/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$CV_FILE" > "$MOCK_OUTPUT"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Mock parser testé avec succès${NC}"
else
    echo -e "${RED}Erreur lors du test du mock parser${NC}"
    exit 1
fi

# 3. Configurer pour utiliser le parser réel
echo -e "${BLUE}Configuration du parser réel...${NC}"
sed -i "s/USE_MOCK_PARSER=true/USE_MOCK_PARSER=false/" "cv-parser-service/.env"
docker-compose -f docker-compose.yml restart nexten-cv-parser
sleep 5
echo -e "${GREEN}✓ Parser réel configuré${NC}"

# 4. Tester le parser réel
echo -e "${BLUE}Test du parser réel...${NC}"
curl -s -X POST \
  http://localhost:8000/api/parse-cv/ \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$CV_FILE" > "$REAL_OUTPUT"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Parser réel testé avec succès${NC}"
else
    echo -e "${RED}Erreur lors du test du parser réel${NC}"
    exit 1
fi

# 5. Comparer les résultats
echo -e "${BLUE}=== Résultats de la comparaison ===${NC}"
echo -e "${YELLOW}Résultat du mock parser:${NC}"
cat "$MOCK_OUTPUT" | jq .

echo ""
echo -e "${YELLOW}Résultat du parser réel:${NC}"
cat "$REAL_OUTPUT" | jq .

# 6. Sauvegarder les résultats
RESULTS_DIR="parser_comparison_results"
mkdir -p "$RESULTS_DIR"
cp "$MOCK_OUTPUT" "$RESULTS_DIR/mock_output.json"
cp "$REAL_OUTPUT" "$RESULTS_DIR/real_output.json"

echo ""
echo -e "${GREEN}✓ Comparaison terminée${NC}"
echo -e "${BLUE}Les résultats ont été sauvegardés dans le dossier $RESULTS_DIR${NC}"

# Nettoyage
rm -rf "$TEMP_DIR"
