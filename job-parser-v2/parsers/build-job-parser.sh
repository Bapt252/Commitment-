#!/bin/bash

# Arrêter les conteneurs existants
echo "Arrêt des conteneurs existants..."
docker-compose stop job-parser job-parser-worker

# Construire avec le Dockerfile corrigé
echo "Construction des images avec le Dockerfile corrigé..."
docker build -t nexten-job-parser -f job-parser-service/Dockerfile.fix job-parser-service/
docker build -t nexten-job-parser-worker -f job-parser-service/Dockerfile.fix job-parser-service/

# Démarrer les services
echo "Démarrage des services..."
docker-compose up -d job-parser job-parser-worker

echo "Terminé. Vous pouvez maintenant tester le service avec:"
echo "./curl-test-job-parser.sh /chemin/vers/votre/fdp.pdf"
