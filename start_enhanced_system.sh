#!/bin/bash

# 🚀 SuperSmartMatch V2.1 Enhanced - Script de Démarrage Rapide
# Script pour démarrer et tester le système amélioré

set -e  # Arrêter en cas d'erreur

echo "🚀 SUPERSMARTMATCH V2.1 ENHANCED - DÉMARRAGE RAPIDE"
echo "=================================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Fonction pour vérifier si un port est utilisé
check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        log_success "$service déjà en cours d'exécution sur le port $port"
        return 0
    else
        log_warning "$service non disponible sur le port $port"
        return 1
    fi
}

# Fonction pour tester la connectivité API
test_api() {
    local url=$1
    local name=$2
    
    if curl -s -f "$url" > /dev/null; then
        log_success "$name accessible"
        return 0
    else
        log_error "$name non accessible à $url"
        return 1
    fi
}

# Variables de configuration
CV_PARSER_PORT=5051
JOB_PARSER_PORT=5053
ENHANCED_API_PORT=5055

# 1. Vérification des services requis
echo ""
log_info "Vérification des services requis..."

check_port $CV_PARSER_PORT "CV Parser V2" || {
    log_error "CV Parser V2 non démarré. Veuillez le démarrer sur le port $CV_PARSER_PORT"
    echo "   Command: cd cv-parser-v2 && python app.py"
}

check_port $JOB_PARSER_PORT "Job Parser V2" || {
    log_error "Job Parser V2 non démarré. Veuillez le démarrer sur le port $JOB_PARSER_PORT"
    echo "   Command: cd job-parser-v2 && python app.py"
}

# 2. Démarrage de l'API Enhanced (si pas déjà démarrée)
echo ""
log_info "Démarrage de l'API Enhanced V2.1..."

if check_port $ENHANCED_API_PORT "Enhanced API"; then
    log_info "API Enhanced déjà démarrée"
else
    log_info "Démarrage de l'API Enhanced en arrière-plan..."
    nohup python api-matching-enhanced-v2.py > enhanced_api.log 2>&1 &
    sleep 3
    
    if check_port $ENHANCED_API_PORT "Enhanced API"; then
        log_success "API Enhanced démarrée avec succès"
    else
        log_error "Échec du démarrage de l'API Enhanced"
        echo "Vérifiez le fichier enhanced_api.log pour plus de détails"
        exit 1
    fi
fi

# 3. Tests de connectivité
echo ""
log_info "Test de connectivité des APIs..."

test_api "http://localhost:$CV_PARSER_PORT/health" "CV Parser API"
test_api "http://localhost:$JOB_PARSER_PORT/health" "Job Parser API" 
test_api "http://localhost:$ENHANCED_API_PORT/health" "Enhanced API"

# 4. Test rapide du cas Hugo Salvat
echo ""
log_info "Test du cas Hugo Salvat (Commercial IT vs Assistant Facturation)..."

HUGO_RESULT=$(curl -s "http://localhost:$ENHANCED_API_PORT/api/test/hugo-salvat" 2>/dev/null)

if [ $? -eq 0 ]; then
    SCORE=$(echo "$HUGO_RESULT" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['enhanced_result']['total_score'])" 2>/dev/null)
    TEST_STATUS=$(echo "$HUGO_RESULT" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['test_status'])" 2>/dev/null)
    
    if [ "$TEST_STATUS" = "success" ]; then
        log_success "Test Hugo Salvat réussi - Score: ${SCORE}% (attendu <30%)"
    else
        log_warning "Test Hugo Salvat - Score: ${SCORE}% (attention: score élevé détecté)"
    fi
else
    log_error "Impossible d'exécuter le test Hugo Salvat"
fi

# 5. Menu interactif
echo ""
echo "🎯 MENU D'OPTIONS DE TEST"
echo "========================"
echo "1. Test avec données d'exemple"
echo "2. Test avec fichier CV et Job spécifiques"
echo "3. Test en lot (dossier de CVs)"
echo "4. Ouvrir l'interface web (si disponible)"
echo "5. Voir les logs de l'API"
echo "6. Arrêter l'API Enhanced"
echo "7. Aide et documentation"
echo "0. Quitter"
echo ""

while true; do
    echo -n "Choisissez une option (0-7): "
    read -r choice
    
    case $choice in
        1)
            log_info "Lancement du test avec données d'exemple..."
            python test_matching_system.py --sample-test --predefined-tests
            ;;
        2)
            echo -n "Chemin vers le CV PDF: "
            read -r cv_path
            echo -n "Chemin vers le Job PDF: "
            read -r job_path
            
            if [ -f "$cv_path" ] && [ -f "$job_path" ]; then
                log_info "Test avec fichiers spécifiés..."
                python test_matching_system.py --cv "$cv_path" --job "$job_path"
            else
                log_error "Fichiers non trouvés"
            fi
            ;;
        3)
            echo -n "Dossier contenant les CVs: "
            read -r cvs_folder
            echo -n "Dossier contenant les Jobs: "
            read -r jobs_folder
            
            if [ -d "$cvs_folder" ] && [ -d "$jobs_folder" ]; then
                log_info "Test en lot..."
                python test_matching_system.py --cvs-folder "$cvs_folder" --jobs-folder "$jobs_folder"
            else
                log_error "Dossiers non trouvés"
            fi
            ;;
        4)
            log_info "Ouverture de l'interface web..."
            if command -v xdg-open > /dev/null; then
                xdg-open "http://localhost:8000"  # Supposé être votre interface web
            elif command -v open > /dev/null; then
                open "http://localhost:8000"
            else
                echo "Ouvrez manuellement: http://localhost:8000"
            fi
            ;;
        5)
            log_info "Logs de l'API Enhanced (10 dernières lignes):"
            if [ -f "enhanced_api.log" ]; then
                tail -10 enhanced_api.log
            else
                log_warning "Fichier de log non trouvé"
            fi
            ;;
        6)
            log_info "Arrêt de l'API Enhanced..."
            pkill -f "api-matching-enhanced-v2.py" 2>/dev/null || log_warning "Aucun processus Enhanced API trouvé"
            log_success "API Enhanced arrêtée"
            ;;
        7)
            log_info "Documentation disponible:"
            echo "📖 README_V2.1_ENHANCED.md - Guide complet"
            echo "🧪 test_matching_system.py --help - Options de test"
            echo "🌐 http://localhost:$ENHANCED_API_PORT/health - Info API"
            echo "📡 Endpoints API:"
            echo "   • GET  /health"
            echo "   • POST /api/matching/enhanced"
            echo "   • GET  /api/test/hugo-salvat"
            ;;
        0)
            log_info "Au revoir !"
            break
            ;;
        *)
            log_warning "Option invalide. Choisissez entre 0 et 7."
            ;;
    esac
    
    echo ""
done

# 6. Résumé final
echo ""
echo "📊 RÉSUMÉ DU SYSTÈME"
echo "==================="
log_info "Services actifs:"
check_port $CV_PARSER_PORT "CV Parser V2" && echo "   ✅ CV Parser V2: http://localhost:$CV_PARSER_PORT"
check_port $JOB_PARSER_PORT "Job Parser V2" && echo "   ✅ Job Parser V2: http://localhost:$JOB_PARSER_PORT"
check_port $ENHANCED_API_PORT "Enhanced API" && echo "   ✅ Enhanced API: http://localhost:$ENHANCED_API_PORT"

echo ""
log_info "Commandes utiles:"
echo "   • Test complet: python test_matching_system.py --predefined-tests --sample-test"
echo "   • API Health: curl http://localhost:$ENHANCED_API_PORT/health"
echo "   • Test Hugo: curl http://localhost:$ENHANCED_API_PORT/api/test/hugo-salvat"
echo "   • Logs API: tail -f enhanced_api.log"

echo ""
log_success "SuperSmartMatch V2.1 Enhanced est prêt ! 🚀"
echo "Consultez README_V2.1_ENHANCED.md pour plus de détails."
