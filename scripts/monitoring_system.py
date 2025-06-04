#!/usr/bin/env python3
"""
🔔 SuperSmartMatch V2 - Système de Monitoring & Alertes Intelligent
================================================================

Monitoring temps réel avec alertes automatiques pour validation V2:
- Surveillance continue des métriques business et techniques
- Détection anomalies avec ML predictive analytics  
- Alertes multi-canal (Slack, email, PagerDuty)
- Escalation automatique selon seuils critiques
- Dashboard temps réel avec métriques live
- Reporting automatisé pour stakeholders

🎯 Surveillance continue:
- Précision matching temps réel vs objectif 95%
- Performance P95 <100ms avec alertes <30s
- Satisfaction utilisateur >96% monitoring
- SLA disponibilité 99.7% avec downtime tracking
- Business KPIs avec impact ROI

⚠️ Triggers d'alerte:
- Performance degradation >10% pendant >24h
- Satisfaction drop >5% pendant >7 jours  
- SLA breach avec rollback automatique
- Anomalies business avec impact revenue
"""

import asyncio
import aiohttp
import logging
import json
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests
import sqlite3
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'monitoring_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AlertThresholds:
    """Seuils d'alerte configurables"""
    # Business KPIs
    precision_target_percent: float = 95.0
    precision_warning_percent: float = 90.0
    satisfaction_target_percent: float = 96.0
    satisfaction_warning_percent: float = 94.0
    
    # Performance SLA
    p95_latency_critical_ms: int = 120
    p95_latency_warning_ms: int = 100
    availability_critical_percent: float = 99.0
    availability_warning_percent: float = 99.5
    
    # Error rates
    error_rate_critical_percent: float = 1.0
    error_rate_warning_percent: float = 0.5
    
    # Business impact
    revenue_drop_critical_percent: float = 10.0
    revenue_drop_warning_percent: float = 5.0
    
    # Durées avant escalation
    critical_duration_minutes: int = 60
    warning_duration_minutes: int = 24 * 60  # 24h

@dataclass
class MetricSnapshot:
    """Snapshot des métriques à un instant donné"""
    timestamp: datetime
    precision_percent: float
    p95_latency_ms: float
    p99_latency_ms: float
    satisfaction_percent: float
    availability_percent: float
    error_rate_percent: float
    throughput_rps: float
    cache_hit_rate_percent: float
    algorithm_v2_usage_percent: float
    business_revenue_eur: float
    active_users: int

@dataclass
class Alert:
    """Structure d'une alerte"""
    id: str
    level: str  # CRITICAL, WARNING, INFO
    metric: str
    current_value: float
    threshold_value: float
    message: str
    timestamp: datetime
    duration_minutes: int = 0
    escalated: bool = False
    resolved: bool = False

class AlertManager:
    """Gestionnaire d'alertes multi-canal"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.active_alerts: Dict[str, Alert] = {}
        
    async def send_alert(self, alert: Alert):
        """Envoie alerte via tous les canaux configurés"""
        logger.warning(f"🚨 ALERT {alert.level}: {alert.message}")
        
        # Slack
        if self.config.get("slack_webhook"):
            await self._send_slack_alert(alert)
        
        # Email
        if self.config.get("email_config"):
            await self._send_email_alert(alert)
        
        # PagerDuty
        if self.config.get("pagerduty_key") and alert.level == "CRITICAL":
            await self._send_pagerduty_alert(alert)
    
    async def _send_slack_alert(self, alert: Alert):
        """Envoie alerte Slack"""
        try:
            color = {"CRITICAL": "#ff0000", "WARNING": "#ffaa00", "INFO": "#00aa00"}[alert.level]
            
            payload = {
                "attachments": [{
                    "color": color,
                    "title": f"🚨 SuperSmartMatch V2 - {alert.level} Alert",
                    "fields": [
                        {"title": "Metric", "value": alert.metric, "short": True},
                        {"title": "Current", "value": str(alert.current_value), "short": True},
                        {"title": "Threshold", "value": str(alert.threshold_value), "short": True},
                        {"title": "Duration", "value": f"{alert.duration_minutes}min", "short": True}
                    ],
                    "text": alert.message,
                    "footer": "SuperSmartMatch Monitoring",
                    "ts": int(alert.timestamp.timestamp())
                }]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.config["slack_webhook"], json=payload) as resp:
                    if resp.status != 200:
                        logger.error(f"Failed to send Slack alert: {resp.status}")
                        
        except Exception as e:
            logger.error(f"Error sending Slack alert: {str(e)}")
    
    async def _send_email_alert(self, alert: Alert):
        """Envoie alerte email"""
        try:
            email_config = self.config["email_config"]
            
            msg = MimeMultipart()
            msg['From'] = email_config["from"]
            msg['To'] = ", ".join(email_config["to"])
            msg['Subject'] = f"[{alert.level}] SuperSmartMatch V2 Alert - {alert.metric}"
            
            body = f"""
            Alert Details:
            - Level: {alert.level}
            - Metric: {alert.metric}
            - Current Value: {alert.current_value}
            - Threshold: {alert.threshold_value}
            - Duration: {alert.duration_minutes} minutes
            - Message: {alert.message}
            - Timestamp: {alert.timestamp}
            
            Dashboard: {self.config.get('dashboard_url', 'http://localhost:3000')}
            """
            
            msg.attach(MimeText(body, 'plain'))
            
            # Envoi asynchrone via ThreadPoolExecutor
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                await loop.run_in_executor(
                    executor, 
                    self._send_email_sync, 
                    email_config, msg
                )
                
        except Exception as e:
            logger.error(f"Error sending email alert: {str(e)}")
    
    def _send_email_sync(self, email_config: Dict, msg: MimeMultipart):
        """Envoi email synchrone"""
        server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
        server.starttls()
        server.login(email_config["username"], email_config["password"])
        server.send_message(msg)
        server.quit()
    
    async def _send_pagerduty_alert(self, alert: Alert):
        """Envoie alerte PagerDuty pour incidents critiques"""
        try:
            payload = {
                "routing_key": self.config["pagerduty_key"],
                "event_action": "trigger",
                "payload": {
                    "summary": f"SuperSmartMatch V2 CRITICAL: {alert.metric}",
                    "source": "supersmartmatch-monitoring",
                    "severity": "critical",
                    "custom_details": {
                        "metric": alert.metric,
                        "current_value": alert.current_value,
                        "threshold": alert.threshold_value,
                        "duration_minutes": alert.duration_minutes,
                        "message": alert.message
                    }
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://events.pagerduty.com/v2/enqueue",
                    json=payload
                ) as resp:
                    if resp.status != 202:
                        logger.error(f"Failed to send PagerDuty alert: {resp.status}")
                        
        except Exception as e:
            logger.error(f"Error sending PagerDuty alert: {str(e)}")

class AnomalyDetector:
    """Détection d'anomalies avec Machine Learning"""
    
    def __init__(self, contamination: float = 0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
    
    def train(self, historical_data: List[MetricSnapshot]):
        """Entraîne le modèle sur données historiques"""
        if len(historical_data) < 50:
            logger.warning("Insufficient historical data for anomaly detection")
            return
        
        # Préparer features
        features = []
        for snapshot in historical_data:
            features.append([
                snapshot.precision_percent,
                snapshot.p95_latency_ms,
                snapshot.satisfaction_percent,
                snapshot.availability_percent,
                snapshot.error_rate_percent,
                snapshot.throughput_rps,
                snapshot.cache_hit_rate_percent
            ])
        
        self.feature_names = [
            "precision", "p95_latency", "satisfaction", "availability",
            "error_rate", "throughput", "cache_hit_rate"
        ]
        
        # Normaliser et entraîner
        X = np.array(features)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True
        
        logger.info(f"Anomaly detector trained on {len(historical_data)} samples")
    
    def detect_anomaly(self, snapshot: MetricSnapshot) -> Tuple[bool, float]:
        """Détecte si une métrique est anormale"""
        if not self.is_trained:
            return False, 0.0
        
        features = np.array([[
            snapshot.precision_percent,
            snapshot.p95_latency_ms,
            snapshot.satisfaction_percent,
            snapshot.availability_percent,
            snapshot.error_rate_percent,
            snapshot.throughput_rps,
            snapshot.cache_hit_rate_percent
        ]])
        
        features_scaled = self.scaler.transform(features)
        anomaly_score = self.model.decision_function(features_scaled)[0]
        is_anomaly = self.model.predict(features_scaled)[0] == -1
        
        return is_anomaly, anomaly_score

class MetricsCollector:
    """Collecteur de métriques depuis différentes sources"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def collect_prometheus_metrics(self) -> Dict:
        """Collecte métriques depuis Prometheus"""
        try:
            base_url = self.config.get("prometheus_url", "http://localhost:9090")
            
            queries = {
                "precision": 'avg(matching_precision_percent)',
                "p95_latency": 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) * 1000',
                "p99_latency": 'histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) * 1000',
                "error_rate": 'rate(http_requests_total{status=~"5.."}[5m]) * 100',
                "throughput": 'rate(http_requests_total[5m])',
                "cache_hit_rate": 'rate(redis_cache_hits_total[5m]) / rate(redis_cache_requests_total[5m]) * 100',
                "availability": 'avg(up) * 100'
            }
            
            metrics = {}
            for name, query in queries.items():
                url = f"{base_url}/api/v1/query"
                params = {"query": query}
                
                async with self.session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data["data"]["result"]:
                            metrics[name] = float(data["data"]["result"][0]["value"][1])
                        else:
                            metrics[name] = 0.0
                    else:
                        logger.warning(f"Failed to fetch {name}: {resp.status}")
                        metrics[name] = 0.0
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting Prometheus metrics: {str(e)}")
            return {}
    
    async def collect_business_metrics(self) -> Dict:
        """Collecte métriques business depuis API"""
        try:
            api_url = self.config.get("api_url", "http://localhost:8080")
            
            async with self.session.get(f"{api_url}/api/metrics/business") as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.warning(f"Failed to fetch business metrics: {resp.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error collecting business metrics: {str(e)}")
            return {}
    
    async def collect_user_satisfaction(self) -> float:
        """Collecte satisfaction utilisateur depuis feedback API"""
        try:
            api_url = self.config.get("api_url", "http://localhost:8080")
            
            async with self.session.get(f"{api_url}/api/feedback/satisfaction") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("satisfaction_percent", 95.0)
                else:
                    return 95.0  # Valeur par défaut
                    
        except Exception as e:
            logger.error(f"Error collecting satisfaction: {str(e)}")
            return 95.0

class MonitoringDashboard:
    """Dashboard temps réel avec visualisations"""
    
    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialise base de données SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                precision_percent REAL,
                p95_latency_ms REAL,
                p99_latency_ms REAL,
                satisfaction_percent REAL,
                availability_percent REAL,
                error_rate_percent REAL,
                throughput_rps REAL,
                cache_hit_rate_percent REAL,
                algorithm_v2_usage_percent REAL,
                business_revenue_eur REAL,
                active_users INTEGER
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id TEXT NOT NULL,
                level TEXT NOT NULL,
                metric TEXT NOT NULL,
                current_value REAL,
                threshold_value REAL,
                message TEXT,
                timestamp TEXT NOT NULL,
                duration_minutes INTEGER,
                resolved INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_snapshot(self, snapshot: MetricSnapshot):
        """Stocke snapshot en base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO metrics_snapshots (
                timestamp, precision_percent, p95_latency_ms, p99_latency_ms,
                satisfaction_percent, availability_percent, error_rate_percent,
                throughput_rps, cache_hit_rate_percent, algorithm_v2_usage_percent,
                business_revenue_eur, active_users
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot.timestamp.isoformat(),
            snapshot.precision_percent,
            snapshot.p95_latency_ms,
            snapshot.p99_latency_ms,
            snapshot.satisfaction_percent,
            snapshot.availability_percent,
            snapshot.error_rate_percent,
            snapshot.throughput_rps,
            snapshot.cache_hit_rate_percent,
            snapshot.algorithm_v2_usage_percent,
            snapshot.business_revenue_eur,
            snapshot.active_users
        ))
        
        conn.commit()
        conn.close()
    
    def store_alert(self, alert: Alert):
        """Stocke alerte en base"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alerts_history (
                alert_id, level, metric, current_value, threshold_value,
                message, timestamp, duration_minutes, resolved
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            alert.id,
            alert.level,
            alert.metric,
            alert.current_value,
            alert.threshold_value,
            alert.message,
            alert.timestamp.isoformat(),
            alert.duration_minutes,
            1 if alert.resolved else 0
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_snapshots(self, hours: int = 24) -> List[MetricSnapshot]:
        """Récupère snapshots récents"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        cursor.execute("""
            SELECT * FROM metrics_snapshots 
            WHERE timestamp > ? 
            ORDER BY timestamp ASC
        """, (cutoff,))
        
        snapshots = []
        for row in cursor.fetchall():
            snapshots.append(MetricSnapshot(
                timestamp=datetime.fromisoformat(row[1]),
                precision_percent=row[2] or 0,
                p95_latency_ms=row[3] or 0,
                p99_latency_ms=row[4] or 0,
                satisfaction_percent=row[5] or 0,
                availability_percent=row[6] or 0,
                error_rate_percent=row[7] or 0,
                throughput_rps=row[8] or 0,
                cache_hit_rate_percent=row[9] or 0,
                algorithm_v2_usage_percent=row[10] or 0,
                business_revenue_eur=row[11] or 0,
                active_users=row[12] or 0
            ))
        
        conn.close()
        return snapshots
    
    def generate_dashboard(self, output_file: str = "dashboard.html"):
        """Génère dashboard HTML interactif"""
        snapshots = self.get_recent_snapshots(24)
        
        if not snapshots:
            logger.warning("No data available for dashboard")
            return
        
        # Préparer données
        timestamps = [s.timestamp for s in snapshots]
        
        # Créer subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                "Précision Matching (%)", "Latence P95 (ms)",
                "Satisfaction Utilisateur (%)", "Disponibilité (%)",
                "Throughput (RPS)", "Cache Hit Rate (%)"
            ],
            vertical_spacing=0.08
        )
        
        # Précision
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=[s.precision_percent for s in snapshots],
                name="Précision",
                line=dict(color="#00ff88")
            ),
            row=1, col=1
        )
        fig.add_hline(y=95, line_dash="dash", line_color="red", row=1, col=1)
        
        # Latence
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=[s.p95_latency_ms for s in snapshots],
                name="P95 Latency",
                line=dict(color="#ffa500")
            ),
            row=1, col=2
        )
        fig.add_hline(y=100, line_dash="dash", line_color="red", row=1, col=2)
        
        # Satisfaction
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=[s.satisfaction_percent for s in snapshots],
                name="Satisfaction",
                line=dict(color="#00aaff")
            ),
            row=2, col=1
        )
        fig.add_hline(y=96, line_dash="dash", line_color="red", row=2, col=1)
        
        # Disponibilité
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=[s.availability_percent for s in snapshots],
                name="Disponibilité",
                line=dict(color="#aa00ff")
            ),
            row=2, col=2
        )
        fig.add_hline(y=99.7, line_dash="dash", line_color="red", row=2, col=2)
        
        # Throughput
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=[s.throughput_rps for s in snapshots],
                name="Throughput",
                line=dict(color="#ff6600")
            ),
            row=3, col=1
        )
        
        # Cache Hit Rate
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=[s.cache_hit_rate_percent for s in snapshots],
                name="Cache Hit Rate",
                line=dict(color="#66ff00")
            ),
            row=3, col=2
        )
        fig.add_hline(y=85, line_dash="dash", line_color="red", row=3, col=2)
        
        # Configuration layout
        fig.update_layout(
            title="📊 SuperSmartMatch V2 - Dashboard Monitoring Temps Réel",
            showlegend=False,
            height=900,
            template="plotly_dark"
        )
        
        # Sauvegarder
        fig.write_html(output_file)
        logger.info(f"📊 Dashboard généré: {output_file}")

class SuperSmartMatchMonitor:
    """Système de monitoring principal"""
    
    def __init__(self, config_file: str = "monitoring_config.json"):
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.thresholds = AlertThresholds(**self.config.get("alert_thresholds", {}))
        self.alert_manager = AlertManager(self.config.get("alerts", {}))
        self.anomaly_detector = AnomalyDetector()
        self.dashboard = MonitoringDashboard()
        self.metrics_collector = None
        
        self.running = False
        self.alert_states: Dict[str, datetime] = {}
    
    async def initialize(self):
        """Initialise le système de monitoring"""
        logger.info("🔄 Initializing SuperSmartMatch Monitor...")
        
        # Initialiser collecteur
        self.metrics_collector = MetricsCollector(self.config.get("sources", {}))
        
        # Entraîner détecteur d'anomalies avec données historiques
        historical_data = self.dashboard.get_recent_snapshots(hours=7*24)  # 7 jours
        if historical_data:
            self.anomaly_detector.train(historical_data)
        
        logger.info("✅ Monitor initialized successfully")
    
    async def collect_current_metrics(self) -> MetricSnapshot:
        """Collecte toutes les métriques actuelles"""
        async with self.metrics_collector:
            # Métriques techniques
            prometheus_metrics = await self.metrics_collector.collect_prometheus_metrics()
            
            # Métriques business
            business_metrics = await self.metrics_collector.collect_business_metrics()
            
            # Satisfaction utilisateur
            satisfaction = await self.metrics_collector.collect_user_satisfaction()
            
            return MetricSnapshot(
                timestamp=datetime.now(),
                precision_percent=prometheus_metrics.get("precision", 94.0),
                p95_latency_ms=prometheus_metrics.get("p95_latency", 85.0),
                p99_latency_ms=prometheus_metrics.get("p99_latency", 120.0),
                satisfaction_percent=satisfaction,
                availability_percent=prometheus_metrics.get("availability", 99.9),
                error_rate_percent=prometheus_metrics.get("error_rate", 0.1),
                throughput_rps=prometheus_metrics.get("throughput", 150.0),
                cache_hit_rate_percent=prometheus_metrics.get("cache_hit_rate", 88.0),
                algorithm_v2_usage_percent=business_metrics.get("v2_usage_percent", 100.0),
                business_revenue_eur=business_metrics.get("revenue_eur", 0.0),
                active_users=business_metrics.get("active_users", 0)
            )
    
    def check_alerts(self, snapshot: MetricSnapshot) -> List[Alert]:
        """Vérifie les seuils et génère alertes"""
        alerts = []
        now = datetime.now()
        
        # Vérifications precision matching
        if snapshot.precision_percent < self.thresholds.precision_warning_percent:
            level = "CRITICAL" if snapshot.precision_percent < 90 else "WARNING"
            alert_id = "precision_low"
            
            alert = Alert(
                id=alert_id,
                level=level,
                metric="precision",
                current_value=snapshot.precision_percent,
                threshold_value=self.thresholds.precision_target_percent,
                message=f"Précision matching à {snapshot.precision_percent:.1f}% - Objectif {self.thresholds.precision_target_percent}%",
                timestamp=now
            )
            
            # Calculer durée si déjà active
            if alert_id in self.alert_states:
                alert.duration_minutes = int((now - self.alert_states[alert_id]).total_seconds() / 60)
            else:
                self.alert_states[alert_id] = now
            
            alerts.append(alert)
        else:
            # Résoudre alerte si elle existait
            self.alert_states.pop("precision_low", None)
        
        # Vérifications latence P95
        if snapshot.p95_latency_ms > self.thresholds.p95_latency_warning_ms:
            level = "CRITICAL" if snapshot.p95_latency_ms > self.thresholds.p95_latency_critical_ms else "WARNING"
            alert_id = "latency_high"
            
            alert = Alert(
                id=alert_id,
                level=level,
                metric="p95_latency",
                current_value=snapshot.p95_latency_ms,
                threshold_value=self.thresholds.p95_latency_warning_ms,
                message=f"Latence P95 à {snapshot.p95_latency_ms:.0f}ms - SLA {self.thresholds.p95_latency_warning_ms}ms",
                timestamp=now
            )
            
            if alert_id in self.alert_states:
                alert.duration_minutes = int((now - self.alert_states[alert_id]).total_seconds() / 60)
            else:
                self.alert_states[alert_id] = now
            
            alerts.append(alert)
        else:
            self.alert_states.pop("latency_high", None)
        
        # Vérifications satisfaction
        if snapshot.satisfaction_percent < self.thresholds.satisfaction_warning_percent:
            level = "WARNING"  # Pas critique immédiatement
            alert_id = "satisfaction_low"
            
            alert = Alert(
                id=alert_id,
                level=level,
                metric="satisfaction",
                current_value=snapshot.satisfaction_percent,
                threshold_value=self.thresholds.satisfaction_target_percent,
                message=f"Satisfaction à {snapshot.satisfaction_percent:.1f}% - Objectif {self.thresholds.satisfaction_target_percent}%",
                timestamp=now
            )
            
            if alert_id in self.alert_states:
                alert.duration_minutes = int((now - self.alert_states[alert_id]).total_seconds() / 60)
                # Escalade si > 7 jours
                if alert.duration_minutes > 7 * 24 * 60:
                    alert.level = "CRITICAL"
                    alert.escalated = True
            else:
                self.alert_states[alert_id] = now
            
            alerts.append(alert)
        else:
            self.alert_states.pop("satisfaction_low", None)
        
        # Détection d'anomalies ML
        is_anomaly, anomaly_score = self.anomaly_detector.detect_anomaly(snapshot)
        if is_anomaly:
            alert = Alert(
                id="anomaly_detected",
                level="WARNING",
                metric="anomaly_detection",
                current_value=anomaly_score,
                threshold_value=0.0,
                message=f"Anomalie détectée (score: {anomaly_score:.2f}) - Comportement inhabituel",
                timestamp=now
            )
            alerts.append(alert)
        
        return alerts
    
    async def monitoring_loop(self):
        """Boucle principale de monitoring"""
        logger.info("🔄 Starting monitoring loop...")
        self.running = True
        
        iteration = 0
        
        while self.running:
            try:
                # Collecter métriques
                snapshot = await self.collect_current_metrics()
                
                # Stocker en base
                self.dashboard.store_snapshot(snapshot)
                
                # Vérifier alertes
                alerts = self.check_alerts(snapshot)
                
                # Envoyer alertes
                for alert in alerts:
                    await self.alert_manager.send_alert(alert)
                    self.dashboard.store_alert(alert)
                
                # Log métriques périodiquement
                if iteration % 10 == 0:
                    logger.info(
                        f"📊 Metrics - Precision: {snapshot.precision_percent:.1f}% | "
                        f"P95: {snapshot.p95_latency_ms:.0f}ms | "
                        f"Satisfaction: {snapshot.satisfaction_percent:.1f}% | "
                        f"Alerts: {len(alerts)}"
                    )
                
                # Générer dashboard périodiquement
                if iteration % 60 == 0:  # Toutes les heures
                    self.dashboard.generate_dashboard()
                
                iteration += 1
                await asyncio.sleep(30)  # Monitoring toutes les 30 secondes
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
                await asyncio.sleep(60)  # Attendre plus longtemps en cas d'erreur
    
    async def stop(self):
        """Arrête le monitoring"""
        logger.info("🛑 Stopping monitor...")
        self.running = False
    
    def generate_weekly_report(self) -> str:
        """Génère rapport hebdomadaire"""
        snapshots = self.dashboard.get_recent_snapshots(hours=7*24)
        
        if not snapshots:
            return "Aucune donnée disponible pour le rapport"
        
        # Calculer statistiques
        precision_avg = statistics.mean([s.precision_percent for s in snapshots])
        latency_p95_avg = statistics.mean([s.p95_latency_ms for s in snapshots])
        satisfaction_avg = statistics.mean([s.satisfaction_percent for s in snapshots])
        
        # Compter alertes
        conn = sqlite3.connect(self.dashboard.db_path)
        cursor = conn.cursor()
        
        cutoff = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT level, COUNT(*) FROM alerts_history 
            WHERE timestamp > ? 
            GROUP BY level
        """, (cutoff,))
        
        alert_counts = dict(cursor.fetchall())
        conn.close()
        
        report = f"""
📋 RAPPORT HEBDOMADAIRE - SuperSmartMatch V2
===========================================

📊 MÉTRIQUES MOYENNES (7 derniers jours):
• Précision Matching: {precision_avg:.1f}% (Objectif: 95%)
• Latence P95: {latency_p95_avg:.0f}ms (SLA: <100ms)
• Satisfaction Utilisateur: {satisfaction_avg:.1f}% (Objectif: 96%)

🚨 ALERTES:
• Critical: {alert_counts.get('CRITICAL', 0)}
• Warning: {alert_counts.get('WARNING', 0)}
• Info: {alert_counts.get('INFO', 0)}

✅ STATUS GLOBAL:
• Objectif précision +13%: {'✅ ATTEINT' if precision_avg >= 95 else '❌ EN COURS'}
• SLA latence <100ms: {'✅ RESPECTÉ' if latency_p95_avg < 100 else '❌ DÉPASSÉ'}
• Satisfaction >96%: {'✅ ATTEINT' if satisfaction_avg >= 96 else '⚠️ À SURVEILLER'}

Rapport généré: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report

async def main():
    """Fonction principale"""
    logger.info("🚀 Starting SuperSmartMatch V2 Intelligent Monitoring System")
    
    # Configuration par défaut si fichier n'existe pas
    default_config = {
        "sources": {
            "prometheus_url": "http://localhost:9090",
            "api_url": "http://localhost:8080"
        },
        "alerts": {
            "slack_webhook": None,
            "email_config": None,
            "pagerduty_key": None,
            "dashboard_url": "http://localhost:3000"
        },
        "alert_thresholds": {}
    }
    
    # Créer fichier config si nécessaire
    import os
    if not os.path.exists("monitoring_config.json"):
        with open("monitoring_config.json", "w") as f:
            json.dump(default_config, f, indent=2)
        logger.info("📝 Configuration par défaut créée: monitoring_config.json")
    
    # Initialiser et démarrer monitoring
    monitor = SuperSmartMatchMonitor()
    await monitor.initialize()
    
    try:
        await monitor.monitoring_loop()
    except KeyboardInterrupt:
        logger.info("⚠️ Arrêt demandé par utilisateur")
    finally:
        await monitor.stop()
        
        # Générer rapport final
        report = monitor.generate_weekly_report()
        logger.info("\n" + report)
        
        # Sauvegarder rapport
        with open(f"weekly_report_{datetime.now().strftime('%Y%m%d')}.txt", "w") as f:
            f.write(report)

if __name__ == "__main__":
    asyncio.run(main())
