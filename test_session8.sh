#!/bin/bash
# Script de test pour la Session 8: Analyse comportementale et profiling utilisateur

echo "=============================================================="
echo "🧪 Test de Session 8: Analyse comportementale et profiling utilisateur"
echo "=============================================================="

# Vérifier les prérequis
echo -e "\n1. Vérification des prérequis..."

# Vérifier Python
if command -v python3 >/dev/null 2>&1; then
    echo "✅ Python 3 est installé"
    python_version=$(python3 --version)
    echo "   Version: $python_version"
else
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier les packages Python
echo -e "\n2. Vérification des packages Python..."
packages=("pandas" "numpy" "flask" "sqlalchemy" "scikit-learn")
all_packages_installed=true

for package in "${packages[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo "✅ $package est installé"
    else
        echo "❌ $package n'est pas installé"
        all_packages_installed=false
    fi
done

if ! $all_packages_installed; then
    echo "⚠️ Certains packages nécessaires ne sont pas installés."
    echo "Voulez-vous les installer maintenant? (y/n)"
    read install_packages
    
    if [ "$install_packages" = "y" ] || [ "$install_packages" = "Y" ]; then
        echo "Installation des packages manquants..."
        pip3 install pandas numpy flask sqlalchemy scikit-learn
    else
        echo "⚠️ Les packages manquants doivent être installés pour utiliser la Session 8."
    fi
fi

# Vérifier l'environnement
echo -e "\n3. Vérification de l'environnement..."

if [ -f ".session8.env" ]; then
    echo "✅ Fichier d'environnement .session8.env trouvé"
    source .session8.env
    echo "   PORT: $PORT"
    echo "   DATABASE_URL: ${DATABASE_URL:-non défini}"
else
    echo "⚠️ Fichier d'environnement .session8.env non trouvé"
    echo "Création d'un fichier d'environnement par défaut..."
    
    cat > .session8.env << EOF
# Environment configuration for Session 8
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/commitment}"
export PORT=4242
export API_KEY="${API_KEY:-commitment-session8-key}"
export PYTHONPATH="${PYTHONPATH:-$(pwd)}"
EOF
    
    source .session8.env
    echo "✅ Fichier d'environnement créé et chargé"
fi

# Vérifier les modules d'analyse
echo -e "\n4. Vérification des modules d'analyse..."

if [ -d "analysis_session8" ]; then
    echo "✅ Module analysis_session8 trouvé"
    
    if [ -f "analysis_session8/__init__.py" ]; then
        echo "✅ Fichier d'initialisation analysis_session8/__init__.py trouvé"
    else
        echo "❌ Fichier d'initialisation analysis_session8/__init__.py manquant"
    fi
    
    module_files=("analyzer.py" "patterns.py" "preferences.py")
    all_modules_present=true
    
    for module in "${module_files[@]}"; do
        if [ -f "analysis_session8/$module" ]; then
            echo "✅ Module analysis_session8/$module trouvé"
        else
            echo "❌ Module analysis_session8/$module manquant"
            all_modules_present=false
        fi
    done
    
    if ! $all_modules_present; then
        echo "⚠️ Certains modules d'analyse nécessaires sont manquants"
    fi
else
    echo "⚠️ Module analysis_session8 non trouvé. Vérification de l'ancienne structure..."
    
    if [ -d "analysis" ]; then
        echo "✅ Module analysis trouvé (structure originale)"
        
        if [ -f "analysis/behavioral_analysis.py" ] && [ -f "analysis/pattern_detection.py" ] && [ -f "analysis/preference_scoring.py" ]; then
            echo "✅ Modules d'analyse nécessaires trouvés dans la structure originale"
        else
            echo "❌ Certains modules d'analyse nécessaires sont manquants dans la structure originale"
        fi
    else
        echo "❌ Aucun module d'analyse trouvé"
        echo "⚠️ L'API utilisera le mode de démonstration sans accès réel aux données"
    fi
fi

# Vérifier l'API
echo -e "\n5. Vérification de l'API..."

if [ -f "api/user_profile_api.py" ]; then
    echo "✅ API de profil utilisateur trouvée"
else
    echo "❌ API de profil utilisateur manquante"
    exit 1
fi

# Vérifier les scripts
echo -e "\n6. Vérification des scripts..."

if [ -f "scripts/start_profile_api.sh" ]; then
    echo "✅ Script de démarrage trouvé"
    
    if ! [ -x "scripts/start_profile_api.sh" ]; then
        echo "   Rendre le script exécutable..."
        chmod +x scripts/start_profile_api.sh
    fi
else
    echo "❌ Script de démarrage manquant"
fi

if [ -f "scripts/stop_profile_api.sh" ]; then
    echo "✅ Script d'arrêt trouvé"
    
    if ! [ -x "scripts/stop_profile_api.sh" ]; then
        echo "   Rendre le script exécutable..."
        chmod +x scripts/stop_profile_api.sh
    fi
else
    echo "❌ Script d'arrêt manquant"
fi

# Tester le démarrage de l'API
echo -e "\n7. Test de démarrage de l'API..."

if [ -x "scripts/start_profile_api.sh" ]; then
    echo "Voulez-vous tester le démarrage de l'API? (y/n)"
    read test_api
    
    if [ "$test_api" = "y" ] || [ "$test_api" = "Y" ]; then
        # Vérifier si l'API est déjà en cours d'exécution
        if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
            echo "⚠️ Le port $PORT est déjà en utilisation. L'API est peut-être déjà en cours d'exécution."
            echo "Voulez-vous arrêter le service existant? (y/n)"
            read stop_service
            
            if [ "$stop_service" = "y" ] || [ "$stop_service" = "Y" ]; then
                ./scripts/stop_profile_api.sh
                sleep 2
            else
                echo "⚠️ Test de l'API ignoré."
                test_api="n"
            fi
        fi
        
        if [ "$test_api" = "y" ] || [ "$test_api" = "Y" ]; then
            # Démarrer l'API
            ./scripts/start_profile_api.sh
            
            # Attendre le démarrage
            echo "Attente du démarrage de l'API..."
            sleep 3
            
            # Tester l'API
            echo "Test de l'API..."
            if curl -s http://localhost:$PORT/api/health > /dev/null; then
                health_response=$(curl -s http://localhost:$PORT/api/health)
                echo "✅ API en cours d'exécution"
                echo "Réponse de santé: $health_response"
                
                # Tester un profil utilisateur
                echo "Test de récupération d'un profil utilisateur..."
                curl -s -H "X-API-Key: $API_KEY" http://localhost:$PORT/api/profiles/user/1 | python3 -m json.tool
                
                # Arrêter l'API
                echo "Arrêt de l'API..."
                ./scripts/stop_profile_api.sh
            else
                echo "❌ L'API n'a pas pu démarrer correctement"
                echo "Vérifiez les logs dans logs/profile_api.log"
            fi
        fi
    else
        echo "Test de l'API ignoré."
    fi
else
    echo "❌ Impossible de tester l'API: script de démarrage manquant ou non exécutable."
fi

# Résumé
echo -e "\n=============================================================="
echo "✅ Tests Session 8 terminés"
echo "=============================================================="
echo ""
echo "Pour démarrer l'API de Session 8:"
echo "  ./scripts/start_profile_api.sh"
echo ""
echo "Pour l'arrêter:"
echo "  ./scripts/stop_profile_api.sh"
echo ""
echo "Pour l'utiliser pour la démonstration:"
echo "  ./demo_session8.sh"
echo "=============================================================="
