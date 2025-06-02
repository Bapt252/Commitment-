#!/usr/bin/env python3
"""
🧪 SuperSmartMatch V2 - Tests Unitaires et d'Intégration

Tests complets pour valider :
- Sélection intelligente d'algorithme  
- Intégration services externes (Nexten, V1)
- Circuit breakers et fallbacks
- Cache Redis et performance
- API endpoints et validation
"""

import pytest
import asyncio
import json
import time
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

# Imports du service à tester
import sys
import os
sys.path.append('.')

# Mock des imports pour les tests
with patch.dict('sys.modules', {
    'aiohttp': MagicMock(),
    'redis.asyncio': MagicMock(),
    'fastapi': MagicMock(),
    'uvicorn': MagicMock()
}):
    from supersmartmatch_v2_unified_service import (
        SuperSmartMatchV2UnifiedService,
        IntelligentAlgorithmSelector, 
        AlgorithmType,
        MatchRequest,
        MatchResult,
        DataAdapter,
        CircuitBreaker
    )

class TestIntelligentAlgorithmSelector:
    """Tests du sélecteur intelligent d'algorithme"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.selector = IntelligentAlgorithmSelector()
    
    def test_select_nexten_for_complete_questionnaire(self):
        """Test sélection Nexten pour questionnaires complets"""
        request = MatchRequest(
            candidate={
                "name": "John Doe",
                "technical_skills": ["Python", "Machine Learning"],
                "experiences": [{"duration_months": 24}]
            },
            offers=[{"id": "1", "title": "ML Engineer"}],
            candidate_questionnaire={
                "work_style": "collaborative",
                "culture_preferences": "innovation",
                "remote_preference": "hybrid",
                "team_size_preference": "small",
                "management_style": "agile",
                "career_goals": "tech_lead"
            }
        )
        
        algorithm, reason = self.selector.select_algorithm(request)
        assert algorithm == AlgorithmType.NEXTEN
        assert "questionnaires complets" in reason.lower()
    
    def test_select_smart_for_location_constraints(self):
        """Test sélection Smart pour contraintes géographiques"""
        request = MatchRequest(
            candidate={
                "name": "Jane Smith",
                "localisation": "Paris",
                "technical_skills": ["JavaScript", "React"],
                "mobility": True
            },
            offers=[
                {"id": "1", "title": "Frontend Dev", "localisation": "Lyon"},
                {"id": "2", "title": "Backend Dev", "localisation": "Marseille"}
            ]
        )
        
        # Simuler circuit breaker Nexten ouvert
        self.selector.metrics["nexten"].circuit_breaker_open = True
        
        algorithm, reason = self.selector.select_algorithm(request)
        assert algorithm == AlgorithmType.SMART_MATCH
        assert "géographiques" in reason.lower()
    
    def test_select_enhanced_for_senior_profile(self):
        """Test sélection Enhanced pour profils séniors"""
        request = MatchRequest(
            candidate={
                "name": "Senior Dev",
                "technical_skills": ["Java", "Architecture"],
                "experiences": [
                    {"duration_months": 36},  # 3 ans
                    {"duration_months": 48},  # 4 ans
                    {"duration_months": 24}   # 2 ans = 9 ans total
                ]
            },
            offers=[{"id": "1", "title": "Tech Lead"}]
        )
        
        # Simuler circuits breakers fermés sauf enhanced
        self.selector.metrics["nexten"].circuit_breaker_open = True
        self.selector.metrics["smart"].circuit_breaker_open = True
        
        algorithm, reason = self.selector.select_algorithm(request)
        assert algorithm == AlgorithmType.ENHANCED
        assert "sénior" in reason.lower()
    
    def test_select_semantic_for_complex_skills(self):
        """Test sélection Semantic pour compétences complexes"""
        request = MatchRequest(
            candidate={
                "name": "AI Specialist",
                "technical_skills": [
                    "Machine Learning",
                    "Deep Learning", 
                    "Neural Networks",
                    "Computer Vision",
                    "Natural Language Processing",
                    "TensorFlow",
                    "PyTorch"
                ]
            },
            offers=[{"id": "1", "title": "AI Engineer"}]
        )
        
        # Simuler autres algorithmes indisponibles
        for algo in ["nexten", "smart", "enhanced"]:
            self.selector.metrics[algo].circuit_breaker_open = True
        
        algorithm, reason = self.selector.select_algorithm(request)
        assert algorithm == AlgorithmType.SEMANTIC
        assert "sémantique" in reason.lower()
    
    def test_fallback_hierarchy(self):
        """Test hiérarchie de fallback"""
        request = MatchRequest(
            candidate={"name": "Test"},
            offers=[{"id": "1", "title": "Test Job"}]
        )
        
        # Simuler tous les algorithmes principaux fermés
        for algo in ["nexten", "smart", "enhanced", "semantic"]:
            self.selector.metrics[algo].circuit_breaker_open = True
        
        algorithm, reason = self.selector.select_algorithm(request)
        assert algorithm == AlgorithmType.BASIC
        assert "fallback" in reason.lower()
    
    def test_skills_complexity_calculation(self):
        """Test calcul complexité des compétences"""
        # Compétences simples
        simple_skills = ["HTML", "CSS", "JavaScript"]
        simple_score = self.selector._calculate_skills_complexity(simple_skills)
        assert simple_score < 0.3
        
        # Compétences complexes
        complex_skills = [
            "Machine Learning", "Deep Learning", "AI", 
            "Computer Vision", "NLP", "Data Science"
        ]
        complex_score = self.selector._calculate_skills_complexity(complex_skills)
        assert complex_score > 0.7
    
    def test_context_analysis(self):
        """Test analyse du contexte"""
        request = MatchRequest(
            candidate={
                "technical_skills": ["Python", "Machine Learning"],
                "localisation": "Paris",
                "experiences": [{"duration_months": 48}]
            },
            offers=[
                {"id": "1", "localisation": "Lyon"},
                {"id": "2", "localisation": "Marseille"}
            ],
            candidate_questionnaire={
                "work_style": "collaborative",
                "remote_preference": "hybrid"
            }
        )
        
        context = self.selector._analyze_context(request)
        
        assert context["has_location_constraints"] == True
        assert context["offers_count"] == 2
        assert context["experience_years"] == 4.0
        assert context["questionnaire_completeness"] > 0

class TestDataAdapter:
    """Tests de l'adaptateur de données"""
    
    def test_to_nexten_format(self):
        """Test conversion vers format Nexten"""
        request = MatchRequest(
            candidate={"name": "John", "skills": ["Python"]},
            offers=[{"id": "1", "title": "Dev"}],
            candidate_questionnaire={"work_style": "agile"}
        )
        
        nexten_data = DataAdapter.to_nexten_format(request)
        
        assert "candidate" in nexten_data
        assert "jobs" in nexten_data
        assert nexten_data["candidate"]["questionnaire"]["work_style"] == "agile"
        assert len(nexten_data["jobs"]) == 1
    
    def test_to_v1_format(self):
        """Test conversion vers format V1"""
        request = MatchRequest(
            candidate={"name": "Jane"},
            offers=[{"id": "1"}, {"id": "2"}],
            algorithm="smart"
        )
        
        v1_data = DataAdapter.to_v1_format(request)
        
        assert "cv_data" in v1_data
        assert "job_data" in v1_data
        assert v1_data["algorithm"] == "smart"
        assert len(v1_data["job_data"]) == 2
    
    def test_from_nexten_response(self):
        """Test conversion depuis réponse Nexten"""
        nexten_response = {
            "matches": [
                {
                    "job_id": "job_123",
                    "compatibility_score": 0.85,
                    "confidence": 0.9,
                    "skills_match": 0.95,
                    "experience_match": 0.8,
                    "insights": ["Excellent tech match"],
                    "explanation": "Great fit"
                }
            ]
        }
        
        matches = DataAdapter.from_nexten_response(nexten_response)
        
        assert len(matches) == 1
        assert matches[0].offer_id == "job_123"
        assert matches[0].overall_score == 0.85
        assert matches[0].skill_match_score == 0.95
    
    def test_from_v1_response(self):
        """Test conversion depuis réponse V1"""
        v1_response = {
            "matches": [
                {
                    "offer_id": "offer_456", 
                    "score": 0.78,
                    "confidence": 0.82,
                    "details": {
                        "skill_match": 0.85,
                        "experience_match": 0.7
                    }
                }
            ]
        }
        
        matches = DataAdapter.from_v1_response(v1_response)
        
        assert len(matches) == 1
        assert matches[0].offer_id == "offer_456"
        assert matches[0].overall_score == 0.78
        assert matches[0].skill_match_score == 0.85

class TestCircuitBreaker:
    """Tests du circuit breaker"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        self.circuit_breaker = CircuitBreaker(threshold=3, timeout=1)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_normal_operation(self):
        """Test fonctionnement normal"""
        async def success_func():
            return "success"
        
        result = await self.circuit_breaker.call(success_func)
        assert result == "success"
        assert self.circuit_breaker.state == "CLOSED"
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """Test ouverture après échecs répétés"""
        async def failing_func():
            raise Exception("Service unavailable")
        
        # Générer assez d'échecs pour ouvrir le circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await self.circuit_breaker.call(failing_func)
        
        assert self.circuit_breaker.state == "OPEN"
        
        # Tentative d'appel avec circuit ouvert
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await self.circuit_breaker.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self):
        """Test récupération via état HALF_OPEN"""
        async def failing_func():
            raise Exception("Fail")
        
        async def success_func():
            return "recovered"
        
        # Ouvrir le circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await self.circuit_breaker.call(failing_func)
        
        assert self.circuit_breaker.state == "OPEN"
        
        # Attendre timeout et tester récupération
        await asyncio.sleep(1.1)  # Dépasser le timeout
        
        result = await self.circuit_breaker.call(success_func)
        assert result == "recovered"
        assert self.circuit_breaker.state == "CLOSED"

@pytest.mark.asyncio
class TestSuperSmartMatchV2UnifiedService:
    """Tests du service unifié complet"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        with patch('redis.asyncio.from_url'), \
             patch('aiohttp.ClientSession'):
            self.service = SuperSmartMatchV2UnifiedService()
    
    async def test_service_initialization(self):
        """Test initialisation du service"""
        with patch.object(self.service, 'redis_client') as mock_redis:
            mock_redis.ping = AsyncMock()
            await self.service.initialize()
            mock_redis.ping.assert_called_once()
    
    async def test_cache_operations(self):
        """Test opérations de cache"""
        # Mock Redis client
        mock_redis = AsyncMock()
        self.service.redis_client = mock_redis
        
        # Test cache miss
        mock_redis.get.return_value = None
        result = await self.service._get_from_cache("test_key")
        assert result is None
        
        # Test cache hit
        cached_response = {
            "success": True,
            "matches": [],
            "algorithm_used": "test",
            "execution_time_ms": 100.0,
            "selection_reason": "test"
        }
        mock_redis.get.return_value = json.dumps(cached_response)
        
        result = await self.service._get_from_cache("test_key")
        assert result is not None
        assert result.algorithm_used == "test"
    
    async def test_basic_fallback_algorithm(self):
        """Test algorithme de fallback basique"""
        request = MatchRequest(
            candidate={
                "technical_skills": ["Python", "Django"],
                "competences": ["React"]
            },
            offers=[
                {
                    "id": "1",
                    "title": "Python Developer", 
                    "required_skills": ["Python", "Flask"]
                },
                {
                    "id": "2",
                    "title": "Frontend Developer",
                    "required_skills": ["React", "JavaScript"]
                }
            ]
        )
        
        matches = await self.service._call_basic_fallback(request)
        
        assert len(matches) >= 1
        assert all(isinstance(match, MatchResult) for match in matches)
        # Le premier match devrait avoir un score > 0 (Python match)
        assert matches[0].overall_score > 0
    
    async def test_fallback_hierarchy_execution(self):
        """Test exécution de la hiérarchie de fallback"""
        request = MatchRequest(
            candidate={"name": "Test"},
            offers=[{"id": "1", "title": "Test"}]
        )
        
        # Mock tous les algorithmes externes pour échouer
        with patch.object(self.service, '_call_nexten_matcher', side_effect=Exception("Nexten down")), \
             patch.object(self.service, '_call_supersmartmatch_v1', side_effect=Exception("V1 down")):
            
            matches, algorithm_used = await self.service._execute_with_fallback(
                AlgorithmType.NEXTEN, request
            )
            
            # Devrait fallback vers basic
            assert algorithm_used == "basic"
            assert len(matches) >= 0
    
    def test_cache_key_generation(self):
        """Test génération de clés de cache"""
        request = MatchRequest(
            candidate={"name": "John"},
            offers=[{"id": "1"}],
            algorithm="nexten"
        )
        
        key1 = self.service._generate_cache_key(request)
        key2 = self.service._generate_cache_key(request)
        
        # Même requête = même clé
        assert key1 == key2
        assert key1.startswith("supersmartmatch_v2:")
        
        # Requête différente = clé différente
        request.algorithm = "smart"
        key3 = self.service._generate_cache_key(request)
        assert key1 != key3

# Tests d'intégration avec mocks
class TestIntegrationWithMocks:
    """Tests d'intégration avec services externes mockés"""
    
    @pytest.mark.asyncio
    async def test_nexten_integration_success(self):
        """Test intégration Nexten réussie"""
        service = SuperSmartMatchV2UnifiedService()
        
        # Mock réponse Nexten
        mock_response = {
            "matches": [
                {
                    "job_id": "job_123",
                    "compatibility_score": 0.92,
                    "confidence": 0.88,
                    "skills_match": 0.95,
                    "insights": ["Excellent match"]
                }
            ]
        }
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response_obj = AsyncMock()
            mock_response_obj.status = 200
            mock_response_obj.json.return_value = mock_response
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response_obj
            
            request = MatchRequest(
                candidate={"name": "Test"},
                offers=[{"id": "job_123", "title": "Test"}]
            )
            
            matches = await service._call_nexten_matcher(request)
            
            assert len(matches) == 1
            assert matches[0].offer_id == "job_123"
            assert matches[0].overall_score == 0.92
    
    @pytest.mark.asyncio
    async def test_v1_integration_success(self):
        """Test intégration V1 réussie"""
        service = SuperSmartMatchV2UnifiedService()
        
        # Mock réponse V1
        mock_response = {
            "matches": [
                {
                    "offer_id": "offer_456",
                    "score": 0.85,
                    "confidence": 0.9,
                    "details": {"skill_match": 0.88}
                }
            ]
        }
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response_obj = AsyncMock()
            mock_response_obj.status = 200
            mock_response_obj.json.return_value = mock_response
            
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response_obj
            
            request = MatchRequest(
                candidate={"name": "Test"},
                offers=[{"id": "offer_456", "title": "Test"}]
            )
            
            matches = await service._call_supersmartmatch_v1(request, "smart")
            
            assert len(matches) == 1
            assert matches[0].offer_id == "offer_456"
            assert matches[0].overall_score == 0.85

# Tests de performance
class TestPerformance:
    """Tests de performance et benchmarks"""
    
    @pytest.mark.asyncio
    async def test_response_time_basic_fallback(self):
        """Test temps de réponse de l'algorithme basique"""
        service = SuperSmartMatchV2UnifiedService()
        
        request = MatchRequest(
            candidate={"technical_skills": ["Python"] * 10},
            offers=[{"id": str(i), "required_skills": ["Python"]} for i in range(50)]
        )
        
        start_time = time.time()
        matches = await service._call_basic_fallback(request)
        execution_time = (time.time() - start_time) * 1000
        
        # L'algorithme basique devrait être très rapide
        assert execution_time < 100  # < 100ms
        assert len(matches) <= 10  # Limité à 10 résultats
    
    def test_algorithm_metrics_update(self):
        """Test mise à jour des métriques"""
        selector = IntelligentAlgorithmSelector()
        
        # Test succès
        selector.update_metrics("nexten", True, 75.5)
        metrics = selector.metrics["nexten"]
        
        assert metrics.total_requests == 1
        assert metrics.successful_requests == 1
        assert metrics.failed_requests == 0
        assert metrics.avg_response_time_ms == 75.5
        
        # Test échec
        selector.update_metrics("nexten", False, 150.0)
        assert metrics.total_requests == 2
        assert metrics.failed_requests == 1

if __name__ == "__main__":
    # Exécution des tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10"
    ])
