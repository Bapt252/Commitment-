FROM python:3.9-slim

WORKDIR /app

# Copier les dépendances et les installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Créer un script de démarrage
RUN echo '#!/bin/bash\npython -m flask run --host=0.0.0.0 --port=5000' > start.sh
RUN chmod +x start.sh

# Port par défaut
EXPOSE 5000

# Commande de démarrage
CMD ["./start.sh"]