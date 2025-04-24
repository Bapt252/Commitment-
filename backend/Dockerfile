FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances de base
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-fra \
        tesseract-ocr-eng \
        antiword \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt requirements.docker.txt ./
RUN pip install --no-cache-dir -r requirements.docker.txt

# Créer les répertoires nécessaires
RUN mkdir -p /app/data /app/logs /app/models

# Copier le code de l'application
COPY app/ ./app/
COPY scripts/ ./scripts/

# Exposer le port
EXPOSE 5000

# Commande par défaut
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]