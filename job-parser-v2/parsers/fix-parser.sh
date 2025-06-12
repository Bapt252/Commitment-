#!/bin/bash

# Couleurs pour une meilleure lisibilité
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== CORRECTION DU SERVICE JOB-PARSER ===${NC}"

# Créer le Dockerfile.fix
echo -e "${YELLOW}Création du Dockerfile corrigé...${NC}"
cat > job-parser-service/Dockerfile.fix << 'EOF'
FROM python:3.11-slim

# Dépendances runtime pour traitement de documents
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libmagic1 \
    curl \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    antiword \
    unrtf \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    CIRCUIT_BREAKER_ENABLED=false

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers du projet
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs /app/temp && \
    chmod 777 /app/logs && \
    chmod 777 /app/temp

# Installation directe des dépendances spécifiées sans circuit_breaker
RUN pip install --no-cache-dir \
    fastapi>=0.100.0 \
    uvicorn>=0.23.0 \
    python-multipart>=0.0.6 \
    python-dotenv>=1.0.0 \
    pydantic>=2.1.0 \
    pydantic-settings>=2.0.0 \
    requests>=2.31.0 \
    PyPDF2>=3.0.0 \
    pdfminer.six>=20220524 \
    python-docx>=0.8.11 \
    striprtf>=0.0.24 \
    pdfplumber>=0.9.0 \
    pdf2image>=1.16.3 \
    pytesseract>=0.3.10 \
    redis>=4.6.0 \
    rq>=1.15.0 \
    minio>=7.1.15 \
    openai>=1.3.0 \
    tenacity>=8.2.2 \
    pybreaker>=1.0.0 \
    python-magic>=0.4.27

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Port exposé
EXPOSE 5000

# Commande par défaut
CMD ["python", "main.py"]
EOF

# Arrêt des conteneurs existants
echo -e "${YELLOW}Arrêt des conteneurs existants...${NC}"
docker-compose stop job-parser job-parser-worker

# Suppression des conteneurs existants
echo -e "${YELLOW}Suppression des conteneurs existants...${NC}"
docker-compose rm -f job-parser job-parser-worker

# Construction avec le Dockerfile corrigé
echo -e "${YELLOW}Construction des images avec le Dockerfile corrigé...${NC}"
docker build -t nexten-job-parser -f job-parser-service/Dockerfile.fix job-parser-service/
docker build -t nexten-job-parser-worker -f job-parser-service/Dockerfile.fix job-parser-service/

# Démarrage des services
echo -e "${YELLOW}Démarrage des services...${NC}"
docker-compose up -d job-parser job-parser-worker

# Attendre que les services démarrent
echo -e "${YELLOW}Attente du démarrage des services...${NC}"
sleep 10

# Vérifier l'état des services
if docker-compose ps | grep job-parser | grep -v worker | grep -q "Up"; then
    echo -e "${GREEN}Service job-parser démarré avec succès!${NC}"
else
    echo -e "${RED}Échec du démarrage du service job-parser.${NC}"
    echo -e "${YELLOW}Logs du service job-parser:${NC}"
    docker-compose logs job-parser
fi

if docker-compose ps | grep job-parser-worker | grep -q "Up"; then
    echo -e "${GREEN}Service job-parser-worker démarré avec succès!${NC}"
else
    echo -e "${RED}Échec du démarrage du service job-parser-worker.${NC}"
    echo -e "${YELLOW}Logs du service job-parser-worker:${NC}"
    docker-compose logs job-parser-worker
fi

# Afficher les informations sur le port
echo -e "${YELLOW}Information sur le port:${NC}"
port=$(docker-compose port job-parser 5000 | cut -d ':' -f 2 || echo "5053")
echo -e "${GREEN}Le service job-parser est accessible sur http://localhost:${port}${NC}"

# Instructions pour tester
echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}Pour tester le parsing d'une fiche de poste:${NC}"
echo -e "${YELLOW}./curl-test-job-parser.sh /chemin/vers/votre/fichier.pdf${NC}"
echo -e "${GREEN}===========================================${NC}"
