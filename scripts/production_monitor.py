#!/usr/bin/env python3
"""
SuperSmartMatch V2 - Production Monitoring Dashboard
====================================================
Dashboard temps réel avec métriques avancées et alerting intelligent
Author: SuperSmartMatch Team
Version: 1.0
"""

import asyncio
import json
import time
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import aiohttp
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram

# Configuration
MONITORING_CONFIG = {
    'refresh_interval': 5,  # seconds
    'metrics_retention': 24,  # hours
    'alert_thresholds': {
        'precision_min': 94.0,
        'latency_p95_max': 200,
        'error_rate_max': 2.0,
        'uptime_min': 99.0,
        'roi_min': 175000
    },
    'services': {
        'supersmartmatch_v2': 'http://localhost:5070',
        'supersmartmatch_v1': 'http://localhost:5062',
        'nexten': 'http://localhost:5052',
        'api': 'http://localhost:5050'
    }
}

@dataclass
class MetricsSnapshot:
    """Snapshot des métriques à un instant T"""
    timestamp: datetime
    precision: float
    latency_p95: float
    latency_avg: float
    error_rate: float
    throughput: float
    cpu_usage: float
    memory_usage: float
    uptime: float
    roi_current: float
    active_users: int
    queue_depth: int
    cache_hit_rate: float
    prompt5_compliance: float

class ProductionMonitor:
    """Monitoring production avancé pour SuperSmartMatch V2"""
    
    def __init__(self):
        self.metrics_history: List[MetricsSnapshot] = []
        self.alerts_active: Dict[str, bool] = {}
        self.registry = CollectorRegistry()
        self.setup_prometheus_metrics()
        
    def setup_prometheus_metrics(self):
        """Configuration des métriques Prometheus"""
        self.precision_gauge = Gauge(
            'supersmartmatch_precision_percent',
            'Précision du matching SuperSmartMatch',
            registry=self.registry
        )
        
        self.latency_histogram = Histogram(
            'supersmartmatch_latency_seconds',
            'Latence des requêtes SuperSmartMatch',
            buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0],
            registry=self.registry
        )
        
        self.error_counter = Counter(
            'supersmartmatch_errors_total',
            'Nombre total d\'erreurs SuperSmartMatch',
            registry=self.registry
        )
        
        self.roi_gauge = Gauge(
            'supersmartmatch_roi_euros',
            'ROI SuperSmartMatch en euros',
            registry=self.registry
        )

    async def collect_metrics(self) -> MetricsSnapshot:
        """Collecte les métriques en temps réel"""
        try:
            async with aiohttp.ClientSession() as session:
                # Métriques de performance
                perf_data = await self._fetch_performance_metrics(session)
                
                # Métriques business
                business_data = await self._fetch_business_metrics(session)
                
                # Métriques système
                system_data = await self._fetch_system_metrics(session)
                
                # Métriques PROMPT 5
                prompt5_data = await self._fetch_prompt5_metrics(session)
                
                snapshot = MetricsSnapshot(
                    timestamp=datetime.now(),
                    precision=perf_data.get('precision', 0.0),
                    latency_p95=perf_data.get('latency_p95', 0.0),
                    latency_avg=perf_data.get('latency_avg', 0.0),
                    error_rate=perf_data.get('error_rate', 0.0),
                    throughput=perf_data.get('throughput', 0.0),
                    cpu_usage=system_data.get('cpu_usage', 0.0),
                    memory_usage=system_data.get('memory_usage', 0.0),
                    uptime=system_data.get('uptime', 0.0),
                    roi_current=business_data.get('roi_current', 0.0),
                    active_users=business_data.get('active_users', 0),
                    queue_depth=system_data.get('queue_depth', 0),
                    cache_hit_rate=system_data.get('cache_hit_rate', 0.0),
                    prompt5_compliance=prompt5_data.get('compliance_score', 0.0)
                )
                
                # Mise à jour des métriques Prometheus
                self._update_prometheus_metrics(snapshot)
                
                return snapshot
                
        except Exception as e:
            logging.error(f"Erreur lors de la collecte des métriques: {e}")
            return self._get_default_snapshot()

    async def _fetch_performance_metrics(self, session: aiohttp.ClientSession) -> Dict:
        """Récupère les métriques de performance"""
        try:
            async with session.get(f"{MONITORING_CONFIG['services']['supersmartmatch_v2']}/metrics/performance") as resp:
                return await resp.json()
        except:
            return {}

    async def _fetch_business_metrics(self, session: aiohttp.ClientSession) -> Dict:
        """Récupère les métriques business"""
        try:
            async with session.get(f"{MONITORING_CONFIG['services']['api']}/metrics/business") as resp:
                return await resp.json()
        except:
            return {}

    async def _fetch_system_metrics(self, session: aiohttp.ClientSession) -> Dict:
        """Récupère les métriques système"""
        try:
            async with session.get(f"{MONITORING_CONFIG['services']['api']}/metrics/system") as resp:
                return await resp.json()
        except:
            return {}

    async def _fetch_prompt5_metrics(self, session: aiohttp.ClientSession) -> Dict:
        """Récupère les métriques PROMPT 5"""
        try:
            async with session.get(f"{MONITORING_CONFIG['services']['supersmartmatch_v2']}/metrics/prompt5") as resp:
                return await resp.json()
        except:
            return {}

    def _update_prometheus_metrics(self, snapshot: MetricsSnapshot):
        """Met à jour les métriques Prometheus"""
        self.precision_gauge.set(snapshot.precision)
        self.latency_histogram.observe(snapshot.latency_avg / 1000)  # Convert to seconds
        self.roi_gauge.set(snapshot.roi_current)

    def _get_default_snapshot(self) -> MetricsSnapshot:
        """Retourne un snapshot par défaut en cas d'erreur"""
        return MetricsSnapshot(
            timestamp=datetime.now(),
            precision=0.0, latency_p95=0.0, latency_avg=0.0,
            error_rate=0.0, throughput=0.0, cpu_usage=0.0,
            memory_usage=0.0, uptime=0.0, roi_current=0.0,
            active_users=0, queue_depth=0, cache_hit_rate=0.0,
            prompt5_compliance=0.0
        )

    def add_metrics_to_history(self, snapshot: MetricsSnapshot):
        """Ajoute les métriques à l'historique"""
        self.metrics_history.append(snapshot)
        
        # Garder seulement les dernières 24h
        cutoff_time = datetime.now() - timedelta(hours=MONITORING_CONFIG['metrics_retention'])
        self.metrics_history = [
            m for m in self.metrics_history 
            if m.timestamp > cutoff_time
        ]

    def check_alerts(self, snapshot: MetricsSnapshot) -> List[Dict]:
        """Vérifie les conditions d'alerte"""
        alerts = []
        thresholds = MONITORING_CONFIG['alert_thresholds']
        
        # Alerte précision
        if snapshot.precision < thresholds['precision_min']:
            alerts.append({
                'severity': 'CRITICAL',
                'metric': 'precision',
                'value': snapshot.precision,
                'threshold': thresholds['precision_min'],
                'message': f"Précision critique: {snapshot.precision:.2f}% < {thresholds['precision_min']}%"
            })
        
        # Alerte latence
        if snapshot.latency_p95 > thresholds['latency_p95_max']:
            alerts.append({
                'severity': 'WARNING',
                'metric': 'latency_p95',
                'value': snapshot.latency_p95,
                'threshold': thresholds['latency_p95_max'],
                'message': f"Latence élevée: {snapshot.latency_p95:.0f}ms > {thresholds['latency_p95_max']}ms"
            })
        
        # Alerte taux d'erreur
        if snapshot.error_rate > thresholds['error_rate_max']:
            alerts.append({
                'severity': 'CRITICAL',
                'metric': 'error_rate',
                'value': snapshot.error_rate,
                'threshold': thresholds['error_rate_max'],
                'message': f"Taux d'erreur critique: {snapshot.error_rate:.2f}% > {thresholds['error_rate_max']}%"
            })
        
        # Alerte ROI
        if snapshot.roi_current < thresholds['roi_min']:
            alerts.append({
                'severity': 'WARNING',
                'metric': 'roi',
                'value': snapshot.roi_current,
                'threshold': thresholds['roi_min'],
                'message': f"ROI en baisse: €{snapshot.roi_current:,.0f} < €{thresholds['roi_min']:,.0f}"
            })
        
        return alerts

    def get_deployment_status(self) -> Dict:
        """Retourne le statut du déploiement"""
        if not self.metrics_history:
            return {'status': 'UNKNOWN', 'health': 'UNKNOWN'}
        
        latest = self.metrics_history[-1]
        alerts = self.check_alerts(latest)
        
        # Déterminer le statut global
        if any(alert['severity'] == 'CRITICAL' for alert in alerts):
            status = 'CRITICAL'
            health = 'UNHEALTHY'
        elif any(alert['severity'] == 'WARNING' for alert in alerts):
            status = 'WARNING' 
            health = 'DEGRADED'
        else:
            status = 'HEALTHY'
            health = 'HEALTHY'
        
        return {
            'status': status,
            'health': health,
            'precision': latest.precision,
            'latency_p95': latest.latency_p95,
            'error_rate': latest.error_rate,
            'uptime': latest.uptime,
            'roi_current': latest.roi_current,
            'prompt5_compliance': latest.prompt5_compliance,
            'active_alerts': len(alerts),
            'last_update': latest.timestamp.isoformat()
        }

def create_dashboard():
    """Crée le dashboard Streamlit"""
    st.set_page_config(
        page_title="SuperSmartMatch V2 - Production Monitor",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🚀 SuperSmartMatch V2 - Production Monitor")
    st.markdown("**Dashboard Temps Réel** | Version 1.0 | PROMPT 5 Compliant ✅")
    
    # Initialize monitor
    if 'monitor' not in st.session_state:
        st.session_state.monitor = ProductionMonitor()
    
    monitor = st.session_state.monitor
    
    # Auto-refresh
    placeholder = st.empty()
    
    while True:
        with placeholder.container():
            # Collect metrics
            snapshot = asyncio.run(monitor.collect_metrics())
            monitor.add_metrics_to_history(snapshot)
            
            # Status overview
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    "🎯 Précision",
                    f"{snapshot.precision:.2f}%",
                    delta=f"+0.09%" if snapshot.precision > 95 else f"{snapshot.precision - 95:.2f}%"
                )
            
            with col2:
                st.metric(
                    "⚡ Latence P95",
                    f"{snapshot.latency_p95:.0f}ms",
                    delta=f"-{200 - snapshot.latency_p95:.0f}ms" if snapshot.latency_p95 < 200 else f"+{snapshot.latency_p95 - 200:.0f}ms"
                )
            
            with col3:
                st.metric(
                    "🚨 Taux d'erreur",
                    f"{snapshot.error_rate:.2f}%",
                    delta=f"-{2.0 - snapshot.error_rate:.2f}%" if snapshot.error_rate < 2.0 else f"+{snapshot.error_rate - 2.0:.2f}%"
                )
            
            with col4:
                st.metric(
                    "💰 ROI Actuel",
                    f"€{snapshot.roi_current:,.0f}",
                    delta=f"+€{snapshot.roi_current - 175000:,.0f}" if snapshot.roi_current > 175000 else f"-€{175000 - snapshot.roi_current:,.0f}"
                )
            
            with col5:
                st.metric(
                    "🏆 PROMPT 5",
                    f"{snapshot.prompt5_compliance:.0f}%",
                    delta="100%" if snapshot.prompt5_compliance == 100 else f"{snapshot.prompt5_compliance - 100:.0f}%"
                )
            
            # Alerts
            alerts = monitor.check_alerts(snapshot)
            if alerts:
                st.error(f"🚨 **{len(alerts)} Alerte(s) Active(s)**")
                for alert in alerts:
                    if alert['severity'] == 'CRITICAL':
                        st.error(f"🔴 {alert['message']}")
                    else:
                        st.warning(f"🟡 {alert['message']}")
            else:
                st.success("✅ **Système en bonne santé - Aucune alerte**")
            
            # Charts
            if len(monitor.metrics_history) > 1:
                # Performance charts
                st.subheader("📊 Métriques de Performance")
                
                df = pd.DataFrame([asdict(m) for m in monitor.metrics_history[-100:]])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                
                # Precision and Latency
                fig = make_subplots(
                    rows=2, cols=2,
                    subplot_titles=('Précision (%)', 'Latence P95 (ms)', 'Taux d\'erreur (%)', 'ROI (€)'),
                    vertical_spacing=0.1
                )
                
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['precision'], name='Précision'),
                    row=1, col=1
                )
                fig.add_hline(y=95, line_dash="dash", line_color="red", row=1, col=1)
                
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['latency_p95'], name='Latence P95'),
                    row=1, col=2
                )
                fig.add_hline(y=200, line_dash="dash", line_color="red", row=1, col=2)
                
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['error_rate'], name='Taux d\'erreur'),
                    row=2, col=1
                )
                fig.add_hline(y=2.0, line_dash="dash", line_color="red", row=2, col=1)
                
                fig.add_trace(
                    go.Scatter(x=df['timestamp'], y=df['roi_current'], name='ROI'),
                    row=2, col=2
                )
                fig.add_hline(y=175000, line_dash="dash", line_color="red", row=2, col=2)
                
                fig.update_layout(height=600, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # System metrics
                st.subheader("🖥️ Métriques Système")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_cpu = go.Figure()
                    fig_cpu.add_trace(go.Scatter(x=df['timestamp'], y=df['cpu_usage'], name='CPU'))
                    fig_cpu.update_layout(title="CPU Usage (%)", yaxis_range=[0, 100])
                    st.plotly_chart(fig_cpu, use_container_width=True)
                
                with col2:
                    fig_mem = go.Figure()
                    fig_mem.add_trace(go.Scatter(x=df['timestamp'], y=df['memory_usage'], name='Memory'))
                    fig_mem.update_layout(title="Memory Usage (%)", yaxis_range=[0, 100])
                    st.plotly_chart(fig_mem, use_container_width=True)
            
            # Deployment status
            st.subheader("📈 Statut du Déploiement")
            deployment_status = monitor.get_deployment_status()
            
            status_color = {
                'HEALTHY': 'green',
                'WARNING': 'orange', 
                'CRITICAL': 'red',
                'UNKNOWN': 'gray'
            }
            
            st.markdown(f"""
            **Status Global**: :{status_color[deployment_status['status']]}[{deployment_status['status']}]  
            **Santé**: {deployment_status['health']}  
            **Dernière MàJ**: {deployment_status['last_update']}  
            **Alertes Actives**: {deployment_status['active_alerts']}
            """)
        
        # Wait before next refresh
        time.sleep(MONITORING_CONFIG['refresh_interval'])

if __name__ == "__main__":
    create_dashboard()
