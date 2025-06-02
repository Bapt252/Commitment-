#!/usr/bin/env python3
"""
SuperSmartMatch V2 - Test Suite
Comprehensive unit and integration tests for the unified matching service

🧪 Test Coverage:
- Algorithm selection logic
- External service integration
- Circuit breaker functionality  
- API endpoints
- Fallback mechanisms
- Data validation
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from httpx import AsyncClient
import json
import time

# Import the main application
import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import (
    app, service, SuperSmartMatchV2, IntelligentAlgorithmSelector,
    AlgorithmType, MatchRequest, Candidate, TechnicalSkill, Experience, 
    Offer, CandidateQuestionnaire, CircuitBreaker, CircuitBreakerState
)

# =================== FIXTURES ===================

@pytest.fixture
def sample_candidate():
    """Sample candidate for testing"""
    return Candidate(
        name="John Doe",
        email="john@example.com",
        technical_skills=[
            TechnicalSkill(name="Python", level="Expert", years=5),
            TechnicalSkill(name="Machine Learning", level="Advanced", years=3),
            TechnicalSkill(name="Docker", level="Intermediate", years=2)
        ],
        experiences=[
            Experience(
                title="Senior Developer",
                company="TechCorp",
                duration_months=24,
                skills=["Python", "Django", "PostgreSQL"]
            ),
            Experience(
                title="ML Engineer",
                company="AI Startup", 
                duration_months=18,
                skills=["Python", "TensorFlow", "AWS"]
            )
        ]
    )

@pytest.fixture
def sample_offers():
    """Sample job offers for testing"""
    return [
        Offer(
            id="job_123",
            title="ML Engineer",
            company="AI Company",
            required_skills=["Python", "TensorFlow", "Machine Learning"],
            description="Building ML models for recommendation systems"
        ),
        Offer(
            id="job_456", 
            title="Backend Developer",
            company="Web Corp",
            required_skills=["Python", "Django", "PostgreSQL"],
            description="Developing scalable web applications"
        ),
        Offer(
            id="job_789",
            title="Data Scientist",
            company="Analytics Inc",
            required_skills=["Python", "Machine Learning", "Statistics"],
            description="Analyzing large datasets for business insights"
        )
    ]

@pytest.fixture
def complete_questionnaire():
    """Complete candidate questionnaire for testing"""
    return CandidateQuestionnaire(
        work_style="collaborative",
        culture_preferences="innovation_focused",
        remote_preference="hybrid",
        career_goals="technical_leadership",
        team_size_preference="small"
    )

@pytest.fixture
def sample_match_request(sample_candidate, sample_offers, complete_questionnaire):
    """Complete match request for testing"""
    return MatchRequest(
        candidate=sample_candidate,
        candidate_questionnaire=complete_questionnaire,
        offers=sample_offers,
        algorithm=AlgorithmType.AUTO
    )

# =================== ALGORITHM SELECTOR TESTS ===================

class TestIntelligentAlgorithmSelector:
    """Test the intelligent algorithm selection logic"""
    
    def setup_method(self):
        """Setup for each test"""
        self.selector = IntelligentAlgorithmSelector()
    
    def test_context_analysis_complete_data(self, sample_match_request):
        """Test context analysis with complete data"""
        context = self.selector.analyze_context(sample_match_request)
        
        assert context["questionnaire_completeness"] == 1.0  # All fields filled
        assert context["cv_completeness"] >= 0.8  # Good CV data
        assert context["experience_level"] == "senior"  # 42 months total
        assert context["skills_complexity"] >= 0.6  # Expert/Advanced skills
        assert context["offers_count"] == 3
    
    def test_context_analysis_minimal_data(self, sample_candidate, sample_offers):
        """Test context analysis with minimal data"""
        minimal_request = MatchRequest(
            candidate=Candidate(name="Jane Doe", email="jane@example.com"),
            offers=sample_offers,
            algorithm=AlgorithmType.AUTO
        )
        
        context = self.selector.analyze_context(minimal_request)
        
        assert context["questionnaire_completeness"] == 0.0
        assert context["cv_completeness"] <= 0.4
        assert context["experience_level"] == "junior"
        assert context["skills_complexity"] == 0.0
    
    def test_algorithm_selection_nexten_priority(self, sample_match_request):
        """Test that Nexten is selected for complete data"""
        context = self.selector.analyze_context(sample_match_request)
        algorithm, reason = self.selector.select_algorithm(sample_match_request, context)
        
        assert algorithm == AlgorithmType.NEXTEN
        assert "complete questionnaire" in reason.lower()
    
    def test_algorithm_selection_smart_for_location(self, sample_candidate, sample_offers):
        """Test that Smart is selected for location constraints"""
        from main import Location
        
        candidate_with_location = Candidate(
            name="John Doe",
            email="john@example.com", 
            location=Location(city="Paris", country="France")
        )
        
        request = MatchRequest(
            candidate=candidate_with_location,
            offers=sample_offers,
            algorithm=AlgorithmType.AUTO
        )
        
        context = self.selector.analyze_context(request)
        algorithm, reason = self.selector.select_algorithm(request, context)
        
        assert algorithm == AlgorithmType.SMART
        assert "geographic" in reason.lower()
    
    def test_algorithm_selection_enhanced_for_senior(self, sample_candidate, sample_offers):
        """Test that Enhanced is selected for senior profiles"""
        # Create senior candidate with longer experience
        senior_candidate = Candidate(
            name="Senior Dev",
            email="senior@example.com",
            technical_skills=[TechnicalSkill(name="Python", level="Expert", years=8)],
            experiences=[
                Experience(title="Senior Developer", company="Corp", duration_months=60),
                Experience(title="Lead Developer", company="Corp2", duration_months=36)
            ]
        )
        
        request = MatchRequest(
            candidate=senior_candidate,
            offers=sample_offers,
            algorithm=AlgorithmType.AUTO
        )
        
        context = self.selector.analyze_context(request)
        # Remove location constraints and questionnaire to trigger enhanced
        context["has_location_constraints"] = False
        context["questionnaire_completeness"] = 0.3
        
        algorithm, reason = self.selector.select_algorithm(request, context)
        
        assert algorithm == AlgorithmType.ENHANCED
        assert "senior" in reason.lower()
    
    def test_user_specified_algorithm(self, sample_match_request):
        """Test that user-specified algorithm is respected"""
        sample_match_request.algorithm = AlgorithmType.SEMANTIC
        
        context = self.selector.analyze_context(sample_match_request)
        algorithm, reason = self.selector.select_algorithm(sample_match_request, context)
        
        assert algorithm == AlgorithmType.SEMANTIC
        assert "user specified" in reason.lower()

# =================== CIRCUIT BREAKER TESTS ===================

class TestCircuitBreaker:
    """Test circuit breaker functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_closed_state(self):
        """Test circuit breaker in closed state"""
        async def success_func():
            return "success"
        
        result = await self.circuit_breaker.call(success_func)
        assert result == "success"
        assert self.circuit_breaker.state == CircuitBreakerState.CLOSED
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """Test circuit breaker opens after threshold failures"""
        async def failing_func():
            raise Exception("Service error")
        
        # Record failures to reach threshold
        for _ in range(3):
            with pytest.raises(Exception):
                await self.circuit_breaker.call(failing_func)
        
        assert self.circuit_breaker.state == CircuitBreakerState.OPEN
        
        # Should raise HTTPException for subsequent calls
        with pytest.raises(Exception):  # HTTPException
            await self.circuit_breaker.call(failing_func)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovery(self):
        """Test circuit breaker recovery after timeout"""
        async def failing_func():
            raise Exception("Service error")
        
        async def success_func():
            return "recovered"
        
        # Open the circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await self.circuit_breaker.call(failing_func)
        
        assert self.circuit_breaker.state == CircuitBreakerState.OPEN
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        # Should move to half-open and recover
        result = await self.circuit_breaker.call(success_func)
        assert result == "recovered"
        assert self.circuit_breaker.state == CircuitBreakerState.CLOSED

# =================== SERVICE INTEGRATION TESTS ===================

class TestSuperSmartMatchV2:
    """Test the main service integration"""
    
    def setup_method(self):
        """Setup for each test"""
        self.service = SuperSmartMatchV2()
    
    @patch('main.NextenMatcherAdapter.match')
    @pytest.mark.asyncio
    async def test_nexten_integration(self, mock_nexten, sample_match_request):
        """Test integration with Nexten Matcher"""
        from main import MatchResult
        
        # Mock Nexten response
        mock_nexten.return_value = [
            MatchResult(
                offer_id="job_123",
                overall_score=0.92,
                confidence=0.88,
                skill_match_score=0.95,
                experience_match_score=0.89,
                insights=["Excellent Python skills match"],
                explanation="Nexten ML analysis shows strong alignment"
            )
        ]
        
        response = await self.service.match(sample_match_request)
        
        assert response.success
        assert len(response.matches) == 1
        assert response.matches[0].overall_score == 0.92
        assert response.algorithm_used == "nexten"
        assert "complete questionnaire" in response.selection_reason
        mock_nexten.assert_called_once()
    
    @patch('main.V1AlgorithmsAdapter.match')
    @patch('main.NextenMatcherAdapter.match')
    @pytest.mark.asyncio
    async def test_fallback_to_v1(self, mock_nexten, mock_v1, sample_match_request):
        """Test fallback from Nexten to V1 algorithms"""
        from main import MatchResult
        
        # Mock Nexten failure
        mock_nexten.side_effect = Exception("Nexten service down")
        
        # Mock V1 success
        mock_v1.return_value = [
            MatchResult(
                offer_id="job_123",
                overall_score=0.85,
                confidence=0.75,
                skill_match_score=0.88,
                experience_match_score=0.82,
                insights=["Good skills alignment"],
                explanation="Enhanced algorithm analysis"
            )
        ]
        
        response = await self.service.match(sample_match_request)
        
        assert response.success
        assert len(response.matches) == 1
        assert response.matches[0].overall_score == 0.85
        mock_nexten.assert_called_once()
        mock_v1.assert_called_once()
    
    @patch('main.NextenMatcherAdapter.match')
    @patch('main.V1AlgorithmsAdapter.match')
    @pytest.mark.asyncio
    async def test_emergency_fallback(self, mock_nexten, mock_v1, sample_match_request):
        """Test emergency fallback when all services fail"""
        # Mock all services failing
        mock_nexten.side_effect = Exception("Nexten down")
        mock_v1.side_effect = Exception("V1 down")
        
        response = await self.service.match(sample_match_request)
        
        assert response.success
        assert len(response.matches) == 3  # All offers get basic scores
        assert all(match.overall_score > 0 for match in response.matches)
        assert all("emergency" in match.explanation.lower() for match in response.matches)

# =================== API ENDPOINT TESTS ===================

@pytest.mark.asyncio
class TestAPIEndpoints:
    """Test FastAPI endpoints"""
    
    async def test_root_endpoint(self):
        """Test root endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "SuperSmartMatch V2"
        assert data["version"] == "2.0.0"
        assert data["port"] == 5070
    
    async def test_health_endpoint(self):
        """Test health check endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["port"] == 5070
    
    @patch('main.SuperSmartMatchV2.match')
    async def test_v2_match_endpoint(self, mock_match, sample_match_request):
        """Test V2 matching endpoint"""
        from main import MatchResponse, MatchResult
        
        # Mock service response
        mock_match.return_value = MatchResponse(
            success=True,
            matches=[
                MatchResult(
                    offer_id="job_123",
                    overall_score=0.92,
                    confidence=0.88,
                    skill_match_score=0.95,
                    experience_match_score=0.89,
                    insights=["Excellent match"],
                    explanation="High compatibility"
                )
            ],
            algorithm_used="nexten",
            execution_time_ms=75,
            selection_reason="Complete data available",
            context_analysis={},
            performance_metrics={}
        )
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v2/match",
                json=sample_match_request.model_dump()
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["matches"]) == 1
        assert data["algorithm_used"] == "nexten"
        mock_match.assert_called_once()
    
    async def test_v1_compatibility_endpoint(self):
        """Test V1 compatibility endpoint"""
        v1_request = {
            "candidate": {
                "name": "John Doe",
                "email": "john@example.com",
                "technical_skills": ["Python", "Machine Learning"],
                "experiences": [
                    {
                        "title": "Developer",
                        "company": "TechCorp",
                        "duration": 24
                    }
                ]
            },
            "offers": [
                {
                    "id": "job_123",
                    "title": "ML Engineer", 
                    "company": "AI Corp",
                    "required_skills": ["Python", "TensorFlow"]
                }
            ]
        }
        
        with patch('main.SuperSmartMatchV2.match') as mock_match:
            from main import MatchResponse, MatchResult
            
            mock_match.return_value = MatchResponse(
                success=True,
                matches=[
                    MatchResult(
                        offer_id="job_123",
                        overall_score=0.88,
                        confidence=0.82,
                        skill_match_score=0.90,
                        experience_match_score=0.85,
                        insights=["Good fit"],
                        explanation="Solid match"
                    )
                ],
                algorithm_used="auto",
                execution_time_ms=65,
                selection_reason="Auto selection",
                context_analysis={},
                performance_metrics={}
            )
            
            async with AsyncClient(app=app, base_url="http://test") as client:
                response = await client.post("/match", json=v1_request)
            
            assert response.status_code == 200
            data = response.json()
            assert "matches" in data
            assert "algorithm_used" in data
            assert "execution_time_ms" in data
    
    async def test_stats_endpoint(self):
        """Test stats endpoint"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["port"] == 5070
        assert "algorithms" in data
        assert "circuit_breakers" in data

# =================== PERFORMANCE TESTS ===================

class TestPerformance:
    """Test performance requirements"""
    
    @patch('main.NextenMatcherAdapter.match')
    @pytest.mark.asyncio
    async def test_response_time_requirement(self, mock_nexten, sample_match_request):
        """Test that response time meets <100ms requirement"""
        from main import MatchResult
        
        # Mock fast response
        mock_nexten.return_value = [
            MatchResult(
                offer_id="job_123",
                overall_score=0.90,
                confidence=0.85,
                skill_match_score=0.92,
                experience_match_score=0.88,
                insights=["Fast match"],
                explanation="Quick analysis"
            )
        ]
        
        start_time = time.time()
        response = await service.match(sample_match_request)
        elapsed_ms = (time.time() - start_time) * 1000
        
        assert response.success
        assert elapsed_ms < 100  # Performance requirement
        assert response.execution_time_ms < 100

# =================== DATA VALIDATION TESTS ===================

class TestDataValidation:
    """Test data validation and error handling"""
    
    async def test_invalid_algorithm_type(self):
        """Test handling of invalid algorithm type"""
        invalid_request = {
            "candidate": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "offers": [],
            "algorithm": "invalid_algorithm"
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post("/api/v2/match", json=invalid_request)
        
        assert response.status_code == 422  # Validation error
    
    async def test_empty_offers_handling(self, sample_candidate):
        """Test handling of empty offers list"""
        request = MatchRequest(
            candidate=sample_candidate,
            offers=[],  # Empty offers
            algorithm=AlgorithmType.AUTO
        )
        
        response = await service.match(request)
        assert response.success
        assert len(response.matches) == 0
    
    async def test_minimal_candidate_data(self, sample_offers):
        """Test handling of minimal candidate data"""
        minimal_candidate = Candidate(
            name="Minimal User",
            email="minimal@example.com"
            # No skills or experience
        )
        
        request = MatchRequest(
            candidate=minimal_candidate,
            offers=sample_offers,
            algorithm=AlgorithmType.AUTO
        )
        
        response = await service.match(request)
        assert response.success
        assert len(response.matches) == len(sample_offers)
        # Should still get some scoring even with minimal data

# =================== CONFIGURATION TESTS ===================

def test_algorithm_configuration():
    """Test algorithm configuration and priorities"""
    selector = IntelligentAlgorithmSelector()
    
    # Test that circuit breakers are properly initialized
    assert selector.nexten_circuit_breaker.failure_threshold == 3
    assert selector.v1_circuit_breaker.failure_threshold == 5
    assert selector.nexten_circuit_breaker.state == CircuitBreakerState.CLOSED

# =================== RUN TESTS ===================

if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
