#!/bin/bash
# Script pour construire et tester le service job-parser avec le nouveau Dockerfile optimisé

set -e

echo "==== Construction de l'image avec le nouveau Dockerfile ===="
docker build -t job-parser-service:latest -f Dockerfile.new .

echo "==== Test du script de compatibilité Pydantic ===="
chmod +x test_pydantic_compat.py
docker run --rm job-parser-service:latest python test_pydantic_compat.py

echo "==== Test du service mock_parser ===="
docker run --rm job-parser-service:latest python -c "from app.services.mock_parser import get_mock_job_data; print(get_mock_job_data('Test de fiche de poste pour un Développeur Python Senior à Paris.'))"

echo "==== Démarrage du service en arrière-plan ===="
echo "Pour tester le service, vous pouvez utiliser la commande:"
echo "curl http://localhost:5053/health"
echo ""
echo "Pour arrêter le service, utilisez: docker stop job-parser"

docker run --rm -d --name job-parser -p 5053:5053 job-parser-service:latest
