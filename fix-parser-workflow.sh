#!/bin/bash

# 🔧 Fix du workflow parser - Correction de l'appel des parsers autonomes

echo "🔧 FIX WORKFLOW PARSER - APPEL DIRECT DES CLASSES"
echo "================================================"

# Corriger l'API CV Parser pour appeler directement la classe FixedPDFParser
echo "📝 Correction API CV Parser - Appel direct des classes..."
cat > cv-parser-v2/app.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SuperSmartMatch V2 - CV Parser API CORRIGÉ v2
Appel direct des classes de parsers autonomes
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
        """Étape 1 : Extraction du texte propre - APPEL DIRECT"""
        logger.info("🔧 Extraction texte propre avec appel direct...")
        
        work_dir = self.temp_dir / f"work_{os.getpid()}"
        work_dir.mkdir(exist_ok=True)
        
        # Copier le PDF avec le nom attendu
        work_pdf = work_dir / "input.pdf"
        subprocess.run(['cp', str(pdf_path), str(work_pdf)], check=True)
        
        # Créer un script wrapper qui appelle directement la classe
        wrapper_script = f"""
const fs = require('fs');
const FixedPDFParser = require('{self.fix_pdf_parser}');

async function extractPDF() {{
    try {{
        const parser = new FixedPDFParser();
        
        console.log('🔧 Début extraction PDF...');
        const result = await parser.extractCleanText('input.pdf');
        
        console.log('✅ Extraction terminée');
        console.log('📄 Fichier:', result.method);
        console.log('📊 Longueur:', result.text.length);
        
        // Sauvegarder le résultat avec un nom prévisible
        fs.writeFileSync('extracted_text.txt', result.text);
        console.log('💾 Texte sauvegardé: extracted_text.txt');
        
    }} catch (error) {{
        console.error('❌ Erreur extraction:', error.message);
        process.exit(1);
    }}
}}

extractPDF();
"""
        
        script_file = work_dir / "extract_wrapper.js"
        script_file.write_text(wrapper_script)
        
        result = subprocess.run(
            ['node', str(script_file)],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        logger.info(f"📋 Extraction stdout: {result.stdout}")
        logger.info(f"📋 Extraction stderr: {result.stderr}")
        
        if result.returncode != 0:
            raise Exception(f"Extraction PDF échouée: {result.stderr}")
        
        # Chercher le fichier texte généré
        text_file = work_dir / "extracted_text.txt"
        if not text_file.exists():
            # Fallback : chercher d'autres fichiers
            text_files = list(work_dir.glob("*_clean_extracted.txt")) + list(work_dir.glob("*.txt"))
            if text_files:
                text_file = text_files[0]
            else:
                raise Exception("Aucun fichier texte généré par l'extraction")
        
        clean_text = text_file.read_text(encoding='utf-8')
        
        logger.info(f"✅ Texte extrait: {len(clean_text)} caractères")
        return clean_text, str(text_file)
    
    def parse_cv_data(self, text_file_path):
        """Étape 2 : Parsing du CV - APPEL DIRECT"""
        logger.info("🧠 Parsing CV avec appel direct...")
        
        work_dir = Path(text_file_path).parent
        
        script_content = f"""
const fs = require('fs');
const SuperOptimizedParser = require('{self.super_parser}');

async function parseCV() {{
    try {{
        const parser = new SuperOptimizedParser();
        const text = fs.readFileSync('{text_file_path}', 'utf8');
        
        console.log('🧠 Début parsing CV...');
        console.log('📄 Texte à parser:', text.length, 'caractères');
        
        const cvData = parser.parseEnhancedCV(text);
        
        console.log('✅ Parsing CV terminé');
        console.log('🎯 Compétences trouvées:', cvData.skills ? cvData.skills.length : 0);
        console.log('👤 Nom détecté:', cvData.personal_info?.name || 'Non détecté');
        
        fs.writeFileSync('cv_parsed_result.json', JSON.stringify(cvData, null, 2));
        console.log(JSON.stringify(cvData, null, 2));
        
    }} catch (error) {{
        console.error('❌ Erreur parsing CV:', error.message);
        console.error('📋 Stack:', error.stack);
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
        
        logger.info(f"📋 Parsing stdout: {result.stdout}")
        logger.info(f"📋 Parsing stderr: {result.stderr}")
        
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
                raise Exception("Pas de JSON trouvé dans la sortie")
        
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

# Corriger l'API Job Parser de la même manière
echo "📝 Correction API Job Parser - Appel direct des classes..."
cat > job-parser-v2/app.py << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SuperSmartMatch V2 - Job Parser API CORRIGÉ v2
Appel direct des classes de parsers autonomes
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
        """Étape 1 : Extraction du texte propre - APPEL DIRECT"""
        logger.info("🔧 Extraction texte propre avec appel direct...")
        
        work_dir = self.temp_dir / f"work_{os.getpid()}"
        work_dir.mkdir(exist_ok=True)
        
        # Copier le PDF avec le nom attendu
        work_pdf = work_dir / "input.pdf"
        subprocess.run(['cp', str(pdf_path), str(work_pdf)], check=True)
        
        # Créer un script wrapper qui appelle directement la classe
        wrapper_script = f"""
const fs = require('fs');
const FixedPDFParser = require('{self.fix_pdf_parser}');

async function extractPDF() {{
    try {{
        const parser = new FixedPDFParser();
        
        console.log('🔧 Début extraction PDF...');
        const result = await parser.extractCleanText('input.pdf');
        
        console.log('✅ Extraction terminée');
        console.log('📄 Fichier:', result.method);
        console.log('📊 Longueur:', result.text.length);
        
        // Sauvegarder le résultat avec un nom prévisible
        fs.writeFileSync('extracted_text.txt', result.text);
        console.log('💾 Texte sauvegardé: extracted_text.txt');
        
    }} catch (error) {{
        console.error('❌ Erreur extraction:', error.message);
        process.exit(1);
    }}
}}

extractPDF();
"""
        
        script_file = work_dir / "extract_wrapper.js"
        script_file.write_text(wrapper_script)
        
        result = subprocess.run(
            ['node', str(script_file)],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        logger.info(f"📋 Extraction stdout: {result.stdout}")
        logger.info(f"📋 Extraction stderr: {result.stderr}")
        
        if result.returncode != 0:
            raise Exception(f"Extraction PDF échouée: {result.stderr}")
        
        # Chercher le fichier texte généré
        text_file = work_dir / "extracted_text.txt"
        if not text_file.exists():
            # Fallback : chercher d'autres fichiers
            text_files = list(work_dir.glob("*_clean_extracted.txt")) + list(work_dir.glob("*.txt"))
            if text_files:
                text_file = text_files[0]
            else:
                raise Exception("Aucun fichier texte généré par l'extraction")
        
        clean_text = text_file.read_text(encoding='utf-8')
        
        logger.info(f"✅ Texte extrait: {len(clean_text)} caractères")
        return clean_text, str(text_file)
    
    def parse_job_data(self, text_file_path):
        """Étape 2 : Parsing du Job - APPEL DIRECT"""
        logger.info("💼 Parsing Job avec appel direct...")
        
        work_dir = Path(text_file_path).parent
        
        script_content = f"""
const fs = require('fs');
const SuperOptimizedParser = require('{self.super_parser}');

async function parseJob() {{
    try {{
        const parser = new SuperOptimizedParser();
        const text = fs.readFileSync('{text_file_path}', 'utf8');
        
        console.log('💼 Début parsing Job...');
        console.log('📄 Texte à parser:', text.length, 'caractères');
        
        const jobData = parser.parseEnhancedJob(text);
        
        console.log('✅ Parsing Job terminé');
        console.log('💼 Titre détecté:', jobData.job_info?.title || 'Non détecté');
        console.log('📍 Lieu détecté:', jobData.job_info?.location || 'Non détecté');
        
        fs.writeFileSync('job_parsed_result.json', JSON.stringify(jobData, null, 2));
        console.log(JSON.stringify(jobData, null, 2));
        
    }} catch (error) {{
        console.error('❌ Erreur parsing Job:', error.message);
        console.error('📋 Stack:', error.stack);
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
        
        logger.info(f"📋 Parsing stdout: {result.stdout}")
        logger.info(f"📋 Parsing stderr: {result.stderr}")
        
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
                raise Exception("Pas de JSON trouvé dans la sortie")
        
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

# Rebuild et redémarrage des services
echo "🏗️ Rebuild des services avec workflow corrigé..."
docker-compose -f docker-compose.v2.yml build

echo "🚀 Redémarrage des services..."
docker-compose -f docker-compose.v2.yml up -d

echo "⏳ Attente du démarrage..."
sleep 20

echo "🏥 Test health checks..."
curl -s http://localhost:5051/health | jq . || echo "❌ CV Parser pas prêt"
curl -s http://localhost:5053/health | jq . || echo "❌ Job Parser pas prêt"

echo ""
echo "✅ FIX WORKFLOW TERMINÉ!"
echo "======================="
echo ""
echo "🎯 Workflow corrigé:"
echo "   PDF → FixedPDFParser.extractCleanText() → SuperOptimizedParser.parseEnhanced*() → JSON"
echo ""
echo "🧪 Tests des APIs corrigées:"
echo "   curl -X POST -F \"file=@cv_christine.pdf\" http://localhost:5051/api/parse-cv/"
echo "   curl -X POST -F \"file=@fdp.pdf\" http://localhost:5053/api/parse-job"
echo ""
echo "🔍 Pour débugger (logs détaillés maintenant):"
echo "   docker-compose -f docker-compose.v2.yml logs -f cv-parser-v2"
echo "   docker-compose -f docker-compose.v2.yml logs -f job-parser-v2"