"""
Surveillant de performances des modèles ML pour le système de matching.

Ce module track les métriques de performance en temps réel, détecte les
dégradations et problèmes de performance, et fournit des alertes.
"""

import logging
import numpy as np
import statistics
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum

from ..core.models import MatchResult

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Niveaux d'alerte pour les métriques de performance."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PerformanceMetric:
    """Métrique de performance."""
    name: str
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None


@dataclass
class PerformanceAlert:
    """Alerte de performance."""
    alert_id: str
    level: AlertLevel
    metric_name: str
    message: str
    value: float
    threshold: float
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class ModelPerformanceReport:
    """Rapport de performance d'un modèle."""
    model_name: str
    period_start: datetime
    period_end: datetime
    total_predictions: int
    accuracy_metrics: Dict[str, float]
    latency_metrics: Dict[str, float]
    resource_metrics: Dict[str, float]
    quality_metrics: Dict[str, float]
    alerts: List[PerformanceAlert]
    trends: Dict[str, str]  # 'improving', 'degrading', 'stable'


class PerformanceTracker:
    """
    Surveillant de performances des modèles ML.
    
    Fonctionnalités:
    - Tracking temps réel des métriques (accuracy, latence, utilisation)
    - Détection automatique de dégradations
    - Alertes configurables avec seuils adaptatifs
    - Historique et tendances de performance
    - Intégration avec monitoring infrastructure
    """
    
    def __init__(self, 
                 config: Optional[Dict[str, Any]] = None,
                 alert_handlers: Optional[List[callable]] = None):
        """
        Initialise le tracker de performance.
        
        Args:
            config: Configuration du tracker
            alert_handlers: Handlers pour les alertes
        """
        self.config = config or self._get_default_config()
        self.alert_handlers = alert_handlers or []
        
        # Storage des métriques (en-mémoire pour démo, DB en production)
        self.metrics_history = defaultdict(lambda: deque(maxlen=10000))
        self.active_alerts = {}
        self.model_states = defaultdict(dict)
        
        # Fenêtres glissantes pour calculs temps réel
        self.sliding_windows = defaultdict(lambda: deque(maxlen=100))
        
        # Seuils adaptatifs
        self.adaptive_thresholds = defaultdict(dict)
        
        # Performance baselines
        self.baselines = {}
        
        logger.info("PerformanceTracker initialized")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut."""
        return {
            'tracking_enabled': True,
            'alert_enabled': True,
            'window_size': 100,  # Taille fenêtre glissante
            'baseline_period_hours': 24,  # Période pour calcul baseline
            'alert_cooldown_minutes': 15,  # Éviter spam d'alertes
            'metrics_retention_hours': 168,  # 1 semaine
            
            # Seuils par défaut
            'thresholds': {
                'accuracy': {'min': 0.8, 'warning': 0.75, 'critical': 0.7},
                'precision': {'min': 0.8, 'warning': 0.75, 'critical': 0.7},
                'recall': {'min': 0.7, 'warning': 0.65, 'critical': 0.6},
                'latency_ms': {'max': 500, 'warning': 1000, 'critical': 2000},
                'throughput_rps': {'min': 10, 'warning': 5, 'critical': 1},
                'memory_usage_mb': {'max': 1024, 'warning': 2048, 'critical': 4096},
                'cpu_usage_percent': {'max': 80, 'warning': 90, 'critical': 95}
            },
            
            # Détection d'anomalies
            'anomaly_detection': {
                'enabled': True,
                'sensitivity': 'medium',  # 'low', 'medium', 'high'
                'methods': ['statistical', 'trending']
            }
        }
    
    def track_prediction_performance(self, 
                                   model_name: str,
                                   predictions: List[MatchResult],
                                   ground_truth: Optional[List[Any]] = None,
                                   execution_time_ms: Optional[float] = None,
                                   resource_usage: Optional[Dict[str, float]] = None) -> None:
        """
        Track la performance d'un batch de prédictions.
        
        Args:
            model_name: Nom du modèle
            predictions: Résultats de prédiction
            ground_truth: Vérité terrain (si disponible)
            execution_time_ms: Temps d'exécution en ms
            resource_usage: Usage des ressources
        """
        try:
            timestamp = datetime.now()
            
            # Métriques de base
            num_predictions = len(predictions)
            
            # Métriques de qualité (si vérité terrain disponible)
            if ground_truth:
                quality_metrics = self._calculate_quality_metrics(
                    predictions, ground_truth
                )
                
                for metric_name, value in quality_metrics.items():
                    self._record_metric(
                        model_name, f"quality_{metric_name}", 
                        value, timestamp
                    )
            
            # Métriques de latence
            if execution_time_ms is not None:
                avg_latency = execution_time_ms / max(num_predictions, 1)
                self._record_metric(
                    model_name, "latency_ms", 
                    avg_latency, timestamp
                )
                
                # Throughput
                throughput = num_predictions / (execution_time_ms / 1000) if execution_time_ms > 0 else 0
                self._record_metric(
                    model_name, "throughput_rps", 
                    throughput, timestamp
                )
            
            # Métriques de ressources
            if resource_usage:
                for resource, value in resource_usage.items():
                    self._record_metric(
                        model_name, f"resource_{resource}", 
                        value, timestamp
                    )
            
            # Métriques de distribution des scores
            if predictions:
                scores = [p.score for p in predictions if hasattr(p, 'score')]
                if scores:
                    score_metrics = self._calculate_score_distribution_metrics(scores)
                    for metric_name, value in score_metrics.items():
                        self._record_metric(
                            model_name, f"score_{metric_name}", 
                            value, timestamp
                        )
            
            # Mise à jour des baselines
            self._update_baselines(model_name)
            
            # Vérification des alertes
            self._check_alerts(model_name)
            
            logger.debug(f"Tracked performance for {model_name}: {num_predictions} predictions")
            
        except Exception as e:
            logger.error(f"Error tracking prediction performance: {e}")
    
    def track_realtime_metric(self, 
                            model_name: str,
                            metric_name: str,
                            value: float,
                            metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Track une métrique en temps réel.
        
        Args:
            model_name: Nom du modèle
            metric_name: Nom de la métrique
            value: Valeur de la métrique
            metadata: Métadonnées additionnelles
        """
        try:
            timestamp = datetime.now()
            
            # Enregistrer la métrique
            self._record_metric(model_name, metric_name, value, timestamp, metadata)
            
            # Vérifications temps réel
            self._check_realtime_alerts(model_name, metric_name, value)
            
            # Détection d'anomalies
            if self.config['anomaly_detection']['enabled']:
                self._detect_anomalies(model_name, metric_name, value)
            
        except Exception as e:
            logger.error(f"Error tracking realtime metric: {e}")
    
    def get_performance_report(self, 
                             model_name: str,
                             period_hours: int = 24) -> ModelPerformanceReport:
        """
        Génère un rapport de performance pour un modèle.
        
        Args:
            model_name: Nom du modèle
            period_hours: Période du rapport en heures
            
        Returns:
            Rapport de performance
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=period_hours)
            
            # Récupérer les métriques de la période
            period_metrics = self._get_metrics_in_period(
                model_name, start_time, end_time
            )
            
            # Calculer métriques agrégées
            accuracy_metrics = self._aggregate_metrics_by_prefix(
                period_metrics, "quality_"
            )
            latency_metrics = self._aggregate_metrics_by_prefix(
                period_metrics, "latency_"
            )
            resource_metrics = self._aggregate_metrics_by_prefix(
                period_metrics, "resource_"
            )
            quality_metrics = self._aggregate_metrics_by_prefix(
                period_metrics, "score_"
            )
            
            # Compter les prédictions
            total_predictions = len(period_metrics.get('predictions', []))
            
            # Récupérer les alertes de la période
            period_alerts = [
                alert for alert in self.active_alerts.values()
                if start_time <= alert.timestamp <= end_time
            ]
            
            # Calculer les tendances
            trends = self._calculate_trends(model_name, period_hours)
            
            return ModelPerformanceReport(
                model_name=model_name,
                period_start=start_time,
                period_end=end_time,
                total_predictions=total_predictions,
                accuracy_metrics=accuracy_metrics,
                latency_metrics=latency_metrics,
                resource_metrics=resource_metrics,
                quality_metrics=quality_metrics,
                alerts=period_alerts,
                trends=trends
            )
            
        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return ModelPerformanceReport(
                model_name=model_name,
                period_start=start_time,
                period_end=end_time,
                total_predictions=0,
                accuracy_metrics={},
                latency_metrics={},
                resource_metrics={},
                quality_metrics={},
                alerts=[],
                trends={}
            )
    
    def get_system_health_status(self) -> Dict[str, Any]:
        """
        Retourne le statut de santé global du système.
        
        Returns:
            Statut de santé avec métriques et alertes
        """
        try:
            health_status = {
                'overall_status': 'healthy',
                'timestamp': datetime.now(),
                'models': {},
                'active_alerts': len(self.active_alerts),
                'critical_alerts': len([
                    a for a in self.active_alerts.values() 
                    if a.level == AlertLevel.CRITICAL
                ]),
                'system_metrics': {}
            }
            
            # Statut par modèle
            for model_name in self.model_states.keys():
                model_metrics = self._get_latest_metrics(model_name)
                model_status = self._evaluate_model_health(model_name, model_metrics)
                health_status['models'][model_name] = model_status
            
            # Statut global basé sur les modèles
            if health_status['critical_alerts'] > 0:
                health_status['overall_status'] = 'critical'
            elif health_status['active_alerts'] > 0:
                health_status['overall_status'] = 'warning'
            elif not health_status['models']:
                health_status['overall_status'] = 'unknown'
            elif any(status['status'] == 'degraded' for status in health_status['models'].values()):
                health_status['overall_status'] = 'degraded'
            
            # Métriques système globales
            health_status['system_metrics'] = self._calculate_system_metrics()
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error getting system health status: {e}")
            return {
                'overall_status': 'error',
                'timestamp': datetime.now(),
                'error': str(e)
            }
    
    def set_dynamic_threshold(self, 
                            model_name: str,
                            metric_name: str,
                            threshold_config: Dict[str, float]) -> None:
        """
        Configure un seuil dynamique pour une métrique.
        
        Args:
            model_name: Nom du modèle
            metric_name: Nom de la métrique
            threshold_config: Configuration du seuil
        """
        try:
            if model_name not in self.adaptive_thresholds:
                self.adaptive_thresholds[model_name] = {}
            
            self.adaptive_thresholds[model_name][metric_name] = threshold_config
            
            logger.info(f"Set dynamic threshold for {model_name}.{metric_name}")
            
        except Exception as e:
            logger.error(f"Error setting dynamic threshold: {e}")
    
    def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """
        Acquitte une alerte.
        
        Args:
            alert_id: ID de l'alerte
            user: Utilisateur qui acquitte
            
        Returns:
            True si succès
        """
        try:
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].acknowledged = True
                logger.info(f"Alert {alert_id} acknowledged by {user}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            return False
    
    def resolve_alert(self, alert_id: str, user: str = "system") -> bool:
        """
        Résout une alerte.
        
        Args:
            alert_id: ID de l'alerte
            user: Utilisateur qui résout
            
        Returns:
            True si succès
        """
        try:
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].resolved = True
                logger.info(f"Alert {alert_id} resolved by {user}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error resolving alert: {e}")
            return False
    
    # Méthodes privées
    
    def _record_metric(self, 
                      model_name: str,
                      metric_name: str,
                      value: float,
                      timestamp: datetime,
                      metadata: Optional[Dict[str, Any]] = None) -> None:
        """Enregistre une métrique."""
        metric = PerformanceMetric(
            name=metric_name,
            value=value,
            timestamp=timestamp,
            metadata=metadata or {}
        )
        
        # Stockage historique
        key = f"{model_name}_{metric_name}"
        self.metrics_history[key].append(metric)
        
        # Fenêtre glissante pour calculs temps réel
        self.sliding_windows[key].append(metric)
        
        # Mise à jour état du modèle
        if model_name not in self.model_states:
            self.model_states[model_name] = {}
        self.model_states[model_name][metric_name] = metric
    
    def _calculate_quality_metrics(self, 
                                  predictions: List[MatchResult],
                                  ground_truth: List[Any]) -> Dict[str, float]:
        """Calcule les métriques de qualité."""
        try:
            if len(predictions) != len(ground_truth):
                logger.warning("Prediction and ground truth lengths don't match")
                return {}
            
            # Convertir en scores binaires pour simplifier
            pred_binary = [1 if p.score > 0.5 else 0 for p in predictions]
            true_binary = [1 if t else 0 for t in ground_truth]
            
            # Calculs de base
            tp = sum(1 for p, t in zip(pred_binary, true_binary) if p == 1 and t == 1)
            tn = sum(1 for p, t in zip(pred_binary, true_binary) if p == 0 and t == 0)
            fp = sum(1 for p, t in zip(pred_binary, true_binary) if p == 1 and t == 0)
            fn = sum(1 for p, t in zip(pred_binary, true_binary) if p == 0 and t == 1)
            
            # Métriques
            accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1
            }
            
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {e}")
            return {}
    
    def _calculate_score_distribution_metrics(self, scores: List[float]) -> Dict[str, float]:
        """Calcule les métriques de distribution des scores."""
        try:
            if not scores:
                return {}
            
            return {
                'mean': statistics.mean(scores),
                'median': statistics.median(scores),
                'std': statistics.stdev(scores) if len(scores) > 1 else 0,
                'min': min(scores),
                'max': max(scores),
                'q25': np.percentile(scores, 25),
                'q75': np.percentile(scores, 75)
            }
            
        except Exception as e:
            logger.error(f"Error calculating score distribution: {e}")
            return {}
    
    def _check_alerts(self, model_name: str) -> None:
        """Vérifie et déclenche les alertes pour un modèle."""
        try:
            latest_metrics = self._get_latest_metrics(model_name)
            
            for metric_name, metric in latest_metrics.items():
                self._check_metric_thresholds(model_name, metric_name, metric.value)
                
        except Exception as e:
            logger.error(f"Error checking alerts: {e}")
    
    def _check_realtime_alerts(self, 
                              model_name: str,
                              metric_name: str,
                              value: float) -> None:
        """Vérifie les alertes en temps réel."""
        self._check_metric_thresholds(model_name, metric_name, value)
    
    def _check_metric_thresholds(self, 
                                model_name: str,
                                metric_name: str,
                                value: float) -> None:
        """Vérifie les seuils d'une métrique."""
        try:
            # Récupérer les seuils (adaptatifs ou par défaut)
            thresholds = self._get_thresholds(model_name, metric_name)
            
            if not thresholds:
                return
            
            alert_level = None
            threshold_value = None
            message = None
            
            # Vérifier les seuils critiques
            if 'critical' in thresholds:
                if 'min' in thresholds['critical'] and value < thresholds['critical']['min']:
                    alert_level = AlertLevel.CRITICAL
                    threshold_value = thresholds['critical']['min']
                    message = f"{metric_name} below critical minimum: {value} < {threshold_value}"
                elif 'max' in thresholds['critical'] and value > thresholds['critical']['max']:
                    alert_level = AlertLevel.CRITICAL
                    threshold_value = thresholds['critical']['max']
                    message = f"{metric_name} above critical maximum: {value} > {threshold_value}"
            
            # Vérifier les seuils warning
            if not alert_level and 'warning' in thresholds:
                if 'min' in thresholds['warning'] and value < thresholds['warning']['min']:
                    alert_level = AlertLevel.WARNING
                    threshold_value = thresholds['warning']['min']
                    message = f"{metric_name} below warning minimum: {value} < {threshold_value}"
                elif 'max' in thresholds['warning'] and value > thresholds['warning']['max']:
                    alert_level = AlertLevel.WARNING
                    threshold_value = thresholds['warning']['max']
                    message = f"{metric_name} above warning maximum: {value} > {threshold_value}"
            
            # Créer l'alerte si nécessaire
            if alert_level:
                self._create_alert(model_name, metric_name, alert_level, message, value, threshold_value)
                
        except Exception as e:
            logger.error(f"Error checking metric thresholds: {e}")
    
    def _create_alert(self, 
                     model_name: str,
                     metric_name: str,
                     level: AlertLevel,
                     message: str,
                     value: float,
                     threshold: float) -> None:
        """Crée une nouvelle alerte."""
        try:
            alert_id = f"{model_name}_{metric_name}_{level.value}_{datetime.now().timestamp()}"
            
            # Vérifier cooldown pour éviter spam
            similar_alerts = [
                a for a in self.active_alerts.values()
                if a.metric_name == metric_name and a.level == level and not a.resolved
            ]
            
            if similar_alerts:
                last_alert_time = max(a.timestamp for a in similar_alerts)
                cooldown = timedelta(minutes=self.config['alert_cooldown_minutes'])
                if datetime.now() - last_alert_time < cooldown:
                    return  # Skip due to cooldown
            
            alert = PerformanceAlert(
                alert_id=alert_id,
                level=level,
                metric_name=metric_name,
                message=message,
                value=value,
                threshold=threshold,
                timestamp=datetime.now()
            )
            
            self.active_alerts[alert_id] = alert
            
            # Notifier les handlers
            for handler in self.alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Error in alert handler: {e}")
            
            logger.warning(f"Created alert: {message}")
            
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
    
    def _detect_anomalies(self, 
                         model_name: str,
                         metric_name: str,
                         value: float) -> None:
        """Détecte les anomalies dans une métrique."""
        try:
            key = f"{model_name}_{metric_name}"
            history = list(self.sliding_windows[key])
            
            if len(history) < 10:  # Pas assez d'historique
                return
            
            # Méthode statistique simple
            values = [m.value for m in history[-50:]]  # 50 dernières valeurs
            mean = statistics.mean(values)
            std = statistics.stdev(values) if len(values) > 1 else 0
            
            if std == 0:
                return
            
            # Z-score
            z_score = abs(value - mean) / std
            
            # Seuils basés sur la sensibilité
            sensitivity = self.config['anomaly_detection']['sensitivity']
            thresholds = {
                'low': 3.0,
                'medium': 2.5,
                'high': 2.0
            }
            
            if z_score > thresholds.get(sensitivity, 2.5):
                message = f"Anomaly detected in {metric_name}: z-score={z_score:.2f}"
                self._create_alert(
                    model_name, metric_name, 
                    AlertLevel.WARNING, message, 
                    value, mean
                )
                
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
    
    def _get_thresholds(self, model_name: str, metric_name: str) -> Dict[str, Any]:
        """Récupère les seuils pour une métrique."""
        # Seuils adaptatifs prioritaires
        if (model_name in self.adaptive_thresholds and 
            metric_name in self.adaptive_thresholds[model_name]):
            return self.adaptive_thresholds[model_name][metric_name]
        
        # Seuils par défaut
        base_metric = metric_name.replace('quality_', '').replace('resource_', '')
        return self.config['thresholds'].get(base_metric, {})
    
    def _get_latest_metrics(self, model_name: str) -> Dict[str, PerformanceMetric]:
        """Récupère les dernières métriques d'un modèle."""
        return self.model_states.get(model_name, {})
    
    def _get_metrics_in_period(self, 
                              model_name: str,
                              start_time: datetime,
                              end_time: datetime) -> Dict[str, List[PerformanceMetric]]:
        """Récupère les métriques dans une période."""
        period_metrics = defaultdict(list)
        
        for key, metrics in self.metrics_history.items():
            if key.startswith(f"{model_name}_"):
                metric_name = key[len(f"{model_name}_"):]
                for metric in metrics:
                    if start_time <= metric.timestamp <= end_time:
                        period_metrics[metric_name].append(metric)
        
        return period_metrics
    
    def _aggregate_metrics_by_prefix(self, 
                                   period_metrics: Dict[str, List[PerformanceMetric]],
                                   prefix: str) -> Dict[str, float]:
        """Agrège les métriques par préfixe."""
        aggregated = {}
        
        for metric_name, metrics in period_metrics.items():
            if metric_name.startswith(prefix):
                if metrics:
                    values = [m.value for m in metrics]
                    clean_name = metric_name[len(prefix):]
                    aggregated[f"{clean_name}_avg"] = statistics.mean(values)
                    aggregated[f"{clean_name}_min"] = min(values)
                    aggregated[f"{clean_name}_max"] = max(values)
                    
                    if len(values) > 1:
                        aggregated[f"{clean_name}_std"] = statistics.stdev(values)
        
        return aggregated
    
    def _calculate_trends(self, model_name: str, period_hours: int) -> Dict[str, str]:
        """Calcule les tendances des métriques."""
        trends = {}
        
        try:
            end_time = datetime.now()
            mid_time = end_time - timedelta(hours=period_hours/2)
            start_time = end_time - timedelta(hours=period_hours)
            
            # Comparer première et seconde moitié de période
            first_half = self._get_metrics_in_period(model_name, start_time, mid_time)
            second_half = self._get_metrics_in_period(model_name, mid_time, end_time)
            
            for metric_name in set(first_half.keys()) & set(second_half.keys()):
                if first_half[metric_name] and second_half[metric_name]:
                    avg_first = statistics.mean([m.value for m in first_half[metric_name]])
                    avg_second = statistics.mean([m.value for m in second_half[metric_name]])
                    
                    change_percent = ((avg_second - avg_first) / avg_first * 100) if avg_first != 0 else 0
                    
                    if abs(change_percent) < 5:
                        trends[metric_name] = 'stable'
                    elif change_percent > 5:
                        trends[metric_name] = 'improving' if 'error' not in metric_name else 'degrading'
                    else:
                        trends[metric_name] = 'degrading' if 'error' not in metric_name else 'improving'
            
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
        
        return trends
    
    def _evaluate_model_health(self, 
                              model_name: str,
                              latest_metrics: Dict[str, PerformanceMetric]) -> Dict[str, Any]:
        """Évalue la santé d'un modèle."""
        try:
            if not latest_metrics:
                return {'status': 'unknown', 'last_update': None}
            
            # Vérifier les métriques critiques
            critical_issues = []
            warning_issues = []
            
            for metric_name, metric in latest_metrics.items():
                thresholds = self._get_thresholds(model_name, metric_name)
                if not thresholds:
                    continue
                
                # Vérifier seuils critiques
                if 'critical' in thresholds:
                    if ('min' in thresholds['critical'] and 
                        metric.value < thresholds['critical']['min']):
                        critical_issues.append(f"{metric_name} too low")
                    elif ('max' in thresholds['critical'] and 
                          metric.value > thresholds['critical']['max']):
                        critical_issues.append(f"{metric_name} too high")
                
                # Vérifier seuils warning
                elif 'warning' in thresholds:
                    if ('min' in thresholds['warning'] and 
                        metric.value < thresholds['warning']['min']):
                        warning_issues.append(f"{metric_name} low")
                    elif ('max' in thresholds['warning'] and 
                          metric.value > thresholds['warning']['max']):
                        warning_issues.append(f"{metric_name} high")
            
            # Déterminer statut
            if critical_issues:
                status = 'critical'
            elif warning_issues:
                status = 'degraded'
            else:
                status = 'healthy'
            
            # Dernière mise à jour
            last_update = max(m.timestamp for m in latest_metrics.values())
            
            return {
                'status': status,
                'last_update': last_update,
                'issues': critical_issues + warning_issues,
                'metrics_count': len(latest_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error evaluating model health: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_system_metrics(self) -> Dict[str, Any]:
        """Calcule les métriques système globales."""
        try:
            return {
                'total_models': len(self.model_states),
                'total_metrics_tracked': sum(len(metrics) for metrics in self.model_states.values()),
                'avg_metrics_per_model': (
                    sum(len(metrics) for metrics in self.model_states.values()) / 
                    len(self.model_states) if self.model_states else 0
                ),
                'tracker_uptime_hours': 24,  # À remplacer par vraie uptime
                'memory_usage_mb': 100  # À remplacer par vraie utilisation
            }
            
        except Exception as e:
            logger.error(f"Error calculating system metrics: {e}")
            return {}
    
    def _update_baselines(self, model_name: str) -> None:
        """Met à jour les baselines de performance."""
        try:
            baseline_period = timedelta(hours=self.config['baseline_period_hours'])
            cutoff_time = datetime.now() - baseline_period
            
            # Pour chaque métrique du modèle
            for key, metrics in self.metrics_history.items():
                if key.startswith(f"{model_name}_"):
                    metric_name = key[len(f"{model_name}_"):]
                    
                    # Filtrer les métriques dans la période baseline
                    baseline_metrics = [
                        m for m in metrics 
                        if m.timestamp >= cutoff_time
                    ]
                    
                    if len(baseline_metrics) > 10:  # Minimum pour baseline fiable
                        values = [m.value for m in baseline_metrics]
                        baseline_key = f"{model_name}_{metric_name}"
                        
                        self.baselines[baseline_key] = {
                            'mean': statistics.mean(values),
                            'std': statistics.stdev(values) if len(values) > 1 else 0,
                            'min': min(values),
                            'max': max(values),
                            'count': len(values),
                            'last_updated': datetime.now()
                        }
                        
        except Exception as e:
            logger.error(f"Error updating baselines: {e}")
    
    def clear_resolved_alerts(self) -> int:
        """Nettoie les alertes résolues anciennes."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            resolved_count = 0
            
            alerts_to_remove = []
            for alert_id, alert in self.active_alerts.items():
                if alert.resolved and alert.timestamp < cutoff_time:
                    alerts_to_remove.append(alert_id)
                    resolved_count += 1
            
            for alert_id in alerts_to_remove:
                del self.active_alerts[alert_id]
            
            logger.info(f"Cleaned {resolved_count} resolved alerts")
            return resolved_count
            
        except Exception as e:
            logger.error(f"Error clearing resolved alerts: {e}")
            return 0
    
    def export_performance_data(self, 
                               model_name: str,
                               format: str = 'json') -> Dict[str, Any]:
        """Exporte les données de performance."""
        try:
            export_data = {
                'model_name': model_name,
                'export_timestamp': datetime.now().isoformat(),
                'metrics': {},
                'alerts': {},
                'baselines': {}
            }
            
            # Export des métriques
            for key, metrics in self.metrics_history.items():
                if key.startswith(f"{model_name}_"):
                    metric_name = key[len(f"{model_name}_"):]
                    export_data['metrics'][metric_name] = [
                        {
                            'value': m.value,
                            'timestamp': m.timestamp.isoformat(),
                            'metadata': m.metadata
                        }
                        for m in metrics
                    ]
            
            # Export des alertes
            export_data['alerts'] = [
                {
                    'alert_id': alert.alert_id,
                    'level': alert.level.value,
                    'metric_name': alert.metric_name,
                    'message': alert.message,
                    'value': alert.value,
                    'threshold': alert.threshold,
                    'timestamp': alert.timestamp.isoformat(),
                    'acknowledged': alert.acknowledged,
                    'resolved': alert.resolved
                }
                for alert in self.active_alerts.values()
            ]
            
            # Export des baselines
            for key, baseline in self.baselines.items():
                if key.startswith(f"{model_name}_"):
                    metric_name = key[len(f"{model_name}_"):]
                    export_data['baselines'][metric_name] = {
                        **baseline,
                        'last_updated': baseline['last_updated'].isoformat()
                    }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Error exporting performance data: {e}")
            return {'error': str(e)}
