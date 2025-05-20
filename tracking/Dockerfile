FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances systèmes
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de dépendances
COPY requirements.txt /app/
COPY tracking/requirements.txt /app/tracking-requirements.txt

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r tracking-requirements.txt

# Copie du code
COPY . /app/

# Variables d'environnement
ENV PYTHONPATH=/app
ENV PORT=5000

# Exposition du port
EXPOSE 5000

# Point d'entrée
CMD ["python", "-m", "tracking.api.app"]
