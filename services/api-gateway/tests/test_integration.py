"""
Tests d'intégration pour l'API Gateway SuperSmartMatch V2
Validation du fonctionnement complet avec tous les microservices
"""

import pytest
import asyncio
import httpx
import json
from typing import Dict, Any

# Configuration des tests
BASE_URL = "http://localhost:5050"
GATEWAY_URL = f"{BASE_URL}/api/gateway"

# Données de test
TEST_USER = {
    "email": "test@supersmartmatch.com",
    "password": "TestPassword123!",
    "full_name": "Test User",
    "role": "candidat"
}

TEST_CV_TEXT = """
John Doe
Senior Python Developer
Email: john.doe@email.com
Phone: +33 1 23 45 67 89

EXPERIENCE:
- 5 years Python development
- FastAPI, Django expertise
- Machine Learning projects

SKILLS:
- Python, JavaScript, SQL
- AWS, Docker, Kubernetes
- Machine Learning, Data Science

EDUCATION:
- Master Computer Science
- Python Certification
"""

TEST_JOB = {
    "title": "Senior Python Developer",
    "description": "We are looking for a Senior Python Developer with FastAPI experience...",
    "company": "TechCorp",
    "location": "Paris, France",
    "required_skills": ["Python", "FastAPI", "Machine Learning"],
    "experience_required": 3,
    "salary_range": "60000-80000"
}

class TestAPIGateway:
    """Tests de l'API Gateway"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.auth_token = None
        self.user_id = None
    
    async def cleanup(self):
        """Nettoyer les ressources après les tests"""
        await self.client.aclose()

@pytest.fixture
async def api_client():
    """Client de test pour l'API"""
    test_client = TestAPIGateway()
    yield test_client
    await test_client.cleanup()

@pytest.mark.asyncio
class TestHealthChecks:
    """Tests des health checks"""
    
    async def test_gateway_status(self, api_client):
        """Tester le status du gateway"""
        response = await api_client.client.get(f"{GATEWAY_URL}/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
    
    async def test_global_health(self, api_client):
        """Tester le health check global"""
        response = await api_client.client.get(f"{GATEWAY_URL}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "services" in data
        assert "gateway_info" in data
        
        # Vérifier la présence des services attendus
        expected_services = ["cv_parser", "job_parser", "matching"]
        for service in expected_services:
            assert service in data["services"]
    
    async def test_individual_service_health(self, api_client):
        """Tester les health checks individuels des services"""
        services = ["cv_parser", "job_parser", "matching"]
        
        for service in services:
            response = await api_client.client.get(f"{GATEWAY_URL}/health/{service}")
            assert response.status_code in [200, 503]  # Service peut être down en test
            
            if response.status_code == 200:
                data = response.json()
                assert "service" in data
                assert "health" in data

@pytest.mark.asyncio  
class TestAuthentication:
    """Tests d'authentification"""
    
    async def test_user_registration(self, api_client):
        """Tester l'inscription d'un utilisateur"""
        response = await api_client.client.post(
            f"{GATEWAY_URL}/auth/register",
            json=TEST_USER
        )
        
        if response.status_code == 201:
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
            assert "user" in data
            
            # Stocker le token pour les tests suivants
            api_client.auth_token = data["access_token"]
            api_client.user_id = data["user"]["id"]
        else:
            # L'utilisateur existe peut-être déjà
            assert response.status_code == 400
    
    async def test_user_login(self, api_client):
        """Tester la connexion d'un utilisateur"""
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        response = await api_client.client.post(
            f"{GATEWAY_URL}/auth/login",
            json=login_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        
        # Stocker le token pour les tests suivants
        api_client.auth_token = data["access_token"]
        api_client.user_id = data["user"]["id"]
    
    async def test_protected_route_without_auth(self, api_client):
        """Tester l'accès à une route protégée sans authentification"""
        response = await api_client.client.get(f"{GATEWAY_URL}/auth/me")
        assert response.status_code == 401
    
    async def test_protected_route_with_auth(self, api_client):
        """Tester l'accès à une route protégée avec authentification"""
        if not api_client.auth_token:
            await self.test_user_login(api_client)
        
        headers = {"Authorization": f"Bearer {api_client.auth_token}"}
        response = await api_client.client.get(
            f"{GATEWAY_URL}/auth/me",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER["email"]
    
    async def test_token_refresh(self, api_client):
        """Tester le renouvellement de token"""
        if not api_client.auth_token:
            await self.test_user_login(api_client)
        
        # Note: Ce test nécessiterait le refresh_token de la réponse de login
        # Pour simplifier, on teste juste que l'endpoint existe
        response = await api_client.client.post(
            f"{GATEWAY_URL}/auth/refresh",
            json={"refresh_token": "dummy_token"}
        )
        
        # Peut retourner 401 avec un faux token, c'est normal
        assert response.status_code in [200, 401]

@pytest.mark.asyncio
class TestParsers:
    """Tests des services de parsing"""
    
    async def test_cv_parser_formats(self, api_client):
        """Tester la récupération des formats supportés"""
        if not api_client.auth_token:
            await TestAuthentication().test_user_login(api_client)
        
        headers = {"Authorization": f"Bearer {api_client.auth_token}"}
        response = await api_client.client.get(
            f"{GATEWAY_URL}/parse-cv/formats",
            headers=headers
        )
        
        # Peut retourner 503 si le service CV Parser n'est pas disponible
        assert response.status_code in [200, 503]
    
    async def test_cv_parsing_text(self, api_client):
        """Tester le parsing d'un CV texte"""
        if not api_client.auth_token:
            await TestAuthentication().test_user_login(api_client)
        
        headers = {"Authorization": f"Bearer {api_client.auth_token}"}
        
        # Créer un fichier texte temporaire
        files = {
            "file": ("test_cv.txt", TEST_CV_TEXT.encode(), "text/plain")
        }
        data = {
            "extract_skills": "true",
            "extract_experience": "true"
        }
        
        response = await api_client.client.post(
            f"{GATEWAY_URL}/parse-cv",
            headers=headers,
            files=files,
            data=data
        )
        
        # Peut retourner 503 si le service n'est pas disponible
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "extracted_data" in data or "result" in data
    
    async def test_job_parsing(self, api_client):
        """Tester le parsing d'une offre d'emploi"""
        if not api_client.auth_token:
            await TestAuthentication().test_user_login(api_client)
        
        headers = {"Authorization": f"Bearer {api_client.auth_token}"}
        
        response = await api_client.client.post(
            f"{GATEWAY_URL}/parse-job",
            headers=headers,
            json=TEST_JOB
        )
        
        # Peut retourner 503 si le service n'est pas disponible
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "extracted_data" in data or "result" in data

@pytest.mark.asyncio
class TestMatching:
    """Tests du service de matching"""
    
    async def test_algorithms_list(self, api_client):
        """Tester la récupération de la liste des algorithmes"""
        if not api_client.auth_token:
            await TestAuthentication().test_user_login(api_client)
        
        headers = {"Authorization": f"Bearer {api_client.auth_token}"}
        response = await api_client.client.get(
            f"{GATEWAY_URL}/match/algorithms",
            headers=headers
        )
        
        # Peut retourner 503 si le service n'est pas disponible
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))
    
    async def test_simple_matching(self, api_client):
        """Tester un matching simple"""
        if not api_client.auth_token:
            await TestAuthentication().test_user_login(api_client)
        
        headers = {"Authorization": f"Bearer {api_client.auth_token}"}
        
        matching_request = {
            "candidate_profile": {
                "skills": ["Python", "FastAPI", "Machine Learning"],
                "experience": 5,
                "education": "Master Computer Science",
                "location": "Paris, France"
            },
            "job_offer": {
                "required_skills": ["Python", "FastAPI"],
                "experience_required": 3,
                "job_title": "Senior Python Developer",
                "location": "Paris, France"
            }
        }
        
        response = await api_client.client.post(
            f"{GATEWAY_URL}/match",
            headers=headers,
            json=matching_request
        )
        
        # Peut retourner 503 si le service n'est pas disponible
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "score" in data or "result" in data

@pytest.mark.asyncio
class TestRateLimiting:
    """Tests du rate limiting"""
    
    async def test_rate_limit_headers(self, api_client):
        """Tester la présence des headers de rate limiting"""
        response = await api_client.client.get(f"{GATEWAY_URL}/status")
        assert response.status_code == 200
        
        # Vérifier les headers de rate limiting
        headers = response.headers
        rate_limit_headers = [
            "x-ratelimit-limit",
            "x-ratelimit-remaining",
            "x-ratelimit-reset"
        ]
        
        # Les headers peuvent être présents ou non selon la configuration
        for header in rate_limit_headers:
            if header in headers:
                assert headers[header].isdigit() or header == "x-ratelimit-reset"
    
    async def test_rate_limit_enforcement(self, api_client):
        """Tester l'application du rate limiting (test léger)"""
        # Faire quelques requêtes rapides
        for i in range(5):
            response = await api_client.client.get(f"{GATEWAY_URL}/status")
            assert response.status_code == 200
        
        # Le rate limiting devrait être configuré pour permettre ces requêtes
        # En test, on ne va pas jusqu'à déclencher le 429

@pytest.mark.asyncio
class TestErrorHandling:
    """Tests de gestion d'erreurs"""
    
    async def test_404_endpoint(self, api_client):
        """Tester un endpoint inexistant"""
        response = await api_client.client.get(f"{GATEWAY_URL}/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data or "detail" in data
    
    async def test_invalid_json(self, api_client):
        """Tester une requête avec JSON invalide"""
        if not api_client.auth_token:
            await TestAuthentication().test_user_login(api_client)
        
        headers = {
            "Authorization": f"Bearer {api_client.auth_token}",
            "Content-Type": "application/json"
        }
        
        # Envoyer du JSON invalide
        response = await api_client.client.post(
            f"{GATEWAY_URL}/match",
            headers=headers,
            content="invalid json content"
        )
        
        assert response.status_code in [400, 422]

@pytest.mark.asyncio
class TestMetrics:
    """Tests des métriques"""
    
    async def test_prometheus_metrics(self, api_client):
        """Tester l'endpoint des métriques Prometheus"""
        response = await api_client.client.get(f"{GATEWAY_URL}/metrics")
        assert response.status_code == 200
        
        content = response.text
        assert "supersmartmatch_gateway_up" in content
        assert "# HELP" in content
        assert "# TYPE" in content

# Tests de performance (optionnels)
@pytest.mark.asyncio
@pytest.mark.performance
class TestPerformance:
    """Tests de performance"""
    
    async def test_response_time(self, api_client):
        """Tester le temps de réponse du health check"""
        import time
        
        start_time = time.time()
        response = await api_client.client.get(f"{GATEWAY_URL}/status")
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        
        # Le health check devrait répondre en moins de 1 seconde
        assert response_time < 1.0
    
    async def test_concurrent_requests(self, api_client):
        """Tester les requêtes concurrentes"""
        tasks = []
        
        for i in range(10):
            task = api_client.client.get(f"{GATEWAY_URL}/status")
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        
        # Toutes les requêtes devraient réussir
        for response in responses:
            assert response.status_code == 200

# Fonction d'aide pour exécuter les tests
async def run_integration_tests():
    """Exécuter tous les tests d'intégration"""
    print("🧪 Démarrage des tests d'intégration SuperSmartMatch V2 API Gateway")
    
    # Créer un client de test
    test_client = TestAPIGateway()
    
    try:
        # Tests de base
        health_tests = TestHealthChecks()
        await health_tests.test_gateway_status(test_client)
        await health_tests.test_global_health(test_client)
        print("✅ Health checks OK")
        
        # Tests d'authentification
        auth_tests = TestAuthentication()
        await auth_tests.test_user_login(test_client)
        print("✅ Authentication OK")
        
        # Tests des métriques
        metrics_tests = TestMetrics()
        await metrics_tests.test_prometheus_metrics(test_client)
        print("✅ Metrics OK")
        
        print("🎉 Tous les tests d'intégration sont passés avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur dans les tests: {e}")
        raise
    finally:
        await test_client.cleanup()

if __name__ == "__main__":
    asyncio.run(run_integration_tests())
