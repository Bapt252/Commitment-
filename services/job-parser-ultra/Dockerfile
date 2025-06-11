# 🚀 Job Parser Ultra v2.0 - PROMPT 2
# Dockerfile optimisé pour parsing d'offres avec streaming temps réel

FROM python:3.11-slim

# Métadonnées
LABEL version="2.0.0"
LABEL description="Job Parser Ultra v2.0 with WebSocket streaming and targeted extraction"
LABEL maintainer="SuperSmartMatch Team"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    # OCR et traitement d'images  
    tesseract-ocr \
    tesseract-ocr-fra \
    libtesseract-dev \
    # Traitement PDF
    poppler-utils \
    # Traitement images
    libmagic1 \
    # NLP et processing
    libxml2-dev \
    libxslt1-dev \
    # Utilitaires
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
WORKDIR /app

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p /tmp/job-uploads /var/log/app /var/cache/job-parser

# Permissions
RUN chmod +x /app/entrypoint.sh

# Port d'exposition
EXPOSE 5053

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5053/health || exit 1

# Point d'entrée
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5053", "--workers", "4"]
