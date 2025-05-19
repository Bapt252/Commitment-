"""Tests de performance avec Locust pour l'API Nexten."""
import random
import json
from locust import HttpUser, task, between
from locust.exception import RescheduleTask


class APIUser(HttpUser):
    """Utilisateur simulé pour les tests de performance."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup initial pour chaque utilisateur."""
        # Test de connectivité
        try:
            response = self.client.get("/health")
            if response.status_code != 200:
                raise RescheduleTask("Service not available")
        except Exception as e:
            print(f"Service unavailable: {e}")
            raise RescheduleTask("Service not available")
    
    @task(3)
    def test_health_check(self):
        """Test du endpoint de santé."""
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(2)
    def test_metrics_endpoint(self):
        """Test du endpoint de métriques."""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Metrics endpoint failed: {response.status_code}")
    
    @task(5)
    def test_parse_cv_text(self):
        """Test de parsing de CV par texte."""
        cv_samples = [
            "John Doe\nSoftware Engineer\n5 years experience in Python",
            "Jane Smith\nData Scientist\nPh.D. in Computer Science\nSkills: Python, ML, TensorFlow",
            "Bob Johnson\nFull Stack Developer\nJavaScript, React, Node.js\n3 years experience",
            "Alice Brown\nDevOps Engineer\nAWS, Docker, Kubernetes\nBachelor's in Computer Science"
        ]
        
        cv_text = random.choice(cv_samples)
        
        with self.client.post(
            "/api/parse-cv/text",
            json={"text": cv_text},
            catch_response=True
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
                try:
                    data = response.json()
                    if "parsed_data" not in data:
                        response.failure("Missing parsed_data in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"CV parsing failed: {response.status_code}")
    
    @task(3)
    def test_parse_job_description(self):
        """Test de parsing de description de poste."""
        job_samples = [
            "Software Engineer position requiring Python, Django, and PostgreSQL experience. 3+ years required.",
            "Data Scientist role. Must have experience with ML algorithms, Python, and statistical analysis.",
            "DevOps Engineer needed. Experience with AWS, Docker, and CI/CD pipelines required.",
            "Frontend Developer position. React, JavaScript, and CSS skills needed. Remote work available."
        ]
        
        job_text = random.choice(job_samples)
        
        with self.client.post(
            "/api/analyze",
            json={"text": job_text},
            catch_response=True
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
                try:
                    data = response.json()
                    if "analysis" not in data:
                        response.failure("Missing analysis in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Job parsing failed: {response.status_code}")
    
    @task(2)
    def test_matching_simple(self):
        """Test de matching simple."""
        cv_data = {
            "name": "Test User",
            "skills": ["Python", "Django", "PostgreSQL"],
            "experience_years": 3
        }
        
        job_data = {
            "title": "Software Engineer",
            "required_skills": ["Python", "Django"],
            "min_experience": 2
        }
        
        with self.client.post(
            "/api/match/simple",
            json={"cv_data": cv_data, "job_data": job_data},
            catch_response=True
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
                try:
                    data = response.json()
                    if "match_score" not in data:
                        response.failure("Missing match_score in response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"Matching failed: {response.status_code}")
    
    @task(1)
    def test_parse_cv_file_simulation(self):
        """Simulation de parsing de fichier CV."""
        # Simuler un fichier PDF
        fake_pdf_content = b"%PDF-1.4\nFake PDF content for testing"
        
        files = {
            'file': ('test_cv.pdf', fake_pdf_content, 'application/pdf')
        }
        
        with self.client.post(
            "/api/parse-cv/",
            files=files,
            catch_response=True
        ) as response:
            # Accepter les erreurs de parsing car c'est un faux fichier
            if response.status_code in [200, 202, 400, 422]:
                response.success()
            else:
                response.failure(f"Unexpected response: {response.status_code}")


class AdminUser(HttpUser):
    """Utilisateur admin pour les tests d'endpoints administratifs."""
    
    wait_time = between(5, 10)
    weight = 1  # Moins d'utilisateurs admin
    
    @task(2)
    def test_admin_metrics(self):
        """Test des métriques administratives."""
        endpoints = [
            "/admin/stats",
            "/admin/health/detailed",
            "/admin/queue/status"
        ]
        
        for endpoint in endpoints:
            with self.client.get(endpoint, catch_response=True) as response:
                # Les endpoints admin peuvent nécessiter une authentification
                if response.status_code in [200, 401, 403]:
                    response.success()
                else:
                    response.failure(f"Admin endpoint failed: {response.status_code}")
    
    @task(1)
    def test_system_info(self):
        """Test des informations système."""
        with self.client.get("/system/info", catch_response=True) as response:
            if response.status_code in [200, 401, 403]:
                response.success()
            else:
                response.failure(f"System info failed: {response.status_code}")


class MLIntensiveUser(HttpUser):
    """Utilisateur pour les tests intensifs de ML."""
    
    wait_time = between(2, 5)
    weight = 1  # Utilisateur spécialisé
    
    @task(1)
    def test_batch_cv_processing(self):
        """Test de traitement par batch de CVs."""
        cv_batch = [
            "John Doe - Software Engineer with Python experience",
            "Jane Smith - Data Scientist with ML background",
            "Bob Wilson - DevOps Engineer with AWS skills"
        ]
        
        with self.client.post(
            "/api/parse-cv/batch",
            json={"texts": cv_batch},
            catch_response=True
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
            else:
                response.failure(f"Batch processing failed: {response.status_code}")
    
    @task(1)
    def test_advanced_matching(self):
        """Test de matching avancé avec IA."""
        cv_data = {
            "name": "Expert Developer",
            "skills": ["Python", "Machine Learning", "TensorFlow", "Django", "PostgreSQL"],
            "experience_years": 8,
            "education": "Master's in Computer Science",
            "certifications": ["AWS Solutions Architect", "Google Cloud Professional"]
        }
        
        job_data = {
            "title": "Senior ML Engineer",
            "required_skills": ["Python", "Machine Learning", "TensorFlow"],
            "preferred_skills": ["Django", "Cloud Platforms"],
            "min_experience": 5,
            "education_level": "Bachelor's degree"
        }
        
        with self.client.post(
            "/api/match/advanced",
            json={"cv_data": cv_data, "job_data": job_data},
            catch_response=True
        ) as response:
            if response.status_code in [200, 202]:
                response.success()
            else:
                response.failure(f"Advanced matching failed: {response.status_code}")