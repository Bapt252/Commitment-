FROM python:3.9-slim

WORKDIR /app

# Copier les dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Port par défaut
EXPOSE 5000

# Commande de démarrage avec le nouveau script
CMD ["python", "run.py"]