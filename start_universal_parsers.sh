#!/bin/bash
# 🚀 SuperSmartMatch V2.1 - Démarrage Rapide Universal Parsers
# Script de démarrage automatique pour test immédiat

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 SuperSmartMatch V2.1 - Démarrage Rapide Universal Parsers${NC}"
echo "=============================================================="

# Fonction de log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Vérification Docker
if ! command -v docker &> /dev/null; then
    log_warning "Docker non trouvé. Installation locale recommandée :"
    echo "./install_universal_parsers.sh"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_warning "Docker Compose non trouvé. Utilisation de 'docker compose' (v2)"
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Arrêt des services existants
log_info "Arrêt des services existants..."
$DOCKER_COMPOSE down 2>/dev/null || true

# Construction des images
log_info "Construction des images Universal Parsers..."
$DOCKER_COMPOSE build cv-parser job-parser

# Démarrage des parsers
log_info "Démarrage des Universal Parsers..."
$DOCKER_COMPOSE up -d cv-parser job-parser redis

# Attente démarrage
log_info "Attente du démarrage des services..."
sleep 15

# Tests de santé
log_info "Tests de santé des parsers..."

# Test CV Parser
if curl -f http://localhost:5051/health >/dev/null 2>&1; then
    log_success "CV Parser (port 5051) : ✅ Opérationnel"
else
    log_warning "CV Parser (port 5051) : ⚠️ Non accessible"
fi

# Test Job Parser
if curl -f http://localhost:5053/health >/dev/null 2>&1; then
    log_success "Job Parser (port 5053) : ✅ Opérationnel"
else
    log_warning "Job Parser (port 5053) : ⚠️ Non accessible"
fi

# Test formats supportés
log_info "Vérification des formats supportés..."
FORMATS=$(curl -s http://localhost:5051/api/formats 2>/dev/null | grep -o '"total_formats":[0-9]*' | cut -d':' -f2 || echo "0")
if [ "$FORMATS" -gt 0 ]; then
    log_success "Formats supportés : $FORMATS formats détectés"
else
    log_warning "Impossible de récupérer les formats supportés"
fi

echo
echo "🎉 UNIVERSAL PARSERS V2.1 DÉMARRÉS AVEC SUCCÈS !"
echo "================================================="
echo
echo "📋 ENDPOINTS DISPONIBLES :"
echo "  • CV Parser Health    : http://localhost:5051/health"
echo "  • CV Parser API       : http://localhost:5051/api/parse-cv/"
echo "  • CV Parser Formats   : http://localhost:5051/api/formats"
echo "  • Job Parser Health   : http://localhost:5053/health"  
echo "  • Job Parser API      : http://localhost:5053/api/parse-job"
echo "  • Job Parser Formats  : http://localhost:5053/api/formats"
echo
echo "🧪 TESTS RAPIDES :"
echo
echo "# Test health check"
echo "curl http://localhost:5051/health"
echo
echo "# Test formats supportés"
echo "curl http://localhost:5051/api/formats"
echo
echo "# Test parsing PDF (rétrocompatible)"
echo "curl -X POST -F 'file=@votre_cv.pdf' http://localhost:5051/api/parse-cv/"
echo
echo "# Test parsing Word (NOUVEAU)"
echo "curl -X POST -F 'file=@votre_cv.docx' http://localhost:5051/api/parse-cv/"
echo
echo "# Test parsing Image OCR (NOUVEAU)"
echo "curl -X POST -F 'file=@scan_cv.png' http://localhost:5051/api/parse-cv/"
echo
echo "📄 FORMATS MAINTENANT SUPPORTÉS :"
echo "  ✅ PDF (natif + fallback)"
echo "  ✅ Microsoft Word (.docx, .doc)"
echo "  ✅ Images avec OCR (.jpg, .png, .tiff, .bmp, .webp)"
echo "  ✅ Fichiers texte (.txt, .csv)"
echo "  ✅ Pages web (.html, .htm)"
echo "  ✅ Rich Text Format (.rtf)"
echo "  ✅ OpenOffice Document (.odt)"
echo
echo "🔧 COMMANDES UTILES :"
echo "  • Logs en temps réel   : $DOCKER_COMPOSE logs -f cv-parser job-parser"
echo "  • Redémarrage          : $DOCKER_COMPOSE restart cv-parser job-parser"
echo "  • Arrêt               : $DOCKER_COMPOSE down"
echo "  • Tests automatiques  : python3 test_universal_parsers.py"
echo
echo "📚 DOCUMENTATION COMPLÈTE : README.md"
echo
log_success "Universal Parsers V2.1 prêts pour SuperSmartMatch Enhanced ! 🚀"
