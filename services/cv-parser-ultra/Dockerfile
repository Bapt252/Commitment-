# 🚀 CV Parser Ultra v2.0 - Dockerfile optimisé
# PROMPT 2 - SuperSmartMatch V2 - Production ready

FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Baptiste Coma <baptiste.coma@gmail.com>"
LABEL version="2.0.0"
LABEL description="CV Parser Ultra avec streaming WebSocket temps réel"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DEBIAN_FRONTEND=noninteractive

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    # Dépendances générales
    build-essential \
    wget \
    curl \
    git \
    # OCR et traitement d'images
    tesseract-ocr \
    tesseract-ocr-fra \
    libtesseract-dev \
    # Traitement PDF
    poppler-utils \
    # Dépendances pour lxml et autres
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    # Nettoyage
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Copie des requirements
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p /app/temp /app/logs

# Permissions
RUN chmod +x /app/app.py

# Port exposé
EXPOSE 5051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:5051/health || exit 1

# Commande de démarrage
CMD ["python", "app.py"]
