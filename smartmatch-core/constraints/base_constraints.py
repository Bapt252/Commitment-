#!/usr/bin/env python3
"""
Session 6: Base Constraints Module
==================================

Classes de base abstraites pour le système de contraintes.
Définit l'architecture fondamentale pour toutes les contraintes du système.

🔥 Classes principales:
- BaseConstraint: Classe abstraite de base
- HardConstraint: Contrainte éliminatoire
- SoftConstraint: Contrainte avec pénalité
- ConstraintResult: Résultat d'évaluation
- CompositeConstraint: Contrainte composite (AND/OR)

Architecture SOLID respectée pour extensibilité maximale.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import time
import uuid

# Configuration du logging
logger = logging.getLogger(__name__)

class ConstraintType(Enum):
    """Types de contraintes disponibles."""
    HARD = "hard"        # Éliminatoire (candidat rejeté si violée)
    SOFT = "soft"        # Pénalité (score réduit si violée)
    PREFERENCE = "preference"  # Simple préférence (bonus si satisfaite)

class ConstraintPriority(Enum):
    """Priorités des contraintes."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ConstraintScope(Enum):
    """Portée d'application des contraintes."""
    CANDIDATE = "candidate"      # S'applique aux candidats
    JOB = "job"                 # S'applique aux jobs
    PAIR = "pair"               # S'applique aux paires candidat-job
    GLOBAL = "global"           # S'applique au matching global

class ConstraintStatus(Enum):
    """Statut d'une contrainte."""
    ENABLED = "enabled"
    DISABLED = "disabled"
    SUSPENDED = "suspended"     # Temporairement désactivée

@dataclass
class ConstraintResult:
    """
    Résultat de l'évaluation d'une contrainte.
    
    Attributes:
        satisfied: True si la contrainte est satisfaite
        penalty: Pénalité appliquée (pour contraintes soft)
        confidence: Niveau de confiance dans l'évaluation [0, 1]
        message: Message explicatif
        details: Informations détaillées supplémentaires
        metadata: Métadonnées pour debugging/analytics
    """
    satisfied: bool
    penalty: float = 0.0
    confidence: float = 1.0
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validation des résultats."""
        # Validation de base
        if self.penalty < 0:
            logger.warning(f"Negative penalty: {self.penalty}")
            self.penalty = 0.0
        
        if not 0 <= self.confidence <= 1:
            logger.warning(f"Invalid confidence: {self.confidence}")
            self.confidence = max(0.0, min(1.0, self.confidence))
        
        # Cohérence logique
        if self.satisfied and self.penalty > 0:
            logger.warning("Constraint satisfied but penalty > 0")
    
    def __str__(self) -> str:
        status = "✓" if self.satisfied else "✗"
        return f"{status} {self.message} (penalty: {self.penalty:.3f}, confidence: {self.confidence:.3f})"

class BaseConstraint(ABC):
    """
    Classe de base abstraite pour toutes les contraintes.
    
    Implémente l'interface commune et les fonctionnalités de base.
    Toutes les contraintes spécifiques doivent hériter de cette classe.
    """
    
    def __init__(self, 
                 name: str,
                 constraint_type: ConstraintType,
                 priority: ConstraintPriority = ConstraintPriority.MEDIUM,
                 scope: ConstraintScope = ConstraintScope.PAIR,
                 description: str = "",
                 tags: Optional[List[str]] = None):
        """
        Initialise une contrainte de base.
        
        Args:
            name: Nom unique de la contrainte
            constraint_type: Type de contrainte (HARD/SOFT/PREFERENCE)
            priority: Priorité d'évaluation
            scope: Portée d'application
            description: Description de la contrainte
            tags: Tags pour catégorisation
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.constraint_type = constraint_type
        self.priority = priority
        self.scope = scope
        self.description = description
        self.tags = tags or []
        
        # État de la contrainte
        self.status = ConstraintStatus.ENABLED
        self.created_at = time.time()
        self.last_evaluated_at: Optional[float] = None
        
        # Statistiques d'évaluation
        self.evaluation_count = 0
        self.satisfaction_count = 0
        self.average_penalty = 0.0
        self.average_evaluation_time = 0.0
        
        # Configuration
        self.cache_results = False
        self.max_penalty = float('inf')
        self.weight = 1.0
        
        # Cache pour optimisation
        self._result_cache: Dict[str, ConstraintResult] = {}
        
        logger.debug(f"Created constraint: {self}")
    
    @abstractmethod
    def evaluate(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]] = None) -> ConstraintResult:
        """
        Évalue la contrainte pour une paire candidat-job.
        
        Args:
            candidate: Objet candidat
            job: Objet job
            context: Contexte d'évaluation (optionnel)
            
        Returns:
            ConstraintResult avec le résultat de l'évaluation
        """
        pass
    
    def is_enabled(self) -> bool:
        """Vérifie si la contrainte est activée."""
        return self.status == ConstraintStatus.ENABLED
    
    def enable(self) -> None:
        """Active la contrainte."""
        old_status = self.status
        self.status = ConstraintStatus.ENABLED
        if old_status != ConstraintStatus.ENABLED:
            logger.info(f"Constraint '{self.name}' enabled")
    
    def disable(self) -> None:
        """Désactive la contrainte."""
        old_status = self.status
        self.status = ConstraintStatus.DISABLED
        if old_status != ConstraintStatus.DISABLED:
            logger.info(f"Constraint '{self.name}' disabled")
    
    def suspend(self) -> None:
        """Suspend temporairement la contrainte."""
        old_status = self.status
        self.status = ConstraintStatus.SUSPENDED
        if old_status != ConstraintStatus.SUSPENDED:
            logger.info(f"Constraint '{self.name}' suspended")
    
    def evaluate_with_tracking(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]] = None) -> ConstraintResult:
        """
        Évalue la contrainte avec suivi des statistiques.
        
        Args:
            candidate: Objet candidat
            job: Objet job
            context: Contexte d'évaluation
            
        Returns:
            ConstraintResult avec le résultat de l'évaluation
        """
        if not self.is_enabled():
            return ConstraintResult(
                satisfied=True,
                message=f"Constraint '{self.name}' is disabled",
                metadata={'status': self.status.value}
            )
        
        # Cache check
        if self.cache_results:
            cache_key = self._generate_cache_key(candidate, job, context)
            if cache_key in self._result_cache:
                logger.debug(f"Cache hit for constraint '{self.name}'")
                return self._result_cache[cache_key]
        
        # Évaluation avec timing
        start_time = time.time()
        try:
            result = self.evaluate(candidate, job, context)
        except Exception as e:
            logger.error(f"Error evaluating constraint '{self.name}': {e}")
            result = ConstraintResult(
                satisfied=False,
                penalty=self.max_penalty,
                confidence=0.0,
                message=f"Evaluation error: {str(e)}",
                metadata={'error': str(e)}
            )
        
        evaluation_time = time.time() - start_time
        
        # Mise à jour des statistiques
        self._update_statistics(result, evaluation_time)
        
        # Ajout de métadonnées
        result.metadata.update({
            'constraint_id': self.id,
            'constraint_name': self.name,
            'evaluation_time': evaluation_time,
            'evaluation_count': self.evaluation_count
        })
        
        # Cache du résultat
        if self.cache_results:
            self._result_cache[cache_key] = result
        
        return result
    
    def _generate_cache_key(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]]) -> str:
        """Génère une clé de cache pour l'évaluation."""
        candidate_id = getattr(candidate, 'id', id(candidate))
        job_id = getattr(job, 'id', id(job))
        context_hash = hash(str(sorted(context.items()))) if context else 0
        return f"{self.id}_{candidate_id}_{job_id}_{context_hash}"
    
    def _update_statistics(self, result: ConstraintResult, evaluation_time: float) -> None:
        """Met à jour les statistiques d'évaluation."""
        self.evaluation_count += 1
        
        if result.satisfied:
            self.satisfaction_count += 1
        
        # Moyenne mobile des pénalités
        alpha = 0.1  # Facteur de lissage
        self.average_penalty = (1 - alpha) * self.average_penalty + alpha * result.penalty
        
        # Moyenne mobile du temps d'évaluation
        self.average_evaluation_time = (1 - alpha) * self.average_evaluation_time + alpha * evaluation_time
        
        self.last_evaluated_at = time.time()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de la contrainte."""
        satisfaction_rate = self.satisfaction_count / self.evaluation_count if self.evaluation_count > 0 else 0
        
        return {
            'name': self.name,
            'type': self.constraint_type.value,
            'priority': self.priority.value,
            'scope': self.scope.value,
            'status': self.status.value,
            'evaluation_count': self.evaluation_count,
            'satisfaction_rate': satisfaction_rate,
            'average_penalty': self.average_penalty,
            'average_evaluation_time': self.average_evaluation_time,
            'cache_size': len(self._result_cache),
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.created_at))
        }
    
    def clear_cache(self) -> None:
        """Vide le cache de résultats."""
        cache_size = len(self._result_cache)
        self._result_cache.clear()
        logger.debug(f"Cleared cache for constraint '{self.name}' ({cache_size} entries)")
    
    def clone(self) -> 'BaseConstraint':
        """Crée une copie de la contrainte."""
        # Doit être implémenté par les classes dérivées pour une copie complète
        raise NotImplementedError("Clone method must be implemented by subclasses")
    
    def __str__(self) -> str:
        status_icon = {
            ConstraintStatus.ENABLED: "✅",
            ConstraintStatus.DISABLED: "❌",
            ConstraintStatus.SUSPENDED: "⏸️"
        }
        return f"{status_icon[self.status]} {self.name} ({self.constraint_type.value}, {self.priority.name})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', type={self.constraint_type.value})>"

class HardConstraint(BaseConstraint):
    """
    Contrainte hard (éliminatoire).
    
    Si violée, la paire candidat-job est automatiquement rejetée.
    Aucune pénalité n'est calculée, seule la satisfaction compte.
    """
    
    def __init__(self, name: str, **kwargs):
        # Force le type à HARD
        kwargs['constraint_type'] = ConstraintType.HARD
        super().__init__(name, **kwargs)
        
        # Les contraintes hard n'ont pas de pénalité maximale
        self.max_penalty = 0.0

class SoftConstraint(BaseConstraint):
    """
    Contrainte soft (avec pénalité).
    
    Si violée, applique une pénalité au score de matching.
    La paire peut toujours être sélectionnée avec un score réduit.
    """
    
    def __init__(self, 
                 name: str,
                 max_penalty: float = 1.0,
                 penalty_function: Optional[Callable[[float], float]] = None,
                 **kwargs):
        # Force le type à SOFT
        kwargs['constraint_type'] = ConstraintType.SOFT
        super().__init__(name, **kwargs)
        
        self.max_penalty = max_penalty
        self.penalty_function = penalty_function or self._linear_penalty
    
    def _linear_penalty(self, violation_degree: float) -> float:
        """Fonction de pénalité linéaire par défaut."""
        return min(self.max_penalty, violation_degree * self.max_penalty)
    
    def calculate_penalty(self, violation_degree: float) -> float:
        """
        Calcule la pénalité basée sur le degré de violation.
        
        Args:
            violation_degree: Degré de violation [0, 1]
            
        Returns:
            Pénalité calculée
        """
        if violation_degree <= 0:
            return 0.0
        
        penalty = self.penalty_function(violation_degree)
        return min(penalty, self.max_penalty)

class PreferenceConstraint(BaseConstraint):
    """
    Contrainte de préférence.
    
    Applique un bonus au score si la condition est satisfaite.
    N'élimine jamais une paire, améliore seulement le score.
    """
    
    def __init__(self, 
                 name: str,
                 max_bonus: float = 0.5,
                 **kwargs):
        # Force le type à PREFERENCE
        kwargs['constraint_type'] = ConstraintType.PREFERENCE
        super().__init__(name, **kwargs)
        
        self.max_bonus = max_bonus
        # Pour les préférences, penalty négative = bonus
        self.max_penalty = -max_bonus

class CompositeConstraint(BaseConstraint):
    """
    Contrainte composite combinant plusieurs contraintes.
    
    Supporte les opérateurs logiques AND, OR, NOT.
    """
    
    def __init__(self, 
                 name: str,
                 constraints: List[BaseConstraint],
                 operator: str = "AND",
                 **kwargs):
        super().__init__(name, **kwargs)
        
        self.constraints = constraints
        self.operator = operator.upper()
        
        if self.operator not in ["AND", "OR", "NOT"]:
            raise ValueError(f"Invalid operator: {self.operator}")
        
        if self.operator == "NOT" and len(constraints) != 1:
            raise ValueError("NOT operator requires exactly one constraint")
    
    def evaluate(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]] = None) -> ConstraintResult:
        """Évalue la contrainte composite."""
        if not self.constraints:
            return ConstraintResult(satisfied=True, message="No constraints to evaluate")
        
        # Évaluer toutes les contraintes enfants
        results = []
        for constraint in self.constraints:
            if constraint.is_enabled():
                result = constraint.evaluate_with_tracking(candidate, job, context)
                results.append(result)
        
        if not results:
            return ConstraintResult(satisfied=True, message="No enabled constraints")
        
        # Appliquer l'opérateur logique
        if self.operator == "AND":
            return self._evaluate_and(results)
        elif self.operator == "OR":
            return self._evaluate_or(results)
        elif self.operator == "NOT":
            return self._evaluate_not(results[0])
        
        # Fallback
        return ConstraintResult(satisfied=True, message="Unknown operator")
    
    def _evaluate_and(self, results: List[ConstraintResult]) -> ConstraintResult:
        """Évalue l'opérateur AND."""
        satisfied = all(r.satisfied for r in results)
        total_penalty = sum(r.penalty for r in results)
        average_confidence = sum(r.confidence for r in results) / len(results)
        
        messages = [r.message for r in results if r.message]
        message = f"AND: {' AND '.join(messages)}" if messages else "All constraints satisfied"
        
        return ConstraintResult(
            satisfied=satisfied,
            penalty=total_penalty,
            confidence=average_confidence,
            message=message,
            details={'operator': 'AND', 'child_results': results}
        )
    
    def _evaluate_or(self, results: List[ConstraintResult]) -> ConstraintResult:
        """Évalue l'opérateur OR."""
        satisfied = any(r.satisfied for r in results)
        min_penalty = min(r.penalty for r in results)
        max_confidence = max(r.confidence for r in results)
        
        satisfied_messages = [r.message for r in results if r.satisfied and r.message]
        if satisfied_messages:
            message = f"OR: {satisfied_messages[0]}"
        else:
            messages = [r.message for r in results if r.message]
            message = f"OR: {' OR '.join(messages)}" if messages else "No constraints satisfied"
        
        return ConstraintResult(
            satisfied=satisfied,
            penalty=min_penalty,
            confidence=max_confidence,
            message=message,
            details={'operator': 'OR', 'child_results': results}
        )
    
    def _evaluate_not(self, result: ConstraintResult) -> ConstraintResult:
        """Évalue l'opérateur NOT."""
        satisfied = not result.satisfied
        penalty = 0.0 if satisfied else self.max_penalty
        
        message = f"NOT: {result.message}"
        
        return ConstraintResult(
            satisfied=satisfied,
            penalty=penalty,
            confidence=result.confidence,
            message=message,
            details={'operator': 'NOT', 'child_result': result}
        )
    
    def clone(self) -> 'CompositeConstraint':
        """Crée une copie de la contrainte composite."""
        cloned_constraints = [constraint.clone() for constraint in self.constraints]
        return CompositeConstraint(
            name=f"{self.name}_clone",
            constraints=cloned_constraints,
            operator=self.operator,
            constraint_type=self.constraint_type,
            priority=self.priority,
            scope=self.scope,
            description=self.description,
            tags=self.tags.copy()
        )

# ===========================================
# FONCTIONS UTILITAIRES
# ===========================================

def create_constraint_group(name: str, 
                           constraints: List[BaseConstraint],
                           operator: str = "AND") -> CompositeConstraint:
    """
    Crée un groupe de contraintes avec un opérateur logique.
    
    Args:
        name: Nom du groupe
        constraints: Liste des contraintes
        operator: Opérateur logique (AND/OR/NOT)
        
    Returns:
        CompositeConstraint représentant le groupe
    """
    return CompositeConstraint(
        name=name,
        constraints=constraints,
        operator=operator,
        description=f"Group of {len(constraints)} constraints with {operator} operator"
    )

def validate_constraint_definition(constraint: BaseConstraint) -> List[str]:
    """
    Valide la définition d'une contrainte.
    
    Args:
        constraint: Contrainte à valider
        
    Returns:
        Liste des erreurs de validation
    """
    errors = []
    
    # Validation du nom
    if not constraint.name or not constraint.name.strip():
        errors.append("Constraint name is required")
    
    # Validation des types énumérés
    if constraint.constraint_type not in ConstraintType:
        errors.append(f"Invalid constraint type: {constraint.constraint_type}")
    
    if constraint.priority not in ConstraintPriority:
        errors.append(f"Invalid priority: {constraint.priority}")
    
    if constraint.scope not in ConstraintScope:
        errors.append(f"Invalid scope: {constraint.scope}")
    
    # Validation du poids
    if constraint.weight < 0:
        errors.append("Constraint weight must be non-negative")
    
    # Validation spécifique aux contraintes soft
    if isinstance(constraint, SoftConstraint):
        if constraint.max_penalty < 0:
            errors.append("Max penalty must be non-negative")
    
    return errors

if __name__ == "__main__":
    # Tests basiques
    print("🧪 Testing Base Constraints")
    
    # Test de création de contrainte simple
    class TestConstraint(HardConstraint):
        def evaluate(self, candidate, job, context=None):
            return ConstraintResult(satisfied=True, message="Test OK")
    
    constraint = TestConstraint("test_constraint")
    print(f"Created: {constraint}")
    
    # Test d'évaluation
    result = constraint.evaluate_with_tracking(None, None)
    print(f"Evaluation result: {result}")
    
    # Test des statistiques
    stats = constraint.get_statistics()
    print(f"Statistics: {stats}")
    
    # Test de validation
    errors = validate_constraint_definition(constraint)
    print(f"Validation errors: {errors}")
    
    print("✅ Base constraints module working correctly")
