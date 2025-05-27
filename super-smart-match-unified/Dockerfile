FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie des requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY . .

# Création des dossiers pour les modèles
RUN mkdir -p models/embeddings models/ner_models models/learning_data

# Port d'écoute
EXPOSE 5052

# Variables d'environnement par défaut
ENV PYTHONPATH=/app
ENV FLASK_APP=supersmartmatch_unified.py
ENV PORT=5052
ENV DEBUG=false

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5052/health || exit 1

# Commande de démarrage
CMD ["python", "supersmartmatch_unified.py"]
