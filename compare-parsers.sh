#!/bin/bash
# Script pour comparer les résultats du mock parser et du parser réel
# Version compatible avec macOS

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

# Fonction pour modifier le fichier .env selon le système d'exploitation
update_env_file() {
    local use_mock=$1
    local env_file="cv-parser-service/.env"
    
    # Vérifier si le fichier .env existe
    if [ ! -f "$env_file" ]; then
        echo -e "${RED}Erreur: Le fichier $env_file n'existe pas.${NC}"
        return 1
    fi
    
    # Modification compatible avec macOS ou Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if [ "$use_mock" = true ]; then
            sed -i '' 's/USE_MOCK_PARSER=false/USE_MOCK_PARSER=true/' "$env_file"
        else
            sed -i '' 's/USE_MOCK_PARSER=true/USE_MOCK_PARSER=false/' "$env_file"
        fi
    else
        # Linux
        if [ "$use_mock" = true ]; then
            sed -i 's/USE_MOCK_PARSER=false/USE_MOCK_PARSER=true/' "$env_file"
        else
            sed -i 's/USE_MOCK_PARSER=true/USE_MOCK_PARSER=false/' "$env_file"
        fi
    fi
    
    return 0
}

# Fonction pour redémarrer le service Docker s'il existe
restart_service() {
    local service_name="nexten-cv-parser"
    
    # Vérifier si le service existe
    if docker ps -a | grep -q $service_name; then
        echo -e "${BLUE}Redémarrage du service $service_name...${NC}"
        docker-compose restart $service_name 2>/dev/null || {
            echo -e "${YELLOW}Impossible de redémarrer avec docker-compose, essai avec docker restart...${NC}"
            docker restart $service_name 2>/dev/null || {
                echo -e "${YELLOW}Impossible de redémarrer le service. Le service sera ignoré.${NC}"
                return 1
            }
        }
        echo -e "${GREEN}✓ Service redémarré${NC}"
        sleep 3
    else
        echo -e "${YELLOW}Le service $service_name n'existe pas. Ignoré.${NC}"
        return 1
    fi
    
    return 0
}

# Vérifier si un fichier CV est fourni en argument
if [ -z "$CV_FILE" ]; then
    echo -e "${YELLOW}Aucun fichier CV fourni. Utilisation de l'exemple par défaut.${NC}"
    
    # Créer un CV exemple si aucun n'est fourni
    CV_FILE="$TEMP_DIR/example_cv.txt"
    if [ -f "example_cv.txt" ]; then
        # Utiliser le CV exemple existant s'il existe
        cp "example_cv.txt" "$CV_FILE"
    else
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
    fi

    echo -e "${GREEN}✓ CV exemple créé avec succès${NC}"
fi

echo -e "${BLUE}=== Comparaison des parsers de CV ===${NC}"

# Déterminer l'URL de l'API
API_BASE_URL="http://localhost:8000"
API_ENDPOINT="/api/parse-cv/"
API_URL="${API_BASE_URL}${API_ENDPOINT}"

# Vérifier si l'API est accessible
echo -e "${BLUE}Vérification de l'API...${NC}"
if ! curl -s "${API_BASE_URL}/health" > /dev/null; then
    echo -e "${YELLOW}L'API ne semble pas être accessible sur ${API_BASE_URL}/health${NC}"
    echo -e "${YELLOW}Essai sans le health endpoint...${NC}"
    if ! curl -s "${API_BASE_URL}" > /dev/null; then
        echo -e "${RED}L'API n'est pas accessible. Vérifiez que le service est en cours d'exécution.${NC}"
        echo -e "${YELLOW}Le test sera effectué sans redémarrer les services.${NC}"
        SKIP_SERVICE_RESTART=true
    fi
fi

# 1. Configurer pour utiliser le mock parser
echo -e "${BLUE}Configuration du mock parser...${NC}"
if [ -z "$SKIP_SERVICE_RESTART" ]; then
    update_env_file true
    restart_service
fi
echo -e "${GREEN}✓ Mock parser configuré${NC}"

# 2. Tester le mock parser
echo -e "${BLUE}Test du mock parser...${NC}"
curl -s -X POST \
  "${API_URL}" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$CV_FILE" > "$MOCK_OUTPUT"

if [ $? -eq 0 ] && [ -s "$MOCK_OUTPUT" ]; then
    echo -e "${GREEN}✓ Mock parser testé avec succès${NC}"
else
    echo -e "${RED}Erreur lors du test du mock parser${NC}"
    echo -e "${YELLOW}L'API est-elle accessible à ${API_URL}?${NC}"
fi

# 3. Configurer pour utiliser le parser réel
echo -e "${BLUE}Configuration du parser réel...${NC}"
if [ -z "$SKIP_SERVICE_RESTART" ]; then
    update_env_file false
    restart_service
fi
echo -e "${GREEN}✓ Parser réel configuré${NC}"

# 4. Tester le parser réel
echo -e "${BLUE}Test du parser réel...${NC}"
curl -s -X POST \
  "${API_URL}" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$CV_FILE" > "$REAL_OUTPUT"

if [ $? -eq 0 ] && [ -s "$REAL_OUTPUT" ]; then
    echo -e "${GREEN}✓ Parser réel testé avec succès${NC}"
else
    echo -e "${RED}Erreur lors du test du parser réel${NC}"
    echo -e "${YELLOW}L'API est-elle accessible à ${API_URL}?${NC}"
fi

# 5. Comparer les résultats
echo -e "${BLUE}=== Résultats de la comparaison ===${NC}"
echo -e "${YELLOW}Résultat du mock parser:${NC}"
if command -v jq &> /dev/null; then
    cat "$MOCK_OUTPUT" | jq
elif command -v python &> /dev/null; then
    cat "$MOCK_OUTPUT" | python -m json.tool
else
    cat "$MOCK_OUTPUT"
fi

echo ""
echo -e "${YELLOW}Résultat du parser réel:${NC}"
if command -v jq &> /dev/null; then
    cat "$REAL_OUTPUT" | jq
elif command -v python &> /dev/null; then
    cat "$REAL_OUTPUT" | python -m json.tool
else
    cat "$REAL_OUTPUT"
fi

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
