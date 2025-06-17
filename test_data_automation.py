#!/usr/bin/env python3
"""
Script d'automatisation des données de test SuperSmartMatch V3.0
Support multi-formats: PDF, DOCX, DOC, PNG, JPG, JPEG, TXT
"""

import os
import json
from pathlib import Path
from typing import Dict, List
import logging

class TestDataAutomation:
    """Automatisation de la préparation des données de test multi-formats"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_data_dir = self.project_root / "test_data"
        self.cv_dir = self.test_data_dir / "cv"
        self.fdp_dir = self.test_data_dir / "fdp"
        self.results_dir = self.test_data_dir / "results"
        
        # Configuration logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Formats supportés
        self.supported_formats = ['.pdf', '.docx', '.doc', '.png', '.jpg', '.jpeg', '.txt']
        
        # Templates de contenu
        self.cv_templates = self._get_cv_templates()
        self.fdp_templates = self._get_fdp_templates()
    
    def create_full_test_structure(self):
        """Créer la structure complète de test avec tous les formats"""
        
        self.logger.info("🏗️  Création structure test complète SuperSmartMatch V3.0")
        
        # Créer les dossiers
        self._create_directories()
        
        # Créer les fichiers de test
        self._create_cv_files()
        self._create_fdp_files()
        
        # Créer configuration de test
        self._create_test_config()
        
        # Créer scripts de validation
        self._create_validation_scripts()
        
        self.logger.info("✅ Structure de test complète créée !")
        self._print_structure_summary()
    
    def _create_directories(self):
        """Créer tous les dossiers nécessaires"""
        directories = [
            self.test_data_dir,
            self.cv_dir,
            self.fdp_dir,
            self.results_dir,
            self.test_data_dir / "logs",
            self.test_data_dir / "reports"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"📁 Créé: {directory}")
    
    def _create_cv_files(self):
        """Créer des fichiers CV dans tous les formats supportés"""
        
        cv_configs = [
            {
                'profile': 'senior_python_lead',
                'name': 'Baptiste COMAS - Lead Developer Python',
                'template': 'senior_lead_developer'
            },
            {
                'profile': 'devops_expert',
                'name': 'Alex MARTIN - DevOps Expert',
                'template': 'devops_expert'
            },
            {
                'profile': 'fullstack_senior',
                'name': 'Sarah DUBOIS - Senior Full-Stack',
                'template': 'fullstack_senior'
            },
            {
                'profile': 'junior_frontend',
                'name': 'Thomas LEROY - Junior Frontend',
                'template': 'junior_frontend'
            }
        ]
        
        for cv_config in cv_configs:
            template = self.cv_templates[cv_config['template']]
            content = template.format(**cv_config)
            
            # Créer dans tous les formats texte supportés
            for format_ext in ['.txt']:  # Commencer par .txt, d'autres formats nécessiteraient des libs
                filename = f"{cv_config['profile']}_cv{format_ext}"
                file_path = self.cv_dir / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.logger.info(f"📄 CV créé: {filename}")
    
    def _create_fdp_files(self):
        """Créer des fichiers FDP dans tous les formats supportés"""
        
        fdp_configs = [
            {
                'position': 'Lead Developer Python',
                'company': 'TechnoInnovation',
                'salary': '70-85K€',
                'template': 'lead_developer_python'
            },
            {
                'position': 'DevOps Lead',
                'company': 'CloudCorp',
                'salary': '75-90K€',
                'template': 'devops_lead'
            },
            {
                'position': 'Senior Full-Stack Developer',
                'company': 'StartupTech',
                'salary': '60-75K€',
                'template': 'senior_fullstack'
            },
            {
                'position': 'Frontend Developer',
                'company': 'WebAgency',
                'salary': '45-55K€',
                'template': 'frontend_developer'
            }
        ]
        
        for fdp_config in fdp_configs:
            template = self.fdp_templates[fdp_config['template']]
            content = template.format(**fdp_config)
            
            # Créer dans tous les formats texte supportés
            for format_ext in ['.txt']:
                filename = f"{fdp_config['position'].lower().replace(' ', '_')}_fdp{format_ext}"
                file_path = self.fdp_dir / filename
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.logger.info(f"💼 FDP créé: {filename}")
    
    def _create_test_config(self):
        """Créer fichier de configuration des tests"""
        
        config = {
            "test_configuration": {
                "supersmartmatch_version": "Enhanced_V3.0",
                "supported_formats": self.supported_formats,
                "test_data_structure": {
                    "cv_directory": str(self.cv_dir.relative_to(self.project_root)),
                    "fdp_directory": str(self.fdp_dir.relative_to(self.project_root)),
                    "results_directory": str(self.results_dir.relative_to(self.project_root))
                },
                "test_scenarios": {
                    "performance_targets": {
                        "accuracy_score": 98.6,
                        "min_response_time_ms": 6.9,
                        "max_response_time_ms": 35.0,
                        "target_success_rate": 98.5
                    },
                    "algorithm_tests": [
                        "Enhanced_V3.0",
                        "Semantic_V2.1",
                        "Weighted_Skills",
                        "Experience_Based",
                        "Hybrid_ML",
                        "Fuzzy_Logic",
                        "Neural_Network"
                    ],
                    "format_tests": self.supported_formats
                },
                "expected_results": {
                    "senior_to_lead_match": {"min_score": 95.0, "category": "excellent"},
                    "devops_to_devops_lead": {"min_score": 90.0, "category": "excellent"},
                    "junior_to_senior_mismatch": {"max_score": 60.0, "category": "poor"},
                    "skillset_mismatch": {"max_score": 50.0, "category": "poor"}
                }
            },
            "service_endpoints": {
                "cv_parser": "http://localhost:5051",
                "job_parser": "http://localhost:5053",
                "supersmartmatch": "http://localhost:5067",
                "api_gateway": "http://localhost:5065",
                "dashboard": "http://localhost:5070"
            },
            "mime_type_mapping": {
                ".pdf": "application/pdf",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ".doc": "application/msword",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".txt": "text/plain"
            }
        }
        
        config_path = self.test_data_dir / "test_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"⚙️  Configuration créée: {config_path}")
    
    def _create_validation_scripts(self):
        """Créer scripts de validation des tests"""
        
        # Script de validation rapide
        validation_script = '''#!/usr/bin/env python3
"""Script de validation rapide des tests SuperSmartMatch V3.0"""

import json
import requests
from pathlib import Path

def validate_test_setup():
    """Valide que tous les éléments sont en place pour les tests"""
    
    print("🔍 Validation setup SuperSmartMatch V3.0...")
    
    # Vérifier structure des fichiers
    test_data = Path("test_data")
    cv_files = list(test_data.glob("cv/*"))
    fdp_files = list(test_data.glob("fdp/*"))
    
    print(f"📄 CV files: {len(cv_files)}")
    print(f"💼 FDP files: {len(fdp_files)}")
    
    if len(cv_files) == 0 or len(fdp_files) == 0:
        print("❌ Fichiers de test manquants")
        return False
    
    # Vérifier services
    services = {
        "CV Parser": "http://localhost:5051/health",
        "Job Parser": "http://localhost:5053/health", 
        "SuperSmartMatch": "http://localhost:5067/health",
        "Dashboard": "http://localhost:5070/health"
    }
    
    active_services = 0
    for service, url in services.items():
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"✅ {service}: OK")
                active_services += 1
            else:
                print(f"❌ {service}: Error {response.status_code}")
        except:
            print(f"⚪ {service}: Offline")
    
    if active_services >= 2:
        print(f"🎯 Setup validé: {active_services}/4 services actifs")
        return True
    else:
        print(f"❌ Setup insuffisant: {active_services}/4 services actifs")
        return False

if __name__ == "__main__":
    validate_test_setup()
'''
        
        validation_path = self.test_data_dir / "validate_setup.py"
        with open(validation_path, 'w', encoding='utf-8') as f:
            f.write(validation_script)
        
        # Rendre exécutable
        validation_path.chmod(0o755)
        
        self.logger.info(f"🔍 Script validation créé: {validation_path}")
    
    def _print_structure_summary(self):
        """Affiche un résumé de la structure créée"""
        
        cv_count = len(list(self.cv_dir.glob("*")))
        fdp_count = len(list(self.fdp_dir.glob("*")))
        
        print("\n" + "="*60)
        print("🎯 SUPERSMARTMATCH V3.0 - STRUCTURE TEST CRÉÉE")
        print("="*60)
        print(f"📁 Dossier principal: {self.test_data_dir}")
        print(f"📄 Fichiers CV: {cv_count}")
        print(f"💼 Fichiers FDP: {fdp_count}")
        print(f"📊 Formats supportés: {', '.join(self.supported_formats)}")
        print("\n📋 Structure:")
        print("test_data/")
        print("  ├── cv/               # CVs de test")
        print("  ├── fdp/              # Fiches de poste")
        print("  ├── results/          # Résultats des tests")
        print("  ├── logs/             # Logs des tests")
        print("  ├── reports/          # Rapports")
        print("  ├── test_config.json  # Configuration")
        print("  └── validate_setup.py # Validation")
        print("\n🚀 COMMANDES UTILES:")
        print("# Valider le setup:")
        print("python test_data/validate_setup.py")
        print("\n# Lancer les tests:")
        print("python -m unittest test_supersmartmatch_v3_enhanced.py -v")
        print("\n🏆 Prêt pour tester vos scores de 98.6% !")
        print("="*60)
    
    def _get_cv_templates(self) -> Dict[str, str]:
        """Templates de CV pour différents profils"""
        
        return {
            'senior_lead_developer': '''
{name}
Lead Developer Python Senior

CONTACT:
Email: {profile}@example.com
LinkedIn: linkedin.com/in/{profile}
GitHub: github.com/{profile}

EXPÉRIENCE PROFESSIONNELLE:

Lead Developer - TechCorp (2020-2025)
• Direction technique équipe 8 développeurs Python
• Développement système SuperSmartMatch V3.0 (98.6% précision)
• Architecture microservices haute performance (6.9-35ms)
• Pipeline DevOps/CI-CD automatisé
• Management et mentoring équipe technique
• Technologies: Python, Django, FastAPI, PostgreSQL, Redis, Docker, Kubernetes

Senior Python Developer - InnovSoft (2018-2020)
• Développement APIs REST scalables
• Intégration solutions IA/Machine Learning
• Optimisation performance (amélioration 300%)
• Technologies: Python, Flask, MongoDB, AWS, Redis

Python Developer - StartupTech (2016-2018)
• Développement applications web full-stack
• Participation décisions architecture
• Technologies: Python, Django, JavaScript, React, PostgreSQL

COMPÉTENCES TECHNIQUES:
• Langages: Python (Expert), JavaScript, TypeScript, SQL, Bash
• Frameworks: Django, FastAPI, Flask, React, Vue.js
• Bases de données: PostgreSQL, MongoDB, Redis, MySQL
• DevOps: Docker, Kubernetes, AWS, GCP, CI/CD, Jenkins, Git
• IA/ML: Scikit-learn, TensorFlow, Pandas, NumPy
• Outils: Linux, Nginx, Apache, Elasticsearch

LEADERSHIP & MANAGEMENT:
• Management équipe 3-12 développeurs
• Mentoring et formation techniques
• Gestion projets complexes et deadlines
• Communication stakeholders et clients
• Recrutement et évaluation talents

RÉALISATIONS CLÉS:
• SuperSmartMatch V3.0: 98.6% précision, temps 6.9-35ms
• Pipeline ML automatisé: réduction 80% temps traitement
• Architecture microservices: support 1M+ utilisateurs concurrent
• Équipe développement: croissance 3 à 12 personnes en 2 ans

FORMATION:
Master Informatique - École Centrale (2016)
Certification AWS Solutions Architect (2019)
Formation Management Technique (2020)

LANGUES:
Français: Natif | Anglais: Courant (C1) | Espagnol: Intermédiaire (B2)
''',
            
            'devops_expert': '''
{name}
DevOps Engineer Expert

CONTACT:
Email: {profile}@example.com
LinkedIn: linkedin.com/in/{profile}

EXPÉRIENCE PROFESSIONNELLE:

DevOps Lead - CloudCorp (2019-2025)
• Direction infrastructure cloud pour 50+ applications
• Mise en place architecture Kubernetes multi-cluster
• Automatisation CI/CD (Jenkins, GitLab CI, GitHub Actions)
• Monitoring et observabilité (Prometheus, Grafana, ELK)
• Management équipe DevOps 6 personnes
• Technologies: Kubernetes, Docker, AWS, Terraform, Ansible

Senior DevOps Engineer - TechScale (2017-2019)
• Migration infrastructure on-premise vers AWS
• Automatisation déploiements (réduction 90% temps)
• Mise en place IaC (Infrastructure as Code)
• Technologies: AWS, Docker, Jenkins, Terraform, Python

DevOps Engineer - StartupCloud (2015-2017)
• Mise en place premiers processus DevOps
• Containerisation applications legacy
• Technologies: Docker, AWS, Jenkins, Python, Bash

COMPÉTENCES TECHNIQUES:
• Cloud: AWS (Expert), GCP, Azure
• Containers: Docker, Kubernetes, Helm
• IaC: Terraform, Ansible, CloudFormation
• CI/CD: Jenkins, GitLab CI, GitHub Actions, ArgoCD
• Monitoring: Prometheus, Grafana, ELK Stack, Datadog
• Languages: Python, Bash, Go, YAML
• Databases: PostgreSQL, MongoDB, Redis

CERTIFICATIONS:
• AWS Solutions Architect Professional
• Certified Kubernetes Administrator (CKA)
• Terraform Associate

RÉALISATIONS:
• Migration 100+ applications vers Kubernetes
• Réduction 95% temps déploiement
• Mise en place observabilité complète
• Infrastructure supportant 10M+ requêtes/jour

FORMATION:
Ingénieur Systèmes et Réseaux - EPITA (2015)
''',
            
            'fullstack_senior': '''
{name}
Senior Full-Stack Developer

CONTACT:
Email: {profile}@example.com
GitHub: github.com/{profile}

EXPÉRIENCE PROFESSIONNELLE:

Senior Full-Stack Developer - WebTech (2019-2025)
• Développement applications web complexes
• Lead technique projets front-end et back-end
• Architecture APIs REST et GraphQL
• Technologies: React, Node.js, Python, PostgreSQL

Full-Stack Developer - DigitalAgency (2017-2019)
• Développement sites e-commerce haute performance
• Intégration solutions de paiement et CRM
• Technologies: Vue.js, PHP, MySQL, Redis

Junior Full-Stack Developer - WebStart (2016-2017)
• Développement applications web responsive
• Technologies: JavaScript, HTML5, CSS3, PHP

COMPÉTENCES TECHNIQUES:
• Frontend: React, Vue.js, Angular, TypeScript, HTML5, CSS3
• Backend: Node.js, Python, PHP, Express, FastAPI
• Databases: PostgreSQL, MySQL, MongoDB, Redis
• Tools: Git, Docker, Webpack, Vite

PROJETS:
• Plateforme e-commerce (500K+ utilisateurs)
• Application mobile-first responsive
• API GraphQL haute performance
''',
            
            'junior_frontend': '''
{name}
Junior Frontend Developer

CONTACT:
Email: {profile}@example.com
Portfolio: {profile}.dev

EXPÉRIENCE PROFESSIONNELLE:

Junior Frontend Developer - WebAgency (2023-2025)
• Développement interfaces utilisateur modernes
• Intégration maquettes design vers code
• Optimisation performance applications web
• Technologies: React, JavaScript, CSS3, HTML5

Stage Frontend Developer - DigitalStart (2023)
• Développement composants React réutilisables
• Intégration APIs REST
• Technologies: React, JavaScript, Sass

FORMATION:
Master Développement Web - Université Tech (2023)
Formation React/JavaScript - École 42 (2022)

COMPÉTENCES TECHNIQUES:
• Languages: JavaScript, TypeScript, HTML5, CSS3
• Frameworks: React, Vue.js
• Tools: Git, Webpack, Sass, Figma
• Bases: Node.js, REST APIs

PROJETS:
• Portfolio personnel responsive
• Application météo React
• Site vitrine e-commerce
'''
        }
    
    def _get_fdp_templates(self) -> Dict[str, str]:
        """Templates de FDP pour différents postes"""
        
        return {
            'lead_developer_python': '''
FICHE DE POSTE - {position}

ENTREPRISE: {company}
LOCALISATION: Paris / Remote hybride
CONTRAT: CDI
RÉMUNÉRATION: {salary} + variables

CONTEXTE:
{company} recherche un Lead Developer Python pour diriger notre équipe de développement et porter nos innovations technologiques.

MISSIONS PRINCIPALES:
• Direction technique équipe 10+ développeurs Python
• Architecture et développement solutions IA/ML de pointe
• Management et mentoring équipe technique
• Collaboration étroite Product Managers et stakeholders
• Innovation technologique et veille

RESPONSABILITÉS:
• Leadership technique projets stratégiques
• Décisions architecture et choix technologiques
• Gestion performance et évolution équipe
• Optimisation performance et scalabilité systèmes
• Recrutement et formation nouveaux talents

PROFIL RECHERCHÉ:

EXPÉRIENCE REQUISE:
• 5+ années développement Python/Django/FastAPI
• 3+ années expérience management équipe technique
• Expérience significative développement systèmes IA/ML
• Maîtrise architecture microservices et APIs
• Connaissance approfondie DevOps/Cloud (AWS/GCP)

COMPÉTENCES TECHNIQUES:
• Python (Expert), JavaScript, TypeScript
• Django, FastAPI, Flask
• PostgreSQL, Redis, MongoDB
• Docker, Kubernetes, CI/CD
• AWS/GCP, Infrastructure as Code
• Machine Learning, Data Science

COMPÉTENCES MANAGÉRIALES:
• Leadership et management équipe technique
• Communication excellente (français/anglais)
• Gestion projets complexes et deadlines
• Mentoring et développement talents
• Vision produit et technique

SOFT SKILLS:
• Esprit d'équipe et collaboration
• Capacité d'adaptation et innovation
• Résolution problèmes complexes
• Curiosité technologique permanente

AVANTAGES:
• Télétravail hybride flexible
• Formation continue et conférences
• Package stock-options attractive
• Mutuelle premium + RTT
• Équipement technique haut de gamme
• Budget formation 3000€/an

PROCESS RECRUTEMENT:
1. Entretien RH (30min)
2. Test technique + review code (2h)
3. Entretien technique CTO (1h)
4. Rencontre équipe + culture fit (1h)
5. Décision sous 48h
''',
            
            'devops_lead': '''
FICHE DE POSTE - {position}

ENTREPRISE: {company}
LOCALISATION: Paris / Full Remote
CONTRAT: CDI
RÉMUNÉRATION: {salary} + primes

CONTEXTE:
{company} recherche un DevOps Lead pour transformer notre infrastructure et accompagner notre hypercroissance.

MISSIONS:
• Direction stratégique infrastructure cloud
• Management équipe DevOps 8+ personnes
• Architecture plateforme Kubernetes enterprise
• Automatisation complète CI/CD/CD
• Observabilité et monitoring avancé

RESPONSABILITÉS:
• Design architecture cloud multi-région
• Gestion budget infrastructure (500K€/an)
• Recrutement et formation équipe DevOps
• Collaboration avec équipes développement
• Sécurité et conformité infrastructure

PROFIL RECHERCHÉ:

EXPÉRIENCE:
• 6+ années DevOps/Infrastructure
• 3+ années management équipe technique
• Expertise Kubernetes en production
• Maîtrise clouds publics (AWS/GCP/Azure)

COMPÉTENCES TECHNIQUES:
• Kubernetes, Docker, Helm
• AWS/GCP (certifications appréciées)
• Terraform, Ansible, IaC
• Jenkins, GitLab CI, ArgoCD
• Prometheus, Grafana, ELK
• Python, Go, Bash

AVANTAGES:
• Full remote possible
• Formation certifications cloud
• Conférences internationales
• Stock-options significatives
''',
            
            'senior_fullstack': '''
FICHE DE POSTE - {position}

ENTREPRISE: {company}
LOCALISATION: Paris / Hybride
CONTRAT: CDI
RÉMUNÉRATION: {salary}

MISSIONS:
• Développement applications web full-stack
• Architecture front-end et back-end
• Mentoring développeurs junior
• Collaboration équipes design/product

PROFIL:
• 4+ années développement full-stack
• Maîtrise React/Vue.js + Node.js/Python
• Expérience APIs REST/GraphQL
• Bases DevOps (Docker, CI/CD)

STACK TECHNIQUE:
• Frontend: React, TypeScript, Next.js
• Backend: Node.js, Python, PostgreSQL
• Cloud: AWS, Docker
• Tools: Git, Jest, Cypress
''',
            
            'frontend_developer': '''
FICHE DE POSTE - {position}

ENTREPRISE: {company}
LOCALISATION: Paris
CONTRAT: CDI
RÉMUNÉRATION: {salary}

MISSIONS:
• Développement interfaces utilisateur modernes
• Intégration maquettes vers code optimisé
• Collaboration designers et développeurs
• Optimisation performance applications

PROFIL:
• 2+ années développement frontend
• Maîtrise React ou Vue.js
• Connaissance HTML5, CSS3, JavaScript
• Sensibilité UX/UI

STACK:
• React, TypeScript
• CSS3, Sass, Tailwind
• Git, Webpack, Vite
• Figma, Adobe XD
'''
        }

def main():
    """Fonction principale"""
    automation = TestDataAutomation()
    automation.create_full_test_structure()

if __name__ == "__main__":
    main()
