FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copie du fichier de requirements adapté pour Docker
COPY requirements.docker.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.docker.txt

# Copie du code source
COPY . .

# Exposition du port
EXPOSE 5000

# Commande de démarrage du serveur
CMD ["uvicorn", "app:app", "--host=0.0.0.0", "--port=5000"]
