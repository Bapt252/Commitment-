#!/usr/bin/env python3
"""
Session 6: Core Hungarian Algorithm Implementation
===============================================

Implémentation optimisée de l'algorithme hongrois pour le matching optimal.
Utilise scipy pour les performances et inclut une version custom pour l'éducation.

🔥 Fonctionnalités:
- Algorithme hongrois avec scipy (O(n³) optimisé)
- Support matrices non-carrées
- Gestion mémoire optimisée
- Version custom éducative
- Métriques de performance
"""

import numpy as np
import logging
from typing import Tuple, List, Dict, Optional, Union
from dataclasses import dataclass
from scipy.optimize import linear_sum_assignment
import time
from abc import ABC, abstractmethod

# Configuration du logging
logger = logging.getLogger(__name__)

@dataclass
class AssignmentResult:
    """Résultat d'un assignment avec métriques."""
    row_indices: np.ndarray
    col_indices: np.ndarray
    total_cost: float
    execution_time: float
    algorithm_used: str
    matrix_shape: Tuple[int, int]
    optimality_verified: bool = False
    
    def __post_init__(self):
        """Validation des résultats."""
        assert len(self.row_indices) == len(self.col_indices), "Indices mismatch"
        assert self.total_cost >= 0, "Cost cannot be negative"
        assert self.execution_time >= 0, "Time cannot be negative"

class AbstractHungarianSolver(ABC):
    """Interface abstraite pour solveurs hongrois."""
    
    @abstractmethod
    def solve(self, cost_matrix: np.ndarray) -> AssignmentResult:
        """Résout le problème d'assignment."""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retourne le nom du solveur."""
        pass

class ScipyHungarianSolver(AbstractHungarianSolver):
    """Solveur utilisant scipy.optimize.linear_sum_assignment."""
    
    def __init__(self, maximize: bool = False):
        self.maximize = maximize
        logger.info(f"ScipyHungarianSolver initialized (maximize={maximize})")
    
    def solve(self, cost_matrix: np.ndarray) -> AssignmentResult:
        """Résout avec scipy - le plus rapide et stable."""
        start_time = time.time()
        
        # Validation de la matrice
        if cost_matrix.size == 0:
            raise ValueError("Cost matrix cannot be empty")
        
        if not np.isfinite(cost_matrix).all():
            raise ValueError("Cost matrix contains infinite or NaN values")
        
        # Conversion pour maximisation si nécessaire
        matrix_to_solve = -cost_matrix if self.maximize else cost_matrix
        
        try:
            # Résolution avec scipy
            row_indices, col_indices = linear_sum_assignment(matrix_to_solve)
            
            # Calcul du coût total
            total_cost = cost_matrix[row_indices, col_indices].sum()
            
            execution_time = time.time() - start_time
            
            return AssignmentResult(
                row_indices=row_indices,
                col_indices=col_indices,
                total_cost=total_cost,
                execution_time=execution_time,
                algorithm_used="scipy",
                matrix_shape=cost_matrix.shape,
                optimality_verified=True  # scipy garantit l'optimalité
            )
            
        except Exception as e:
            logger.error(f"Scipy solver failed: {e}")
            raise RuntimeError(f"Failed to solve assignment problem: {e}")
    
    def get_name(self) -> str:
        return "scipy_hungarian"

class CustomHungarianSolver(AbstractHungarianSolver):
    """Implémentation custom de l'algorithme hongrois (éducative)."""
    
    def __init__(self, maximize: bool = False):
        self.maximize = maximize
        self.debug = False
        logger.info(f"CustomHungarianSolver initialized (maximize={maximize})")
    
    def solve(self, cost_matrix: np.ndarray) -> AssignmentResult:
        """Implémentation custom de l'algorithme hongrois."""
        start_time = time.time()
        
        # Conversion pour maximisation
        if self.maximize:
            matrix = -cost_matrix.copy()
        else:
            matrix = cost_matrix.copy()
        
        # Assurer que la matrice est carrée
        matrix = self._make_square(matrix)
        n = matrix.shape[0]
        
        # Étapes de l'algorithme hongrois
        matrix = self._subtract_row_minimums(matrix)
        matrix = self._subtract_col_minimums(matrix)
        
        # Recherche de l'assignment optimal
        assignment = self._find_optimal_assignment(matrix)
        
        # Extraction des indices originaux
        row_indices = []
        col_indices = []
        
        for i, j in assignment:
            if i < cost_matrix.shape[0] and j < cost_matrix.shape[1]:
                row_indices.append(i)
                col_indices.append(j)
        
        row_indices = np.array(row_indices)
        col_indices = np.array(col_indices)
        
        # Calcul du coût total
        total_cost = cost_matrix[row_indices, col_indices].sum()
        
        execution_time = time.time() - start_time
        
        return AssignmentResult(
            row_indices=row_indices,
            col_indices=col_indices,
            total_cost=total_cost,
            execution_time=execution_time,
            algorithm_used="custom",
            matrix_shape=cost_matrix.shape,
            optimality_verified=False  # À vérifier manuellement
        )
    
    def _make_square(self, matrix: np.ndarray) -> np.ndarray:
        """Rend la matrice carrée en ajoutant des zéros."""
        rows, cols = matrix.shape
        size = max(rows, cols)
        
        if rows == cols:
            return matrix
        
        square_matrix = np.full((size, size), np.inf)
        square_matrix[:rows, :cols] = matrix
        
        return square_matrix
    
    def _subtract_row_minimums(self, matrix: np.ndarray) -> np.ndarray:
        """Soustrait le minimum de chaque ligne."""
        for i in range(matrix.shape[0]):
            min_val = np.min(matrix[i, :])
            if min_val != np.inf:
                matrix[i, :] -= min_val
        return matrix
    
    def _subtract_col_minimums(self, matrix: np.ndarray) -> np.ndarray:
        """Soustrait le minimum de chaque colonne."""
        for j in range(matrix.shape[1]):
            min_val = np.min(matrix[:, j])
            if min_val != np.inf:
                matrix[:, j] -= min_val
        return matrix
    
    def _find_optimal_assignment(self, matrix: np.ndarray) -> List[Tuple[int, int]]:
        """Trouve l'assignment optimal (version simplifiée)."""
        n = matrix.shape[0]
        assignment = []
        
        # Version greedy simple pour l'exemple
        # Une vraie implémentation nécessiterait l'algorithme complet
        used_rows = set()
        used_cols = set()
        
        # Trouve les zéros et essaie un assignment greedy
        zero_positions = np.where(matrix == 0)
        
        for row, col in zip(zero_positions[0], zero_positions[1]):
            if row not in used_rows and col not in used_cols:
                assignment.append((row, col))
                used_rows.add(row)
                used_cols.add(col)
        
        # Si l'assignment n'est pas complet, utilise scipy en fallback
        if len(assignment) < min(matrix.shape):
            logger.warning("Custom solver incomplete, falling back to scipy")
            row_indices, col_indices = linear_sum_assignment(matrix)
            assignment = list(zip(row_indices, col_indices))
        
        return assignment
    
    def get_name(self) -> str:
        return "custom_hungarian"

class HungarianAlgorithm:
    """Classe principale pour l'algorithme hongrois."""
    
    def __init__(self, 
                 algorithm: str = "scipy",
                 maximize: bool = False,
                 memory_efficient: bool = True):
        """
        Initialise l'algorithme hongrois.
        
        Args:
            algorithm: "scipy" ou "custom"
            maximize: True pour maximiser, False pour minimiser
            memory_efficient: Optimisations mémoire pour grandes matrices
        """
        self.algorithm = algorithm
        self.maximize = maximize
        self.memory_efficient = memory_efficient
        
        # Sélection du solveur
        if algorithm == "scipy":
            self.solver = ScipyHungarianSolver(maximize=maximize)
        elif algorithm == "custom":
            self.solver = CustomHungarianSolver(maximize=maximize)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        logger.info(f"HungarianAlgorithm initialized with {algorithm} solver")
    
    def solve(self, 
              cost_matrix: Union[np.ndarray, List[List[float]]],
              validate_result: bool = True) -> AssignmentResult:
        """
        Résout le problème d'assignment.
        
        Args:
            cost_matrix: Matrice de coûts (rows x cols)
            validate_result: Valide la solution
            
        Returns:
            AssignmentResult avec la solution optimale
        """
        # Conversion en numpy array
        if isinstance(cost_matrix, list):
            cost_matrix = np.array(cost_matrix)
        
        # Vérifications préliminaires
        self._validate_cost_matrix(cost_matrix)
        
        # Optimisation mémoire pour grandes matrices
        if self.memory_efficient and cost_matrix.size > 1_000_000:
            cost_matrix = self._optimize_memory(cost_matrix)
        
        # Résolution
        result = self.solver.solve(cost_matrix)
        
        # Validation optionnelle
        if validate_result:
            self._validate_solution(cost_matrix, result)
        
        logger.info(f"Solved {cost_matrix.shape} matrix in {result.execution_time:.4f}s")
        logger.info(f"Total cost: {result.total_cost:.4f}")
        
        return result
    
    def _validate_cost_matrix(self, cost_matrix: np.ndarray) -> None:
        """Valide la matrice de coûts."""
        if cost_matrix.size == 0:
            raise ValueError("Cost matrix cannot be empty")
        
        if len(cost_matrix.shape) != 2:
            raise ValueError("Cost matrix must be 2-dimensional")
        
        if not np.isfinite(cost_matrix).all():
            raise ValueError("Cost matrix contains infinite or NaN values")
        
        # Vérification de la taille
        max_size = 10_000  # Configurable
        if cost_matrix.shape[0] > max_size or cost_matrix.shape[1] > max_size:
            raise ValueError(f"Matrix too large: {cost_matrix.shape} > {max_size}")
    
    def _optimize_memory(self, cost_matrix: np.ndarray) -> np.ndarray:
        """Optimisations mémoire pour grandes matrices."""
        # Conversion en float32 si possible
        if cost_matrix.dtype == np.float64:
            if np.allclose(cost_matrix, cost_matrix.astype(np.float32)):
                cost_matrix = cost_matrix.astype(np.float32)
                logger.info("Converted to float32 for memory efficiency")
        
        return cost_matrix
    
    def _validate_solution(self, cost_matrix: np.ndarray, result: AssignmentResult) -> None:
        """Valide que la solution est correcte."""
        # Vérification des indices
        if len(result.row_indices) != len(result.col_indices):
            raise ValueError("Solution indices mismatch")
        
        # Vérification des bounds
        if (result.row_indices >= cost_matrix.shape[0]).any():
            raise ValueError("Row indices out of bounds")
        
        if (result.col_indices >= cost_matrix.shape[1]).any():
            raise ValueError("Column indices out of bounds")
        
        # Vérification du coût
        calculated_cost = cost_matrix[result.row_indices, result.col_indices].sum()
        if not np.isclose(calculated_cost, result.total_cost):
            raise ValueError(f"Cost mismatch: {calculated_cost} != {result.total_cost}")

# Interface principale simplifiée
def solve_assignment_problem(cost_matrix: Union[np.ndarray, List[List[float]]],
                           algorithm: str = "scipy",
                           maximize: bool = False) -> AssignmentResult:
    """
    Interface simplifiée pour résoudre un problème d'assignment.
    
    Args:
        cost_matrix: Matrice de coûts
        algorithm: "scipy" ou "custom"
        maximize: True pour maximiser, False pour minimiser
        
    Returns:
        AssignmentResult avec la solution optimale
        
    Example:
        >>> import numpy as np
        >>> cost_matrix = np.array([[4, 1, 3], [2, 0, 5], [3, 2, 2]])
        >>> result = solve_assignment_problem(cost_matrix)
        >>> print(f"Cost: {result.total_cost}")
        >>> print(f"Assignment: {list(zip(result.row_indices, result.col_indices))}")
    """
    solver = HungarianAlgorithm(algorithm=algorithm, maximize=maximize)
    return solver.solve(cost_matrix)

# Fonction utilitaire pour benchmark
def benchmark_algorithms(cost_matrix: np.ndarray, 
                        algorithms: List[str] = ["scipy", "custom"]) -> Dict[str, AssignmentResult]:
    """
    Compare les performances de différents algorithmes.
    
    Args:
        cost_matrix: Matrice de coûts
        algorithms: Liste des algorithmes à tester
        
    Returns:
        Dictionnaire des résultats par algorithme
    """
    results = {}
    
    for algo in algorithms:
        try:
            solver = HungarianAlgorithm(algorithm=algo)
            result = solver.solve(cost_matrix)
            results[algo] = result
            
            logger.info(f"{algo}: {result.total_cost:.4f} in {result.execution_time:.4f}s")
        except Exception as e:
            logger.error(f"Failed to run {algo}: {e}")
            results[algo] = None
    
    return results

if __name__ == "__main__":
    # Test rapide
    np.random.seed(42)
    test_matrix = np.random.randint(1, 10, (5, 5))
    
    print("🧪 Testing Hungarian Algorithm")
    print(f"Matrix shape: {test_matrix.shape}")
    print(f"Matrix:\n{test_matrix}")
    
    result = solve_assignment_problem(test_matrix)
    print(f"\n✅ Solution found:")
    print(f"   Cost: {result.total_cost}")
    print(f"   Time: {result.execution_time:.4f}s")
    print(f"   Assignment: {list(zip(result.row_indices, result.col_indices))}")
    
    # Benchmark
    print("\n🏁 Benchmarking algorithms...")
    benchmark_results = benchmark_algorithms(test_matrix)
    for algo, result in benchmark_results.items():
        if result:
            print(f"   {algo}: {result.total_cost} ({result.execution_time:.4f}s)")
