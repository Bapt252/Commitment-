#!/bin/bash

# Fix SuperSmartMatch - Version Rapide et Corrigée
# Résout le problème de port 5060 et les warnings d'import SmartMatch

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Fix SuperSmartMatch - Version Rapide${NC}"
echo "=========================================="

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

# 1. Déterminer un port libre
determine_port() {
    local test_port
    for test_port in 5060 5061 5062 5063; do
        if ! lsof -ti :$test_port > /dev/null 2>&1; then
            echo $test_port
            return 0
        fi
    done
    echo 5064  # Port de fallback
}

# 2. Arrêter les processus Docker qui utilisent le port 5060
stop_docker_processes() {
    log_info "Vérification des processus Docker sur le port 5060..."
    
    local pids=$(lsof -ti :5060 2>/dev/null | head -3)  # Limiter à 3 processus max
    
    if [ -n "$pids" ]; then
        log_warning "Arrêt des processus Docker occupant le port 5060..."
        for pid in $pids; do
            if ps -p $pid > /dev/null 2>&1; then
                kill -TERM $pid 2>/dev/null || true
                sleep 1
            fi
        done
        sleep 2
    fi
}

# 3. Corriger le fichier app.py de SuperSmartMatch
fix_app_py() {
    log_info "Correction du fichier super-smart-match/app.py..."
    
    if [ ! -f "super-smart-match/app.py" ]; then
        log_error "Fichier super-smart-match/app.py non trouvé"
        return 1
    fi
    
    # Créer une sauvegarde
    cp "super-smart-match/app.py" "super-smart-match/app.py.backup"
    
    # Remplacer la ligne problématique du port par défaut
    sed -i '' 's/port = int(os.environ.get(.PORT., 5060))/port = int(os.environ.get("PORT", 5061))/' "super-smart-match/app.py" 2>/dev/null || \
    sed -i 's/port = int(os.environ.get(.PORT., 5060))/port = int(os.environ.get("PORT", 5061))/' "super-smart-match/app.py" 2>/dev/null || true
    
    # Ajouter une gestion d'erreur plus robuste pour SmartMatch
    cat > "super-smart-match/app_patch.py" << 'EOF'
# Patch pour imports SmartMatch robustes
import sys
import os

# Ajouter le répertoire parent pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def safe_import_smartmatch():
    """Import sécurisé de SmartMatch avec fallback"""
    try:
        # Essayer différents chemins
        import app.smartmatch as smartmatch_module
        return smartmatch_module
    except ImportError:
        try:
            import smartmatch as smartmatch_module
            return smartmatch_module
        except ImportError:
            return None

def create_simple_fallback():
    """Créer un algorithme de fallback simple"""
    def simple_matching(cv_data, questionnaire_data, job_data):
        results = []
        candidate_skills = set(cv_data.get('competences', []))
        
        for job in job_data:
            job_skills = set(job.get('competences', []))
            
            if candidate_skills and job_skills:
                common_skills = candidate_skills.intersection(job_skills)
                score = (len(common_skills) / len(job_skills)) * 100 if job_skills else 50
            else:
                score = 50
            
            job_copy = job.copy()
            job_copy['matching_score'] = min(100, max(0, int(score)))
            results.append(job_copy)
        
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    return simple_matching
EOF
    
    log_success "Fichier app.py préparé avec corrections"
}

# 4. Installer les dépendances
setup_environment() {
    log_info "Configuration de l'environnement..."
    
    cd super-smart-match
    
    # Créer un environnement virtuel s'il n'existe pas
    if [ ! -d "venv" ]; then
        log_info "Création de l'environnement virtuel..."
        python3 -m venv venv
    fi
    
    # Activer et installer les dépendances
    source venv/bin/activate
    pip install --quiet flask flask-cors
    
    cd ..
    log_success "Environnement configuré"
}

# 5. Créer le script de démarrage simple
create_startup_script() {
    local port=$1
    
    log_info "Création du script de démarrage simple..."
    
    cat > "start-supersmartmatch-simple.sh" << EOF
#!/bin/bash

echo "🚀 Démarrage de SuperSmartMatch sur le port $port"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 requis"
    exit 1
fi

# Aller dans le répertoire et activer venv
cd super-smart-match
source venv/bin/activate

# Variables d'environnement
export PYTHONPATH="\$(pwd)/..:$PYTHONPATH"
export PORT=$port

echo "🎯 SuperSmartMatch disponible sur: http://localhost:$port"
echo "📊 Endpoints:"
echo "   - Health: http://localhost:$port/api/health"
echo "   - Match: http://localhost:$port/api/match"

# Démarrer
python3 app.py
EOF
    
    chmod +x "start-supersmartmatch-simple.sh"
    log_success "Script de démarrage créé: start-supersmartmatch-simple.sh"
}

# 6. Créer un script de test simple
create_test_script() {
    local port=$1
    
    cat > "test-supersmartmatch-simple.sh" << EOF
#!/bin/bash

PORT=$port
echo "🧪 Test rapide de SuperSmartMatch sur le port $PORT"

# Test de santé
echo "1️⃣ Test de santé..."
curl -s "http://localhost:$PORT/api/health" | head -200

echo ""
echo "2️⃣ Test de matching simple..."
curl -s -X POST "http://localhost:$PORT/api/match" \\
  -H "Content-Type: application/json" \\
  -d '{
    "cv_data": {
      "competences": ["Python", "JavaScript"],
      "annees_experience": 3
    },
    "questionnaire_data": {
      "adresse": "Paris",
      "salaire_souhaite": 45000
    },
    "job_data": [
      {
        "id": "job1",
        "titre": "Développeur",
        "competences": ["Python", "React"],
        "localisation": "Paris"
      }
    ],
    "algorithm": "auto"
  }' | head -500

echo ""
echo "🎯 Tests terminés"
EOF
    
    chmod +x "test-supersmartmatch-simple.sh"
    log_success "Script de test créé: test-supersmartmatch-simple.sh"
}

# Fonction principale
main() {
    # 1. Arrêter Docker sur le port 5060
    stop_docker_processes
    
    # 2. Déterminer le port à utiliser
    PORT=$(determine_port)
    log_info "Port sélectionné: $PORT"
    
    # 3. Corriger app.py
    fix_app_py
    
    # 4. Configurer l'environnement
    setup_environment
    
    # 5. Créer les scripts
    create_startup_script $PORT
    create_test_script $PORT
    
    echo ""
    log_success "🎉 SuperSmartMatch prêt !"
    echo ""
    echo "🚀 Démarrage:"
    echo "   ./start-supersmartmatch-simple.sh"
    echo ""
    echo "🧪 Test:"
    echo "   ./test-supersmartmatch-simple.sh"
    echo ""
    echo "🌐 URL: http://localhost:$PORT"
    
    # Demander s'il faut démarrer
    echo ""
    read -p "Démarrer SuperSmartMatch maintenant ? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        log_info "Démarrage de SuperSmartMatch..."
        ./start-supersmartmatch-simple.sh
    fi
}

main "$@"
