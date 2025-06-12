#!/bin/bash

# 🌐 SuperSmartMatch V2 - Lancement Interface Web
echo "🌐 Lancement Interface Web SuperSmartMatch V2"
echo "============================================="

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[WEB]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# 1. Nettoyer les processus existants
log "🧹 Nettoyage des serveurs existants..."
pkill -f "http.server" 2>/dev/null
pkill -f "cors-proxy" 2>/dev/null
sleep 2

# 2. Vérifier les prérequis
log "🔍 Vérification des prérequis..."

if [ ! -f "cors-proxy.py" ]; then
    error "❌ cors-proxy.py non trouvé"
    exit 1
fi

if [ ! -d "web-interface" ]; then
    error "❌ Dossier web-interface non trouvé"
    exit 1
fi

if [ ! -f "web-interface/index.html" ]; then
    error "❌ Interface web non trouvée"
    exit 1
fi

# 3. Vérifier que SuperSmartMatch V2 fonctionne
log "⚡ Vérification SuperSmartMatch V2..."
if curl -s -f http://localhost:5051/health > /dev/null; then
    log "✅ CV Parser V2 opérationnel"
else
    warn "⚠️  CV Parser V2 non accessible - Lancez 'docker-compose up -d' d'abord"
fi

if curl -s -f http://localhost:5053/health > /dev/null; then
    log "✅ Job Parser V2 opérationnel" 
else
    warn "⚠️  Job Parser V2 non accessible - Lancez 'docker-compose up -d' d'abord"
fi

# 4. Lancer le proxy CORS
log "🔗 Lancement du proxy CORS (port 8090)..."
python3 cors-proxy.py > cors-proxy.log 2>&1 &
CORS_PID=$!
sleep 3

# Vérifier le proxy CORS
if curl -s -f http://localhost:8090 > /dev/null; then
    log "✅ Proxy CORS démarré sur http://localhost:8090"
else
    error "❌ Erreur démarrage proxy CORS"
    kill $CORS_PID 2>/dev/null
    exit 1
fi

# 5. Lancer l'interface web
log "🌐 Lancement interface web (port 8080)..."
cd web-interface
python3 -m http.server 8080 > ../web-interface.log 2>&1 &
WEB_PID=$!
cd ..
sleep 3

# Vérifier l'interface web
if curl -s -f http://localhost:8080 > /dev/null; then
    log "✅ Interface web démarrée sur http://localhost:8080"
else
    error "❌ Erreur démarrage interface web"
    kill $CORS_PID $WEB_PID 2>/dev/null
    exit 1
fi

# 6. Test final des endpoints
log "🧪 Test des endpoints..."
echo ""
echo "Proxy CORS endpoints:"
curl -s http://localhost:8090/health-cv | jq -r '.service + " - " + .status' 2>/dev/null || echo "Health CV disponible"
curl -s http://localhost:8090/health-job | jq -r '.service + " - " + .status' 2>/dev/null || echo "Health Job disponible"

# 7. Affichage final
echo ""
log "🎉 INTERFACE WEB LANCÉE AVEC SUCCÈS!"
echo "===================================="
echo ""
log "📋 ACCÈS:"
echo "🌐 Interface Web: http://localhost:8080"
echo "🔗 Proxy CORS:   http://localhost:8090"
echo ""
log "🧪 TESTS DISPONIBLES:"
echo "1. Health Check Complet - Vérifier tous les services"
echo "2. Test Échantillon - Simulation sans PDF"
echo "3. Upload CV/Job - Drag & drop de vrais fichiers"
echo "4. Matching V2 - Scoring 40% missions"
echo ""
log "🔧 COMMANDES UTILES:"
echo "• Voir logs proxy: tail -f cors-proxy.log"
echo "• Voir logs web: tail -f web-interface.log"
echo "• Arrêter tout: kill $CORS_PID $WEB_PID"
echo ""
log "🎯 SuperSmartMatch V2 - Interface prête!"

# 8. Fonction de nettoyage à l'arrêt
cleanup() {
    echo ""
    log "🛑 Arrêt des serveurs web..."
    kill $CORS_PID $WEB_PID 2>/dev/null
    log "✅ Serveurs arrêtés"
    exit 0
}

trap cleanup INT TERM

# 9. Garder le script actif et afficher les logs
echo ""
log "📊 Logs en temps réel (Ctrl+C pour arrêter):"
echo "============================================="

# Surveiller les deux serveurs
while true; do
    if ! kill -0 $CORS_PID 2>/dev/null; then
        error "❌ Proxy CORS arrêté inopinément"
        break
    fi
    if ! kill -0 $WEB_PID 2>/dev/null; then
        error "❌ Interface web arrêtée inopinément"
        break
    fi
    sleep 5
done

cleanup