"""
SuperSmartMatch V2 - Configuration Manager

Dynamic configuration management system with environment-specific settings,
feature flags, and runtime configuration updates for production deployment.
"""

import logging
import json
import os
import yaml
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class AlgorithmConfig:
    """Configuration for individual algorithms"""
    enabled: bool = True
    weight: float = 1.0
    timeout_ms: int = 80
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300
    max_parallel_requests: int = 10
    fallback_enabled: bool = True
    custom_parameters: Optional[Dict[str, Any]] = None

@dataclass
class SelectionConfig:
    """Configuration for algorithm selection logic"""
    # Nexten selection thresholds
    min_skills_for_nexten: int = 5
    min_questionnaire_completeness: float = 0.7
    min_company_questionnaire_completeness: float = 0.5
    
    # Enhanced selection criteria
    senior_experience_threshold: int = 7
    partial_questionnaire_threshold: float = 0.3
    
    # Geographic selection criteria
    max_distance_km: int = 50
    mobility_complexity_threshold: int = 3
    
    # Semantic analysis triggers
    semantic_skill_description_length: int = 100
    semantic_complexity_threshold: float = 0.8
    
    # Hybrid validation triggers
    critical_positions: List[str] = None
    high_value_clients: List[str] = None
    
    def __post_init__(self):
        if self.critical_positions is None:
            self.critical_positions = ['CEO', 'CTO', 'Senior Manager']
        if self.high_value_clients is None:
            self.high_value_clients = []

@dataclass
class PerformanceConfig:
    """Performance and monitoring configuration"""
    max_response_time_ms: int = 100
    cache_enabled: bool = True
    cache_size: int = 1000
    cache_ttl_seconds: int = 300
    
    # Monitoring settings
    enable_detailed_logging: bool = True
    metrics_retention_hours: int = 24
    enable_ab_testing: bool = True
    
    # Alert thresholds
    error_rate_warning: float = 0.02
    error_rate_critical: float = 0.05
    response_time_warning_ms: int = 120
    response_time_critical_ms: int = 150
    success_rate_threshold: float = 0.95

@dataclass
class NextenConfig:
    """Nexten Matcher specific configuration"""
    enabled: bool = True
    timeout_ms: int = 80
    cache_enabled: bool = True
    parallel_processing: bool = True
    max_workers: int = 4
    
    # ML Model settings
    model_version: str = "latest"
    confidence_threshold: float = 0.7
    enable_questionnaire_weighting: bool = True
    
    # Performance optimization
    enable_skill_caching: bool = True
    enable_embedding_cache: bool = True
    batch_processing_size: int = 10
    
    # Fallback settings
    fallback_to_enhanced: bool = True
    emergency_timeout_ms: int = 50

@dataclass
class FeatureFlags:
    """Feature flags for gradual rollout"""
    enable_v2: bool = False
    v2_traffic_percentage: int = 0
    enable_nexten_algorithm: bool = True
    enable_smart_selection: bool = True
    enable_questionnaire_matching: bool = True
    enable_performance_monitoring: bool = True
    enable_ab_testing: bool = False
    enable_fallback_chaining: bool = True
    enable_cache_warming: bool = False

@dataclass
class SuperSmartMatchV2Config:
    """Complete SuperSmartMatch V2 configuration"""
    # Core settings
    version: str = "2.0.0"
    environment: str = "development"
    debug: bool = False
    
    # Component configurations
    algorithms: Dict[str, AlgorithmConfig] = None
    selection: SelectionConfig = None
    performance: PerformanceConfig = None
    nexten: NextenConfig = None
    feature_flags: FeatureFlags = None
    
    # External service settings
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    monitoring_endpoint: Optional[str] = None
    
    # Security settings
    api_key_required: bool = False
    rate_limit_requests_per_minute: int = 1000
    max_request_size_mb: int = 10
    
    def __post_init__(self):
        if self.algorithms is None:
            self.algorithms = {
                'nexten': AlgorithmConfig(enabled=True, weight=1.3, timeout_ms=80),
                'smart': AlgorithmConfig(enabled=True, weight=1.0, timeout_ms=70),
                'enhanced': AlgorithmConfig(enabled=True, weight=1.1, timeout_ms=60),
                'semantic': AlgorithmConfig(enabled=True, weight=0.9, timeout_ms=90),
                'hybrid': AlgorithmConfig(enabled=True, weight=1.2, timeout_ms=100)
            }
        if self.selection is None:
            self.selection = SelectionConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.nexten is None:
            self.nexten = NextenConfig()
        if self.feature_flags is None:
            self.feature_flags = FeatureFlags()

class ConfigManager:
    """
    Comprehensive configuration management for SuperSmartMatch V2
    
    Features:
    - Environment-specific configuration loading
    - Runtime configuration updates
    - Configuration validation
    - Feature flag management
    - Hot-reload capabilities
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self._config = SuperSmartMatchV2Config()
        self._config_cache = {}
        self._environment = os.getenv('ENVIRONMENT', 'development')
        
        # Load configuration
        self._load_configuration()
        
        logger.info(f"ConfigManager initialized for environment: {self._environment}")
    
    def _load_configuration(self) -> None:
        """Load configuration from multiple sources with precedence"""
        
        # 1. Load default configuration
        self._config = SuperSmartMatchV2Config()
        
        # 2. Load from environment-specific file
        env_config_path = self._get_environment_config_path()
        if env_config_path and os.path.exists(env_config_path):
            self._load_from_file(env_config_path)
            logger.info(f"Loaded environment config from: {env_config_path}")
        
        # 3. Load from custom config path if provided
        if self.config_path and os.path.exists(self.config_path):
            self._load_from_file(self.config_path)
            logger.info(f"Loaded custom config from: {self.config_path}")
        
        # 4. Override with environment variables
        self._load_from_environment()
        
        # 5. Validate configuration
        self._validate_configuration()
        
        # 6. Apply environment-specific adjustments
        self._apply_environment_adjustments()
    
    def _get_environment_config_path(self) -> Optional[str]:
        """Get configuration file path for current environment"""
        config_dir = Path(__file__).parent / "config"
        config_file = config_dir / f"config_{self._environment}.yaml"
        
        if config_file.exists():
            return str(config_file)
        
        # Fallback to generic config
        generic_config = config_dir / "config.yaml"
        if generic_config.exists():
            return str(generic_config)
        
        return None
    
    def _load_from_file(self, file_path: str) -> None:
        """Load configuration from YAML or JSON file"""
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    file_config = yaml.safe_load(f)
                else:
                    file_config = json.load(f)
            
            # Merge with existing configuration
            self._merge_config(file_config)
            
        except Exception as e:
            logger.error(f"Failed to load config from {file_path}: {e}")
    
    def _load_from_environment(self) -> None:
        """Load configuration overrides from environment variables"""
        
        # Core settings
        if os.getenv('SUPERSMARTMATCH_DEBUG'):
            self._config.debug = os.getenv('SUPERSMARTMATCH_DEBUG').lower() == 'true'
        
        if os.getenv('SUPERSMARTMATCH_VERSION'):
            self._config.version = os.getenv('SUPERSMARTMATCH_VERSION')
        
        # Feature flags
        if os.getenv('ENABLE_V2'):
            self._config.feature_flags.enable_v2 = os.getenv('ENABLE_V2').lower() == 'true'
        
        if os.getenv('V2_TRAFFIC_PERCENTAGE'):
            self._config.feature_flags.v2_traffic_percentage = int(os.getenv('V2_TRAFFIC_PERCENTAGE'))
        
        if os.getenv('ENABLE_NEXTEN'):
            self._config.feature_flags.enable_nexten_algorithm = os.getenv('ENABLE_NEXTEN').lower() == 'true'
        
        # Performance settings
        if os.getenv('MAX_RESPONSE_TIME_MS'):
            self._config.performance.max_response_time_ms = int(os.getenv('MAX_RESPONSE_TIME_MS'))
        
        if os.getenv('CACHE_ENABLED'):
            self._config.performance.cache_enabled = os.getenv('CACHE_ENABLED').lower() == 'true'
        
        # External services
        if os.getenv('DATABASE_URL'):
            self._config.database_url = os.getenv('DATABASE_URL')
        
        if os.getenv('REDIS_URL'):
            self._config.redis_url = os.getenv('REDIS_URL')
        
        # Nexten specific
        if os.getenv('NEXTEN_TIMEOUT_MS'):
            self._config.nexten.timeout_ms = int(os.getenv('NEXTEN_TIMEOUT_MS'))
        
        if os.getenv('NEXTEN_MAX_WORKERS'):
            self._config.nexten.max_workers = int(os.getenv('NEXTEN_MAX_WORKERS'))
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration with existing configuration"""
        
        def deep_merge(target: Dict, source: Dict) -> Dict:
            for key, value in source.items():
                if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                    deep_merge(target[key], value)
                else:
                    target[key] = value
            return target
        
        # Convert config to dict, merge, and convert back
        config_dict = asdict(self._config)
        merged_dict = deep_merge(config_dict, new_config)
        
        # Reconstruct config object (simplified approach)
        # In a production system, you'd want more sophisticated object reconstruction
        self._apply_dict_to_config(merged_dict)
    
    def _apply_dict_to_config(self, config_dict: Dict[str, Any]) -> None:
        """Apply dictionary values to configuration object"""
        
        # Core settings
        if 'version' in config_dict:
            self._config.version = config_dict['version']
        if 'environment' in config_dict:
            self._config.environment = config_dict['environment']
        if 'debug' in config_dict:
            self._config.debug = config_dict['debug']
        
        # Feature flags
        if 'feature_flags' in config_dict:
            ff = config_dict['feature_flags']
            for key, value in ff.items():
                if hasattr(self._config.feature_flags, key):
                    setattr(self._config.feature_flags, key, value)
        
        # Performance settings
        if 'performance' in config_dict:
            perf = config_dict['performance']
            for key, value in perf.items():
                if hasattr(self._config.performance, key):
                    setattr(self._config.performance, key, value)
        
        # Nexten settings
        if 'nexten' in config_dict:
            nexten = config_dict['nexten']
            for key, value in nexten.items():
                if hasattr(self._config.nexten, key):
                    setattr(self._config.nexten, key, value)
        
        # Algorithm settings
        if 'algorithms' in config_dict:
            for algo_name, algo_config in config_dict['algorithms'].items():
                if algo_name not in self._config.algorithms:
                    self._config.algorithms[algo_name] = AlgorithmConfig()
                
                for key, value in algo_config.items():
                    if hasattr(self._config.algorithms[algo_name], key):
                        setattr(self._config.algorithms[algo_name], key, value)
    
    def _validate_configuration(self) -> None:
        """Validate configuration values"""
        
        errors = []
        
        # Validate performance settings
        if self._config.performance.max_response_time_ms <= 0:
            errors.append("max_response_time_ms must be positive")
        
        if not 0 <= self._config.feature_flags.v2_traffic_percentage <= 100:
            errors.append("v2_traffic_percentage must be between 0 and 100")
        
        # Validate Nexten settings
        if self._config.nexten.timeout_ms <= 0:
            errors.append("nexten timeout_ms must be positive")
        
        if self._config.nexten.max_workers <= 0:
            errors.append("nexten max_workers must be positive")
        
        # Validate selection thresholds
        if not 0 <= self._config.selection.min_questionnaire_completeness <= 1:
            errors.append("min_questionnaire_completeness must be between 0 and 1")
        
        if self._config.selection.min_skills_for_nexten < 0:
            errors.append("min_skills_for_nexten must be non-negative")
        
        if errors:
            error_msg = "Configuration validation errors: " + "; ".join(errors)
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info("Configuration validation passed")
    
    def _apply_environment_adjustments(self) -> None:
        """Apply environment-specific configuration adjustments"""
        
        if self._environment == 'production':
            # Production optimizations
            self._config.debug = False
            self._config.performance.enable_detailed_logging = False
            self._config.nexten.parallel_processing = True
            self._config.performance.cache_enabled = True
            
            # Tighter timeouts for production
            self._config.performance.max_response_time_ms = 80
            self._config.nexten.timeout_ms = 60
            
        elif self._environment == 'development':
            # Development conveniences
            self._config.debug = True
            self._config.performance.enable_detailed_logging = True
            self._config.feature_flags.enable_ab_testing = True
            
        elif self._environment == 'testing':
            # Testing optimizations
            self._config.performance.cache_enabled = False
            self._config.nexten.cache_enabled = False
            self._config.performance.enable_detailed_logging = True
            
            # Faster timeouts for tests
            self._config.performance.max_response_time_ms = 50
            self._config.nexten.timeout_ms = 30
        
        logger.info(f"Applied {self._environment} environment adjustments")
    
    # Public API methods
    
    def get_config(self) -> SuperSmartMatchV2Config:
        """Get the complete configuration object"""
        return self._config
    
    def get_algorithm_config(self, algorithm_name: str) -> Optional[AlgorithmConfig]:
        """Get configuration for specific algorithm"""
        return self._config.algorithms.get(algorithm_name)
    
    def is_algorithm_enabled(self, algorithm_name: str) -> bool:
        """Check if algorithm is enabled"""
        algo_config = self.get_algorithm_config(algorithm_name)
        return algo_config.enabled if algo_config else False
    
    def get_feature_flag(self, flag_name: str) -> Any:
        """Get value of specific feature flag"""
        return getattr(self._config.feature_flags, flag_name, None)
    
    def set_feature_flag(self, flag_name: str, value: Any) -> None:
        """Set feature flag value at runtime"""
        if hasattr(self._config.feature_flags, flag_name):
            setattr(self._config.feature_flags, flag_name, value)
            logger.info(f"Feature flag updated: {flag_name} = {value}")
        else:
            logger.warning(f"Unknown feature flag: {flag_name}")
    
    def update_algorithm_config(self, algorithm_name: str, updates: Dict[str, Any]) -> None:
        """Update algorithm configuration at runtime"""
        if algorithm_name in self._config.algorithms:
            algo_config = self._config.algorithms[algorithm_name]
            for key, value in updates.items():
                if hasattr(algo_config, key):
                    setattr(algo_config, key, value)
                    logger.info(f"Algorithm config updated: {algorithm_name}.{key} = {value}")
        else:
            logger.warning(f"Unknown algorithm: {algorithm_name}")
    
    def reload_configuration(self) -> None:
        """Reload configuration from files and environment"""
        logger.info("Reloading configuration...")
        self._load_configuration()
        logger.info("Configuration reloaded successfully")
    
    def export_config(self, format: str = 'yaml') -> str:
        """Export current configuration in specified format"""
        config_dict = asdict(self._config)
        
        if format == 'yaml':
            return yaml.dump(config_dict, default_flow_style=False, indent=2)
        elif format == 'json':
            return json.dumps(config_dict, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def validate_environment_readiness(self) -> Dict[str, Any]:
        """Validate that environment is ready for SuperSmartMatch V2"""
        
        readiness = {
            'ready': True,
            'checks': {},
            'warnings': [],
            'errors': []
        }
        
        # Check if V2 is enabled
        readiness['checks']['v2_enabled'] = self._config.feature_flags.enable_v2
        if not self._config.feature_flags.enable_v2:
            readiness['warnings'].append("SuperSmartMatch V2 is not enabled")
        
        # Check algorithm availability
        enabled_algorithms = [
            name for name, config in self._config.algorithms.items() 
            if config.enabled
        ]
        readiness['checks']['enabled_algorithms'] = enabled_algorithms
        
        if 'nexten' not in enabled_algorithms:
            readiness['warnings'].append("Nexten algorithm is not enabled")
        
        if len(enabled_algorithms) < 2:
            readiness['errors'].append("At least 2 algorithms should be enabled for fallback")
            readiness['ready'] = False
        
        # Check external dependencies
        if self._config.redis_url:
            readiness['checks']['redis_configured'] = True
        else:
            readiness['warnings'].append("Redis not configured - caching disabled")
        
        # Check performance settings
        if self._config.performance.max_response_time_ms > 150:
            readiness['warnings'].append("Max response time > 150ms may affect user experience")
        
        # Check Nexten configuration
        if self._config.nexten.timeout_ms >= self._config.performance.max_response_time_ms:
            readiness['errors'].append("Nexten timeout should be less than max response time")
            readiness['ready'] = False
        
        return readiness
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get environment information and configuration summary"""
        return {
            'environment': self._environment,
            'version': self._config.version,
            'debug_mode': self._config.debug,
            'feature_flags': asdict(self._config.feature_flags),
            'algorithm_status': {
                name: config.enabled 
                for name, config in self._config.algorithms.items()
            },
            'performance_config': {
                'max_response_time_ms': self._config.performance.max_response_time_ms,
                'cache_enabled': self._config.performance.cache_enabled,
                'monitoring_enabled': self._config.performance.enable_detailed_logging
            },
            'config_sources': {
                'environment_file': self._get_environment_config_path(),
                'custom_file': self.config_path,
                'environment_variables': True
            }
        }
