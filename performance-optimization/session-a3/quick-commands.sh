#!/bin/bash

# Session A3 - Commandes rapides pendant l'attente de validation
# Script utilitaire pour les actions courantes

set -euo pipefail

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}🚀 SESSION A3 - COMMANDES RAPIDES${NC}"
echo -e "${CYAN}================================${NC}"

# 1. Vérification rapide des services
echo -e "\n${BLUE}1. 📊 ÉTAT DES SERVICES${NC}"
echo "Vérification rapide des services principaux..."

services=(
    "5050:API-Principal"
    "5051:CV-Parser" 
    "5052:Matching-API"
    "5055:Job-Parser"
    "5060:Personalization"
)

for service in "${services[@]}"; do
    port=$(echo "$service" | cut -d: -f1)
    name=$(echo "$service" | cut -d: -f2)
    
    if curl -s -f "http://localhost:$port/health" --max-time 2 >/dev/null 2>&1; then
        echo -e "  ✅ $name (port $port)"
    else
        echo -e "  ❌ $name (port $port)"
    fi
done

# 2. Processus de validation
echo -e "\n${BLUE}2. 🔍 PROCESSUS VALIDATION${NC}"
validation_pid=$(pgrep -f "validation-final.sh" 2>/dev/null || echo "")
if [ -n "$validation_pid" ]; then
    echo -e "✅ Script validation-final.sh en cours (PID: $validation_pid)"
    
    # Temps d'exécution
    start_time=$(ps -o lstart= -p $validation_pid 2>/dev/null | head -1)
    echo -e "   Démarré: $start_time"
    
    # Utilisation CPU/RAM
    cpu_mem=$(ps -o pcpu,pmem -p $validation_pid --no-headers 2>/dev/null)
    echo -e "   Ressources: CPU/MEM $cpu_mem"
else
    echo -e "❌ Aucune validation en cours"
fi

# 3. Fichiers de résultats récents
echo -e "\n${BLUE}3. 📁 FICHIERS RÉCENTS${NC}"

# Dossiers de validation
validation_dirs=($(find . -maxdepth 1 -type d -name "validation-*" 2>/dev/null | sort -r | head -2))
if [ ${#validation_dirs[@]} -gt 0 ]; then
    echo "Dossiers de validation récents:"
    for dir in "${validation_dirs[@]}"; do
        dir_time=$(stat -c %Y "$dir" 2>/dev/null)
        dir_time_human=$(date -d @$dir_time "+%H:%M:%S" 2>/dev/null || echo "N/A")
        echo -e "  📁 $(basename "$dir") (créé à $dir_time_human)"
        
        # Contenu du dossier
        file_count=$(find "$dir" -type f 2>/dev/null | wc -l)
        echo -e "     $file_count fichiers générés"
    done
else
    echo -e "   ${YELLOW}Aucun dossier de validation trouvé${NC}"
fi

# 4. Logs Docker récents
echo -e "\n${BLUE}4. 📝 LOGS DOCKER RÉCENTS${NC}"
echo "Dernières lignes des logs des services principaux:"

docker_services=("nexten-api" "nexten-cv-parser" "nexten-matching")
for service in "${docker_services[@]}"; do
    echo -e "\n  ${CYAN}$service:${NC}"
    if docker ps --format "{{.Names}}" | grep -q "$service" 2>/dev/null; then
        docker logs --tail 3 "$service" 2>/dev/null | sed 's/^/    /' || echo "    Logs non disponibles"
    else
        echo -e "    ${YELLOW}Service non trouvé${NC}"
    fi
done

# 5. Statistiques système rapides
echo -e "\n${BLUE}5. ⚡ STATS SYSTÈME${NC}"

# CPU et mémoire
if command -v top >/dev/null 2>&1; then
    echo "Top processus CPU (3 premiers):"
    top -b -n 1 | head -12 | tail -3 | sed 's/^/  /'
fi

# Espace disque Docker
echo -e "\nEspace disque Docker:"
docker system df --format "table {{.Type}}\t{{.TotalCount}}\t{{.Size}}" | sed 's/^/  /'

# 6. Commandes utiles suggérées
echo -e "\n${BLUE}6. 💡 COMMANDES UTILES${NC}"
echo -e "${GREEN}Pendant l'attente de validation:${NC}"
echo -e "  ${CYAN}./check-validation-status.sh${NC}     - Vérifier l'avancement"
echo -e "  ${CYAN}tail -f validation-*/comprehensive_benchmarking.log${NC} - Suivre les benchmarks"
echo -e "  ${CYAN}docker-compose logs -f --tail 10${NC} - Logs en temps réel"
echo -e "  ${CYAN}./session-a3-guide.sh status${NC}     - État complet Session A3"

echo -e "\n${GREEN}Après la validation:${NC}"
echo -e "  ${CYAN}./session-a3-guide.sh report${NC}     - Afficher le rapport final"
echo -e "  ${CYAN}./monitor-performance.sh${NC}         - Monitoring post-optimisation"
echo -e "  ${CYAN}git add . && git commit -m 'Session A3 completed'${NC} - Commit des résultats"

# 7. Estimation du temps restant
echo -e "\n${BLUE}7. ⏰ ESTIMATION TEMPS RESTANT${NC}"
if [ -n "$validation_pid" ]; then
    # Calcul approximatif basé sur l'heure de début
    current_time=$(date +%s)
    start_epoch=$(stat -c %Y /proc/$validation_pid 2>/dev/null || echo "$current_time")
    elapsed=$((current_time - start_epoch))
    
    echo "Temps écoulé: ${elapsed}s (~$((elapsed/60))min)"
    
    # Estimation basée sur la durée totale attendue (5-10 min)
    if [ $elapsed -lt 300 ]; then  # Moins de 5min
        remaining=$((300 - elapsed))
        echo -e "Temps restant estimé: ${remaining}s (~$((remaining/60))min) ${GREEN}[En cours normal]${NC}"
    elif [ $elapsed -lt 600 ]; then  # 5-10min
        remaining=$((600 - elapsed))
        echo -e "Temps restant estimé: ${remaining}s (~$((remaining/60))min) ${YELLOW}[Bientôt fini]${NC}"
    else  # Plus de 10min
        echo -e "${YELLOW}⚠️  Validation plus longue que prévu (>10min)${NC}"
        echo -e "   Vérifiez les logs pour d'éventuels problèmes"
    fi
else
    echo -e "${YELLOW}Aucune validation en cours à surveiller${NC}"
fi

echo -e "\n${CYAN}🔄 Pour rafraîchir ces informations: $0${NC}"
echo -e "${CYAN}📊 Monitoring continu: watch -n 30 '$0'${NC}"
