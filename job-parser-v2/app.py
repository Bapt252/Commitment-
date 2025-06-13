#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SuperSmartMatch V2 - Job Parser API ENRICHI
NOUVEAU : Extraction des missions détaillées du poste
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

class JobParserEnriched:
    def __init__(self):
        # ✅ CORRECTION : Utilisation d'un chemin relatif au lieu de Docker
        self.parsers_dir = Path("./parsers")
        self.temp_dir = Path("/tmp/job_parsing")
        self.temp_dir.mkdir(exist_ok=True)
        
        self.fix_pdf_parser = self.parsers_dir / "fix-pdf-extraction.js"
        self.enhanced_parser = self.parsers_dir / "enhanced-mission-parser.js"
    
    def extract_clean_text(self, pdf_path):
        """Étape 1 : Extraction du texte propre"""
        logger.info("🔧 Extraction texte propre...")
        
        work_dir = self.temp_dir / f"work_{os.getpid()}"
        work_dir.mkdir(exist_ok=True)
        
        work_pdf = work_dir / "input.pdf"
        subprocess.run(['cp', str(pdf_path), str(work_pdf)], check=True)
        
        # ✅ CORRECTION MAJEURE : Utiliser le chemin ABSOLU des parsers
        fix_pdf_parser_absolute = str(self.fix_pdf_parser.absolute())
        
        wrapper_script = f"""
const fs = require('fs');
const FixedPDFParser = require('{fix_pdf_parser_absolute}');

async function extractPDF() {{
    try {{
        const parser = new FixedPDFParser();
        const result = await parser.extractCleanText('input.pdf');
        fs.writeFileSync('extracted_text.txt', result.text);
        console.log('✅ Extraction terminée');
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
        
        if result.returncode != 0:
            raise Exception(f"Extraction PDF échouée: {result.stderr}")
        
        text_file = work_dir / "extracted_text.txt"
        if not text_file.exists():
            text_files = list(work_dir.glob("*_clean_extracted.txt")) + list(work_dir.glob("*.txt"))
            if text_files:
                text_file = text_files[0]
            else:
                raise Exception("Aucun fichier texte généré")
        
        clean_text = text_file.read_text(encoding='utf-8')
        logger.info(f"✅ Texte extrait: {len(clean_text)} caractères")
        return clean_text, str(text_file)
    
    def parse_job_enriched(self, text_file_path):
        """Étape 2 : Parsing Job enrichi avec missions"""
        logger.info("💼 Parsing Job enrichi avec missions...")
        
        work_dir = Path(text_file_path).parent
        
        # ✅ CORRECTION MAJEURE : Utiliser le chemin ABSOLU des parsers
        enhanced_parser_absolute = str(self.enhanced_parser.absolute())
        
        script_content = f"""
const fs = require('fs');
const EnhancedMissionParser = require('{enhanced_parser_absolute}');

async function parseJob() {{
    try {{
        const parser = new EnhancedMissionParser();
        const text = fs.readFileSync('{text_file_path}', 'utf8');
        
        console.log('💼 Début parsing Job enrichi...');
        const jobData = parser.parseEnhancedJobWithMissions(text);
        
        console.log('✅ Parsing Job enrichi terminé');
        console.log('🎯 Missions trouvées:', jobData.missions ? jobData.missions.length : 0);
        console.log('💼 Titre détecté:', jobData.job_info?.title || 'Non détecté');
        
        fs.writeFileSync('job_parsed_enriched.json', JSON.stringify(jobData, null, 2));
        console.log(JSON.stringify(jobData, null, 2));
        
    }} catch (error) {{
        console.error('❌ Erreur parsing Job enrichi:', error.message);
        process.exit(1);
    }}
}}

parseJob();
"""
        
        script_file = work_dir / "parse_job_enriched.js"
        script_file.write_text(script_content)
        
        result = subprocess.run(
            ['node', str(script_file)],
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        logger.info(f"📋 Parsing stdout: {result.stdout}")
        
        if result.returncode != 0:
            raise Exception(f"Parsing Job enrichi échoué: {result.stderr}")
        
        result_file = work_dir / "job_parsed_enriched.json"
        if result_file.exists():
            job_data = json.loads(result_file.read_text())
        else:
            lines = result.stdout.strip().split('\n')
            json_lines = [line for line in lines if line.startswith('{')]
            if json_lines:
                job_data = json.loads(json_lines[-1])
            else:
                raise Exception("Pas de JSON trouvé")
        
        logger.info(f"✅ Job enrichi parsé: {len(job_data.get('missions', []))} missions")
        return job_data
    
    def process_job(self, pdf_file):
        """Workflow complet enrichi"""
        logger.info("🚀 Workflow Job enrichi...")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            pdf_file.save(temp_pdf.name)
            temp_pdf_path = temp_pdf.name
        
        try:
            clean_text, text_file_path = self.extract_clean_text(temp_pdf_path)
            job_data = self.parse_job_enriched(text_file_path)
            
            job_data['_metadata'] = {
                'text_length': len(clean_text),
                'processing_status': 'success',
                'parser_version': 'enriched_v2'
            }
            
            return job_data
        finally:
            try:
                os.unlink(temp_pdf_path)
            except:
                pass

job_parser = JobParserEnriched()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'job-parser-v2-enriched',
        'parsers_available': {
            'fix_pdf_extraction': job_parser.fix_pdf_parser.exists(),
            'enhanced_mission_parser': job_parser.enhanced_parser.exists()
        }
    })

@app.route('/api/parse-job', methods=['POST'])
def parse_job():
    logger.info("💼 Nouvelle demande parsing Job enrichi...")
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Seuls les fichiers PDF sont acceptés'}), 400
        
        job_data = job_parser.process_job(file)
        
        logger.info("✅ Job enrichi parsé avec succès")
        return jsonify({
            'status': 'success',
            'data': job_data
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}")
        return jsonify({'error': f'Impossible de parser le job: {str(e)}'}), 500

if __name__ == '__main__':
    logger.info("🚀 Démarrage Job Parser V2 Enrichi...")
    app.run(host='0.0.0.0', port=5053, debug=False)
