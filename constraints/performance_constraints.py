"""Performance constraints module for Hungarian algorithm.

This module defines constraints related to execution time, memory usage,
and scalability properties for the Hungarian matching algorithm.
"""

import time
import sys
import psutil
import numpy as np
from typing import Dict, Any, Optional, Callable, List, Tuple, Union
from functools import wraps

from .base_constraints import BaseConstraint, ConstraintViolationError, ConstraintPriority


class TimeConstraint(BaseConstraint):
    """Constraint for maximum execution time allowed for the algorithm."""
    
    def __init__(self, 
                 max_time_seconds: float, 
                 priority: ConstraintPriority = ConstraintPriority.HIGH,
                 penalty_factor: float = 1.0):
        """
        Initialize time constraint.
        
        Args:
            max_time_seconds: Maximum execution time in seconds
            priority: Priority level for this constraint
            penalty_factor: Factor applied to cost when time constraint is violated
        """
        super().__init__(priority=priority, penalty_factor=penalty_factor)
        self.max_time_seconds = max_time_seconds
        self.start_time = None
        
    def initialize(self) -> None:
        """Start time measurement when constraint checking begins."""
        self.start_time = time.time()
        
    def check(self, context: Dict[str, Any]) -> bool:
        """
        Check if current execution time exceeds the maximum allowed time.
        
        Args:
            context: Execution context
            
        Returns:
            True if constraint is satisfied, False otherwise
        """
        if self.start_time is None:
            self.initialize()
            
        elapsed_time = time.time() - self.start_time
        return elapsed_time <= self.max_time_seconds
    
    def calculate_penalty(self, context: Dict[str, Any]) -> float:
        """
        Calculate penalty for time constraint violation.
        
        Args:
            context: Execution context
            
        Returns:
            Penalty value based on how much the time constraint was violated
        """
        if self.start_time is None:
            return 0.0
            
        elapsed_time = time.time() - self.start_time
        if elapsed_time <= self.max_time_seconds:
            return 0.0
        
        # Penalty grows quadratically with the excess time
        excess_ratio = elapsed_time / self.max_time_seconds - 1.0
        return self.penalty_factor * (excess_ratio ** 2)
    
    def __str__(self) -> str:
        return f"TimeConstraint(max_time={self.max_time_seconds}s, priority={self.priority})"


class MemoryConstraint(BaseConstraint):
    """Constraint for maximum memory usage allowed for the algorithm."""
    
    def __init__(self, 
                 max_memory_mb: float, 
                 priority: ConstraintPriority = ConstraintPriority.HIGH,
                 penalty_factor: float = 1.0):
        """
        Initialize memory constraint.
        
        Args:
            max_memory_mb: Maximum memory usage in megabytes
            priority: Priority level for this constraint
            penalty_factor: Factor applied to cost when memory constraint is violated
        """
        super().__init__(priority=priority, penalty_factor=penalty_factor)
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.process = psutil.Process()
        
    def check(self, context: Dict[str, Any]) -> bool:
        """
        Check if current memory usage exceeds the maximum allowed.
        
        Args:
            context: Execution context
            
        Returns:
            True if constraint is satisfied, False otherwise
        """
        current_memory = self.process.memory_info().rss
        return current_memory <= self.max_memory_bytes
    
    def calculate_penalty(self, context: Dict[str, Any]) -> float:
        """
        Calculate penalty for memory constraint violation.
        
        Args:
            context: Execution context
            
        Returns:
            Penalty value based on how much the memory constraint was violated
        """
        current_memory = self.process.memory_info().rss
        if current_memory <= self.max_memory_bytes:
            return 0.0
        
        # Penalty grows linearly with the excess memory
        excess_ratio = current_memory / self.max_memory_bytes - 1.0
        return self.penalty_factor * excess_ratio
    
    def __str__(self) -> str:
        return f"MemoryConstraint(max_memory={self.max_memory_bytes/1024/1024:.1f}MB, priority={self.priority})"


class MatrixSizeConstraint(BaseConstraint):
    """Constraint for the maximum size of the cost matrix."""
    
    def __init__(self, 
                 max_dimension: int, 
                 priority: ConstraintPriority = ConstraintPriority.HIGH,
                 penalty_factor: float = 1.0):
        """
        Initialize matrix size constraint.
        
        Args:
            max_dimension: Maximum number of rows/columns in the cost matrix
            priority: Priority level for this constraint
            penalty_factor: Factor applied to cost when size constraint is violated
        """
        super().__init__(priority=priority, penalty_factor=penalty_factor)
        self.max_dimension = max_dimension
        
    def check(self, context: Dict[str, Any]) -> bool:
        """
        Check if matrix dimensions exceed the maximum allowed.
        
        Args:
            context: Execution context with 'cost_matrix' key containing the cost matrix
            
        Returns:
            True if constraint is satisfied, False otherwise
        """
        if 'cost_matrix' not in context:
            raise ValueError("Context must contain 'cost_matrix' for MatrixSizeConstraint")
            
        cost_matrix = context['cost_matrix']
        rows, cols = cost_matrix.shape
        return max(rows, cols) <= self.max_dimension
    
    def calculate_penalty(self, context: Dict[str, Any]) -> float:
        """
        Calculate penalty for matrix size constraint violation.
        
        Args:
            context: Execution context with 'cost_matrix' key
            
        Returns:
            Penalty value based on how much the size constraint was violated
        """
        if 'cost_matrix' not in context:
            return 0.0
            
        cost_matrix = context['cost_matrix']
        rows, cols = cost_matrix.shape
        max_dim = max(rows, cols)
        
        if max_dim <= self.max_dimension:
            return 0.0
        
        # Penalty grows quadratically with the excess size
        excess_ratio = max_dim / self.max_dimension - 1.0
        return self.penalty_factor * (excess_ratio ** 2)
    
    def __str__(self) -> str:
        return f"MatrixSizeConstraint(max_dimension={self.max_dimension}, priority={self.priority})"


class ScalabilityConstraint(BaseConstraint):
    """Constraint for algorithm scalability with problem size."""
    
    def __init__(self, 
                 complexity_function: Callable[[int], float],
                 scale_factor: float = 1.0,
                 priority: ConstraintPriority = ConstraintPriority.MEDIUM,
                 penalty_factor: float = 1.0):
        """
        Initialize scalability constraint.
        
        Args:
            complexity_function: Function that returns expected time for a given problem size
            scale_factor: Scaling factor for the complexity function
            priority: Priority level for this constraint
            penalty_factor: Factor applied to cost when scalability constraint is violated
        """
        super().__init__(priority=priority, penalty_factor=penalty_factor)
        self.complexity_function = complexity_function
        self.scale_factor = scale_factor
        self.start_time = None
        self.problem_size = None
        
    def initialize(self, context: Dict[str, Any]) -> None:
        """
        Start time measurement and record problem size.
        
        Args:
            context: Execution context with 'cost_matrix' key
        """
        if 'cost_matrix' not in context:
            raise ValueError("Context must contain 'cost_matrix' for ScalabilityConstraint")
            
        cost_matrix = context['cost_matrix']
        self.problem_size = max(cost_matrix.shape)
        self.start_time = time.time()
        
    def check(self, context: Dict[str, Any]) -> bool:
        """
        Check if execution time is within expected bounds for the problem size.
        
        Args:
            context: Execution context
            
        Returns:
            True if constraint is satisfied, False otherwise
        """
        if self.start_time is None or self.problem_size is None:
            self.initialize(context)
            return True
            
        elapsed_time = time.time() - self.start_time
        expected_time = self.complexity_function(self.problem_size) * self.scale_factor
        
        return elapsed_time <= expected_time
    
    def calculate_penalty(self, context: Dict[str, Any]) -> float:
        """
        Calculate penalty for scalability constraint violation.
        
        Args:
            context: Execution context
            
        Returns:
            Penalty value based on how much the scalability constraint was violated
        """
        if self.start_time is None or self.problem_size is None:
            return 0.0
            
        elapsed_time = time.time() - self.start_time
        expected_time = self.complexity_function(self.problem_size) * self.scale_factor
        
        if elapsed_time <= expected_time:
            return 0.0
        
        # Penalty grows linearly with the ratio of actual to expected time
        excess_ratio = elapsed_time / expected_time - 1.0
        return self.penalty_factor * excess_ratio
    
    def __str__(self) -> str:
        return f"ScalabilityConstraint(scale_factor={self.scale_factor}, priority={self.priority})"


class PerformanceConstraintDecorator:
    """Decorator for enforcing performance constraints on functions."""
    
    def __init__(self, constraints: List[BaseConstraint]):
        """
        Initialize decorator with a list of constraints.
        
        Args:
            constraints: List of performance constraints to enforce
        """
        self.constraints = constraints
        
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Initialize context
            context = {'func_name': func.__name__, 'args': args, 'kwargs': kwargs}
            
            # Initialize time-based constraints
            for constraint in self.constraints:
                if hasattr(constraint, 'initialize'):
                    constraint.initialize()
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Update context with result
            context['result'] = result
            
            # Check constraints
            violations = []
            for constraint in self.constraints:
                if not constraint.check(context):
                    violations.append(constraint)
            
            # Handle violations based on priority
            if violations:
                highest_priority = min(c.priority.value for c in violations)
                critical_violations = [c for c in violations if c.priority.value == highest_priority]
                
                if highest_priority <= ConstraintPriority.HIGH.value:
                    violation_str = ', '.join(str(c) for c in critical_violations)
                    raise ConstraintViolationError(
                        f"Critical performance constraints violated: {violation_str}"
                    )
            
            return result
        
        return wrapper


# Utility complexity functions for ScalabilityConstraint
def cubic_complexity(n: int) -> float:
    """Cubic time complexity O(n^3)."""
    return 1e-6 * (n ** 3)  # Scaled for seconds

def quadratic_complexity(n: int) -> float:
    """Quadratic time complexity O(n^2)."""
    return 1e-5 * (n ** 2)  # Scaled for seconds

def linear_complexity(n: int) -> float:
    """Linear time complexity O(n)."""
    return 1e-4 * n  # Scaled for seconds