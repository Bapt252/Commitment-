#!/bin/bash

# Debug SuperSmartMatch - Diagnostic complet

echo "🔍 Diagnostic SuperSmartMatch"
echo "============================="

# 1. Vérifier les processus Python
echo "1️⃣ Processus Python actifs:"
ps aux | grep python3 | grep -v grep

echo ""

# 2. Vérifier les ports utilisés
echo "2️⃣ Ports 5060-5063 utilisés:"
for port in 5060 5061 5062 5063; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "   Port $port: OCCUPÉ"
        lsof -i :$port
    else
        echo "   Port $port: LIBRE"
    fi
done

echo ""

# 3. Vérifier l'environnement SuperSmartMatch
echo "3️⃣ Vérification environnement SuperSmartMatch:"
if [ -d "super-smart-match" ]; then
    echo "   ✅ Répertoire super-smart-match existe"
    
    if [ -f "super-smart-match/app.py" ]; then
        echo "   ✅ app.py existe"
    else
        echo "   ❌ app.py manquant"
    fi
    
    if [ -d "super-smart-match/venv" ]; then
        echo "   ✅ Environnement virtuel existe"
    else
        echo "   ❌ Environnement virtuel manquant"
    fi
else
    echo "   ❌ Répertoire super-smart-match manquant"
fi

echo ""

# 4. Test de démarrage rapide
echo "4️⃣ Test de démarrage sur port libre:"

# Trouver un port libre
for test_port in 5060 5061 5062 5063 5064; do
    if ! lsof -i :$test_port > /dev/null 2>&1; then
        echo "   🎯 Port libre trouvé: $test_port"
        
        echo "   📦 Démarrage de SuperSmartMatch..."
        cd super-smart-match
        
        if [ -d "venv" ]; then
            source venv/bin/activate
            export PYTHONPATH="$(pwd)/..:$PYTHONPATH"
            export PORT=$test_port
            
            echo "   🚀 Tentative de démarrage..."
            timeout 10s python3 app.py &
            PID=$!
            
            # Attendre un peu
            sleep 3
            
            # Tester la connexion
            if curl -s "http://localhost:$test_port/api/health" > /dev/null 2>&1; then
                echo "   ✅ SuperSmartMatch fonctionne sur le port $test_port !"
                echo "   🌐 URL: http://localhost:$test_port"
                
                # Arrêter le test
                kill $PID 2>/dev/null
                
                # Créer un script de démarrage corrigé
                cd ..
                cat > "start-supersmartmatch-debug.sh" << EOF
#!/bin/bash
echo "🚀 Démarrage SuperSmartMatch sur port $test_port"
cd super-smart-match
source venv/bin/activate
export PYTHONPATH="\$(pwd)/..:$PYTHONPATH"
export PORT=$test_port
echo "🌐 Disponible sur: http://localhost:$test_port"
python3 app.py
EOF
                chmod +x "start-supersmartmatch-debug.sh"
                
                echo ""
                echo "🎉 Solution trouvée !"
                echo "   Utilisez: ./start-supersmartmatch-debug.sh"
                echo "   URL: http://localhost:$test_port"
                
                exit 0
            else
                echo "   ❌ Échec du test sur le port $test_port"
                kill $PID 2>/dev/null
            fi
        else
            echo "   ❌ Environnement virtuel manquant"
        fi
        
        cd ..
        break
    fi
done

echo ""
echo "🚨 Problème détecté. Solutions:"
echo "   1. Exécutez: ./fix-supersmartmatch-quick.sh"
echo "   2. Ou: git pull origin main && ./fix-supersmartmatch-dependencies.sh"
echo "   3. Vérifiez que Docker n'utilise pas les ports"
