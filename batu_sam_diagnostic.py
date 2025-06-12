#!/usr/bin/env python3
"""
🩺 Diagnostic BATU Sam.pdf - Résolution des problèmes d'extraction
Script spécialisé pour diagnostiquer et résoudre le problème d'extraction de texte

PROBLÈME IDENTIFIÉ:
❌ BATU Sam.pdf extrait 0 caractères au lieu de 131 caractères précédemment

SOLUTIONS TESTÉES:
✅ Diagnostic approfondi du fichier
✅ Test de plusieurs méthodes d'extraction
✅ Vérification de l'intégrité du fichier
✅ Comparaison avec d'autres parsers
"""

import requests
import json
import os
import time
from pathlib import Path
import hashlib
import subprocess
from datetime import datetime

class BatuSamDiagnostic:
    
    def __init__(self):
        self.cv_parser_url = "http://localhost:5051"
        self.file_path = None
        self.diagnostic_results = {}
        
    def find_batu_sam_file(self, search_folders: list) -> str:
        """Trouve le fichier BATU Sam.pdf dans les dossiers spécifiés"""
        print("🔍 Recherche de BATU Sam.pdf...")
        
        possible_names = [
            "BATU Sam.pdf",
            "batu sam.pdf",
            "BATU_Sam.pdf",
            "batu_sam.pdf",
            "BATUSam.pdf",
            "batusam.pdf"
        ]
        
        for folder in search_folders:
            folder_path = Path(folder).expanduser().resolve()
            print(f"   📁 Recherche dans: {folder_path}")
            
            if not folder_path.exists():
                print(f"   ❌ Dossier non trouvé: {folder_path}")
                continue
                
            for name in possible_names:
                file_path = folder_path / name
                if file_path.exists():
                    print(f"   ✅ Trouvé: {file_path}")
                    return str(file_path)
            
            # Recherche récursive plus large
            for file in folder_path.rglob("*.pdf"):
                if "batu" in file.name.lower() and "sam" in file.name.lower():
                    print(f"   ✅ Trouvé (pattern match): {file}")
                    return str(file)
        
        print("   ❌ Fichier BATU Sam.pdf non trouvé")
        return None
    
    def analyze_file_integrity(self, file_path: str) -> dict:
        """Analyse l'intégrité du fichier PDF"""
        print("🔍 Analyse de l'intégrité du fichier...")
        
        try:
            file_path = Path(file_path)
            stats = file_path.stat()
            
            # Calcul du hash pour détecter les corruptions
            with open(file_path, 'rb') as f:
                content = f.read()
                md5_hash = hashlib.md5(content).hexdigest()
                sha256_hash = hashlib.sha256(content).hexdigest()
            
            # Vérification basique de la structure PDF
            is_valid_pdf = content.startswith(b'%PDF-')
            has_eof = content.endswith(b'%%EOF') or b'%%EOF' in content[-100:]
            
            analysis = {
                'file_size': stats.st_size,
                'modified_time': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                'md5_hash': md5_hash,
                'sha256_hash': sha256_hash,
                'starts_with_pdf_header': is_valid_pdf,
                'has_eof_marker': has_eof,
                'first_100_bytes': content[:100].hex(),
                'last_100_bytes': content[-100:].hex(),
                'is_readable': os.access(file_path, os.R_OK),
                'permissions': oct(stats.st_mode)[-3:]
            }
            
            print(f"   📏 Taille: {stats.st_size} bytes")
            print(f"   🔒 Hash MD5: {md5_hash}")
            print(f"   📄 Header PDF valide: {is_valid_pdf}")
            print(f"   🔚 Marqueur EOF: {has_eof}")
            
            return analysis
            
        except Exception as e:
            print(f"   ❌ Erreur analyse intégrité: {e}")
            return {'error': str(e)}
    
    def test_external_pdf_tools(self, file_path: str) -> dict:
        """Test avec des outils externes d'extraction PDF"""
        print("🛠️ Test avec outils externes...")
        
        results = {}
        
        # Test avec pdftotext (si disponible)
        try:
            result = subprocess.run(
                ['pdftotext', file_path, '-'], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            if result.returncode == 0:
                text_length = len(result.stdout.strip())
                results['pdftotext'] = {
                    'success': True,
                    'text_length': text_length,
                    'preview': result.stdout[:200] + '...' if len(result.stdout) > 200 else result.stdout
                }
                print(f"   ✅ pdftotext: {text_length} caractères extraits")
            else:
                results['pdftotext'] = {
                    'success': False,
                    'error': result.stderr
                }
                print(f"   ❌ pdftotext: {result.stderr}")
        except FileNotFoundError:
            results['pdftotext'] = {'success': False, 'error': 'pdftotext non installé'}
            print("   ⚠️ pdftotext non disponible")
        except Exception as e:
            results['pdftotext'] = {'success': False, 'error': str(e)}
            print(f"   ❌ pdftotext: {e}")
        
        # Test avec pdfplumber via Python (si disponible)
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                
                results['pdfplumber'] = {
                    'success': True,
                    'text_length': len(text),
                    'pages': len(pdf.pages),
                    'preview': text[:200] + '...' if len(text) > 200 else text
                }
                print(f"   ✅ pdfplumber: {len(text)} caractères extraits sur {len(pdf.pages)} pages")
        except ImportError:
            results['pdfplumber'] = {'success': False, 'error': 'pdfplumber non installé'}
            print("   ⚠️ pdfplumber non disponible")
        except Exception as e:
            results['pdfplumber'] = {'success': False, 'error': str(e)}
            print(f"   ❌ pdfplumber: {e}")
        
        # Test avec PyPDF2 (si disponible)
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                
                results['pypdf2'] = {
                    'success': True,
                    'text_length': len(text),
                    'pages': len(reader.pages),
                    'preview': text[:200] + '...' if len(text) > 200 else text
                }
                print(f"   ✅ PyPDF2: {len(text)} caractères extraits sur {len(reader.pages)} pages")
        except ImportError:
            results['pypdf2'] = {'success': False, 'error': 'PyPDF2 non installé'}
            print("   ⚠️ PyPDF2 non disponible")
        except Exception as e:
            results['pypdf2'] = {'success': False, 'error': str(e)}
            print(f"   ❌ PyPDF2: {e}")
        
        return results
    
    def test_cv_parser_service(self, file_path: str) -> dict:
        """Test avec le service CV Parser (5051)"""
        print("🧪 Test avec CV Parser Service...")
        
        results = {}
        
        # Test avec force_refresh=true
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    f"{self.cv_parser_url}/api/parse-cv/",
                    files={'file': f},
                    data={'force_refresh': 'true'},
                    timeout=30
                )
            
            if response.ok:
                cv_data = response.json()
                text_length = len(cv_data.get('raw_text', ''))
                
                results['force_refresh_true'] = {
                    'success': True,
                    'status_code': response.status_code,
                    'text_length': text_length,
                    'candidate_name': cv_data.get('candidate_name'),
                    'missions_count': len(cv_data.get('professional_experience', [{}])[0].get('missions', [])),
                    'skills_count': len(cv_data.get('technical_skills', []) + cv_data.get('soft_skills', [])),
                    'raw_response': cv_data
                }
                print(f"   ✅ force_refresh=true: {text_length} caractères")
            else:
                results['force_refresh_true'] = {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
                print(f"   ❌ force_refresh=true: HTTP {response.status_code}")
                
        except Exception as e:
            results['force_refresh_true'] = {'success': False, 'error': str(e)}
            print(f"   ❌ force_refresh=true: {e}")
        
        # Test avec force_refresh=false
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    f"{self.cv_parser_url}/api/parse-cv/",
                    files={'file': f},
                    data={'force_refresh': 'false'},
                    timeout=30
                )
            
            if response.ok:
                cv_data = response.json()
                text_length = len(cv_data.get('raw_text', ''))
                
                results['force_refresh_false'] = {
                    'success': True,
                    'status_code': response.status_code,
                    'text_length': text_length,
                    'candidate_name': cv_data.get('candidate_name'),
                    'missions_count': len(cv_data.get('professional_experience', [{}])[0].get('missions', [])),
                    'skills_count': len(cv_data.get('technical_skills', []) + cv_data.get('soft_skills', [])),
                    'raw_response': cv_data
                }
                print(f"   ✅ force_refresh=false: {text_length} caractères")
            else:
                results['force_refresh_false'] = {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text
                }
                print(f"   ❌ force_refresh=false: HTTP {response.status_code}")
                
        except Exception as e:
            results['force_refresh_false'] = {'success': False, 'error': str(e)}
            print(f"   ❌ force_refresh=false: {e}")
        
        return results
    
    def check_cv_parser_service_health(self) -> dict:
        """Vérifie l'état du service CV Parser"""
        print("💊 Vérification de l'état du CV Parser Service...")
        
        try:
            response = requests.get(f"{self.cv_parser_url}/health", timeout=10)
            if response.ok:
                health_data = response.json()
                print("   ✅ Service CV Parser opérationnel")
                return {'healthy': True, 'data': health_data}
            else:
                print(f"   ❌ Service CV Parser: HTTP {response.status_code}")
                return {'healthy': False, 'status_code': response.status_code}
        except requests.exceptions.ConnectionError:
            print("   ❌ Service CV Parser: Connexion impossible")
            return {'healthy': False, 'error': 'Connection refused'}
        except Exception as e:
            print(f"   ❌ Service CV Parser: {e}")
            return {'healthy': False, 'error': str(e)}
    
    def run_complete_diagnosis(self, file_path: str = None) -> dict:
        """Lance un diagnostic complet"""
        print("🩺 DIAGNOSTIC COMPLET - BATU Sam.pdf")
        print("="*50)
        
        if not file_path:
            # Recherche automatique du fichier
            file_path = self.find_batu_sam_file([
                "~/Desktop/CV TEST",
                "~/Desktop/CV TEST/",
                "~/Desktop/",
                "~/Downloads/",
                "."
            ])
            
            if not file_path:
                return {
                    'status': 'file_not_found',
                    'message': 'Fichier BATU Sam.pdf non trouvé'
                }
        
        self.file_path = file_path
        print(f"📄 Fichier analysé: {file_path}")
        
        # Diagnostic complet
        self.diagnostic_results = {
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'file_integrity': self.analyze_file_integrity(file_path),
            'service_health': self.check_cv_parser_service_health(),
            'cv_parser_tests': self.test_cv_parser_service(file_path),
            'external_tools_tests': self.test_external_pdf_tools(file_path)
        }
        
        return self.diagnostic_results
    
    def generate_diagnostic_report(self) -> str:
        """Génère un rapport de diagnostic"""
        if not self.diagnostic_results:
            return "Aucun diagnostic effectué"
        
        report = []
        report.append("🩺 RAPPORT DE DIAGNOSTIC - BATU Sam.pdf")
        report.append("="*50)
        
        # Analyse de l'intégrité
        integrity = self.diagnostic_results.get('file_integrity', {})
        if 'error' not in integrity:
            report.append(f"📏 Taille du fichier: {integrity.get('file_size', 'N/A')} bytes")
            report.append(f"📄 Header PDF valide: {'✅' if integrity.get('starts_with_pdf_header') else '❌'}")
            report.append(f"🔚 Marqueur EOF: {'✅' if integrity.get('has_eof_marker') else '❌'}")
        
        # État du service
        service_health = self.diagnostic_results.get('service_health', {})
        report.append(f"💊 Service CV Parser: {'✅ Opérationnel' if service_health.get('healthy') else '❌ Problème'}")
        
        # Tests d'extraction
        cv_tests = self.diagnostic_results.get('cv_parser_tests', {})
        report.append("\n🧪 TESTS D'EXTRACTION:")
        
        for test_name, result in cv_tests.items():
            if result.get('success'):
                length = result.get('text_length', 0)
                report.append(f"   • {test_name}: ✅ {length} caractères extraits")
            else:
                report.append(f"   • {test_name}: ❌ {result.get('error', 'Erreur inconnue')}")
        
        # Outils externes
        external_tests = self.diagnostic_results.get('external_tools_tests', {})
        report.append("\n🛠️ OUTILS EXTERNES:")
        
        for tool_name, result in external_tests.items():
            if result.get('success'):
                length = result.get('text_length', 0)
                report.append(f"   • {tool_name}: ✅ {length} caractères extraits")
            else:
                report.append(f"   • {tool_name}: ❌ {result.get('error', 'Non disponible')}")
        
        # Recommandations
        report.append("\n🎯 RECOMMANDATIONS:")
        
        # Analyse des résultats pour générer des recommandations
        cv_success = any(test.get('success') and test.get('text_length', 0) > 0 
                        for test in cv_tests.values())
        external_success = any(test.get('success') and test.get('text_length', 0) > 0 
                             for test in external_tests.values())
        
        if not cv_success and not external_success:
            report.append("   ❌ CRITIQUE: Aucun outil ne peut extraire le texte")
            report.append("   → Le fichier PDF pourrait être corrompu ou protégé")
            report.append("   → Essayer de régénérer le PDF ou utiliser un autre fichier")
        elif not cv_success and external_success:
            report.append("   ⚠️ PROBLÈME SERVICE: Le CV Parser ne fonctionne pas correctement")
            report.append("   → Redémarrer le service CV Parser (port 5051)")
            report.append("   → Vérifier les logs du service pour plus de détails")
            report.append("   → Mettre à jour les dépendances PDF du service")
        elif cv_success:
            report.append("   ✅ RÉSOLU: Le CV Parser fonctionne maintenant")
            report.append("   → Le problème était temporaire")
            report.append("   → Continuer les tests normalement")
        
        return "\n".join(report)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Diagnostic BATU Sam.pdf')
    parser.add_argument('--file', help='Chemin vers BATU Sam.pdf (optionnel)')
    parser.add_argument('--save-report', help='Sauvegarder le rapport en JSON')
    
    args = parser.parse_args()
    
    diagnostic = BatuSamDiagnostic()
    
    # Lancement du diagnostic
    results = diagnostic.run_complete_diagnosis(args.file)
    
    # Affichage du rapport
    print("\n" + diagnostic.generate_diagnostic_report())
    
    # Sauvegarde si demandée
    if args.save_report:
        with open(args.save_report, 'w', encoding='utf-8') as f:
            json.dump(diagnostic.diagnostic_results, f, indent=2, ensure_ascii=False)
        print(f"\n📋 Rapport détaillé sauvegardé: {args.save_report}")
    
    # Déterminer le statut de sortie
    cv_tests = results.get('cv_parser_tests', {})
    success = any(test.get('success') and test.get('text_length', 0) > 0 
                  for test in cv_tests.values())
    
    if success:
        print("\n✅ DIAGNOSTIC: Problème résolu!")
        exit(0)
    else:
        print("\n❌ DIAGNOSTIC: Problème persistant")
        exit(1)

if __name__ == '__main__':
    main()
