FROM python:3.11-slim

# Métadonnées
LABEL maintainer="Nexten Team"
LABEL version="1.0.0"
LABEL description="SuperSmartMatch - Service unifié de matching"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production
ENV PORT=5070
ENV HOST=0.0.0.0

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copie des requirements et installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Création du répertoire des logs
RUN mkdir -p /app/logs

# Copie du code source
COPY . .

# Copie des algorithmes existants depuis le répertoire parent
COPY ../matching_engine.py ./
COPY ../enhanced_matching_engine.py ./
COPY ../my_matching_engine.py ./

# Exposition du port
EXPOSE 5070

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5070/health || exit 1

# Commande de démarrage
CMD ["python", "app.py"]
