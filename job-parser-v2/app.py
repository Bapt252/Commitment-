#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
💼 SuperSmartMatch V2.1 - Job Parser Universal
NOUVEAU : Support multi-formats (PDF, Word, Images, Texte, HTML, RTF, ODT)
RÉTROCOMPATIBLE : API et workflow inchangés
"""

import os
import json
import tempfile
import subprocess
import logging
from pathlib import Path
from flask import Flask, request, jsonify

# Import des modules universels
from format_detector import format_detector
from text_extractor import text_extractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

class JobParserUniversal:
    """
    Parser Job Universal V2.1
    Support : PDF, Word, Images (OCR), Texte, HTML, RTF, OpenOffice
    """
    
    def __init__(self):
        # Configuration identique à V2
        self.parsers_dir = Path("./parsers")
        self.temp_dir = Path("/tmp/job_parsing")
        self.temp_dir.mkdir(exist_ok=True)
        
        self.fix_pdf_parser = self.parsers_dir / "fix-pdf-extraction.js"
        self.enhanced_parser = self.parsers_dir / "enhanced-mission-parser.js"
        
        # Log des chemins pour debug
        logger.info(f"📁 Dossier parsers: {self.parsers_dir}")
        logger.info(f"🔧 Fix PDF parser: {self.fix_pdf_parser} (existe: {self.fix_pdf_parser.exists()})")
        logger.info(f"🧠 Enhanced parser: {self.enhanced_parser} (existe: {self.enhanced_parser.exists()})")
        
        # Status des modules universels
        logger.info("🌍 Modules universels initialisés:")
        logger.info(f"   📋 Format detector: ✅")
        logger.info(f"   📄 Text extractor: ✅")
        supported_formats = format_detector.get_supported_formats()
        logger.info(f"   🎯 Formats supportés: {', '.join(supported_formats.keys())}")
    
    def extract_text_universal(self, file_path: str, filename: str) -> tuple:
        """
        Extraction de texte universelle avec fallback PDF
        
        Returns:
            tuple: (clean_text, text_file_path, extraction_metadata)
        """
        logger.info(f"🌍 Extraction universelle: {filename}")
        
        # Validation du fichier
        validation = format_detector.validate_file_for_parsing(file_path, filename)
        if not validation['can_parse']:
            raise Exception(f"Fichier invalide: {', '.join(validation['errors'])}")
        
        format_type = validation['detected_format']
        logger.info(f"🔍 Format détecté: {format_type} ({validation['mime_type']})")
        
        try:
            # Extraction universelle
            clean_text, extraction_metadata = text_extractor.extract_text_universal(
                file_path, format_type, filename
            )
            
            if not clean_text.strip():
                raise Exception("Aucun texte extrait du document")
            
            # Sauvegarde du texte extrait
            work_dir = self.temp_dir / f"work_{os.getpid()}"
            work_dir.mkdir(exist_ok=True)
            
            text_file = work_dir / "extracted_text.txt"
            text_file.write_text(clean_text, encoding='utf-8')
            
            logger.info(f"✅ Extraction universelle réussie: {len(clean_text)} caractères")
            return clean_text, str(text_file), extraction_metadata
            
        except Exception as e:
            logger.error(f"❌ Extraction universelle échouée: {e}")
            
            # Fallback vers méthode PDF classique (rétrocompatibilité)
            if format_type == 'pdf':
                logger.info("🔄 Fallback vers extraction PDF classique...")
                try:
                    return self.extract_clean_text_legacy(file_path)
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback PDF classique échoué: {fallback_error}")
            
            raise Exception(f"Impossible d'extraire le texte: {e}")
    
    def extract_clean_text_legacy(self, pdf_path: str) -> tuple:
        """
        Méthode d'extraction PDF classique (rétrocompatibilité)
        Identique à la V2 originale
        """
        logger.info("🔧 Extraction PDF classique (legacy)...")
        
        work_dir = self.temp_dir / f"work_{os.getpid()}"
        work_dir.mkdir(exist_ok=True)
        
        work_pdf = work_dir / "input.pdf"
        subprocess.run(['cp', str(pdf_path), str(work_pdf)], check=True)
        
        # Correction majeure : utiliser le chemin absolu des parsers
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
            raise Exception(f"Extraction PDF legacy échouée: {result.stderr}")
        
        text_file = work_dir / "extracted_text.txt"
        if not text_file.exists():
            text_files = list(work_dir.glob("*_clean_extracted.txt")) + list(work_dir.glob("*.txt"))
            if text_files:
                text_file = text_files[0]
            else:
                raise Exception("Aucun fichier texte généré")
        
        clean_text = text_file.read_text(encoding='utf-8')
        
        # Métadonnées legacy
        extraction_metadata = {
            'extraction_method': 'legacy_pdf',
            'format_type': 'pdf',
            'extraction_status': 'success'
        }
        
        logger.info(f"✅ Extraction PDF legacy: {len(clean_text)} caractères")
        return clean_text, str(text_file), extraction_metadata
    
    def parse_job_enriched(self, text_file_path: str) -> dict:
        """
        Parsing Job enrichi avec missions (identique V2)
        """
        logger.info("💼 Parsing Job enrichi avec missions...")
        
        work_dir = Path(text_file_path).parent
        
        # Correction majeure : utiliser le chemin absolu et corriger l'import
        enhanced_parser_absolute = str(self.enhanced_parser.absolute())
        
        script_content = f"""
const fs = require('fs');

// Correction : Import et instanciation corrigés
const EnhancedMissionParserClass = require('{enhanced_parser_absolute}');
const parser = new EnhancedMissionParserClass();

async function parseJob() {{
    try {{
        const text = fs.readFileSync('{text_file_path}', 'utf8');
        
        console.log('💼 Début parsing Job enrichi...');
        
        // Vérification : S'assurer que la fonction existe
        if (typeof parser.parseEnhancedJobWithMissions !== 'function') {{
            throw new Error('parseEnhancedJobWithMissions is not a function. Available methods: ' + Object.getOwnPropertyNames(Object.getPrototypeOf(parser)));
        }}
        
        const jobData = parser.parseEnhancedJobWithMissions(text);
        
        console.log('✅ Parsing Job enrichi terminé');
        console.log('🎯 Missions trouvées:', jobData.missions ? jobData.missions.length : 0);
        console.log('💼 Titre détecté:', jobData.job_info?.title || 'Non détecté');
        
        fs.writeFileSync('job_parsed_enriched.json', JSON.stringify(jobData, null, 2));
        console.log(JSON.stringify(jobData, null, 2));
        
    }} catch (error) {{
        console.error('❌ Erreur parsing Job enrichi:', error.message);
        console.error('Stack:', error.stack);
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
    
    def process_job_universal(self, uploaded_file) -> dict:
        """
        Workflow complet universel avec rétrocompatibilité
        """
        filename = uploaded_file.filename
        logger.info(f"🚀 Workflow Job universel: {filename}")
        
        # Sauvegarde temporaire
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            uploaded_file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # Extraction universelle
            clean_text, text_file_path, extraction_metadata = self.extract_text_universal(
                temp_file_path, filename
            )
            
            # Parsing enrichi (inchangé)
            job_data = self.parse_job_enriched(text_file_path)
            
            # Métadonnées enrichies
            job_data['_metadata'] = {
                'text_length': len(clean_text),
                'processing_status': 'success',
                'parser_version': 'universal_v2.1',
                'extraction_metadata': extraction_metadata,
                'supported_formats': list(format_detector.get_supported_formats().keys())
            }
            
            logger.info("✅ Job universel parsé avec succès")
            return job_data
            
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass

# Instance du parser universel
job_parser = JobParserUniversal()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check enrichi avec status formats"""
    supported_formats = format_detector.get_supported_formats()
    supported_extensions = format_detector.get_supported_extensions()
    
    return jsonify({
        'status': 'healthy',
        'service': 'job-parser-universal-v2.1',
        'parsers_available': {
            'fix_pdf_extraction': job_parser.fix_pdf_parser.exists(),
            'enhanced_mission_parser': job_parser.enhanced_parser.exists()
        },
        'universal_support': {
            'formats_supported': supported_formats,
            'extensions_supported': supported_extensions,
            'total_formats': len(supported_formats)
        },
        'capabilities': [
            'PDF (natif + fallback)',
            'Microsoft Word (.docx, .doc)',
            'Images avec OCR (.jpg, .png, .tiff, .bmp, .webp)',
            'Fichiers texte (.txt, .csv)',
            'Pages web (.html, .htm)',
            'Rich Text Format (.rtf)',
            'OpenOffice Document (.odt)'
        ]
    })

@app.route('/api/parse-job', methods=['POST'])
def parse_job():
    """
    API de parsing Job universel
    RÉTROCOMPATIBLE : même signature et format de réponse
    NOUVEAU : support multi-formats automatique
    """
    logger.info("💼 Nouvelle demande parsing Job universel...")
    
    try:
        # Validation de base (identique V2)
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nom de fichier vide'}), 400
        
        # NOUVEAU : Validation universelle au lieu de PDF uniquement
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file.save(temp_file.name)
            temp_file_path = temp_file.name
        
        try:
            # Validation du format
            validation = format_detector.validate_file_for_parsing(temp_file_path, file.filename)
            
            if not validation['can_parse']:
                error_msg = f"Format non supporté. {', '.join(validation['errors'])}"
                supported_ext = ', '.join(format_detector.get_supported_extensions())
                error_msg += f" Formats acceptés: {supported_ext}"
                
                return jsonify({'error': error_msg}), 400
            
            logger.info(f"🎯 Format validé: {validation['detected_format']}")
            
            # Restauration du fichier pour processing
            file.seek(0)  # Reset file pointer
            
            # Processing universel
            job_data = job_parser.process_job_universal(file)
            
            logger.info("✅ Job universel parsé avec succès")
            return jsonify({
                'status': 'success',
                'data': job_data
            })
            
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
    except Exception as e:
        logger.error(f"❌ Erreur parsing Job universel: {str(e)}")
        return jsonify({'error': f'Impossible de parser le job: {str(e)}'}), 500

@app.route('/api/formats', methods=['GET'])
def get_supported_formats():
    """
    NOUVEAU : Endpoint pour lister les formats supportés
    """
    formats = format_detector.get_supported_formats()
    extensions = format_detector.get_supported_extensions()
    
    return jsonify({
        'status': 'success',
        'supported_formats': formats,
        'supported_extensions': extensions,
        'total_formats': len(formats),
        'parser_version': 'universal_v2.1'
    })

if __name__ == '__main__':
    logger.info("🚀 Démarrage Job Parser Universal V2.1...")
    logger.info("🌍 Support multi-formats activé:")
    
    formats = format_detector.get_supported_formats()
    for fmt, desc in formats.items():
        logger.info(f"   ✅ {fmt.upper()}: {desc}")
    
    app.run(host='0.0.0.0', port=5053, debug=False)
