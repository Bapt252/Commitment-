FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers requirements et installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Exposition du port
EXPOSE 5000

# Variable d'environnement pour Flask
ENV FLASK_APP=app/__init__.py
ENV FLASK_ENV=production

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]