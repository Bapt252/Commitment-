#!/usr/bin/env python3
"""
🧪 SuperSmartMatch V2.1 - Tests Massifs et Benchmarking
Script avancé pour tester et optimiser le système en lot
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
        
    def test_cv_parsing_quality(self, cv_folder: str) -> Dict:
        """Évalue la qualité du parsing des CV"""
        cv_files = list(Path(cv_folder).expanduser().glob("*.pdf"))
        parsing_results = []
        
        print(f"🔍 Test qualité parsing sur {len(cv_files)} CV...")
        
        for cv_file in cv_files:
            try:
                with open(cv_file, 'rb') as f:
                    response = requests.post(
                        "http://localhost:5051/api/parse-cv/",
                        files={'file': f},
                        data={'force_refresh': 'true'},
                        timeout=30
                    )
                
                if response.ok:
                    cv_data = response.json()
                    quality_score = self.evaluate_cv_quality(cv_data)
                    parsing_results.append({
                        'file': cv_file.name,
                        'quality_score': quality_score,
                        'text_length': len(cv_data.get('raw_text', '')),
                        'missions_count': len(cv_data.get('professional_experience', [{}])[0].get('missions', [])),
                        'skills_count': len(cv_data.get('technical_skills', []) + cv_data.get('soft_skills', [])),
                        'status': 'success'
                    })
                else:
                    parsing_results.append({
                        'file': cv_file.name,
                        'status': 'error',
                        'error_code': response.status_code
                    })
                    
            except Exception as e:
                parsing_results.append({
                    'file': cv_file.name,
                    'status': 'exception',
                    'error': str(e)
                })
        
        return {
            'total_files': len(cv_files),
            'successful_parses': len([r for r in parsing_results if r.get('status') == 'success']),
            'average_quality': statistics.mean([r.get('quality_score', 0) for r in parsing_results if r.get('quality_score')]) if parsing_results else 0,
            'detailed_results': parsing_results
        }
    
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
        cv_files = list(Path(cv_folder).expanduser().glob("*.pdf"))[:10]  # Limite pour tests
        job_files = list(Path(job_folder).expanduser().glob("*.pdf"))[:5]   # Limite pour tests
        
        print(f"🚀 Tests de matching en lot: {len(cv_files)} CV × {len(job_files)} Jobs")
        
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
                            'job_file': job_file.name,
                            'score': matching_analysis.get('total_score', 0),
                            'recommendation': matching_analysis.get('recommendation', ''),
                            'processing_time': processing_time,
                            'alerts_count': len(matching_analysis.get('alerts', [])),
                            'domain_compatibility': matching_analysis.get('domain_analysis', {}).get('compatibility_level', 'unknown'),
                            'cv_domain': matching_analysis.get('domain_analysis', {}).get('cv_domain', 'unknown'),
                            'job_domain': matching_analysis.get('domain_analysis', {}).get('job_domain', 'unknown'),
                            'status': 'success'
                        }
                        
                        # Analyse des composants du score
                        breakdown = matching_analysis.get('detailed_breakdown', {})
                        for component in ['domain_compatibility', 'missions', 'skills', 'experience', 'quality']:
                            if component in breakdown:
                                result[f'{component}_score'] = breakdown[component].get('raw_score', 0)
                        
                        results.append(result)
                        
                    else:
                        results.append({
                            'cv_file': cv_file.name,
                            'job_file': job_file.name,
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
                        'job_file': job_file.name,
                        'status': 'exception',
                        'error': str(e)
                    })
                    combinations_tested += 1
        
        return self.analyze_batch_results(results)
    
    def analyze_batch_results(self, results: List[Dict]) -> Dict:
        """Analyse statistique des résultats de tests en lot"""
        successful_results = [r for r in results if r.get('status') == 'success']
        
        if not successful_results:
            return {'error': 'Aucun résultat valide pour analyse'}
        
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
        
        # Analyse des domaines
        domain_analysis = {}
        for result in successful_results:
            cv_domain = result.get('cv_domain', 'unknown')
            job_domain = result.get('job_domain', 'unknown')
            compatibility = result.get('domain_compatibility', 'unknown')
            
            key = f"{cv_domain}_vs_{job_domain}"
            if key not in domain_analysis:
                domain_analysis[key] = {
                    'count': 0,
                    'avg_score': 0,
                    'compatibility_level': compatibility,
                    'scores': []
                }
            
            domain_analysis[key]['count'] += 1
            domain_analysis[key]['scores'].append(result['score'])
            domain_analysis[key]['avg_score'] = statistics.mean(domain_analysis[key]['scores'])
        
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
                'success_rate': len(successful_results) / len(results) * 100,
                'average_score': statistics.mean(scores),
                'median_score': statistics.median(scores),
                'score_std_dev': statistics.stdev(scores) if len(scores) > 1 else 0,
                'average_processing_time': statistics.mean(processing_times),
                'max_processing_time': max(processing_times),
                'min_processing_time': min(processing_times)
            },
            'score_distribution': score_distribution,
            'domain_analysis': domain_analysis,
            'potential_false_positives': potential_false_positives,
            'performance_metrics': {
                'tests_per_second': len(successful_results) / sum(processing_times) if sum(processing_times) > 0 else 0,
                'avg_response_time_ms': statistics.mean(processing_times) * 1000
            },
            'detailed_results': successful_results
        }
    
    def test_problematic_file(self, file_path: str) -> Dict:
        """Test spécifique pour un fichier problématique comme BATU Sam.pdf"""
        try:
            file_path = Path(file_path).expanduser()
            
            # Test parsing CV
            with open(file_path, 'rb') as f:
                cv_response = requests.post(
                    "http://localhost:5051/api/parse-cv/",
                    files={'file': f},
                    data={'force_refresh': 'true'},
                    timeout=30
                )
            
            if not cv_response.ok:
                return {
                    'file': file_path.name,
                    'status': 'parsing_error',
                    'error_code': cv_response.status_code
                }
            
            cv_data = cv_response.json()
            
            # Analyse détaillée
            analysis = {
                'file': file_path.name,
                'status': 'success',
                'text_extraction': {
                    'raw_text_length': len(cv_data.get('raw_text', '')),
                    'raw_text_preview': cv_data.get('raw_text', '')[:200] + '...' if cv_data.get('raw_text') else '',
                    'quality_score': self.evaluate_cv_quality(cv_data)
                },
                'content_analysis': {
                    'candidate_name': cv_data.get('candidate_name', 'Non trouvé'),
                    'professional_experience_count': len(cv_data.get('professional_experience', [])),
                    'missions_count': len(cv_data.get('professional_experience', [{}])[0].get('missions', [])) if cv_data.get('professional_experience') else 0,
                    'technical_skills_count': len(cv_data.get('technical_skills', [])),
                    'soft_skills_count': len(cv_data.get('soft_skills', []))
                },
                'potential_issues': []
            }
            
            # Détection des problèmes
            if analysis['text_extraction']['raw_text_length'] < 200:
                analysis['potential_issues'].append({
                    'type': 'low_text_extraction',
                    'description': f"Très peu de texte extrait ({analysis['text_extraction']['raw_text_length']} caractères)",
                    'recommendation': "Vérifier le format PDF ou les permissions de lecture"
                })
            
            if analysis['content_analysis']['missions_count'] == 0:
                analysis['potential_issues'].append({
                    'type': 'no_missions_found',
                    'description': "Aucune mission détectée",
                    'recommendation': "Vérifier le parsing des expériences professionnelles"
                })
            
            return analysis
            
        except Exception as e:
            return {
                'file': Path(file_path).name,
                'status': 'exception',
                'error': str(e)
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
            
            domain_issues = []
            for domain_pair, data in self.stats.get('domain_analysis', {}).items():
                if data.get('compatibility_level') == 'incompatible' and data.get('avg_score', 0) > 50:
                    domain_issues.append(domain_pair)
            
            if domain_issues:
                recommendations.append(f"🔧 Problèmes de domaines: {', '.join(domain_issues[:3])}")
        
        return recommendations

def main():
    parser = argparse.ArgumentParser(description='Tests massifs SuperSmartMatch V2.1')
    parser.add_argument('--cv-folder', default='~/Desktop/CV TEST/', help='Dossier des CV')
    parser.add_argument('--job-folder', default='~/Desktop/FDP TEST/', help='Dossier des Jobs')
    parser.add_argument('--max-tests', type=int, default=50, help='Nombre max de combinaisons')
    parser.add_argument('--output', help='Fichier de sortie du rapport')
    parser.add_argument('--parsing-quality', action='store_true', help='Test qualité parsing')
    parser.add_argument('--test-file', help='Test un fichier spécifique (ex: ~/Desktop/BATU Sam.pdf)')
    
    args = parser.parse_args()
    
    test_suite = EnhancedTestSuite()
    
    print("🚀 SuperSmartMatch V2.1 - Suite de Tests Avancés")
    print("="*60)
    
    # Test d'un fichier spécifique
    if args.test_file:
        print(f"\n🔍 Test du fichier spécifique: {args.test_file}")
        file_analysis = test_suite.test_problematic_file(args.test_file)
        print(f"   📄 Fichier: {file_analysis['file']}")
        print(f"   📊 Statut: {file_analysis['status']}")
        
        if file_analysis['status'] == 'success':
            text_info = file_analysis['text_extraction']
            print(f"   📝 Texte extrait: {text_info['raw_text_length']} caractères")
            print(f"   🏆 Score qualité: {text_info['quality_score']:.1f}%")
            
            if file_analysis['potential_issues']:
                print("   ⚠️  Problèmes détectés:")
                for issue in file_analysis['potential_issues']:
                    print(f"      • {issue['description']}")
                    print(f"        → {issue['recommendation']}")
        else:
            print(f"   ❌ Erreur: {file_analysis.get('error', 'Erreur inconnue')}")
        
        print("\n" + "="*60)
    
    # Test qualité parsing
    if args.parsing_quality:
        print("\n1️⃣ Test de la qualité du parsing...")
        parsing_results = test_suite.test_cv_parsing_quality(args.cv_folder)
        test_suite.stats['parsing_quality'] = parsing_results
        print(f"   ✅ {parsing_results['successful_parses']}/{parsing_results['total_files']} CV parsés")
        print(f"   📊 Qualité moyenne: {parsing_results['average_quality']:.1f}%")
        
        # Affichage des CV problématiques
        problematic_cvs = [r for r in parsing_results['detailed_results'] 
                          if r.get('status') == 'success' and r.get('text_length', 0) < 200]
        
        if problematic_cvs:
            print(f"   ⚠️  {len(problematic_cvs)} CV avec extraction faible:")
            for cv in problematic_cvs[:5]:  # Afficher les 5 premiers
                print(f"      • {cv['file']}: {cv['text_length']} caractères")
    
    # Tests de matching en lot
    print("\n2️⃣ Tests de matching en lot...")
    batch_results = test_suite.run_batch_matching_tests(args.cv_folder, args.job_folder, args.max_tests)
    test_suite.stats.update(batch_results)
    
    # Affichage des résultats
    print("\n📊 RÉSULTATS FINAUX:")
    summary = batch_results.get('summary', {})
    print(f"   • Tests réussis: {summary.get('successful_tests', 0)}/{summary.get('total_tests', 0)}")
    print(f"   • Score moyen: {summary.get('average_score', 0):.1f}%")
    print(f"   • Temps moyen: {summary.get('average_processing_time', 0)*1000:.0f}ms")
    print(f"   • Faux positifs potentiels: {len(batch_results.get('potential_false_positives', []))}")
    
    # Distribution des scores
    print("\n📈 DISTRIBUTION DES SCORES:")
    for range_name, count in batch_results.get('score_distribution', {}).items():
        print(f"   • {range_name}: {count} tests")
    
    # Analyse des domaines problématiques
    domain_analysis = batch_results.get('domain_analysis', {})
    problematic_domains = {k: v for k, v in domain_analysis.items() 
                          if v.get('compatibility_level') == 'incompatible' and v.get('avg_score', 0) > 50}
    
    if problematic_domains:
        print("\n⚠️  DOMAINES PROBLÉMATIQUES:")
        for domain_pair, data in problematic_domains.items():
            print(f"   • {domain_pair}: score moyen {data['avg_score']:.1f}% (incompatible!)")
    
    # Faux positifs détectés
    false_positives = batch_results.get('potential_false_positives', [])
    if false_positives:
        print(f"\n🚨 FAUX POSITIFS DÉTECTÉS ({len(false_positives)}):")
        for fp in false_positives[:3]:  # Afficher les 3 premiers
            print(f"   • {fp['cv_file']} → {fp['job_file']}: {fp['score']}% ({fp['cv_domain']} vs {fp['job_domain']})")
    
    # Génération du rapport
    report_file = test_suite.generate_test_report(args.output)
    print(f"\n📋 Rapport généré: {report_file}")
    
    # Recommandations
    recommendations = test_suite.generate_optimization_recommendations()
    if recommendations:
        print("\n🎯 RECOMMANDATIONS:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    # Validation globale
    print("\n✅ VALIDATION SYSTÈME:")
    success_rate = summary.get('success_rate', 0)
    avg_score = summary.get('average_score', 0)
    fp_count = len(false_positives)
    
    if success_rate >= 95:
        print("   🟢 Taux de succès: EXCELLENT")
    elif success_rate >= 90:
        print("   🟡 Taux de succès: BON")
    else:
        print("   🔴 Taux de succès: À AMÉLIORER")
    
    if fp_count == 0:
        print("   🟢 Faux positifs: AUCUN ✅")
    elif fp_count <= 2:
        print("   🟡 Faux positifs: ACCEPTABLE")
    else:
        print("   🔴 Faux positifs: TROP NOMBREUX")
    
    print(f"\n🎯 SuperSmartMatch V2.1 Enhanced - Tests terminés!")

if __name__ == '__main__':
    main()
