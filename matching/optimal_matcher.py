"""Optimal matcher module for Hungarian algorithm implementation.

This module provides the main implementation of the Hungarian algorithm
with support for constraints, priorities, and multi-criteria optimization.
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Set, Any, Optional, Union, Callable
from functools import lru_cache
import time

from ..hungarian.algorithm import HungarianAlgorithm
from ..hungarian.cost_matrix import CostMatrix
from ..hungarian.constraint_system import ConstraintSystem
from ..hungarian.bidirectional_matcher import BidirectionalMatcher
from ..constraints.base_constraints import BaseConstraint, ConstraintPriority
from ..constraints.constraint_validator import ConstraintValidator, ConstraintGroup

logger = logging.getLogger(__name__)


class OptimalMatcher:
    """
    Primary matching class that uses the Hungarian algorithm to find optimal assignments.
    
    This class integrates the core Hungarian algorithm with constraints, caching,
    and optimization strategies to provide efficient and accurate matching solutions.
    """
    
    def __init__(self, 
                 use_bidirectional: bool = False,
                 cache_size: int = 128,
                 constraint_validator: Optional[ConstraintValidator] = None):
        """
        Initialize the optimal matcher.
        
        Args:
            use_bidirectional: Whether to use bidirectional matching for preference stability
            cache_size: Size of the LRU cache for cost matrix computations
            constraint_validator: Validator for checking constraints
        """
        self.hungarian = HungarianAlgorithm()
        self.use_bidirectional = use_bidirectional
        self.bidirectional_matcher = BidirectionalMatcher() if use_bidirectional else None
        self.constraint_system = ConstraintSystem()
        self.constraint_validator = constraint_validator or ConstraintValidator()
        
        # Performance tracking
        self.execution_times = []
        self.last_execution_time = None
        
        # Configure caching
        self._configure_cache(cache_size)
    
    def _configure_cache(self, cache_size: int) -> None:
        """
        Configure LRU cache for cost computations.
        
        Args:
            cache_size: Maximum number of entries in the cache
        """
        if cache_size > 0:
            self.compute_assignment = lru_cache(maxsize=cache_size)(self._compute_assignment_uncached)
        else:
            self.compute_assignment = self._compute_assignment_uncached
    
    def add_constraint(self, constraint: BaseConstraint, group_name: str = "default") -> None:
        """
        Add a constraint to be considered during matching.
        
        Args:
            constraint: The constraint to add
            group_name: Name of the constraint group to add to
        """
        # Ensure the constraint group exists
        if group_name not in self.constraint_validator.groups:
            self.constraint_validator.create_group(group_name)
            
        # Add the constraint to the group
        self.constraint_validator.get_group(group_name).add_constraint(constraint)
        
        # Also add to the constraint system for use during optimization
        self.constraint_system.add_constraint(constraint)
    
    def match(self, 
              cost_matrix: np.ndarray,
              row_preferences: Optional[List[List[int]]] = None,
              col_preferences: Optional[List[List[int]]] = None,
              context: Optional[Dict[str, Any]] = None) -> Tuple[List[Tuple[int, int]], float]:
        """
        Find optimal assignment using the Hungarian algorithm.
        
        Args:
            cost_matrix: 2D array of assignment costs
            row_preferences: Optional ordered preferences for rows (for bidirectional matching)
            col_preferences: Optional ordered preferences for columns (for bidirectional matching)
            context: Additional context for constraint validation
            
        Returns:
            Tuple containing:
            - List of (row, col) assignment pairs
            - Total cost of the assignment
            
        Raises:
            ValueError: If the input data is invalid
            ConstraintViolationError: If critical constraints are violated
        """
        start_time = time.time()
        
        # Prepare context
        if context is None:
            context = {}
        context['cost_matrix'] = cost_matrix
        context['timestamp'] = start_time
        
        # Validate input dimensions
        self._validate_input(cost_matrix, row_preferences, col_preferences)
        
        # Validate constraints before computation
        self.constraint_validator.validate_group("pre_computation", context)
        
        # Choose matching strategy
        if self.use_bidirectional and row_preferences and col_preferences:
            assignments = self._bidirectional_match(
                cost_matrix, row_preferences, col_preferences, context
            )
        else:
            assignments = self._hungarian_match(cost_matrix, context)
        
        # Calculate total cost
        total_cost = self._calculate_total_cost(cost_matrix, assignments)
        
        # Update context with results
        context['assignments'] = assignments
        context['total_cost'] = total_cost
        
        # Validate constraints after computation
        self.constraint_validator.validate_group("post_computation", context)
        
        # Record execution time
        self.last_execution_time = time.time() - start_time
        self.execution_times.append(self.last_execution_time)
        
        return assignments, total_cost
    
    def _validate_input(self, 
                       cost_matrix: np.ndarray, 
                       row_preferences: Optional[List[List[int]]] = None,
                       col_preferences: Optional[List[List[int]]] = None) -> None:
        """
        Validate input data for matching.
        
        Args:
            cost_matrix: 2D array of assignment costs
            row_preferences: Optional ordered preferences for rows
            col_preferences: Optional ordered preferences for columns
            
        Raises:
            ValueError: If inputs are invalid
        """
        # Check cost matrix dimensions
        if cost_matrix.ndim != 2:
            raise ValueError("Cost matrix must be 2-dimensional")
        
        rows, cols = cost_matrix.shape
        
        # Check preference lists if provided
        if row_preferences is not None:
            if len(row_preferences) != rows:
                raise ValueError(f"Row preferences list length ({len(row_preferences)}) "
                               f"must match cost matrix rows ({rows})")
                
            for i, prefs in enumerate(row_preferences):
                if not all(0 <= p < cols for p in prefs):
                    raise ValueError(f"Row {i} preferences contain invalid column indices")
        
        if col_preferences is not None:
            if len(col_preferences) != cols:
                raise ValueError(f"Column preferences list length ({len(col_preferences)}) "
                               f"must match cost matrix columns ({cols})")
                
            for i, prefs in enumerate(col_preferences):
                if not all(0 <= p < rows for p in prefs):
                    raise ValueError(f"Column {i} preferences contain invalid row indices")
    
    def _hungarian_match(self, 
                        cost_matrix: np.ndarray,
                        context: Dict[str, Any]) -> List[Tuple[int, int]]:
        """
        Perform matching using the Hungarian algorithm.
        
        Args:
            cost_matrix: 2D array of assignment costs
            context: Additional context for constraint validation
            
        Returns:
            List of (row, col) assignment pairs
        """
        # Apply constraint penalties to cost matrix
        adjusted_matrix = self.constraint_system.apply_penalties(cost_matrix, context)
        
        # Create a cost matrix wrapper
        cost_matrix_obj = CostMatrix(adjusted_matrix)
        
        # Use cached computation for identical inputs
        matrix_hash = cost_matrix_obj.hash()
        row_indices, col_indices = self.compute_assignment(matrix_hash)
        
        # Convert to list of pairs
        assignments = [(int(row), int(col)) for row, col in zip(row_indices, col_indices)]
        
        return assignments
    
    @staticmethod
    def _compute_assignment_uncached(matrix_hash: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute Hungarian algorithm assignment (uncached version).
        
        Args:
            matrix_hash: Hash of the cost matrix for caching
            
        Returns:
            Tuple of row and column indices for optimal assignment
        """
        # In a real implementation, this would extract the matrix from the hash
        # and compute the assignment. For now, we'll just return dummy indices.
        # This would be replaced with actual Hungarian algorithm implementation.
        cost_matrix = CostMatrix.from_hash(matrix_hash)
        algorithm = HungarianAlgorithm()
        row_indices, col_indices = algorithm.solve(cost_matrix.matrix)
        return row_indices, col_indices
    
    def _bidirectional_match(self, 
                            cost_matrix: np.ndarray,
                            row_preferences: List[List[int]],
                            col_preferences: List[List[int]],
                            context: Dict[str, Any]) -> List[Tuple[int, int]]:
        """
        Perform matching using bidirectional stable matching.
        
        Args:
            cost_matrix: 2D array of assignment costs
            row_preferences: Ordered preferences for rows
            col_preferences: Ordered preferences for columns
            context: Additional context for constraint validation
            
        Returns:
            List of (row, col) assignment pairs
        """
        if self.bidirectional_matcher is None:
            raise ValueError("Bidirectional matcher was not initialized")
        
        # Apply constraint penalties to preference rankings
        # This is a simplified approach; a more sophisticated implementation
        # would adjust the preference rankings based on constraints
        
        # Get stable matching
        assignments = self.bidirectional_matcher.match(
            row_preferences, col_preferences
        )
        
        return assignments
    
    def _calculate_total_cost(self, 
                             cost_matrix: np.ndarray,
                             assignments: List[Tuple[int, int]]) -> float:
        """
        Calculate the total cost of an assignment.
        
        Args:
            cost_matrix: 2D array of assignment costs
            assignments: List of (row, col) assignment pairs
            
        Returns:
            Total cost of the assignment
        """
        return sum(cost_matrix[row, col] for row, col in assignments)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics from matcher execution.
        
        Returns:
            Dictionary of performance statistics
        """
        if not self.execution_times:
            return {
                'count': 0,
                'avg_time': 0,
                'min_time': 0,
                'max_time': 0,
                'last_time': 0
            }
        
        return {
            'count': len(self.execution_times),
            'avg_time': sum(self.execution_times) / len(self.execution_times),
            'min_time': min(self.execution_times),
            'max_time': max(self.execution_times),
            'last_time': self.last_execution_time
        }
    
    def clear_cache(self) -> None:
        """Clear the computation cache."""
        if hasattr(self.compute_assignment, 'cache_clear'):
            self.compute_assignment.cache_clear()
    
    def get_constraint_report(self) -> Dict[str, Any]:
        """
        Get a report of constraint validations.
        
        Returns:
            Constraint validation report
        """
        return self.constraint_validator.generate_report()