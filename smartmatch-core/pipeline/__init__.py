"""
Pipeline Module for SmartMatch-Core
====================================

This module provides the automated machine learning pipeline infrastructure:
- Auto-training system for continuous model improvement
- A/B testing framework for model comparison
- Drift detection and monitoring system

Key Components:
- AutoTrainer: Orchestrates automated training cycles
- ABTester: Manages A/B testing infrastructure  
- DriftMonitor: Detects and responds to model/data drift

Integration Points:
- Enhanced Skills Matcher (Session 4)
- Optimization modules (Optuna, metrics)
- Dataset generation and validation

Author: AI Assistant & Bapt252
Session: 5 - ML Optimization Intelligence
"""

from .auto_trainer import AutoTrainer, TrainingConfig, ModelVersion
from .ab_tester import ABTester, ABTest, TestGroup, StatisticalAnalysis
from .drift_monitor import DriftMonitor, DriftAlert, DriftDetector

# Pipeline orchestration utilities
import logging
from typing import Dict, List, Optional, Tuple
import asyncio
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """
    Central orchestrator for all pipeline components.
    Coordinates training, testing, and monitoring workflows.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.auto_trainer = AutoTrainer(config.get('training', {}))
        self.ab_tester = ABTester(config.get('ab_testing', {}))
        self.drift_monitor = DriftMonitor(config.get('drift_monitoring', {}))
        
        # Pipeline state
        self.is_running = False
        self.current_jobs = {}
        
    async def start_pipeline(self):
        """Start the full ML pipeline orchestration."""
        if self.is_running:
            logger.warning("Pipeline already running")
            return
            
        self.is_running = True
        logger.info("Starting ML Pipeline orchestration")
        
        # Start all components
        tasks = [
            self.auto_trainer.start_training_loop(),
            self.ab_tester.start_testing_loop(),
            self.drift_monitor.start_monitoring_loop()
        ]
        
        await asyncio.gather(*tasks)
    
    async def stop_pipeline(self):
        """Gracefully stop the pipeline."""
        logger.info("Stopping ML Pipeline orchestration")
        self.is_running = False
        
        # Stop all components
        await self.auto_trainer.stop()
        await self.ab_tester.stop()
        await self.drift_monitor.stop()
    
    def get_pipeline_status(self) -> Dict:
        """Get comprehensive pipeline status."""
        return {
            'is_running': self.is_running,
            'timestamp': datetime.now().isoformat(),
            'components': {
                'auto_trainer': self.auto_trainer.get_status(),
                'ab_tester': self.ab_tester.get_status(),
                'drift_monitor': self.drift_monitor.get_status()
            },
            'current_jobs': self.current_jobs
        }

# Utility functions for pipeline management
def create_pipeline_config(
    training_interval: int = 3600,  # 1 hour
    ab_test_duration: int = 86400,  # 24 hours
    drift_check_interval: int = 300,  # 5 minutes
    **kwargs
) -> Dict:
    """Create a standard pipeline configuration."""
    return {
        'training': {
            'interval_seconds': training_interval,
            'max_concurrent_jobs': 2,
            'validation_splits': 5,
            'early_stopping_patience': 10,
            **kwargs.get('training', {})
        },
        'ab_testing': {
            'test_duration_seconds': ab_test_duration,
            'min_sample_size': 1000,
            'significance_level': 0.05,
            'power': 0.8,
            **kwargs.get('ab_testing', {})
        },
        'drift_monitoring': {
            'check_interval_seconds': drift_check_interval,
            'drift_threshold': 0.1,
            'performance_threshold': 0.05,
            'window_size': 1000,
            **kwargs.get('drift_monitoring', {})
        }
    }

def load_pipeline_state(filepath: str) -> Optional[Dict]:
    """Load pipeline state from file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load pipeline state: {e}")
        return None

def save_pipeline_state(state: Dict, filepath: str) -> bool:
    """Save pipeline state to file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Failed to save pipeline state: {e}")
        return False

# Export main classes and utilities
__all__ = [
    'AutoTrainer', 'TrainingConfig', 'ModelVersion',
    'ABTester', 'ABTest', 'TestGroup', 'StatisticalAnalysis',
    'DriftMonitor', 'DriftAlert', 'DriftDetector',
    'PipelineOrchestrator',
    'create_pipeline_config',
    'load_pipeline_state',
    'save_pipeline_state'
]

# Version info
__version__ = "1.0.0"
__author__ = "AI Assistant & Bapt252"
__session__ = "5 - ML Optimization Intelligence"
