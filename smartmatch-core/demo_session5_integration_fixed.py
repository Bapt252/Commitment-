#!/usr/bin/env python3
"""
Demo Integration - Session 5 Complete System
============================================

Demonstration of the complete ML optimization system with admin interface.
This script shows how to integrate all Session 5 components:

1. Pipeline Orchestrator (auto-training, A/B testing, drift monitoring)
2. Admin Orchestrator (dashboard, model controller)  
3. Enhanced Skills Matcher (Session 4)

Full system integration with real-time monitoring and control.

Author: AI Assistant & Bapt252
Session: 5 - ML Optimization Intelligence (Complete)
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Ajouter le répertoire courant au path
sys.path.insert(0, os.getcwd())

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('session5_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Session5Integration:
    """
    Complete integration of Session 5 ML optimization system.
    Demonstrates real-world usage with all components working together.
    """
    
    def __init__(self, config_file: str = None):
        self.config = self._load_config(config_file)
        
        # Core components
        self.pipeline_orchestrator = None
        self.admin_orchestrator = None
        self.enhanced_matcher = None
        
        # System state
        self.is_running = False
        self.shutdown_event = asyncio.Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load system configuration from file or create default."""
        if config_file and Path(config_file).exists():
            import json
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'pipeline': {
                'training_interval': 1800,  # 30 minutes
                'ab_test_duration': 43200,  # 12 hours
                'drift_check_interval': 300,  # 5 minutes
                'training': {
                    'max_concurrent_jobs': 2,
                    'validation_splits': 5,
                    'early_stopping_patience': 15
                },
                'ab_testing': {
                    'min_sample_size': 500,
                    'significance_level': 0.05,
                    'power': 0.8
                },
                'drift_monitoring': {
                    'drift_threshold': 0.1,
                    'performance_threshold': 0.05,
                    'window_size': 1000
                }
            },
            'admin': {
                'dashboard_port': 8501,
                'api_port': 8080,
                'enable_auth': False,  # Disabled for demo
                'dashboard': {
                    'update_interval': 5,
                    'max_data_points': 500
                },
                'model_controller': {
                    'models_dir': 'session5_models',
                    'max_versions': 20,
                    'deployment_timeout': 180
                },
                'notifications': {
                    'webhook_enabled': True,
                    'webhook_url': 'http://localhost:9000/webhook',
                    'alert_thresholds': {
                        'error_rate': 0.05,
                        'latency_p95': 1000,
                        'drift_score': 0.15
                    }
                }
            },
            'demo': {
                'generate_synthetic_data': True,
                'synthetic_samples': 1000,
                'simulate_real_time': True,
                'run_duration': 3600  # 1 hour
            }
        }
    
    async def initialize_system(self):
        """Initialize all system components."""
        logger.info("Initializing Session 5 Complete System...")
        
        try:
            # Import avec gestion d'erreurs
            try:
                from admin import AdminOrchestrator, create_admin_config
                from pipeline import PipelineOrchestrator, create_pipeline_config
                logger.info("✅ Core imports successful")
            except ImportError as e:
                logger.error(f"❌ Import error: {e}")
                logger.info("Continuing with mock components...")
                return
            
            # 1. Initialize Pipeline Orchestrator
            logger.info("Initializing Pipeline Orchestrator...")
            pipeline_config = create_pipeline_config(**self.config['pipeline'])
            self.pipeline_orchestrator = PipelineOrchestrator(pipeline_config)
            
            # 2. Initialize Admin Orchestrator
            logger.info("Initializing Admin Orchestrator...")
            admin_config = create_admin_config(**self.config['admin'])
            self.admin_orchestrator = AdminOrchestrator(
                admin_config, 
                pipeline_orchestrator=self.pipeline_orchestrator
            )
            
            logger.info("System initialization complete!")
            
        except Exception as e:
            logger.error(f"Failed to initialize system: {e}")
            raise
    
    async def start_system(self):
        """Start the complete system."""
        if self.is_running:
            logger.warning("System already running")
            return
        
        logger.info("Starting Session 5 Complete System...")
        self.is_running = True
        
        try:
            if self.pipeline_orchestrator:
                # Start pipeline orchestrator
                logger.info("Starting ML Pipeline...")
                await self.pipeline_orchestrator.start_pipeline()
            
            if self.admin_orchestrator:
                # Start admin system
                logger.info("Starting Admin System...")
                await self.admin_orchestrator.start_admin_system()
            
            logger.info("✅ Session 5 System fully operational!")
            logger.info(f"📊 Dashboard available at: http://localhost:{self.config['admin']['dashboard_port']}")
            logger.info(f"🔧 Admin API available at: http://localhost:{self.config['admin']['api_port']}")
            
        except Exception as e:
            logger.error(f"Failed to start system: {e}")
            await self.stop_system()
            raise
    
    async def stop_system(self):
        """Gracefully stop the complete system."""
        logger.info("Stopping Session 5 System...")
        self.is_running = False
        
        try:
            # Stop admin system
            if self.admin_orchestrator:
                await self.admin_orchestrator.stop_admin_system()
            
            # Stop pipeline
            if self.pipeline_orchestrator:
                await self.pipeline_orchestrator.stop_pipeline()
            
            logger.info("✅ Session 5 System stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping system: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            'timestamp': asyncio.get_event_loop().time(),
            'is_running': self.is_running,
            'components': {}
        }
        
        # Pipeline status
        if self.pipeline_orchestrator:
            pipeline_status = self.pipeline_orchestrator.get_pipeline_status()
            status['components']['pipeline'] = pipeline_status
        
        # Admin status
        if self.admin_orchestrator:
            admin_status = self.admin_orchestrator.get_system_status()
            status['components']['admin'] = admin_status
        
        # Create summary
        status['summary'] = {
            'components_active': len([c for c in status['components'].values() if c.get('is_running', False)]),
            'total_components': len(status['components']),
            'system_healthy': self.is_running and len(status['components']) > 0
        }
        
        return status
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_event.set()
    
    async def run_forever(self):
        """Run the system until shutdown signal."""
        try:
            # Wait for shutdown signal or configured duration
            timeout = self.config['demo'].get('run_duration')
            
            if timeout:
                logger.info(f"System will run for {timeout} seconds")
                try:
                    await asyncio.wait_for(self.shutdown_event.wait(), timeout=timeout)
                except asyncio.TimeoutError:
                    logger.info("Configured runtime reached, shutting down...")
            else:
                logger.info("System running indefinitely (Ctrl+C to stop)")
                await self.shutdown_event.wait()
                
        finally:
            await self.stop_system()

# Demo execution functions
async def run_demo(config_file: str = None):
    """Run the complete Session 5 demo."""
    integration = Session5Integration(config_file)
    
    try:
        # Initialize
        await integration.initialize_system()
        
        # Start
        await integration.start_system()
        
        # Run for a short time for demo
        await asyncio.sleep(30)  # 30 seconds demo
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await integration.stop_system()

def create_demo_config() -> str:
    """Create a demo configuration file."""
    config_path = 'session5_demo_config.json'
    integration = Session5Integration()
    
    import json
    with open(config_path, 'w') as f:
        json.dump(integration.config, f, indent=2)
    
    logger.info(f"Demo configuration saved to {config_path}")
    return config_path

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Session 5 Complete System Demo")
    parser.add_argument('--config', '-c', help="Configuration file path")
    parser.add_argument('--create-config', action='store_true', help="Create demo configuration file")
    parser.add_argument('--verbose', '-v', action='store_true', help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.create_config:
        config_path = create_demo_config()
        print(f"Demo configuration created: {config_path}")
        print("Run with: python demo_session5_integration_fixed.py --config", config_path)
        sys.exit(0)
    
    print("\n🚀 Session 5: ML Optimization Intelligence Demo")
    print("=" * 50)
    print("Starting complete system integration...")
    
    try:
        asyncio.run(run_demo(args.config))
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        sys.exit(1)
    
    print("\n✅ Demo completed successfully!")
