"""Performance analyzer module for Hungarian algorithm implementation.

This module provides tools for measuring, analyzing, and comparing the
performance of different matching algorithms and configurations.
"""

import numpy as np
import time
import logging
import csv
import json
from typing import Dict, List, Tuple, Set, Any, Optional, Union, Callable
from enum import Enum
from dataclasses import dataclass
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import psutil
import gc

from ..hungarian.algorithm import HungarianAlgorithm
from .optimal_matcher import OptimalMatcher

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """Types of performance metrics to measure."""
    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    SOLUTION_QUALITY = "solution_quality"
    CONSTRAINT_VIOLATIONS = "constraint_violations"
    CACHE_HITS = "cache_hits"
    ITERATIONS = "iterations"


@dataclass
class PerformanceResult:
    """Container for performance test results."""
    matcher_name: str
    matrix_size: Tuple[int, int]
    execution_time: float
    memory_usage: float
    solution_quality: float
    constraint_violations: int
    cache_hits: int
    iterations: int
    timestamp: datetime = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'matcher_name': self.matcher_name,
            'matrix_size': self.matrix_size,
            'execution_time': self.execution_time,
            'memory_usage': self.memory_usage,
            'solution_quality': self.solution_quality,
            'constraint_violations': self.constraint_violations,
            'cache_hits': self.cache_hits,
            'iterations': self.iterations,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PerformanceResult':
        """Create from dictionary."""
        return cls(
            matcher_name=data['matcher_name'],
            matrix_size=tuple(data['matrix_size']),
            execution_time=data['execution_time'],
            memory_usage=data['memory_usage'],
            solution_quality=data['solution_quality'],
            constraint_violations=data['constraint_violations'],
            cache_hits=data['cache_hits'],
            iterations=data['iterations'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


class PerformanceAnalyzer:
    """
    Analyzer for measuring and comparing algorithm performance.
    
    This class provides tools for benchmarking different matcher implementations,
    analyzing their performance characteristics, and generating reports.
    """
    
    def __init__(self, results_dir: Optional[str] = None):
        """
        Initialize the performance analyzer.
        
        Args:
            results_dir: Directory for storing performance results
        """
        self.results: List[PerformanceResult] = []
        self.results_dir = Path(results_dir) if results_dir else Path("./performance_results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def measure_performance(self, 
                           matcher: OptimalMatcher,
                           cost_matrix: np.ndarray,
                           matcher_name: str = "default",
                           iterations: int = 1,
                           warmup: int = 1,
                           row_preferences: Optional[List[List[int]]] = None,
                           col_preferences: Optional[List[List[int]]] = None,
                           context: Optional[Dict[str, Any]] = None) -> PerformanceResult:
        """
        Measure the performance of a matcher on a given problem.
        
        Args:
            matcher: The matcher to test
            cost_matrix: The cost matrix for matching
            matcher_name: Name identifier for the matcher
            iterations: Number of iterations to run
            warmup: Number of warmup iterations to perform
            row_preferences: Optional row preferences for bidirectional matching
            col_preferences: Optional column preferences for bidirectional matching
            context: Additional context for matching
            
        Returns:
            Performance results
        """
        # Perform warmup runs
        for _ in range(warmup):
            matcher.match(cost_matrix, row_preferences, col_preferences, context)
            # Clear cache between runs if available
            if hasattr(matcher, 'clear_cache'):
                matcher.clear_cache()
        
        # Measure memory before
        process = psutil.Process()
        gc.collect()  # Force garbage collection
        memory_before = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Start timing
        start_time = time.time()
        
        # Run iterations
        solution_quality = 0
        constraint_violations = 0
        cache_hits = 0
        iterations_count = 0
        
        for i in range(iterations):
            # Run the matcher
            assignments, total_cost = matcher.match(
                cost_matrix, row_preferences, col_preferences, context
            )
            
            # Record quality metrics
            solution_quality += total_cost
            
            # Record iterations if available
            if hasattr(matcher.hungarian, 'iterations'):
                iterations_count += matcher.hungarian.iterations
            
            # Record constraint violations if available
            if hasattr(matcher, 'constraint_validator'):
                validator = matcher.constraint_validator
                for group_name in validator.groups:
                    history = validator.get_validation_history(group_name, only_violations=True)
                    constraint_violations += sum(r['violation_count'] for r in history)
            
            # Record cache hits if available
            if hasattr(matcher.compute_assignment, 'cache_info'):
                cache_info = matcher.compute_assignment.cache_info()
                cache_hits += cache_info.hits
            
            # Clear cache between runs if available
            if hasattr(matcher, 'clear_cache') and i < iterations - 1:
                matcher.clear_cache()
        
        # End timing
        end_time = time.time()
        execution_time = (end_time - start_time) / iterations
        
        # Measure memory after
        gc.collect()  # Force garbage collection
        memory_after = process.memory_info().rss / (1024 * 1024)  # MB
        memory_usage = memory_after - memory_before
        
        # Average metrics
        solution_quality /= iterations
        constraint_violations /= iterations
        cache_hits /= iterations
        iterations_count /= iterations
        
        # Create result
        result = PerformanceResult(
            matcher_name=matcher_name,
            matrix_size=cost_matrix.shape,
            execution_time=execution_time,
            memory_usage=memory_usage,
            solution_quality=solution_quality,
            constraint_violations=constraint_violations,
            cache_hits=cache_hits,
            iterations=iterations_count
        )
        
        # Add to results
        self.results.append(result)
        
        return result
    
    def compare_matchers(self, 
                        matchers: Dict[str, OptimalMatcher],
                        cost_matrices: List[np.ndarray],
                        iterations: int = 1,
                        warmup: int = 1) -> List[PerformanceResult]:
        """
        Compare multiple matchers on multiple problem instances.
        
        Args:
            matchers: Dictionary mapping matcher names to matcher instances
            cost_matrices: List of cost matrices to test
            iterations: Number of iterations for each test
            warmup: Number of warmup iterations
            
        Returns:
            List of performance results
        """
        results = []
        
        for name, matcher in matchers.items():
            logger.info(f"Testing matcher: {name}")
            
            for i, matrix in enumerate(cost_matrices):
                logger.info(f"  Matrix {i+1}/{len(cost_matrices)}: {matrix.shape}")
                
                result = self.measure_performance(
                    matcher=matcher,
                    cost_matrix=matrix,
                    matcher_name=name,
                    iterations=iterations,
                    warmup=warmup
                )
                
                results.append(result)
        
        return results
    
    def run_scalability_test(self, 
                            matcher: OptimalMatcher,
                            min_size: int = 10,
                            max_size: int = 1000,
                            step: int = 100,
                            iterations: int = 1,
                            warmup: int = 1,
                            matcher_name: str = "default") -> List[PerformanceResult]:
        """
        Test matcher performance across different problem sizes.
        
        Args:
            matcher: The matcher to test
            min_size: Minimum matrix size
            max_size: Maximum matrix size
            step: Size increment between tests
            iterations: Number of iterations for each test
            warmup: Number of warmup iterations
            matcher_name: Name identifier for the matcher
            
        Returns:
            List of performance results
        """
        results = []
        sizes = range(min_size, max_size + 1, step)
        
        for size in sizes:
            logger.info(f"Testing size: {size}x{size}")
            
            # Generate random cost matrix
            matrix = np.random.rand(size, size)
            
            result = self.measure_performance(
                matcher=matcher,
                cost_matrix=matrix,
                matcher_name=matcher_name,
                iterations=iterations,
                warmup=warmup
            )
            
            results.append(result)
        
        return results
    
    def save_results(self, filename: Optional[str] = None) -> str:
        """
        Save performance results to file.
        
        Args:
            filename: Name for the results file (without extension)
            
        Returns:
            Path to the saved results file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_results_{timestamp}"
        
        # Save as JSON
        json_path = self.results_dir / f"{filename}.json"
        with open(json_path, 'w') as f:
            json.dump([r.to_dict() for r in self.results], f, indent=2)
        
        # Save as CSV
        csv_path = self.results_dir / f"{filename}.csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Matcher', 'Rows', 'Columns', 'Execution Time (s)',
                'Memory Usage (MB)', 'Solution Quality', 'Constraint Violations',
                'Cache Hits', 'Iterations', 'Timestamp'
            ])
            
            # Write data
            for result in self.results:
                writer.writerow([
                    result.matcher_name,
                    result.matrix_size[0],
                    result.matrix_size[1],
                    result.execution_time,
                    result.memory_usage,
                    result.solution_quality,
                    result.constraint_violations,
                    result.cache_hits,
                    result.iterations,
                    result.timestamp.isoformat()
                ])
        
        logger.info(f"Results saved to {json_path} and {csv_path}")
        
        return str(json_path)
    
    def load_results(self, filepath: str) -> None:
        """
        Load performance results from file.
        
        Args:
            filepath: Path to the results file
        """
        path = Path(filepath)
        
        if not path.exists():
            raise FileNotFoundError(f"Results file not found: {filepath}")
        
        if path.suffix == '.json':
            with open(path, 'r') as f:
                data = json.load(f)
                self.results = [PerformanceResult.from_dict(r) for r in data]
        elif path.suffix == '.csv':
            self.results = []
            with open(path, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    result = PerformanceResult(
                        matcher_name=row['Matcher'],
                        matrix_size=(int(row['Rows']), int(row['Columns'])),
                        execution_time=float(row['Execution Time (s)']),
                        memory_usage=float(row['Memory Usage (MB)']),
                        solution_quality=float(row['Solution Quality']),
                        constraint_violations=int(row['Constraint Violations']),
                        cache_hits=int(row['Cache Hits']),
                        iterations=int(row['Iterations']),
                        timestamp=datetime.fromisoformat(row['Timestamp'])
                    )
                    self.results.append(result)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        logger.info(f"Loaded {len(self.results)} results from {filepath}")
    
    def plot_performance(self, 
                        metric: PerformanceMetric = PerformanceMetric.EXECUTION_TIME,
                        by_size: bool = True,
                        save_path: Optional[str] = None) -> None:
        """
        Plot performance results.
        
        Args:
            metric: The metric to plot
            by_size: Whether to group by matrix size
            save_path: Path to save the plot image
        """
        if not self.results:
            logger.warning("No results to plot")
            return
        
        # Set up the figure
        plt.figure(figsize=(10, 6))
        
        # Group results
        if by_size:
            # Group by matcher and matrix size
            data = {}
            for result in self.results:
                matcher = result.matcher_name
                size = max(result.matrix_size)
                
                if matcher not in data:
                    data[matcher] = {'sizes': [], 'values': []}
                    
                data[matcher]['sizes'].append(size)
                
                # Get the metric value
                if metric == PerformanceMetric.EXECUTION_TIME:
                    value = result.execution_time
                elif metric == PerformanceMetric.MEMORY_USAGE:
                    value = result.memory_usage
                elif metric == PerformanceMetric.SOLUTION_QUALITY:
                    value = result.solution_quality
                elif metric == PerformanceMetric.CONSTRAINT_VIOLATIONS:
                    value = result.constraint_violations
                elif metric == PerformanceMetric.CACHE_HITS:
                    value = result.cache_hits
                elif metric == PerformanceMetric.ITERATIONS:
                    value = result.iterations
                else:
                    value = 0
                    
                data[matcher]['values'].append(value)
            
            # Plot each matcher
            for matcher, values in data.items():
                # Sort by size
                sizes = np.array(values['sizes'])
                metrics = np.array(values['values'])
                indices = np.argsort(sizes)
                
                plt.plot(sizes[indices], metrics[indices], 'o-', label=matcher)
                
            plt.xlabel('Matrix Size')
            
        else:
            # Group by matcher only
            data = {}
            for result in self.results:
                matcher = result.matcher_name
                
                if matcher not in data:
                    data[matcher] = []
                
                # Get the metric value
                if metric == PerformanceMetric.EXECUTION_TIME:
                    value = result.execution_time
                elif metric == PerformanceMetric.MEMORY_USAGE:
                    value = result.memory_usage
                elif metric == PerformanceMetric.SOLUTION_QUALITY:
                    value = result.solution_quality
                elif metric == PerformanceMetric.CONSTRAINT_VIOLATIONS:
                    value = result.constraint_violations
                elif metric == PerformanceMetric.CACHE_HITS:
                    value = result.cache_hits
                elif metric == PerformanceMetric.ITERATIONS:
                    value = result.iterations
                else:
                    value = 0
                    
                data[matcher].append(value)
            
            # Plot each matcher as a box plot
            plt.boxplot([values for values in data.values()], labels=list(data.keys()))
            plt.xticks(rotation=45)
            
        # Set labels and title
        plt.ylabel(metric.value.replace('_', ' ').title())
        plt.title(f'{metric.value.replace("_", " ").title()} Performance')
        
        if by_size:
            plt.legend()
            
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # Save if requested
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Plot saved to {save_path}")
        
        plt.close()
    
    def generate_performance_report(self, 
                                   output_file: Optional[str] = None,
                                   include_plots: bool = True,
                                   plot_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report.
        
        Args:
            output_file: Path to save the report JSON
            include_plots: Whether to generate and include plots
            plot_dir: Directory to save plot images
            
        Returns:
            Dictionary containing the report
        """
        if not self.results:
            logger.warning("No results to generate report")
            return {}
        
        # Create timestamp
        timestamp = datetime.now().isoformat()
        
        # Initialize report
        report = {
            'timestamp': timestamp,
            'result_count': len(self.results),
            'matchers': set(r.matcher_name for r in self.results),
            'summary': {},
            'details': {}
        }
        
        # Generate plots if requested
        plot_paths = {}
        if include_plots and plot_dir:
            plot_dir = Path(plot_dir)
            plot_dir.mkdir(parents=True, exist_ok=True)
            
            # Plot each metric
            for metric in PerformanceMetric:
                plot_path = plot_dir / f"{metric.value}_by_size.png"
                self.plot_performance(metric, by_size=True, save_path=str(plot_path))
                plot_paths[f"{metric.value}_by_size"] = str(plot_path)
                
                plot_path = plot_dir / f"{metric.value}_by_matcher.png"
                self.plot_performance(metric, by_size=False, save_path=str(plot_path))
                plot_paths[f"{metric.value}_by_matcher"] = str(plot_path)
        
        # Add plot paths to report
        if plot_paths:
            report['plots'] = plot_paths
        
        # Group results by matcher
        matcher_results = {}
        for result in self.results:
            matcher = result.matcher_name
            if matcher not in matcher_results:
                matcher_results[matcher] = []
            matcher_results[matcher].append(result)
        
        # Calculate summary statistics
        for matcher, results in matcher_results.items():
            # Extract metrics
            execution_times = [r.execution_time for r in results]
            memory_usages = [r.memory_usage for r in results]
            solution_qualities = [r.solution_quality for r in results]
            constraint_violations = [r.constraint_violations for r in results]
            
            # Calculate statistics
            report['summary'][matcher] = {
                'count': len(results),
                'execution_time': {
                    'min': min(execution_times),
                    'max': max(execution_times),
                    'avg': sum(execution_times) / len(execution_times),
                    'median': sorted(execution_times)[len(execution_times) // 2]
                },
                'memory_usage': {
                    'min': min(memory_usages),
                    'max': max(memory_usages),
                    'avg': sum(memory_usages) / len(memory_usages),
                    'median': sorted(memory_usages)[len(memory_usages) // 2]
                },
                'solution_quality': {
                    'min': min(solution_qualities),
                    'max': max(solution_qualities),
                    'avg': sum(solution_qualities) / len(solution_qualities),
                    'median': sorted(solution_qualities)[len(solution_qualities) // 2]
                },
                'constraint_violations': {
                    'min': min(constraint_violations),
                    'max': max(constraint_violations),
                    'avg': sum(constraint_violations) / len(constraint_violations),
                    'median': sorted(constraint_violations)[len(constraint_violations) // 2]
                }
            }
        
        # Add detailed results
        report['details'] = [r.to_dict() for r in self.results]
        
        # Save if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {output_file}")
        
        return report
    
    def clear_results(self) -> None:
        """Clear all performance results."""
        self.results = []
        logger.info("Performance results cleared")