#!/bin/bash

echo "🔍 VÉRIFICATION SERVICES COMMITMENT-"
echo "=================================="

# Services à vérifier
services=(
    "CV Parser:5051"
    "Matching Service:5052" 
    "Job Parser:5055"
    "Personalization:5060"
    "Frontend:3000"
)

echo "📊 État des services :"
for service in "${services[@]}"; do
    name=$(echo $service | cut -d':' -f1)
    port=$(echo $service | cut -d':' -f2)
    
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port > /dev/null 2>&1; then
        status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port)
        if [ $status -eq 200 ] || [ $status -eq 404 ] || [ $status -eq 422 ]; then
            echo "✅ $name (port $port) : ACTIF"
        else
            echo "⚠️  $name (port $port) : CODE $status"
        fi
    else
        echo "❌ $name (port $port) : INACCESSIBLE"
    fi
done

echo ""
echo "🐳 Conteneurs Docker actifs :"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | head -10

echo ""
echo "💾 Utilisation ressources :"
echo "CPU : $(ps -A -o %cpu | awk '{s+=$1} END {print s "%"}')"
echo "RAM : $(ps -A -o %mem | awk '{s+=$1} END {print s "%"}')"
echo "Disk: $(df -h / | awk 'NR==2 {print $5}')"

echo ""
echo "✅ Vérification terminée !"
