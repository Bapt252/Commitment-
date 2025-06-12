#!/usr/bin/env python3
"""
🧪 SCRIPT DE TEST - SuperSmartMatch V2.1 Enhanced
Test automatisé du nouveau système de matching avec cas réels
"""

import requests
import json
import time
from pathlib import Path
import argparse
from typing import Dict, List, Optional
from datetime import datetime
import os

# Configuration
API_BASE_URL = "http://localhost:5055"
CV_PARSER_URL = "http://localhost:5051"
JOB_PARSER_URL = "http://localhost:5053"

class MatchingTester:
    
    def __init__(self, api_url: str = API_BASE_URL):
        self.api_url = api_url
        self.test_results = []
    
    def test_api_health(self) -> bool:
        """Test de la connexion à l'API"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                info = response.json()
                print(f"✅ API {info['service']} v{info['version']} - Status: {info['status']}")
                return True
            else:
                print(f"❌ API Health Check Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erreur connexion API: {e}")
            return False
    
    def parse_cv_file(self, cv_path: str) -> Optional[Dict]:
        """Parse un CV PDF via l'API"""
        try:
            with open(cv_path, 'rb') as f:
                response = requests.post(
                    f"{CV_PARSER_URL}/api/parse-cv/",
                    files={'file': f},
                    data={'force_refresh': 'false'},
                    timeout=30
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erreur parsing CV: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur parsing CV {cv_path}: {e}")
            return None
    
    def parse_job_file(self, job_path: str) -> Optional[Dict]:
        """Parse une fiche de poste PDF via l'API"""
        try:
            with open(job_path, 'rb') as f:
                response = requests.post(
                    f"{JOB_PARSER_URL}/api/parse-job",
                    files={'file': f},
                    data={'force_refresh': 'false'},
                    timeout=30
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erreur parsing Job: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur parsing Job {job_path}: {e}")
            return None
    
    def test_matching_enhanced(self, cv_data: Dict, job_data: Dict) -> Optional[Dict]:
        """Test du nouveau système de matching amélioré"""
        try:
            payload = {
                'cv_data': cv_data,
                'job_data': job_data
            }
            
            response = requests.post(
                f"{self.api_url}/api/matching/enhanced",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erreur matching: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"❌ Erreur test matching: {e}")
            return None
    
    def test_matching_legacy(self, cv_data: Dict, job_data: Dict) -> Optional[Dict]:
        """Test de l'ancien système pour comparaison"""
        try:
            payload = {
                'cv_data': cv_data,
                'job_data': job_data
            }
            
            response = requests.post(
                f"{self.api_url}/api/matching/complete",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erreur matching legacy: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erreur test matching legacy: {e}")
            return None
    
    def test_hugo_salvat_case(self) -> Dict:
        """Test du cas problématique Hugo Salvat"""
        try:
            response = requests.get(f"{self.api_url}/api/test/hugo-salvat", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erreur test Hugo Salvat: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Erreur test Hugo Salvat: {e}")
            return {}
    
    def run_file_comparison(self, cv_path: str, job_path: str, description: str = "") -> Dict:
        """Compare ancien vs nouveau système sur des fichiers réels"""
        print(f"\n{'='*60}")
        print(f"🧪 TEST: {description or f'{Path(cv_path).name} vs {Path(job_path).name}'}")
        print(f"{'='*60}")
        
        # Étape 1: Parsing des fichiers
        print("📄 Parsing des fichiers...")
        cv_data = self.parse_cv_file(cv_path)
        if not cv_data:
            return {'error': 'Erreur parsing CV'}
        
        job_data = self.parse_job_file(job_path)
        if not job_data:
            return {'error': 'Erreur parsing Job'}
        
        print(f"   ✅ CV parsé: {cv_data.get('candidate_name', 'Nom non trouvé')}")
        print(f"   ✅ Job parsé: {job_data.get('title', 'Titre non trouvé')}")
        
        # Étape 2: Test du nouveau système
        print("\n🚀 Test système amélioré V2.1...")
        enhanced_result = self.test_matching_enhanced(cv_data, job_data)
        
        # Étape 3: Test de l'ancien système pour comparaison
        print("🔄 Test système legacy pour comparaison...")
        legacy_result = self.test_matching_legacy(cv_data, job_data)
        
        # Analyse des résultats
        if enhanced_result and legacy_result:
            enhanced_score = enhanced_result['matching_analysis']['total_score']
            legacy_score = legacy_result['matching_analysis']['total_score']
            
            print(f"\n📊 RÉSULTATS COMPARATIFS:")
            print(f"   🆕 Système V2.1: {enhanced_score}%")
            print(f"   🔄 Système Legacy: {legacy_score}%")
            print(f"   📈 Différence: {enhanced_score - legacy_score:+.1f}%")
            
            # Analyse des alertes
            alerts = enhanced_result['matching_analysis'].get('alerts', [])
            if alerts:
                print(f"\n⚠️  ALERTES DÉTECTÉES:")
                for alert in alerts:
                    severity_icon = "🚨" if alert['severity'] == 'critical' else "⚠️"
                    print(f"   {severity_icon} {alert['message']}")
            
            # Analyse des domaines
            domain_analysis = enhanced_result['matching_analysis'].get('domain_analysis', {})
            if domain_analysis:
                print(f"\n🎯 ANALYSE DES DOMAINES:")
                print(f"   CV: {domain_analysis.get('cv_domain', 'N/A')}")
                print(f"   Job: {domain_analysis.get('job_domain', 'N/A')}")
                print(f"   Compatibilité: {domain_analysis.get('compatibility_level', 'N/A')}")
                print(f"   Message: {domain_analysis.get('compatibility_message', 'N/A')}")
        
        result = {
            'cv_path': cv_path,
            'job_path': job_path,
            'description': description,
            'enhanced_result': enhanced_result,
            'legacy_result': legacy_result,
            'timestamp': datetime.now().isoformat()
        }
        
        self.test_results.append(result)
        return result
    
    def run_predefined_tests(self) -> None:
        """Lance une série de tests prédéfinis"""
        print("\n🧪 LANCEMENT DES TESTS PRÉDÉFINIS")
        print("="*50)
        
        # Test 1: Cas Hugo Salvat
        print("\n🎯 Test 1: Cas Hugo Salvat (Commercial IT vs Assistant Facturation)")
        hugo_result = self.test_hugo_salvat_case()
        if hugo_result:
            test_status = hugo_result.get('test_status', 'unknown')
            score = hugo_result.get('enhanced_result', {}).get('total_score', 0)
            print(f"   Score: {score}%")
            print(f"   Status: {'✅ PASSÉ' if test_status == 'success' else '⚠️ ATTENTION'}")
            
            validation = hugo_result.get('validation', {})
            print(f"   Score < 30%: {'✅' if validation.get('score_under_30') else '❌'}")
            print(f"   Alertes présentes: {'✅' if validation.get('alerts_present') else '❌'}")
            print(f"   Incompatibilité détectée: {'✅' if validation.get('domain_incompatibility_detected') else '❌'}")
    
    def save_results(self, output_file: str = "test_results.json") -> None:
        """Sauvegarde les résultats des tests"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_tests': len(self.test_results),
                    'results': self.test_results
                }, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Résultats sauvegardés dans: {output_file}")
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
    
    def print_summary(self) -> None:
        """Affiche un résumé des tests"""
        if not self.test_results:
            print("\n📊 Aucun test executé")
            return
        
        print(f"\n📊 RÉSUMÉ DES TESTS ({len(self.test_results)} tests)")
        print("="*50)
        
        for i, result in enumerate(self.test_results, 1):
            if 'error' in result:
                print(f"{i}. ❌ {result['description']} - {result['error']}")
            else:
                enhanced = result.get('enhanced_result', {}).get('matching_analysis', {})
                legacy = result.get('legacy_result', {}).get('matching_analysis', {})
                
                enhanced_score = enhanced.get('total_score', 0)
                legacy_score = legacy.get('total_score', 0)
                
                improvement = "📈" if enhanced_score < legacy_score else "📉" if enhanced_score > legacy_score else "➡️"
                
                print(f"{i}. {improvement} {result['description']}")
                print(f"   V2.1: {enhanced_score}% | Legacy: {legacy_score}% | Δ: {enhanced_score-legacy_score:+.1f}%")

def create_sample_data():
    """Crée des données d'exemple pour test sans fichiers"""
    return {
        'cv_commercial': {
            'candidate_name': 'Test Commercial',
            'current_position': 'Responsable Commercial',
            'professional_experience': [{
                'missions': [
                    {'description': 'Développement commercial B2B', 'category': 'commercial'},
                    {'description': 'Prospection clients', 'category': 'commercial'},
                    {'description': 'Négociation contrats', 'category': 'commercial'}
                ]
            }],
            'technical_skills': ['CRM', 'commercial', 'négociation'],
            'experience_years': 5
        },
        'cv_comptable': {
            'candidate_name': 'Test Comptable',
            'current_position': 'Assistant Comptable',
            'professional_experience': [{
                'missions': [
                    {'description': 'Saisie écritures comptables', 'category': 'comptabilité'},
                    {'description': 'Facturation clients', 'category': 'facturation'},
                    {'description': 'Contrôle des comptes', 'category': 'contrôle'}
                ]
            }],
            'technical_skills': ['comptabilité', 'facturation', 'excel'],
            'experience_years': 3
        },
        'job_commercial': {
            'title': 'Responsable Commercial IT',
            'missions': [
                {'description': 'Développement business', 'category': 'commercial'},
                {'description': 'Gestion portefeuille clients', 'category': 'commercial'}
            ],
            'requirements': {
                'technical_skills': ['commercial', 'IT'],
                'experience_level': '3-5 ans'
            }
        },
        'job_facturation': {
            'title': 'Assistant Facturation',
            'missions': [
                {'description': 'Facturation clients', 'category': 'facturation'},
                {'description': 'Saisie comptable', 'category': 'comptabilité'}
            ],
            'requirements': {
                'technical_skills': ['facturation', 'comptabilité'],
                'experience_level': '1-3 ans'
            }
        }
    }

def main():
    parser = argparse.ArgumentParser(description='Test SuperSmartMatch V2.1 Enhanced')
    parser.add_argument('--cv', type=str, help='Chemin vers le CV PDF')
    parser.add_argument('--job', type=str, help='Chemin vers la fiche de poste PDF')
    parser.add_argument('--cvs-folder', type=str, help='Dossier contenant plusieurs CV')
    parser.add_argument('--jobs-folder', type=str, help='Dossier contenant plusieurs fiches de poste')
    parser.add_argument('--api-url', type=str, default=API_BASE_URL, help='URL de l\'API')
    parser.add_argument('--output', type=str, default='test_results.json', help='Fichier de sortie')
    parser.add_argument('--sample-test', action='store_true', help='Test avec données d\'exemple')
    parser.add_argument('--predefined-tests', action='store_true', help='Lance les tests prédéfinis')
    
    args = parser.parse_args()
    
    print("🚀 SUPERSMARTMATCH V2.1 - SCRIPT DE TEST")
    print("="*50)
    
    tester = MatchingTester(args.api_url)
    
    # Test de la connexion API
    if not tester.test_api_health():
        print("❌ Impossible de se connecter à l'API. Vérifiez que le serveur est démarré.")
        return
    
    # Tests prédéfinis
    if args.predefined_tests:
        tester.run_predefined_tests()
    
    # Test avec données d'exemple
    if args.sample_test:
        print("\n🧪 TEST AVEC DONNÉES D'EXEMPLE")
        sample_data = create_sample_data()
        
        # Test 1: Commercial → Commercial (bon match)
        print("\n✅ Test Commercial → Commercial (attendu: score élevé)")
        enhanced_result = tester.test_matching_enhanced(
            sample_data['cv_commercial'], 
            sample_data['job_commercial']
        )
        if enhanced_result:
            score = enhanced_result['matching_analysis']['total_score']
            print(f"   Score: {score}%")
        
        # Test 2: Commercial → Facturation (mauvais match)
        print("\n❌ Test Commercial → Facturation (attendu: score faible)")
        enhanced_result = tester.test_matching_enhanced(
            sample_data['cv_commercial'], 
            sample_data['job_facturation']
        )
        if enhanced_result:
            score = enhanced_result['matching_analysis']['total_score']
            alerts = enhanced_result['matching_analysis'].get('alerts', [])
            print(f"   Score: {score}%")
            print(f"   Alertes: {len(alerts)} détectée(s)")
    
    # Test avec fichiers spécifiques
    if args.cv and args.job:
        if os.path.exists(args.cv) and os.path.exists(args.job):
            tester.run_file_comparison(args.cv, args.job, "Test fichiers spécifiés")
        else:
            print("❌ Fichiers CV ou Job introuvables")
    
    # Test avec dossiers de fichiers
    if args.cvs_folder and args.jobs_folder:
        cv_folder = Path(args.cvs_folder)
        job_folder = Path(args.jobs_folder)
        
        if cv_folder.exists() and job_folder.exists():
            cv_files = list(cv_folder.glob("*.pdf"))
            job_files = list(job_folder.glob("*.pdf"))
            
            print(f"\n📁 Tests en lot: {len(cv_files)} CVs vs {len(job_files)} Jobs")
            
            for cv_file in cv_files[:3]:  # Limite à 3 CVs pour éviter la surcharge
                for job_file in job_files[:2]:  # Limite à 2 Jobs par CV
                    tester.run_file_comparison(
                        str(cv_file), 
                        str(job_file), 
                        f"{cv_file.stem} vs {job_file.stem}"
                    )
        else:
            print("❌ Dossiers CVs ou Jobs introuvables")
    
    # Résumé et sauvegarde
    tester.print_summary()
    tester.save_results(args.output)
    
    print(f"\n✅ Tests terminés ! Résultats disponibles dans {args.output}")

if __name__ == "__main__":
    main()
