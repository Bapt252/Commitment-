#!/bin/bash

# 🚀 Script de résolution rapide CV Parser V2
# Fix pour "Connection reset by peer" sur port 5051

echo "🔧 === FIX RAPIDE CV PARSER V2 ==="
echo "Résolution du problème de connexion sur port 5051..."
echo ""

# Fonction de logging avec timestamps
log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

# 1. Arrêt propre des services existants
log "🛑 Arrêt des services CV Parser existants..."
docker kill $(docker ps -q --filter 'publish=5051') 2>/dev/null && log "✅ Conteneur arrêté" || log "ℹ️  Aucun conteneur actif sur 5051"
docker rm $(docker ps -aq --filter 'publish=5051') 2>/dev/null && log "✅ Conteneur supprimé" || log "ℹ️  Aucun conteneur à supprimer"

# Nettoyage des processus Python sur 5051
log "🧹 Nettoyage des processus Python sur port 5051..."
pkill -f "python.*app.py.*5051" 2>/dev/null && log "✅ Processus Python arrêté" || log "ℹ️  Aucun processus Python sur 5051"

# 2. Vérification et création des répertoires requis
log "📁 Vérification des répertoires..."
mkdir -p cv-parser-v2/parsers 2>/dev/null

# 3. Reconstruction de l'image Docker
log "🔨 Reconstruction de l'image CV Parser V2..."
cd cv-parser-v2

# Vérification des fichiers critiques
if [ ! -f "app.py" ]; then
    log "❌ ERREUR: app.py manquant dans cv-parser-v2/"
    exit 1
fi

if [ ! -f "Dockerfile" ]; then
    log "❌ ERREUR: Dockerfile manquant dans cv-parser-v2/"
    exit 1
fi

if [ ! -f "parsers/fix-pdf-extraction.js" ]; then
    log "❌ ERREUR: fix-pdf-extraction.js manquant dans cv-parser-v2/parsers/"
    exit 1
fi

if [ ! -f "parsers/enhanced-mission-parser.js" ]; then
    log "❌ ERREUR: enhanced-mission-parser.js manquant dans cv-parser-v2/parsers/"
    exit 1
fi

log "✅ Tous les fichiers critiques sont présents"

# Build de l'image
log "🏗️  Construction de l'image Docker..."
docker build -t cv-parser-v2-fixed . --no-cache

if [ $? -ne 0 ]; then
    log "❌ ERREUR: Échec de la construction Docker"
    exit 1
fi

log "✅ Image Docker construite avec succès"

# 4. Démarrage du nouveau conteneur
log "🚀 Démarrage du conteneur CV Parser V2..."
docker run -d \
    -p 5051:5051 \
    --name cv-parser-v2-fixed \
    --restart unless-stopped \
    cv-parser-v2-fixed

if [ $? -ne 0 ]; then
    log "❌ ERREUR: Échec du démarrage du conteneur"
    exit 1
fi

log "✅ Conteneur démarré"

# 5. Vérification du démarrage
log "⏳ Attente du démarrage du service (15 secondes)..."
sleep 15

# Test de connectivité
log "🔍 Test de connectivité..."
for i in {1..5}; do
    if curl -s -f http://localhost:5051/health > /dev/null; then
        log "✅ CV Parser V2 répond sur port 5051 !"
        break
    else
        log "⏳ Tentative $i/5 - en attente..."
        sleep 5
    fi
done

# 6. Vérification finale et tests
echo ""
echo "🔍 === VÉRIFICATION FINALE ==="

# Test health check
echo "Health Check CV Parser V2:"
HEALTH_RESPONSE=$(curl -s http://localhost:5051/health)
if [ $? -eq 0 ]; then
    echo "✅ Succès: $HEALTH_RESPONSE"
else
    echo "❌ Échec de connexion"
    log "🚨 Affichage des logs pour diagnostic..."
    docker logs --tail 20 cv-parser-v2-fixed
    exit 1
fi

# Test des autres services
echo ""
echo "Vérification des autres services:"

echo "Job Parser V2 (5053):"
curl -s http://localhost:5053/health > /dev/null && echo "✅ Actif" || echo "❌ Inactif"

echo "Enhanced API V2.1 (5055):"
curl -s http://localhost:5055/health > /dev/null && echo "✅ Actif" || echo "❌ Inactif"

# 7. Instructions pour les tests
echo ""
echo "🎯 === TESTS RECOMMANDÉS ==="
echo ""
echo "1. Test simple du CV Parser:"
echo "   curl http://localhost:5051/health"
echo ""
echo "2. Test avec un fichier CV (remplacez le chemin):"
echo "   curl -X POST -F 'file=@~/Desktop/BATU\\ Sam.pdf' http://localhost:5051/api/parse-cv/"
echo ""
echo "3. Test du système complet Enhanced V2.1:"
echo "   curl http://localhost:5055/api/test/hugo-salvat"
echo ""
echo "4. Test avec vos fichiers réels:"
echo "   python test_matching_system.py --cv '~/Desktop/BATU Sam.pdf' --job '~/Desktop/IT .pdf'"
echo ""

# 8. Informations de monitoring
echo "📊 === MONITORING ==="
echo ""
echo "Pour surveiller les logs en temps réel:"
echo "   docker logs -f cv-parser-v2-fixed"
echo ""
echo "Pour redémarrer si nécessaire:"
echo "   docker restart cv-parser-v2-fixed"
echo ""
echo "Statut des conteneurs:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(5051|5053|5055)"

echo ""
log "🎉 CV Parser V2 restauré avec succès sur port 5051 !"
echo "Vous pouvez maintenant tester BATU Sam.pdf vs IT.pdf avec le système V2.1 Enhanced"
