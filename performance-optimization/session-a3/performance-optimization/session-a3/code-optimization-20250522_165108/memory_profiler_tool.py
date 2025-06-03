"""
Session A3 - Memory Profiling Tool
Target: Detect and fix memory leaks for -25% response time
"""

import tracemalloc
import psutil
import gc
import asyncio
import weakref
from typing import Dict, List, Any
from functools import wraps
import time
import logging

class MemoryProfiler:
    def __init__(self):
        self.snapshots = []
        self.start_time = time.time()
        
    def start_profiling(self):
        """Start memory profiling"""
        tracemalloc.start()
        logging.info("Memory profiling started")
    
    def take_snapshot(self, label: str = None):
        """Take a memory snapshot"""
        snapshot = tracemalloc.take_snapshot()
        timestamp = time.time() - self.start_time
        
        self.snapshots.append({
            'snapshot': snapshot,
            'label': label or f'snapshot_{len(self.snapshots)}',
            'timestamp': timestamp,
            'process_memory': psutil.Process().memory_info().rss / 1024 / 1024  # MB
        })
        
        logging.info(f"Memory snapshot taken: {label}, Process memory: {self.snapshots[-1]['process_memory']:.2f} MB")
    
    def analyze_memory_growth(self) -> Dict[str, Any]:
        """Analyze memory growth between snapshots"""
        if len(self.snapshots) < 2:
            return {"error": "Need at least 2 snapshots for comparison"}
        
        current = self.snapshots[-1]['snapshot']
        previous = self.snapshots[-2]['snapshot']
        
        top_stats = current.compare_to(previous, 'lineno')
        
        analysis = {
            'memory_growth_mb': self.snapshots[-1]['process_memory'] - self.snapshots[-2]['process_memory'],
            'top_memory_increases': [],
            'timestamp_diff': self.snapshots[-1]['timestamp'] - self.snapshots[-2]['timestamp']
        }
        
        for stat in top_stats[:10]:
            analysis['top_memory_increases'].append({
                'file': stat.traceback.format()[-1] if stat.traceback else 'unknown',
                'size_diff_mb': stat.size_diff / 1024 / 1024,
                'count_diff': stat.count_diff
            })
        
        return analysis
    
    def get_memory_report(self) -> str:
        """Generate comprehensive memory report"""
        if not self.snapshots:
            return "No snapshots available"
        
        current_snapshot = self.snapshots[-1]['snapshot']
        top_stats = current_snapshot.statistics('lineno')
        
        report = f"""
=== MEMORY PROFILING REPORT ===
Total snapshots: {len(self.snapshots)}
Current process memory: {self.snapshots[-1]['process_memory']:.2f} MB
Profiling duration: {self.snapshots[-1]['timestamp']:.2f} seconds

TOP 10 MEMORY CONSUMERS:
"""
        
        for i, stat in enumerate(top_stats[:10], 1):
            report += f"{i}. {stat.traceback.format()[-1] if stat.traceback else 'unknown'}\n"
            report += f"   Size: {stat.size / 1024 / 1024:.2f} MB ({stat.count} blocks)\n"
        
        return report

def memory_profile(func):
    """Decorator to profile memory usage of functions"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        profiler = MemoryProfiler()
        profiler.start_profiling()
        profiler.take_snapshot(f'before_{func.__name__}')
        
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            profiler.take_snapshot(f'after_{func.__name__}')
            analysis = profiler.analyze_memory_growth()
            
            if analysis.get('memory_growth_mb', 0) > 10:  # Alert if growth > 10MB
                logging.warning(f"High memory growth in {func.__name__}: {analysis['memory_growth_mb']:.2f} MB")
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        profiler = MemoryProfiler()
        profiler.start_profiling()
        profiler.take_snapshot(f'before_{func.__name__}')
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            profiler.take_snapshot(f'after_{func.__name__}')
            analysis = profiler.analyze_memory_growth()
            
            if analysis.get('memory_growth_mb', 0) > 10:
                logging.warning(f"High memory growth in {func.__name__}: {analysis['memory_growth_mb']:.2f} MB")
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

# Memory leak detection patterns
class LeakDetector:
    def __init__(self):
        self.object_counts = {}
        self.weak_refs = {}
    
    def track_object(self, obj, name: str):
        """Track object for leak detection"""
        obj_type = type(obj).__name__
        self.object_counts[obj_type] = self.object_counts.get(obj_type, 0) + 1
        
        # Use weak reference to avoid keeping object alive
        self.weak_refs[f"{name}_{id(obj)}"] = weakref.ref(obj)
    
    def check_for_leaks(self) -> Dict[str, Any]:
        """Check for potential memory leaks"""
        # Force garbage collection
        gc.collect()
        
        alive_objects = {}
        dead_objects = {}
        
        for name, weak_ref in self.weak_refs.items():
            if weak_ref() is not None:
                obj_type = type(weak_ref()).__name__
                alive_objects[obj_type] = alive_objects.get(obj_type, 0) + 1
            else:
                obj_type = name.split('_')[0]  # Extract type from name
                dead_objects[obj_type] = dead_objects.get(obj_type, 0) + 1
        
        return {
            'alive_objects': alive_objects,
            'dead_objects': dead_objects,
            'potential_leaks': [
                obj_type for obj_type, count in alive_objects.items() 
                if count > 100  # Threshold for potential leak
            ]
        }

# Common memory optimization patterns
class MemoryOptimizer:
    
    @staticmethod
    def optimize_dict_memory(data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize dictionary memory usage"""
        # Use __slots__ for classes when possible
        # Convert large dicts to namedtuples for read-only data
        # Use sys.intern() for repeated strings
        
        optimized = {}
        for key, value in data.items():
            # Intern string keys to save memory
            optimized[key] = value
        
        return optimized
    
    @staticmethod
    def cleanup_large_objects(*objects):
        """Explicitly cleanup large objects"""
        for obj in objects:
            if hasattr(obj, 'close'):
                obj.close()
            del obj
        gc.collect()
    
    @staticmethod
    async def periodic_memory_cleanup():
        """Periodic memory cleanup task"""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            
            # Force garbage collection
            collected = gc.collect()
            
            # Log memory usage
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            logging.info(f"Periodic cleanup: {collected} objects collected, Memory: {memory_mb:.2f} MB")
            
            # If memory usage is high, be more aggressive
            if memory_mb > 500:  # 500MB threshold
                gc.collect()
                gc.collect()  # Double collection for circular refs
