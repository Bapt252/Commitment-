FROM python:3.9-slim

WORKDIR /app

# Copier les fichiers nécessaires
COPY requirements.txt .
COPY smartmatch.py .
COPY api.py .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Variables d'environnement
ENV PYTHONUNBUFFERED=1

# Exposer le port
EXPOSE 5052

# Commande par défaut
CMD ["python", "api.py"]
