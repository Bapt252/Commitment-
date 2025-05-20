"""Constraint validator module for Hungarian algorithm.

This module provides facilities to validate constraints and group them
into logical sets that can be applied, tracked, and reported together.
"""

from enum import Enum, auto
from typing import Dict, List, Set, Any, Optional, Union, Tuple, Callable
import logging
from collections import defaultdict

from .base_constraints import BaseConstraint, ConstraintViolationError, ConstraintPriority

logger = logging.getLogger(__name__)


class ConstraintValidationLevel(Enum):
    """Defines validation levels for constraint checking."""
    STRICT = auto()  # Fail on any constraint violation
    RELAXED = auto()  # Apply penalties for soft constraints, fail on hard constraints
    REPORT_ONLY = auto()  # Only report violations, never fail


class ConstraintGroup:
    """Represents a logical grouping of related constraints."""
    
    def __init__(self, 
                 name: str, 
                 description: str = "",
                 validation_level: ConstraintValidationLevel = ConstraintValidationLevel.RELAXED):
        """
        Initialize a constraint group.
        
        Args:
            name: Name of the constraint group
            description: Description of the purpose of the group
            validation_level: Default validation level for the group
        """
        self.name = name
        self.description = description
        self.validation_level = validation_level
        self.constraints: List[BaseConstraint] = []
        
    def add_constraint(self, constraint: BaseConstraint) -> None:
        """
        Add a constraint to the group.
        
        Args:
            constraint: The constraint to add
        """
        self.constraints.append(constraint)
        
    def add_constraints(self, constraints: List[BaseConstraint]) -> None:
        """
        Add multiple constraints to the group.
        
        Args:
            constraints: List of constraints to add
        """
        self.constraints.extend(constraints)
        
    def validate(self, context: Dict[str, Any]) -> Tuple[bool, List[BaseConstraint], float]:
        """
        Validate all constraints in the group against a context.
        
        Args:
            context: The context to validate against
            
        Returns:
            Tuple containing:
            - Boolean indicating overall validity
            - List of violated constraints
            - Total penalty from all violations
        
        Raises:
            ConstraintViolationError: If validation_level is STRICT and any constraints are violated
        """
        violations = []
        total_penalty = 0.0
        
        for constraint in self.constraints:
            if not constraint.check(context):
                violations.append(constraint)
                penalty = constraint.calculate_penalty(context)
                total_penalty += penalty
                
                logger.debug(f"Constraint violation: {constraint}, penalty: {penalty}")
        
        is_valid = len(violations) == 0
        
        # Handle violations based on validation level
        if not is_valid and self.validation_level == ConstraintValidationLevel.STRICT:
            critical_violations = [str(c) for c in violations 
                                 if c.priority in (ConstraintPriority.HIGH, ConstraintPriority.CRITICAL)]
            if critical_violations:
                raise ConstraintViolationError(
                    f"Constraints violated in group '{self.name}': {', '.join(critical_violations)}"
                )
        
        return is_valid, violations, total_penalty
    
    def __str__(self) -> str:
        return f"ConstraintGroup('{self.name}', {len(self.constraints)} constraints)"


class ConstraintValidator:
    """Central validator for managing and checking multiple constraint groups."""
    
    def __init__(self, 
                 default_validation_level: ConstraintValidationLevel = ConstraintValidationLevel.RELAXED):
        """
        Initialize the constraint validator.
        
        Args:
            default_validation_level: Default validation level for constraint groups
        """
        self.groups: Dict[str, ConstraintGroup] = {}
        self.default_validation_level = default_validation_level
        self.validation_history: List[Dict[str, Any]] = []
        
    def create_group(self, 
                     name: str, 
                     description: str = "", 
                     validation_level: Optional[ConstraintValidationLevel] = None) -> ConstraintGroup:
        """
        Create a new constraint group.
        
        Args:
            name: Name of the constraint group
            description: Description of the purpose of the group
            validation_level: Validation level for the group (uses default if None)
            
        Returns:
            Newly created constraint group
            
        Raises:
            ValueError: If a group with the given name already exists
        """
        if name in self.groups:
            raise ValueError(f"Constraint group '{name}' already exists")
            
        level = validation_level if validation_level is not None else self.default_validation_level
        group = ConstraintGroup(name, description, level)
        self.groups[name] = group
        return group
    
    def get_group(self, name: str) -> ConstraintGroup:
        """
        Get a constraint group by name.
        
        Args:
            name: Name of the constraint group
            
        Returns:
            The constraint group
            
        Raises:
            KeyError: If no group with the given name exists
        """
        if name not in self.groups:
            raise KeyError(f"Constraint group '{name}' does not exist")
            
        return self.groups[name]
    
    def validate_group(self, 
                       group_name: str, 
                       context: Dict[str, Any],
                       record_history: bool = True) -> Tuple[bool, List[BaseConstraint], float]:
        """
        Validate all constraints in a specific group.
        
        Args:
            group_name: Name of the group to validate
            context: Context to validate against
            record_history: Whether to record validation results in history
            
        Returns:
            Tuple containing:
            - Boolean indicating overall validity
            - List of violated constraints
            - Total penalty from all violations
        """
        group = self.get_group(group_name)
        is_valid, violations, penalty = group.validate(context)
        
        if record_history:
            self._record_validation(group_name, is_valid, violations, penalty, context)
            
        return is_valid, violations, penalty
    
    def validate_all(self, 
                     context: Dict[str, Any],
                     record_history: bool = True) -> Dict[str, Tuple[bool, List[BaseConstraint], float]]:
        """
        Validate all constraints in all groups.
        
        Args:
            context: Context to validate against
            record_history: Whether to record validation results in history
            
        Returns:
            Dictionary mapping group names to validation results
        """
        results = {}
        
        for group_name, group in self.groups.items():
            try:
                is_valid, violations, penalty = group.validate(context)
                results[group_name] = (is_valid, violations, penalty)
                
                if record_history:
                    self._record_validation(group_name, is_valid, violations, penalty, context)
                    
            except ConstraintViolationError as e:
                # Re-raise error with additional context
                raise ConstraintViolationError(f"In group '{group_name}': {str(e)}") from e
            
        return results
    
    def _record_validation(self, 
                          group_name: str, 
                          is_valid: bool, 
                          violations: List[BaseConstraint],
                          penalty: float,
                          context: Dict[str, Any]) -> None:
        """
        Record validation results in history.
        
        Args:
            group_name: Name of the validated group
            is_valid: Overall validity result
            violations: List of violated constraints
            penalty: Total penalty from violations
            context: Validation context
        """
        # Create a lightweight copy of the context to avoid storing large objects
        context_copy = {}
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool, type(None))):
                context_copy[key] = value
            else:
                context_copy[key] = f"{type(value).__name__} instance"
        
        record = {
            'timestamp': context.get('timestamp', None),
            'group': group_name,
            'is_valid': is_valid,
            'violation_count': len(violations),
            'violations': [str(v) for v in violations],
            'penalty': penalty,
            'context': context_copy
        }
        
        self.validation_history.append(record)
    
    def get_validation_history(self, 
                              group_name: Optional[str] = None, 
                              only_violations: bool = False) -> List[Dict[str, Any]]:
        """
        Get validation history, optionally filtered.
        
        Args:
            group_name: If provided, only return history for this group
            only_violations: If True, only return records with violations
            
        Returns:
            List of validation history records
        """
        filtered = self.validation_history
        
        if group_name is not None:
            filtered = [r for r in filtered if r['group'] == group_name]
            
        if only_violations:
            filtered = [r for r in filtered if not r['is_valid']]
            
        return filtered
    
    def generate_report(self, 
                        include_history: bool = True,
                        group_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive report of constraints and their validation status.
        
        Args:
            include_history: Whether to include validation history
            group_name: If provided, only report on this group
            
        Returns:
            Dictionary containing the report
        """
        report = {
            'groups': {},
            'overall_stats': {
                'total_groups': 0,
                'total_constraints': 0,
                'groups_with_violations': 0,
                'total_violations': 0
            }
        }
        
        # Filter groups if needed
        groups_to_report = {group_name: self.groups[group_name]} if group_name else self.groups
        
        # Process each group
        for name, group in groups_to_report.items():
            group_report = {
                'name': name,
                'description': group.description,
                'validation_level': group.validation_level.name,
                'constraint_count': len(group.constraints),
                'constraints': [str(c) for c in group.constraints]
            }
            
            report['groups'][name] = group_report
            report['overall_stats']['total_groups'] += 1
            report['overall_stats']['total_constraints'] += len(group.constraints)
        
        # Include history if requested
        if include_history:
            history = self.get_validation_history(group_name)
            
            # Summarize history
            violations_by_group = defaultdict(int)
            for record in history:
                if not record['is_valid']:
                    violations_by_group[record['group']] += record['violation_count']
            
            report['overall_stats']['groups_with_violations'] = len(violations_by_group)
            report['overall_stats']['total_violations'] = sum(violations_by_group.values())
            
            for group, violations in violations_by_group.items():
                if group in report['groups']:
                    report['groups'][group]['violation_count'] = violations
            
            # Include detailed history records
            report['history'] = history
            
        return report


class CompoundConstraint(BaseConstraint):
    """A constraint that combines multiple other constraints with logical operations."""
    
    def __init__(self, 
                 constraints: List[BaseConstraint],
                 operation: str = 'AND',
                 priority: ConstraintPriority = ConstraintPriority.MEDIUM,
                 penalty_factor: float = 1.0):
        """
        Initialize a compound constraint.
        
        Args:
            constraints: List of constraints to combine
            operation: Logical operation, 'AND' or 'OR'
            priority: Priority level for this constraint
            penalty_factor: Factor applied to cost when constraint is violated
        """
        super().__init__(priority=priority, penalty_factor=penalty_factor)
        self.constraints = constraints
        self.operation = operation.upper()
        
        if self.operation not in ('AND', 'OR'):
            raise ValueError("Operation must be 'AND' or 'OR'")
    
    def check(self, context: Dict[str, Any]) -> bool:
        """
        Check if the compound constraint is satisfied.
        
        Args:
            context: Execution context
            
        Returns:
            True if constraint is satisfied, False otherwise
        """
        if self.operation == 'AND':
            return all(constraint.check(context) for constraint in self.constraints)
        else:  # 'OR'
            return any(constraint.check(context) for constraint in self.constraints)
    
    def calculate_penalty(self, context: Dict[str, Any]) -> float:
        """
        Calculate penalty for compound constraint violation.
        
        Args:
            context: Execution context
            
        Returns:
            Combined penalty from all violated constraints
        """
        penalties = [constraint.calculate_penalty(context) for constraint in self.constraints]
        
        if self.operation == 'AND':
            # For AND, sum all penalties
            return self.penalty_factor * sum(penalties)
        else:  # 'OR'
            # For OR, take minimum penalty (if any constraint is satisfied, penalty is 0)
            if self.check(context):
                return 0.0
            else:
                return self.penalty_factor * min(penalties) if penalties else 0.0
    
    def __str__(self) -> str:
        constraint_strs = [str(c) for c in self.constraints]
        op_str = f" {self.operation} ".join(constraint_strs)
        return f"({op_str})"