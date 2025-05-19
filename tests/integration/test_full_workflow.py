"""Tests d'intégration pour le workflow complet de l'application."""
import pytest
import requests
import time
import json
from typing import Dict, Any
import os


class TestFullWorkflow:
    """Tests du workflow complet: CV parsing + Job parsing + Matching."""
    
    @pytest.fixture(scope="class")
    def api_base_url(self):
        """URL de base de l'API."""
        return os.getenv("API_BASE_URL", "http://localhost:5050")
    
    @pytest.fixture(scope="class")
    def api_headers(self):
        """Headers pour les requêtes API."""
        headers = {"Content-Type": "application/json"}
        
        # Ajouter un token d'authentification si disponible
        api_key = os.getenv("API_KEY")
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        return headers
    
    @pytest.fixture
    def sample_cv_text(self):
        """Exemple de CV pour les tests."""
        return """
        John Doe
        Software Engineer
        
        Experience:
        - 5 years in Python development
        - Expert in Django and FastAPI
        - Experience with PostgreSQL and Redis
        - DevOps knowledge: Docker, Kubernetes
        
        Skills:
        - Programming: Python, JavaScript, SQL
        - Frameworks: Django, FastAPI, React
        - Databases: PostgreSQL, MongoDB, Redis
        - Tools: Git, Docker, Jenkins
        - Cloud: AWS, GCP
        
        Education:
        - Master's degree in Computer Science
        - AWS Solutions Architect certification
        
        Languages:
        - English (fluent)
        - French (native)
        """
    
    @pytest.fixture
    def sample_job_description(self):
        """Exemple de description de poste pour les tests."""
        return """
        Senior Software Engineer Position
        
        We are looking for an experienced software engineer to join our team.
        
        Requirements:
        - 3+ years of experience in software development
        - Strong knowledge of Python and web frameworks
        - Experience with relational databases
        - Familiarity with cloud platforms (AWS/GCP)
        - Knowledge of containerization (Docker)
        
        Responsibilities:
        - Develop and maintain web applications
        - Design scalable architecture
        - Collaborate with cross-functional teams
        - Mentor junior developers
        
        We offer:
        - Competitive salary
        - Remote work options
        - Health insurance
        - Professional development opportunities
        """
    
    def test_service_health(self, api_base_url):
        """Test que tous les services sont opérationnels."""
        health_endpoints = [
            "/health",
            "/api/cv-parser/health",
            "/api/job-parser/health",
            "/api/matching/health"
        ]
        
        for endpoint in health_endpoints:
            response = requests.get(f"{api_base_url}{endpoint}")
            assert response.status_code == 200, f"Health check failed for {endpoint}"
    
    def test_metrics_available(self, api_base_url):
        """Test que les métriques sont disponibles."""
        response = requests.get(f"{api_base_url}/metrics")
        assert response.status_code == 200
        assert "http_requests_total" in response.text
    
    def test_cv_parsing_text(self, api_base_url, api_headers, sample_cv_text):
        """Test du parsing de CV par texte."""
        response = requests.post(
            f"{api_base_url}/api/parse-cv/text",
            headers=api_headers,
            json={"text": sample_cv_text}
        )
        
        assert response.status_code in [200, 202]
        data = response.json()
        
        # Vérifier la structure de la réponse
        assert "parsed_data" in data
        parsed_data = data["parsed_data"]
        
        # Vérifier que les informations clés sont extraites
        assert "name" in parsed_data
        assert "skills" in parsed_data
        assert "experience" in parsed_data
        
        # Vérifier que le nom est correct
        assert "John Doe" in parsed_data["name"]
        
        # Vérifier que des compétences sont extraites
        assert len(parsed_data["skills"]) > 0
        assert any("Python" in skill for skill in parsed_data["skills"])
        
        return parsed_data
    
    def test_job_parsing(self, api_base_url, api_headers, sample_job_description):
        """Test du parsing de description de poste."""
        response = requests.post(
            f"{api_base_url}/api/analyze",
            headers=api_headers,
            json={"text": sample_job_description}
        )
        
        assert response.status_code in [200, 202]
        data = response.json()
        
        # Vérifier la structure de la réponse
        assert "analysis" in data
        analysis = data["analysis"]
        
        # Vérifier que les informations clés sont extraites
        assert "title" in analysis
        assert "required_skills" in analysis
        assert "responsibilities" in analysis
        
        # Vérifier le titre
        assert "Software Engineer" in analysis["title"]
        
        # Vérifier que des compétences sont extraites
        assert len(analysis["required_skills"]) > 0
        
        return analysis
    
    def test_simple_matching(self, api_base_url, api_headers):
        """Test du matching simple."""
        cv_data = {
            "name": "Test Candidate",
            "skills": ["Python", "Django", "PostgreSQL"],
            "experience_years": 5,
            "education": "Master's degree"
        }
        
        job_data = {
            "title": "Software Engineer",
            "required_skills": ["Python", "Django"],
            "min_experience": 3,
            "location": "Remote"
        }
        
        response = requests.post(
            f"{api_base_url}/api/match/simple",
            headers=api_headers,
            json={"cv_data": cv_data, "job_data": job_data}
        )
        
        assert response.status_code in [200, 202]
        data = response.json()
        
        # Vérifier la structure de la réponse
        assert "match_score" in data
        assert "details" in data
        
        # Vérifier que le score est dans une plage valide
        match_score = data["match_score"]
        assert 0 <= match_score <= 100
        
        # Le score devrait être élevé car les compétences correspondent
        assert match_score > 50
        
        return data
    
    def test_full_workflow_integration(self, api_base_url, api_headers, 
                                      sample_cv_text, sample_job_description):
        """Test du workflow complet: parsing + matching."""
        # Étape 1: Parser le CV
        cv_response = requests.post(
            f"{api_base_url}/api/parse-cv/text",
            headers=api_headers,
            json={"text": sample_cv_text}
        )
        assert cv_response.status_code in [200, 202]
        cv_data = cv_response.json()["parsed_data"]
        
        # Étape 2: Parser la description de poste
        job_response = requests.post(
            f"{api_base_url}/api/analyze",
            headers=api_headers,
            json={"text": sample_job_description}
        )
        assert job_response.status_code in [200, 202]
        job_data = job_response.json()["analysis"]
        
        # Étape 3: Effectuer le matching
        match_response = requests.post(
            f"{api_base_url}/api/match/advanced",
            headers=api_headers,
            json={"cv_data": cv_data, "job_data": job_data}
        )
        assert match_response.status_code in [200, 202]
        match_data = match_response.json()
        
        # Vérifications du résultat final
        assert "match_score" in match_data
        assert "detailed_analysis" in match_data
        
        match_score = match_data["match_score"]
        assert 0 <= match_score <= 100
        
        # Vérifier les détails de l'analyse
        analysis = match_data["detailed_analysis"]
        assert "skills_match" in analysis
        assert "experience_match" in analysis
        
        return match_data
    
    def test_concurrent_requests(self, api_base_url, api_headers, sample_cv_text):
        """Test de requêtes concurrentes."""
        import concurrent.futures
        import threading
        
        results = []
        errors = []
        
        def make_request():
            try:
                response = requests.post(
                    f"{api_base_url}/api/parse-cv/text",
                    headers=api_headers,
                    json={"text": sample_cv_text},
                    timeout=30
                )
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Lancer 10 requêtes concurrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            concurrent.futures.wait(futures)
        
        # Vérifier que toutes les requêtes ont réussi
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        assert all(status in [200, 202] for status in results)
    
    def test_error_handling(self, api_base_url, api_headers):
        """Test de la gestion d'erreurs."""
        # Test avec des données invalides
        invalid_requests = [
            # CV parsing avec texte vide
            ("/api/parse-cv/text", {"text": ""}),
            # Job parsing avec données manquantes
            ("/api/analyze", {}),
            # Matching avec données invalides
            ("/api/match/simple", {"cv_data": {}, "job_data": {}}),
        ]
        
        for endpoint, payload in invalid_requests:
            response = requests.post(
                f"{api_base_url}{endpoint}",
                headers=api_headers,
                json=payload
            )
            # Les erreurs doivent être gérées proprement
            assert response.status_code in [400, 422, 500]
            
            # La réponse doit contenir des informations sur l'erreur
            if response.headers.get("content-type", "").startswith("application/json"):
                error_data = response.json()
                assert "error" in error_data or "detail" in error_data
    
    def test_performance_benchmarks(self, api_base_url, api_headers, sample_cv_text):
        """Test des benchmarks de performance."""
        # Test de temps de réponse
        start_time = time.time()
        
        response = requests.post(
            f"{api_base_url}/api/parse-cv/text",
            headers=api_headers,
            json={"text": sample_cv_text}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code in [200, 202]
        
        # Le parsing ne devrait pas prendre plus de 30 secondes
        assert response_time < 30, f"Response time too slow: {response_time}s"
        
        # Log des performances
        print(f"CV parsing response time: {response_time:.2f}s")
    
    def test_data_consistency(self, api_base_url, api_headers, sample_cv_text):
        """Test de la cohérence des données."""
        # Parser le même CV plusieurs fois
        responses = []
        
        for _ in range(3):
            response = requests.post(
                f"{api_base_url}/api/parse-cv/text",
                headers=api_headers,
                json={"text": sample_cv_text}
            )
            assert response.status_code in [200, 202]
            responses.append(response.json())
        
        # Vérifier que les résultats sont cohérents
        first_result = responses[0]["parsed_data"]
        
        for result in responses[1:]:
            parsed_data = result["parsed_data"]
            
            # Le nom devrait être identique
            assert parsed_data["name"] == first_result["name"]
            
            # Les compétences principales devraient être similaires
            common_skills = set(first_result["skills"]) & set(parsed_data["skills"])
            assert len(common_skills) > 0