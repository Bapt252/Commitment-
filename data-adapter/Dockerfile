FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances systèmes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de l'application
COPY requirements.txt .
COPY smartmatch_data_adapter.py .
COPY flask_api.py .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Téléchargement des ressources NLTK
RUN python -c "import nltk; nltk.download('wordnet')"

# Exposer le port
EXPOSE 5053

# Commande par défaut
CMD ["python", "flask_api.py"]