#!/usr/bin/env python3
"""
🧪 SuperSmartMatch V2.1 - Tests Massifs et Benchmarking (CORRIGÉ V2)
Script avancé pour tester et optimiser le système en lot
Supports: PDF, DOC, DOCX, PNG, JPG, JPEG
CORRECTIFS: Gestion des espaces + bon CV de Sam
"""

import requests
import json
import os
import time
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
import statistics
from datetime import datetime
import argparse
import concurrent.futures
from threading import Lock

class EnhancedTestSuite:
    
    def __init__(self, base_url="http://localhost:5055"):
        self.base_url = base_url
        self.results = []
        self.stats = {}
        self.lock = Lock()
        
        # Formats de fichiers supportés
        self.supported_cv_formats = {'.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg'}
        self.supported_job_formats = {'.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg'}
        
    def resolve_folder_path(self, folder_path: str) -> Path:
        """Résout le chemin d'un dossier en gérant les espaces et tildes"""
        # Étendre le tilde (~) d'abord
        expanded_path = os.path.expanduser(folder_path)
        
        # Convertir en objet Path et résoudre
        resolved_path = Path(expanded_path).resolve()
        
        return resolved_path
        
    def find_files_in_folder(self, folder_path: str, file_types: set) -> List[Path]:
        """Trouve tous les fichiers supportés dans un dossier (CORRIGÉ)"""
        try:
            folder = self.resolve_folder_path(folder_path)
            found_files = []
            
            print(f"🔍 Recherche dans: {folder}")
            
            if not folder.exists():
                print(f"❌ Dossier non trouvé: {folder}")
                # Essayer des chemins alternatifs
                alternative_paths = [
                    folder_path.replace(' ', '\\ '),  # Échapper les espaces
                    folder_path.strip(),              # Supprimer espaces début/fin
                    folder_path.replace('\\\\', '/'),   # Normaliser les slashes
                ]
                
                for alt_path in alternative_paths:
                    alt_folder = self.resolve_folder_path(alt_path)
                    if alt_folder.exists():
                        print(f"✅ Chemin alternatif trouvé: {alt_folder}")
                        folder = alt_folder
                        break
                else:
                    # Essayer de lister le parent pour aider au debug
                    parent = folder.parent
                    if parent.exists():
                        print(f"📂 Contenu du dossier parent ({parent}):")
                        for item in parent.iterdir():
                            if item.is_dir():
                                print(f"   📁 {item.name}")
                    return []
            
            print(f"✅ Dossier accessible: {folder}")
            
            # Compter le nombre total de fichiers
            total_files = 0
            supported_files = 0
            
            for item in folder.iterdir():
                if item.is_file():
                    total_files += 1
                    ext = item.suffix.lower()
                    if ext in file_types:
                        found_files.append(item)
                        supported_files += 1
            
            print(f"   📊 {total_files} fichiers total, {supported_files} supportés")
            
            # Afficher les formats trouvés
            formats_found = {}
            for file_path in found_files:
                ext = file_path.suffix.lower()
                formats_found[ext] = formats_found.get(ext, 0) + 1
            
            if formats_found:
                print(f"   📄 Formats: {dict(formats_found)}")
            
            return sorted(found_files)
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche dans {folder_path}: {e}")
            return []
    
    def test_problematic_files(self) -> Dict:
        """Test des fichiers spécifiquement problématiques identifiés"""
        print(f"\n🔍 TEST FICHIERS PROBLÉMATIQUES IDENTIFIÉS")
        print("-" * 50)
        
        # Fichiers problématiques connus avec leurs chemins corrects
        problematic_files = {
            'BATU Sam (Desktop)': "/Users/baptistecomas/Desktop/BATU Sam.pdf",
            'Sam Candidature (CV TEST)': "/Users/baptistecomas/Desktop/CV TEST/Bcom HR - Candidature de Sam.pdf", 
            'Hugo Salvat': "/Users/baptistecomas/Desktop/CV TEST/SALVAT Hugo_CV.pdf"
        }
        
        results = {}
        
        for name, file_path in problematic_files.items():
            print(f"\n📄 Test: {name}")
            print(f"   Chemin: {file_path}")
            
            try:
                path_obj = Path(file_path)
                if not path_obj.exists():
                    print(f"   ❌ Fichier non trouvé")
                    results[name] = {'status': 'not_found', 'error': 'Fichier non trouvé'}
                    continue
                
                print(f"   📏 Taille: {path_obj.stat().st_size} bytes")
                
                # Test parsing
                with open(path_obj, 'rb') as f:
                    response = requests.post(
                        "http://localhost:5051/api/parse-cv/",
                        files={'file': f},
                        data={'force_refresh': 'true'},
                        timeout=30
                    )
                
                if response.ok:
                    data = response.json()
                    text_length = len(data.get('raw_text', ''))
                    candidate_name = data.get('candidate_name', 'Non trouvé')
                    
                    exp = data.get('professional_experience', [])
                    missions_count = len(exp[0].get('missions', [])) if exp else 0
                    
                    skills_count = len(data.get('technical_skills', [])) + len(data.get('soft_skills', []))
                    
                    print(f"   ✅ Parsing réussi")
                    print(f"   📝 Texte: {text_length} caractères")
                    print(f"   👤 Nom: {candidate_name}")
                    print(f"   🎯 Missions: {missions_count}")
                    print(f"   🛠️ Compétences: {skills_count}")
                    
                    results[name] = {
                        'status': 'success',
                        'text_length': text_length,
                        'candidate_name': candidate_name,
                        'missions_count': missions_count,
                        'skills_count': skills_count,
                        'quality_score': self.evaluate_cv_quality(data),
                        'data': data
                    }
                    
                    # Diagnostics spécifiques
                    if text_length < 200:
                        print(f"   ⚠️ ALERTE: Peu de texte extrait")
                    if missions_count == 0:
                        print(f"   ⚠️ ALERTE: Aucune mission détectée")
                    
                else:
                    print(f"   ❌ Erreur parsing: {response.status_code}")
                    results[name] = {'status': 'parsing_error', 'code': response.status_code}
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
                results[name] = {'status': 'exception', 'error': str(e)}
        
        return results
    
    def test_sam_comparison(self) -> Dict:
        """Compare les deux CV de Sam pour comprendre la différence"""
        print(f"\n🔍 COMPARAISON CV SAM")
        print("-" * 30)
        
        sam_files = {
            'BATU Sam (Desktop)': "/Users/baptistecomas/Desktop/BATU Sam.pdf",
            'Sam Candidature (CV TEST)': "/Users/baptistecomas/Desktop/CV TEST/Bcom HR - Candidature de Sam.pdf"
        }
        
        comparison = {}
        
        for name, file_path in sam_files.items():
            try:
                with open(file_path, 'rb') as f:
                    response = requests.post(
                        "http://localhost:5051/api/parse-cv/",
                        files={'file': f},
                        data={'force_refresh': 'true'},
                        timeout=30
                    )
                
                if response.ok:
                    data = response.json()
                    comparison[name] = {
                        'text_length': len(data.get('raw_text', '')),
                        'candidate_name': data.get('candidate_name', 'Non trouvé'),
                        'experience_count': len(data.get('professional_experience', [])),
                        'missions_total': sum(len(exp.get('missions', [])) for exp in data.get('professional_experience', [])),
                        'skills_count': len(data.get('technical_skills', [])) + len(data.get('soft_skills', [])),
                        'position': data.get('professional_experience', [{}])[0].get('position', 'Aucune') if data.get('professional_experience') else 'Aucune'
                    }
            except Exception as e:
                comparison[name] = {'error': str(e)}
        
        # Affichage comparatif
        print("📊 COMPARAISON:")
        for name, data in comparison.items():
            if 'error' not in data:
                print(f"\n📄 {name}:")
                print(f"   📝 Texte: {data['text_length']} caractères")
                print(f"   👤 Nom: {data['candidate_name']}")
                print(f"   💼 Poste: {data['position']}")
                print(f"   🎯 Missions: {data['missions_total']}")
                print(f"   🛠️ Compétences: {data['skills_count']}")
        
        return comparison
    
    def test_hugo_salvat_matching(self) -> Dict:
        """Test spécifique du cas Hugo Salvat vs poste facturation"""
        print(f"\n🧪 TEST CAS HUGO SALVAT - VALIDATION SYSTÈME")
        print("-" * 50)
        
        # CV Hugo Salvat (commercial IT)
        hugo_cv_path = "/Users/baptistecomas/Desktop/CV TEST/SALVAT Hugo_CV.pdf"
        
        # Créer un job facturation pour test
        test_job_facturation = {
            'title': 'Assistant Facturation',
            'missions': [
                {'description': 'Facturation clients', 'category': 'facturation'},
                {'description': 'Contrôle des comptes', 'category': 'contrôle'}, 
                {'description': 'Saisie comptable', 'category': 'comptabilité'},
                {'description': 'Reporting financier', 'category': 'reporting'}
            ],
            'requirements': {
                'technical_skills': ['facturation', 'comptabilité', 'excel'],
                'soft_skills': ['rigueur', 'organisation'],
                'experience_level': '1-3 ans'
            }
        }
        
        try:
            # Parser le CV Hugo
            with open(hugo_cv_path, 'rb') as f:
                cv_response = requests.post(
                    "http://localhost:5051/api/parse-cv/",
                    files={'file': f},
                    data={'force_refresh': 'true'},
                    timeout=30
                )
            
            if not cv_response.ok:
                return {'error': f'Erreur parsing CV Hugo: {cv_response.status_code}'}
            
            hugo_cv_data = cv_response.json()
            
            # Test matching avec API Enhanced
            matching_response = requests.post(
                f"{self.base_url}/api/matching/enhanced",
                json={
                    'cv_data': hugo_cv_data,
                    'job_data': test_job_facturation
                },
                timeout=60
            )
            
            if not matching_response.ok:
                return {'error': f'Erreur matching: {matching_response.status_code}'}
            
            matching_result = matching_response.json()
            matching_analysis = matching_result.get('matching_analysis', {})
            
            score = matching_analysis.get('total_score', 0)
            alerts = matching_analysis.get('alerts', [])
            domain_analysis = matching_analysis.get('domain_analysis', {})
            
            print(f"📊 RÉSULTATS HUGO SALVAT vs ASSISTANT FACTURATION:")
            print(f"   🎯 Score final: {score}%")
            print(f"   📈 Domaine CV: {domain_analysis.get('cv_domain', 'unknown')}")
            print(f"   📈 Domaine Job: {domain_analysis.get('job_domain', 'unknown')}")
            print(f"   🔗 Compatibilité: {domain_analysis.get('compatibility_level', 'unknown')}")
            print(f"   🚨 Alertes: {len(alerts)}")
            
            for alert in alerts:
                print(f"      • {alert.get('message', '')}")
            
            # Validation
            validation = {
                'score_under_30': score < 30,
                'incompatibility_detected': domain_analysis.get('compatibility_level') == 'incompatible',
                'alerts_present': len(alerts) > 0,
                'system_working': score < 30 and len(alerts) > 0
            }
            
            print(f"\n✅ VALIDATION SYSTÈME:")
            print(f"   Score < 30%: {'✅' if validation['score_under_30'] else '❌'}")
            print(f"   Incompatibilité détectée: {'✅' if validation['incompatibility_detected'] else '❌'}")
            print(f"   Alertes présentes: {'✅' if validation['alerts_present'] else '❌'}")
            print(f"   Système fonctionne: {'✅' if validation['system_working'] else '❌'}")
            
            return {
                'score': score,
                'domain_analysis': domain_analysis,
                'alerts': alerts,
                'validation': validation,
                'matching_result': matching_analysis
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def evaluate_cv_quality(self, cv_data: Dict) -> float:
        """Évalue la qualité d'un CV parsé"""
        score = 0
        
        # Nom du candidat (20%)
        if cv_data.get('candidate_name'):
            score += 20
            
        # Expérience professionnelle (30%)
        exp = cv_data.get('professional_experience', [])
        if exp and len(exp) > 0:
            score += 15
            missions = exp[0].get('missions', [])
            if missions and len(missions) >= 3:
                score += 15
                
        # Compétences (25%)
        tech_skills = cv_data.get('technical_skills', [])
        soft_skills = cv_data.get('soft_skills', [])
        if tech_skills:
            score += 15
        if soft_skills:
            score += 10
            
        # Texte extrait (15%)
        raw_text = cv_data.get('raw_text', '')
        if len(raw_text) > 500:
            score += 15
        elif len(raw_text) > 200:
            score += 10
            
        # Formation (10%)
        if cv_data.get('education'):
            score += 10
            
        return min(score, 100)
    
    def run_batch_matching_tests(self, cv_folder: str, job_folder: str, max_combinations: int = 50) -> Dict:
        """Lance des tests de matching en lot avec analyse statistique"""
        cv_files = self.find_files_in_folder(cv_folder, self.supported_cv_formats)[:10]  # Limite pour tests
        job_files = self.find_files_in_folder(job_folder, self.supported_job_formats)[:5]   # Limite pour tests
        
        print(f"🚀 Tests de matching en lot: {len(cv_files)} CV × {len(job_files)} Jobs")
        
        if not cv_files:
            print(f"   ⚠️ Aucun CV trouvé dans {cv_folder}")
        
        if not job_files:
            print(f"   ⚠️ Aucun Job trouvé dans {job_folder}")
        
        if not cv_files or not job_files:
            return {
                'error': 'Aucun fichier trouvé pour les tests',
                'cv_count': len(cv_files),
                'job_count': len(job_files)
            }
        
        results = []
        combinations_tested = 0
        
        for job_file in job_files:
            for cv_file in cv_files:
                if combinations_tested >= max_combinations:
                    break
                    
                try:
                    start_time = time.time()
                    
                    # Test de matching
                    with open(cv_file, 'rb') as cv_f, open(job_file, 'rb') as job_f:
                        response = requests.post(
                            f"{self.base_url}/api/matching/files",
                            files={
                                'cv_file': cv_f,
                                'job_file': job_f
                            },
                            timeout=60
                        )
                    
                    processing_time = time.time() - start_time
                    
                    if response.ok:
                        match_result = response.json()
                        matching_analysis = match_result.get('matching_analysis', {})
                        
                        result = {
                            'cv_file': cv_file.name,
                            'cv_format': cv_file.suffix.lower(),
                            'job_file': job_file.name,
                            'job_format': job_file.suffix.lower(),
                            'score': matching_analysis.get('total_score', 0),
                            'recommendation': matching_analysis.get('recommendation', ''),
                            'processing_time': processing_time,
                            'alerts_count': len(matching_analysis.get('alerts', [])),
                            'domain_compatibility': matching_analysis.get('domain_analysis', {}).get('compatibility_level', 'unknown'),
                            'cv_domain': matching_analysis.get('domain_analysis', {}).get('cv_domain', 'unknown'),
                            'job_domain': matching_analysis.get('domain_analysis', {}).get('job_domain', 'unknown'),
                            'status': 'success'
                        }
                        
                        results.append(result)
                        
                    else:
                        results.append({
                            'cv_file': cv_file.name,
                            'cv_format': cv_file.suffix.lower(),
                            'job_file': job_file.name,
                            'job_format': job_file.suffix.lower(),
                            'status': 'error',
                            'error_code': response.status_code,
                            'processing_time': processing_time
                        })
                    
                    combinations_tested += 1
                    
                    if combinations_tested % 10 == 0:
                        print(f"   ✅ {combinations_tested} combinaisons testées...")
                        
                except Exception as e:
                    results.append({
                        'cv_file': cv_file.name,
                        'cv_format': cv_file.suffix.lower() if cv_file else 'unknown',
                        'job_file': job_file.name,
                        'job_format': job_file.suffix.lower() if job_file else 'unknown',
                        'status': 'exception',
                        'error': str(e)
                    })
                    combinations_tested += 1
        
        return self.analyze_batch_results(results)
    
    def analyze_batch_results(self, results: List[Dict]) -> Dict:
        """Analyse statistique des résultats de tests en lot"""
        successful_results = [r for r in results if r.get('status') == 'success']
        
        if not successful_results:
            return {
                'error': 'Aucun résultat valide pour analyse',
                'total_results': len(results),
                'failed_results': len(results)
            }
        
        scores = [r['score'] for r in successful_results]
        processing_times = [r['processing_time'] for r in successful_results]
        
        # Distribution des scores
        score_distribution = {
            'excellent (80-100%)': len([s for s in scores if s >= 80]),
            'bon (60-79%)': len([s for s in scores if 60 <= s < 80]),
            'moyen (40-59%)': len([s for s in scores if 40 <= s < 60]),
            'faible (20-39%)': len([s for s in scores if 20 <= s < 40]),
            'très_faible (0-19%)': len([s for s in scores if s < 20])
        }
        
        # Détection de faux positifs potentiels
        potential_false_positives = []
        for result in successful_results:
            if (result.get('domain_compatibility') == 'incompatible' and 
                result.get('score', 0) > 50):
                potential_false_positives.append({
                    'cv_file': result['cv_file'],
                    'job_file': result['job_file'],
                    'score': result['score'],
                    'cv_domain': result.get('cv_domain'),
                    'job_domain': result.get('job_domain'),
                    'alerts_count': result.get('alerts_count', 0)
                })
        
        return {
            'summary': {
                'total_tests': len(results),
                'successful_tests': len(successful_results),
                'success_rate': len(successful_results) / len(results) * 100 if results else 0,
                'average_score': statistics.mean(scores) if scores else 0,
                'median_score': statistics.median(scores) if scores else 0,
                'average_processing_time': statistics.mean(processing_times) if processing_times else 0,
            },
            'score_distribution': score_distribution,
            'potential_false_positives': potential_false_positives,
            'performance_metrics': {
                'tests_per_second': len(successful_results) / sum(processing_times) if sum(processing_times) > 0 else 0,
                'avg_response_time_ms': statistics.mean(processing_times) * 1000 if processing_times else 0
            },
            'detailed_results': successful_results
        }
    
    def generate_test_report(self, output_file: str = None) -> str:
        """Génère un rapport complet des tests"""
        if not output_file:
            output_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'system_version': 'SuperSmartMatch V2.1 Enhanced',
            'test_results': self.results,
            'statistics': self.stats,
            'recommendations': self.generate_optimization_recommendations()
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return output_file
    
    def generate_optimization_recommendations(self) -> List[str]:
        """Génère des recommandations d'optimisation basées sur les tests"""
        recommendations = []
        
        if self.stats:
            summary = self.stats.get('summary', {})
            avg_score = summary.get('average_score', 0)
            processing_time = self.stats.get('performance_metrics', {}).get('avg_response_time_ms', 0)
            false_positives = len(self.stats.get('potential_false_positives', []))
            
            if avg_score < 50:
                recommendations.append("📊 Score moyen faible: revoir les pondérations")
            
            if processing_time > 2000:
                recommendations.append("⚡ Temps de traitement élevé: optimiser les algorithmes")
            
            if false_positives > 0:
                recommendations.append(f"🚨 {false_positives} faux positifs détectés: affiner la matrice de compatibilité")
        
        return recommendations

def main():
    parser = argparse.ArgumentParser(description='Tests massifs SuperSmartMatch V2.1 - CORRIGÉ V2')
    parser.add_argument('--cv-folder', default='~/Desktop/CV TEST', help='Dossier des CV')
    parser.add_argument('--job-folder', default='~/Desktop/FDP TEST', help='Dossier des Jobs')
    parser.add_argument('--max-tests', type=int, default=50, help='Nombre max de combinaisons')
    parser.add_argument('--output', help='Fichier de sortie du rapport')
    parser.add_argument('--test-problematic', action='store_true', help='Test fichiers problématiques')
    parser.add_argument('--test-sam', action='store_true', help='Comparaison CV Sam')
    parser.add_argument('--test-hugo', action='store_true', help='Test Hugo Salvat validation')
    parser.add_argument('--run-batch', action='store_true', help='Tests en lot')
    
    args = parser.parse_args()
    
    test_suite = EnhancedTestSuite()
    
    print("🚀 SuperSmartMatch V2.1 - Suite de Tests CORRIGÉE V2")
    print("=" * 55)
    print("🔧 CORRECTIFS APPLIQUÉS:")
    print("   ✅ Gestion des espaces dans les noms de dossiers")
    print("   ✅ Utilisation du bon CV de Sam (Bcom HR)")
    print("   ✅ Tests spécifiques des fichiers problématiques")
    print("   ✅ Validation du cas Hugo Salvat")
    print("=" * 55)
    
    # Test fichiers problématiques
    if args.test_problematic or not any([args.test_sam, args.test_hugo, args.run_batch]):
        print("\n1️⃣ TEST FICHIERS PROBLÉMATIQUES")
        problematic_results = test_suite.test_problematic_files()
        test_suite.stats['problematic_files'] = problematic_results
    
    # Test comparaison Sam
    if args.test_sam or not any([args.test_problematic, args.test_hugo, args.run_batch]):
        sam_comparison = test_suite.test_sam_comparison()
        test_suite.stats['sam_comparison'] = sam_comparison
    
    # Test Hugo Salvat
    if args.test_hugo or not any([args.test_problematic, args.test_sam, args.run_batch]):
        hugo_results = test_suite.test_hugo_salvat_matching()
        test_suite.stats['hugo_validation'] = hugo_results
    
    # Tests en lot
    if args.run_batch:
        batch_results = test_suite.run_batch_matching_tests(args.cv_folder, args.job_folder, args.max_tests)
        test_suite.stats.update(batch_results)
    
    # Génération du rapport
    report_file = test_suite.generate_test_report(args.output)
    print(f"\n📋 Rapport généré: {report_file}")
    
    # Recommandations
    recommendations = test_suite.generate_optimization_recommendations()
    if recommendations:
        print("\n🎯 RECOMMANDATIONS:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    print(f"\n🎯 SuperSmartMatch V2.1 Enhanced - Tests terminés!")

if __name__ == '__main__':
    main()
