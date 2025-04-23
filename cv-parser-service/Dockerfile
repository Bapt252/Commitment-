FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système pour PyPDF2
RUN apt-get update && apt-get install -y \
    poppler-utils \
    antiword \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers requis
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Création des répertoires nécessaires
RUN mkdir -p logs uploads

# Copie du reste du code source
COPY . .

# Exposition du port
EXPOSE 5000

# Variables d'environnement par défaut
ENV FLASK_APP=app/__init__.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Commande de démarrage avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
