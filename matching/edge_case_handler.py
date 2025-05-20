"""Edge case handler module for Hungarian algorithm implementation.

This module handles special cases and exceptions that can occur during
the matching process, including non-square matrices, infeasible assignments,
and ties in preferences.
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Set, Any, Optional, Union, Callable
from enum import Enum, auto

logger = logging.getLogger(__name__)


class EdgeCaseType(Enum):
    """Types of edge cases that can occur during matching."""
    NON_SQUARE_MATRIX = auto()
    INFEASIBLE_ASSIGNMENT = auto()
    MULTIPLE_OPTIMAL_SOLUTIONS = auto()
    PREFERENCE_TIES = auto()
    MISSING_PREFERENCES = auto()
    ZERO_COST_CYCLES = auto()
    NEGATIVE_COST_CYCLES = auto()
    DISCONNECTED_GRAPH = auto()


class ResolutionStrategy(Enum):
    """Strategies for resolving edge cases."""
    PAD_MATRIX = auto()
    GREEDY_ASSIGNMENT = auto()
    RANDOM_SELECTION = auto()
    PROPORTIONAL_SELECTION = auto()
    USE_SECONDARY_CRITERIA = auto()
    SPLIT_ASSIGNMENT = auto()
    MANUAL_RESOLUTION = auto()


class EdgeCaseHandler:
    """
    Handler for special cases and exceptions in the Hungarian algorithm.
    
    This class detects and resolves various edge cases that can occur during
    the matching process, providing robust handling for real-world scenarios.
    """
    
    def __init__(self, default_strategy_map: Optional[Dict[EdgeCaseType, ResolutionStrategy]] = None):
        """
        Initialize the edge case handler.
        
        Args:
            default_strategy_map: Mapping of edge case types to default resolution strategies
        """
        self.default_strategies = default_strategy_map or {
            EdgeCaseType.NON_SQUARE_MATRIX: ResolutionStrategy.PAD_MATRIX,
            EdgeCaseType.INFEASIBLE_ASSIGNMENT: ResolutionStrategy.GREEDY_ASSIGNMENT,
            EdgeCaseType.MULTIPLE_OPTIMAL_SOLUTIONS: ResolutionStrategy.USE_SECONDARY_CRITERIA,
            EdgeCaseType.PREFERENCE_TIES: ResolutionStrategy.PROPORTIONAL_SELECTION,
            EdgeCaseType.MISSING_PREFERENCES: ResolutionStrategy.GREEDY_ASSIGNMENT,
            EdgeCaseType.ZERO_COST_CYCLES: ResolutionStrategy.USE_SECONDARY_CRITERIA,
            EdgeCaseType.NEGATIVE_COST_CYCLES: ResolutionStrategy.GREEDY_ASSIGNMENT,
            EdgeCaseType.DISCONNECTED_GRAPH: ResolutionStrategy.SPLIT_ASSIGNMENT
        }
        
        self.custom_handlers: Dict[EdgeCaseType, Callable] = {}
        self.detected_cases: List[Tuple[EdgeCaseType, Any]] = []
    
    def register_custom_handler(self, 
                               case_type: EdgeCaseType, 
                               handler_func: Callable) -> None:
        """
        Register a custom handler function for a specific edge case type.
        
        Args:
            case_type: The edge case type to handle
            handler_func: Function that handles the edge case
        """
        self.custom_handlers[case_type] = handler_func
    
    def detect_non_square_matrix(self, cost_matrix: np.ndarray) -> bool:
        """
        Detect if the cost matrix is non-square.
        
        Args:
            cost_matrix: The cost matrix to check
            
        Returns:
            True if the matrix is non-square, False otherwise
        """
        rows, cols = cost_matrix.shape
        is_non_square = rows != cols
        
        if is_non_square:
            self.detected_cases.append((EdgeCaseType.NON_SQUARE_MATRIX, (rows, cols)))
            logger.debug(f"Detected non-square matrix: {rows}x{cols}")
            
        return is_non_square
    
    def detect_infeasible_assignment(self, 
                                    cost_matrix: np.ndarray,
                                    inf_value: float = float('inf')) -> bool:
        """
        Detect if the assignment problem is infeasible due to infinite costs.
        
        Args:
            cost_matrix: The cost matrix to check
            inf_value: Value representing infinite cost
            
        Returns:
            True if infeasible assignment detected, False otherwise
        """
        # Count infinities in each row and column
        rows, cols = cost_matrix.shape
        inf_positions = np.isinf(cost_matrix) | (cost_matrix == inf_value)
        
        row_inf_counts = inf_positions.sum(axis=1)
        col_inf_counts = inf_positions.sum(axis=0)
        
        # Check if any row or column has all infinities
        infeasible_rows = np.where(row_inf_counts == cols)[0]
        infeasible_cols = np.where(col_inf_counts == rows)[0]
        
        is_infeasible = len(infeasible_rows) > 0 or len(infeasible_cols) > 0
        
        if is_infeasible:
            details = {
                'infeasible_rows': infeasible_rows.tolist(),
                'infeasible_cols': infeasible_cols.tolist()
            }
            self.detected_cases.append((EdgeCaseType.INFEASIBLE_ASSIGNMENT, details))
            logger.debug(f"Detected infeasible assignment: {details}")
            
        return is_infeasible
    
    def detect_multiple_optimal_solutions(self, 
                                         cost_matrix: np.ndarray,
                                         assignments: List[Tuple[int, int]],
                                         total_cost: float,
                                         tolerance: float = 1e-10) -> bool:
        """
        Detect if there are multiple optimal solutions with the same cost.
        
        Args:
            cost_matrix: The cost matrix
            assignments: The current optimal assignments
            total_cost: The total cost of the current assignments
            tolerance: Numerical tolerance for cost equality
            
        Returns:
            True if multiple optimal solutions detected, False otherwise
        """
        # Implement a simplified check for alternate optimal solutions
        # A complete check would require more sophisticated graph algorithms
        
        rows, cols = cost_matrix.shape
        assigned_rows = {row for row, _ in assignments}
        assigned_cols = {col for _, col in assignments}
        
        # Try simple row and column swaps to see if we can get the same cost
        for i in range(rows):
            for j in range(i + 1, rows):
                if i in assigned_rows and j in assigned_rows:
                    # Find the assigned columns for these rows
                    col_i = next(col for row, col in assignments if row == i)
                    col_j = next(col for row, col in assignments if row == j)
                    
                    # Calculate cost of swapping these assignments
                    current_cost = cost_matrix[i, col_i] + cost_matrix[j, col_j]
                    swapped_cost = cost_matrix[i, col_j] + cost_matrix[j, col_i]
                    
                    # If costs are the same (within tolerance), we have multiple optimal solutions
                    if abs(current_cost - swapped_cost) <= tolerance:
                        details = {
                            'swappable_rows': (i, j),
                            'swappable_cols': (col_i, col_j)
                        }
                        self.detected_cases.append((EdgeCaseType.MULTIPLE_OPTIMAL_SOLUTIONS, details))
                        logger.debug(f"Detected multiple optimal solutions: {details}")
                        return True
        
        return False
    
    def detect_preference_ties(self,
                              preferences: List[List[int]],
                              tie_threshold: float = 0.0) -> bool:
        """
        Detect if there are ties in the preference lists.
        
        Args:
            preferences: List of preference lists
            tie_threshold: Threshold for considering preferences tied
            
        Returns:
            True if preference ties detected, False otherwise
        """
        # In a proper implementation, the preferences would include scores/weights
        # For this simplified version, we assume ties are explicitly marked
        # by having the same index appear multiple times in a preference list
        
        has_ties = False
        tie_details = {}
        
        for i, prefs in enumerate(preferences):
            # Check for explicit duplicates
            seen = set()
            duplicates = []
            
            for p in prefs:
                if p in seen:
                    duplicates.append(p)
                else:
                    seen.add(p)
            
            if duplicates:
                has_ties = True
                tie_details[i] = duplicates
        
        if has_ties:
            self.detected_cases.append((EdgeCaseType.PREFERENCE_TIES, tie_details))
            logger.debug(f"Detected preference ties: {tie_details}")
            
        return has_ties
    
    def detect_all_edge_cases(self, 
                             cost_matrix: np.ndarray,
                             assignments: Optional[List[Tuple[int, int]]] = None,
                             total_cost: Optional[float] = None,
                             row_preferences: Optional[List[List[int]]] = None,
                             col_preferences: Optional[List[List[int]]] = None) -> List[EdgeCaseType]:
        """
        Detect all edge cases in the provided data.
        
        Args:
            cost_matrix: The cost matrix
            assignments: The current assignments, if available
            total_cost: The total cost of the assignments, if available
            row_preferences: Row preference lists, if available
            col_preferences: Column preference lists, if available
            
        Returns:
            List of detected edge case types
        """
        # Clear previous detections
        self.detected_cases = []
        
        # Detect various edge cases
        self.detect_non_square_matrix(cost_matrix)
        self.detect_infeasible_assignment(cost_matrix)
        
        if assignments is not None and total_cost is not None:
            self.detect_multiple_optimal_solutions(cost_matrix, assignments, total_cost)
        
        if row_preferences is not None:
            self.detect_preference_ties(row_preferences)
        
        if col_preferences is not None:
            self.detect_preference_ties(col_preferences)
        
        # Return unique edge case types
        return list({case_type for case_type, _ in self.detected_cases})
    
    def resolve(self, 
               case_type: EdgeCaseType, 
               cost_matrix: np.ndarray,
               context: Dict[str, Any],
               strategy: Optional[ResolutionStrategy] = None) -> np.ndarray:
        """
        Resolve an edge case with the specified or default strategy.
        
        Args:
            case_type: The edge case type to resolve
            cost_matrix: The cost matrix to modify
            context: Additional context for resolution
            strategy: Resolution strategy to use (uses default if None)
            
        Returns:
            Modified cost matrix after resolution
        """
        if case_type in self.custom_handlers:
            # Use custom handler if registered
            return self.custom_handlers[case_type](cost_matrix, context)
        
        # Use the specified or default strategy
        strategy = strategy or self.default_strategies.get(case_type)
        
        if strategy is None:
            logger.warning(f"No resolution strategy defined for {case_type}")
            return cost_matrix
        
        # Apply the appropriate resolution strategy
        if strategy == ResolutionStrategy.PAD_MATRIX:
            return self._pad_matrix(cost_matrix, context)
        elif strategy == ResolutionStrategy.GREEDY_ASSIGNMENT:
            return self._apply_greedy_costs(cost_matrix, context)
        elif strategy == ResolutionStrategy.USE_SECONDARY_CRITERIA:
            return self._apply_secondary_criteria(cost_matrix, context)
        elif strategy == ResolutionStrategy.PROPORTIONAL_SELECTION:
            return self._apply_proportional_weights(cost_matrix, context)
        elif strategy == ResolutionStrategy.SPLIT_ASSIGNMENT:
            return self._handle_disconnected_graph(cost_matrix, context)
        elif strategy == ResolutionStrategy.RANDOM_SELECTION:
            return self._apply_random_tiebreaker(cost_matrix, context)
        elif strategy == ResolutionStrategy.MANUAL_RESOLUTION:
            logger.warning("Manual resolution strategy requires custom handler")
            return cost_matrix
        else:
            logger.warning(f"Unknown resolution strategy: {strategy}")
            return cost_matrix
    
    def _pad_matrix(self, 
                   cost_matrix: np.ndarray, 
                   context: Dict[str, Any]) -> np.ndarray:
        """
        Pad a non-square matrix to make it square.
        
        Args:
            cost_matrix: The cost matrix to pad
            context: Additional context for padding
            
        Returns:
            Padded square matrix
        """
        rows, cols = cost_matrix.shape
        
        if rows == cols:
            return cost_matrix
        
        # Determine padding value (default to very high cost)
        pad_value = context.get('pad_value', 1e6)
        
        # Create square matrix of the larger dimension
        max_dim = max(rows, cols)
        padded_matrix = np.ones((max_dim, max_dim)) * pad_value
        
        # Copy original values
        padded_matrix[:rows, :cols] = cost_matrix
        
        logger.debug(f"Padded {rows}x{cols} matrix to {max_dim}x{max_dim}")
        
        return padded_matrix
    
    def _apply_greedy_costs(self, 
                           cost_matrix: np.ndarray, 
                           context: Dict[str, Any]) -> np.ndarray:
        """
        Apply greedy cost adjustments for infeasible assignments.
        
        Args:
            cost_matrix: The cost matrix to adjust
            context: Additional context for adjustment
            
        Returns:
            Adjusted cost matrix
        """
        inf_value = float('inf')
        high_value = context.get('high_cost_value', 1e6)
        
        # Replace infinities with high but finite values
        adjusted_matrix = np.copy(cost_matrix)
        adjusted_matrix[np.isinf(adjusted_matrix) | (adjusted_matrix == inf_value)] = high_value
        
        return adjusted_matrix
    
    def _apply_secondary_criteria(self, 
                                 cost_matrix: np.ndarray, 
                                 context: Dict[str, Any]) -> np.ndarray:
        """
        Apply secondary criteria to break ties in optimal solutions.
        
        Args:
            cost_matrix: The cost matrix to adjust
            context: Additional context including secondary criteria
            
        Returns:
            Adjusted cost matrix with secondary criteria applied
        """
        if 'secondary_matrix' not in context:
            logger.warning("Secondary criteria requested but no secondary_matrix provided")
            return cost_matrix
        
        secondary_matrix = context['secondary_matrix']
        secondary_weight = context.get('secondary_weight', 1e-4)
        
        # Ensure compatible dimensions
        if secondary_matrix.shape != cost_matrix.shape:
            logger.warning("Secondary matrix dimensions do not match cost matrix")
            return cost_matrix
        
        # Add scaled secondary criteria to break ties
        adjusted_matrix = cost_matrix + secondary_weight * secondary_matrix
        
        return adjusted_matrix
    
    def _apply_proportional_weights(self, 
                                  cost_matrix: np.ndarray, 
                                  context: Dict[str, Any]) -> np.ndarray:
        """
        Apply proportional weights to handle preference ties.
        
        Args:
            cost_matrix: The cost matrix to adjust
            context: Additional context including preference weights
            
        Returns:
            Adjusted cost matrix with proportional weights
        """
        if 'preference_weights' not in context:
            logger.warning("Proportional selection requested but no preference_weights provided")
            return cost_matrix
        
        weights = context['preference_weights']
        weight_factor = context.get('weight_factor', 1e-3)
        
        # Apply weights as a small adjustment to the cost matrix
        # In a real implementation, this would be more sophisticated
        # For now, just add a small random perturbation
        
        np.random.seed(context.get('random_seed', 42))
        noise = np.random.rand(*cost_matrix.shape) * weight_factor
        
        adjusted_matrix = cost_matrix + noise
        
        return adjusted_matrix
    
    def _apply_random_tiebreaker(self, 
                               cost_matrix: np.ndarray, 
                               context: Dict[str, Any]) -> np.ndarray:
        """
        Apply random small adjustments to break ties.
        
        Args:
            cost_matrix: The cost matrix to adjust
            context: Additional context including random seed
            
        Returns:
            Adjusted cost matrix with random tiebreakers
        """
        noise_level = context.get('random_noise_level', 1e-10)
        
        # Add very small random noise to break ties
        np.random.seed(context.get('random_seed', 42))
        noise = np.random.rand(*cost_matrix.shape) * noise_level
        
        adjusted_matrix = cost_matrix + noise
        
        return adjusted_matrix
    
    def _handle_disconnected_graph(self, 
                                 cost_matrix: np.ndarray, 
                                 context: Dict[str, Any]) -> np.ndarray:
        """
        Handle disconnected components in the assignment graph.
        
        Args:
            cost_matrix: The cost matrix to adjust
            context: Additional context for handling disconnected graph
            
        Returns:
            Adjusted cost matrix
        """
        # This is a simplified implementation
        # A full implementation would identify connected components
        # and handle them separately
        
        # For now, just ensure all elements are connected by replacing
        # infinite values with very high finite values
        inf_value = float('inf')
        high_value = context.get('high_cost_value', 1e6)
        
        adjusted_matrix = np.copy(cost_matrix)
        adjusted_matrix[np.isinf(adjusted_matrix) | (adjusted_matrix == inf_value)] = high_value
        
        return adjusted_matrix
    
    def get_detected_cases(self) -> List[Tuple[EdgeCaseType, Any]]:
        """
        Get the list of detected edge cases with details.
        
        Returns:
            List of tuples containing edge case type and details
        """
        return self.detected_cases
    
    def clear_detected_cases(self) -> None:
        """Clear the list of detected edge cases."""
        self.detected_cases = []