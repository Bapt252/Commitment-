#!/bin/bash

echo "🔧 RÉPARATION SERVICES COMMITMENT-"
echo "=================================="

echo "📊 1. Diagnostic détaillé des services en panne..."

# Vérifier logs des services en panne
echo "🔍 Logs Job Parser:"
docker logs nexten-job-parser --tail 20

echo -e "\n🔍 Logs Job Parser Worker 1:"
docker logs commitment--job-parser-worker-1 --tail 10

echo -e "\n🔍 Logs Job Parser Worker 2:"
docker logs commitment--job-parser-worker-2 --tail 10

echo -e "\n🔧 2. Tentative redémarrage services..."

# Arrêter les services problématiques
echo "⏹️  Arrêt services en panne..."
docker stop nexten-job-parser commitment--job-parser-worker-1 commitment--job-parser-worker-2 2>/dev/null

# Attendre un peu
sleep 3

# Redémarrer les services
echo "🚀 Redémarrage Job Parser..."
docker start nexten-job-parser

sleep 5

echo "🚀 Redémarrage Workers..."
docker start commitment--job-parser-worker-1
docker start commitment--job-parser-worker-2

sleep 10

echo -e "\n📊 3. Vérification post-réparation..."

# Re-test des services
services_to_test=(
    "Job Parser:5055"
    "Matching Service:5052"
)

for service in "${services_to_test[@]}"; do
    name=$(echo $service | cut -d':' -f1)
    port=$(echo $service | cut -d':' -f2)
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port > /dev/null 2>&1; then
        status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port)
        if [ $status -eq 200 ] || [ $status -eq 404 ] || [ $status -eq 422 ]; then
            echo "✅ $name (port $port) : RÉPARÉ"
        else
            echo "⚠️  $name (port $port) : CODE $status"
        fi
    else
        echo "❌ $name (port $port) : TOUJOURS INACCESSIBLE"
    fi
done

echo -e "\n🐳 État conteneurs après réparation:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(job-parser|matching)"

echo -e "\n✅ Réparation terminée !"
