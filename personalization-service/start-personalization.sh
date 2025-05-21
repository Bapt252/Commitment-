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

# Vérification des variables d'environnement
if [ -z "$REDIS_HOST" ]; then
  echo -e "${YELLOW}[INFO] REDIS_HOST non défini, utilisation de la valeur par défaut: localhost${NC}"
  export REDIS_HOST=localhost
fi

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
try:
    r = redis.Redis(host='${REDIS_HOST}', port=${REDIS_PORT})
    r.ping()
    print('Connexion à Redis établie avec succès!')
except Exception as e:
    print(f'Erreur de connexion à Redis: {str(e)}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
  echo -e "${RED}[ERREUR] Impossible de se connecter à Redis. Vérifiez que Redis est en cours d'exécution.${NC}"
  exit 1
fi

# Démarrage du service
echo -e "${GREEN}[INFO] Démarrage du service de personnalisation (port: ${API_PORT})...${NC}"

# En mode développement (reload automatique)
if [ "$1" == "dev" ]; then
  echo -e "${YELLOW}[INFO] Mode développement activé (rechargement automatique)${NC}"
  exec python -m flask --app api run --host=0.0.0.0 --port=${API_PORT} --debug
else
  # En mode production avec gunicorn
  echo -e "${GREEN}[INFO] Mode production${NC}"
  exec gunicorn --bind 0.0.0.0:${API_PORT} --workers=4 --timeout=120 --access-logfile=logs/access.log --error-logfile=logs/error.log "api:app"
fi

echo -e "${RED}[ERREUR] Le service s'est arrêté de manière inattendue${NC}"
exit 1
