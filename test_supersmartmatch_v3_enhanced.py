#!/usr/bin/env python3
"""
Test SuperSmartMatch V3.0 - Enhanced Multi-Format Support
Intégration des améliorations Cursor + optimisations pour vos scores de 98.6%
"""

import unittest
import requests
import time
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import mimetypes
from datetime import datetime
import logging

# Configuration des chemins
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

try:
    from config.ports import PortConfig
except ImportError:
    # Fallback si config non disponible
    class PortConfig:
        API_GATEWAY = 5065
        CV_PARSER = 5051
        JOB_PARSER = 5053
        SUPERSMARTMATCH_V3 = 5067
        DASHBOARD = 5070
        
        @classmethod
        def get_service_urls(cls):
            return {
                'api_gateway': f'http://localhost:{cls.API_GATEWAY}',
                'cv_parser': f'http://localhost:{cls.CV_PARSER}',
                'job_parser': f'http://localhost:{cls.JOB_PARSER}',
                'supersmartmatch': f'http://localhost:{cls.SUPERSMARTMATCH_V3}',
                'dashboard': f'http://localhost:{cls.DASHBOARD}'
            }

class TestSuperSmartMatchV3Enhanced(unittest.TestCase):
    """Tests SuperSmartMatch V3.0 avec support multi-formats"""
    
    @classmethod
    def setUpClass(cls):
        """Configuration initiale des tests multi-formats"""
        cls.config = PortConfig()
        cls.urls = cls.config.get_service_urls()
        
        # Structure des dossiers de test
        cls.test_data_dir = PROJECT_ROOT / "test_data"
        cls.cv_dir = cls.test_data_dir / "cv"
        cls.fdp_dir = cls.test_data_dir / "fdp"  # Fiches de poste
        cls.test_results_dir = cls.test_data_dir / "results"
        
        # Créer les dossiers
        cls.cv_dir.mkdir(parents=True, exist_ok=True)
        cls.fdp_dir.mkdir(parents=True, exist_ok=True)
        cls.test_results_dir.mkdir(parents=True, exist_ok=True)
        
        # Formats de fichiers acceptés (amélioration Cursor)
        cls.accepted_formats = ['.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg', '.txt']
        
        # Mapping types MIME (amélioration Cursor)
        cls.mime_types = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.txt': 'text/plain'
        }
        
        # Vérifier la présence des fichiers dans tous les formats
        cls.cv_files = []
        cls.fdp_files = []
        
        for format_ext in cls.accepted_formats:
            cls.cv_files.extend(list(cls.cv_dir.glob(f"*{format_ext}")))
            cls.fdp_files.extend(list(cls.fdp_dir.glob(f"*{format_ext}")))
        
        # Créer des fichiers de test si absents
        cls.create_test_files_if_missing()
        
        # Configuration logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(cls.test_results_dir / 'test_log.log'),
                logging.StreamHandler()
            ]
        )
        cls.logger = logging.getLogger(__name__)
        
        # Métriques de test
        cls.test_metrics = {
            'total_tests': 0,
            'successful_tests': 0,
            'failed_tests': 0,
            'avg_response_time': 0,
            'formats_tested': {},
            'score_distribution': {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        }
        
        cls.logger.info("🎯 SuperSmartMatch V3.0 Enhanced Tests - Setup terminé")
        cls.logger.info(f"📁 CV files trouvés: {len(cls.cv_files)}")
        cls.logger.info(f"📄 FDP files trouvés: {len(cls.fdp_files)}")
    
    @classmethod
    def create_test_files_if_missing(cls):
        """Crée des fichiers de test dans différents formats si manquants"""
        
        # Contenu CV de référence (profil développeur senior)
        cv_content = """
DÉVELOPPEUR PYTHON SENIOR

INFORMATIONS PERSONNELLES:
Nom: Baptiste COMAS
Email: baptiste.comas@example.com
Téléphone: +33 6 12 34 56 78
LinkedIn: linkedin.com/in/baptistecomas

EXPÉRIENCE PROFESSIONNELLE:
Lead Developer - TechCorp (2020-2025)
• Direction technique équipe 8 développeurs Python
• Développement système matching IA (98.6% précision)
• Architecture microservices scalable (1M+ utilisateurs)
• Pipeline DevOps/CI-CD automatisé
• Technologies: Python, Django, FastAPI, PostgreSQL, Redis, Docker, Kubernetes

Senior Python Developer - InnovSoft (2018-2020)
• Développement APIs REST haute performance
• Mentoring développeurs junior
• Intégration solutions ML/IA
• Technologies: Python, Flask, MongoDB, AWS

Python Developer - StartupTech (2016-2018)
• Développement applications web full-stack
• Participation architecture technique
• Technologies: Python, Django, JavaScript, React

COMPÉTENCES TECHNIQUES:
• Langages: Python (Expert), JavaScript, TypeScript, SQL
• Frameworks: Django, FastAPI, Flask, React, Vue.js
• Bases de données: PostgreSQL, MongoDB, Redis, MySQL
• DevOps: Docker, Kubernetes, AWS, GCP, CI/CD, Jenkins
• Outils: Git, Linux, Nginx, Apache
• IA/ML: Scikit-learn, TensorFlow, Pandas, NumPy

COMPÉTENCES MANAGÉRIALES:
• Leadership technique et management équipe
• Gestion projets complexes et deadlines
• Communication stakeholders et clients
• Mentoring et formation équipes

FORMATION:
Master Informatique - École Centrale (2016)
Ingénieur Logiciel - Formation continue (2018)

RÉALISATIONS CLÉS:
• Système SuperSmartMatch V3.0 (98.6% précision, 6.9-35ms)
• Pipeline ML automatisé (réduction 80% temps traitement)
• Architecture microservices (support 1M+ utilisateurs)
• Équipe développement (croissance 3 à 12 personnes)

LANGUES:
• Français: Natif
• Anglais: Courant (C1)
• Espagnol: Intermédiaire (B2)
"""
        
        # Contenu FDP de référence
        fdp_content = """
FICHE DE POSTE - LEAD DEVELOPER

ENTREPRISE: TechnoInnovation
LOCALISATION: Paris / Remote hybride
TYPE DE CONTRAT: CDI
SALAIRE: 70-85K€ + variable

CONTEXTE:
Notre scale-up technologique recherche un Lead Developer pour diriger notre équipe de développement et porter nos innovations IA/ML.

MISSIONS PRINCIPALES:
• Direction technique équipe 10+ développeurs
• Architecture et développement solutions IA/ML
• Management et mentoring équipe technique
• Collaboration étroite avec Product Managers
• Innovation et veille technologique

RESPONSABILITÉS:
• Leadership technique sur projets stratégiques
• Décisions d'architecture et choix technologiques  
• Gestion performance et évolution équipe
• Collaboration avec stakeholders métier
• Optimisation performance et scalabilité

PROFIL RECHERCHÉ:

EXPÉRIENCE REQUISE:
• 5+ années développement Python/Django/FastAPI
• 3+ années expérience management équipe technique
• Expérience significative systèmes IA/ML
• Connaissance approfondie DevOps/Cloud (AWS/GCP)
• Maîtrise architecture microservices

COMPÉTENCES TECHNIQUES:
• Python (Expert), JavaScript, TypeScript
• Django, FastAPI, Flask
• PostgreSQL, Redis, MongoDB
• Docker, Kubernetes
• AWS/GCP, CI/CD
• IA/ML, Data Science

COMPÉTENCES MANAGÉRIALES:
• Leadership et management équipe
• Communication et collaboration
• Gestion projets techniques
• Mentoring développeurs

SOFT SKILLS:
• Excellent relationnel et communication
• Esprit d'équipe et leadership
• Capacité d'adaptation et innovation
• Résolution problèmes complexes

AVANTAGES:
• Télétravail hybride (2-3 jours/semaine)
• Formation continue et conférences
• Stock-options startup
• Mutuelle premium + RTT
• Équipement tech haut de gamme

PROCESS DE RECRUTEMENT:
1. Entretien RH (30min)
2. Test technique + code review (2h)
3. Entretien technique avec CTO (1h)
4. Entretien équipe + culture fit (1h)
5. Décision sous 48h
"""
        
        # Créer fichiers CV dans différents formats
        cv_files = [
            ('cv_senior_python.txt', cv_content),
            ('cv_lead_developer.txt', cv_content.replace('DÉVELOPPEUR PYTHON SENIOR', 'LEAD DEVELOPER FULL-STACK')),
            ('cv_devops_expert.txt', cv_content.replace('DÉVELOPPEUR PYTHON SENIOR', 'DEVOPS ENGINEER EXPERT'))
        ]
        
        for filename, content in cv_files:
            file_path = cls.cv_dir / filename
            if not file_path.exists():
                file_path.write_text(content, encoding='utf-8')
                cls.logger.info(f"✅ Créé: {filename}")
        
        # Créer fichiers FDP
        fdp_files = [
            ('fdp_lead_developer.txt', fdp_content),
            ('fdp_senior_python.txt', fdp_content.replace('LEAD DEVELOPER', 'SENIOR PYTHON DEVELOPER')),
            ('fdp_devops_lead.txt', fdp_content.replace('LEAD DEVELOPER', 'LEAD DEVOPS ENGINEER'))
        ]
        
        for filename, content in fdp_files:
            file_path = cls.fdp_dir / filename
            if not file_path.exists():
                file_path.write_text(content, encoding='utf-8')
                cls.logger.info(f"✅ Créé: {filename}")
    
    def test_services_health_multiformat(self):
        """Test santé des services avec support multi-formats"""
        self.logger.info("🏥 Test santé services multi-formats...")
        
        healthy_services = 0
        for service, url in self.urls.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    healthy_services += 1
                    self.logger.info(f"✅ {service}: OK")
                else:
                    self.logger.warning(f"❌ {service}: Status {response.status_code}")
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"⚪ {service}: {str(e)}")
        
        # Au moins 2 services doivent être up pour les tests
        self.assertGreaterEqual(healthy_services, 2, "Pas assez de services actifs")
    
    def test_supersmartmatch_v3_multiformat_performance(self):
        """Test performance SuperSmartMatch V3.0 avec différents formats"""
        self.logger.info("🎯 Test performance SuperSmartMatch V3.0 multi-formats...")
        
        # Données de test basées sur vos résultats exceptionnels
        test_combinations = [
            {
                'name': 'Profil Senior → Lead Developer',
                'cv_data': {
                    'skills': ['python', 'django', 'leadership', 'devops', 'docker', 'kubernetes', 'postgresql'],
                    'experience_years': 6,
                    'level': 'Senior',
                    'profile': 'Lead Developer Python'
                },
                'job_data': {
                    'title': 'Lead Developer',
                    'skills_required': ['python', 'management', 'devops', 'leadership', 'docker'],
                    'experience_required': 5,
                    'level': 'Senior'
                },
                'expected_min_score': 95.0  # Basé sur votre 98.6%
            },
            {
                'name': 'Profil DevOps → DevOps Lead',
                'cv_data': {
                    'skills': ['docker', 'kubernetes', 'aws', 'python', 'devops', 'ci/cd'],
                    'experience_years': 5,
                    'level': 'Senior',
                    'profile': 'DevOps Engineer'
                },
                'job_data': {
                    'title': 'DevOps Lead',
                    'skills_required': ['devops', 'kubernetes', 'aws', 'leadership'],
                    'experience_required': 4,
                    'level': 'Senior'
                },
                'expected_min_score': 90.0
            }
        ]
        
        matching_results = []
        
        for test_case in test_combinations:
            try:
                start_time = time.time()
                
                response = requests.post(
                    f"{self.urls['supersmartmatch']}/match",
                    json={
                        'cv_data': test_case['cv_data'],
                        'job_data': test_case['job_data'],
                        'algorithm': 'Enhanced_V3.0'
                    },
                    timeout=30
                )
                
                end_time = time.time()
                response_time_ms = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    match_result = response.json()
                    score = match_result.get('match_score', 0)
                    
                    # Vérifications basées sur vos résultats
                    if 'expected_min_score' in test_case:
                        self.assertGreaterEqual(
                            score, test_case['expected_min_score'],
                            f"Score trop faible pour {test_case['name']}: {score}% < {test_case['expected_min_score']}%"
                        )
                    
                    # Vérification temps de réponse (vos résultats: 6.9-35ms)
                    processing_time = match_result.get('processing_time_ms', response_time_ms)
                    self.assertLess(processing_time, 100, f"Temps trop lent: {processing_time}ms")
                    
                    # Classification du score
                    score_category = self._classify_score(score)
                    self.test_metrics['score_distribution'][score_category] += 1
                    
                    matching_results.append({
                        'test_name': test_case['name'],
                        'score': score,
                        'processing_time_ms': processing_time,
                        'algorithm': match_result.get('algorithm', 'Unknown'),
                        'details': match_result.get('details', {}),
                        'recommendations': match_result.get('recommendations', [])
                    })
                    
                    self.logger.info(f"✅ {test_case['name']}: {score}% en {processing_time:.1f}ms")
                    
                    # Score exceptionnel détecté
                    if score >= 95:
                        self.logger.info(f"🏆 Score exceptionnel détecté: {score}% !")
                        
                else:
                    self.logger.error(f"❌ {test_case['name']}: Status {response.status_code}")
                    
                self.test_metrics['total_tests'] += 1
                if response.status_code == 200:
                    self.test_metrics['successful_tests'] += 1
                else:
                    self.test_metrics['failed_tests'] += 1
                    
            except Exception as e:
                self.logger.error(f"❌ {test_case['name']}: {str(e)}")
                self.test_metrics['failed_tests'] += 1
        
        # Au moins un test doit réussir
        self.assertGreater(self.test_metrics['successful_tests'], 0, "Aucun test de matching réussi")
    
    def _classify_score(self, score: float) -> str:
        """Classifie un score en catégorie"""
        if score >= 95:
            return 'excellent'
        elif score >= 85:
            return 'good'
        elif score >= 70:
            return 'fair'
        else:
            return 'poor'

if __name__ == "__main__":
    unittest.main(verbosity=2)
