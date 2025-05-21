#!/bin/bash

# Script de démarrage pour le service de personnalisation
# Auteur: Claude
# Date: Mai 2025

# Couleurs pour les logs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Démarrage du service de personnalisation ===${NC}"

# Vérification de l'environnement
if [ ! -f "api.py" ]; then
  echo -e "${RED}[ERREUR] Le fichier api.py est manquant. Assurez-vous d'être dans le bon répertoire.${NC}"
  exit 1
fi

# Vérification des dépendances
echo -e "${YELLOW}[INFO] Vérification des dépendances...${NC}"
pip install -r requirements.txt

# Vérification du mode d'exécution (local ou Docker)
if docker ps 2>/dev/null | grep -q nexten-redis; then
  # Mode Docker - utiliser le nom du conteneur Redis
  export REDIS_HOST=nexten-redis
  echo -e "${YELLOW}[INFO] Mode Docker détecté - Utilisation de REDIS_HOST=nexten-redis${NC}"
else
  # Mode local - utiliser localhost
  export REDIS_HOST=localhost
  echo -e "${YELLOW}[INFO] Mode local détecté - Utilisation de REDIS_HOST=localhost${NC}"
fi

# Vérification des variables d'environnement
if [ -z "$REDIS_PORT" ]; then
  echo -e "${YELLOW}[INFO] REDIS_PORT non défini, utilisation de la valeur par défaut: 6379${NC}"
  export REDIS_PORT=6379
fi

if [ -z "$API_PORT" ]; then
  echo -e "${YELLOW}[INFO] API_PORT non défini, utilisation de la valeur par défaut: 5060${NC}"
  export API_PORT=5060
fi

# Création des répertoires de logs et de données si nécessaire
mkdir -p logs
mkdir -p data

# Préparation de la base de données
echo -e "${YELLOW}[INFO] Vérification des migrations de la base de données...${NC}"
if [ -d "migrations" ]; then
  echo -e "${YELLOW}[INFO] Application des migrations...${NC}"
  # Commande de migration si nécessaire
  # python migrate.py
fi

# Vérification de la connexion à Redis
echo -e "${YELLOW}[INFO] Vérification de la connexion à Redis (${REDIS_HOST}:${REDIS_PORT})...${NC}"
python -c "
import redis
import sys
import time

max_retries = 5
retry_interval = 3

for attempt in range(max_retries):
    try:
        r = redis.Redis(host='${REDIS_HOST}', port=${REDIS_PORT})
        r.ping()
        print('Connexion à Redis établie avec succès!')
        sys.exit(0)
    except Exception as e:
        print(f'Tentative {attempt+1}/{max_retries}: Erreur de connexion à Redis: {str(e)}')
        if attempt < max_retries - 1:
            print(f'Nouvelle tentative dans {retry_interval} secondes...')
            time.sleep(retry_interval)
        else:
            print('Échec de toutes les tentatives de connexion à Redis')
            sys.exit(1)
"

if [ $? -ne 0 ]; then
  echo -e "${YELLOW}[WARNING] Impossible de se connecter à Redis. Tentative de démarrage du service quand même...${NC}"
fi

# Démarrage du service
echo -e "${GREEN}[INFO] Démarrage du service de personnalisation (port: ${API_PORT})...${NC}"

# En mode développement (reload automatique)
if [ "$1" == "dev" ]; then
  echo -e "${YELLOW}[INFO] Mode développement activé (rechargement automatique)${NC}"
  exec python -m flask --app api run --host=0.0.0.0 --port=${API_PORT} --debug
else
  # En mode production avec gunicorn si disponible
  if command -v gunicorn >/dev/null 2>&1; then
    echo -e "${GREEN}[INFO] Mode production avec gunicorn${NC}"
    exec gunicorn --bind 0.0.0.0:${API_PORT} --workers=4 --timeout=120 --access-logfile=logs/access.log --error-logfile=logs/error.log "api:app"
  else
    # Sinon utiliser Flask
    echo -e "${GREEN}[INFO] Mode production avec Flask (gunicorn non disponible)${NC}"
    exec python api.py
  fi
fi

echo -e "${RED}[ERREUR] Le service s'est arrêté de manière inattendue${NC}"
exit 1
