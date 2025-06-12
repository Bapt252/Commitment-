#!/bin/bash

# 🔧 Script de diagnostic et résolution CV Parser V2
# Fix pour le problème "Connection reset by peer" sur port 5051

echo "🔍 === DIAGNOSTIC CV PARSER V2 - PORT 5051 ==="
echo "Recherche de la source du problème de connexion..."
echo ""

# 1. Vérifier l'état actuel des services
echo "📊 1. État des services..."
echo "CV Parser V2 (5051):"
curl -s http://localhost:5051/health && echo " ✅ Actif" || echo " ❌ Inactif/Problème"

echo "Job Parser V2 (5053):"
curl -s http://localhost:5053/health && echo " ✅ Actif" || echo " ❌ Inactif"

echo "Enhanced API V2.1 (5055):"
curl -s http://localhost:5055/health && echo " ✅ Actif" || echo " ❌ Inactif"
echo ""

# 2. Vérifier les conteneurs Docker
echo "🐳 2. État des conteneurs Docker..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(5051|5053|5055|cv-parser|job-parser)"
echo ""

# 3. Vérifier les logs des conteneurs
echo "📋 3. Logs des conteneurs CV Parser..."
CV_CONTAINER=$(docker ps --format "{{.Names}}" | grep -i cv | head -1)
if [ ! -z "$CV_CONTAINER" ]; then
    echo "Conteneur trouvé: $CV_CONTAINER"
    echo "Logs récents:"
    docker logs --tail 20 $CV_CONTAINER
else
    echo "❌ Aucun conteneur CV Parser trouvé"
fi
echo ""

# 4. Vérifier la présence des fichiers critiques
echo "📁 4. Vérification des fichiers critiques..."
cd cv-parser-v2/parsers/

echo "fix-pdf-extraction.js:"
[ -f "fix-pdf-extraction.js" ] && echo " ✅ Présent" || echo " ❌ Manquant"

echo "enhanced-mission-parser.js:"
[ -f "enhanced-mission-parser.js" ] && echo " ✅ Présent" || echo " ❌ Manquant"

echo "Dockerfile:"
[ -f "../Dockerfile" ] && echo " ✅ Présent" || echo " ❌ Manquant"

echo "app.py:"
[ -f "../app.py" ] && echo " ✅ Présent" || echo " ❌ Manquant"
echo ""

# 5. Vérifier les ports utilisés
echo "🔌 5. Ports utilisés..."
echo "Port 5051:"
netstat -tlnp 2>/dev/null | grep :5051 || echo " ❌ Aucun processus sur 5051"

echo "Port 5053:"
netstat -tlnp 2>/dev/null | grep :5053 || echo " ❌ Aucun processus sur 5053"

echo "Port 5055:"
netstat -tlnp 2>/dev/null | grep :5055 || echo " ❌ Aucun processus sur 5055"
echo ""

# 6. Solutions proposées
echo "🛠️  === SOLUTIONS PROPOSÉES ==="

# Solution 1: Restart des conteneurs
echo "1. 🔄 Redémarrage des conteneurs CV Parser:"
echo "   docker restart \$(docker ps -q --filter 'name=cv')"
echo ""

# Solution 2: Rebuild de l'image
echo "2. 🔨 Reconstruction de l'image CV Parser:"
echo "   cd cv-parser-v2"
echo "   docker build -t cv-parser-v2 ."
echo "   docker run -d -p 5051:5051 --name cv-parser-v2-new cv-parser-v2"
echo ""

# Solution 3: Démarrage direct (sans Docker)
echo "3. 🐍 Démarrage direct Python (debug):"
echo "   cd cv-parser-v2"
echo "   pip install -r requirements.txt"
echo "   python app.py"
echo ""

# Solution 4: Kill et redémarrage complet
echo "4. 💥 Reset complet du système:"
echo "   docker kill \$(docker ps -q --filter 'publish=5051')"
echo "   docker rm \$(docker ps -aq --filter 'publish=5051')"
echo "   cd cv-parser-v2"
echo "   docker build -t cv-parser-v2-fixed ."
echo "   docker run -d -p 5051:5051 --name cv-parser-v2-fixed cv-parser-v2-fixed"
echo ""

# AUTO-FIX: Tentative de résolution automatique
echo "🤖 === AUTO-FIX ==="
read -p "Voulez-vous que je tente de résoudre automatiquement ? (y/n): " auto_fix

if [ "$auto_fix" = "y" ] || [ "$auto_fix" = "Y" ]; then
    echo "🔄 Tentative de résolution automatique..."
    
    # Stopper les conteneurs CV Parser existants
    echo "Arrêt des conteneurs CV Parser existants..."
    docker kill $(docker ps -q --filter 'publish=5051') 2>/dev/null || echo "Aucun conteneur sur 5051"
    docker rm $(docker ps -aq --filter 'publish=5051') 2>/dev/null || echo "Aucun conteneur à supprimer"
    
    # Rebuild et redémarrage
    echo "Reconstruction de l'image CV Parser..."
    cd cv-parser-v2
    docker build -t cv-parser-v2-fixed .
    
    echo "Démarrage du nouveau conteneur..."
    docker run -d -p 5051:5051 --name cv-parser-v2-fixed cv-parser-v2-fixed
    
    # Test
    echo "Test du nouveau conteneur (attente 10s)..."
    sleep 10
    
    curl -s http://localhost:5051/health && echo "✅ CV Parser V2 redémarré avec succès !" || echo "❌ Problème persiste"
    
    echo ""
    echo "🔍 Statut final des services:"
    echo "CV Parser V2 (5051):"
    curl -s http://localhost:5051/health && echo " ✅ Actif" || echo " ❌ Toujours inactif"
    
    echo "Job Parser V2 (5053):"
    curl -s http://localhost:5053/health && echo " ✅ Actif" || echo " ❌ Inactif"
    
    echo "Enhanced API V2.1 (5055):"
    curl -s http://localhost:5055/health && echo " ✅ Actif" || echo " ❌ Inactif"
fi

echo ""
echo "🎯 === PROCHAINES ÉTAPES ==="
echo "1. Si le problème persiste, vérifiez les logs Docker: docker logs cv-parser-v2-fixed"
echo "2. Testez BATU Sam.pdf: curl -X POST -F 'file=@/path/to/BATU\\ Sam.pdf' http://localhost:5051/api/parse-cv/"
echo "3. Une fois résolu, testez le matching complet avec Enhanced API V2.1"
echo ""
echo "📝 Pour des tests avancés, utilisez: python test_matching_system.py"
