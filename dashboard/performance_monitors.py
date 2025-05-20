from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import asyncio
import logging

logger = logging.getLogger(__name__)

class AlertCondition:
    def __init__(self, metric_name: str, threshold: float, operator: str, lookback_days: int = 7):
        self.metric_name = metric_name
        self.threshold = threshold
        self.operator = operator  # 'lt', 'gt', 'eq', 'lte', 'gte'
        self.lookback_days = lookback_days
        
    def check(self, current_value: float) -> bool:
        """Vérifie si la condition est remplie"""
        if self.operator == 'lt':
            return current_value < self.threshold
        elif self.operator == 'gt':
            return current_value > self.threshold
        elif self.operator == 'eq':
            return current_value == self.threshold
        elif self.operator == 'lte':
            return current_value <= self.threshold
        elif self.operator == 'gte':
            return current_value >= self.threshold
        return False

class Alert:
    def __init__(self, name: str, description: str, condition: AlertCondition, severity: str = "info"):
        self.name = name
        self.description = description
        self.condition = condition
        self.severity = severity  # 'info', 'warning', 'critical'
        self.triggered = False
        self.last_triggered = None
        self.last_value = None
        
    def trigger(self, current_value: float):
        """Déclenche l'alerte"""
        self.triggered = True
        self.last_triggered = datetime.utcnow()
        self.last_value = current_value
        
    def resolve(self):
        """Résout l'alerte"""
        self.triggered = False

class PerformanceMonitor:
    def __init__(self, metrics_calculator, alerts: List[Alert] = None, check_interval_minutes: int = 60):
        self.metrics_calculator = metrics_calculator
        self.alerts = alerts or []
        self.check_interval_minutes = check_interval_minutes
        self.alert_handlers = []
        self.active_alerts = {}
        
    def register_alert_handler(self, handler: Callable[[Alert, float], None]):
        """Enregistre un handler pour les alertes"""
        self.alert_handlers.append(handler)
        
    def add_alert(self, alert: Alert):
        """Ajoute une alerte au moniteur"""
        self.alerts.append(alert)
        
    async def check_alerts(self):
        """Vérifie toutes les alertes configurées"""
        for alert in self.alerts:
            try:
                # Récupérer la valeur actuelle de la métrique
                current_value = await self._get_metric_value(alert.condition.metric_name, alert.condition.lookback_days)
                
                # Vérifier si la condition est remplie
                condition_met = alert.condition.check(current_value)
                
                # Gérer l'état de l'alerte
                alert_key = alert.name
                
                if condition_met and alert_key not in self.active_alerts:
                    # Nouvelle alerte déclenchée
                    alert.trigger(current_value)
                    self.active_alerts[alert_key] = alert
                    self._notify_alert_handlers(alert, current_value)
                    logger.warning(f"Alert triggered: {alert.name} - {alert.description} (value: {current_value})")
                    
                elif not condition_met and alert_key in self.active_alerts:
                    # Alerte résolue
                    alert.resolve()
                    del self.active_alerts[alert_key]
                    logger.info(f"Alert resolved: {alert.name} (value: {current_value})")
                    
            except Exception as e:
                logger.error(f"Error checking alert {alert.name}: {str(e)}")
                
    def _notify_alert_handlers(self, alert: Alert, current_value: float):
        """Notifie tous les handlers d'alerte enregistrés"""
        for handler in self.alert_handlers:
            try:
                handler(alert, current_value)
            except Exception as e:
                logger.error(f"Error in alert handler: {str(e)}")
                
    async def _get_metric_value(self, metric_name: str, lookback_days: int) -> float:
        """Récupère la valeur actuelle d'une métrique"""
        # Implémenter la logique pour récupérer la métrique spécifique
        if metric_name == "acceptance_rate":
            metrics = await self.metrics_calculator.calculate_acceptance_rate(lookback_days)
            return metrics["acceptance_rate"]
        elif metric_name == "avg_rating":
            metrics = await self.metrics_calculator.calculate_satisfaction_metrics(lookback_days)
            return metrics["avg_rating"] or 0
        elif metric_name == "completion_rate":
            metrics = await self.metrics_calculator.calculate_engagement_metrics(lookback_days)
            return metrics["completion_rate"]
        elif metric_name == "overall_efficiency":
            metrics = await self.metrics_calculator.calculate_matching_efficiency(lookback_days)
            return metrics["overall_efficiency"]
        else:
            logger.warning(f"Unknown metric: {metric_name}")
            return 0
            
    async def monitoring_worker(self):
        """Worker qui exécute le monitoring périodiquement"""
        while True:
            try:
                await self.check_alerts()
            except Exception as e:
                logger.error(f"Error in monitoring worker: {str(e)}")
                
            # Attendre jusqu'à la prochaine vérification
            await asyncio.sleep(self.check_interval_minutes * 60)
            
    def create_default_alerts(self):
        """Crée des alertes par défaut pour les métriques clés"""
        self.add_alert(Alert(
            name="low_acceptance_rate",
            description="Le taux d'acceptation est tombé en dessous de 20%",
            condition=AlertCondition("acceptance_rate", 0.2, "lt", 3),
            severity="warning"
        ))
        
        self.add_alert(Alert(
            name="low_satisfaction",
            description="La satisfaction moyenne est tombée en dessous de 3/5",
            condition=AlertCondition("avg_rating", 3.0, "lt", 7),
            severity="warning"
        ))
        
        self.add_alert(Alert(
            name="critical_efficiency",
            description="L'efficacité globale est tombée en dessous de 30%",
            condition=AlertCondition("overall_efficiency", 0.3, "lt", 7),
            severity="critical"
        ))
        
        self.add_alert(Alert(
            name="high_abandonment",
            description="Le taux d'abandon des engagements dépasse 50%",
            condition=AlertCondition("completion_rate", 0.5, "lt", 14),
            severity="critical"
        ))
        
        logger.info(f"Created {len(self.alerts)} default alerts")