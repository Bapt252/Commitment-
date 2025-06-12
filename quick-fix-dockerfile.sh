#!/bin/bash

# 🔧 Fix rapide pour le Dockerfile - Erreur pdftotext

echo "🔧 CORRECTION RAPIDE DOCKERFILE"
echo "================================"

# Corriger le Dockerfile CV Parser
echo "📝 Correction Dockerfile CV Parser V2..."
cat > cv-parser-v2/Dockerfile << 'EOF'
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl wget git build-essential \
    poppler-utils \
    tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng \
    imagemagick python3-dev \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/parsers /tmp/cv_parsing /tmp/job_parsing

COPY parsers/ /app/parsers/
RUN chmod +x /app/parsers/*.js

COPY app.py .

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5051/health || exit 1

EXPOSE 5051

CMD ["python", "app.py"]
EOF

# Corriger le Dockerfile Job Parser  
echo "📝 Correction Dockerfile Job Parser V2..."
cp cv-parser-v2/Dockerfile job-parser-v2/Dockerfile

# Modifier le port pour Job Parser
sed -i 's/5051/5053/g' job-parser-v2/Dockerfile

echo "✅ Dockerfiles corrigés!"

# Rebuild et redémarrage
echo "🏗️ Rebuild avec Dockerfiles corrigés..."
docker-compose -f docker-compose.v2.yml build --no-cache

echo "🚀 Redémarrage des services..."
docker-compose -f docker-compose.v2.yml up -d

echo "⏳ Attente démarrage..."
sleep 20

echo "🏥 Test health checks..."
curl -s http://localhost:5051/health || echo "❌ CV Parser pas prêt"
curl -s http://localhost:5053/health || echo "❌ Job Parser pas prêt"

echo ""
echo "✅ CORRECTION TERMINÉE!"
echo "======================"
echo ""
echo "🎯 Services disponibles:"
echo "   • CV Parser V2:  http://localhost:5051/health"
echo "   • Job Parser V2: http://localhost:5053/health"
echo ""
echo "🧪 Tests:"
echo "   curl -X POST -F \"file=@cv_christine.pdf\" http://localhost:5051/api/parse-cv/"
echo "   curl -X POST -F \"file=@fdp.pdf\" http://localhost:5053/api/parse-job"