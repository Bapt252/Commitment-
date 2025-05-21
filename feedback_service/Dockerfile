FROM python:3.9-slim

WORKDIR /app

# Copier les fichiers de dépendances en premier pour profiter du cache Docker
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Télécharger les ressources NLTK nécessaires pour TextBlob
RUN python -m textblob.download_corpora lite

# Copier le reste du code
COPY . .

# Ajouter le répertoire courant au PYTHONPATH
ENV PYTHONPATH=/app

# Exposer le port
EXPOSE 5058

# Définir les variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PORT=5058
ENV FLASK_APP=api.app

# Commande par défaut pour démarrer l'application
CMD ["gunicorn", "--bind", "0.0.0.0:5058", "--workers", "4", "--timeout", "120", "wsgi:app"]
