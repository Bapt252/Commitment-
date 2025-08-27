#!/bin/bash

# 🧹 SCRIPT DE NETTOYAGE REPOSITORY SUPERSMARTMATCH V2
# =======================================================
# Ce script supprime les fichiers et dossiers obsolètes
# tout en préservant l'architecture microservices fonctionnelle

echo "🧹 DÉBUT DU NETTOYAGE REPOSITORY SUPERSMARTMATCH V2"
echo "=================================================="

# PHASE 1: Suppression des caches et temporaires
echo "📁 PHASE 1: Suppression des caches Python..."

# Supprimer __pycache__ (cache Python obsolète)
if [ -d "__pycache__" ]; then
    echo "  ❌ Suppression: __pycache__/ (9 fichiers .pyc obsolètes)"
    rm -rf __pycache__/
fi

# Supprimer backup (1 fichier de test obsolète)
if [ -d "backup" ]; then
    echo "  ❌ Suppression: backup/ (1 fichier test A/B obsolète)"
    rm -rf backup/
fi

# PHASE 2: Suppression des dossiers d'analyse temporaires
echo "📊 PHASE 2: Suppression des analyses temporaires..."

# Supprimer analysis_session8 (session temporaire)
if [ -d "analysis_session8" ]; then
    echo "  ❌ Suppression: analysis_session8/ (session d'analyse temporaire)"
    rm -rf analysis_session8/
fi

# Supprimer airflow_dags (non utilisé dans l'architecture actuelle)
if [ -d "airflow_dags" ]; then
    echo "  ❌ Suppression: airflow_dags/ (DAG Airflow non utilisé)"
    rm -rf airflow_dags/
fi

# PHASE 3: Nettoyage des assets obsolètes
echo "🎨 PHASE 3: Nettoyage des assets..."

# Supprimer assets (ressources obsolètes)
if [ -d "assets" ]; then
    echo "  ❌ Suppression: assets/ (ressources obsolètes)"
    rm -rf assets/
fi

echo ""
echo "✅ NETTOYAGE TERMINÉ"
echo "==================="
echo "🎯 PRÉSERVÉ:"
echo "  ✅ docker-compose.production.yml (7 microservices)"
echo "  ✅ services/ (architecture microservices)"
echo "  ✅ nginx/ (reverse proxy)"
echo "  ✅ monitoring/ (Prometheus/Grafana)"
echo "  ✅ database/ (PostgreSQL)"
echo "  ✅ README.md et documentation"
echo ""
echo "🗑️ SUPPRIMÉ:"
echo "  ❌ __pycache__/ (cache Python obsolète)"
echo "  ❌ backup/ (test A/B obsolète)"
echo "  ❌ analysis_session8/ (session temporaire)"
echo "  ❌ airflow_dags/ (DAG non utilisé)"
echo "  ❌ assets/ (ressources obsolètes)"
echo ""
echo "🏗️ ARCHITECTURE MICROSERVICES PRÉSERVÉE ET FONCTIONNELLE"
