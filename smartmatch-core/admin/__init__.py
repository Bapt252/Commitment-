"""
Admin Module for SmartMatch-Core
===============================

This module provides administrative interfaces and controls for the ML optimization system:
- Real-time optimization dashboard
- Model lifecycle management
- System monitoring and control

Key Components:
- OptimizationDashboard: Interactive dashboard for monitoring and control
- ModelController: Administrative API for model management
- AdminOrchestrator: Coordination layer for admin functions

Integration Points:
- Pipeline orchestration (auto-training, A/B testing, drift monitoring)
- Metrics and optimization modules
- Enhanced Skills Matcher

Author: AI Assistant & Bapt252
Session: 5 - ML Optimization Intelligence
"""

from .optimization_dashboard import (
    OptimizationDashboard,
    DashboardConfig,
    DashboardMetrics,
    VisualizationComponent
)
from .model_controller import (
    ModelController,
    ModelLifecycleManager,
    AdminAPI,
    NotificationSystem,
    DeploymentStrategy
)

# Admin coordination utilities
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import json
import os

logger = logging.getLogger(__name__)

class AdminOrchestrator:
    """
    Central orchestrator for all administrative functions.
    Coordinates dashboard, model controller, and system monitoring.
    """
    
    def __init__(self, config: Dict, pipeline_orchestrator=None):
        self.config = config
        self.pipeline_orchestrator = pipeline_orchestrator
        
        # Initialize admin components
        self.dashboard = OptimizationDashboard(
            config.get('dashboard', {}),
            pipeline_orchestrator=pipeline_orchestrator
        )
        self.model_controller = ModelController(
            config.get('model_controller', {}),
            pipeline_orchestrator=pipeline_orchestrator
        )
        
        # Admin state
        self.is_running = False
        self.admin_sessions = {}
        self.system_alerts = []
        
    async def start_admin_system(self):
        """Start the complete admin system."""
        if self.is_running:
            logger.warning("Admin system already running")
            return
            
        self.is_running = True
        logger.info("Starting Admin system")
        
        # Start all admin components
        tasks = [
            self.dashboard.start_dashboard(),
            self.model_controller.start_api_server()
        ]
        
        await asyncio.gather(*tasks)
        logger.info("Admin system fully operational")
    
    async def stop_admin_system(self):
        """Gracefully stop the admin system."""
        logger.info("Stopping Admin system")
        self.is_running = False
        
        # Stop all components
        await self.dashboard.stop_dashboard()
        await self.model_controller.stop_api_server()
        
        logger.info("Admin system stopped")
    
    def get_system_status(self) -> Dict:
        """Get comprehensive system status."""
        pipeline_status = (
            self.pipeline_orchestrator.get_pipeline_status() 
            if self.pipeline_orchestrator else {}
        )
        
        return {
            'admin_system': {
                'is_running': self.is_running,
                'timestamp': datetime.now().isoformat(),
                'active_sessions': len(self.admin_sessions),
                'pending_alerts': len(self.system_alerts)
            },
            'dashboard': self.dashboard.get_status(),
            'model_controller': self.model_controller.get_status(),
            'pipeline': pipeline_status
        }
    
    def add_system_alert(self, alert: Dict):
        """Add a system-wide alert."""
        alert['timestamp'] = datetime.now().isoformat()
        alert['id'] = f"alert_{len(self.system_alerts)}_{int(datetime.now().timestamp())}"
        self.system_alerts.append(alert)
        
        # Limit alert history
        if len(self.system_alerts) > 100:
            self.system_alerts = self.system_alerts[-100:]
        
        logger.info(f"System alert added: {alert['type']} - {alert['message']}")
    
    def get_system_alerts(self, limit: int = 50) -> List[Dict]:
        """Get recent system alerts."""
        return sorted(self.system_alerts, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def clear_system_alerts(self, alert_ids: Optional[List[str]] = None):
        """Clear system alerts."""
        if alert_ids:
            self.system_alerts = [a for a in self.system_alerts if a['id'] not in alert_ids]
        else:
            self.system_alerts = []
        logger.info(f"Cleared {len(alert_ids) if alert_ids else 'all'} system alerts")

# Utility functions for admin configuration
def create_admin_config(
    dashboard_port: int = 8501,
    api_port: int = 8080,
    enable_auth: bool = True,
    **kwargs
) -> Dict:
    """Create a standard admin configuration."""
    return {
        'dashboard': {
            'port': dashboard_port,
            'host': '0.0.0.0',
            'enable_auth': enable_auth,
            'update_interval': 5,  # seconds
            'max_data_points': 1000,
            **kwargs.get('dashboard', {})
        },
        'model_controller': {
            'api_port': api_port,
            'api_host': '0.0.0.0',
            'enable_auth': enable_auth,
            'max_concurrent_deployments': 3,
            'deployment_timeout': 300,  # seconds
            **kwargs.get('model_controller', {})
        },
        'notifications': {
            'email_enabled': False,
            'slack_enabled': False,
            'webhook_enabled': True,
            'alert_thresholds': {
                'error_rate': 0.05,
                'latency_p95': 1000,  # ms
                'drift_score': 0.1
            },
            **kwargs.get('notifications', {})
        }
    }

def setup_admin_logging(log_level: str = 'INFO') -> None:
    """Setup admin-specific logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('admin.log'),
            logging.StreamHandler()
        ]
    )

def load_admin_state(filepath: str = 'admin_state.json') -> Optional[Dict]:
    """Load admin state from file."""
    if not os.path.exists(filepath):
        return None
        
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load admin state: {e}")
        return None

def save_admin_state(state: Dict, filepath: str = 'admin_state.json') -> bool:
    """Save admin state to file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Failed to save admin state: {e}")
        return False

# Export main classes and utilities
__all__ = [
    'OptimizationDashboard', 'DashboardConfig', 'DashboardMetrics', 'VisualizationComponent',
    'ModelController', 'ModelLifecycleManager', 'AdminAPI', 'NotificationSystem',
    'AdminOrchestrator',
    'create_admin_config',
    'setup_admin_logging',
    'load_admin_state',
    'save_admin_state'
]

# Version info
__version__ = "1.0.0"
__author__ = "AI Assistant & Bapt252"
__session__ = "5 - ML Optimization Intelligence"
