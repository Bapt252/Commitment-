FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copie du fichier de requirements adapté pour Docker
COPY requirements.docker.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.docker.txt

# Copie du code source
COPY . .

# Création d'un fichier de healthcheck
RUN echo 'from fastapi import FastAPI, Depends\nimport uvicorn\n\napp = FastAPI()\n\n@app.get("/health")\ndef health_check():\n    return {"status": "healthy"}\n\nif __name__ == "__main__":\n    uvicorn.run(app, host="0.0.0.0", port=5000)' > health_app.py

# Exposition du port
EXPOSE 5000

# Commande de démarrage du serveur
CMD ["uvicorn", "health_app:app", "--host=0.0.0.0", "--port=5000"]
