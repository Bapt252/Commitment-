FROM python:3.11-slim

WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Copier les algorithmes depuis le répertoire parent
COPY ../matching_engine.py ./
COPY ../matching_engine_enhanced.py ./
COPY ../my_matching_engine.py ./
COPY ../enhanced_matching_engine.py ./
COPY ../compare_algorithms.py ./

# Variables d'environnement
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Exposer le port
EXPOSE 5060

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:5060", "--workers", "4", "app:app"]
