#!/bin/bash

# 🎯 Script de Correction SuperSmartMatch V2
# Corrige le problème de parsing en implémentant le workflow complet

set -e

echo "🚀 CORRECTION SUPERSMARTMATCH V2 - WORKFLOW COMPLET"
echo "=================================================="

# Vérifications préliminaires
echo "🔍 Vérifications préliminaires..."

if [ ! -f "fix-pdf-extraction.js" ] || [ ! -f "super-optimized-parser.js" ]; then
    echo "❌ Parsers autonomes manquants! Vérifiez que fix-pdf-extraction.js et super-optimized-parser.js sont présents."
    exit 1
fi

if [ ! -f "cv_christine.pdf" ] || [ ! -f "fdp.pdf" ]; then
    echo "⚠️ Fichiers de test manquants (cv_christine.pdf, fdp.pdf) - continuons quand même"
fi

echo "✅ Fichiers parsers trouvés"

# Arrêter les services V2 existants
echo "🛑 Arrêt des services V2 existants..."
docker-compose -f docker-compose.v2.yml down --remove-orphans 2>/dev/null || true

# Créer la structure V2 corrigée
echo "📁 Création de la structure V2 corrigée..."

# CV Parser V2
mkdir -p cv-parser-v2/parsers
mkdir -p job-parser-v2/parsers

# Copier les parsers autonomes
echo "📋 Copie des parsers autonomes..."
cp fix-pdf-extraction.js cv-parser-v2/parsers/
cp super-optimized-parser.js cv-parser-v2/parsers/
cp fix-pdf-extraction.js job-parser-v2/parsers/
cp super-optimized-parser.js job-parser-v2/parsers/

echo "✅ Parsers copiés dans les répertoires V2"

# Créer app.py CV Parser V2 - VERSION CORRIGÉE
echo "📝 Création de l'API CV Parser V2 corrigée..."
cat > cv-parser-v2/app.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SuperSmartMatch V2 - CV Parser API CORRIGÉ
Implémente le workflow complet : PDF → fix-pdf-extraction.js → super-optimized-parser.js → JSON
"""

import os
import json
import tempfile
import subprocess
import logging
from pathlib import Path
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

class CVParserV2:
    def __init__(self):
        self.parsers_dir = Path("/app/parsers")
        self.temp_dir = Path("/tmp/cv_parsing")
        self.temp_dir.mkdir(exist_ok=True)
        
        self.fix_pdf_parser = self.parsers_dir / "fix-pdf-extraction.js"
        self.super_parser = self.parsers_dir / "super-optimized-parser.js"
    
    def extract_clean_text(self, pdf_path):
        """Étape 1 : Extraction du texte propre"""
        logger.info("🔧 Extraction texte propre...")
        
        work_dir = self.temp_dir / f"work_{os.getpid()}"
        work_dir.mkdir(exist_ok=True)
        
        work_pdf = work_dir / "uploaded_cv.pdf"
        subprocess.run(['cp', str(pdf_path), str(work_pdf)], check=True)
        
        result = subprocess.run(
            ['node', str(self.fix_pdf_parser)],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise Exception(f"Extraction PDF échouée: {result.stderr}")
        
        text_files = list(work_dir.glob("*_clean_extracted.txt"))
        if not text_files:
            text_files = list(work_dir.glob("*.txt"))
        
        if not text_files:
            raise Exception("Aucun fichier texte généré")
        
        text_file = text_files[0]
        clean_text = text_file.read_text(encoding='utf-8')
        
        logger.info(f"✅ Texte extrait: {len(clean_text)} caractères")
        return clean_text, str(text_file)
    
    def parse_cv_data(self, text_file_path):
        """Étape 2 : Parsing du CV"""
        logger.info("🧠 Parsing CV...")
        
        work_dir = Path(text_file_path).parent
        
        script_content = f"""
const fs = require('fs');
const SuperOptimizedParser = require('{self.super_parser}');

async function parseCV() {{
    try {{
        const parser = new SuperOptimizedParser();
        const text = fs.readFileSync('{text_file_path}', 'utf8');
        const cvData = parser.parseEnhancedCV(text);
        
        fs.writeFileSync('cv_parsed_result.json', JSON.stringify(cvData, null, 2));
        console.log(JSON.stringify(cvData, null, 2));
    }} catch (error) {{
        console.error('❌ Erreur parsing CV:', error.message);
        process.exit(1);
    }}
}}

parseCV();
"""
        
        script_file = work_dir / "parse_cv_script.js"
        script_file.write_text(script_content)
        
        result = subprocess.run(
            ['node', str(script_file)],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise Exception(f"Parsing CV échoué: {result.stderr}")
        
        result_file = work_dir / "cv_parsed_result.json"
        if result_file.exists():
            cv_data = json.loads(result_file.read_text())
        else:
            lines = result.stdout.strip().split('\n')
            json_lines = [line for line in lines if line.startswith('{')]
            if json_lines:
                cv_data = json.loads(json_lines[-1])
            else:
                raise Exception("Pas de JSON trouvé")
        
        logger.info(f"✅ CV parsé: {len(cv_data.get('skills', []))} compétences")
        return cv_data
    
    def process_cv(self, pdf_file):
        """Workflow complet"""
        logger.info("🚀 Workflow CV complet...")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            pdf_file.save(temp_pdf.name)
            temp_pdf_path = temp_pdf.name
        
        try:
            clean_text, text_file_path = self.extract_clean_text(temp_pdf_path)
            cv_data = self.parse_cv_data(text_file_path)
            
            cv_data['_metadata'] = {
                'text_length': len(clean_text),
                'processing_status': 'success'
            }
            
            return cv_data
        finally:
            try:
                os.unlink(temp_pdf_path)
            except:
                pass

cv_parser = CVParserV2()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'cv-parser-v2',
        'parsers_available': {
            'fix_pdf_extraction': cv_parser.fix_pdf_parser.exists(),
            'super_optimized_parser': cv_parser.super_parser.exists()
        }
    })

@app.route('/api/parse-cv/', methods=['POST'])
def parse_cv():
    logger.info("📄 Nouvelle demande parsing CV...")
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Seuls les fichiers PDF sont acceptés'}), 400
        
        cv_data = cv_parser.process_cv(file)
        
        logger.info("✅ CV parsé avec succès")
        return jsonify({
            'status': 'success',
            'data': cv_data
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}")
        return jsonify({'error': f'Impossible de parser le CV: {str(e)}'}), 500

if __name__ == '__main__':
    logger.info("🚀 Démarrage CV Parser V2...")
    app.run(host='0.0.0.0', port=5051, debug=False)
EOF

# Créer app.py Job Parser V2 - VERSION CORRIGÉE
echo "📝 Création de l'API Job Parser V2 corrigée..."
cat > job-parser-v2/app.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SuperSmartMatch V2 - Job Parser API CORRIGÉ
"""

import os
import json
import tempfile
import subprocess
import logging
from pathlib import Path
from flask import Flask, request, jsonify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

class JobParserV2:
    def __init__(self):
        self.parsers_dir = Path("/app/parsers")
        self.temp_dir = Path("/tmp/job_parsing")
        self.temp_dir.mkdir(exist_ok=True)
        
        self.fix_pdf_parser = self.parsers_dir / "fix-pdf-extraction.js"
        self.super_parser = self.parsers_dir / "super-optimized-parser.js"
    
    def extract_clean_text(self, pdf_path):
        """Étape 1 : Extraction du texte propre"""
        logger.info("🔧 Extraction texte propre...")
        
        work_dir = self.temp_dir / f"work_{os.getpid()}"
        work_dir.mkdir(exist_ok=True)
        
        work_pdf = work_dir / "uploaded_job.pdf"
        subprocess.run(['cp', str(pdf_path), str(work_pdf)], check=True)
        
        result = subprocess.run(
            ['node', str(self.fix_pdf_parser)],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            raise Exception(f"Extraction PDF échouée: {result.stderr}")
        
        text_files = list(work_dir.glob("*_clean_extracted.txt"))
        if not text_files:
            text_files = list(work_dir.glob("*.txt"))
        
        if not text_files:
            raise Exception("Aucun fichier texte généré")
        
        text_file = text_files[0]
        clean_text = text_file.read_text(encoding='utf-8')
        
        logger.info(f"✅ Texte extrait: {len(clean_text)} caractères")
        return clean_text, str(text_file)
    
    def parse_job_data(self, text_file_path):
        """Étape 2 : Parsing du Job"""
        logger.info("💼 Parsing Job...")
        
        work_dir = Path(text_file_path).parent
        
        script_content = f"""
const fs = require('fs');
const SuperOptimizedParser = require('{self.super_parser}');

async function parseJob() {{
    try {{
        const parser = new SuperOptimizedParser();
        const text = fs.readFileSync('{text_file_path}', 'utf8');
        const jobData = parser.parseEnhancedJob(text);
        
        fs.writeFileSync('job_parsed_result.json', JSON.stringify(jobData, null, 2));
        console.log(JSON.stringify(jobData, null, 2));
    }} catch (error) {{
        console.error('❌ Erreur parsing Job:', error.message);
        process.exit(1);
    }}
}}

parseJob();
"""
        
        script_file = work_dir / "parse_job_script.js"
        script_file.write_text(script_content)
        
        result = subprocess.run(
            ['node', str(script_file)],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise Exception(f"Parsing Job échoué: {result.stderr}")
        
        result_file = work_dir / "job_parsed_result.json"
        if result_file.exists():
            job_data = json.loads(result_file.read_text())
        else:
            lines = result.stdout.strip().split('\n')
            json_lines = [line for line in lines if line.startswith('{')]
            if json_lines:
                job_data = json.loads(json_lines[-1])
            else:
                raise Exception("Pas de JSON trouvé")
        
        logger.info(f"✅ Job parsé: {job_data.get('job_info', {}).get('title', 'Titre non détecté')}")
        return job_data
    
    def process_job(self, pdf_file):
        """Workflow complet"""
        logger.info("🚀 Workflow Job complet...")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            pdf_file.save(temp_pdf.name)
            temp_pdf_path = temp_pdf.name
        
        try:
            clean_text, text_file_path = self.extract_clean_text(temp_pdf_path)
            job_data = self.parse_job_data(text_file_path)
            
            job_data['_metadata'] = {
                'text_length': len(clean_text),
                'processing_status': 'success'
            }
            
            return job_data
        finally:
            try:
                os.unlink(temp_pdf_path)
            except:
                pass

job_parser = JobParserV2()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'job-parser-v2',
        'parsers_available': {
            'fix_pdf_extraction': job_parser.fix_pdf_parser.exists(),
            'super_optimized_parser': job_parser.super_parser.exists()
        }
    })

@app.route('/api/parse-job', methods=['POST'])
def parse_job():
    logger.info("💼 Nouvelle demande parsing Job...")
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Seuls les fichiers PDF sont acceptés'}), 400
        
        job_data = job_parser.process_job(file)
        
        logger.info("✅ Job parsé avec succès")
        return jsonify({
            'status': 'success',
            'data': job_data
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}")
        return jsonify({'error': f'Impossible de parser le job: {str(e)}'}), 500

if __name__ == '__main__':
    logger.info("🚀 Démarrage Job Parser V2...")
    app.run(host='0.0.0.0', port=5053, debug=False)
EOF

# Créer requirements.txt
echo "📦 Création requirements.txt..."
cat > cv-parser-v2/requirements.txt << 'EOF'
Flask==2.3.3
Werkzeug==2.3.7
PyPDF2==3.0.1
pdfplumber==0.9.0
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
markupsafe==2.1.3
jsonschema==4.19.1
EOF

cp cv-parser-v2/requirements.txt job-parser-v2/requirements.txt

# Créer Dockerfile CORRIGÉ
echo "🐳 Création Dockerfile corrigé..."
cat > cv-parser-v2/Dockerfile << 'EOF'
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    curl wget git build-essential \
    poppler-utils pdftotext \
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

cp cv-parser-v2/Dockerfile job-parser-v2/Dockerfile

# Créer docker-compose.v2.yml CORRIGÉ
echo "🔧 Création docker-compose.v2.yml corrigé..."
cat > docker-compose.v2.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: ssm_redis_v2
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3
    networks:
      - ssm_network

  cv-parser-v2:
    build:
      context: ./cv-parser-v2
      dockerfile: Dockerfile
    container_name: ssm_cv_parser_v2
    ports:
      - "5051:5051"
    volumes:
      - "./fix-pdf-extraction.js:/app/parsers/fix-pdf-extraction.js:ro"
      - "./super-optimized-parser.js:/app/parsers/super-optimized-parser.js:ro"
      - "/tmp/cv_parsing:/tmp/cv_parsing"
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5051/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    depends_on:
      - redis
    networks:
      - ssm_network
    restart: unless-stopped

  job-parser-v2:
    build:
      context: ./job-parser-v2
      dockerfile: Dockerfile
    container_name: ssm_job_parser_v2
    ports:
      - "5053:5053"
    volumes:
      - "./fix-pdf-extraction.js:/app/parsers/fix-pdf-extraction.js:ro"
      - "./super-optimized-parser.js:/app/parsers/super-optimized-parser.js:ro"
      - "/tmp/job_parsing:/tmp/job_parsing"
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5053/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    depends_on:
      - redis
    networks:
      - ssm_network
    restart: unless-stopped

volumes:
  redis_data:
    driver: local

networks:
  ssm_network:
    driver: bridge
EOF

# Build et démarrage des services V2 corrigés
echo "🏗️ Build des services V2 corrigés..."
docker-compose -f docker-compose.v2.yml build --no-cache

echo "🚀 Démarrage des services V2 corrigés..."
docker-compose -f docker-compose.v2.yml up -d

# Attendre que les services démarrent
echo "⏳ Attente du démarrage des services..."
sleep 30

# Tests de santé
echo "🏥 Tests de santé des services..."
curl -s http://localhost:5051/health | jq . || echo "❌ CV Parser V2 pas encore prêt"
curl -s http://localhost:5053/health | jq . || echo "❌ Job Parser V2 pas encore prêt"

# Afficher le statut
echo "📊 Statut des services:"
docker-compose -f docker-compose.v2.yml ps

echo ""
echo "✅ CORRECTION SUPERSMARTMATCH V2 TERMINÉE !"
echo "============================================"
echo ""
echo "🎯 Les services V2 corrigés sont démarrés:"
echo "   • CV Parser V2:  http://localhost:5051"
echo "   • Job Parser V2: http://localhost:5053"
echo ""
echo "🧪 Tests des endpoints corrigés:"
echo "   curl -X POST -F \"file=@cv_christine.pdf\" http://localhost:5051/api/parse-cv/"
echo "   curl -X POST -F \"file=@fdp.pdf\" http://localhost:5053/api/parse-job"
echo ""
echo "📋 Workflow corrigé implémenté:"
echo "   PDF → fix-pdf-extraction.js → Texte Propre → super-optimized-parser.js → JSON"
echo ""
echo "🔍 Pour débugger:"
echo "   docker-compose -f docker-compose.v2.yml logs cv-parser-v2"
echo "   docker-compose -f docker-compose.v2.yml logs job-parser-v2"
