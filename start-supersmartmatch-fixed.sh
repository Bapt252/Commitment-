#!/bin/bash

# Script de démarrage SuperSmartMatch avec fix NumPy
echo "🚀 Démarrage SuperSmartMatch - Version Fixed"
echo "============================================="

# Vérifications
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé. Exécutez ./fix-numpy-compatibility.sh d'abord."
    exit 1
fi

# Activation de l'environnement
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "❌ Impossible d'activer l'environnement virtuel"
    exit 1
fi

# Variables d'environnement pour supprimer les warnings
export PYTHONWARNINGS="ignore"
export TF_CPP_MIN_LOG_LEVEL="2"

# Démarrage
cd super-smart-match
echo "🌐 Service disponible sur: http://localhost:5061"
python app.py
