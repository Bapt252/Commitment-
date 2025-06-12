#!/bin/bash
echo "🔧 SuperSmartMatch V2 - Correction Rapide"
echo "========================================"

# Synchronisation avec GitHub
echo "📥 Récupération des fichiers V2..."
git add .
git commit -m "🚀 Sauvegarde locale avant sync V2" || true
git pull origin main

# Correction docker-compose
echo "🐳 Création docker-compose.v2.yml corrigé..."
cat > docker-compose.v2.yml << 'EOD'
services:
  cv-parser:
    build:
      context: ./cv-parser
      dockerfile: Dockerfile
    ports:
      - "5051:5051"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
    volumes:
      - ./temp:/app/temp
    restart: unless-stopped

  job-parser:
    build:
      context: ./job-parser
      dockerfile: Dockerfile
    ports:
      - "5053:5053"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
    volumes:
      - ./temp:/app/temp
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
EOD

echo "✅ Configuration corrigée"

# Démarrage des services
echo "🚀 Démarrage des services V2..."
docker-compose -f docker-compose.v2.yml up -d

sleep 20

# Test des services
echo "🔍 Test des services..."
curl -s http://localhost:5051/health && echo "✅ CV Parser OK" || echo "❌ CV Parser KO"
curl -s http://localhost:5053/health && echo "✅ Job Parser OK" || echo "❌ Job Parser KO"

echo "🎉 Correction terminée !"
