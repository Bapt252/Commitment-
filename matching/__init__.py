"""Matching module for Hungarian algorithm implementation.

This module provides optimized implementations of matching algorithms
based on the Hungarian method for assignment problems, with support for
constraints, edge cases, and performance analysis.
"""

from typing import Dict, List, Tuple, Set, Any, Optional, Union, Callable

# Import main components
from .optimal_matcher import OptimalMatcher
from .edge_case_handler import EdgeCaseHandler
from .performance_analyzer import PerformanceAnalyzer

# Define version
__version__ = "0.1.0"