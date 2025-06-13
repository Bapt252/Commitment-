#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 SuperSmartMatch V2.1 - Tests Universal Parsers
Script de validation pour tous les formats supportés
"""

import os
import requests
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from io import BytesIO

# Imports pour génération de fichiers de test
from docx import Document
from PIL import Image, ImageDraw, ImageFont
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UniversalParserTester:
    """
    Testeur complet pour les parsers universels
    Génère des fichiers de test et valide le parsing
    """
    
    def __init__(self, cv_parser_url="http://localhost:5051", job_parser_url="http://localhost:5053"):
        self.cv_parser_url = cv_parser_url
        self.job_parser_url = job_parser_url
        self.test_dir = Path(tempfile.gettempdir()) / "parser_tests"
        self.test_dir.mkdir(exist_ok=True)
        
        logger.info(f"🧪 Tests universels initialisés")
        logger.info(f"   CV Parser: {cv_parser_url}")
        logger.info(f"   Job Parser: {job_parser_url}")
        logger.info(f"   Dossier tests: {self.test_dir}")
    
    def create_test_files(self) -> Dict[str, str]:
        """
        Génère des fichiers de test pour tous les formats
        
        Returns:
            Dict mapping format -> file_path
        """
        logger.info("📝 Génération des fichiers de test...")
        
        test_files = {}
        
        # Contenu de test pour CV
        cv_content = """
ZACHARY MARTIN
Commercial Senior | Expert Vente B2B
📧 zachary.martin@email.fr | 📱 +33 6 12 34 56 78
🏠 Lyon, France

EXPÉRIENCE PROFESSIONNELLE

Commercial Senior - TechSolutions SAS (2020-2024)
• Développement portefeuille clients B2B (+150 comptes)
• Négociation contrats stratégiques (500K€-2M€)
• Management équipe commerciale (5 personnes)
• Prospection digitale et terrain
• Atteinte objectifs : 125% sur 4 années consécutives

Responsable Ventes - InnovCorp (2018-2020)
• Création département ventes régional
• Formation équipes commerciales
• Mise en place CRM Salesforce
• Croissance CA : +45% en 2 ans

COMPÉTENCES
• Vente B2B/B2C, Négociation, Management
• CRM (Salesforce, HubSpot), Prospection digitale
• Analyse financière, Gestion budgets
• Leadership, Communication, Adaptabilité

FORMATION
Master Commerce International - ESCP Business School (2018)
Licence Gestion Commerciale - Université Lyon 3 (2016)

LANGUES
Français (natif), Anglais (courant), Espagnol (intermédiaire)
"""
        
        # 1. Fichier texte (.txt)
        txt_file = self.test_dir / "cv_test.txt"
        txt_file.write_text(cv_content, encoding='utf-8')
        test_files['txt'] = str(txt_file)
        
        # 2. Fichier Word DOCX (.docx)
        try:
            docx_file = self.test_dir / "cv_test.docx"
            doc = Document()
            for line in cv_content.split('\n'):
                if line.strip():
                    doc.add_paragraph(line)
            doc.save(str(docx_file))
            test_files['docx'] = str(docx_file)
        except Exception as e:
            logger.warning(f"⚠️ Impossible de créer DOCX: {e}")
        
        # 3. Fichier HTML (.html)
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>CV Test</title>
    <meta charset="utf-8">
</head>
<body>
    <div>
        {cv_content.replace('\n', '<br>\n')}
    </div>
</body>
</html>
"""
        html_file = self.test_dir / "cv_test.html"
        html_file.write_text(html_content, encoding='utf-8')
        test_files['html'] = str(html_file)
        
        # 4. Fichier RTF (.rtf)
        rtf_content = f"""{{\\rtf1\\ansi\\deff0
{{\\fonttbl{{\\f0 Times New Roman;}}}}
\\f0\\fs24 {cv_content.replace('\n', '\\par\n')}
}}"""
        rtf_file = self.test_dir / "cv_test.rtf"
        rtf_file.write_text(rtf_content, encoding='utf-8')
        test_files['rtf'] = str(rtf_file)
        
        # 5. Image avec texte pour OCR (.png)
        try:
            img_file = self.test_dir / "cv_test.png"
            self._create_text_image(cv_content[:500], str(img_file))  # Première partie seulement
            test_files['image'] = str(img_file)
        except Exception as e:
            logger.warning(f"⚠️ Impossible de créer image OCR: {e}")
        
        logger.info(f"✅ {len(test_files)} fichiers de test générés")
        return test_files
    
    def _create_text_image(self, text: str, output_path: str):
        """Crée une image avec du texte pour tester l'OCR"""
        try:
            # Création d'une image blanche
            img = Image.new('RGB', (800, 1000), color='white')
            draw = ImageDraw.Draw(img)
            
            # Utilisation d'une police par défaut
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            # Écriture du texte ligne par ligne
            lines = text.split('\n')
            y_position = 50
            line_height = 20
            
            for line in lines[:30]:  # Limiter à 30 lignes
                if line.strip():
                    draw.text((50, y_position), line, fill='black', font=font)
                    y_position += line_height
            
            img.save(output_path)
            logger.info(f"🖼️ Image OCR créée: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ Erreur création image OCR: {e}")
    
    def test_parser_health(self, parser_url: str, parser_name: str) -> bool:
        """Test du health check d'un parser"""
        try:
            response = requests.get(f"{parser_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ {parser_name} healthy: {data.get('service', 'N/A')}")
                
                # Affichage des formats supportés si disponible
                if 'universal_support' in data:
                    formats = data['universal_support']['formats_supported']
                    logger.info(f"   📋 Formats: {', '.join(formats.keys())}")
                
                return True
            else:
                logger.error(f"❌ {parser_name} health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ {parser_name} non accessible: {e}")
            return False
    
    def test_file_parsing(self, file_path: str, format_type: str, parser_url: str, 
                         parser_name: str) -> Tuple[bool, Dict]:
        """
        Test du parsing d'un fichier spécifique
        
        Returns:
            Tuple[success, result_data]
        """
        try:
            endpoint = "/api/parse-cv/" if "cv" in parser_name.lower() else "/api/parse-job"
            
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                response = requests.post(
                    f"{parser_url}{endpoint}",
                    files=files,
                    timeout=60
                )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    result = data.get('data', {})
                    metadata = result.get('_metadata', {})
                    
                    logger.info(f"✅ {format_type.upper()} - {parser_name}")
                    logger.info(f"   📄 Texte: {metadata.get('text_length', 0)} caractères")
                    logger.info(f"   🔧 Méthode: {metadata.get('extraction_metadata', {}).get('extraction_method', 'N/A')}")
                    
                    return True, result
                else:
                    logger.error(f"❌ {format_type.upper()} - {parser_name}: {data.get('error', 'Erreur inconnue')}")
                    return False, {}
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                logger.error(f"❌ {format_type.upper()} - {parser_name}: HTTP {response.status_code}")
                logger.error(f"   Error: {error_data.get('error', response.text[:200])}")
                return False, {}
                
        except Exception as e:
            logger.error(f"❌ {format_type.upper()} - {parser_name}: Exception {e}")
            return False, {}
    
    def run_comprehensive_tests(self) -> Dict:
        """
        Lance tous les tests de validation
        
        Returns:
            Dictionnaire avec résultats détaillés
        """
        logger.info("🚀 Début des tests complets...")
        
        results = {
            'parsers_health': {},
            'format_tests': {
                'cv_parser': {},
                'job_parser': {}
            },
            'summary': {}
        }
        
        # 1. Tests de santé des parsers
        logger.info("\n📋 Tests de santé des parsers...")
        results['parsers_health']['cv'] = self.test_parser_health(self.cv_parser_url, "CV Parser")
        results['parsers_health']['job'] = self.test_parser_health(self.job_parser_url, "Job Parser")
        
        if not any(results['parsers_health'].values()):
            logger.error("❌ Aucun parser accessible - arrêt des tests")
            return results
        
        # 2. Génération des fichiers de test
        test_files = self.create_test_files()
        
        # 3. Tests par format et parser
        logger.info("\n🧪 Tests de parsing par format...")
        
        for format_type, file_path in test_files.items():
            logger.info(f"\n--- Test format: {format_type.upper()} ---")
            
            # Test CV Parser
            if results['parsers_health']['cv']:
                success, data = self.test_file_parsing(
                    file_path, format_type, self.cv_parser_url, "CV Parser"
                )
                results['format_tests']['cv_parser'][format_type] = {
                    'success': success,
                    'data_length': len(str(data)) if success else 0
                }
            
            # Test Job Parser
            if results['parsers_health']['job']:
                success, data = self.test_file_parsing(
                    file_path, format_type, self.job_parser_url, "Job Parser"
                )
                results['format_tests']['job_parser'][format_type] = {
                    'success': success,
                    'data_length': len(str(data)) if success else 0
                }
        
        # 4. Génération du résumé
        self._generate_test_summary(results)
        
        return results
    
    def _generate_test_summary(self, results: Dict):
        """Génère un résumé des tests"""
        logger.info("\n📊 RÉSUMÉ DES TESTS")
        logger.info("=" * 50)
        
        # Santé des parsers
        cv_healthy = results['parsers_health']['cv']
        job_healthy = results['parsers_health']['job']
        logger.info(f"🏥 Santé parsers: CV {'✅' if cv_healthy else '❌'} | Job {'✅' if job_healthy else '❌'}")
        
        # Tests par format
        for parser_name, parser_tests in results['format_tests'].items():
            if not parser_tests:
                continue
                
            successful_formats = sum(1 for test in parser_tests.values() if test['success'])
            total_formats = len(parser_tests)
            success_rate = (successful_formats / total_formats * 100) if total_formats > 0 else 0
            
            logger.info(f"📈 {parser_name}: {successful_formats}/{total_formats} formats OK ({success_rate:.1f}%)")
            
            # Détail par format
            for format_type, test_result in parser_tests.items():
                status = "✅" if test_result['success'] else "❌"
                logger.info(f"   {status} {format_type.upper()}")
        
        # Formats problématiques
        failed_formats = set()
        for parser_tests in results['format_tests'].values():
            for format_type, test in parser_tests.items():
                if not test['success']:
                    failed_formats.add(format_type)
        
        if failed_formats:
            logger.info(f"⚠️ Formats en échec: {', '.join(failed_formats)}")
        else:
            logger.info("🎉 Tous les formats testés avec succès !")
        
        # Sauvegarde des résultats
        results_file = self.test_dir / "test_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Résultats sauvegardés: {results_file}")
        
        results['summary'] = {
            'parsers_healthy': cv_healthy and job_healthy,
            'total_formats_tested': len(test_files),
            'failed_formats': list(failed_formats),
            'success_rate': 100 - (len(failed_formats) / len(test_files) * 100) if test_files else 0
        }

def main():
    """Fonction principale de test"""
    logger.info("🧪 SuperSmartMatch V2.1 - Tests Universal Parsers")
    logger.info("=" * 60)
    
    # Configuration des URLs (modifiables)
    cv_parser_url = os.getenv('CV_PARSER_URL', 'http://localhost:5051')
    job_parser_url = os.getenv('JOB_PARSER_URL', 'http://localhost:5053')
    
    # Lancement des tests
    tester = UniversalParserTester(cv_parser_url, job_parser_url)
    results = tester.run_comprehensive_tests()
    
    # Résultat final
    success_rate = results.get('summary', {}).get('success_rate', 0)
    if success_rate >= 80:
        logger.info(f"\n🎉 TESTS RÉUSSIS ({success_rate:.1f}% de réussite)")
        exit(0)
    else:
        logger.error(f"\n❌ TESTS PARTIELLEMENT ÉCHOUÉS ({success_rate:.1f}% de réussite)")
        exit(1)

if __name__ == "__main__":
    main()
