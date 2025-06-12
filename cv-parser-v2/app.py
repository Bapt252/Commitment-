#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 SuperSmartMatch V2 - CV Parser API ENRICHI - VERSION CORRIGÉE
NOUVEAU : Extraction des missions détaillées du CV
CORRECTIF : Chemins relatifs pour fonctionnement local
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

class CVParserEnriched:
    def __init__(self):
        # CORRECTIF: Utiliser le chemin relatif au lieu de /app/parsers
        current_dir = Path(__file__).parent
        self.parsers_dir = current_dir / "parsers"
        self.temp_dir = Path("/tmp/cv_parsing")
        self.temp_dir.mkdir(exist_ok=True)
        
        self.fix_pdf_parser = self.parsers_dir / "fix-pdf-extraction.js"
        self.enhanced_parser = self.parsers_dir / "enhanced-mission-parser.js"
        
        # Log des chemins pour debug
        logger.info(f"📁 Dossier parsers: {self.parsers_dir}")
        logger.info(f"🔧 Fix PDF parser: {self.fix_pdf_parser} (existe: {self.fix_pdf_parser.exists()})")
        logger.info(f"🧠 Enhanced parser: {self.enhanced_parser} (existe: {self.enhanced_parser.exists()})")
    
    def extract_clean_text(self, pdf_path):
        """Étape 1 : Extraction du texte propre"""
        logger.info("🔧 Extraction texte propre...")
        
        work_dir = self.temp_dir / f"work_{os.getpid()}"
        work_dir.mkdir(exist_ok=True)
        
        work_pdf = work_dir / "input.pdf"
        subprocess.run(['cp', str(pdf_path), str(work_pdf)], check=True)
        
        # CORRECTIF: Utiliser le chemin absolu correct
        wrapper_script = f"""
const fs = require('fs');
const FixedPDFParser = require('{self.fix_pdf_parser.absolute()}');

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
    
    def parse_cv_enriched(self, text_file_path):
        """Étape 2 : Parsing CV enrichi avec missions"""
        logger.info("🧠 Parsing CV enrichi avec missions...")
        
        work_dir = Path(text_file_path).parent
        
        # CORRECTIF: Utiliser le chemin absolu correct
        script_content = f"""
const fs = require('fs');
const EnhancedMissionParser = require('{self.enhanced_parser.absolute()}');

async function parseCV() {{
    try {{
        const parser = new EnhancedMissionParser();
        const text = fs.readFileSync('{text_file_path}', 'utf8');
        
        console.log('🧠 Début parsing CV enrichi...');
        const cvData = parser.parseEnhancedCVWithMissions(text);
        
        console.log('✅ Parsing CV enrichi terminé');
        console.log('🎯 Expériences trouvées:', cvData.professional_experience ? cvData.professional_experience.length : 0);
        console.log('👤 Nom détecté:', cvData.personal_info?.name || 'Non détecté');
        
        fs.writeFileSync('cv_parsed_enriched.json', JSON.stringify(cvData, null, 2));
        console.log(JSON.stringify(cvData, null, 2));
        
    }} catch (error) {{
        console.error('❌ Erreur parsing CV enrichi:', error.message);
        process.exit(1);
    }}
}}

parseCV();
"""
        
        script_file = work_dir / "parse_cv_enriched.js"
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
            raise Exception(f"Parsing CV enrichi échoué: {result.stderr}")
        
        result_file = work_dir / "cv_parsed_enriched.json"
        if result_file.exists():
            cv_data = json.loads(result_file.read_text())
        else:
            lines = result.stdout.strip().split('\n')
            json_lines = [line for line in lines if line.startswith('{')]
            if json_lines:
                cv_data = json.loads(json_lines[-1])
            else:
                raise Exception("Pas de JSON trouvé")
        
        logger.info(f"✅ CV enrichi parsé: {len(cv_data.get('professional_experience', []))} expériences")
        return cv_data
    
    def process_cv(self, pdf_file):
        """Workflow complet enrichi"""
        logger.info("🚀 Workflow CV enrichi...")
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            pdf_file.save(temp_pdf.name)
            temp_pdf_path = temp_pdf.name
        
        try:
            clean_text, text_file_path = self.extract_clean_text(temp_pdf_path)
            cv_data = self.parse_cv_enriched(text_file_path)
            
            cv_data['_metadata'] = {
                'text_length': len(clean_text),
                'processing_status': 'success',
                'parser_version': 'enriched_v2'
            }
            
            return cv_data
        finally:
            try:
                os.unlink(temp_pdf_path)
            except:
                pass

cv_parser = CVParserEnriched()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'cv-parser-v2-enriched',
        'parsers_available': {
            'fix_pdf_extraction': cv_parser.fix_pdf_parser.exists(),
            'enhanced_mission_parser': cv_parser.enhanced_parser.exists()
        }
    })

@app.route('/api/parse-cv/', methods=['POST'])
def parse_cv():
    logger.info("📄 Nouvelle demande parsing CV enrichi...")
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Seuls les fichiers PDF sont acceptés'}), 400
        
        cv_data = cv_parser.process_cv(file)
        
        logger.info("✅ CV enrichi parsé avec succès")
        return jsonify({
            'status': 'success',
            'data': cv_data
        })
        
    except Exception as e:
        logger.error(f"❌ Erreur: {str(e)}")
        return jsonify({'error': f'Impossible de parser le CV: {str(e)}'}), 500

if __name__ == '__main__':
    logger.info("🚀 Démarrage CV Parser V2 Enrichi - VERSION CORRIGÉE...")
    app.run(host='0.0.0.0', port=5051, debug=False)
