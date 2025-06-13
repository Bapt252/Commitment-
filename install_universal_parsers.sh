#!/bin/bash
# 🚀 SuperSmartMatch V2.1 - Installation Universal Parsers
# Script d'installation automatique pour parsers universels

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${SCRIPT_DIR}"
PYTHON_MIN_VERSION="3.8"
NODE_MIN_VERSION="14"

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Détection du système d'exploitation
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            OS="ubuntu"
        elif command -v yum &> /dev/null; then
            OS="centos"
        else
            OS="linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    else
        OS="unknown"
    fi
    log_info "Système détecté: $OS"
}

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python $PYTHON_VERSION trouvé"
    else
        log_error "Python 3 non trouvé. Installation requise."
        exit 1
    fi
    
    # Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | sed 's/v//')
        log_success "Node.js $NODE_VERSION trouvé"
    else
        log_error "Node.js non trouvé. Installation requise."
        exit 1
    fi
    
    # pip
    if command -v pip3 &> /dev/null; then
        log_success "pip3 trouvé"
    else
        log_error "pip3 non trouvé. Installation requise."
        exit 1
    fi
}

# Installation des dépendances système
install_system_dependencies() {
    log_info "Installation des dépendances système..."
    
    case $OS in
        "ubuntu")
            log_info "Installation via apt-get..."
            sudo apt-get update
            sudo apt-get install -y \
                libmagic-dev \
                tesseract-ocr \
                tesseract-ocr-fra \
                tesseract-ocr-eng \
                libreoffice \
                libjpeg-dev \
                libpng-dev \
                libtiff-dev \
                libxml2-dev \
                libxslt1-dev \
                build-essential
            ;;
        "centos")
            log_info "Installation via yum..."
            sudo yum install -y \
                file-devel \
                tesseract \
                tesseract-langpack-fra \
                tesseract-langpack-eng \
                libreoffice \
                libjpeg-devel \
                libpng-devel \
                libtiff-devel \
                libxml2-devel \
                libxslt-devel \
                gcc \
                gcc-c++
            ;;
        "macos")
            log_info "Installation via Homebrew..."
            if ! command -v brew &> /dev/null; then
                log_error "Homebrew non trouvé. Installation:"
                log_info "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            brew install libmagic tesseract tesseract-lang libreoffice
            ;;
        *)
            log_warning "Système non supporté automatiquement. Installation manuelle requise:"
            log_info "- libmagic-dev (détection format)"
            log_info "- tesseract-ocr + langues fr/en (OCR)"
            log_info "- libreoffice (conversion fallback)"
            log_info "- dépendances développement (gcc, headers)"
            ;;
    esac
    
    log_success "Dépendances système installées"
}

# Installation des dépendances Python
install_python_dependencies() {
    log_info "Installation des dépendances Python..."
    
    # Upgrade pip
    python3 -m pip install --upgrade pip
    
    # Installation dans CV Parser
    if [[ -f "${INSTALL_DIR}/cv-parser-v2/requirements.txt" ]]; then
        cd "${INSTALL_DIR}/cv-parser-v2"
        python3 -m pip install -r requirements.txt
        log_success "Dépendances CV Parser installées"
        cd "${INSTALL_DIR}"
    fi
    
    # Installation dans Job Parser
    if [[ -f "${INSTALL_DIR}/job-parser-v2/requirements.txt" ]]; then
        cd "${INSTALL_DIR}/job-parser-v2"
        python3 -m pip install -r requirements.txt
        log_success "Dépendances Job Parser installées"
        cd "${INSTALL_DIR}"
    fi
    
    # Installation globale pour les tests
    python3 -m pip install requests docx pillow
}

# Test des dépendances
test_dependencies() {
    log_info "Test des dépendances..."
    
    # Test python-magic
    if python3 -c "import magic; print('✅ python-magic OK')" 2>/dev/null; then
        log_success "python-magic OK"
    else
        log_error "python-magic ÉCHEC"
        return 1
    fi
    
    # Test pytesseract
    if python3 -c "import pytesseract; print('✅ pytesseract OK')" 2>/dev/null; then
        log_success "pytesseract OK"
    else
        log_error "pytesseract ÉCHEC"
        return 1
    fi
    
    # Test Tesseract CLI
    if tesseract --version &>/dev/null; then
        TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n1)
        log_success "Tesseract OK: $TESSERACT_VERSION"
    else
        log_error "Tesseract CLI ÉCHEC"
        return 1
    fi
    
    # Test modules Python
    MODULES=("docx" "PIL" "bs4" "striprtf" "odf" "pdfplumber")
    for module in "${MODULES[@]}"; do
        if python3 -c "import $module" 2>/dev/null; then
            log_success "Module $module OK"
        else
            log_warning "Module $module manquant (peut être installé automatiquement)"
        fi
    done
    
    log_success "Tests de dépendances terminés"
}

# Création de la structure des dossiers
create_directory_structure() {
    log_info "Création de la structure des dossiers..."
    
    # Dossiers temporaires
    mkdir -p /tmp/cv_parsing
    mkdir -p /tmp/job_parsing
    chmod 777 /tmp/cv_parsing /tmp/job_parsing 2>/dev/null || true
    
    # Dossiers de logs
    mkdir -p "${INSTALL_DIR}/logs"
    
    log_success "Structure des dossiers créée"
}

# Configuration des variables d'environnement
setup_environment() {
    log_info "Configuration de l'environnement..."
    
    # Création du fichier .env
    cat > "${INSTALL_DIR}/.env" << EOF
# SuperSmartMatch V2.1 - Configuration Universal Parsers
FLASK_ENV=production
FLASK_DEBUG=False
MAX_CONTENT_LENGTH=52428800
TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
PYTHONPATH=${INSTALL_DIR}
EOF
    
    # Configuration Tesseract
    if [[ "$OS" == "macos" ]]; then
        echo "TESSDATA_PREFIX=$(brew --prefix)/share/tessdata" >> "${INSTALL_DIR}/.env"
    fi
    
    log_success "Variables d'environnement configurées"
}

# Génération des scripts de démarrage
create_startup_scripts() {
    log_info "Création des scripts de démarrage..."
    
    # Script de démarrage CV Parser
    cat > "${INSTALL_DIR}/start_cv_parser.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/cv-parser-v2"
export PYTHONPATH="$(dirname "$0"):$PYTHONPATH"
source ../venv/bin/activate 2>/dev/null || true
python3 app.py
EOF
    
    # Script de démarrage Job Parser
    cat > "${INSTALL_DIR}/start_job_parser.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/job-parser-v2"
export PYTHONPATH="$(dirname "$0"):$PYTHONPATH"
source ../venv/bin/activate 2>/dev/null || true
python3 app.py
EOF
    
    # Script de test
    cat > "${INSTALL_DIR}/run_tests.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH="$(dirname "$0"):$PYTHONPATH"
source venv/bin/activate 2>/dev/null || true
python3 test_universal_parsers.py
EOF
    
    # Permissions d'exécution
    chmod +x "${INSTALL_DIR}/start_cv_parser.sh"
    chmod +x "${INSTALL_DIR}/start_job_parser.sh"
    chmod +x "${INSTALL_DIR}/run_tests.sh"
    
    log_success "Scripts de démarrage créés"
}

# Test de l'installation
test_installation() {
    log_info "Test de l'installation..."
    
    # Test import des modules dans CV Parser
    cd "${INSTALL_DIR}/cv-parser-v2"
    if python3 -c "from format_detector import format_detector; print('✅ format_detector OK')" 2>/dev/null; then
        log_success "CV Parser format_detector importé"
    else
        log_error "Échec import CV Parser format_detector"
        return 1
    fi
    
    if python3 -c "from text_extractor import text_extractor; print('✅ text_extractor OK')" 2>/dev/null; then
        log_success "CV Parser text_extractor importé"
    else
        log_error "Échec import CV Parser text_extractor"
        return 1
    fi
    
    # Test import des modules dans Job Parser
    cd "${INSTALL_DIR}/job-parser-v2"
    if python3 -c "from format_detector import format_detector; print('✅ format_detector OK')" 2>/dev/null; then
        log_success "Job Parser format_detector importé"
    else
        log_error "Échec import Job Parser format_detector"
        return 1
    fi
    
    if python3 -c "from text_extractor import text_extractor; print('✅ text_extractor OK')" 2>/dev/null; then
        log_success "Job Parser text_extractor importé"
    else
        log_error "Échec import Job Parser text_extractor"
        return 1
    fi
    
    cd "${INSTALL_DIR}"
    
    # Test des formats supportés
    FORMATS=$(cd cv-parser-v2 && python3 -c "from format_detector import format_detector; print(','.join(format_detector.get_supported_formats().keys()))" 2>/dev/null)
    log_success "Formats supportés: $FORMATS"
    
    log_success "Installation testée avec succès"
}

# Affichage des instructions finales
show_final_instructions() {
    log_success "🎉 Installation des Universal Parsers terminée !"
    echo
    log_info "📋 INSTRUCTIONS DE DÉMARRAGE:"
    echo
    log_info "1. Démarrage CV Parser (port 5051):"
    echo "   ./start_cv_parser.sh"
    echo
    log_info "2. Démarrage Job Parser (port 5053):"
    echo "   ./start_job_parser.sh"
    echo
    log_info "3. Test des parsers:"
    echo "   ./run_tests.sh"
    echo
    log_info "4. Vérification health:"
    echo "   curl http://localhost:5051/health"
    echo "   curl http://localhost:5053/health"
    echo
    log_info "5. Test d'un fichier:"
    echo "   curl -X POST -F 'file=@document.pdf' http://localhost:5051/api/parse-cv/"
    echo
    log_info "📄 FORMATS SUPPORTÉS:"
    echo "   ✅ PDF (natif + fallback)"
    echo "   ✅ Microsoft Word (.docx, .doc)"
    echo "   ✅ Images avec OCR (.jpg, .png, .tiff, .bmp, .webp)"
    echo "   ✅ Fichiers texte (.txt, .csv)"
    echo "   ✅ Pages web (.html, .htm)"
    echo "   ✅ Rich Text Format (.rtf)"
    echo "   ✅ OpenOffice Document (.odt)"
    echo
    log_info "📁 DOSSIERS IMPORTANTS:"
    echo "   - Logs: ${INSTALL_DIR}/logs/"
    echo "   - Config: ${INSTALL_DIR}/.env"
    echo "   - CV Parser: ${INSTALL_DIR}/cv-parser-v2/"
    echo "   - Job Parser: ${INSTALL_DIR}/job-parser-v2/"
    echo
    log_info "🔧 DÉPANNAGE:"
    echo "   - Tests: ./run_tests.sh"
    echo "   - Vérification deps: python3 -c 'import magic, pytesseract; print(\"OK\")'"
    echo "   - Logs détaillés dans les sorties des parsers"
}

# Fonction principale
main() {
    echo "🚀 SuperSmartMatch V2.1 - Installation Universal Parsers"
    echo "========================================================="
    echo
    
    detect_os
    check_prerequisites
    install_system_dependencies
    install_python_dependencies
    test_dependencies
    create_directory_structure
    setup_environment
    create_startup_scripts
    test_installation
    show_final_instructions
    
    log_success "🎉 Installation complète réussie !"
}

# Options de ligne de commande
case "${1:-}" in
    "deps-only")
        log_info "Installation des dépendances uniquement..."
        detect_os
        install_system_dependencies
        install_python_dependencies
        test_dependencies
        ;;
    "test")
        log_info "Test des dépendances uniquement..."
        test_dependencies
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [deps-only|test|help]"
        echo
        echo "  deps-only  : Installe uniquement les dépendances système et Python"
        echo "  test       : Teste les dépendances installées"
        echo "  help       : Affiche cette aide"
        echo "  (aucun)    : Installation complète"
        ;;
    *)
        main
        ;;
esac
