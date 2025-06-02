# SuperSmartMatch V2 - Dockerfile
FROM python:3.11-slim

# Labels pour metadata
LABEL maintainer="SuperSmartMatch Team"
LABEL version="2.0.0"
LABEL description="Service de matching intelligent unifié"

# Variables d'environnement pour optimisation Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie des requirements et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY app/ ./app/

# Création d'un utilisateur non-root pour sécurité
RUN groupadd -r supersmartmatch && useradd -r -g supersmartmatch supersmartmatch
RUN chown -R supersmartmatch:supersmartmatch /app
USER supersmartmatch

# Port exposé (5070 pour SuperSmartMatch V2)
EXPOSE 5070

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5070/api/v2/health || exit 1

# Point d'entrée
CMD ["python", "-m", "app.main"]
