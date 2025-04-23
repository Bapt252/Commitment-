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
EXPOSE 8000

# Variables d'environnement par défaut
ENV PYTHONPATH=/app
ENV PORT=8000
ENV ENVIRONMENT=production
ENV LOG_LEVEL=info

# Commande de démarrage avec uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
