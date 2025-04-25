#!/bin/bash

# Couleurs pour le terminal
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables par défaut
PRESERVE_VOLUMES=false
NO_CACHE=true
FORCE=false
SERVICES_TO_BUILD=""

# Fonction d'aide
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -p, --preserve-volumes  Ne pas supprimer les volumes Docker"
    echo "  -c, --cache            Utiliser le cache Docker pour la construction"
    echo "  -f, --force            Ne pas demander de confirmation"
    echo "  -s, --services         Services spécifiques à reconstruire (ex: 'cv-parser,matching')"
    echo "  -h, --help             Afficher cette aide"
    echo ""
    exit 0
}

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--preserve-volumes)
            PRESERVE_VOLUMES=true
            shift
            ;;
        -c|--cache)
            NO_CACHE=false
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -s|--services)
            SERVICES_TO_BUILD="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo -e "${RED}Option inconnue: $1${NC}"
            show_help
            ;;
    esac
done

# Vérifier les prérequis
echo -e "${BLUE}🔍 Vérification des prérequis...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé!${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas installé!${NC}"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Le daemon Docker n'est pas démarré ou vous n'avez pas les permissions!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prérequis OK${NC}\n"

# Confirmation
if [ "$FORCE" = false ]; then
    echo -e "${YELLOW}⚠️  Attention: Cette opération va reconstruire tous les services.${NC}"
    if [ "$PRESERVE_VOLUMES" = false ]; then
        echo -e "${RED}⚠️  Les volumes Docker seront supprimés (perte de données potentielle).${NC}"
    fi
    echo -e "${YELLOW}Voulez-vous continuer? (y/n)${NC}"
    read -r confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Opération annulée.${NC}"
        exit 0
    fi
fi

echo -e "${YELLOW}🚀 Starting NexTen Project Rebuild...${NC}\n"

# Étape 1: Arrêter les services en cours
echo -e "${GREEN}1. Stopping running services...${NC}"
docker-compose down --remove-orphans
echo -e "${GREEN}✓ Services stopped${NC}\n"

# Étape 2: Supprimer les volumes obsolètes (si non préservés)
if [ "$PRESERVE_VOLUMES" = false ]; then
    echo -e "${GREEN}2. Removing obsolete volumes...${NC}"
    docker volume prune -f
    echo -e "${GREEN}✓ Volumes cleaned${NC}\n"
else
    echo -e "${YELLOW}2. Skipping volume removal (--preserve-volumes)${NC}\n"
fi

# Étape 3: Supprimer les images existantes
echo -e "${GREEN}3. Removing existing images...${NC}"
docker-compose rm -f
docker image prune -f
echo -e "${GREEN}✓ Images cleaned${NC}\n"

# Étape 4: Vérifier les fichiers requirements.txt
echo -e "${GREEN}4. Checking requirements.txt files...${NC}"
required_files=("cv-parser-service/requirements.txt" "matching-service/requirements.txt" "backend/requirements.txt")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ $file not found!${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✓ All requirements.txt files found${NC}\n"

# Étape 5: Rebuild avec ou sans cache
echo -e "${GREEN}5. Rebuilding services...${NC}"
BUILD_CMD="docker-compose build"
if [ "$NO_CACHE" = true ]; then
    BUILD_CMD="$BUILD_CMD --no-cache"
fi
if [ -n "$SERVICES_TO_BUILD" ]; then
    BUILD_CMD="$BUILD_CMD $SERVICES_TO_BUILD"
fi

eval $BUILD_CMD
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed! Check the logs above.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Build successful${NC}\n"

# Étape 6: Démarrer les services
echo -e "${GREEN}6. Starting services...${NC}"
docker-compose up -d
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to start services!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Services started${NC}\n"

# Étape 7: Attendre que les services soient prêts
echo -e "${GREEN}7. Waiting for services to be ready...${NC}"
sleep 10
echo -e "${GREEN}✓ Services should be ready${NC}\n"

# Étape 8: Vérifier le statut des containers
echo -e "${GREEN}8. Checking container status...${NC}"
docker-compose ps
echo ""

# Vérifier la santé des services
echo -e "${GREEN}9. Checking service health...${NC}"
unhealthy=$(docker-compose ps -q | xargs docker inspect --format='{{.State.Health.Status}} {{.Name}}' | grep -v healthy | grep -v none)
if [ ! -z "$unhealthy" ]; then
    echo -e "${RED}⚠️  Some services are not healthy:${NC}"
    echo "$unhealthy"
else
    echo -e "${GREEN}✓ All services are healthy${NC}\n"
fi

# Étape 10: Afficher les logs pour debug (optionnel)
echo -e "${YELLOW}📋 Do you want to see the logs? (y/n)${NC}"
read -r answer
if [ "$answer" = "y" ]; then
    docker-compose logs -f --tail=100
fi

echo -e "\n${GREEN}✅ NexTen Project rebuild completed successfully!${NC}"
echo -e "${YELLOW}🌐 Your services should now be running without errors.${NC}"
echo -e "${YELLOW}📊 Check the container status above.${NC}"
