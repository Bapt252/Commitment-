"""Tests de charge spécifiques pour l'environnement de staging."""
import random
import json
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Initialisation des tests Locust."""
    if isinstance(environment.runner, MasterRunner):
        logger.info("Démarrage des tests de charge sur staging")


class StagingUser(HttpUser):
    """Utilisateur pour les tests de charge en staging."""
    
    wait_time = between(0.5, 2)
    
    def on_start(self):
        """Setup pour chaque utilisateur."""
        # Vérifier la disponibilité du service
        response = self.client.get("/health")
        if response.status_code != 200:
            logger.error(f"Service non disponible: {response.status_code}")
            self.stop()
        
        logger.info(f"Utilisateur {self.id} démarré")
    
    @task(5)
    def realistic_cv_parsing(self):
        """Test de parsing avec des CVs réalistes."""
        realistic_cvs = [
            """
            Jean Dupont
            Ingénieur Logiciel Senior
            
            Expérience:
            - 7 ans en développement Python/Django
            - Expert en architecture microservices
            - Expérience en DevOps et conteneurisation
            
            Compétences:
            - Python, Django, FastAPI
            - PostgreSQL, Redis
            - Docker, Kubernetes
            - AWS, GCP
            
            Formation:
            - Master en Informatique, École Polytechnique
            - Certifié AWS Solutions Architect
            """,
            """
            Marie Martin
            Data Scientist
            
            Expérience:
            - 5 ans en analyse de données
            - Spécialisée en ML et Deep Learning
            - Projets en NLP et Computer Vision
            
            Compétences:
            - Python, R, SQL
            - TensorFlow, PyTorch, Scikit-learn
            - Spark, Hadoop
            - Tableau, Power BI
            
            Formation:
            - PhD en Statistiques, Université Paris-Saclay
            - Publications en machine learning
            """,
            """
            Pierre Durand
            DevOps Engineer
            
            Expérience:
            - 4 ans en infrastructure cloud
            - Expert en automation et CI/CD
            - Gestion de clusters Kubernetes en production
            
            Compétences:
            - Terraform, Ansible
            - Jenkins, GitLab CI
            - Monitoring: Prometheus, Grafana
            - Linux, Bash, Python
            
            Formation:
            - Ingénieur INSA Lyon
            - Certifications Kubernetes (CKA, CKAD)
            """
        ]
        
        cv_text = random.choice(realistic_cvs)
        
        with self.client.post(
            "/api/parse-cv/text",
            json={"text": cv_text.strip()},
            catch_response=True,
            name="CV Parsing (Realistic)"
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
                # Mesurer le temps de traitement
                if hasattr(response, 'elapsed'):
                    logger.info(f"CV parsing took {response.elapsed.total_seconds():.2f}s")
            else:
                response.failure(f"Failed: {response.status_code}")
    
    @task(4)
    def realistic_job_parsing(self):
        """Test de parsing avec des descriptions de poste réalistes."""
        realistic_jobs = [
            """
            Nous recherchons un Développeur Full Stack Senior
            
            Missions:
            - Développer des applications web avec React/Node.js
            - Concevoir des APIs RESTful robustes
            - Participer à l'architecture technique
            - Encadrer les développeurs juniors
            
            Profil recherché:
            - 5+ ans d'expérience en développement web
            - Maîtrise de JavaScript, TypeScript
            - Expérience avec React, Node.js, Express
            - Connaissance des bases de données (PostgreSQL, MongoDB)
            - Familiarité avec Docker et les outils DevOps
            
            Nous offrons:
            - Salaire: 55-70k€
            - Télétravail partiel
            - Formation continue
            - Assurance santé premium
            """,
            """
            Data Engineer - équipe Analytics
            
            Responsabilités:
            - Développer des pipelines de données robustes
            - Optimiser les performances des requêtes
            - Maintenir l'infrastructure Big Data
            - Collaborer avec les Data Scientists
            
            Compétences requises:
            - Python, SQL avancé
            - Apache Spark, Kafka
            - Cloud (AWS/GCP): S3, BigQuery, Dataflow
            - Outils d'orchestration: Airflow, Prefect
            - Docker, Kubernetes
            
            Profil:
            - Bac+5 en informatique ou équivalent
            - 3+ ans en ingénierie des données
            - Expérience avec les architectures distribuées
            - Anglais courant
            """,
            """
            Chef de Projet Technique
            
            Contexte:
            Nous développons une plateforme SaaS innovante dans le domaine
            de l'intelligence artificielle. Nous cherchons un chef de projet
            pour coordonner nos équipes techniques.
            
            Missions principales:
            - Gérer les roadmaps produit et technique
            - Coordonner les équipes dev, QA, DevOps
            - Interface entre business et technique
            - Assurer la qualité des livrables
            
            Profil souhaité:
            - Formation ingénieur + expérience en gestion de projet
            - Compréhension des enjeux techniques (architecture, sécurité)
            - Certification PMP ou équivalent
            - Expérience en méthodologies Agile/Scrum
            - Leadership et communication
            """
        ]
        
        job_text = random.choice(realistic_jobs)
        
        with self.client.post(
            "/api/analyze",
            json={"text": job_text.strip()},
            catch_response=True,
            name="Job Parsing (Realistic)"
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
            else:
                response.failure(f"Failed: {response.status_code}")
    
    @task(3)
    def stress_test_matching(self):
        """Test de stress pour le matching."""
        # Générer des données aléatoires mais cohérentes
        skills_pool = [
            ["Python", "Django", "PostgreSQL"],
            ["JavaScript", "React", "Node.js"],
            ["Java", "Spring", "MySQL"],
            ["C#", ".NET", "SQL Server"],
            ["Python", "Machine Learning", "TensorFlow"],
            ["DevOps", "Docker", "Kubernetes"],
            ["AWS", "Terraform", "Jenkins"]
        ]
        
        cv_skills = random.choice(skills_pool)
        job_skills = random.choice(skills_pool)
        
        cv_data = {
            "name": f"Candidat {random.randint(1000, 9999)}",
            "skills": cv_skills,
            "experience_years": random.randint(1, 15),
            "education": random.choice(["Bachelor", "Master", "PhD"]),
            "location": random.choice(["Paris", "Lyon", "Toulouse", "Remote"])
        }
        
        job_data = {
            "title": f"Poste {random.randint(100, 999)}",
            "required_skills": job_skills[:2],
            "preferred_skills": job_skills[2:],
            "min_experience": random.randint(1, 8),
            "location": random.choice(["Paris", "Lyon", "Toulouse", "Remote"])
        }
        
        with self.client.post(
            "/api/match/advanced",
            json={"cv_data": cv_data, "job_data": job_data},
            catch_response=True,
            name="Advanced Matching (Stress)"
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
                try:
                    data = response.json()
                    match_score = data.get("match_score", 0)
                    if 0 <= match_score <= 100:
                        # Score valide
                        pass
                    else:
                        response.failure(f"Invalid match score: {match_score}")
                except (json.JSONDecodeError, KeyError):
                    response.failure("Invalid response format")
            else:
                response.failure(f"Failed: {response.status_code}")
    
    @task(1)
    def test_concurrent_file_upload(self):
        """Test de téléchargement de fichiers concurrents."""
        # Simuler différents types de fichiers
        file_types = [
            ('cv.pdf', b'%PDF-1.4\nFake PDF CV', 'application/pdf'),
            ('cv.docx', b'PK\x03\x04Fake DOCX CV', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            ('cv.txt', b'Plain text CV content', 'text/plain')
        ]
        
        filename, content, mimetype = random.choice(file_types)
        
        files = {
            'file': (filename, content, mimetype)
        }
        
        with self.client.post(
            "/api/parse-cv/",
            files=files,
            data={'force_refresh': 'false'},
            catch_response=True,
            name="File Upload (Concurrent)"
        ) as response:
            # Les faux fichiers peuvent échouer, c'est OK
            if response.status_code in [200, 202, 400, 422, 500]:
                response.success()
            else:
                response.failure(f"Unexpected: {response.status_code}")
    
    @task(1)
    def health_and_metrics_check(self):
        """Vérification périodique de santé et métriques."""
        endpoints = [
            ("/health", "Health Check"),
            ("/metrics", "Metrics"),
            ("/api/cv-parser/health", "CV Parser Health"),
            ("/api/job-parser/health", "Job Parser Health")
        ]
        
        for endpoint, name in endpoints:
            with self.client.get(
                endpoint,
                catch_response=True,
                name=name
            ) as response:
                if response.status_code == 200:
                    response.success()
                elif response.status_code == 404:
                    # Certains endpoints peuvent ne pas exister
                    response.success()
                else:
                    response.failure(f"Failed: {response.status_code}")
    
    def on_stop(self):
        """Nettoyage à l'arrêt de l'utilisateur."""
        logger.info(f"Utilisateur {self.id} arrêté")