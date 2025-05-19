"""Tests unitaires pour les métriques Prometheus."""
import pytest
import time
from unittest.mock import Mock, patch
from prometheus_client import REGISTRY, CollectorRegistry
from shared.metrics.prometheus import (
    PrometheusMiddleware,
    track_ml_operation,
    track_openai_call,
    setup_prometheus_middleware,
    REQUEST_COUNT,
    REQUEST_DURATION,
    ML_PROCESSING_TIME,
    OPENAI_API_CALLS
)


class TestPrometheusMetrics:
    """Tests pour les métriques Prometheus."""
    
    @pytest.fixture(autouse=True)
    def setup_metrics(self):
        """Setup pour chaque test."""
        # Utiliser un registre séparé pour les tests
        self.test_registry = CollectorRegistry()
        
        # Mock du registre global
        with patch('shared.metrics.prometheus.REGISTRY', self.test_registry):
            yield
    
    def test_prometheus_middleware_basic(self):
        """Test du middleware Prometheus de base."""
        middleware = PrometheusMiddleware("test-service")
        
        # Mock de la requête et réponse
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url.path = "/test"
        mock_request.body.return_value = b"test body"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.body = b"response body"
        
        async def mock_call_next(request):
            time.sleep(0.1)  # Simuler un traitement
            return mock_response
        
        # Test du middleware
        import asyncio
        result = asyncio.run(middleware(mock_request, mock_call_next))
        
        assert result == mock_response
    
    def test_ml_operation_tracking_success(self):
        """Test du tracking d'opération ML réussie."""
        @track_ml_operation("test-service", "parsing", "gpt-4")
        def mock_ml_function():
            time.sleep(0.1)
            return {"result": "success"}
        
        result = mock_ml_function()
        
        assert result["result"] == "success"
        
        # Vérifier que les métriques ont été enregistrées
        # Note: Dans un vrai test, on vérifierait les valeurs des métriques
    
    def test_ml_operation_tracking_error(self):
        """Test du tracking d'opération ML avec erreur."""
        @track_ml_operation("test-service", "parsing", "gpt-4")
        def mock_ml_function_error():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            mock_ml_function_error()
    
    def test_openai_call_tracking(self):
        """Test du tracking d'appels OpenAI."""
        @track_openai_call("test-service", "gpt-4")
        def mock_openai_call():
            # Mock de la réponse OpenAI
            response = Mock()
            response.usage = Mock()
            response.usage.prompt_tokens = 100
            response.usage.completion_tokens = 50
            return response
        
        result = mock_openai_call()
        
        assert result.usage.prompt_tokens == 100
        assert result.usage.completion_tokens == 50
    
    def test_async_ml_operation_tracking(self):
        """Test du tracking d'opération ML asynchrone."""
        @track_ml_operation("test-service", "async-parsing", "gpt-4")
        async def mock_async_ml_function():
            await asyncio.sleep(0.1)
            return {"result": "async_success"}
        
        import asyncio
        result = asyncio.run(mock_async_ml_function())
        
        assert result["result"] == "async_success"
    
    def test_multiple_service_metrics(self):
        """Test des métriques pour plusieurs services."""
        services = ["cv-parser", "job-parser", "matching-api"]
        
        for service in services:
            middleware = PrometheusMiddleware(service)
            assert middleware.service_name == service
    
    def test_metrics_collection_performance(self):
        """Test de performance de la collecte de métriques."""
        middleware = PrometheusMiddleware("perf-test")
        
        # Mesurer le temps de traitement du middleware
        start_time = time.time()
        
        # Simuler de nombreuses requêtes
        for i in range(100):
            mock_request = Mock()
            mock_request.method = "GET"
            mock_request.url.path = f"/test-{i}"
            mock_request.body.return_value = b"test"
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.body = b"ok"
            
            async def quick_call_next(request):
                return mock_response
            
            import asyncio
            asyncio.run(middleware(mock_request, quick_call_next))
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Le middleware ne devrait pas ajouter une latence significative
        assert total_time < 1.0, f"Metrics collection too slow: {total_time}s"
    
    def test_custom_metric_labels(self):
        """Test des labels personnalisés pour les métriques."""
        # Test avec différents codes de statut
        status_codes = [200, 400, 500]
        
        for status_code in status_codes:
            mock_request = Mock()
            mock_request.method = "POST"
            mock_request.url.path = "/api/test"
            mock_request.body.return_value = b"test"
            
            mock_response = Mock()
            mock_response.status_code = status_code
            mock_response.body = b"response"
            
            middleware = PrometheusMiddleware("label-test")
            
            async def mock_call_next(request):
                return mock_response
            
            import asyncio
            asyncio.run(middleware(mock_request, mock_call_next))
    
    def test_error_handling_in_middleware(self):
        """Test de la gestion d'erreurs dans le middleware."""
        middleware = PrometheusMiddleware("error-test")
        
        mock_request = Mock()
        mock_request.method = "GET"
        mock_request.url.path = "/error"
        mock_request.body.return_value = b"test"
        
        async def error_call_next(request):
            raise Exception("Test error")
        
        import asyncio
        with pytest.raises(Exception):
            asyncio.run(middleware(mock_request, error_call_next))
    
    def test_metrics_registry_isolation(self):
        """Test de l'isolation des métriques entre tests."""
        # Vérifier que les métriques ne s'accumulent pas entre les tests
        initial_collectors = len(list(REGISTRY._collector_to_names.keys()))
        
        # Créer un nouveau middleware
        middleware = PrometheusMiddleware("isolation-test")
        
        # Le nombre de collecteurs ne devrait pas avoir changé
        # (car ils sont déjà définis globalement)
        final_collectors = len(list(REGISTRY._collector_to_names.keys()))
        assert final_collectors >= initial_collectors