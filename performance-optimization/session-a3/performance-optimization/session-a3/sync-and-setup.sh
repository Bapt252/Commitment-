#!/bin/bash

# Session A3 - Synchronisation et setup des scripts
# Ce script télécharge et configure tous les scripts Session A3

set -euo pipefail

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}🔄 SESSION A3 - SYNCHRONISATION & SETUP${NC}"
echo -e "${CYAN}======================================${NC}"
echo ""

# Vérifier si on est dans le bon dossier
if [[ ! $(pwd) =~ session-a3$ ]]; then
    echo -e "${YELLOW}⚠️  Naviguez d'abord vers le dossier session-a3:${NC}"
    echo -e "${YELLOW}cd performance-optimization/session-a3${NC}"
    exit 1
fi

echo -e "${BLUE}📁 Dossier actuel: $(pwd)${NC}"
echo ""

# 1. Faire un git pull pour récupérer les derniers scripts
echo -e "${BLUE}1. 🔄 Synchronisation avec GitHub...${NC}"
cd ../.. # Retour à la racine du projet

if git status >/dev/null 2>&1; then
    echo "Synchronisation des derniers scripts depuis GitHub..."
    
    # Stash les changements locaux s'il y en a
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo "Sauvegarde des changements locaux..."
        git stash push -m "Session A3 local changes before sync"
    fi
    
    # Pull des derniers changements
    git pull origin main
    
    echo -e "${GREEN}✅ Synchronisation terminée${NC}"
else
    echo -e "${YELLOW}⚠️  Pas un dépôt Git ou problème de connexion${NC}"
fi

# Retour au dossier session-a3
cd performance-optimization/session-a3

# 2. Vérifier la présence des scripts
echo -e "\n${BLUE}2. 📋 Vérification des scripts Session A3...${NC}"

required_scripts=(
    "baseline-profiling.sh"
    "database-optimization.sh"
    "redis-optimization.sh"
    "docker-optimization.sh"
    "code-optimization.sh"
    "validation-final.sh"
    "session-a3-master.sh"
    "monitor-performance.sh"
    "check-validation-status.sh"
    "session-a3-guide.sh"
    "quick-commands.sh"
    "make-executable.sh"
)

missing_scripts=()
for script in "${required_scripts[@]}"; do
    if [ -f "$script" ]; then
        echo -e "  ✅ $script"
    else
        echo -e "  ❌ $script ${RED}(manquant)${NC}"
        missing_scripts+=("$script")
    fi
done

# 3. Créer les scripts manquants si nécessaire
if [ ${#missing_scripts[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}⚠️  ${#missing_scripts[@]} scripts manquants détectés${NC}"
    echo -e "${BLUE}Création des scripts manquants...${NC}"
    
    # Créer check-validation-status.sh si manquant
    if [[ " ${missing_scripts[@]} " =~ " check-validation-status.sh " ]]; then
        echo "Création de check-validation-status.sh..."
        cat > check-validation-status.sh << 'EOF'
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

echo -e "${CYAN}🔍 SESSION A3 - VÉRIFICATION DU STATUT DE VALIDATION${NC}"
echo -e "${CYAN}⏱️  Script lancé à: $(date)${NC}"
echo ""

# 1. Vérifier si le script de validation est en cours
echo -e "${BLUE}1. Vérification du processus de validation...${NC}"

validation_running=$(pgrep -f "validation-final.sh" || echo "")
if [ -n "$validation_running" ]; then
    echo -e "${GREEN}✅ Script validation-final.sh en cours d'exécution (PID: $validation_running)${NC}"
    echo -e "${BLUE}   Démarré depuis: $(ps -o lstart= -p $validation_running 2>/dev/null || echo 'N/A')${NC}"
else
    echo -e "${YELLOW}⚠️  Script validation-final.sh non détecté en cours d'exécution${NC}"
fi

echo ""

# 2. Vérifier l'état des services
echo -e "${BLUE}2. Vérification rapide de l'état des services...${NC}"

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
echo -e "${BLUE}3. Vérification des fichiers de résultats existants...${NC}"

validation_dirs=($(find . -maxdepth 1 -type d -name "validation-*" 2>/dev/null | sort -r))
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
    echo -e "${YELLOW}Aucun dossier de validation trouvé${NC}"
fi

echo ""

# 4. Recommandations basées sur l'état
echo -e "${BLUE}4. Recommandations et prochaines étapes...${NC}"

if [ -n "$validation_running" ]; then
    echo -e "${YELLOW}📋 RECOMMANDATIONS - VALIDATION EN COURS:${NC}"
    echo -e "  ${YELLOW}1. Attendez la fin du script validation-final.sh (~5-10 minutes restantes)${NC}"
    echo -e "  ${YELLOW}2. Surveillez les logs en temps réel: tail -f validation-*/comprehensive_benchmarking.log${NC}"
    echo -e "  ${YELLOW}3. Relancez ce script dans 5 minutes pour vérifier l'avancement${NC}"
    echo -e "  ${YELLOW}4. Une fois terminé, consultez le rapport final dans final-report/${NC}"
else
    if [ ${#validation_dirs[@]} -gt 0 ]; then
        echo -e "${GREEN}✅ Validation Session A3 semble terminée!${NC}"
        echo -e "${GREEN}📋 PROCHAINES ÉTAPES - VALIDATION TERMINÉE:${NC}"
        echo -e "  ${GREEN}1. Consulter le rapport final: final-report/session_a3_final_report_*.md${NC}"
        echo -e "  ${GREEN}2. Analyser les métriques de performance obtenues${NC}"
        echo -e "  ${GREEN}3. Préparer le déploiement de la configuration optimisée${NC}"
        echo -e "  ${GREEN}4. Lancer le monitoring post-optimisation: ./monitor-performance.sh${NC}"
        echo -e "  ${GREEN}5. Commitez et poussez les changements sur GitHub${NC}"
    else
        echo -e "${YELLOW}État indéterminé - vérifiez manuellement${NC}"
        echo -e "${YELLOW}📋 ACTIONS RECOMMANDÉES:${NC}"
        echo -e "  ${YELLOW}1. Relancez le script de validation: ./validation-final.sh${NC}"
        echo -e "  ${YELLOW}2. Vérifiez l'état des services Docker${NC}"
        echo -e "  ${YELLOW}3. Consultez les logs Docker: docker-compose logs${NC}"
    fi
fi

echo ""
echo -e "${CYAN}🔄 Pour relancer cette vérification: ./check-validation-status.sh${NC}"
echo -e "${CYAN}📊 Pour monitoring continu: ./monitor-performance.sh${NC}"
EOF
    fi
    
    # Créer quick-commands.sh si manquant
    if [[ " ${missing_scripts[@]} " =~ " quick-commands.sh " ]]; then
        echo "Création de quick-commands.sh..."
        cat > quick-commands.sh << 'EOF'
#!/bin/bash

# Session A3 - Commandes rapides pendant l'attente de validation

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${CYAN}🚀 SESSION A3 - COMMANDES RAPIDES${NC}"
echo -e "${CYAN}================================${NC}"

echo -e "\n${BLUE}1. 📊 ÉTAT DES SERVICES${NC}"
services=("5050:API-Principal" "5051:CV-Parser" "5052:Matching-API")

for service in "${services[@]}"; do
    port=$(echo "$service" | cut -d: -f1)
    name=$(echo "$service" | cut -d: -f2)
    
    if curl -s -f "http://localhost:$port/health" --max-time 2 >/dev/null 2>&1; then
        echo -e "  ✅ $name (port $port)"
    else
        echo -e "  ❌ $name (port $port)"
    fi
done

echo -e "\n${BLUE}2. 🔍 PROCESSUS VALIDATION${NC}"
validation_pid=$(pgrep -f "validation-final.sh" 2>/dev/null || echo "")
if [ -n "$validation_pid" ]; then
    echo -e "✅ Script validation-final.sh en cours (PID: $validation_pid)"
else
    echo -e "❌ Aucune validation en cours"
fi

echo -e "\n${BLUE}3. 💡 COMMANDES UTILES${NC}"
echo -e "${GREEN}Pendant l'attente de validation:${NC}"
echo -e "  ${CYAN}./check-validation-status.sh${NC}     - Vérifier l'avancement"
echo -e "  ${CYAN}docker-compose logs -f --tail 10${NC} - Logs en temps réel"

echo -e "\n${GREEN}Après la validation:${NC}"
echo -e "  ${CYAN}./monitor-performance.sh${NC}         - Monitoring post-optimisation"
echo -e "  ${CYAN}git add . && git commit -m 'Session A3 completed'${NC} - Commit des résultats"
EOF
    fi
fi

# 4. Rendre tous les scripts exécutables
echo -e "\n${BLUE}4. 🔧 Configuration des permissions...${NC}"
chmod +x *.sh 2>/dev/null || true

echo -e "${GREEN}✅ Tous les scripts sont maintenant exécutables${NC}"

# 5. Vérification finale
echo -e "\n${BLUE}5. ✅ Vérification finale...${NC}"
echo "Scripts Session A3 disponibles:"

for script in "${required_scripts[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        echo -e "  ✅ $script"
    elif [ -f "$script" ]; then
        echo -e "  ⚠️  $script (pas exécutable)"
    else
        echo -e "  ❌ $script (manquant)"
    fi
done

echo ""
echo -e "${GREEN}🎯 SESSION A3 SETUP TERMINÉ!${NC}"
echo ""
echo -e "${CYAN}Commandes principales:${NC}"
echo -e "  ${CYAN}./check-validation-status.sh${NC}     - Vérifier l'état de validation"
echo -e "  ${CYAN}./quick-commands.sh${NC}              - Commandes rapides"
echo -e "  ${CYAN}./validation-final.sh${NC}            - Lancer validation finale"
echo -e "  ${CYAN}./monitor-performance.sh${NC}         - Monitoring performance"
