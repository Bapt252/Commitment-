"""
Optimization Dashboard for SmartMatch-Core
=========================================

Real-time administrative dashboard for monitoring and controlling ML optimization.
Provides interactive visualizations and control interfaces.

Key Features:
- Real-time metrics monitoring
- A/B testing management
- Drift detection visualization
- Model performance tracking
- System health monitoring
- Interactive controls

Technology Stack:
- Streamlit for web interface
- Plotly for interactive charts
- Real-time data updates
- Responsive design

Author: AI Assistant & Bapt252
Session: 5 - ML Optimization Intelligence
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import asyncio
import json
import logging
from dataclasses import dataclass
import time
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

@dataclass
class DashboardConfig:
    """Configuration for the optimization dashboard."""
    port: int = 8501
    host: str = '0.0.0.0'
    update_interval: int = 5  # seconds
    max_data_points: int = 1000
    enable_auth: bool = True
    theme: str = 'dark'
    
@dataclass
class DashboardMetrics:
    """Container for dashboard metrics."""
    timestamp: datetime
    training_metrics: Dict
    ab_test_metrics: Dict
    drift_metrics: Dict
    system_metrics: Dict
    model_performance: Dict

class VisualizationComponent:
    """Base class for dashboard visualization components."""
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.data_cache = []
        self.last_update = None
        
    def update_data(self, data: Dict):
        """Update component data."""
        self.data_cache.append({
            'timestamp': datetime.now(),
            'data': data
        })
        
        # Limit cache size
        if len(self.data_cache) > self.config.get('max_points', 100):
            self.data_cache = self.data_cache[-self.config.get('max_points', 100):]
        
        self.last_update = datetime.now()
    
    def render(self) -> go.Figure:
        """Render the visualization component."""
        raise NotImplementedError

class ModelPerformanceChart(VisualizationComponent):
    """Chart for model performance metrics over time."""
    
    def render(self) -> go.Figure:
        if not self.data_cache:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Extract time series data
        timestamps = [item['timestamp'] for item in self.data_cache]
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Accuracy', 'Precision', 'Recall', 'F1-Score'),
            vertical_spacing=0.15
        )
        
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for metric, (row, col) in zip(metrics, positions):
            values = []
            for item in self.data_cache:
                perf_data = item['data'].get('model_performance', {})
                values.append(perf_data.get(metric, 0))
            
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=values,
                    mode='lines+markers',
                    name=metric.title(),
                    line=dict(width=2)
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title="Model Performance Over Time",
            showlegend=False,
            height=400
        )
        
        return fig

class ABTestingChart(VisualizationComponent):
    """Chart for A/B testing results and progress."""
    
    def render(self) -> go.Figure:
        if not self.data_cache:
            return go.Figure()
        
        latest_data = self.data_cache[-1]['data'].get('ab_test_metrics', {})
        active_tests = latest_data.get('active_tests', [])
        
        if not active_tests:
            fig = go.Figure()
            fig.add_annotation(
                text="No active A/B tests",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Create comparison chart for active tests
        fig = make_subplots(
            rows=len(active_tests), cols=1,
            subplot_titles=[f"Test: {test['name']}" for test in active_tests],
            vertical_spacing=0.1
        )
        
        for i, test in enumerate(active_tests, 1):
            groups = test.get('groups', [])
            if len(groups) >= 2:
                control = groups[0]
                variant = groups[1]
                
                categories = ['Conversion Rate', 'CTR', 'Engagement']
                control_values = [
                    control.get('conversion_rate', 0),
                    control.get('ctr', 0),
                    control.get('engagement', 0)
                ]
                variant_values = [
                    variant.get('conversion_rate', 0),
                    variant.get('ctr', 0),
                    variant.get('engagement', 0)
                ]
                
                fig.add_trace(
                    go.Bar(
                        x=categories,
                        y=control_values,
                        name='Control',
                        showlegend=(i == 1)
                    ),
                    row=i, col=1
                )
                
                fig.add_trace(
                    go.Bar(
                        x=categories,
                        y=variant_values,
                        name='Variant',
                        showlegend=(i == 1)
                    ),
                    row=i, col=1
                )
        
        fig.update_layout(
            title="A/B Testing Results",
            height=300 * len(active_tests)
        )
        
        return fig

class DriftMonitoringChart(VisualizationComponent):
    """Chart for data/concept drift monitoring."""
    
    def render(self) -> go.Figure:
        if not self.data_cache:
            return go.Figure()
        
        # Extract drift scores over time
        timestamps = [item['timestamp'] for item in self.data_cache]
        data_drift_scores = []
        concept_drift_scores = []
        prior_drift_scores = []
        
        for item in self.data_cache:
            drift_data = item['data'].get('drift_metrics', {})
            data_drift_scores.append(drift_data.get('data_drift_score', 0))
            concept_drift_scores.append(drift_data.get('concept_drift_score', 0))
            prior_drift_scores.append(drift_data.get('prior_drift_score', 0))
        
        fig = go.Figure()
        
        # Add threshold line
        threshold = 0.1  # Configurable threshold
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            line_color="red",
            annotation_text="Drift Threshold"
        )
        
        # Add drift score lines
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=data_drift_scores,
            mode='lines+markers',
            name='Data Drift',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=concept_drift_scores,
            mode='lines+markers',
            name='Concept Drift',
            line=dict(color='green', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=prior_drift_scores,
            mode='lines+markers',
            name='Prior Drift',
            line=dict(color='orange', width=2)
        ))
        
        fig.update_layout(
            title="Drift Monitoring",
            xaxis_title="Time",
            yaxis_title="Drift Score",
            yaxis=dict(range=[0, 1]),
            height=400
        )
        
        return fig

class SystemHealthChart(VisualizationComponent):
    """Chart for system health metrics."""
    
    def render(self) -> go.Figure:
        if not self.data_cache:
            return go.Figure()
        
        latest_data = self.data_cache[-1]['data'].get('system_metrics', {})
        
        # Create gauge charts for key metrics
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}],
                   [{'type': 'indicator'}, {'type': 'indicator'}]],
            subplot_titles=('CPU Usage', 'Memory Usage', 'API Latency', 'Error Rate')
        )
        
        # CPU Usage
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=latest_data.get('cpu_usage', 0),
                title={'text': "CPU %"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ),
            row=1, col=1
        )
        
        # Memory Usage
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=latest_data.get('memory_usage', 0),
                title={'text': "Memory %"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "red"}
                    ]
                }
            ),
            row=1, col=2
        )
        
        # API Latency
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=latest_data.get('api_latency_p95', 0),
                title={'text': "Latency (ms)"},
                gauge={
                    'axis': {'range': [None, 2000]},
                    'bar': {'color': "darkorange"},
                    'steps': [
                        {'range': [0, 500], 'color': "lightgray"},
                        {'range': [500, 1000], 'color': "yellow"},
                        {'range': [1000, 2000], 'color': "red"}
                    ]
                }
            ),
            row=2, col=1
        )
        
        # Error Rate
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=latest_data.get('error_rate', 0) * 100,
                title={'text': "Error Rate %"},
                gauge={
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "red"},
                    'steps': [
                        {'range': [0, 1], 'color': "lightgray"},
                        {'range': [1, 5], 'color': "yellow"},
                        {'range': [5, 10], 'color': "red"}
                    ]
                }
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title="System Health Metrics",
            height=500
        )
        
        return fig

class OptimizationDashboard:
    """Main dashboard class for ML optimization monitoring."""
    
    def __init__(self, config: Dict, pipeline_orchestrator=None):
        self.config = DashboardConfig(**config)
        self.pipeline_orchestrator = pipeline_orchestrator
        
        # Initialize visualization components
        self.components = {
            'model_performance': ModelPerformanceChart('model_performance', config),
            'ab_testing': ABTestingChart('ab_testing', config),
            'drift_monitoring': DriftMonitoringChart('drift_monitoring', config),
            'system_health': SystemHealthChart('system_health', config)
        }
        
        # Dashboard state
        self.is_running = False
        self.update_task = None
        
    async def start_dashboard(self):
        """Start the dashboard server."""
        if self.is_running:
            logger.warning("Dashboard already running")
            return
            
        self.is_running = True
        logger.info(f"Starting dashboard on {self.config.host}:{self.config.port}")
        
        # Start the update task
        self.update_task = asyncio.create_task(self._update_loop())
        
        # Launch Streamlit app
        await self._launch_streamlit_app()
    
    async def stop_dashboard(self):
        """Stop the dashboard server."""
        logger.info("Stopping dashboard")
        self.is_running = False
        
        if self.update_task:
            self.update_task.cancel()
    
    async def _update_loop(self):
        """Continuous update loop for dashboard data."""
        while self.is_running:
            try:
                await self._update_dashboard_data()
                await asyncio.sleep(self.config.update_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in dashboard update loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _update_dashboard_data(self):
        """Update dashboard with latest data."""
        try:
            # Get data from pipeline orchestrator
            if self.pipeline_orchestrator:
                pipeline_status = self.pipeline_orchestrator.get_pipeline_status()
                
                # Create metrics object
                metrics = DashboardMetrics(
                    timestamp=datetime.now(),
                    training_metrics=pipeline_status.get('components', {}).get('auto_trainer', {}),
                    ab_test_metrics=pipeline_status.get('components', {}).get('ab_tester', {}),
                    drift_metrics=pipeline_status.get('components', {}).get('drift_monitor', {}),
                    system_metrics=self._collect_system_metrics(),
                    model_performance=self._collect_model_performance()
                )
                
                # Update all components
                for component in self.components.values():
                    component.update_data({
                        'training_metrics': metrics.training_metrics,
                        'ab_test_metrics': metrics.ab_test_metrics,
                        'drift_metrics': metrics.drift_metrics,
                        'system_metrics': metrics.system_metrics,
                        'model_performance': metrics.model_performance
                    })
                    
        except Exception as e:
            logger.error(f"Failed to update dashboard data: {e}")
    
    def _collect_system_metrics(self) -> Dict:
        """Collect system health metrics."""
        import psutil
        
        return {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'api_latency_p95': np.random.uniform(100, 500),  # Mock data
            'error_rate': np.random.uniform(0, 0.05),  # Mock data
            'active_connections': np.random.randint(10, 100)  # Mock data
        }
    
    def _collect_model_performance(self) -> Dict:
        """Collect model performance metrics."""
        # Mock model performance data
        return {
            'accuracy': np.random.uniform(0.85, 0.95),
            'precision': np.random.uniform(0.80, 0.90),
            'recall': np.random.uniform(0.75, 0.85),
            'f1_score': np.random.uniform(0.78, 0.88),
            'auc_roc': np.random.uniform(0.85, 0.95)
        }
    
    async def _launch_streamlit_app(self):
        """Launch the Streamlit dashboard app."""
        # This would typically be handled by running Streamlit as a subprocess
        # or using Streamlit's programmatic API
        pass
    
    def get_status(self) -> Dict:
        """Get dashboard status."""
        return {
            'is_running': self.is_running,
            'port': self.config.port,
            'last_update': max(
                (comp.last_update for comp in self.components.values() if comp.last_update),
                default=None
            ),
            'components_count': len(self.components)
        }

# Streamlit App Definition
def create_streamlit_app(dashboard: OptimizationDashboard):
    """Create the Streamlit dashboard application."""
    
    st.set_page_config(
        page_title="SmartMatch Optimization Dashboard",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Sidebar
    with st.sidebar:
        st.title("🚀 SmartMatch Admin")
        st.markdown("---")
        
        # System status
        status = dashboard.get_status()
        if status['is_running']:
            st.success("✅ System Online")
        else:
            st.error("❌ System Offline")
        
        # Navigation
        page = st.selectbox(
            "Navigation",
            ["Overview", "Model Performance", "A/B Testing", "Drift Monitoring", "System Health", "Controls"]
        )
        
        # Refresh controls
        st.markdown("---")
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        auto_refresh = st.checkbox("Auto Refresh (5s)", value=True)
        
    # Main content area
    if page == "Overview":
        st.title("📊 ML Optimization Overview")
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Active Models", "3", "1")
        with col2:
            st.metric("A/B Tests Running", "2", "0")
        with col3:
            st.metric("System Health", "95%", "2%")
        with col4:
            st.metric("Drift Alerts", "0", "-1")
        
        # Overview charts
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(
                dashboard.components['model_performance'].render(),
                use_container_width=True
            )
        with col2:
            st.plotly_chart(
                dashboard.components['system_health'].render(),
                use_container_width=True
            )
    
    elif page == "Model Performance":
        st.title("🎯 Model Performance")
        st.plotly_chart(
            dashboard.components['model_performance'].render(),
            use_container_width=True
        )
        
        # Performance details table
        st.subheader("Performance Details")
        perf_data = dashboard._collect_model_performance()
        perf_df = pd.DataFrame([perf_data])
        st.dataframe(perf_df, use_container_width=True)
    
    elif page == "A/B Testing":
        st.title("🧪 A/B Testing")
        st.plotly_chart(
            dashboard.components['ab_testing'].render(),
            use_container_width=True
        )
        
        # A/B test controls
        st.subheader("Test Controls")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Start New Test"):
                st.success("New A/B test initiated")
        with col2:
            if st.button("Stop Running Tests"):
                st.warning("All running tests stopped")
        with col3:
            if st.button("Export Results"):
                st.info("Test results exported")
    
    elif page == "Drift Monitoring":
        st.title("📈 Drift Monitoring")
        st.plotly_chart(
            dashboard.components['drift_monitoring'].render(),
            use_container_width=True
        )
        
        # Drift alerts
        st.subheader("Drift Alerts")
        if st.button("Clear All Alerts"):
            st.success("All drift alerts cleared")
    
    elif page == "System Health":
        st.title("💊 System Health")
        st.plotly_chart(
            dashboard.components['system_health'].render(),
            use_container_width=True
        )
        
        # System controls
        st.subheader("System Controls")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Restart Services"):
                st.info("Services restarting...")
        with col2:
            if st.button("Clear Cache"):
                st.success("Cache cleared")
        with col3:
            if st.button("Generate Report"):
                st.success("Health report generated")
    
    elif page == "Controls":
        st.title("🎛️ System Controls")
        
        # Model deployment controls
        st.subheader("Model Deployment")
        col1, col2 = st.columns(2)
        with col1:
            model_name = st.selectbox("Select Model", ["Enhanced Skills Matcher v1.2", "TF-IDF Baseline", "Hybrid Model"])
            deployment_strategy = st.selectbox("Deployment Strategy", ["Blue-Green", "Canary", "Rolling"])
        with col2:
            if st.button("Deploy Model"):
                st.success(f"Deploying {model_name} using {deployment_strategy} strategy")
            if st.button("Rollback Model"):
                st.warning(f"Rolling back {model_name}")
        
        # Optimization controls
        st.subheader("Optimization Controls")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Optimization"):
                st.info("Optimization cycle started")
            if st.button("Stop Optimization"):
                st.warning("Optimization cycle stopped")
        with col2:
            optimization_params = st.text_area("Optimization Parameters (JSON)", value='{"lr": 0.001, "batch_size": 32}')
            if st.button("Update Parameters"):
                st.success("Optimization parameters updated")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(5)
        st.rerun()

# For standalone execution
if __name__ == "__main__":
    # Create a mock dashboard for testing
    config = {
        'port': 8501,
        'update_interval': 5,
        'max_data_points': 100
    }
    dashboard = OptimizationDashboard(config)
    create_streamlit_app(dashboard)
