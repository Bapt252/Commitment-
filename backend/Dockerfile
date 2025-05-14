FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY backend/ .

# Exposer le port
EXPOSE 5055

# Commande de démarrage
CMD ["python", "job_parser_api.py"]
