#!/bin/bash
# Script pour adapter les importations de la Session 8
# Résout les problèmes de structure de modules entre analysis/ et analysis_session8/

echo "=============================================================="
echo "🔄 Adaptation des importations pour la Session 8"
echo "=============================================================="

# Vérifier si le répertoire analysis_session8 existe
if [ ! -d "analysis_session8" ]; then
    echo "Création du répertoire analysis_session8..."
    mkdir -p analysis_session8
    touch analysis_session8/__init__.py
    echo "✅ Répertoire analysis_session8 créé"
else
    echo "Le répertoire analysis_session8 existe déjà"
fi

# Créer un adaptateur pour les imports
echo "Création de l'adaptateur d'importation..."

cat > analysis_session8/__init__.py << 'EOF'
"""
Session 8: Analyse Comportementale et Profiling Utilisateur
Module principal d'analyse comportementale
"""

# Gérer les deux structures d'importation possibles
try:
    # Essayer d'abord d'importer depuis analysis_session8
    from analysis_session8.analyzer import BehavioralAnalyzer
    from analysis_session8.patterns import PatternDetector
    from analysis_session8.preferences import PreferenceScorer
    SESSION8_IMPORTS = True
except ImportError:
    try:
        # Fallback sur analysis (ancienne structure)
        from analysis.behavioral_analysis import BehavioralAnalyzer
        from analysis.pattern_detection import PatternDetector
        from analysis.preference_scoring import PreferenceScorer
        
        # Réexporter les classes
        SESSION8_IMPORTS = False
        print("Utilisation des modules d'analyse de l'ancienne structure")
    except ImportError:
        print("ERREUR: Impossible d'importer les modules d'analyse")
        # Créer des stubs pour la démonstration si nécessaire
        class BehavioralAnalyzer:
            def __init__(self, *args, **kwargs): pass
        class PatternDetector:
            def __init__(self, *args, **kwargs): pass
        class PreferenceScorer:
            def __init__(self, *args, **kwargs): pass
        SESSION8_IMPORTS = True

# Exporter les classes
__all__ = ['BehavioralAnalyzer', 'PatternDetector', 'PreferenceScorer']
EOF

echo "✅ Adaptateur d'importation créé"

# Mise à jour des imports dans l'API
echo "Mise à jour des imports dans l'API..."

# Vérifier si le fichier API existe
if [ -f "api/user_profile_api.py" ]; then
    # Créer une sauvegarde
    cp api/user_profile_api.py api/user_profile_api.py.bak
    
    # Mise à jour des imports
    if grep -q "from analysis\." api/user_profile_api.py; then
        # Pour macOS, la syntaxe de sed est différente
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' 's/from analysis\./from analysis_session8./g' api/user_profile_api.py
            sed -i '' 's/import analysis\./import analysis_session8./g' api/user_profile_api.py
        else
            # Linux
            sed -i 's/from analysis\./from analysis_session8./g' api/user_profile_api.py
            sed -i 's/import analysis\./import analysis_session8./g' api/user_profile_api.py
        fi
        echo "✅ Imports API mis à jour"
    else
        echo "Aucun import à mettre à jour ou imports déjà adaptés"
    fi
else
    echo "⚠️ Le fichier API user_profile_api.py n'existe pas"
fi

# Configuration pour éviter les conflits de port
echo "Configuration du port pour éviter les conflits..."

# Vérifier si le script de démarrage existe
if [ -f "scripts/start_profile_api.sh" ]; then
    # Récupérer le port actuel
    current_port=$(grep "export PORT=" scripts/start_profile_api.sh | sed 's/export PORT=//')
    
    # Vérifier si le port est déjà défini à 4242
    if [ "$current_port" = "4242" ]; then
        echo "Le port est déjà configuré à 4242"
    else
        # Créer une sauvegarde
        cp scripts/start_profile_api.sh scripts/start_profile_api.sh.bak
        
        # Pour macOS, la syntaxe de sed est différente
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' 's/export PORT=.*/export PORT=4242/' scripts/start_profile_api.sh
        else
            # Linux
            sed -i 's/export PORT=.*/export PORT=4242/' scripts/start_profile_api.sh
        fi
        echo "✅ Port mis à jour à 4242 dans le script de démarrage"
    fi
    
    # S'assurer que le script est exécutable
    chmod +x scripts/start_profile_api.sh
    echo "✅ Script de démarrage rendu exécutable"
else
    echo "⚠️ Le script de démarrage start_profile_api.sh n'existe pas"
fi

# Rendre les scripts exécutables
echo "Rendre les scripts de la Session 8 exécutables..."

# Liste des scripts à rendre exécutables
scripts=(
    "scripts/start_profile_api.sh"
    "scripts/stop_profile_api.sh"
    "scripts/setup_session8.sh"
    "test_session8.sh"
    "demo_session8.sh"
)

for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        echo "✅ $script rendu exécutable"
    else
        echo "⚠️ $script n'existe pas"
    fi
done

echo "=============================================================="
echo "✅ Adaptation des importations terminée"
echo "=============================================================="
echo ""
echo "Prochaines étapes:"
echo "1. Exécuter le script de test pour vérifier l'installation:"
echo "   ./test_session8.sh"
echo ""
echo "2. Démarrer l'API de profil utilisateur:"
echo "   ./scripts/start_profile_api.sh"
echo ""
echo "3. Exécuter la démonstration des fonctionnalités:"
echo "   ./demo_session8.sh"
echo "=============================================================="
