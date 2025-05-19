#!/usr/bin/env python3
"""
Dashboard Session 5 - Version Simplifiée
========================================

Dashboard Streamlit simple pour la démonstration de Session 5
avec visualisations interactives et contrôles d'administration.

Features:
- Vue d'ensemble système en temps réel
- Gestion des modèles ML
- Monitoring A/B tests
- Métriques de performance
- Contrôles administrateur

Usage: streamlit run simple_dashboard.py

Author: AI Assistant & Bapt252
Session: 5 - ML Optimization Intelligence
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time

# Configuration de la page
st.set_page_config(
    page_title="Session 5 - ML Optimization Dashboard",
    page_icon="🚀",
    layout="wide"
)

# Titre principal
st.title("🚀 Session 5 - Système d'Optimisation ML")

# Sidebar
with st.sidebar:
    st.header("🎛️ Contrôles")
    auto_refresh = st.checkbox("Auto-refresh (5s)", value=False)
    
    st.markdown("---")
    st.subheader("📊 Statut Système")
    
    # Métriques système mockées
    col1, col2 = st.columns(2)
    with col1:
        st.metric("CPU", "65%", "↑ 5%")
        st.metric("Modèles", "3", "↑ 1")
    with col2:
        st.metric("Mémoire", "45%", "↓ 2%")
        st.metric("Tests A/B", "2", "→ 0")

# Corps principal
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🤖 Modèles", "🧪 A/B Tests", "📊 Monitoring"])

with tab1:
    st.header("Vue d'ensemble du système")
    
    # Métriques principales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Performance", "94.5%", "↑ 2.1%")
    with col2:
        st.metric("Latence", "120ms", "↓ 15ms")
    with col3:
        st.metric("Uptime", "99.9%", "→ 0%")
    with col4:
        st.metric("Erreurs", "0.1%", "↓ 0.05%")
    
    # Graphique de performance
    dates = pd.date_range('2024-05-01', periods=30, freq='D')
    performance = np.random.normal(0.94, 0.02, 30)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=performance,
        mode='lines+markers',
        name='Performance',
        line=dict(color='#1f77b4', width=3)
    ))
    fig.update_layout(
        title="Performance du Système (30 derniers jours)",
        xaxis_title="Date",
        yaxis_title="Performance (%)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("Gestion des Modèles")
    
    # Table des modèles
    models_data = {
        'Nom': ['Enhanced Skills Matcher v1.2', 'TF-IDF Baseline', 'Hybrid Model'],
        'Version': ['1.2.0', '1.0.0', '1.1.0'],
        'Statut': ['🟢 Déployé', '🟡 Staging', '🔵 Training'],
        'Performance': [94.5, 89.2, 92.1],
        'Déployé': ['2024-05-15', '2024-05-10', '-']
    }
    
    df = pd.DataFrame(models_data)
    st.dataframe(df, use_container_width=True)
    
    # Boutons de contrôle
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🚀 Déployer Nouveau Modèle"):
            st.success("Déploiement initié pour Hybrid Model v1.1.0")
    with col2:
        if st.button("↩️ Rollback"):
            st.warning("Rollback vers Enhanced Skills Matcher v1.1")
    with col3:
        if st.button("🔄 Actualiser"):
            st.info("Statut des modèles actualisé")

with tab3:
    st.header("Tests A/B en cours")
    
    # Configuration test A/B
    with st.expander("🎯 Nouveau Test A/B"):
        test_name = st.text_input("Nom du test", "Test Algorithme Matching")
        control_model = st.selectbox("Modèle Contrôle", ['Enhanced Skills Matcher v1.2'])
        variant_model = st.selectbox("Modèle Variant", ['Hybrid Model v1.1'])
        traffic_split = st.slider("Répartition trafic (%)", 10, 50, 20)
        
        if st.button("🚀 Lancer Test"):
            st.success(f"Test A/B '{test_name}' lancé avec {traffic_split}% de trafic")
    
    # Résultats tests existants
    st.subheader("📊 Résultats actuels")
    
    # Mock data pour graphique A/B
    metrics = ['Precision', 'Recall', 'F1-Score']
    control = [0.89, 0.85, 0.87]
    variant = [0.91, 0.88, 0.89]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=metrics, y=control, name='Contrôle', marker_color='lightblue'))
    fig.add_trace(go.Bar(x=metrics, y=variant, name='Variant', marker_color='lightcoral'))
    
    fig.update_layout(
        title="Comparaison Performance: Contrôle vs Variant",
        xaxis_title="Métriques",
        yaxis_title="Score",
        barmode='group',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.header("Monitoring Système")
    
    # Graphiques de monitoring
    col1, col2 = st.columns(2)
    
    with col1:
        # CPU/Memory over time
        hours = list(range(24))
        cpu_usage = np.random.normal(60, 15, 24)
        memory_usage = np.random.normal(50, 10, 24)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hours, y=cpu_usage, name='CPU %', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=hours, y=memory_usage, name='Memory %', line=dict(color='blue')))
        
        fig.update_layout(
            title="Utilisation Ressources (24h)",
            xaxis_title="Heure",
            yaxis_title="Utilisation (%)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Drift detection
        days = list(range(1, 31))
        drift_scores = np.random.exponential(0.05, 30)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=days, 
            y=drift_scores, 
            mode='lines+markers',
            name='Drift Score',
            line=dict(color='green')
        ))
        fig.add_hline(y=0.1, line_dash="dash", line_color="red", annotation_text="Seuil d'alerte")
        
        fig.update_layout(
            title="Détection de Dérive (30 jours)",
            xaxis_title="Jour",
            yaxis_title="Score de Dérive",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

# Section Configuration Système
st.markdown("---")
with st.expander("⚙️ Configuration Système"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pipeline")
        st.text("Training Interval: 30 min")
        st.text("A/B Test Duration: 12h")
        st.text("Drift Check: 5 min")
        
    with col2:
        st.subheader("Admin Interface")
        st.text("Dashboard Port: 8501")
        st.text("API Port: 8080")
        st.text("Auth: Disabled (Demo)")

# Alertes système
if st.button("🔔 Déclencher Alerte Test"):
    st.error("⚠️ Alert Test: Dérive détectée sur le modèle principal (Score: 0.15)")
    st.warning("🔄 Ré-entraînement automatique initié...")

# Auto-refresh
if auto_refresh:
    time.sleep(5)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("🎯 **Session 5: ML Optimization Intelligence** - Système opérationnel")
st.markdown("📊 Dashboard: `streamlit run simple_dashboard.py`")
st.markdown("🔧 Demo: `python demo_session5_integration_fixed.py --create-config`")

# Instructions d'utilisation
with st.sidebar:
    st.markdown("---")
    st.subheader("📝 Instructions")
    st.markdown("""
    **Pour utiliser Session 5:**
    
    1. **Dashboard**: Déjà actif ! 🎉
    
    2. **Demo Python**:
    ```bash
    python demo_session5_integration_fixed.py --create-config
    python demo_session5_integration_fixed.py --config session5_demo_config.json
    ```
    
    3. **API Admin**: http://localhost:8080
    
    4. **Composants Session 5**:
    - ✅ Pipeline orchestration
    - ✅ Admin dashboard
    - ✅ Model controller
    - ✅ Optimization system
    """)
