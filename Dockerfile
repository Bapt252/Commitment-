# 🐳 SuperSmartMatch V2.1 - Universal Parser Dockerfile
# Support multi-formats avec OCR et détection automatique

FROM python:3.9-slim

# Métadonnées
LABEL maintainer="SuperSmartMatch Team"
LABEL version="2.1.0"
LABEL description="Universal Parser for CV/Job documents - Multi-format support"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    # Dépendances de base
    curl \
    wget \
    unzip \
    git \
    build-essential \
    # Node.js pour les parsers JavaScript existants
    nodejs \
    npm \
    # Détection de format (python-magic)
    libmagic-dev \
    file \
    # OCR Tesseract
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    # LibreOffice pour conversion fallback (optionnel)
    libreoffice \
    # Support images
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    # Support XML/HTML
    libxml2-dev \
    libxslt1-dev \
    # Nettoyage
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Création du dossier de travail
WORKDIR /app

# Configuration Tesseract
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Argument pour déterminer quel parser construire
ARG PARSER_TYPE=cv
ENV PARSER_TYPE=${PARSER_TYPE}

# Copie du dossier parser approprié
COPY ${PARSER_TYPE}-parser-v2/ .

# Installation des dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Création des dossiers temporaires
RUN mkdir -p /tmp/cv_parsing /tmp/job_parsing && \
    chmod 777 /tmp/cv_parsing /tmp/job_parsing

# Test de base des dépendances
RUN python -c "import magic; print('✅ python-magic OK')" && \
    python -c "import pytesseract; print('✅ pytesseract OK')" && \
    tesseract --version && \
    echo "✅ Tesseract OK" && \
    node --version && \
    echo "✅ Node.js OK"

# Port d'exposition
EXPOSE 5051 5053

# Santé du container
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5051/health || curl -f http://localhost:5053/health || exit 1

# Commande de démarrage
CMD ["python", "app.py"]

# === NOTES DE DÉPLOIEMENT ===
# 
# Construction des images :
# docker build --build-arg PARSER_TYPE=cv -t supersmartmatch/cv-parser:v2.1 .
# docker build --build-arg PARSER_TYPE=job -t supersmartmatch/job-parser:v2.1 .
#
# Lancement :
# docker run -p 5051:5051 supersmartmatch/cv-parser:v2.1
# docker run -p 5053:5053 supersmartmatch/job-parser:v2.1
#
# Avec volumes pour persistance :
# docker run -p 5051:5051 -v /host/parsers:/app/parsers supersmartmatch/cv-parser:v2.1
#
# Variables d'environnement optionnelles :
# -e TESSDATA_PREFIX=/custom/path
# -e MAX_CONTENT_LENGTH=100MB
#
# === TAILLE IMAGE ===
# Image finale : ~800MB (avec OCR complet)
# Image sans LibreOffice : ~500MB (retirer libreoffice de apt-get)
#
# === OPTIMISATIONS PRODUCTION ===
# 1. Multi-stage build pour réduire la taille
# 2. Cache des dépendances Python
# 3. Compression des langues Tesseract non utilisées
# 4. Suppression des outils de développement en prod
