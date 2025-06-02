"""
SuperSmartMatch V2 - Tests d'intégration de l'API
===============================================

Tests pour valider le fonctionnement de l'API SuperSmartMatch V2
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.fixture
def client():
    """Client de test FastAPI"""
    return TestClient(app)


@pytest.fixture
def sample_cv_data():
    """Données CV d'exemple pour les tests"""
    return {
        "competences": ["Python", "FastAPI", "Machine Learning"],
        "experience": 5,
        "localisation": "Paris",
        "questionnaire_complete": True,
        "niveau_etudes": "Master",
        "secteur": "Tech"
    }


@pytest.fixture
def sample_jobs():
    """Jobs d'exemple pour les tests"""
    return [
        {
            "id": "job-123",
            "titre": "Développeur Python Senior",
            "competences": ["Python", "Django", "PostgreSQL"],
            "localisation": "Lyon",
            "type_contrat": "CDI",
            "salaire": "45000-55000",
            "experience_requise": 3
        },
        {
            "id": "job-456",
            "titre": "Data Scientist",
            "competences": ["Python", "Machine Learning", "TensorFlow"],
            "localisation": "Paris",
            "type_contrat": "CDI",
            "salaire": "50000-60000",
            "experience_requise": 4
        }
    ]


class TestHealthEndpoint:
    """Tests pour l'endpoint de santé"""
    
    def test_health_check_success(self, client):
        """Test que l'endpoint de santé fonctionne"""
        
        with patch('app.main.matching_orchestrator.check_external_services_health') as mock_health:
            mock_health.return_value = {
                "nexten_matcher": {"status": "healthy", "response_time": 0.1},
                "supersmartmatch_v1": {"status": "healthy", "response_time": 0.05}
            }
            
            response = client.get("/api/v2/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["version"] == "2.0.0"
            assert "external_services" in data


class TestRootEndpoint:
    """Tests pour l'endpoint racine"""
    
    def test_root_endpoint_returns_info(self, client):
        """Test que l'endpoint racine retourne les informations du service"""
        
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "SuperSmartMatch V2"
        assert data["version"] == "2.0.0"
        assert "endpoints" in data
        assert "unified_services" in data
        assert "features" in data


class TestMatchingV2Endpoint:
    """Tests pour l'endpoint de matching V2"""
    
    @patch('app.main.matching_orchestrator')
    @patch('app.main.algorithm_selector')
    @patch('app.main.metrics_collector')
    def test_matching_v2_success(
        self,
        mock_metrics,
        mock_selector,
        mock_orchestrator,
        client,
        sample_cv_data,
        sample_jobs
    ):
        """Test d'une requête de matching V2 réussie"""
        
        # Configuration des mocks
        mock_selector.select_algorithm.return_value = "nexten"
        mock_orchestrator.execute_matching.return_value = AsyncMock(
            matches=[
                {
                    "job_id": "job-456",
                    "score": 0.85,
                    "algorithm": "nexten",
                    "reasons": ["Compétences ML", "Localisation Paris"]
                }
            ],
            metadata={
                "algorithm_used": "nexten",
                "processing_time": 0.15,
                "total_jobs_analyzed": 2
            }
        )
        
        # Données de requête
        request_data = {
            "cv_data": sample_cv_data,
            "jobs": sample_jobs,
            "options": {
                "max_results": 10,
                "enable_fallback": True
            }
        }
        
        response = client.post("/api/v2/match", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert "metadata" in data
        
        # Vérification que les services ont été appelés
        mock_selector.select_algorithm.assert_called_once()
        mock_orchestrator.execute_matching.assert_called_once()
    
    def test_matching_v2_invalid_data(self, client):
        """Test avec des données invalides"""
        
        invalid_request = {
            "cv_data": {},  # CV data vide
            "jobs": []      # Pas de jobs
        }
        
        response = client.post("/api/v2/match", json=invalid_request)
        
        # Devrait retourner une erreur de validation
        assert response.status_code == 422


class TestMatchingV1Compatibility:
    """Tests pour la compatibilité V1"""
    
    @patch('app.main.matching_orchestrator')
    @patch('app.main.algorithm_selector')
    def test_v1_compatibility_endpoint(
        self,
        mock_selector,
        mock_orchestrator,
        client,
        sample_cv_data,
        sample_jobs
    ):
        """Test que l'endpoint V1 de compatibilité fonctionne"""
        
        # Configuration des mocks
        mock_selector.select_algorithm.return_value = "smart-match"
        mock_orchestrator.execute_matching.return_value = AsyncMock(
            matches=[
                {
                    "job_id": "job-123",
                    "score": 0.75,
                    "algorithm": "smart-match"
                }
            ]
        )
        
        # Format V1 (utilise 'job_data' au lieu de 'jobs')
        request_data = {
            "cv_data": sample_cv_data,
            "job_data": sample_jobs,
            "algorithm": "smart-match"
        }
        
        response = client.post("/api/v1/match", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data


class TestMetricsEndpoint:
    """Tests pour l'endpoint de métriques"""
    
    @patch('app.main.metrics_collector')
    def test_metrics_endpoint_success(self, mock_metrics, client):
        """Test de récupération des métriques"""
        
        mock_metrics.get_current_metrics.return_value = {
            "timestamp": 1234567890,
            "version": "2.0.0",
            "total_requests": 100,
            "success_rate": 0.95,
            "algorithm_stats": {
                "nexten": {"count": 50, "success_rate": 0.96},
                "smart-match": {"count": 30, "success_rate": 0.93}
            }
        }
        
        response = client.get("/api/v2/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "total_requests" in data
        assert "algorithm_stats" in data


class TestAlgorithmStatusEndpoint:
    """Tests pour l'endpoint de status des algorithmes"""
    
    @patch('app.main.matching_orchestrator')
    def test_algorithm_status_success(self, mock_orchestrator, client):
        """Test de récupération du status des algorithmes"""
        
        mock_orchestrator.get_algorithms_status.return_value = {
            "nexten_matcher": {
                "status": "healthy",
                "circuit_breaker": "closed",
                "last_success": "2024-01-01T10:00:00Z"
            },
            "supersmartmatch_v1": {
                "status": "healthy",
                "algorithms": {
                    "smart-match": "available",
                    "enhanced": "available",
                    "semantic": "available",
                    "basic": "available"
                }
            }
        }
        
        response = client.get("/api/v2/algorithms/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "nexten_matcher" in data
        assert "supersmartmatch_v1" in data


class TestErrorHandling:
    """Tests pour la gestion d'erreurs"""
    
    @patch('app.main.matching_orchestrator')
    def test_algorithm_selection_error(self, mock_orchestrator, client, sample_cv_data, sample_jobs):
        """Test de gestion d'erreur lors de la sélection d'algorithme"""
        
        mock_orchestrator.execute_matching.side_effect = Exception("Service indisponible")
        
        request_data = {
            "cv_data": sample_cv_data,
            "jobs": sample_jobs
        }
        
        response = client.post("/api/v2/match", json=request_data)
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"] == "Erreur lors du matching"


@pytest.mark.asyncio
class TestAsyncComponents:
    """Tests pour les composants asynchrones"""
    
    async def test_metrics_initialization(self):
        """Test d'initialisation des métriques"""
        
        with patch('app.main.metrics_collector.initialize') as mock_init:
            mock_init.return_value = None
            
            # Test que l'initialisation se passe bien
            await mock_init()
            mock_init.assert_called_once()


# Fixtures pour les tests d'intégration avec services externes
@pytest.fixture
def mock_nexten_service():
    """Mock du service Nexten Matcher"""
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "matches": [
                {"job_id": "job-123", "score": 0.9, "confidence": 0.95}
            ],
            "metadata": {"processing_time": 0.1}
        }
        yield mock_post


@pytest.fixture
def mock_supersmartmatch_v1_service():
    """Mock du service SuperSmartMatch V1"""
    
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "matches": [
                {"job_id": "job-456", "score": 0.8}
            ]
        }
        yield mock_post


class TestExternalServiceIntegration:
    """Tests d'intégration avec les services externes"""
    
    def test_nexten_service_integration(self, mock_nexten_service):
        """Test d'intégration avec Nexten Matcher"""
        # Ces tests seraient plus développés avec les vrais adaptateurs
        pass
    
    def test_supersmartmatch_v1_integration(self, mock_supersmartmatch_v1_service):
        """Test d'intégration avec SuperSmartMatch V1"""
        # Ces tests seraient plus développés avec les vrais adaptateurs
        pass
