#!/usr/bin/env python3
"""
🧪 SuperSmartMatch V2.1 - Tests Massifs et Benchmarking (CORRIGÉ V3)
Script avancé pour tester et optimiser le système en lot
CORRECTIF MAJEUR: Utilise la méthode HTTP qui fonctionne (comme curl)
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
    
    def __init__(self, base_url="http://localhost:5055", cv_parser_url="http://localhost:5051"):
        self.base_url = base_url
        self.cv_parser_url = cv_parser_url
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
    
    def parse_cv_with_correct_method(self, file_path: Path) -> Dict:
        """Parse un CV avec la méthode HTTP qui fonctionne (comme curl)"""
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    f"{self.cv_parser_url}/api/parse-cv/",  # Port 5051 - méthode qui fonctionne
                    files={'file': f},
                    data={'force_refresh': 'true'},
                    timeout=30
                )
            
            if response.ok:
                try:
                    data = response.json()
                    
                    # Structure de réponse correcte : {status: ..., data: {...}}
                    status = data.get('status')
                    cv_data = data.get('data', {})
                    metadata = cv_data.get('_metadata', {})
                    
                    # Extraction des informations avec la bonne structure
                    personal_info = cv_data.get('personal_info', {})
                    experience = cv_data.get('professional_experience', [])
                    skills = cv_data.get('skills', [])
                    
                    # Calculer les métriques importantes
                    text_length = metadata.get('text_length', 0)
                    candidate_name = personal_info.get('name', 'Non trouvé')
                    missions_count = sum(len(exp.get('missions', [])) for exp in experience)
                    skills_count = len(skills)
                    
                    return {
                        'status': 'success',
                        'cv_data': cv_data,
                        'text_length': text_length,
                        'candidate_name': candidate_name,
                        'missions_count': missions_count,
                        'skills_count': skills_count,
                        'experience_count': len(experience),
                        'quality_score': self.evaluate_cv_quality(cv_data),
                        'parser_version': metadata.get('parser_version', 'unknown'),
                        'raw_response': data
                    }
                
                except Exception as e:
                    return {
                        'status': 'json_error',
                        'error': str(e),
                        'raw_text': response.text[:200]
                    }
            else:
                return {
                    'status': 'http_error',
                    'error_code': response.status_code,
                    'error_text': response.text[:200]
                }
                
        except Exception as e:
            return {
                'status': 'exception',
                'error': str(e)
            }
    
    def test_problematic_files(self) -> Dict:
        """Test des fichiers spécifiquement problématiques identifiés - MÉTHODE CORRIGÉE"""
        print(f"\n🔍 TEST FICHIERS PROBLÉMATIQUES - MÉTHODE HTTP CORRIGÉE")
        print("-" * 60)
        
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
            
            path_obj = Path(file_path)
            if not path_obj.exists():
                print(f"   ❌ Fichier non trouvé")
                results[name] = {'status': 'not_found', 'error': 'Fichier non trouvé'}
                continue
            
            print(f"   📏 Taille: {path_obj.stat().st_size} bytes")
            
            # Utiliser la méthode corrigée
            result = self.parse_cv_with_correct_method(path_obj)
            
            if result['status'] == 'success':
                print(f"   ✅ Parsing réussi")
                print(f"   📝 Texte: {result['text_length']} caractères")
                print(f"   👤 Nom: {result['candidate_name']}")
                print(f"   🎯 Missions: {result['missions_count']}")
                print(f"   🛠️ Compétences: {result['skills_count']}")
                print(f"   🔧 Parser: {result['parser_version']}")
                
                # Diagnostics spécifiques
                if result['text_length'] < 200:
                    print(f"   ⚠️ ALERTE: Peu de texte extrait")
                if result['missions_count'] == 0:
                    print(f"   ⚠️ ALERTE: Aucune mission détectée")
                    
            else:
                print(f"   ❌ Erreur: {result.get('error', 'Inconnue')}")
            
            results[name] = result
        
        return results
    
    def test_sam_comparison(self) -> Dict:
        """Compare les deux CV de Sam pour comprendre la différence - MÉTHODE CORRIGÉE"""
        print(f"\n🔍 COMPARAISON CV SAM - MÉTHODE HTTP CORRIGÉE")
        print("-" * 50)
        
        sam_files = {
            'BATU Sam (Desktop)': "/Users/baptistecomas/Desktop/BATU Sam.pdf",
            'Sam Candidature (CV TEST)': "/Users/baptistecomas/Desktop/CV TEST/Bcom HR - Candidature de Sam.pdf"
        }
        
        comparison = {}
        
        for name, file_path in sam_files.items():
            path_obj = Path(file_path)
            if path_obj.exists():
                result = self.parse_cv_with_correct_method(path_obj)
                
                if result['status'] == 'success':
                    comparison[name] = {
                        'text_length': result['text_length'],
                        'candidate_name': result['candidate_name'],
                        'experience_count': result['experience_count'],
                        'missions_total': result['missions_count'],
                        'skills_count': result['skills_count'],
                        'quality_score': result['quality_score'],
                        'parser_version': result['parser_version']
                    }
                else:
                    comparison[name] = {'error': result.get('error', 'Erreur parsing')}
        
        # Affichage comparatif
        print("📊 COMPARAISON:")
        for name, data in comparison.items():
            if 'error' not in data:
                print(f"\n📄 {name}:")
                print(f"   📝 Texte: {data['text_length']} caractères")
                print(f"   👤 Nom: {data['candidate_name']}")
                print(f"   💼 Expériences: {data['experience_count']}")
                print(f"   🎯 Missions: {data['missions_total']}")
                print(f"   🛠️ Compétences: {data['skills_count']}")
                print(f"   📊 Qualité: {data['quality_score']}%")
                print(f"   🔧 Parser: {data['parser_version']}")
            else:
                print(f"\n📄 {name}: ❌ {data['error']}")
        
        return comparison
    
    def test_hugo_salvat_matching(self) -> Dict:
        """Test spécifique du cas Hugo Salvat vs poste facturation - MÉTHODE CORRIGÉE"""
        print(f"\n🧪 TEST CAS HUGO SALVAT - VALIDATION SYSTÈME COMPLET")
        print("-" * 60)
        
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
            path_obj = Path(hugo_cv_path)
            if not path_obj.exists():
                return {'error': 'CV Hugo Salvat non trouvé'}
            
            # Parser le CV Hugo avec la méthode corrigée
            cv_result = self.parse_cv_with_correct_method(path_obj)
            
            if cv_result['status'] != 'success':
                return {'error': f'Erreur parsing CV Hugo: {cv_result.get("error")}'}
            
            hugo_cv_data = cv_result['cv_data']
            
            print(f"✅ CV Hugo parsé avec succès:")
            print(f"   📝 Texte: {cv_result['text_length']} caractères")
            print(f"   👤 Nom: {cv_result['candidate_name']}")
            print(f"   🎯 Missions: {cv_result['missions_count']}")
            
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
            
            print(f"\n📊 RÉSULTATS HUGO SALVAT vs ASSISTANT FACTURATION:")
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
                'matching_result': matching_analysis,
                'cv_parsing_result': cv_result
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def evaluate_cv_quality(self, cv_data: Dict) -> float:
        """Évalue la qualité d'un CV parsé avec la structure correcte"""
        score = 0
        
        # Nom du candidat (20%)
        personal_info = cv_data.get('personal_info', {})
        if personal_info.get('name'):
            score += 20
            
        # Expérience professionnelle (30%)
        exp = cv_data.get('professional_experience', [])
        if exp and len(exp) > 0:
            score += 15
            # Compter toutes les missions
            total_missions = sum(len(e.get('missions', [])) for e in exp)
            if total_missions >= 3:
                score += 15
                
        # Compétences (25%)
        skills = cv_data.get('skills', [])
        if skills and len(skills) >= 3:
            score += 15
        if len(skills) >= 7:
            score += 10
            
        # Texte extrait (15%)
        metadata = cv_data.get('_metadata', {})
        text_length = metadata.get('text_length', 0)
        if text_length > 500:
            score += 15
        elif text_length > 200:
            score += 10
            
        # Formation (10%)
        education = cv_data.get('education', [])
        if education:
            score += 10
            
        return min(score, 100)
    
    def run_batch_cv_parsing_tests(self, cv_folder: str, max_files: int = 20) -> Dict:
        """Lance des tests de parsing en lot avec la méthode HTTP corrigée"""
        cv_files = self.find_files_in_folder(cv_folder, self.supported_cv_formats)[:max_files]
        
        print(f"\n🚀 Tests de parsing CV en lot - MÉTHODE HTTP CORRIGÉE")
        print(f"📁 Dossier: {cv_folder}")
        print(f"📄 Fichiers à tester: {len(cv_files)}")
        
        if not cv_files:
            return {
                'error': 'Aucun CV trouvé',
                'cv_count': 0
            }
        
        results = []
        successful_parses = 0
        
        for i, cv_file in enumerate(cv_files, 1):
            print(f"\n📄 [{i}/{len(cv_files)}] Test: {cv_file.name}")
            
            start_time = time.time()
            
            # Utiliser la méthode HTTP corrigée
            parse_result = self.parse_cv_with_correct_method(cv_file)
            
            processing_time = time.time() - start_time
            
            if parse_result['status'] == 'success':
                successful_parses += 1
                print(f"   ✅ Réussi - {parse_result['text_length']} chars, {parse_result['missions_count']} missions")
                
                result = {
                    'cv_file': cv_file.name,
                    'cv_format': cv_file.suffix.lower(),
                    'status': 'success',
                    'text_length': parse_result['text_length'],
                    'candidate_name': parse_result['candidate_name'],
                    'missions_count': parse_result['missions_count'],
                    'skills_count': parse_result['skills_count'],
                    'quality_score': parse_result['quality_score'],
                    'processing_time': processing_time
                }
            else:
                print(f"   ❌ Échec - {parse_result.get('error', 'Erreur inconnue')}")
                
                result = {
                    'cv_file': cv_file.name,
                    'cv_format': cv_file.suffix.lower(),
                    'status': 'error',
                    'error': parse_result.get('error', 'Erreur inconnue'),
                    'processing_time': processing_time
                }
            
            results.append(result)
        
        return self.analyze_parsing_results(results, successful_parses)
    
    def run_batch_matching_tests(self, cv_folder: str, job_folder: str, max_combinations: int = 50) -> Dict:
        """Lance des tests de matching en lot avec parsing CV corrigé"""
        cv_files = self.find_files_in_folder(cv_folder, self.supported_cv_formats)[:10]
        job_files = self.find_files_in_folder(job_folder, self.supported_job_formats)[:5]
        
        print(f"\n🚀 Tests de matching en lot avec parsing corrigé")
        print(f"📄 {len(cv_files)} CV × {len(job_files)} Jobs")
        
        if not cv_files or not job_files:
            return {
                'error': 'Fichiers manquants',
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
                    
                    # Parser le CV avec la méthode corrigée
                    cv_result = self.parse_cv_with_correct_method(cv_file)
                    
                    if cv_result['status'] != 'success':
                        results.append({
                            'cv_file': cv_file.name,
                            'job_file': job_file.name,
                            'status': 'cv_parsing_error',
                            'error': cv_result.get('error', 'Erreur parsing CV')
                        })
                        combinations_tested += 1
                        continue
                    
                    # Parser le job (ici on pourrait aussi utiliser une méthode similaire)
                    with open(job_file, 'rb') as job_f:
                        job_response = requests.post(
                            f"{self.base_url}/api/parse-job/",
                            files={'file': job_f},
                            timeout=30
                        )
                    
                    if not job_response.ok:
                        results.append({
                            'cv_file': cv_file.name,
                            'job_file': job_file.name,
                            'status': 'job_parsing_error',
                            'error': f'Code {job_response.status_code}'
                        })
                        combinations_tested += 1
                        continue
                    
                    job_data = job_response.json()
                    
                    # Test matching avec les données parsées
                    matching_response = requests.post(
                        f"{self.base_url}/api/matching/enhanced",
                        json={
                            'cv_data': cv_result['cv_data'],
                            'job_data': job_data
                        },
                        timeout=60
                    )
                    
                    processing_time = time.time() - start_time
                    
                    if matching_response.ok:
                        match_result = matching_response.json()
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
                            'cv_text_length': cv_result['text_length'],
                            'cv_missions_count': cv_result['missions_count'],
                            'status': 'success'
                        }
                        
                        results.append(result)
                        
                    else:
                        results.append({
                            'cv_file': cv_file.name,
                            'job_file': job_file.name,
                            'status': 'matching_error',
                            'error_code': matching_response.status_code,
                            'processing_time': processing_time
                        })
                    
                    combinations_tested += 1
                    
                    if combinations_tested % 5 == 0:
                        print(f"   ✅ {combinations_tested} combinaisons testées...")
                        
                except Exception as e:
                    results.append({
                        'cv_file': cv_file.name if cv_file else 'unknown',
                        'job_file': job_file.name if job_file else 'unknown',
                        'status': 'exception',
                        'error': str(e)
                    })
                    combinations_tested += 1
        
        return self.analyze_batch_results(results)
    
    def analyze_parsing_results(self, results: List[Dict], successful_count: int) -> Dict:
        """Analyse des résultats de parsing CV"""
        total_tests = len(results)
        success_rate = (successful_count / total_tests * 100) if total_tests > 0 else 0
        
        successful_results = [r for r in results if r.get('status') == 'success']
        
        # Statistiques sur les CV parsés avec succès
        if successful_results:
            text_lengths = [r['text_length'] for r in successful_results]
            missions_counts = [r['missions_count'] for r in successful_results]
            quality_scores = [r['quality_score'] for r in successful_results]
            processing_times = [r['processing_time'] for r in successful_results]
            
            # Distribution par formats
            format_stats = {}
            for result in successful_results:
                fmt = result['cv_format']
                if fmt not in format_stats:
                    format_stats[fmt] = {'count': 0, 'avg_quality': 0, 'avg_text_length': 0}
                format_stats[fmt]['count'] += 1
            
            # Calculer moyennes par format
            for fmt in format_stats:
                fmt_results = [r for r in successful_results if r['cv_format'] == fmt]
                format_stats[fmt]['avg_quality'] = statistics.mean([r['quality_score'] for r in fmt_results])
                format_stats[fmt]['avg_text_length'] = statistics.mean([r['text_length'] for r in fmt_results])
        
        return {
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_count,
                'success_rate': success_rate,
                'average_text_length': statistics.mean(text_lengths) if successful_results else 0,
                'average_missions': statistics.mean(missions_counts) if successful_results else 0,
                'average_quality_score': statistics.mean(quality_scores) if successful_results else 0,
                'average_processing_time': statistics.mean(processing_times) if successful_results else 0,
            },
            'format_statistics': format_stats if successful_results else {},
            'performance_metrics': {
                'files_per_second': successful_count / sum(processing_times) if successful_results and sum(processing_times) > 0 else 0,
                'avg_response_time_ms': statistics.mean(processing_times) * 1000 if successful_results else 0
            },
            'detailed_results': results
        }
    
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
            'parsing_method': 'HTTP Corrigée (comme curl)',
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
            success_rate = summary.get('success_rate', 0)
            
            if success_rate < 90:
                recommendations.append(f"📊 Taux de succès parsing ({success_rate:.1f}%): améliorer la robustesse")
            
            if avg_score < 50:
                recommendations.append("📊 Score moyen faible: revoir les pondérations")
            
            if processing_time > 2000:
                recommendations.append("⚡ Temps de traitement élevé: optimiser les algorithmes")
            
            if false_positives > 0:
                recommendations.append(f"🚨 {false_positives} faux positifs détectés: affiner la matrice de compatibilité")
        
        return recommendations

def main():
    parser = argparse.ArgumentParser(description='Tests massifs SuperSmartMatch V2.1 - CORRIGÉ V3 MÉTHODE HTTP')
    parser.add_argument('--cv-folder', default='~/Desktop/CV TEST', help='Dossier des CV')
    parser.add_argument('--job-folder', default='~/Desktop/FDP TEST', help='Dossier des Jobs')
    parser.add_argument('--max-tests', type=int, default=50, help='Nombre max de combinaisons')
    parser.add_argument('--output', help='Fichier de sortie du rapport')
    parser.add_argument('--test-problematic', action='store_true', help='Test fichiers problématiques')
    parser.add_argument('--test-sam', action='store_true', help='Comparaison CV Sam')
    parser.add_argument('--test-hugo', action='store_true', help='Test Hugo Salvat validation')
    parser.add_argument('--run-parsing', action='store_true', help='Tests parsing CV en lot')
    parser.add_argument('--run-batch', action='store_true', help='Tests matching en lot')
    
    args = parser.parse_args()
    
    test_suite = EnhancedTestSuite()
    
    print("🚀 SuperSmartMatch V2.1 - Suite de Tests CORRIGÉE V3")
    print("=" * 65)
    print("🔧 CORRECTIFS APPLIQUÉS:")
    print("   ✅ Gestion des espaces dans les noms de dossiers")
    print("   ✅ Méthode HTTP corrigée (port 5051, structure réponse)")
    print("   ✅ Parsing CV avec structure JSON correcte")
    print("   ✅ Tests spécifiques des fichiers problématiques")
    print("   ✅ Validation du cas Hugo Salvat")
    print("=" * 65)
    
    # Test fichiers problématiques
    if args.test_problematic or not any([args.test_sam, args.test_hugo, args.run_parsing, args.run_batch]):
        print("\n1️⃣ TEST FICHIERS PROBLÉMATIQUES")
        problematic_results = test_suite.test_problematic_files()
        test_suite.stats['problematic_files'] = problematic_results
    
    # Test comparaison Sam
    if args.test_sam or not any([args.test_problematic, args.test_hugo, args.run_parsing, args.run_batch]):
        sam_comparison = test_suite.test_sam_comparison()
        test_suite.stats['sam_comparison'] = sam_comparison
    
    # Test Hugo Salvat
    if args.test_hugo or not any([args.test_problematic, args.test_sam, args.run_parsing, args.run_batch]):
        hugo_results = test_suite.test_hugo_salvat_matching()
        test_suite.stats['hugo_validation'] = hugo_results
    
    # Tests parsing CV en lot
    if args.run_parsing:
        print("\n2️⃣ TESTS PARSING CV EN LOT")
        parsing_results = test_suite.run_batch_cv_parsing_tests(args.cv_folder, 20)
        test_suite.stats['parsing_batch'] = parsing_results
    
    # Tests matching en lot
    if args.run_batch:
        print("\n3️⃣ TESTS MATCHING EN LOT")
        batch_results = test_suite.run_batch_matching_tests(args.cv_folder, args.job_folder, args.max_tests)
        test_suite.stats['matching_batch'] = batch_results
    
    # Génération du rapport
    report_file = test_suite.generate_test_report(args.output)
    print(f"\n📋 Rapport généré: {report_file}")
    
    # Recommandations
    recommendations = test_suite.generate_optimization_recommendations()
    if recommendations:
        print("\n🎯 RECOMMANDATIONS:")
        for rec in recommendations:
            print(f"   • {rec}")
    
    print(f"\n🎯 SuperSmartMatch V2.1 Enhanced - Tests terminés avec méthode HTTP corrigée!")

if __name__ == '__main__':
    main()
