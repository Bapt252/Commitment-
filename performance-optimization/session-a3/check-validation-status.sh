#!/bin/bash

# Session A3 - Vérification du statut de la validation finale
# Aide à suivre l'avancement du script validation-final.sh

set -euo pipefail

# Couleurs pour les logs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}🔍 SESSION A3 - VÉRIFICATION DU STATUT DE VALIDATION${NC}"
echo -e "${CYAN}⏱️  Script lancé à: $(date)${NC}"
echo ""

# Fonction pour logger avec timestamp
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING: $1${NC}"
}

success() {
    echo -e "${CYAN}[$(date +'%H:%M:%S')] SUCCESS: $1${NC}"
}

# 1. Vérifier si le script de validation est en cours
log "1. Vérification du processus de validation..."

validation_running=$(pgrep -f "validation-final.sh" || echo "")
if [ -n "$validation_running" ]; then
    success "✅ Script validation-final.sh en cours d'exécution (PID: $validation_running)"
    echo -e "${BLUE}   Démarré depuis: $(ps -o lstart= -p $validation_running 2>/dev/null || echo 'N/A')${NC}"
else
    warning "⚠️  Script validation-final.sh non détecté en cours d'exécution"
fi

echo ""

# 2. Vérifier l'état des services
log "2. Vérification rapide de l'état des services..."

services=(
    "http://localhost:5050/health:API-Principal"
    "http://localhost:5051/health:CV-Parser"
    "http://localhost:5055/health:Job-Parser"
    "http://localhost:5052/health:Matching-API"
    "http://localhost:5060/health:Personalization"
    "http://localhost:5057/health:User-Behavior"
)

services_ready=0
services_total=${#services[@]}

for service in "${services[@]}"; do
    url=$(echo "$service" | cut -d: -f1-2)
    name=$(echo "$service" | cut -d: -f3)
    
    if curl -s -f "$url" --max-time 5 >/dev/null 2>&1; then
        echo -e "  ✅ $name - Ready"
        services_ready=$((services_ready + 1))
    else
        echo -e "  ❌ $name - Not responding"
    fi
done

echo ""
echo -e "${BLUE}Services Status: $services_ready/$services_total ready${NC}"

# 3. Vérifier les fichiers de résultats existants
log "3. Vérification des fichiers de résultats existants..."

validation_dirs=($(find "$SCRIPT_DIR" -maxdepth 1 -type d -name "validation-*" 2>/dev/null | sort -r))
if [ ${#validation_dirs[@]} -gt 0 ]; then
    latest_validation="${validation_dirs[0]}"
    echo -e "${BLUE}Dossier de validation le plus récent: $(basename "$latest_validation")${NC}"
    
    # Vérifier les fichiers de log
    validation_files=(
        "comprehensive_benchmarking.log"
        "database_validation.log" 
        "redis_validation.log"
        "container_validation.log"
        "functional_regression.log"
    )
    
    echo -e "${BLUE}Fichiers de validation générés:${NC}"
    for file in "${validation_files[@]}"; do
        file_path="$latest_validation/$file"
        if [ -f "$file_path" ]; then
            file_size=$(stat -c%s "$file_path" 2>/dev/null || echo "0")
            if [ "$file_size" -gt 0 ]; then
                echo -e "  ✅ $file (${file_size} bytes)"
            else
                echo -e "  ⚠️  $file (vide)"
            fi
        else
            echo -e "  ❌ $file (manquant)"
        fi
    done
else
    warning "Aucun dossier de validation trouvé"
fi

echo ""

# 4. Vérifier les rapports finaux
log "4. Vérification des rapports finaux..."

final_report_dir="$SCRIPT_DIR/final-report"
if [ -d "$final_report_dir" ]; then
    reports=($(find "$final_report_dir" -name "session_a3_final_report_*.md" 2>/dev/null | sort -r))
    if [ ${#reports[@]} -gt 0 ]; then
        latest_report="${reports[0]}"
        echo -e "${BLUE}Rapport final le plus récent: $(basename "$latest_report")${NC}"
        
        if [ -f "$latest_report" ]; then
            report_size=$(stat -c%s "$latest_report" 2>/dev/null || echo "0")
            echo -e "${BLUE}Taille du rapport: ${report_size} bytes${NC}"
            
            # Afficher un aperçu du rapport
            if [ "$report_size" -gt 0 ]; then
                echo -e "${BLUE}Aperçu du rapport:${NC}"
                head -20 "$latest_report" 2>/dev/null || echo "Impossible de lire le rapport"
            fi
        fi
    else
        warning "Aucun rapport final trouvé"
    fi
else
    warning "Dossier final-report non trouvé"
fi

echo ""

# 5. Statistiques Docker rapides
log "5. Statistiques Docker rapides..."

echo -e "${BLUE}Containers Commitment- actifs:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(nexten|commitment)" || echo "Aucun container trouvé"

echo ""

# 6. Recommandations basées sur l'état
log "6. Recommandations et prochaines étapes..."

if [ -n "$validation_running" ]; then
    echo -e "${YELLOW}📋 RECOMMANDATIONS - VALIDATION EN COURS:${NC}"
    echo -e "  ${YELLOW}1. Attendez la fin du script validation-final.sh (~5-10 minutes restantes)${NC}"
    echo -e "  ${YELLOW}2. Surveillez les logs en temps réel: tail -f validation-*/comprehensive_benchmarking.log${NC}"
    echo -e "  ${YELLOW}3. Relancez ce script dans 5 minutes pour vérifier l'avancement${NC}"
    echo -e "  ${YELLOW}4. Une fois terminé, consultez le rapport final dans final-report/${NC}"
else
    if [ ${#validation_dirs[@]} -gt 0 ] && [ -d "$final_report_dir" ] && [ ${#reports[@]} -gt 0 ]; then
        success "✅ Validation Session A3 semble terminée!"
        echo -e "${GREEN}📋 PROCHAINES ÉTAPES - VALIDATION TERMINÉE:${NC}"
        echo -e "  ${GREEN}1. Consulter le rapport final: final-report/session_a3_final_report_*.md${NC}"
        echo -e "  ${GREEN}2. Analyser les métriques de performance obtenues${NC}"
        echo -e "  ${GREEN}3. Préparer le déploiement de la configuration optimisée${NC}"
        echo -e "  ${GREEN}4. Lancer le monitoring post-optimisation: ./monitor-performance.sh${NC}"
        echo -e "  ${GREEN}5. Commitez et poussez les changements sur GitHub${NC}"
    else
        warning "État indéterminé - vérifiez manuellement"
        echo -e "${YELLOW}📋 ACTIONS RECOMMANDÉES:${NC}"
        echo -e "  ${YELLOW}1. Relancez le script de validation: ./validation-final.sh${NC}"
        echo -e "  ${YELLOW}2. Vérifiez l'état des services Docker${NC}"
        echo -e "  ${YELLOW}3. Consultez les logs Docker: docker-compose logs${NC}"
    fi
fi

echo ""
echo -e "${CYAN}🔄 Pour relancer cette vérification: ./check-validation-status.sh${NC}"
echo -e "${CYAN}📊 Pour monitoring continu: ./monitor-performance.sh${NC}"
echo -e "${CYAN}📁 Dossier Session A3: $(pwd)${NC}"
