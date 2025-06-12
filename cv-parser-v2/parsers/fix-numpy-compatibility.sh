#!/bin/bash

# Script de fix automatique pour résoudre les problèmes de compatibilité NumPy
# 🚀 Fix SuperSmartMatch - Résolution des conflits NumPy/TensorFlow

set -e

echo "🔧 Fix SuperSmartMatch - Résolution des conflits NumPy"
echo "====================================================="

# Variables
PROJECT_DIR="$(pwd)"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON_CMD=""

# Détection de Python
detect_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "❌ Python non trouvé. Installez Python 3.8+"
        exit 1
    fi
    
    echo "✅ Python détecté: $($PYTHON_CMD --version)"
}

# Sauvegarde de l'environnement actuel
backup_current_env() {
    if [ -d "$VENV_DIR" ]; then
        echo "📦 Sauvegarde de l'environnement actuel..."
        if [ -f "$VENV_DIR/pyvenv.cfg" ]; then
            cp "$VENV_DIR/pyvenv.cfg" "$PROJECT_DIR/venv-backup.cfg" 2>/dev/null || true
        fi
        
        # Liste des packages installés
        if [ -f "$VENV_DIR/bin/activate" ] || [ -f "$VENV_DIR/Scripts/activate" ]; then
            echo "📝 Sauvegarde de la liste des packages..."
            source "$VENV_DIR/bin/activate" 2>/dev/null || source "$VENV_DIR/Scripts/activate" 2>/dev/null || true
            pip freeze > "$PROJECT_DIR/packages-backup.txt" 2>/dev/null || true
            deactivate 2>/dev/null || true
        fi
    fi
}

# Nettoyage et recréation de l'environnement
recreate_venv() {
    echo "🧹 Nettoyage de l'environnement virtuel..."
    
    if [ -d "$VENV_DIR" ]; then
        rm -rf "$VENV_DIR"
    fi
    
    echo "🆕 Création d'un nouvel environnement virtuel..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    
    # Activation de l'environnement
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
    elif [ -f "$VENV_DIR/Scripts/activate" ]; then
        source "$VENV_DIR/Scripts/activate"
    else
        echo "❌ Impossible d'activer l'environnement virtuel"
        exit 1
    fi
    
    echo "✅ Environnement virtuel créé et activé"
}

# Installation des packages avec versions compatibles
install_compatible_packages() {
    echo "📦 Installation des packages avec versions compatibles..."
    
    # Mise à jour de pip
    pip install --upgrade pip
    
    # Installation dans l'ordre pour éviter les conflits
    echo "1️⃣ Installation de NumPy compatible..."
    pip install "numpy>=1.21.6,<2.0.0" --force-reinstall
    
    echo "2️⃣ Installation de SciPy compatible..."
    pip install "scipy>=1.9.0,<1.12.0" --force-reinstall
    
    echo "3️⃣ Installation de pandas compatible..."
    pip install "pandas>=1.5.0,<2.1.0" --force-reinstall
    
    echo "4️⃣ Installation de scikit-learn..."
    pip install "scikit-learn>=1.1.0,<1.4.0"
    
    # TensorFlow en dernier pour éviter les conflits
    echo "5️⃣ Installation de TensorFlow compatible..."
    pip install "tensorflow>=2.13.0,<2.16.0" --no-deps
    pip install "tensorflow>=2.13.0,<2.16.0"
    
    # Packages web
    echo "6️⃣ Installation des packages web..."
    pip install flask flask-cors fastapi uvicorn pydantic python-multipart
    
    # Autres dépendances
    echo "7️⃣ Installation des autres dépendances..."
    pip install requests PyPDF2 prometheus-client structlog gunicorn python-dotenv nltk
    
    echo "✅ Tous les packages installés avec succès"
}

# Vérification de l'installation
verify_installation() {
    echo "🔍 Vérification de l'installation..."
    
    python -c "
import sys
print(f'Python: {sys.version}')

try:
    import numpy as np
    print(f'✅ NumPy: {np.__version__}')
except Exception as e:
    print(f'❌ NumPy: {e}')

try:
    import scipy
    print(f'✅ SciPy: {scipy.__version__}')
except Exception as e:
    print(f'❌ SciPy: {e}')

try:
    import pandas as pd
    print(f'✅ Pandas: {pd.__version__}')
except Exception as e:
    print(f'❌ Pandas: {e}')

try:
    import tensorflow as tf
    print(f'✅ TensorFlow: {tf.__version__}')
except Exception as e:
    print(f'⚠️  TensorFlow: {e}')

try:
    import flask
    print(f'✅ Flask: {flask.__version__}')
except Exception as e:
    print(f'❌ Flask: {e}')
"
}

# Test de compatibilité spécifique
test_compatibility() {
    echo "🧪 Test de compatibilité NumPy/TensorFlow..."
    
    python -c "
import warnings
warnings.filterwarnings('ignore')

try:
    import numpy as np
    import tensorflow as tf
    print('✅ NumPy et TensorFlow compatibles')
    
    # Test basique
    arr = np.array([1, 2, 3, 4])
    tensor = tf.constant(arr)
    print(f'✅ Test tensor: {tensor.numpy()}')
    
except Exception as e:
    print(f'⚠️  Problème de compatibilité: {e}')

try:
    # Test import du module compat
    import sys
    sys.path.append('.')
    from app.compat import HAS_TENSORFLOW, HAS_SKLEARN
    print(f'✅ Module compat: TensorFlow={HAS_TENSORFLOW}, sklearn={HAS_SKLEARN}')
except Exception as e:
    print(f'⚠️  Module compat: {e}')
"
}

# Création du script de démarrage amélioré
create_startup_script() {
    echo "📝 Création du script de démarrage amélioré..."
    
    cat > "start-supersmartmatch-fixed.sh" << 'EOF'
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
EOF

    chmod +x "start-supersmartmatch-fixed.sh"
    echo "✅ Script de démarrage créé: start-supersmartmatch-fixed.sh"
}

# Fonction principale
main() {
    echo "🎯 Début du processus de fix..."
    
    detect_python
    backup_current_env
    recreate_venv
    install_compatible_packages
    verify_installation
    test_compatibility
    create_startup_script
    
    echo ""
    echo "🎉 Fix terminé avec succès!"
    echo "========================================="
    echo "✅ Environnement virtuel reconfiguré"
    echo "✅ Packages compatibles installés"
    echo "✅ Script de démarrage créé"
    echo ""
    echo "📋 Prochaines étapes:"
    echo "1. Testez: ./start-supersmartmatch-fixed.sh"
    echo "2. Ou directement: cd super-smart-match && python app.py"
    echo ""
    echo "🔧 En cas de problème persistant:"
    echo "   - Vérifiez les logs ci-dessus"
    echo "   - Relancez ce script avec: ./fix-numpy-compatibility.sh"
    echo ""
}

# Exécution
main "$@"
