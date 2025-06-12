#!/bin/bash

echo "🔨 Création de tous les fichiers SuperSmartMatch V2..."

# 1. Dockerfile CV Parser V2
cat > cv-parser-v2/Dockerfile << 'EOF'
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY parsers/ ./parsers/
RUN chmod +x ./parsers/*.sh 2>/dev/null || true

COPY . .

EXPOSE 5051

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5051/health || exit 1

CMD ["python", "app.py"]
EOF

# 2. Dockerfile Job Parser V2
cat > job-parser-v2/Dockerfile << 'EOF'
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY parsers/ ./parsers/
RUN chmod +x ./parsers/*.sh 2>/dev/null || true

COPY . .

EXPOSE 5053

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5053/health || exit 1

CMD ["python", "app.py"]
EOF

# 3. Requirements pour les deux services
cat > cv-parser-v2/requirements.txt << 'EOF'
Flask==2.3.3
Flask-CORS==4.0.0
redis==4.6.0
Werkzeug==2.3.7
gunicorn==21.2.0
PyPDF2==3.0.1
python-docx==0.8.11
requests==2.31.0
EOF

cp cv-parser-v2/requirements.txt job-parser-v2/requirements.txt

# 4. docker-compose.v2.yml
cat > docker-compose.v2.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  cv-parser-v2:
    build:
      context: ./cv-parser-v2
      dockerfile: Dockerfile
    ports:
      - "5051:5051"
    environment:
      - REDIS_URL=redis://redis:6379
      - PARSER_MODE=autonomous
    volumes:
      - ./temp_uploads:/app/temp_uploads
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5051/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  job-parser-v2:
    build:
      context: ./job-parser-v2
      dockerfile: Dockerfile
    ports:
      - "5053:5053"
    environment:
      - REDIS_URL=redis://redis:6379
      - PARSER_MODE=autonomous
    volumes:
      - ./temp_uploads:/app/temp_uploads
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5053/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis-commander:
    image: rediscommander/redis-commander:latest
    ports:
      - "8081:8081"
    environment:
      - REDIS_HOSTS=local:redis:6379
    depends_on:
      - redis

volumes:
  redis_data:
EOF

# 5. Créer le dossier temp_uploads
mkdir -p temp_uploads

echo "✅ Tous les fichiers créés !"
echo ""
echo "📁 Structure créée :"
echo "   • cv-parser-v2/Dockerfile"
echo "   • cv-parser-v2/requirements.txt"
echo "   • job-parser-v2/Dockerfile"
echo "   • job-parser-v2/requirements.txt"
echo "   • docker-compose.v2.yml"
echo "   • temp_uploads/"
echo ""
echo "🚀 Prochaine étape : Créer les APIs Python"
