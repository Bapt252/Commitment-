"""
Model Controller for SmartMatch-Core
===================================

Administrative API and model lifecycle management system.
Provides centralized control over model deployment, monitoring, and optimization.

Key Features:
- Model lifecycle management (deploy/rollback/version control)
- Administrative API endpoints
- Notification and alert system
- Deployment strategies (blue-green, canary, rolling)
- Integration with pipeline orchestrator
- Real-time monitoring and health checks

Author: AI Assistant & Bapt252
Session: 5 - ML Optimization Intelligence
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import os
import uuid
from dataclasses import dataclass, asdict
import pickle
import joblib
from pathlib import Path
import aiofiles
import httpx
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Enums and Models
class DeploymentStrategy(str, Enum):
    """Deployment strategies for model rollout."""
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    IMMEDIATE = "immediate"

class ModelStatus(str, Enum):
    """Model deployment status."""
    TRAINING = "training"
    VALIDATING = "validating"
    STAGING = "staging"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    FAILED = "failed"

class AlertSeverity(str, Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

# Pydantic Models
class ModelMetadata(BaseModel):
    """Model metadata for tracking and versioning."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    version: str
    algorithm: str
    created_at: datetime = Field(default_factory=datetime.now)
    trained_by: str
    training_duration: Optional[float] = None
    metrics: Dict[str, float] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    file_path: Optional[str] = None
    status: ModelStatus = ModelStatus.TRAINING

class DeploymentConfig(BaseModel):
    """Configuration for model deployment."""
    model_id: str
    strategy: DeploymentStrategy = DeploymentStrategy.BLUE_GREEN
    traffic_percentage: float = Field(default=100.0, ge=0.0, le=100.0)
    rollback_threshold: float = Field(default=0.05, ge=0.0, le=1.0)
    health_check_interval: int = Field(default=60, ge=10)
    auto_rollback: bool = True
    notification_channels: List[str] = Field(default_factory=list)

class Alert(BaseModel):
    """System alert model."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    severity: AlertSeverity
    source: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None

class ModelPerformanceMetrics(BaseModel):
    """Real-time model performance metrics."""
    model_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    latency_p50: float
    latency_p95: float
    throughput: float
    error_rate: float

# Core Classes
@dataclass
class ModelVersion:
    """Represents a model version with metadata."""
    metadata: ModelMetadata
    model_object: Any
    deployment_config: Optional[DeploymentConfig] = None
    performance_history: List[ModelPerformanceMetrics] = None
    
    def __post_init__(self):
        if self.performance_history is None:
            self.performance_history = []

class ModelLifecycleManager:
    """Manages the complete lifecycle of ML models."""
    
    def __init__(self, models_dir: str = "models", max_versions: int = 10):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        self.max_versions = max_versions
        
        # Model registry
        self.models: Dict[str, ModelVersion] = {}
        self.active_deployments: Dict[str, DeploymentConfig] = {}
        
        # Load existing models
        self._load_models_from_disk()
    
    def _load_models_from_disk(self):
        """Load existing models from disk on startup."""
        try:
            for model_file in self.models_dir.glob("*.pkl"):
                metadata_file = model_file.with_suffix(".json")
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata_dict = json.load(f)
                    
                    metadata = ModelMetadata(**metadata_dict)
                    model_object = joblib.load(model_file)
                    
                    self.models[metadata.id] = ModelVersion(
                        metadata=metadata,
                        model_object=model_object
                    )
                    
            logger.info(f"Loaded {len(self.models)} models from disk")
        except Exception as e:
            logger.error(f"Error loading models from disk: {e}")
    
    async def register_model(
        self,
        model_object: Any,
        metadata: ModelMetadata
    ) -> str:
        """Register a new model version."""
        try:
            # Save model to disk
            model_path = self.models_dir / f"{metadata.id}.pkl"
            metadata_path = self.models_dir / f"{metadata.id}.json"
            
            # Save model object
            joblib.dump(model_object, model_path)
            
            # Save metadata
            with open(metadata_path, 'w') as f:
                json.dump(metadata.dict(), f, indent=2, default=str)
            
            # Register in memory
            self.models[metadata.id] = ModelVersion(
                metadata=metadata,
                model_object=model_object
            )
            
            # Update file path
            metadata.file_path = str(model_path)
            
            logger.info(f"Registered model {metadata.name} v{metadata.version} with ID {metadata.id}")
            return metadata.id
            
        except Exception as e:
            logger.error(f"Failed to register model {metadata.name}: {e}")
            raise
    
    async def deploy_model(
        self,
        model_id: str,
        deployment_config: DeploymentConfig
    ) -> bool:
        """Deploy a model using the specified strategy."""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        model_version = self.models[model_id]
        
        try:
            # Update model status
            model_version.metadata.status = ModelStatus.VALIDATING
            
            # Validate model before deployment
            if not await self._validate_model(model_version):
                model_version.metadata.status = ModelStatus.FAILED
                return False
            
            # Execute deployment strategy
            success = await self._execute_deployment_strategy(
                model_version,
                deployment_config
            )
            
            if success:
                model_version.metadata.status = ModelStatus.DEPLOYED
                model_version.deployment_config = deployment_config
                self.active_deployments[model_id] = deployment_config
                logger.info(f"Successfully deployed model {model_id}")
            else:
                model_version.metadata.status = ModelStatus.FAILED
                logger.error(f"Failed to deploy model {model_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deploying model {model_id}: {e}")
            model_version.metadata.status = ModelStatus.FAILED
            return False
    
    async def rollback_model(self, model_id: str) -> bool:
        """Rollback a deployed model to the previous version."""
        if model_id not in self.active_deployments:
            raise ValueError(f"Model {model_id} is not actively deployed")
        
        try:
            # Find previous version
            current_model = self.models[model_id]
            previous_versions = [
                m for m in self.models.values()
                if (m.metadata.name == current_model.metadata.name and 
                    m.metadata.id != model_id and
                    m.metadata.status == ModelStatus.DEPLOYED)
            ]
            
            if not previous_versions:
                logger.warning(f"No previous version found for model {model_id}")
                return False
            
            # Get most recent previous version
            previous_version = max(previous_versions, key=lambda x: x.metadata.created_at)
            
            # Execute rollback
            rollback_config = DeploymentConfig(
                model_id=previous_version.metadata.id,
                strategy=DeploymentStrategy.IMMEDIATE
            )
            
            success = await self.deploy_model(previous_version.metadata.id, rollback_config)
            
            if success:
                # Update status of rolled-back model
                current_model.metadata.status = ModelStatus.DEPRECATED
                del self.active_deployments[model_id]
                logger.info(f"Successfully rolled back model {model_id} to {previous_version.metadata.id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error rolling back model {model_id}: {e}")
            return False
    
    async def _validate_model(self, model_version: ModelVersion) -> bool:
        """Validate model before deployment."""
        try:
            # Basic validation checks
            if model_version.model_object is None:
                return False
            
            # Check if model has required methods
            required_methods = ['predict', 'fit']
            for method in required_methods:
                if not hasattr(model_version.model_object, method):
                    logger.warning(f"Model missing required method: {method}")
            
            # Additional validation can be added here
            return True
            
        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return False
    
    async def _execute_deployment_strategy(
        self,
        model_version: ModelVersion,
        deployment_config: DeploymentConfig
    ) -> bool:
        """Execute the specified deployment strategy."""
        strategy = deployment_config.strategy
        
        if strategy == DeploymentStrategy.IMMEDIATE:
            return await self._immediate_deployment(model_version, deployment_config)
        elif strategy == DeploymentStrategy.BLUE_GREEN:
            return await self._blue_green_deployment(model_version, deployment_config)
        elif strategy == DeploymentStrategy.CANARY:
            return await self._canary_deployment(model_version, deployment_config)
        elif strategy == DeploymentStrategy.ROLLING:
            return await self._rolling_deployment(model_version, deployment_config)
        else:
            logger.error(f"Unknown deployment strategy: {strategy}")
            return False
    
    async def _immediate_deployment(self, model_version: ModelVersion, config: DeploymentConfig) -> bool:
        """Immediate deployment - replace current model instantly."""
        try:
            # Simulate deployment process
            logger.info(f"Starting immediate deployment of {model_version.metadata.id}")
            await asyncio.sleep(1)  # Simulate deployment time
            
            # Update status
            model_version.metadata.status = ModelStatus.STAGING
            await asyncio.sleep(1)
            
            return True
        except Exception as e:
            logger.error(f"Immediate deployment failed: {e}")
            return False
    
    async def _blue_green_deployment(self, model_version: ModelVersion, config: DeploymentConfig) -> bool:
        """Blue-green deployment - switch traffic after validation."""
        try:
            logger.info(f"Starting blue-green deployment of {model_version.metadata.id}")
            
            # Deploy to green environment
            model_version.metadata.status = ModelStatus.STAGING
            await asyncio.sleep(2)  # Simulate green environment setup
            
            # Health checks
            if not await self._health_check(model_version):
                return False
            
            # Switch traffic
            logger.info("Switching traffic to green environment")
            await asyncio.sleep(1)
            
            return True
        except Exception as e:
            logger.error(f"Blue-green deployment failed: {e}")
            return False
    
    async def _canary_deployment(self, model_version: ModelVersion, config: DeploymentConfig) -> bool:
        """Canary deployment - gradual traffic increase."""
        try:
            logger.info(f"Starting canary deployment of {model_version.metadata.id}")
            
            # Start with small traffic percentage
            traffic_percentages = [5, 10, 25, 50, 100]
            
            for percentage in traffic_percentages:
                if percentage > config.traffic_percentage:
                    break
                    
                logger.info(f"Routing {percentage}% traffic to canary")
                model_version.metadata.status = ModelStatus.STAGING
                
                # Monitor for issues
                await asyncio.sleep(2)  # Simulate monitoring period
                
                if not await self._health_check(model_version):
                    logger.warning("Canary deployment health check failed, rolling back")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Canary deployment failed: {e}")
            return False
    
    async def _rolling_deployment(self, model_version: ModelVersion, config: DeploymentConfig) -> bool:
        """Rolling deployment - update instances one by one."""
        try:
            logger.info(f"Starting rolling deployment of {model_version.metadata.id}")
            
            # Simulate rolling update across instances
            instances = 5  # Mock number of instances
            
            for i in range(instances):
                logger.info(f"Updating instance {i+1}/{instances}")
                await asyncio.sleep(1)  # Simulate instance update
                
                # Health check after each instance
                if not await self._health_check(model_version):
                    logger.warning(f"Rolling deployment failed at instance {i+1}")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Rolling deployment failed: {e}")
            return False
    
    async def _health_check(self, model_version: ModelVersion) -> bool:
        """Perform health check on deployed model."""
        try:
            # Simulate health check
            await asyncio.sleep(0.5)
            
            # Mock health check logic
            import random
            return random.random() > 0.1  # 90% success rate
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get comprehensive model information."""
        if model_id not in self.models:
            return None
        
        model_version = self.models[model_id]
        return {
            'metadata': model_version.metadata.dict(),
            'deployment_config': model_version.deployment_config.dict() if model_version.deployment_config else None,
            'performance_history': [m.dict() for m in model_version.performance_history],
            'is_active': model_id in self.active_deployments
        }
    
    def list_models(self, status_filter: Optional[ModelStatus] = None) -> List[Dict]:
        """List all registered models."""
        models = list(self.models.values())
        
        if status_filter:
            models = [m for m in models if m.metadata.status == status_filter]
        
        return [self.get_model_info(m.metadata.id) for m in models]

class NotificationSystem:
    """System for sending notifications and alerts."""
    
    def __init__(self, config: Dict):
        self.config = config
        self.alerts: List[Alert] = []
        self.notification_handlers: Dict[str, Callable] = {
            'email': self._send_email,
            'slack': self._send_slack,
            'webhook': self._send_webhook
        }
    
    async def send_alert(self, alert: Alert):
        """Send alert through configured channels."""
        self.alerts.append(alert)
        
        # Limit alert history
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        # Send notifications
        for channel in self.config.get('channels', []):
            if channel in self.notification_handlers:
                try:
                    await self.notification_handlers[channel](alert)
                except Exception as e:
                    logger.error(f"Failed to send {channel} notification: {e}")
    
    async def _send_email(self, alert: Alert):
        """Send email notification."""
        if not self.config.get('email_enabled', False):
            return
        
        # Mock email sending
        logger.info(f"Sending email alert: {alert.message}")
    
    async def _send_slack(self, alert: Alert):
        """Send Slack notification."""
        if not self.config.get('slack_enabled', False):
            return
        
        # Mock Slack sending
        logger.info(f"Sending Slack alert: {alert.message}")
    
    async def _send_webhook(self, alert: Alert):
        """Send webhook notification."""
        webhook_url = self.config.get('webhook_url')
        if not webhook_url:
            return
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=alert.dict(),
                    timeout=10.0
                )
                response.raise_for_status()
            logger.info(f"Sent webhook alert: {alert.message}")
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
    
    def get_alerts(self, 
                   severity_filter: Optional[AlertSeverity] = None,
                   limit: int = 100) -> List[Alert]:
        """Get alerts with optional filtering."""
        alerts = self.alerts
        
        if severity_filter:
            alerts = [a for a in alerts if a.severity == severity_filter]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()
                return True
        return False

class AdminAPI:
    """Administrative API for model management."""
    
    def __init__(self, 
                 lifecycle_manager: ModelLifecycleManager,
                 notification_system: NotificationSystem,
                 pipeline_orchestrator=None):
        self.lifecycle_manager = lifecycle_manager
        self.notification_system = notification_system
        self.pipeline_orchestrator = pipeline_orchestrator
        
        # Create FastAPI app
        self.app = FastAPI(
            title="SmartMatch Admin API",
            description="Administrative API for ML model management",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/models", response_model=List[Dict])
        async def list_models(status: Optional[ModelStatus] = None):
            return self.lifecycle_manager.list_models(status)
        
        @self.app.get("/models/{model_id}", response_model=Dict)
        async def get_model(model_id: str):
            model_info = self.lifecycle_manager.get_model_info(model_id)
            if not model_info:
                raise HTTPException(status_code=404, detail="Model not found")
            return model_info
        
        @self.app.post("/models/{model_id}/deploy")
        async def deploy_model(
            model_id: str,
            deployment_config: DeploymentConfig,
            background_tasks: BackgroundTasks
        ):
            try:
                # Start deployment in background
                background_tasks.add_task(
                    self.lifecycle_manager.deploy_model,
                    model_id,
                    deployment_config
                )
                
                # Send notification
                alert = Alert(
                    severity=AlertSeverity.INFO,
                    source="admin_api",
                    message=f"Starting deployment of model {model_id}",
                    details={"model_id": model_id, "strategy": deployment_config.strategy}
                )
                await self.notification_system.send_alert(alert)
                
                return {"message": "Deployment started", "model_id": model_id}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.post("/models/{model_id}/rollback")
        async def rollback_model(
            model_id: str,
            background_tasks: BackgroundTasks
        ):
            try:
                # Start rollback in background
                background_tasks.add_task(
                    self.lifecycle_manager.rollback_model,
                    model_id
                )
                
                # Send notification
                alert = Alert(
                    severity=AlertSeverity.WARNING,
                    source="admin_api",
                    message=f"Starting rollback of model {model_id}",
                    details={"model_id": model_id}
                )
                await self.notification_system.send_alert(alert)
                
                return {"message": "Rollback started", "model_id": model_id}
            except Exception as e:
                raise HTTPException(status_code=400, detail=str(e))
        
        @self.app.get("/alerts", response_model=List[Alert])
        async def get_alerts(
            severity: Optional[AlertSeverity] = None,
            limit: int = 100
        ):
            return self.notification_system.get_alerts(severity, limit)
        
        @self.app.post("/alerts/{alert_id}/acknowledge")
        async def acknowledge_alert(alert_id: str, acknowledged_by: str):
            success = self.notification_system.acknowledge_alert(alert_id, acknowledged_by)
            if not success:
                raise HTTPException(status_code=404, detail="Alert not found")
            return {"message": "Alert acknowledged"}
        
        @self.app.get("/system/status")
        async def get_system_status():
            pipeline_status = (
                self.pipeline_orchestrator.get_pipeline_status() 
                if self.pipeline_orchestrator else {}
            )
            
            return {
                "models": {
                    "total": len(self.lifecycle_manager.models),
                    "active_deployments": len(self.lifecycle_manager.active_deployments)
                },
                "alerts": {
                    "total": len(self.notification_system.alerts),
                    "unacknowledged": len([
                        a for a in self.notification_system.alerts if not a.acknowledged
                    ])
                },
                "pipeline": pipeline_status
            }
        
        @self.app.post("/system/restart")
        async def restart_system():
            """Restart system components."""
            try:
                if self.pipeline_orchestrator:
                    await self.pipeline_orchestrator.stop_pipeline()
                    await asyncio.sleep(2)
                    await self.pipeline_orchestrator.start_pipeline()
                
                alert = Alert(
                    severity=AlertSeverity.INFO,
                    source="admin_api",
                    message="System restart completed"
                )
                await self.notification_system.send_alert(alert)
                
                return {"message": "System restart initiated"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

class ModelController:
    """Main controller for model lifecycle and administration."""
    
    def __init__(self, config: Dict, pipeline_orchestrator=None):
        self.config = config
        self.pipeline_orchestrator = pipeline_orchestrator
        
        # Initialize components
        self.lifecycle_manager = ModelLifecycleManager(
            models_dir=config.get('models_dir', 'models'),
            max_versions=config.get('max_versions', 10)
        )
        
        self.notification_system = NotificationSystem(
            config.get('notifications', {})
        )
        
        self.admin_api = AdminAPI(
            self.lifecycle_manager,
            self.notification_system,
            pipeline_orchestrator
        )
        
        # Controller state
        self.is_running = False
        self.api_server = None
        self.monitoring_task = None
    
    async def start_api_server(self):
        """Start the administrative API server."""
        if self.is_running:
            logger.warning("Model controller already running")
            return
        
        self.is_running = True
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info(f"Model controller started on {self.config.get('api_host', '0.0.0.0')}:{self.config.get('api_port', 8080)}")
    
    async def stop_api_server(self):
        """Stop the administrative API server."""
        logger.info("Stopping model controller")
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
        
        if self.api_server:
            await self.api_server.shutdown()
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop for model health."""
        while self.is_running:
            try:
                await self._check_model_health()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _check_model_health(self):
        """Check health of all deployed models."""
        for model_id, deployment_config in self.lifecycle_manager.active_deployments.items():
            try:
                model_version = self.lifecycle_manager.models[model_id]
                
                # Simulate health check
                is_healthy = await self.lifecycle_manager._health_check(model_version)
                
                if not is_healthy:
                    alert = Alert(
                        severity=AlertSeverity.ERROR,
                        source="health_monitor",
                        message=f"Model {model_id} health check failed",
                        details={"model_id": model_id}
                    )
                    await self.notification_system.send_alert(alert)
                    
                    # Auto-rollback if configured
                    if deployment_config.auto_rollback:
                        logger.warning(f"Auto-rolling back unhealthy model {model_id}")
                        await self.lifecycle_manager.rollback_model(model_id)
                        
            except Exception as e:
                logger.error(f"Error checking health for model {model_id}: {e}")
    
    def get_status(self) -> Dict:
        """Get controller status."""
        return {
            'is_running': self.is_running,
            'api_port': self.config.get('api_port', 8080),
            'models_count': len(self.lifecycle_manager.models),
            'active_deployments': len(self.lifecycle_manager.active_deployments),
            'pending_alerts': len([
                a for a in self.notification_system.alerts if not a.acknowledged
            ])
        }

# For standalone execution and testing
if __name__ == "__main__":
    import uvicorn
    
    # Create controller with mock config
    config = {
        'api_port': 8080,
        'models_dir': 'test_models',
        'notifications': {
            'webhook_enabled': True,
            'webhook_url': 'http://localhost:9000/webhook'
        }
    }
    
    controller = ModelController(config)
    
    # Run the API server
    uvicorn.run(
        controller.admin_api.app,
        host="0.0.0.0",
        port=config['api_port'],
        log_level="info"
    )
