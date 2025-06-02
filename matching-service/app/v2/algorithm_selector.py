"""
Smart Algorithm Selector for SuperSmartMatch V2

Intelligent algorithm selection based on context analysis and audit findings.
Implements the decision matrix identified during the technical audit.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict
import asyncio
import time

logger = logging.getLogger(__name__)

class AlgorithmType(Enum):
    """Available matching algorithms"""
    NEXTEN = "nexten"
    SMART = "smart"
    ENHANCED = "enhanced"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"

@dataclass
class MatchingContext:
    """Context information for algorithm selection"""
    candidate_skills: List[str]
    candidate_experience: int
    locations: List[str]
    mobility_constraints: str
    questionnaire_completeness: float
    company_questionnaires_completeness: float
    
    # Analysis flags
    has_strong_geo_constraints: bool = False
    requires_semantic_analysis: bool = False
    has_complex_skill_descriptions: bool = False
    requires_validation: bool = False
    is_critical_match: bool = False
    
    def __post_init__(self):
        """Auto-analyze context after initialization"""
        self.has_strong_geo_constraints = self._analyze_geo_constraints()
        self.requires_semantic_analysis = self._requires_semantic()
        self.has_complex_skill_descriptions = self._analyze_skill_complexity()
        self.requires_validation = self._requires_validation()
        self.is_critical_match = self._is_critical()
    
    def _analyze_geo_constraints(self) -> bool:
        """Analyze if geographical constraints are strong"""
        return (
            len(self.locations) > 3 or 
            self.mobility_constraints in ["strict", "limited"] or
            any("remote" in loc.lower() for loc in self.locations)
        )
    
    def _requires_semantic(self) -> bool:
        """Check if semantic analysis is required"""
        return (
            len(self.candidate_skills) > 10 or
            any(len(skill.split()) > 3 for skill in self.candidate_skills)
        )
    
    def _analyze_skill_complexity(self) -> bool:
        """Analyze skill description complexity"""
        return any(
            len(skill) > 20 or 
            any(char in skill for char in [',', '/', '&', '+'])
            for skill in self.candidate_skills
        )
    
    def _requires_validation(self) -> bool:
        """Check if validation is required"""
        return (
            self.candidate_experience >= 10 or
            len(self.candidate_skills) >= 15 or
            self.questionnaire_completeness < 0.3
        )
    
    def _is_critical(self) -> bool:
        """Determine if this is a critical match"""
        return (
            self.candidate_experience >= 15 or
            len(self.candidate_skills) >= 20
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for logging/monitoring"""
        return {
            "skills_count": len(self.candidate_skills),
            "experience_years": self.candidate_experience,
            "locations_count": len(self.locations),
            "mobility": self.mobility_constraints,
            "questionnaire_completeness": self.questionnaire_completeness,
            "company_questionnaires_completeness": self.company_questionnaires_completeness,
            "geo_constraints": self.has_strong_geo_constraints,
            "semantic_required": self.requires_semantic_analysis,
            "complex_skills": self.has_complex_skill_descriptions,
            "validation_required": self.requires_validation,
            "critical_match": self.is_critical_match
        }

class CircuitBreaker:
    """Circuit breaker for algorithm availability"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.is_open = False
    
    def record_success(self):
        """Record successful execution"""
        self.failure_count = 0
        self.is_open = False
    
    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def can_execute(self) -> bool:
        """Check if circuit allows execution"""
        if not self.is_open:
            return True
        
        # Check if recovery timeout has passed
        if time.time() - self.last_failure_time > self.recovery_timeout:
            self.is_open = False
            self.failure_count = 0
            logger.info("Circuit breaker recovered")
            return True
        
        return False

class PerformanceTracker:
    """Track algorithm performance metrics"""
    
    def __init__(self):
        self.execution_times = defaultdict(list)
        self.success_rates = defaultdict(float)
        self.accuracy_scores = defaultdict(list)
        self.usage_counts = defaultdict(int)
    
    def record_execution(self, algorithm: AlgorithmType, execution_time: float, 
                        success: bool, accuracy: Optional[float] = None):
        """Record algorithm execution metrics"""
        self.execution_times[algorithm].append(execution_time)
        self.usage_counts[algorithm] += 1
        
        # Calculate rolling success rate
        total_executions = self.usage_counts[algorithm]
        if success:
            current_successes = self.success_rates[algorithm] * (total_executions - 1) + 1
        else:
            current_successes = self.success_rates[algorithm] * (total_executions - 1)
        
        self.success_rates[algorithm] = current_successes / total_executions
        
        if accuracy is not None:
            self.accuracy_scores[algorithm].append(accuracy)
    
    def get_avg_execution_time(self, algorithm: AlgorithmType) -> float:
        """Get average execution time for algorithm"""
        times = self.execution_times[algorithm]
        return sum(times) / len(times) if times else 0.0
    
    def get_recent_performance(self, algorithm: AlgorithmType, window: int = 10) -> Dict[str, float]:
        """Get recent performance metrics"""
        recent_times = self.execution_times[algorithm][-window:]
        recent_accuracy = self.accuracy_scores[algorithm][-window:]
        
        return {
            "avg_time": sum(recent_times) / len(recent_times) if recent_times else 0.0,
            "success_rate": self.success_rates[algorithm],
            "avg_accuracy": sum(recent_accuracy) / len(recent_accuracy) if recent_accuracy else 0.0,
            "usage_count": self.usage_counts[algorithm]
        }

class SmartAlgorithmSelector:
    """
    Intelligent algorithm selector based on context analysis.
    
    Implements the selection rules identified in the technical audit:
    - Prioritizes Nexten Matcher when questionnaires + skills available
    - Falls back intelligently based on context
    - Includes circuit breakers and performance monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._default_config()
        self.circuit_breakers = {
            algo: CircuitBreaker(
                failure_threshold=self.config.get('circuit_breaker', {}).get('failure_threshold', 5),
                recovery_timeout=self.config.get('circuit_breaker', {}).get('recovery_timeout', 30)
            )
            for algo in AlgorithmType
        }
        self.performance_tracker = PerformanceTracker()
        
        # Fallback hierarchy for each algorithm
        self.fallback_hierarchy = {
            AlgorithmType.NEXTEN: [AlgorithmType.ENHANCED, AlgorithmType.SMART, AlgorithmType.SEMANTIC],
            AlgorithmType.SMART: [AlgorithmType.NEXTEN, AlgorithmType.ENHANCED, AlgorithmType.HYBRID],
            AlgorithmType.ENHANCED: [AlgorithmType.SMART, AlgorithmType.NEXTEN, AlgorithmType.SEMANTIC],
            AlgorithmType.SEMANTIC: [AlgorithmType.NEXTEN, AlgorithmType.ENHANCED, AlgorithmType.SMART],
            AlgorithmType.HYBRID: [AlgorithmType.NEXTEN, AlgorithmType.SMART, AlgorithmType.ENHANCED]
        }
        
        logger.info("SmartAlgorithmSelector initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration"""
        return {
            "nexten_thresholds": {
                "questionnaire_completeness": 0.8,
                "company_questionnaire_completeness": 0.7,
                "minimum_skills": 5
            },
            "performance_thresholds": {
                "max_execution_time": 100,  # ms
                "min_success_rate": 0.95,
                "min_accuracy": 0.7
            },
            "circuit_breaker": {
                "failure_threshold": 5,
                "recovery_timeout": 30
            }
        }
    
    def select_algorithm(self, context: MatchingContext) -> AlgorithmType:
        """
        Select the optimal algorithm based on context analysis.
        Implements the priority rules from the technical audit.
        """
        
        # Rule 1: PRIORITY - Nexten Matcher when data is complete
        if self._should_use_nexten(context):
            selected = AlgorithmType.NEXTEN
            logger.info(f"Selected NEXTEN: questionnaires complete, {len(context.candidate_skills)} skills")
            return selected
        
        # Rule 2: SmartMatch for geographical complexity
        elif self._should_use_smart(context):
            selected = AlgorithmType.SMART
            logger.info(f"Selected SMART: geo constraints or mobility={context.mobility_constraints}")
            return selected
        
        # Rule 3: Enhanced for senior profiles without complete questionnaires
        elif self._should_use_enhanced(context):
            selected = AlgorithmType.ENHANCED
            logger.info(f"Selected ENHANCED: senior profile ({context.candidate_experience}y) with incomplete questionnaires")
            return selected
        
        # Rule 4: Semantic for pure semantic analysis needs
        elif self._should_use_semantic(context):
            selected = AlgorithmType.SEMANTIC
            logger.info(f"Selected SEMANTIC: complex skill descriptions or semantic analysis required")
            return selected
        
        # Rule 5: Hybrid for critical validation needs
        elif self._should_use_hybrid(context):
            selected = AlgorithmType.HYBRID
            logger.info(f"Selected HYBRID: critical match requiring validation")
            return selected
        
        # Rule 6: Default intelligent fallback to Nexten (most performant)
        else:
            selected = AlgorithmType.NEXTEN
            logger.info(f"Selected NEXTEN (default): most performant algorithm for general case")
            return selected
    
    async def select_algorithm_with_fallback(self, context: MatchingContext) -> AlgorithmType:
        """
        Select algorithm with circuit breaker and performance-based fallback.
        """
        
        # Primary selection
        primary_algorithm = self.select_algorithm(context)
        
        # Check circuit breaker
        if not self.circuit_breakers[primary_algorithm].can_execute():
            fallback = self._get_fallback_algorithm(primary_algorithm, context)
            logger.warning(f"Circuit breaker open for {primary_algorithm.value}, using {fallback.value}")
            return fallback
        
        # Check recent performance
        if self._is_performance_degraded(primary_algorithm):
            alternative = self._get_performance_alternative(primary_algorithm, context)
            if alternative:
                logger.info(f"Performance degraded for {primary_algorithm.value}, using {alternative.value}")
                return alternative
        
        return primary_algorithm
    
    def _should_use_nexten(self, context: MatchingContext) -> bool:
        """PRIORITY: Nexten Matcher when questionnaires + skills complete"""
        thresholds = self.config["nexten_thresholds"]
        return (
            context.questionnaire_completeness >= thresholds["questionnaire_completeness"] and
            context.company_questionnaires_completeness >= thresholds["company_questionnaire_completeness"] and
            len(context.candidate_skills) >= thresholds["minimum_skills"]
        )
    
    def _should_use_smart(self, context: MatchingContext) -> bool:
        """SmartMatch for geographical constraints and mobility"""
        return (
            context.mobility_constraints in ["remote", "limited"] or
            context.has_strong_geo_constraints or
            len(context.locations) > 3
        )
    
    def _should_use_enhanced(self, context: MatchingContext) -> bool:
        """Enhanced for senior profiles without complete questionnaires"""
        return (
            context.candidate_experience >= 7 and
            context.questionnaire_completeness < 0.6
        )
    
    def _should_use_semantic(self, context: MatchingContext) -> bool:
        """Semantic for pure semantic analysis requirements"""
        return (
            context.requires_semantic_analysis or
            context.has_complex_skill_descriptions
        )
    
    def _should_use_hybrid(self, context: MatchingContext) -> bool:
        """Hybrid for critical validation requirements"""
        return (
            context.requires_validation or
            context.is_critical_match
        )
    
    def _get_fallback_algorithm(self, failed_algorithm: AlgorithmType, 
                               context: MatchingContext) -> AlgorithmType:
        """Get the best available fallback algorithm"""
        for fallback in self.fallback_hierarchy.get(failed_algorithm, []):
            if self.circuit_breakers[fallback].can_execute():
                return fallback
        
        # Emergency fallback: find any working algorithm
        for algo in AlgorithmType:
            if self.circuit_breakers[algo].can_execute():
                logger.warning(f"Emergency fallback to {algo.value}")
                return algo
        
        # Critical: all algorithms down, use original despite circuit breaker
        logger.critical("All algorithms unavailable, forcing primary algorithm")
        return failed_algorithm
    
    def _is_performance_degraded(self, algorithm: AlgorithmType) -> bool:
        """Check if algorithm performance is degraded"""
        perf = self.performance_tracker.get_recent_performance(algorithm)
        thresholds = self.config["performance_thresholds"]
        
        return (
            perf["avg_time"] > thresholds["max_execution_time"] or
            perf["success_rate"] < thresholds["min_success_rate"] or
            perf["avg_accuracy"] < thresholds["min_accuracy"]
        )
    
    def _get_performance_alternative(self, algorithm: AlgorithmType, 
                                   context: MatchingContext) -> Optional[AlgorithmType]:
        """Get better performing alternative if available"""
        for alt in self.fallback_hierarchy.get(algorithm, []):
            if (self.circuit_breakers[alt].can_execute() and 
                not self._is_performance_degraded(alt)):
                return alt
        return None
    
    def record_execution_result(self, algorithm: AlgorithmType, execution_time: float,
                              success: bool, accuracy: Optional[float] = None):
        """Record algorithm execution result for monitoring"""
        self.performance_tracker.record_execution(algorithm, execution_time, success, accuracy)
        
        if success:
            self.circuit_breakers[algorithm].record_success()
        else:
            self.circuit_breakers[algorithm].record_failure()
            logger.warning(f"Algorithm {algorithm.value} execution failed")
    
    def get_algorithm_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive algorithm statistics"""
        stats = {}
        for algo in AlgorithmType:
            perf = self.performance_tracker.get_recent_performance(algo)
            stats[algo.value] = {
                "performance": perf,
                "circuit_breaker_open": self.circuit_breakers[algo].is_open,
                "failure_count": self.circuit_breakers[algo].failure_count
            }
        return stats