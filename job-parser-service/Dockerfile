FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY gpt_parser_api.py .

# Exposer le port utilisé par l'API
EXPOSE 5055

# Commande pour démarrer l'API
CMD ["python", "gpt_parser_api.py"]
