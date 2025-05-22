#!/bin/bash

echo "🔧 REDÉPLOIEMENT SERVICES COMMITMENT- AVEC CORRECTIONS"
echo "====================================================="

echo "📊 1. Pull des dernières modifications GitHub..."
git pull origin main

echo ""
echo "📊 2. Rebuild des images avec nouvelles dépendances..."

# Arrêt des services problématiques
echo "⏹️  Arrêt services en panne..."
docker-compose down nexten-job-parser commitment--job-parser-worker-1 commitment--job-parser-worker-2

# Rebuild avec cache supprimé pour forcer l'installation des nouvelles dépendances
echo "🐳 Rebuild Job Parser avec nouvelles configurations..."
docker-compose build nexten-job-parser --no-cache

echo "🐳 Rebuild Job Parser Workers..."
docker-compose build commitment--job-parser-worker-1 commitment--job-parser-worker-2 --no-cache

# Rebuild matching service aussi
echo "🐳 Rebuild Matching Service..."
docker-compose build nexten-matching-api --no-cache

echo ""
echo "📊 3. Redémarrage avec nouvelles images..."

# Redémarrage séquentiel pour éviter les conflits
docker-compose up -d nexten-job-parser
sleep 10

docker-compose up -d commitment--job-parser-worker-1 commitment--job-parser-worker-2
sleep 10

docker-compose up -d nexten-matching-api
sleep 10

echo ""
echo "⏳ Attente 45 secondes pour initialisation complète..."
sleep 45

echo ""
echo "📊 4. Test post-déploiement..."

services_to_test=(
    "Job Parser:5055"
    "CV Parser:5051"
    "Matching Service:5052"
    "Personalization:5060"
    "Frontend:3000"
)

echo "🔍 Tests de connectivité services:"
for service in "${services_to_test[@]}"; do
    name=$(echo $service | cut -d':' -f1)
    port=$(echo $service | cut -d':' -f2)
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port > /dev/null 2>&1; then
        status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port)
        if [ $status -eq 200 ] || [ $status -eq 404 ] || [ $status -eq 422 ]; then
            echo "✅ $name (port $port) : FONCTIONNEL"
        else
            echo "⚠️  $name (port $port) : CODE $status"
        fi
    else
        echo "❌ $name (port $port) : INACCESSIBLE"
    fi
done

echo ""
echo "🐳 État final des conteneurs:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -15

echo ""
echo "📊 5. Vérification logs récents..."
echo "🔍 Job Parser logs:"
docker logs nexten-job-parser --tail 5

echo ""
echo "🔍 Job Parser Worker 1 logs:"
docker logs commitment--job-parser-worker-1 --tail 3

echo ""
echo "✅ Redéploiement terminé !"
echo ""
echo "🚀 PRÊT POUR L'AUDIT PERFORMANCE COMPLET"
echo "Exécutez: python3 scripts/partial_performance_audit.py"
