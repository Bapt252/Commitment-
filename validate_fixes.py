#!/usr/bin/env python3
"""
✅ Script de Validation Complète - SuperSmartMatch V2.1
Valide toutes les corrections apportées au système
"""

import requests
import subprocess
import json
from pathlib import Path
import time

class SystemValidator:
    
    def __init__(self):
        self.cv_parser_url = "http://localhost:5051"
        self.job_parser_url = "http://localhost:5053" 
        self.matching_api_url = "http://localhost:5055"
        
        self.results = {}
    
    def validate_folder_structure(self) -> dict:
        """Valide la structure des dossiers"""
        print("📁 VALIDATION STRUCTURE DOSSIERS")
        print("-" * 35)
        
        desktop = Path("~/Desktop").expanduser()
        
        folders = {
            'CV TEST': desktop / 'CV TEST',
            'FDP TEST': desktop / 'FDP TEST'
        }
        
        results = {}
        
        for name, folder_path in folders.items():
            if folder_path.exists():
                file_count = len([f for f in folder_path.iterdir() if f.is_file()])
                pdf_count = len([f for f in folder_path.iterdir() if f.suffix.lower() == '.pdf'])
                
                results[name] = {
                    'exists': True,
                    'total_files': file_count,
                    'pdf_files': pdf_count,
                    'path': str(folder_path)
                }
                print(f"   ✅ {name}: {file_count} fichiers ({pdf_count} PDF)")
            else:
                results[name] = {
                    'exists': False,
                    'path': str(folder_path)
                }
                print(f"   ❌ {name}: Non trouvé")
        
        return results
    
    def validate_batu_sam_file(self) -> dict:
        """Valide la présence et l'accessibilité de BATU Sam.pdf"""
        print("\n📄 VALIDATION BATU SAM.PDF")
        print("-" * 25)
        
        # Chercher le fichier dans plusieurs emplacements
        possible_paths = [
            Path("~/Desktop/BATU Sam.pdf").expanduser(),
            Path("~/Desktop/CV TEST/BATU Sam.pdf").expanduser(),
        ]
        
        for path in possible_paths:
            if path.exists():
                size = path.stat().st_size
                print(f"   ✅ Trouvé: {path}")
                print(f"   📊 Taille: {size} bytes")
                
                return {
                    'found': True,
                    'path': str(path),
                    'size': size
                }
        
        print(f"   ❌ BATU Sam.pdf non trouvé")
        return {'found': False}
    
    def validate_services_health(self) -> dict:
        """Valide l'état des services"""
        print("\n💊 VALIDATION SERVICES")
        print("-" * 20)
        
        services = {
            'CV Parser (5051)': self.cv_parser_url,
            'Job Parser (5053)': self.job_parser_url,
            'Matching API (5055)': self.matching_api_url
        }
        
        results = {}
        
        for name, url in services.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.ok:
                    results[name] = {
                        'status': 'healthy',
                        'response_time': response.elapsed.total_seconds(),
                        'details': response.json() if response.text else {}
                    }
                    print(f"   ✅ {name}: Opérationnel ({response.elapsed.total_seconds():.2f}s)")
                else:
                    results[name] = {
                        'status': 'unhealthy',
                        'status_code': response.status_code
                    }
                    print(f"   ❌ {name}: HTTP {response.status_code}")
            except Exception as e:
                results[name] = {
                    'status': 'unreachable',
                    'error': str(e)
                }
                print(f"   ❌ {name}: Inaccessible ({str(e)[:50]})")
        
        return results
    
    def validate_batu_sam_extraction(self) -> dict:
        """Valide l'extraction de BATU Sam.pdf"""
        print("\n🧪 VALIDATION EXTRACTION BATU SAM")
        print("-" * 33)
        
        batu_file = self.validate_batu_sam_file()
        if not batu_file['found']:
            return {'error': 'Fichier BATU Sam.pdf non trouvé'}
        
        file_path = batu_file['path']
        
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
                candidate_name = cv_data.get('candidate_name', 'Non trouvé')
                
                result = {
                    'success': True,
                    'text_length': text_length,
                    'candidate_name': candidate_name,
                    'has_missions': len(cv_data.get('professional_experience', [{}])[0].get('missions', [])) > 0
                }
                
                print(f"   📝 Texte extrait: {text_length} caractères")
                print(f"   👤 Candidat: {candidate_name}")
                
                if text_length > 100:
                    print(f"   ✅ Extraction réussie!")
                else:
                    print(f"   ⚠️  Extraction faible")
                
                return result
            else:
                print(f"   ❌ Erreur HTTP: {response.status_code}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_hugo_salvat_test(self) -> dict:
        """Valide le test Hugo Salvat (prévention faux positifs)"""
        print("\n🎯 VALIDATION TEST HUGO SALVAT")
        print("-" * 30)
        
        try:
            response = requests.get(f"{self.matching_api_url}/api/test/hugo-salvat", timeout=10)
            
            if response.ok:
                data = response.json()
                enhanced_result = data.get('enhanced_result', {})
                total_score = enhanced_result.get('total_score', 0)
                alerts = enhanced_result.get('alerts', [])
                
                print(f"   📊 Score obtenu: {total_score}%")
                print(f"   🚨 Alertes: {len(alerts)}")
                
                # Validation des critères
                score_ok = total_score < 30
                alerts_ok = len(alerts) > 0
                domain_incompatibility = any(
                    alert.get('type') == 'domain_incompatibility' 
                    for alert in alerts
                )
                
                result = {
                    'success': True,
                    'score': total_score,
                    'alerts_count': len(alerts),
                    'score_under_30': score_ok,
                    'has_alerts': alerts_ok,
                    'domain_incompatibility_detected': domain_incompatibility
                }
                
                if score_ok and alerts_ok:
                    print(f"   ✅ Test réussi: Score faible + Alertes présentes")
                else:
                    print(f"   ⚠️  Test partiellement réussi")
                
                return result
            else:
                print(f"   ❌ Erreur HTTP: {response.status_code}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_enhanced_script(self) -> dict:
        """Valide le script enhanced_batch_testing_fixed.py"""
        print("\n🔧 VALIDATION SCRIPT CORRIGÉ")
        print("-" * 28)
        
        try:
            # Test de découverte des fichiers
            result = subprocess.run([
                'python', 'enhanced_batch_testing_fixed.py', '--discover'
            ], capture_output=True, text=True, timeout=30)
            
            output = result.stdout
            
            # Analyser la sortie
            cv_found = "CV TEST" in output and "✅" in output
            fdp_found = "FDP TEST" in output and "✅" in output
            
            result_data = {
                'script_executed': result.returncode == 0,
                'cv_folder_found': cv_found,
                'fdp_folder_found': fdp_found,
                'output_preview': output[:300] + '...' if len(output) > 300 else output
            }
            
            if cv_found and fdp_found:
                print(f"   ✅ Script fonctionne: Dossiers trouvés")
            else:
                print(f"   ⚠️  Script fonctionne mais dossiers non trouvés")
                print(f"   📋 Voir output pour détails")
            
            return result_data
            
        except Exception as e:
            print(f"   ❌ Erreur exécution: {str(e)}")
            return {
                'script_executed': False,
                'error': str(e)
            }
    
    def run_complete_validation(self) -> dict:
        """Lance une validation complète du système"""
        print("✅ VALIDATION COMPLÈTE - SUPERSMARTMATCH V2.1")
        print("="*50)
        
        # 1. Validation structure dossiers
        self.results['folders'] = self.validate_folder_structure()
        
        # 2. Validation BATU Sam.pdf
        self.results['batu_sam_file'] = self.validate_batu_sam_file()
        
        # 3. Validation services
        self.results['services'] = self.validate_services_health()
        
        # 4. Validation extraction BATU Sam
        self.results['batu_sam_extraction'] = self.validate_batu_sam_extraction()
        
        # 5. Validation test Hugo Salvat
        self.results['hugo_salvat_test'] = self.validate_hugo_salvat_test()
        
        # 6. Validation script corrigé
        self.results['enhanced_script'] = self.validate_enhanced_script()
        
        return self.results
    
    def generate_validation_report(self) -> dict:
        """Génère un rapport de validation"""
        print(f"\n📋 RAPPORT DE VALIDATION")
        print("="*25)
        
        # Calcul du score global
        validations = []
        
        # Folders (2 points)
        cv_ok = self.results.get('folders', {}).get('CV TEST', {}).get('exists', False)
        fdp_ok = self.results.get('folders', {}).get('FDP TEST', {}).get('exists', False)
        validations.extend([cv_ok, fdp_ok])
        
        # Services (3 points)
        services = self.results.get('services', {})
        for service, data in services.items():
            validations.append(data.get('status') == 'healthy')
        
        # BATU Sam extraction (2 points)
        batu_extraction = self.results.get('batu_sam_extraction', {})
        validations.append(batu_extraction.get('success', False))
        validations.append(batu_extraction.get('text_length', 0) > 100)
        
        # Hugo Salvat test (2 points)
        hugo_test = self.results.get('hugo_salvat_test', {})
        validations.append(hugo_test.get('score_under_30', False))
        validations.append(hugo_test.get('has_alerts', False))
        
        # Script enhanced (1 point)
        script_test = self.results.get('enhanced_script', {})
        validations.append(script_test.get('script_executed', False))
        
        # Calcul du score
        passed = sum(validations)
        total = len(validations)
        score = (passed / total) * 100
        
        print(f"Score global: {score:.1f}% ({passed}/{total})")
        
        # Statut par catégorie
        print(f"\nDétail par catégorie:")
        print(f"   📁 Dossiers: {'✅' if cv_ok and fdp_ok else '❌'}")
        print(f"   💊 Services: {sum(1 for s in services.values() if s.get('status') == 'healthy')}/{len(services)} OK")
        print(f"   📄 BATU Sam: {'✅' if batu_extraction.get('text_length', 0) > 100 else '❌'}")
        print(f"   🎯 Hugo Salvat: {'✅' if hugo_test.get('score_under_30') and hugo_test.get('has_alerts') else '❌'}")
        print(f"   🔧 Script: {'✅' if script_test.get('script_executed') else '❌'}")
        
        # Recommandations
        recommendations = []
        
        if not (cv_ok and fdp_ok):
            recommendations.append("🔧 Corriger les noms de dossiers avec fix_folder_paths.py")
        
        if not batu_extraction.get('success'):
            recommendations.append("🩺 Réparer le CV Parser avec fix_cv_parser.py")
        
        unhealthy_services = [name for name, data in services.items() 
                            if data.get('status') != 'healthy']
        if unhealthy_services:
            recommendations.append(f"💊 Redémarrer services: {', '.join(unhealthy_services)}")
        
        if score >= 90:
            status = "🟢 EXCELLENT"
        elif score >= 75:
            status = "🟡 BON"
        elif score >= 50:
            status = "🟠 MOYEN"
        else:
            status = "🔴 CRITIQUE"
        
        return {
            'score': score,
            'status': status,
            'passed': passed,
            'total': total,
            'recommendations': recommendations
        }

def main():
    validator = SystemValidator()
    
    # Validation complète
    results = validator.run_complete_validation()
    
    # Rapport final
    report = validator.generate_validation_report()
    
    print(f"\n🎯 STATUT FINAL: {report['status']}")
    
    if report['recommendations']:
        print(f"\n🔧 ACTIONS RECOMMANDÉES:")
        for rec in report['recommendations']:
            print(f"   • {rec}")
    else:
        print(f"\n✅ SYSTÈME COMPLÈTEMENT OPÉRATIONNEL!")
    
    # Sauvegarde du rapport
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = f"validation_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'validation_results': results,
            'report_summary': report,
            'timestamp': timestamp
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n📋 Rapport détaillé sauvegardé: {report_file}")

if __name__ == "__main__":
    main()
