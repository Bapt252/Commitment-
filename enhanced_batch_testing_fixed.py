#!/usr/bin/env python3
"""
🧪 SuperSmartMatch V2.1 - Tests Massifs et Benchmarking (VERSION CORRIGÉE)
Script avancé pour tester et optimiser le système en lot
Supports: PDF, DOC, DOCX, PNG, JPG, JPEG

CORRECTIONS V2.1.1:
✅ Gestion correcte des espaces dans les noms de dossiers
✅ Amélioration de la robustesse du parsing des chemins
✅ Meilleure gestion des erreurs de fichiers
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
import urllib.parse

class EnhancedTestSuite:
    
    def __init__(self, base_url="http://localhost:5055"):
        self.base_url = base_url
        self.results = []
        self.stats = {}
        self.lock = Lock()
        
        # Formats de fichiers supportés
        self.supported_cv_formats = {'.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg'}
        self.supported_job_formats = {'.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg'}
        
    def normalize_path(self, folder_path: str) -> Path:
        """Normalise un chemin en gérant correctement les espaces et la tilde"""
        # Étape 1: Expansion de la tilde (~)
        expanded_path = os.path.expanduser(folder_path)
        
        # Étape 2: Résolution du chemin absolu
        absolute_path = os.path.abspath(expanded_path)
        
        # Étape 3: Conversion en objet Path pour une manipulation robuste
        path_obj = Path(absolute_path)
        
        print(f"📁 Normalisation chemin:")
        print(f"   Input: {folder_path}")
        print(f"   Expanded: {expanded_path}")
        print(f"   Absolute: {absolute_path}")
        print(f"   Final Path: {path_obj}")
        print(f"   Exists: {path_obj.exists()}")
        
        return path_obj
        
    def find_files_in_folder(self, folder_path: str, file_types: set) -> List[Path]:
        """Trouve tous les fichiers supportés dans un dossier (version corrigée)"""
        try:
            folder = self.normalize_path(folder_path)
            found_files = []
            
            if not folder.exists():
                print(f"⚠️  Dossier non trouvé: {folder}")
                # Tentative de diagnostic
                print(f"📊 Diagnostic:")
                print(f"   - Dossier parent: {folder.parent}")
                print(f"   - Parent existe: {folder.parent.exists()}")
                if folder.parent.exists():
                    print(f"   - Contenu parent: {list(folder.parent.iterdir())}")
                return []
            
            print(f"✅ Dossier trouvé: {folder}")
            
            # Méthode robuste pour trouver les fichiers
            for file_type in file_types:
                try:
                    # Utilise rglob pour être plus permissif
                    files = list(folder.rglob(f"*{file_type}"))
                    found_files.extend(files)
                    print(f"   📄 {file_type}: {len(files)} fichiers")
                except Exception as e:
                    print(f"   ❌ Erreur pour {file_type}: {e}")
            
            # Éliminer les doublons et trier
            found_files = sorted(list(set(found_files)))
            print(f"📊 Total: {len(found_files)} fichiers trouvés")
            
            return found_files
            
        except Exception as e:
            print(f"❌ Erreur dans find_files_in_folder: {e}")
            return []
    
    def analyze_folder_content(self, folder_path: str) -> Dict:
        """Analyse le contenu d'un dossier (version corrigée)"""
        try:
            folder = self.normalize_path(folder_path)
            
            if not folder.exists():
                return {
                    'exists': False,
                    'path': str(folder),
                    'error': f'Dossier non trouvé: {folder}',
                    'parent_exists': folder.parent.exists(),
                    'parent_content': list(folder.parent.iterdir()) if folder.parent.exists() else []
                }
            
            files_by_type = {}
            total_files = 0
            
            for item in folder.iterdir():
                if item.is_file():
                    ext = item.suffix.lower()
                    if ext not in files_by_type:
                        files_by_type[ext] = []
                    files_by_type[ext].append(item.name)
                    total_files += 1
            
            supported_files = []
            all_supported = self.supported_cv_formats.union(self.supported_job_formats)
            
            for ext in all_supported:
                if ext in files_by_type:
                    supported_files.extend([f for f in files_by_type[ext]])
            
            return {
                'exists': True,
                'path': str(folder),
                'total_files': total_files,
                'files_by_type': files_by_type,
                'supported_files': supported_files,
                'supported_count': len(supported_files)
            }
            
        except Exception as e:
            return {
                'exists': False,
                'path': folder_path,
                'error': f'Erreur analyse dossier: {str(e)}'
            }
    
    def test_cv_parsing_quality(self, cv_folder: str) -> Dict:
        """Évalue la qualité du parsing des CV (version améliorée)"""
        cv_files = self.find_files_in_folder(cv_folder, self.supported_cv_formats)
        parsing_results = []
        
        print(f"🔍 Test qualité parsing sur {len(cv_files)} fichiers...")
        
        # Afficher les formats trouvés
        formats_found = {}
        for cv_file in cv_files:
            ext = cv_file.suffix.lower()
            formats_found[ext] = formats_found.get(ext, 0) + 1
        
        if formats_found:
            print(f"   📄 Formats détectés: {dict(formats_found)}")
        
        for i, cv_file in enumerate(cv_files[:20]):  # Limiter à 20 pour les tests
            try:
                print(f"   📄 Test {i+1}/20: {cv_file.name}")
                
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
                    text_length = len(cv_data.get('raw_text', ''))
                    
                    parsing_results.append({
                        'file': cv_file.name,
                        'format': cv_file.suffix.lower(),
                        'quality_score': quality_score,
                        'text_length': text_length,
                        'missions_count': len(cv_data.get('professional_experience', [{}])[0].get('missions', [])),
                        'skills_count': len(cv_data.get('technical_skills', []) + cv_data.get('soft_skills', [])),
                        'status': 'success'
                    })
                    
                    # Diagnostic spécial pour BATU Sam.pdf
                    if 'BATU Sam' in cv_file.name or 'batu sam' in cv_file.name.lower():
                        print(f"   🎯 DIAGNOSTIC BATU SAM:")
                        print(f"      - Texte extrait: {text_length} caractères")
                        print(f"      - Score qualité: {quality_score:.1f}%")
                        print(f"      - Nom candidat: {cv_data.get('candidate_name', 'NON TROUVÉ')}")
                        print(f"      - Missions: {len(cv_data.get('professional_experience', [{}])[0].get('missions', []))}")
                        if text_length < 100:
                            print(f"      ⚠️  PROBLÈME: Très peu de texte extrait!")
                else:
                    print(f"   ❌ Erreur HTTP {response.status_code}")
                    parsing_results.append({
                        'file': cv_file.name,
                        'format': cv_file.suffix.lower(),
                        'status': 'error',
                        'error_code': response.status_code
                    })
                    
            except Exception as e:
                print(f"   ❌ Exception: {str(e)}")
                parsing_results.append({
                    'file': cv_file.name,
                    'format': cv_file.suffix.lower(),
                    'status': 'exception',
                    'error': str(e)
                })
        
        return {
            'total_files': len(cv_files),
            'tested_files': len(parsing_results),
            'successful_parses': len([r for r in parsing_results if r.get('status') == 'success']),
            'average_quality': statistics.mean([r.get('quality_score', 0) for r in parsing_results if r.get('quality_score')]) if parsing_results else 0,
            'formats_found': formats_found,
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
    
    def test_problematic_file(self, file_path: str) -> Dict:
        """Test spécifique pour un fichier problématique (version améliorée)"""
        try:
            file_path = self.normalize_path(file_path)
            
            if not file_path.exists():
                return {
                    'file': file_path.name,
                    'status': 'file_not_found',
                    'error': f'Fichier non trouvé: {file_path}',
                    'path_tried': str(file_path),
                    'parent_exists': file_path.parent.exists(),
                    'parent_content': list(file_path.parent.iterdir()) if file_path.parent.exists() else []
                }
            
            # Vérifier le format
            file_format = file_path.suffix.lower()
            if file_format not in self.supported_cv_formats:
                return {
                    'file': file_path.name,
                    'format': file_format,
                    'status': 'unsupported_format',
                    'error': f'Format non supporté: {file_format}',
                    'supported_formats': list(self.supported_cv_formats)
                }
            
            print(f"🔍 Test spécifique: {file_path.name}")
            print(f"   📁 Chemin: {file_path}")
            print(f"   📊 Taille: {file_path.stat().st_size} bytes")
            
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
                    'format': file_format,
                    'status': 'parsing_error',
                    'error_code': cv_response.status_code,
                    'error_message': cv_response.text[:200] if cv_response.text else 'Erreur inconnue'
                }
            
            cv_data = cv_response.json()
            
            # Analyse détaillée
            analysis = {
                'file': file_path.name,
                'format': file_format,
                'status': 'success',
                'file_size_bytes': file_path.stat().st_size,
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
                'raw_parsing_response': cv_data,  # Pour diagnostic approfondi
                'potential_issues': []
            }
            
            # Détection des problèmes
            if analysis['text_extraction']['raw_text_length'] < 50:
                analysis['potential_issues'].append({
                    'type': 'critical_low_text_extraction',
                    'description': f"CRITIQUE: Très peu de texte extrait ({analysis['text_extraction']['raw_text_length']} caractères)",
                    'recommendation': f"Le fichier {file_format} ne peut pas être lu correctement. Vérifier l'intégrité du fichier ou essayer un autre format."
                })
            elif analysis['text_extraction']['raw_text_length'] < 200:
                analysis['potential_issues'].append({
                    'type': 'low_text_extraction',
                    'description': f"Peu de texte extrait ({analysis['text_extraction']['raw_text_length']} caractères)",
                    'recommendation': f"Vérifier le format {file_format} ou les permissions de lecture"
                })
            
            if analysis['content_analysis']['missions_count'] == 0:
                analysis['potential_issues'].append({
                    'type': 'no_missions_found',
                    'description': "Aucune mission détectée",
                    'recommendation': "Vérifier le parsing des expériences professionnelles"
                })
            
            if analysis['content_analysis']['candidate_name'] == 'Non trouvé':
                analysis['potential_issues'].append({
                    'type': 'no_candidate_name',
                    'description': "Nom du candidat non détecté",
                    'recommendation': "Vérifier la structure du document"
                })
            
            return analysis
            
        except Exception as e:
            return {
                'file': Path(file_path).name if file_path else 'unknown',
                'status': 'exception',
                'error': str(e)
            }

    def discover_files(self, cv_folder: str, job_folder: str) -> Dict:
        """Découvre et analyse les fichiers dans les dossiers (version améliorée)"""
        print("🔍 DÉCOUVERTE DES FICHIERS (Version Corrigée)")
        print("="*50)
        
        cv_analysis = self.analyze_folder_content(cv_folder)
        job_analysis = self.analyze_folder_content(job_folder)
        
        print(f"📁 Dossier CV: {cv_analysis['path']}")
        if cv_analysis['exists']:
            print(f"   ✅ {cv_analysis['total_files']} fichiers trouvés")
            print(f"   📄 {cv_analysis['supported_count']} fichiers supportés")
            print(f"   📊 Types: {dict(cv_analysis['files_by_type'])}")
        else:
            print(f"   ❌ {cv_analysis['error']}")
            if 'parent_exists' in cv_analysis and cv_analysis['parent_exists']:
                print(f"   📁 Parent existe, contenu: {cv_analysis.get('parent_content', [])}")
        
        print(f"\n📁 Dossier Jobs: {job_analysis['path']}")
        if job_analysis['exists']:
            print(f"   ✅ {job_analysis['total_files']} fichiers trouvés")
            print(f"   📄 {job_analysis['supported_count']} fichiers supportés")
            print(f"   📊 Types: {dict(job_analysis['files_by_type'])}")
        else:
            print(f"   ❌ {job_analysis['error']}")
            if 'parent_exists' in job_analysis and job_analysis['parent_exists']:
                print(f"   📁 Parent existe, contenu: {job_analysis.get('parent_content', [])}")
        
        return {
            'cv_folder': cv_analysis,
            'job_folder': job_analysis
        }

def main():
    parser = argparse.ArgumentParser(description='Tests massifs SuperSmartMatch V2.1 - Support multi-formats (VERSION CORRIGÉE)')
    parser.add_argument('--cv-folder', default='~/Desktop/CV TEST', help='Dossier des CV (gestion espaces corrigée)')
    parser.add_argument('--job-folder', default='~/Desktop/FDP TEST', help='Dossier des Jobs (gestion espaces corrigée)')
    parser.add_argument('--max-tests', type=int, default=50, help='Nombre max de combinaisons')
    parser.add_argument('--output', help='Fichier de sortie du rapport')
    parser.add_argument('--parsing-quality', action='store_true', help='Test qualité parsing')
    parser.add_argument('--test-file', help='Test un fichier spécifique')
    parser.add_argument('--discover', action='store_true', help='Découvrir les fichiers dans les dossiers')
    
    args = parser.parse_args()
    
    test_suite = EnhancedTestSuite()
    
    print("🚀 SuperSmartMatch V2.1 - Suite de Tests Avancés (VERSION CORRIGÉE)")
    print("="*70)
    print("🔧 CORRECTIONS APPORTÉES:")
    print("   ✅ Gestion correcte des espaces dans les noms de dossiers")
    print("   ✅ Amélioration de la robustesse du parsing des chemins")
    print("   ✅ Diagnostic amélioré pour fichiers problématiques")
    print("   ✅ Meilleure gestion des erreurs de fichiers")
    print("📄 Formats supportés: PDF, DOC, DOCX, PNG, JPG, JPEG")
    print("="*70)
    
    # Découverte des fichiers
    discovery = test_suite.discover_files(args.cv_folder, args.job_folder)
    
    # Test d'un fichier spécifique
    if args.test_file:
        print(f"\n🔍 TEST FICHIER SPÉCIFIQUE: {args.test_file}")
        print("-" * 50)
        file_analysis = test_suite.test_problematic_file(args.test_file)
        print(f"📄 Fichier: {file_analysis['file']}")
        print(f"📊 Statut: {file_analysis['status']}")
        
        if file_analysis['status'] == 'success':
            text_info = file_analysis['text_extraction']
            print(f"📝 Texte extrait: {text_info['raw_text_length']} caractères")
            print(f"🏆 Score qualité: {text_info['quality_score']:.1f}%")
            
            if file_analysis['potential_issues']:
                print("\n⚠️  PROBLÈMES DÉTECTÉS:")
                for issue in file_analysis['potential_issues']:
                    print(f"   • {issue['description']}")
                    print(f"     → {issue['recommendation']}")
            else:
                print("\n✅ Aucun problème détecté")
    
    # Test qualité parsing
    if args.parsing_quality:
        print("\n1️⃣ TEST QUALITÉ PARSING")
        print("-" * 30)
        parsing_results = test_suite.test_cv_parsing_quality(args.cv_folder)
        
        print(f"✅ {parsing_results['successful_parses']}/{parsing_results['tested_files']} fichiers parsés avec succès")
        print(f"📊 Qualité moyenne: {parsing_results['average_quality']:.1f}%")
    
    print(f"\n🎯 SuperSmartMatch V2.1 Enhanced (Corrigé) - Tests terminés!")

if __name__ == '__main__':
    main()
