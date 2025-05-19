"""
AutoTrainer - Automated Model Training System
==============================================

Intelligent automated training system that continuously improves models
through hyperparameter optimization, validation, and versioning.

Features:
- Orchestrated training cycles with Optuna optimization
- Cross-validation and early stopping
- Model versioning and performance tracking
- Adaptive scheduling based on performance
- Integration with existing enhanced_skills_matcher

Author: AI Assistant & Bapt252
Session: 5 - ML Optimization Intelligence
"""

import asyncio
import logging
import pickle
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
import optuna
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Import from other modules
from ..optimizers.optuna_optimizer import OptunaOptimizer
from ..optimizers.objective_functions import SkillsMatchingObjective
from ..metrics.performance_tracker import PerformanceTracker
from ..datasets.synthetic_generator import SyntheticDataGenerator
from ..datasets.validator import DatasetValidator

logger = logging.getLogger(__name__)

class TrainingStatus(Enum):
    """Training job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TrainingConfig:
    """Configuration for training jobs."""
    model_name: str
    objective_name: str = "skills_matching"
    n_trials: int = 100
    timeout: Optional[int] = 3600  # 1 hour
    cv_folds: int = 5
    early_stopping_patience: int = 10
    validation_fraction: float = 0.2
    random_state: int = 42
    optimization_direction: str = "maximize"
    pruning_enabled: bool = True
    
    # Advanced settings
    warm_start: bool = True
    incremental_learning: bool = False
    ensemble_size: int = 1
    confidence_threshold: float = 0.95
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TrainingConfig':
        return cls(**data)

@dataclass
class ModelVersion:
    """Model version information."""
    version_id: str
    model_name: str
    training_timestamp: datetime
    performance_metrics: Dict[str, float]
    hyperparameters: Dict[str, Any]
    model_path: str
    config: TrainingConfig
    validation_score: float
    training_duration: float
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['training_timestamp'] = self.training_timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ModelVersion':
        data['training_timestamp'] = datetime.fromisoformat(data['training_timestamp'])
        data['config'] = TrainingConfig.from_dict(data['config'])
        return cls(**data)

class AutoTrainer:
    """
    Automated training system with intelligent scheduling and optimization.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.training_queue: List[TrainingConfig] = []
        self.running_jobs: Dict[str, Dict] = {}
        self.completed_jobs: List[ModelVersion] = []
        self.model_registry: Dict[str, List[ModelVersion]] = {}
        
        # Components
        self.optuna_optimizer = OptunaOptimizer(config.get('optuna', {}))
        self.performance_tracker = PerformanceTracker()
        self.data_generator = SyntheticDataGenerator()
        self.validator = DatasetValidator()
        
        # State management
        self.is_running = False
        self.models_dir = Path(config.get('models_dir', 'models'))
        self.models_dir.mkdir(exist_ok=True)
        
        # Training scheduling
        self.training_interval = config.get('interval_seconds', 3600)
        self.max_concurrent_jobs = config.get('max_concurrent_jobs', 2)
        
        # Load existing state
        self._load_state()
    
    async def start_training_loop(self):
        """Start the automated training loop."""
        if self.is_running:
            logger.warning("Training loop already running")
            return
        
        self.is_running = True
        logger.info("Starting automated training loop")
        
        try:
            while self.is_running:
                await self._execute_training_cycle()
                await asyncio.sleep(self.training_interval)
        except Exception as e:
            logger.error(f"Training loop error: {e}")
        finally:
            self.is_running = False
    
    async def stop(self):
        """Stop the training loop gracefully."""
        logger.info("Stopping automated training")
        self.is_running = False
        
        # Wait for running jobs to complete
        while self.running_jobs:
            logger.info(f"Waiting for {len(self.running_jobs)} jobs to complete")
            await asyncio.sleep(5)
        
        self._save_state()
    
    async def schedule_training(self, config: TrainingConfig) -> str:
        """Schedule a new training job."""
        job_id = f"{config.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Add to queue
        self.training_queue.append(config)
        
        logger.info(f"Scheduled training job: {job_id}")
        return job_id
    
    async def _execute_training_cycle(self):
        """Execute one training cycle."""
        # Check for scheduled jobs
        if not self.training_queue:
            await self._schedule_adaptive_training()
        
        # Process queue
        while (len(self.running_jobs) < self.max_concurrent_jobs and 
               self.training_queue):
            config = self.training_queue.pop(0)
            await self._start_training_job(config)
        
        # Check completed jobs
        await self._check_completed_jobs()
    
    async def _schedule_adaptive_training(self):
        """Adaptively schedule training based on performance trends."""
        # Get performance trends for each model
        for model_name, versions in self.model_registry.items():
            if not versions:
                continue
            
            # Check if retraining is needed
            should_retrain = await self._should_retrain_model(model_name, versions)
            
            if should_retrain:
                # Create adaptive config based on previous best
                config = await self._create_adaptive_config(model_name, versions)
                await self.schedule_training(config)
    
    async def _should_retrain_model(
        self, 
        model_name: str, 
        versions: List[ModelVersion]
    ) -> bool:
        """Determine if a model should be retrained."""
        if not versions:
            return True
        
        latest = versions[-1]
        
        # Time-based trigger
        time_since_training = datetime.now() - latest.training_timestamp
        if time_since_training > timedelta(hours=24):
            return True
        
        # Performance degradation trigger
        if len(versions) >= 3:
            recent_scores = [v.validation_score for v in versions[-3:]]
            if len(recent_scores) >= 2:
                # Check for declining trend
                trend = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
                if trend < -0.01:  # Declining by more than 1%
                    logger.info(f"Performance decline detected for {model_name}")
                    return True
        
        return False
    
    async def _create_adaptive_config(
        self, 
        model_name: str, 
        versions: List[ModelVersion]
    ) -> TrainingConfig:
        """Create adaptive training config based on historical performance."""
        if not versions:
            return TrainingConfig(model_name=model_name)
        
        # Use best performing version as baseline
        best_version = max(versions, key=lambda v: v.validation_score)
        
        # Adaptive configuration
        config = TrainingConfig(
            model_name=model_name,
            n_trials=min(200, len(versions) * 50),  # More trials for established models
            timeout=3600 + len(versions) * 300,  # More time for complex models
            warm_start=True,
            incremental_learning=len(versions) > 5
        )
        
        return config
    
    async def _start_training_job(self, config: TrainingConfig):
        """Start a training job."""
        job_id = f"{config.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create job record
        job_record = {
            'job_id': job_id,
            'config': config,
            'status': TrainingStatus.RUNNING,
            'start_time': datetime.now(),
            'task': None
        }
        
        # Start async training
        task = asyncio.create_task(self._train_model(job_id, config))
        job_record['task'] = task
        
        self.running_jobs[job_id] = job_record
        logger.info(f"Started training job: {job_id}")
    
    async def _train_model(self, job_id: str, config: TrainingConfig):
        """Train a model with the given configuration."""
        try:
            logger.info(f"Training model {config.model_name} (job: {job_id})")
            start_time = datetime.now()
            
            # Generate or load training data
            X_train, y_train, X_val, y_val = await self._prepare_training_data(config)
            
            # Validate data quality
            validation_report = self.validator.validate_quality(
                {'features': X_train, 'labels': y_train}
            )
            if not validation_report['is_valid']:
                raise ValueError(f"Data validation failed: {validation_report}")
            
            # Setup optimization objective
            objective = SkillsMatchingObjective(
                X_train=X_train,
                y_train=y_train,
                X_val=X_val,
                y_val=y_val,
                cv_folds=config.cv_folds,
                early_stopping_patience=config.early_stopping_patience
            )
            
            # Run optimization
            study = await self._run_optimization(config, objective)
            
            # Train final model with best parameters
            best_params = study.best_params
            final_model = await self._train_final_model(
                best_params, X_train, y_train, X_val, y_val
            )
            
            # Evaluate final model
            performance_metrics = await self._evaluate_model(
                final_model, X_val, y_val
            )
            
            # Save model and create version
            model_path = await self._save_model(job_id, final_model, best_params)
            
            # Create model version
            version = ModelVersion(
                version_id=job_id,
                model_name=config.model_name,
                training_timestamp=start_time,
                performance_metrics=performance_metrics,
                hyperparameters=best_params,
                model_path=model_path,
                config=config,
                validation_score=study.best_value,
                training_duration=(datetime.now() - start_time).total_seconds()
            )
            
            # Register model version
            await self._register_model_version(version)
            
            # Update job status
            self.running_jobs[job_id]['status'] = TrainingStatus.COMPLETED
            self.running_jobs[job_id]['result'] = version
            
            logger.info(f"Training completed for {config.model_name} (score: {study.best_value:.4f})")
            
        except Exception as e:
            logger.error(f"Training failed for job {job_id}: {e}")
            self.running_jobs[job_id]['status'] = TrainingStatus.FAILED
            self.running_jobs[job_id]['error'] = str(e)
    
    async def _prepare_training_data(
        self, 
        config: TrainingConfig
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Prepare training and validation data."""
        # Generate synthetic data if needed
        dataset = self.data_generator.generate_balanced_dataset(
            size=5000,  # Base dataset size
            cv_job_ratio=1.5,
            skill_diversity=0.8
        )
        
        # Extract features and labels
        # This is a simplified example - in reality, you'd use your feature extraction
        X = np.random.random((len(dataset['cvs']), 100))  # Placeholder
        y = np.random.randint(0, 2, len(dataset['cvs']))  # Placeholder
        
        # Split into train/validation
        split_idx = int(len(X) * (1 - config.validation_fraction))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        return X_train, y_train, X_val, y_val
    
    async def _run_optimization(
        self, 
        config: TrainingConfig, 
        objective: SkillsMatchingObjective
    ) -> optuna.Study:
        """Run hyperparameter optimization."""
        study_name = f"{config.model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        study = optuna.create_study(
            direction=config.optimization_direction,
            study_name=study_name,
            pruner=optuna.pruners.MedianPruner() if config.pruning_enabled else None
        )
        
        # Run optimization
        study.optimize(
            objective,
            n_trials=config.n_trials,
            timeout=config.timeout,
            n_jobs=1  # Keep single-threaded for now
        )
        
        return study
    
    async def _train_final_model(
        self, 
        params: Dict,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> Any:
        """Train the final model with best parameters."""
        # This is a placeholder - implement actual model training
        from sklearn.ensemble import RandomForestClassifier
        
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)
        
        return model
    
    async def _evaluate_model(
        self, 
        model: Any, 
        X_val: np.ndarray, 
        y_val: np.ndarray
    ) -> Dict[str, float]:
        """Evaluate model performance."""
        y_pred = model.predict(X_val)
        
        # Calculate metrics
        metrics = {
            'accuracy': accuracy_score(y_val, y_pred),
            'precision': precision_score(y_val, y_pred, average='weighted'),
            'recall': recall_score(y_val, y_pred, average='weighted'),
            'f1_score': f1_score(y_val, y_pred, average='weighted')
        }
        
        # Add confidence scores if available
        if hasattr(model, 'predict_proba'):
            y_proba = model.predict_proba(X_val)
            confidence = np.max(y_proba, axis=1).mean()
            metrics['confidence'] = confidence
        
        return metrics
    
    async def _save_model(
        self, 
        job_id: str, 
        model: Any, 
        params: Dict
    ) -> str:
        """Save trained model to disk."""
        model_path = self.models_dir / f"{job_id}_model.pkl"
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Save parameters
        params_path = self.models_dir / f"{job_id}_params.json"
        with open(params_path, 'w') as f:
            json.dump(params, f, indent=2)
        
        return str(model_path)
    
    async def _register_model_version(self, version: ModelVersion):
        """Register a new model version."""
        model_name = version.model_name
        
        if model_name not in self.model_registry:
            self.model_registry[model_name] = []
        
        self.model_registry[model_name].append(version)
        self.completed_jobs.append(version)
        
        # Keep only last N versions
        max_versions = 10
        if len(self.model_registry[model_name]) > max_versions:
            old_version = self.model_registry[model_name].pop(0)
            # Optionally clean up old model files
            try:
                Path(old_version.model_path).unlink()
            except Exception as e:
                logger.warning(f"Failed to delete old model: {e}")
        
        # Track performance
        self.performance_tracker.record_metrics(
            model_name=model_name,
            metrics=version.performance_metrics,
            timestamp=version.training_timestamp
        )
    
    async def _check_completed_jobs(self):
        """Check and clean up completed jobs."""
        completed_job_ids = []
        
        for job_id, job_record in self.running_jobs.items():
            task = job_record['task']
            if task.done():
                completed_job_ids.append(job_id)
                
                if job_record['status'] == TrainingStatus.COMPLETED:
                    logger.info(f"Job {job_id} completed successfully")
                else:
                    logger.error(f"Job {job_id} failed: {job_record.get('error', 'Unknown error')}")
        
        # Clean up completed jobs
        for job_id in completed_job_ids:
            del self.running_jobs[job_id]
    
    def get_status(self) -> Dict:
        """Get current trainer status."""
        return {
            'is_running': self.is_running,
            'queue_size': len(self.training_queue),
            'running_jobs': len(self.running_jobs),
            'completed_jobs': len(self.completed_jobs),
            'model_registry': {
                name: len(versions) 
                for name, versions in self.model_registry.items()
            },
            'last_training': (
                max(self.completed_jobs, key=lambda x: x.training_timestamp).training_timestamp.isoformat()
                if self.completed_jobs else None
            )
        }
    
    def get_model_history(self, model_name: str) -> List[Dict]:
        """Get training history for a specific model."""
        if model_name not in self.model_registry:
            return []
        
        return [version.to_dict() for version in self.model_registry[model_name]]
    
    def get_best_model(self, model_name: str) -> Optional[ModelVersion]:
        """Get the best performing version of a model."""
        if model_name not in self.model_registry:
            return None
        
        versions = self.model_registry[model_name]
        return max(versions, key=lambda v: v.validation_score) if versions else None
    
    def _save_state(self):
        """Save trainer state to disk."""
        state = {
            'model_registry': {
                name: [version.to_dict() for version in versions]
                for name, versions in self.model_registry.items()
            },
            'completed_jobs': [job.to_dict() for job in self.completed_jobs]
        }
        
        state_path = self.models_dir / 'trainer_state.json'
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def _load_state(self):
        """Load trainer state from disk."""
        state_path = self.models_dir / 'trainer_state.json'
        
        if not state_path.exists():
            return
        
        try:
            with open(state_path, 'r') as f:
                state = json.load(f)
            
            # Reconstruct model registry
            self.model_registry = {}
            for name, versions_data in state.get('model_registry', {}).items():
                self.model_registry[name] = [
                    ModelVersion.from_dict(version_data) 
                    for version_data in versions_data
                ]
            
            # Reconstruct completed jobs
            self.completed_jobs = [
                ModelVersion.from_dict(job_data)
                for job_data in state.get('completed_jobs', [])
            ]
            
            logger.info(f"Loaded trainer state: {len(self.model_registry)} models")
            
        except Exception as e:
            logger.error(f"Failed to load trainer state: {e}")

# Example usage and testing
if __name__ == "__main__":
    import asyncio
    
    async def test_auto_trainer():
        config = {
            'interval_seconds': 60,  # 1 minute for testing
            'max_concurrent_jobs': 1,
            'models_dir': 'test_models'
        }
        
        trainer = AutoTrainer(config)
        
        # Schedule a test training job
        test_config = TrainingConfig(
            model_name="test_model",
            n_trials=10,
            timeout=120
        )
        
        job_id = await trainer.schedule_training(test_config)
        print(f"Scheduled job: {job_id}")
        
        # Run for a short time
        task = asyncio.create_task(trainer.start_training_loop())
        await asyncio.sleep(180)  # 3 minutes
        await trainer.stop()
        
        # Check results
        print(f"Final status: {trainer.get_status()}")
    
    # Run test
    asyncio.run(test_auto_trainer())
