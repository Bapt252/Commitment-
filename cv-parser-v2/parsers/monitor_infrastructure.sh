#!/bin/bash

echo "🚀 SuperSmartMatch V2 - Infrastructure Monitor"
echo "=============================================="
echo ""

while true; do
    clear
    echo "📊 SUPERSMARTMATCH V2 MONITORING - $(date)"
    echo "=============================================="
    echo ""
    
    # Services Status
    echo "🔧 SERVICES STATUS:"
    docker ps --filter "name=supersmartmatch" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(supersmartmatch|NAME)"
    echo ""
    
    # Resources Usage
    echo "💾 RESOURCE USAGE:"
    docker stats --no-stream --filter "name=supersmartmatch" --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | head -7
    echo ""
    
    # Database Metrics
    echo "📈 PROMPT 5 METRICS:"
    docker exec supersmartmatch-postgres psql -U supersmartmatch_user -d supersmartmatch -c "SELECT metric_name, metric_value FROM metrics ORDER BY metric_name;" 2>/dev/null | grep -E "(precision|performance|roi)" || echo "Metrics loading..."
    echo ""
    
    # Health Checks
    echo "🔍 HEALTH CHECKS:"
    echo -n "Redis: "
    docker exec supersmartmatch-redis redis-cli ping 2>/dev/null || echo "❌ Failed"
    echo -n "PostgreSQL: "
    docker exec supersmartmatch-postgres pg_isready -U supersmartmatch_user 2>/dev/null | grep -q "accepting" && echo "✅ OK" || echo "❌ Failed"
    echo -n "MinIO: "
    curl -sf http://localhost:9000/minio/health/live >/dev/null && echo "✅ OK" || echo "❌ Failed"
    echo -n "Grafana: "
    curl -sf http://localhost:3000/api/health >/dev/null && echo "✅ OK" || echo "❌ Failed"
    echo ""
    
    echo "🔄 Refreshing in 10s... (Ctrl+C to exit)"
    sleep 10
done
