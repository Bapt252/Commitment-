FROM python:3.10-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de requirements
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie des fichiers du service
COPY . .

# Port d'exposition
EXPOSE 5060

# Commande de démarrage
CMD ["python", "api.py"]
