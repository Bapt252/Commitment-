#!/bin/bash

# Script de démarrage optimisé pour SuperSmartMatch avec infrastructure existante
# Compatible avec PostgreSQL + Redis + MinIO existants

set -e

echo "🚀 Configuration SuperSmartMatch v2.1 - Pondération Dynamique"
echo "==============================================================="

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Vérification des prérequis
echo ""
print_info "Vérification des prérequis..."

if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose n'est pas installé"
    exit 1
fi

print_status "Docker et Docker Compose sont installés"

# Vérification de la structure des dossiers
echo ""
print_info "Vérification de la structure des dossiers..."

if [ ! -d "super-smart-match" ]; then
    print_error "Le dossier super-smart-match n'existe pas"
    exit 1
fi

if [ ! -f "super-smart-match/app.py" ]; then
    print_error "Le fichier super-smart-match/app.py n'existe pas"
    exit 1
fi

if [ ! -f "super-smart-match/Dockerfile" ]; then
    print_error "Le fichier super-smart-match/Dockerfile n'existe pas"
    exit 1
fi

print_status "Structure des dossiers SuperSmartMatch OK"

# Vérification et création du fichier .env
echo ""
print_info "Configuration des variables d'environnement..."

if [ ! -f ".env" ]; then
    print_warning "Fichier .env non trouvé, création depuis .env.example"
    
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "Fichier .env créé depuis .env.example"
    else
        print_error "Fichier .env.example non trouvé"
        exit 1
    fi
else
    print_status "Fichier .env existant"
fi

# Vérification des variables critiques
echo ""
print_info "Vérification des variables critiques..."

if ! grep -q "OPENAI=" .env || grep -q "OPENAI=your_openai_api_key_here" .env; then
    print_warning "Clé API OpenAI non configurée"
    echo "⚠️  Veuillez configurer votre clé API OpenAI dans le fichier .env"
    echo "   OPENAI=your_actual_openai_api_key_here"
    echo ""
    read -p "Voulez-vous continuer sans clé OpenAI ? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Configuration interrompue. Configurez votre clé OpenAI et relancez le script."
        exit 1
    fi
else
    print_status "Clé API OpenAI configurée"
fi

if ! grep -q "SECRET_KEY=" .env || grep -q "SECRET_KEY=your-super-secret-key" .env; then
    print_warning "Clé secrète SuperSmartMatch non configurée - génération automatique"
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "super-secret-key-$(date +%s)")
    sed -i.bak "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" .env
    print_status "Clé secrète générée automatiquement"
fi

# Vérification de l'état des services Docker existants
echo ""
print_info "Vérification de l'infrastructure existante..."

if docker ps --format "table {{.Names}}" | grep -q "nexten-postgres"; then
    print_status "PostgreSQL (nexten-postgres) est en cours d'exécution"
    POSTGRES_RUNNING=true
else
    print_warning "PostgreSQL (nexten-postgres) n'est pas en cours d'exécution"
    POSTGRES_RUNNING=false
fi

if docker ps --format "table {{.Names}}" | grep -q "nexten-redis"; then
    print_status "Redis (nexten-redis) est en cours d'exécution"
    REDIS_RUNNING=true
else
    print_warning "Redis (nexten-redis) n'est pas en cours d'exécution"
    REDIS_RUNNING=false
fi

# Choix du mode de démarrage
echo ""
print_info "Choix du mode de démarrage..."
echo "1. Démarrer uniquement SuperSmartMatch (infrastructure existante requise)"
echo "2. Démarrer toute l'infrastructure (recommandé pour un nouveau déploiement)"
echo "3. Redémarrer SuperSmartMatch seulement"
echo ""
read -p "Choisissez une option (1-3): " choice

case $choice in
    1)
        if [ "$POSTGRES_RUNNING" = false ] || [ "$REDIS_RUNNING" = false ]; then
            print_error "Infrastructure non disponible. Utilisez l'option 2 pour démarrer toute l'infrastructure."
            exit 1
        fi
        
        print_info "Démarrage de SuperSmartMatch uniquement..."
        docker-compose up -d supersmartmatch-service
        ;;
    2)
        print_info "Démarrage de toute l'infrastructure Nexten..."
        docker-compose up -d
        ;;
    3)
        print_info "Redémarrage de SuperSmartMatch..."
        docker-compose restart supersmartmatch-service
        ;;
    *)
        print_error "Option invalide"
        exit 1
        ;;
esac

# Attendre que SuperSmartMatch soit prêt
echo ""
print_info "Attente du démarrage de SuperSmartMatch..."

max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s -f http://localhost:5062/api/v1/health > /dev/null 2>&1; then
        print_status "SuperSmartMatch est opérationnel!"
        break
    fi
    
    echo -n "."
    sleep 2
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    print_error "SuperSmartMatch n'a pas démarré dans les temps (60 secondes)"
    echo ""
    print_info "Vérification des logs..."
    docker-compose logs --tail=20 supersmartmatch-service
    exit 1
fi

# Tests de connectivité
echo ""
print_info "Tests de connectivité..."

# Test API Health
if curl -s -f http://localhost:5062/api/v1/health > /dev/null; then
    print_status "API Health: OK"
else
    print_warning "API Health: ÉCHEC"
fi

# Test des algorithmes
if curl -s -f http://localhost:5062/api/algorithms > /dev/null; then
    print_status "API Algorithms: OK"
else
    print_warning "API Algorithms: ÉCHEC"
fi

# Test des données de test
if curl -s -f http://localhost:5062/api/test-data > /dev/null; then
    print_status "API Test Data: OK"
else
    print_warning "API Test Data: ÉCHEC"
fi

# Affichage du statut final
echo ""
echo "🎉 SuperSmartMatch v2.1 est configuré et opérationnel!"
echo "==============================================="
echo ""
print_info "URLs d'accès:"
echo "   • SuperSmartMatch API: http://localhost:5062"
echo "   • Health Check: http://localhost:5062/api/v1/health"
echo "   • Documentation: http://localhost:5062/api/algorithms"
echo "   • Données de test: http://localhost:5062/api/test-data"
echo ""
print_info "Infrastructure Nexten:"
echo "   • API Principale: http://localhost:5050"
echo "   • Frontend: http://localhost:3000"
echo "   • MinIO Console: http://localhost:9001"
echo "   • Redis Commander: http://localhost:8081"
echo "   • RQ Dashboard: http://localhost:9181"
echo ""
print_info "Nouvelles fonctionnalités v2.1:"
echo "   🎛️ Pondération dynamique basée sur priorités candidat"
echo "   📈 4 leviers: Évolution, Rémunération, Proximité, Flexibilité"
echo "   🔄 Nouveau critère flexibilité (télétravail, horaires, RTT)"
echo "   🧠 Raisonnement intelligent et analyse des risques"
echo "   📊 Analytics et monitoring avancés"
echo "   🔄 Matching bidirectionnel (candidat ↔ entreprise)"
echo ""
print_info "Endpoints v2.1:"
echo "   • POST /api/candidate/<id>/questionnaire - Priorités candidat"
echo "   • POST /api/analytics/weighting-impact - Comparaison impact"
echo "   • GET  /api/demo/candidate-profiles - Profils démo"
echo "   • POST /api/match - Matching candidat → jobs"
echo "   • POST /api/match-candidates - Matching entreprise → candidats"
echo ""
print_status "Configuration terminée avec succès!"

# Affichage des logs en temps réel (optionnel)
echo ""
read -p "Voulez-vous afficher les logs de SuperSmartMatch en temps réel ? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Affichage des logs SuperSmartMatch (Ctrl+C pour arrêter)..."
    docker-compose logs -f supersmartmatch-service
fi
