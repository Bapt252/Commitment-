"""
SuperSmartMatch V2 - Unified Intelligent Matching Architecture

This module provides the next-generation matching service that intelligently
combines all existing algorithms with Nexten Matcher as the primary engine.

Key Features:
- Intelligent algorithm selection based on data context
- Unified API with backward compatibility
- Performance monitoring and circuit breakers
- Progressive deployment capabilities
- Real-time fallback mechanisms
"""

from .supersmartmatch_v2 import SuperSmartMatchV2
from .algorithm_selector import SmartAlgorithmSelector, AlgorithmType, MatchingContext
from .nexten_adapter import NextenMatcherAdapter
from .data_adapter import DataFormatAdapter
from .performance_monitor import PerformanceMonitor
from .config_manager import ConfigManager
from .deployment_manager import DeploymentManager

__version__ = "2.0.0"

__all__ = [
    "SuperSmartMatchV2",
    "SmartAlgorithmSelector",
    "AlgorithmType", 
    "MatchingContext",
    "NextenMatcherAdapter",
    "DataFormatAdapter",
    "PerformanceMonitor",
    "ConfigManager",
    "DeploymentManager"
]