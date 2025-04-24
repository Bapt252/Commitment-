FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Installer les dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmagic1 \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copier les requirements d'abord pour optimiser le cache
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer les répertoires nécessaires
RUN mkdir -p /app/logs /app/temp

# Créer un utilisateur non-root pour la sécurité
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app /app/logs /app/temp
USER appuser

# Exposer le port
EXPOSE 5000

# Vérification de santé
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# La commande sera spécifiée dans docker-compose pour les différents services (API ou worker)
CMD ["python", "main.py"]
