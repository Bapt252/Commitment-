#!/bin/bash
echo "🚨 Executing emergency rollback..."
cd "$(dirname "$0")"
docker-compose -f ../../configs/docker/docker-compose.testing.yml stop supersmartmatch-v2
docker cp redis-v1.rdb redis-master:/data/dump.rdb
docker restart redis-master
docker-compose -f ../../configs/docker/docker-compose.testing.yml restart supersmartmatch-v1 nexten
echo "✅ Rollback completed"
