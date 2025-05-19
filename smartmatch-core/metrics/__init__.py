"""
Module de métriques pour l'évaluation et le monitoring du système de matching.

Ce module fournit:
- Métriques métier (satisfaction, conversion, ROI, temps d'embauche)
- Tracking de performance des modèles ML
- Détection de biais algorithmiques
- Monitoring et alertes en temps réel
"""

from .business_metrics import (
    BusinessMetrics,
    BusinessMetricResult,
    ConversionFunnel
)

from .performance_tracker import (
    PerformanceTracker,
    PerformanceMetric,
    PerformanceAlert,
    ModelPerformanceReport,
    AlertLevel
)

from .bias_detector import (
    BiasDetector,
    BiasInstance,
    BiasReport,
    FairnessMetric,
    BiasType,
    BiasStatus
)

__all__ = [
    # Business metrics
    'BusinessMetrics',
    'BusinessMetricResult', 
    'ConversionFunnel',
    
    # Performance tracking
    'PerformanceTracker',
    'PerformanceMetric',
    'PerformanceAlert',
    'ModelPerformanceReport',
    'AlertLevel',
    
    # Bias detection
    'BiasDetector',
    'BiasInstance',
    'BiasReport',
    'FairnessMetric',
    'BiasType',
    'BiasStatus'
]

# Versions des composants
__version__ = "1.0.0"

# Configuration par défaut pour tous les composants
DEFAULT_CONFIG = {
    'metrics_enabled': True,
    'tracking_enabled': True,
    'bias_detection_enabled': True,
    'alert_enabled': True,
    'cache_enabled': True,
    'cache_duration_minutes': 15,
    'retention_days': 30
}


def create_metrics_suite(config=None):
    """
    Crée une suite complète de métriques avec configuration unifiée.
    
    Args:
        config: Configuration partagée
        
    Returns:
        Tuple contenant (BusinessMetrics, PerformanceTracker, BiasDetector)
    """
    config = config or DEFAULT_CONFIG
    
    business_metrics = BusinessMetrics(config=config)
    performance_tracker = PerformanceTracker(config=config)
    bias_detector = BiasDetector(config=config)
    
    return business_metrics, performance_tracker, bias_detector


def get_comprehensive_health_check(business_metrics, performance_tracker, bias_detector):
    """
    Effectue un health check complet du système.
    
    Args:
        business_metrics: Instance BusinessMetrics
        performance_tracker: Instance PerformanceTracker  
        bias_detector: Instance BiasDetector
        
    Returns:
        Rapport de santé complet
    """
    health_report = {
        'timestamp': datetime.now(),
        'overall_status': 'healthy',
        'components': {}
    }
    
    try:
        # Status des métriques métier
        try:
            business_report = business_metrics.get_comprehensive_report()
            health_report['components']['business_metrics'] = {
                'status': 'healthy' if business_report else 'warning',
                'metrics_count': len(business_report),
                'last_update': datetime.now()
            }
        except Exception as e:
            health_report['components']['business_metrics'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Status du performance tracker
        try:
            perf_status = performance_tracker.get_system_health_status()
            health_report['components']['performance_tracker'] = perf_status
        except Exception as e:
            health_report['components']['performance_tracker'] = {
                'status': 'error',
                'error': str(e)
            }
        
        # Status du bias detector (simplifié)
        try:
            bias_trends = bias_detector.monitor_bias_trends()
            health_report['components']['bias_detector'] = {
                'status': 'healthy' if bias_trends['status'] == 'analyzed' else 'warning',
                'trend_status': bias_trends.get('overall_trend', 'unknown'),
                'reports_analyzed': bias_trends.get('reports_analyzed', 0)
            }
        except Exception as e:
            health_report['components']['bias_detector'] = {
                'status': 'error',  
                'error': str(e)
            }
        
        # Déterminer le status global
        component_statuses = [comp.get('status', 'unknown') for comp in health_report['components'].values()]
        
        if 'error' in component_statuses:
            health_report['overall_status'] = 'error'
        elif 'critical' in component_statuses:
            health_report['overall_status'] = 'critical'
        elif 'warning' in component_statuses:
            health_report['overall_status'] = 'warning'
        else:
            health_report['overall_status'] = 'healthy'
        
    except Exception as e:
        health_report['overall_status'] = 'error'
        health_report['error'] = str(e)
    
    return health_report


# Import conditionnel pour éviter les erreurs
try:
    from datetime import datetime
except ImportError:
    import datetime
    datetime = datetime.datetime
