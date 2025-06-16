# SuperSmartMatch V2 API Gateway Dockerfile
# Image optimisée pour la production avec sécurité renforcée

# Stage 1: Build dependencies
FROM python:3.11-slim-bullseye as builder

# Métadonnées
LABEL maintainer="SuperSmartMatch Team"
LABEL version="2.1.0"
LABEL description="API Gateway pour SuperSmartMatch V2"

# Variables d'environnement pour le build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Installer les dépendances système pour le build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc6-dev \
    libpq-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Créer un utilisateur non-root pour la sécurité
RUN useradd --create-home --shell /bin/bash --uid 1000 gateway

# Créer le répertoire de travail
WORKDIR /app

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim-bullseye as production

# Variables d'environnement pour la production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/home/gateway/.local/bin:$PATH"

# Installer uniquement les dépendances runtime essentielles
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Créer l'utilisateur non-root
RUN useradd --create-home --shell /bin/bash --uid 1000 gateway

# Copier les dépendances Python installées depuis le stage builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Créer les répertoires nécessaires
RUN mkdir -p /app /app/logs /app/uploads /app/temp && \
    chown -R gateway:gateway /app

# Passer à l'utilisateur non-root
USER gateway
WORKDIR /app

# Copier le code source
COPY --chown=gateway:gateway . .

# Créer le répertoire pour les logs
RUN mkdir -p logs

# Variables d'environnement par défaut
ENV ENVIRONMENT=production \
    PORT=5050 \
    WORKERS=4 \
    LOG_LEVEL=info \
    TIMEOUT=60

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5050/api/gateway/status || exit 1

# Exposer le port
EXPOSE 5050

# Script de démarrage personnalisé
COPY --chown=gateway:gateway docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

# Point d'entrée
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Commande par défaut
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5050", "--workers", "4"]

# Stage 3: Development image (optionnel)
FROM production as development

# Revenir à root temporairement pour installer les outils de dev
USER root

# Installer les outils de développement
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances de développement
COPY requirements-dev.txt* ./
RUN if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

# Retourner à l'utilisateur non-root
USER gateway

# Variables d'environnement pour le développement
ENV ENVIRONMENT=development \
    DEBUG=true \
    LOG_LEVEL=debug \
    RELOAD=true

# Commande pour le développement avec rechargement automatique
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5050", "--reload", "--log-level", "debug"]
