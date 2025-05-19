FROM python:3.11-slim

WORKDIR /app

# Installation de Locust et des dépendances
RUN pip install --no-cache-dir \
    locust \
    requests \
    faker

# Copie des fichiers de test
COPY . .

# Exposition du port Locust
EXPOSE 8089

# Commande par défaut
CMD ["locust", "--host=http://api:5000", "--web-host=0.0.0.0"]