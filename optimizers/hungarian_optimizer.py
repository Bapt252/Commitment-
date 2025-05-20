"""Hungarian optimizer integration module.

This module integrates the Hungarian algorithm implementation with the
optimizer framework from Session 5, providing a seamless connection
between the matching capabilities and machine learning optimization.
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Set, Any, Optional, Union, Callable
import time
from pathlib import Path
import json

# Import from Session 5 optimizer module
from ..optimizers.base_optimizer import BaseOptimizer, OptimizationResult
from ..optimizers.ml_optimizer import MLOptimizer

# Import from Session 4 skills module
from ..skills.enhanced_skills import SkillSet, Skill

# Import from current session
from ..matching.optimal_matcher import OptimalMatcher
from ..hungarian.cost_matrix import CostMatrix
from ..constraints.constraint_validator import ConstraintValidator

logger = logging.getLogger(__name__)


class HungarianOptimizer(BaseOptimizer):
    """
    Hungarian algorithm optimizer that integrates with Session 5 ML optimizer.
    
    This class extends the base optimizer to provide Hungarian algorithm based
    optimization with support for skill matching and ML-enhanced optimization.
    """
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 use_ml: bool = True,
                 use_cache: bool = True,
                 cache_size: int = 128):
        """
        Initialize the Hungarian optimizer.
        
        Args:
            config_path: Path to configuration file
            use_ml: Whether to use machine learning for optimization
            use_cache: Whether to use caching
            cache_size: Size of the cache if enabled
        """
        super().__init__()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize matchers
        self.optimal_matcher = OptimalMatcher(
            use_bidirectional=self.config.get('use_bidirectional', False),
            cache_size=cache_size if use_cache else 0
        )
        
        # Initialize ML optimizer if enabled
        self.ml_optimizer = MLOptimizer() if use_ml else None
        
        # Set up constraint validator
        self.constraint_validator = ConstraintValidator()
        self.optimal_matcher.constraint_validator = self.constraint_validator
        
        # Set up constraint groups
        self._initialize_constraint_groups()
        
        # Performance tracking
        self.execution_times = []
        
        # Cache for cost matrices
        self.cost_matrix_cache = {}
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        default_config = {
            'use_bidirectional': False,
            'cost_weights': {
                'skill_match': 0.6,
                'preference_match': 0.3,
                'workload_balance': 0.1
            },
            'constraint_weights': {
                'required_skills': 1.0,
                'capacity': 0.8,
                'availability': 0.7,
                'performance': 0.5
            },
            'ml_parameters': {
                'learning_rate': 0.01,
                'regularization': 0.001,
                'max_iterations': 100
            }
        }
        
        if not config_path:
            return default_config
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Merge with defaults for any missing keys
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
                elif isinstance(value, dict) and isinstance(config[key], dict):
                    for sub_key, sub_value in value.items():
                        if sub_key not in config[key]:
                            config[key][sub_key] = sub_value
            
            logger.info(f"Loaded configuration from {config_path}")
            return config
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load configuration from {config_path}: {e}")
            logger.info("Using default configuration")
            return default_config
    
    def _initialize_constraint_groups(self) -> None:
        """Initialize constraint groups in the validator."""
        # Pre-computation constraints
        self.constraint_validator.create_group(
            name="pre_computation",
            description="Constraints to check before computation starts"
        )
        
        # Post-computation constraints
        self.constraint_validator.create_group(
            name="post_computation",
            description="Constraints to check after computation completes"
        )
        
        # Business rule constraints
        self.constraint_validator.create_group(
            name="business_rules",
            description="Constraints based on business rules"
        )
        
        # Performance constraints
        self.constraint_validator.create_group(
            name="performance",
            description="Constraints related to performance metrics"
        )
    
    def calculate_cost_matrix(self, 
                             skills: List[SkillSet],
                             tasks: List[SkillSet],
                             preferences: Optional[List[List[float]]] = None,
                             context: Optional[Dict[str, Any]] = None) -> np.ndarray:
        """
        Calculate the cost matrix based on skills and preferences.
        
        Args:
            skills: List of skill sets for resources
            tasks: List of skill sets for tasks
            preferences: Optional matrix of resource-task preferences
            context: Additional context for calculation
            
        Returns:
            Cost matrix for Hungarian algorithm
        """
        # Create cache key
        cache_key = (
            tuple(hash(skill) for skill in skills),
            tuple(hash(task) for task in tasks),
            None if preferences is None else tuple(tuple(row) for row in preferences)
        )
        
        # Check cache
        if cache_key in self.cost_matrix_cache:
            return self.cost_matrix_cache[cache_key]
        
        # Initialize context
        if context is None:
            context = {}
        
        # Get weights from config
        weights = self.config.get('cost_weights', {})
        skill_weight = weights.get('skill_match', 0.6)
        preference_weight = weights.get('preference_match', 0.3)
        workload_weight = weights.get('workload_balance', 0.1)
        
        # Get dimensions
        num_resources = len(skills)
        num_tasks = len(tasks)
        
        # Initialize cost matrix
        cost_matrix = np.zeros((num_resources, num_tasks))
        
        # Calculate skill match costs
        for i in range(num_resources):
            for j in range(num_tasks):
                # Calculate skill match score (higher is better)
                skill_match = skills[i].match_score(tasks[j])
                
                # Convert to cost (lower is better)
                skill_cost = 1.0 - skill_match
                
                # Add to cost matrix with weight
                cost_matrix[i, j] += skill_weight * skill_cost
        
        # Add preference costs if provided
        if preferences is not None and len(preferences) == num_resources:
            for i in range(num_resources):
                pref_row = preferences[i]
                
                if len(pref_row) == num_tasks:
                    # Normalize preferences to [0, 1]
                    pref_min = min(pref_row)
                    pref_max = max(pref_row)
                    pref_range = pref_max - pref_min
                    
                    if pref_range > 0:
                        normalized_prefs = [(p - pref_min) / pref_range for p in pref_row]
                    else:
                        normalized_prefs = [0.5 for _ in pref_row]
                    
                    # Add to cost matrix (inverted and weighted)
                    for j in range(num_tasks):
                        cost_matrix[i, j] += preference_weight * (1.0 - normalized_prefs[j])
        
        # Add workload balance factor if available in context
        if 'workloads' in context and isinstance(context['workloads'], list):
            workloads = context['workloads']
            
            if len(workloads) == num_resources:
                # Normalize workloads to [0, 1]
                min_load = min(workloads)
                max_load = max(workloads)
                load_range = max_load - min_load
                
                if load_range > 0:
                    normalized_loads = [(load - min_load) / load_range for load in workloads]
                else:
                    normalized_loads = [0.5 for _ in workloads]
                
                # Add to cost matrix (weighted)
                for i in range(num_resources):
                    for j in range(num_tasks):
                        cost_matrix[i, j] += workload_weight * normalized_loads[i]
        
        # Apply ML optimization if enabled
        if self.ml_optimizer is not None and 'historical_assignments' in context:
            # Extract historical data
            historical = context['historical_assignments']
            
            # Let ML optimizer adjust the cost matrix
            cost_matrix = self.ml_optimizer.optimize_cost_matrix(
                cost_matrix, 
                historical,
                learning_rate=self.config.get('ml_parameters', {}).get('learning_rate', 0.01),
                regularization=self.config.get('ml_parameters', {}).get('regularization', 0.001),
                max_iterations=self.config.get('ml_parameters', {}).get('max_iterations', 100)
            )
        
        # Store in cache
        self.cost_matrix_cache[cache_key] = cost_matrix
        
        return cost_matrix
    
    def optimize(self, 
                skills: List[SkillSet],
                tasks: List[SkillSet],
                preferences: Optional[List[List[float]]] = None,
                constraints: Optional[List[Any]] = None,
                context: Optional[Dict[str, Any]] = None) -> OptimizationResult:
        """
        Optimize the assignment of resources to tasks.
        
        Args:
            skills: List of skill sets for resources
            tasks: List of skill sets for tasks
            preferences: Optional matrix of resource-task preferences
            constraints: Optional list of constraints to apply
            context: Additional context for optimization
            
        Returns:
            Optimization result with assignments and metrics
        """
        start_time = time.time()
        
        # Initialize context
        if context is None:
            context = {}
        
        # Add timestamp
        context['timestamp'] = start_time
        
        # Calculate cost matrix
        cost_matrix = self.calculate_cost_matrix(skills, tasks, preferences, context)
        
        # Apply constraints
        if constraints:
            for constraint in constraints:
                self.optimal_matcher.add_constraint(constraint)
        
        # Update context with matrices for constraints
        context['cost_matrix'] = cost_matrix
        
        # Generate preference lists for bidirectional matching if needed
        row_preferences = None
        col_preferences = None
        
        if self.config.get('use_bidirectional', False):
            # Create preference lists from cost matrix (lower cost = higher preference)
            row_preferences = []
            for i in range(cost_matrix.shape[0]):
                row_costs = [(j, cost_matrix[i, j]) for j in range(cost_matrix.shape[1])]
                row_costs.sort(key=lambda x: x[1])  # Sort by cost
                row_preferences.append([j for j, _ in row_costs])  # Keep only indices
            
            col_preferences = []
            for j in range(cost_matrix.shape[1]):
                col_costs = [(i, cost_matrix[i, j]) for i in range(cost_matrix.shape[0])]
                col_costs.sort(key=lambda x: x[1])  # Sort by cost
                col_preferences.append([i for i, _ in col_costs])  # Keep only indices
        
        # Perform matching
        assignments, total_cost = self.optimal_matcher.match(
            cost_matrix, 
            row_preferences, 
            col_preferences, 
            context
        )
        
        # Calculate end time
        end_time = time.time()
        execution_time = end_time - start_time
        self.execution_times.append(execution_time)
        
        # Create result
        result = OptimizationResult(
            assignments=assignments,
            total_cost=total_cost,
            execution_time=execution_time,
            constraint_violations=self._count_constraint_violations(),
            metadata={
                'algorithm': 'Hungarian',
                'matrix_size': cost_matrix.shape,
                'use_ml': self.ml_optimizer is not None,
                'use_bidirectional': self.config.get('use_bidirectional', False)
            }
        )
        
        return result
    
    def _count_constraint_violations(self) -> int:
        """
        Count the number of constraint violations.
        
        Returns:
            Number of constraint violations
        """
        total_violations = 0
        
        for group_name in self.constraint_validator.groups:
            history = self.constraint_validator.get_validation_history(
                group_name, only_violations=True
            )
            total_violations += sum(r['violation_count'] for r in history)
        
        return total_violations
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.
        
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
            'last_time': self.execution_times[-1]
        }
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self.cost_matrix_cache.clear()
        
        if hasattr(self.optimal_matcher, 'clear_cache'):
            self.optimal_matcher.clear_cache()
        
        logger.info("Caches cleared")
    
    def get_constraint_report(self) -> Dict[str, Any]:
        """
        Get a report of constraint validations.
        
        Returns:
            Constraint validation report
        """
        return self.constraint_validator.generate_report()