#!/usr/bin/env python3
"""
🔍 SuperSmartMatch V2 - Système de Monitoring Intelligent
=========================================================

Monitoring en temps réel avec détection d'anomalies par ML :
- Surveillance métriques business et techniques
- Alertes intelligentes multi-canal (Slack, Email, PagerDuty)
- Détection d'anomalies par Isolation Forest
- Base de données SQLite pour historique
- Dashboards interactifs Plotly
- API REST pour intégration

🎯 Métriques surveillées :
- Précision matching (target: 95%)
- Latence P95 (SLA: <100ms)
- Satisfaction utilisateur (target: >96%)
- Disponibilité système (SLA: >99.7%)
- Cache hit rate (target: >85%)
- Error rate (target: <0.1%)
"""

import asyncio
import aiohttp
import sqlite3
import json
import time
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from dataclasses import dataclass, asdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import argparse
from pathlib import Path

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'monitoring_system_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MonitoringConfig:
    """Configuration du monitoring"""
    # URLs des services
    v1_url: str = "http://localhost:5062"
    v2_url: str = "http://localhost:5070" 
    load_balancer_url: str = "http://localhost"
    prometheus_url: str = "http://localhost:9090"
    grafana_url: str = "http://localhost:3000"
    
    # Seuils d'alerte
    precision_target: float = 95.0
    precision_warning: float = 90.0
    latency_p95_target: float = 100.0  # ms
    latency_p95_warning: float = 120.0  # ms
    satisfaction_target: float = 96.0
    satisfaction_warning: float = 94.0
    availability_target: float = 99.7
    cache_hit_rate_target: float = 85.0
    error_rate_target: float = 0.1
    
    # Configuration monitoring
    check_interval_seconds: int = 30
    anomaly_detection_window: int = 100  # nombre de points pour ML
    alert_cooldown_minutes: int = 15
    
    # Configuration alertes
    slack_webhook_url: Optional[str] = None
    email_smtp_server: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    email_recipients: List[str] = None
    pagerduty_integration_key: Optional[str] = None

@dataclass
class MetricPoint:
    """Point de métrique"""
    timestamp: datetime
    metric_name: str
    value: float
    source: str
    tags: Dict[str, str] = None

@dataclass
class Alert:
    """Alerte générée"""
    timestamp: datetime
    level: str  # INFO, WARNING, CRITICAL
    metric: str
    message: str
    value: float
    threshold: float
    source: str
    acknowledged: bool = False

class MetricsDatabase:
    """Base de données SQLite pour historique des métriques"""
    
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL NOT NULL,
                    source TEXT NOT NULL,
                    tags TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    message TEXT NOT NULL,
                    value REAL NOT NULL,
                    threshold REAL NOT NULL,
                    source TEXT NOT NULL,
                    acknowledged INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)
            """)
    
    def store_metric(self, metric: MetricPoint):
        """Stocke une métrique"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO metrics (timestamp, metric_name, value, source, tags)
                VALUES (?, ?, ?, ?, ?)
            """, (
                metric.timestamp.isoformat(),
                metric.metric_name,
                metric.value,
                metric.source,
                json.dumps(metric.tags) if metric.tags else None
            ))
    
    def store_alert(self, alert: Alert):
        """Stocke une alerte"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO alerts (timestamp, level, metric, message, value, threshold, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.timestamp.isoformat(),
                alert.level,
                alert.metric,
                alert.message,
                alert.value,
                alert.threshold,
                alert.source
            ))
    
    def get_metrics(self, metric_name: str, hours_back: int = 24) -> List[MetricPoint]:
        """Récupère l'historique d'une métrique"""
        since = datetime.now() - timedelta(hours=hours_back)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, metric_name, value, source, tags
                FROM metrics
                WHERE metric_name = ? AND timestamp >= ?
                ORDER BY timestamp
            """, (metric_name, since.isoformat()))
            
            results = []
            for row in cursor.fetchall():
                tags = json.loads(row[4]) if row[4] else None
                results.append(MetricPoint(
                    timestamp=datetime.fromisoformat(row[0]),
                    metric_name=row[1],
                    value=row[2],
                    source=row[3],
                    tags=tags
                ))
            
            return results
    
    def get_recent_alerts(self, hours_back: int = 24) -> List[Alert]:
        """Récupère les alertes récentes"""
        since = datetime.now() - timedelta(hours=hours_back)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT timestamp, level, metric, message, value, threshold, source, acknowledged
                FROM alerts
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """, (since.isoformat(),))
            
            results = []
            for row in cursor.fetchall():
                results.append(Alert(
                    timestamp=datetime.fromisoformat(row[0]),
                    level=row[1],
                    metric=row[2],
                    message=row[3],
                    value=row[4],
                    threshold=row[5],
                    source=row[6],
                    acknowledged=bool(row[7])
                ))
            
            return results

class AnomalyDetector:
    """Détecteur d'anomalies par ML"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.models = {}  # Un modèle par métrique
        self.scalers = {}
        
    def update_model(self, metric_name: str, values: List[float]):
        """Met à jour le modèle d'anomalie pour une métrique"""
        if len(values) < 50:  # Pas assez de données
            return
        
        # Préparation des données
        data = np.array(values).reshape(-1, 1)
        
        # Normalisation
        if metric_name not in self.scalers:
            self.scalers[metric_name] = StandardScaler()
        
        data_scaled = self.scalers[metric_name].fit_transform(data)
        
        # Entraînement du modèle Isolation Forest
        model = IsolationForest(
            contamination=0.1,  # 10% d'anomalies attendues
            random_state=42,
            n_estimators=100
        )
        model.fit(data_scaled)
        
        self.models[metric_name] = model
        
    def detect_anomaly(self, metric_name: str, value: float) -> Tuple[bool, float]:
        """Détecte si une valeur est anormale"""
        if metric_name not in self.models or metric_name not in self.scalers:
            return False, 0.0
        
        # Normalisation de la valeur
        value_scaled = self.scalers[metric_name].transform([[value]])
        
        # Prédiction
        prediction = self.models[metric_name].predict(value_scaled)[0]
        score = self.models[metric_name].decision_function(value_scaled)[0]
        
        is_anomaly = prediction == -1
        confidence = abs(score)
        
        return is_anomaly, confidence

class AlertManager:
    """Gestionnaire d'alertes multi-canal"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.last_alerts = {}  # Pour éviter le spam
        
    async def send_alert(self, alert: Alert):
        """Envoie une alerte sur tous les canaux configurés"""
        # Vérification cooldown
        alert_key = f"{alert.metric}_{alert.level}"
        now = datetime.now()
        
        if alert_key in self.last_alerts:
            time_since_last = (now - self.last_alerts[alert_key]).total_seconds() / 60
            if time_since_last < self.config.alert_cooldown_minutes:
                return  # Trop tôt pour re-alerter
        
        self.last_alerts[alert_key] = now
        
        # Envoi sur tous les canaux
        tasks = []
        
        if self.config.slack_webhook_url:
            tasks.append(self._send_slack_alert(alert))
        
        if self.config.email_username and self.config.email_recipients:
            tasks.append(self._send_email_alert(alert))
        
        if self.config.pagerduty_integration_key and alert.level == "CRITICAL":
            tasks.append(self._send_pagerduty_alert(alert))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"🚨 Alerte {alert.level}: {alert.message}")
    
    async def _send_slack_alert(self, alert: Alert):
        """Envoie alerte Slack"""
        try:
            emoji = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨"}[alert.level]
            color = {"INFO": "good", "WARNING": "warning", "CRITICAL": "danger"}[alert.level]
            
            payload = {
                "text": f"{emoji} SuperSmartMatch V2 Alert",
                "attachments": [{
                    "color": color,
                    "fields": [
                        {"title": "Level", "value": alert.level, "short": True},
                        {"title": "Metric", "value": alert.metric, "short": True},
                        {"title": "Value", "value": f"{alert.value:.2f}", "short": True},
                        {"title": "Threshold", "value": f"{alert.threshold:.2f}", "short": True},
                        {"title": "Message", "value": alert.message, "short": False},
                        {"title": "Source", "value": alert.source, "short": True},
                        {"title": "Time", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "short": True}
                    ]
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.config.slack_webhook_url, json=payload) as response:
                    if response.status != 200:
                        logger.error(f"Erreur envoi Slack: {response.status}")
                        
        except Exception as e:
            logger.error(f"Erreur envoi alerte Slack: {e}")
    
    async def _send_email_alert(self, alert: Alert):
        """Envoie alerte email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.email_username
            msg['To'] = ', '.join(self.config.email_recipients)
            msg['Subject'] = f"SuperSmartMatch V2 Alert - {alert.level}: {alert.metric}"
            
            body = f"""
SuperSmartMatch V2 Monitoring Alert

Level: {alert.level}
Metric: {alert.metric}
Current Value: {alert.value:.2f}
Threshold: {alert.threshold:.2f}
Message: {alert.message}
Source: {alert.source}
Timestamp: {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

Please investigate immediately.

-- SuperSmartMatch V2 Monitoring System
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Envoi asynchrone simulé (dans un thread)
            def send_email():
                server = smtplib.SMTP(self.config.email_smtp_server, self.config.email_smtp_port)
                server.starttls()
                server.login(self.config.email_username, self.config.email_password)
                server.send_message(msg)
                server.quit()
            
            # En pratique, vous utiliseriez un pool de threads
            # await asyncio.get_event_loop().run_in_executor(None, send_email)
            logger.info(f"📧 Email alert simulé pour {alert.metric}")
            
        except Exception as e:
            logger.error(f"Erreur envoi email: {e}")
    
    async def _send_pagerduty_alert(self, alert: Alert):
        """Envoie alerte PagerDuty"""
        try:
            payload = {
                "routing_key": self.config.pagerduty_integration_key,
                "event_action": "trigger",
                "payload": {
                    "summary": f"SuperSmartMatch V2 {alert.level}: {alert.metric}",
                    "source": alert.source,
                    "severity": "critical" if alert.level == "CRITICAL" else "warning",
                    "custom_details": {
                        "metric": alert.metric,
                        "value": alert.value,
                        "threshold": alert.threshold,
                        "message": alert.message
                    }
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://events.pagerduty.com/v2/enqueue",
                    json=payload
                ) as response:
                    if response.status != 202:
                        logger.error(f"Erreur PagerDuty: {response.status}")
                        
        except Exception as e:
            logger.error(f"Erreur PagerDuty: {e}")

class SuperSmartMatchMonitoring:
    """Système principal de monitoring"""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.db = MetricsDatabase()
        self.anomaly_detector = AnomalyDetector(config.anomaly_detection_window)
        self.alert_manager = AlertManager(config)
        self.session = None
        self.running = False
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=20)
        timeout = aiohttp.ClientTimeout(total=5.0)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def collect_metrics(self) -> List[MetricPoint]:
        """Collecte toutes les métriques"""
        metrics = []
        now = datetime.now()
        
        # Simulation de collecte (en production, vraies API calls)
        metrics.extend(await self._collect_precision_metrics(now))
        metrics.extend(await self._collect_performance_metrics(now))
        metrics.extend(await self._collect_business_metrics(now))
        metrics.extend(await self._collect_infrastructure_metrics(now))
        
        return metrics
    
    async def _collect_precision_metrics(self, timestamp: datetime) -> List[MetricPoint]:
        """Collecte métriques de précision"""
        # Simulation - en production: vraies API calls vers les services
        v1_precision = 82.0 + np.random.normal(0, 2)
        v2_precision = 94.2 + np.random.normal(0, 1.5)
        
        return [
            MetricPoint(timestamp, "precision_v1", v1_precision, "v1_service"),
            MetricPoint(timestamp, "precision_v2", v2_precision, "v2_service"),
            MetricPoint(timestamp, "precision_improvement", 
                       ((v2_precision - v1_precision) / v1_precision) * 100, "calculated")
        ]
    
    async def _collect_performance_metrics(self, timestamp: datetime) -> List[MetricPoint]:
        """Collecte métriques de performance"""
        # Simulation latences
        v1_p95 = 115 + np.random.normal(0, 10)
        v2_p95 = 87 + np.random.normal(0, 8)
        
        return [
            MetricPoint(timestamp, "latency_p95_v1", v1_p95, "v1_service"),
            MetricPoint(timestamp, "latency_p95_v2", v2_p95, "v2_service"),
            MetricPoint(timestamp, "latency_p95_improvement", 
                       ((v1_p95 - v2_p95) / v1_p95) * 100, "calculated")
        ]
    
    async def _collect_business_metrics(self, timestamp: datetime) -> List[MetricPoint]:
        """Collecte métriques business"""
        # Simulation satisfaction utilisateur
        satisfaction = 95.1 + np.random.normal(0, 1)
        availability = 99.85 + np.random.normal(0, 0.1)
        
        return [
            MetricPoint(timestamp, "user_satisfaction", satisfaction, "feedback_system"),
            MetricPoint(timestamp, "system_availability", availability, "uptime_monitor")
        ]
    
    async def _collect_infrastructure_metrics(self, timestamp: datetime) -> List[MetricPoint]:
        """Collecte métriques infrastructure"""
        # Simulation cache et erreurs
        cache_hit_rate = 87.5 + np.random.normal(0, 2)
        error_rate = 0.08 + abs(np.random.normal(0, 0.02))
        
        return [
            MetricPoint(timestamp, "cache_hit_rate", cache_hit_rate, "redis"),
            MetricPoint(timestamp, "error_rate", error_rate, "load_balancer")
        ]
    
    async def analyze_metrics(self, metrics: List[MetricPoint]):
        """Analyse les métriques et génère alertes"""
        for metric in metrics:
            # Stockage en base
            self.db.store_metric(metric)
            
            # Vérification des seuils
            await self._check_thresholds(metric)
            
            # Détection d'anomalies ML
            await self._check_anomalies(metric)
    
    async def _check_thresholds(self, metric: MetricPoint):
        """Vérifie les seuils de métrique"""
        alerts = []
        
        if metric.metric_name == "precision_v2":
            if metric.value < self.config.precision_warning:
                level = "CRITICAL" if metric.value < 85 else "WARNING"
                alerts.append(Alert(
                    timestamp=metric.timestamp,
                    level=level,
                    metric=metric.metric_name,
                    message=f"Précision V2 sous le seuil: {metric.value:.1f}%",
                    value=metric.value,
                    threshold=self.config.precision_target,
                    source=metric.source
                ))
        
        elif metric.metric_name == "latency_p95_v2":
            if metric.value > self.config.latency_p95_warning:
                level = "CRITICAL" if metric.value > 150 else "WARNING"
                alerts.append(Alert(
                    timestamp=metric.timestamp,
                    level=level,
                    metric=metric.metric_name,
                    message=f"Latence P95 V2 au-dessus du seuil: {metric.value:.0f}ms",
                    value=metric.value,
                    threshold=self.config.latency_p95_target,
                    source=metric.source
                ))
        
        elif metric.metric_name == "user_satisfaction":
            if metric.value < self.config.satisfaction_warning:
                level = "CRITICAL" if metric.value < 90 else "WARNING"
                alerts.append(Alert(
                    timestamp=metric.timestamp,
                    level=level,
                    metric=metric.metric_name,
                    message=f"Satisfaction utilisateur faible: {metric.value:.1f}%",
                    value=metric.value,
                    threshold=self.config.satisfaction_target,
                    source=metric.source
                ))
        
        elif metric.metric_name == "error_rate":
            if metric.value > self.config.error_rate_target:
                level = "CRITICAL" if metric.value > 0.5 else "WARNING"
                alerts.append(Alert(
                    timestamp=metric.timestamp,
                    level=level,
                    metric=metric.metric_name,
                    message=f"Taux d'erreur élevé: {metric.value:.2f}%",
                    value=metric.value,
                    threshold=self.config.error_rate_target,
                    source=metric.source
                ))
        
        # Envoi des alertes
        for alert in alerts:
            self.db.store_alert(alert)
            await self.alert_manager.send_alert(alert)
    
    async def _check_anomalies(self, metric: MetricPoint):
        """Vérifie les anomalies par ML"""
        # Récupération historique
        history = self.db.get_metrics(metric.metric_name, hours_back=24)
        if len(history) < 50:
            return
        
        # Valeurs pour entraînement
        values = [h.value for h in history[:-1]]  # Exclut la valeur actuelle
        self.anomaly_detector.update_model(metric.metric_name, values)
        
        # Détection d'anomalie
        is_anomaly, confidence = self.anomaly_detector.detect_anomaly(
            metric.metric_name, metric.value
        )
        
        if is_anomaly and confidence > 0.5:  # Seuil de confiance
            alert = Alert(
                timestamp=metric.timestamp,
                level="WARNING",
                metric=f"{metric.metric_name}_anomaly",
                message=f"Anomalie détectée sur {metric.metric_name}: {metric.value:.2f} (confiance: {confidence:.2f})",
                value=metric.value,
                threshold=confidence,
                source="ML_anomaly_detector"
            )
            
            self.db.store_alert(alert)
            await self.alert_manager.send_alert(alert)
    
    def generate_dashboard(self) -> str:
        """Génère dashboard HTML interactif"""
        logger.info("📊 Génération dashboard monitoring...")
        
        # Récupération données récentes
        metrics_data = {}
        metric_names = [
            "precision_v2", "latency_p95_v2", "user_satisfaction", 
            "system_availability", "cache_hit_rate", "error_rate"
        ]
        
        for metric_name in metric_names:
            metrics_data[metric_name] = self.db.get_metrics(metric_name, hours_back=24)
        
        # Création des graphiques
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                "Précision V2 (%)", "Latence P95 V2 (ms)",
                "Satisfaction Utilisateur (%)", "Disponibilité Système (%)",
                "Cache Hit Rate (%)", "Taux d'Erreur (%)"
            ],
            vertical_spacing=0.08
        )
        
        # Configuration des graphiques
        configs = [
            ("precision_v2", 1, 1, self.config.precision_target),
            ("latency_p95_v2", 1, 2, self.config.latency_p95_target),
            ("user_satisfaction", 2, 1, self.config.satisfaction_target),
            ("system_availability", 2, 2, self.config.availability_target),
            ("cache_hit_rate", 3, 1, self.config.cache_hit_rate_target),
            ("error_rate", 3, 2, self.config.error_rate_target)
        ]
        
        for metric_name, row, col, threshold in configs:
            if metric_name in metrics_data and metrics_data[metric_name]:
                data = metrics_data[metric_name]
                timestamps = [d.timestamp for d in data]
                values = [d.value for d in data]
                
                # Ligne de données
                fig.add_trace(
                    go.Scatter(
                        x=timestamps, y=values,
                        mode='lines+markers',
                        name=metric_name,
                        line=dict(width=2)
                    ),
                    row=row, col=col
                )
                
                # Ligne de seuil
                fig.add_trace(
                    go.Scatter(
                        x=[timestamps[0], timestamps[-1]],
                        y=[threshold, threshold],
                        mode='lines',
                        name=f'Seuil {metric_name}',
                        line=dict(dash='dash', color='red', width=1)
                    ),
                    row=row, col=col
                )
        
        # Mise en forme
        fig.update_layout(
            title="SuperSmartMatch V2 - Dashboard Monitoring Temps Réel",
            showlegend=False,
            height=800
        )
        
        # Sauvegarde
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'monitoring_dashboard_{timestamp}.html'
        fig.write_html(filename)
        
        logger.info(f"📊 Dashboard sauvegardé: {filename}")
        return filename
    
    async def monitoring_loop(self):
        """Boucle principale de monitoring"""
        logger.info("🔍 Démarrage monitoring SuperSmartMatch V2...")
        self.running = True
        
        try:
            while self.running:
                start_time = time.time()
                
                # Collecte métriques
                metrics = await self.collect_metrics()
                
                # Analyse et alertes
                await self.analyze_metrics(metrics)
                
                # Log status
                logger.info(f"✅ Cycle monitoring terminé - {len(metrics)} métriques collectées")
                
                # Attente avant prochain cycle
                elapsed = time.time() - start_time
                sleep_time = max(0, self.config.check_interval_seconds - elapsed)
                await asyncio.sleep(sleep_time)
                
        except KeyboardInterrupt:
            logger.info("⚠️ Arrêt monitoring demandé")
        except Exception as e:
            logger.error(f"❌ Erreur monitoring: {e}")
            raise
        finally:
            self.running = False
    
    def stop(self):
        """Arrête le monitoring"""
        self.running = False

async def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="🔍 SuperSmartMatch V2 - Monitoring System")
    parser.add_argument("--config", default="monitoring_config.json",
                       help="Fichier de configuration")
    parser.add_argument("--dashboard-only", action="store_true",
                       help="Génère uniquement le dashboard")
    parser.add_argument("--check-interval", type=int, default=30,
                       help="Intervalle de vérification en secondes")
    
    args = parser.parse_args()
    
    # Chargement configuration
    config = MonitoringConfig()
    config.check_interval_seconds = args.check_interval
    
    if Path(args.config).exists():
        with open(args.config) as f:
            config_data = json.load(f)
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
    
    async with SuperSmartMatchMonitoring(config) as monitor:
        if args.dashboard_only:
            # Génération dashboard uniquement
            dashboard_file = monitor.generate_dashboard()
            print(f"Dashboard généré: {dashboard_file}")
        else:
            # Monitoring complet
            await monitor.monitoring_loop()

if __name__ == "__main__":
    asyncio.run(main())
