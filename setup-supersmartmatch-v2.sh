#!/bin/bash

# 🚀 SuperSmartMatch V2 - Script de Configuration Finale
# Rend tous les scripts exécutables et configure l'environnement

echo "🚀 SuperSmartMatch V2 - Configuration Finale"
echo "============================================="

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[CONFIG]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

log "Configuration des permissions et scripts..."

# Liste des scripts à rendre exécutables
SCRIPTS=(
    "optimize-supersmartmatch-v2.sh"
    "test-workflow-complete-v2.sh"
    "upgrade-mission-matching.sh"
    "start-supersmartmatch-auto.sh" 
    "fix-supersmartmatch-v2.sh"
    "test-enhanced-system.sh"
    "build_all.sh"
    "restart-cv-parser.sh"
    "curl-test-cv-parser.sh"
    "curl-test-job-parser.sh"
)

# Rendre les scripts exécutables
log "Attribution des permissions d'exécution..."
for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        chmod +x "$script"
        log "✅ $script - Exécutable"
    else
        warn "⚠️  $script - Non trouvé"
    fi
done

# Scripts dans le dossier matching-service
if [ -d "matching-service/scripts" ]; then
    find matching-service/scripts -name "*.sh" -exec chmod +x {} \;
    log "✅ Scripts matching-service - Exécutables"
fi

# Création du dossier web-interface s'il n'existe pas
mkdir -p web-interface
log "✅ Dossier web-interface créé"

# Copie de l'interface web dans le dossier
if [ ! -f "web-interface/index.html" ]; then
    info "💡 Pour utiliser l'interface web:"
    info "   1. Copiez le contenu de l'artifact 'SuperSmartMatch V2 - Interface de Test'"
    info "   2. Sauvegardez-le comme web-interface/index.html"
    info "   3. Lancez: cd web-interface && python3 -m http.server 8080"
fi

# Création des dossiers de travail
mkdir -p test-files test-results logs temp
log "✅ Dossiers de travail créés: test-files, test-results, logs, temp"

# Vérification de Docker
if command -v docker &> /dev/null; then
    log "✅ Docker détecté"
    if command -v docker-compose &> /dev/null; then
        log "✅ Docker Compose détecté"
    else
        warn "⚠️  Docker Compose non trouvé - Installez docker-compose"
    fi
else
    warn "⚠️  Docker non trouvé - Installez Docker pour utiliser SuperSmartMatch"
fi

# Vérification de Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    log "✅ Node.js détecté: $NODE_VERSION"
else
    warn "⚠️  Node.js non trouvé - Requis pour les parsers enrichis"
fi

# Vérification de Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    log "✅ Python détecté: $PYTHON_VERSION"
else
    warn "⚠️  Python3 non trouvé - Requis pour les APIs"
fi

# Vérification de curl et jq
command -v curl &> /dev/null && log "✅ curl disponible" || warn "⚠️  curl manquant"
command -v jq &> /dev/null && log "✅ jq disponible" || warn "⚠️  jq manquant (installation: sudo apt install jq)"

echo ""
log "🎉 CONFIGURATION TERMINÉE !"
echo "=========================="
echo ""
info "📋 COMMANDES PRINCIPALES V2:"
echo ""
echo "🚀 Démarrage:"
echo "   ./start-supersmartmatch-auto.sh"
echo ""
echo "🧪 Tests:"
echo "   ./test-workflow-complete-v2.sh         # Test complet automatisé"
echo "   ./test-enhanced-system.sh full         # Tests système enrichis"
echo "   ./optimize-supersmartmatch-v2.sh       # Optimisations avancées"
echo ""
echo "🔍 Monitoring:"
echo "   ./monitor-supersmartmatch-v2.sh        # Surveillance performances"
echo "   curl http://localhost:5051/health      # CV Parser V2"
echo "   curl http://localhost:5053/health      # Job Parser V2"
echo ""
echo "🌐 Interface Web:"
echo "   cd web-interface"
echo "   python3 -m http.server 8080"
echo "   # Puis ouvrir http://localhost:8080"
echo ""
echo "🛠️  Développement:"
echo "   ./build_all.sh                         # Rebuild complet"
echo "   ./restart-cv-parser.sh                 # Restart CV parser"
echo "   docker-compose logs cv-parser          # Logs CV parser"
echo ""
info "🎯 SuperSmartMatch V2 - Scoring: 40% missions + 30% compétences + 15% expérience + 15% qualité"
info "✨ Extraction enrichie des missions opérationnelle avec 8 catégories de classification"
echo ""
log "✅ Votre système SuperSmartMatch V2 est maintenant entièrement configuré et prêt !"
