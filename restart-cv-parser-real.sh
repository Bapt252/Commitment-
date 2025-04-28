#!/bin/bash

# Couleurs pour l'affichage
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 Redémarrage du service cv-parser avec le vrai parser (non-mock)...${NC}"

# Vérifier si le fichier .env existe déjà
if [ -f "cv-parser-service/.env" ]; then
    echo -e "${YELLOW}🔍 Fichier .env existant détecté dans cv-parser-service${NC}"
    echo -e "${YELLOW}📝 Mise à jour du paramètre USE_MOCK_PARSER...${NC}"
    sed -i '' 's/USE_MOCK_PARSER=true/USE_MOCK_PARSER=false/g' cv-parser-service/.env
else
    echo -e "${YELLOW}📄 Création du fichier .env dans cv-parser-service${NC}"
    cat > cv-parser-service/.env << EOF
# Configuration du service de parsing CV

# Désactiver le mock parser pour utiliser le vrai parser
USE_MOCK_PARSER=false

# OpenAI API Key (requis pour le parsing CV si USE_MOCK_PARSER=false)
# OPENAI=your_openai_api_key_here

# Configuration de Redis (si utilisation de Redis)
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# Configuration de MinIO (si utilisation de MinIO)
MINIO_ENDPOINT=storage:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=cv-files

# API Settings
DEBUG=true
API_V1_STR=/api/v1
EOF
fi

# Arrêter les conteneurs liés au parsing CV
echo -e "${YELLOW}🛑 Arrêt des services liés au parsing CV...${NC}"
docker-compose stop cv-parser cv-parser-worker

# Reconstruire le service cv-parser pour appliquer les modifications
echo -e "${YELLOW}🏗️ Reconstruction du service cv-parser...${NC}"
docker-compose build cv-parser cv-parser-worker

# Démarrer le service cv-parser avec la nouvelle configuration
echo -e "${YELLOW}🚀 Démarrage des services...${NC}"
docker-compose up -d cv-parser cv-parser-worker

# Vérifier que le service est bien démarré
echo -e "${YELLOW}🔍 Vérification de l'état des services...${NC}"
sleep 5 # Attendre quelques secondes pour le démarrage
docker-compose ps cv-parser cv-parser-worker

# Vérifier les ports utilisés
echo -e "${YELLOW}📋 Ports utilisés par le service cv-parser:${NC}"
docker port nexten-cv-parser

# Vérifier les logs au démarrage
echo -e "${YELLOW}📊 Dernières lignes de logs:${NC}"
docker logs nexten-cv-parser --tail 10

# Guide d'utilisation
echo -e "\n${GREEN}✅ Redémarrage terminé! Le service utilise maintenant le vrai parser (non-mock).${NC}"
echo -e "${BLUE}🔧 Pour tester le service, utilisez:${NC}"
echo -e "./parse_cv_simple.sh --refresh ~/Desktop/MonSuperCV.pdf"
echo -e "# ou directement avec l'API:"
echo -e "curl -X POST \
  http://localhost:8000/api/parse-cv/ \
  -H \"Content-Type: multipart/form-data\" \
  -F \"file=@/Users/baptistecomas/Desktop/MonSuperCV.pdf\" \
  -F \"force_refresh=true\""

# Rendre le script exécutable
chmod +x restart-cv-parser-real.sh
