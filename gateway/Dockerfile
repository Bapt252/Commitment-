FROM python:3.11-slim

WORKDIR /app

# Copie des fichiers requis
COPY requirements.txt .

# Installation des dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste du code source
COPY . .

# Création du dossier de logs
RUN mkdir -p logs

# Exposition du port
EXPOSE 8000

# Variables d'environnement par défaut
ENV FLASK_APP=app/__init__.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Commande de démarrage avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "60", "app:app"]
