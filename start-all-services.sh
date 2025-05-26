#!/bin/bash

# Script de démarrage global pour Nexten avec SuperSmartMatch
# Auteur: Nexten Team
# Version: 2.0.0 - Intégration SuperSmartMatch

echo "🚀 DÉMARRAGE NEXTEN - PLATEFORME COMPLÈTE"
echo "====================================================================="
echo "🆕 NOUVEAUTÉ : SuperSmartMatch - Service Unifié de Matching inclus !"
echo "====================================================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_status() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${PURPLE}ℹ️  $1${NC}"
}

# Vérification des prérequis
print_status "Vérification des prérequis..."

if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

print_success "Docker et Docker Compose sont disponibles"

# Vérification du fichier .env
if [ ! -f ".env" ]; then
    print_warning "Fichier .env manquant. Création depuis .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_info "Veuillez éditer le fichier .env avec vos clés API"
    else
        print_error "Fichier .env.example manquant. Création d'un .env minimal..."
        cat > .env << EOF
# Configuration Nexten
OPENAI=your_openai_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
WEBHOOK_SECRET=your_webhook_secret_here
EOF
        print_warning "⚠️  IMPORTANT: Éditez le fichier .env avec vos vraies clés API !"
    fi
fi

# Nettoyage des anciens conteneurs si demandé
if [ "$1" = "--clean" ] || [ "$1" = "-c" ]; then
    print_status "Nettoyage des anciens conteneurs..."
    docker-compose down -v
    docker system prune -f
    print_success "Nettoyage terminé"
fi

# Arrêt des anciens conteneurs
print_status "Arrêt des services existants..."
docker-compose down

# Construction des images
print_status "Construction des images Docker..."
echo "📦 Construction en cours... (cela peut prendre quelques minutes)"
docker-compose build --parallel

if [ $? -ne 0 ]; then
    print_error "Erreur lors de la construction des images"
    exit 1
fi

print_success "Images construites avec succès"

# Démarrage des services
print_status "Démarrage des services Nexten..."
echo "🔄 Démarrage en cours..."

# Démarrage avec ordre de dépendance
docker-compose up -d postgres redis storage
print_info "Base de données et stockage démarrés..."
sleep 5

# Services de parsing
docker-compose up -d cv-parser cv-parser-worker job-parser job-parser-worker
print_info "Services de parsing démarrés..."
sleep 3

# Services de matching et intelligence
docker-compose up -d matching-api matching-worker-high matching-worker-standard matching-worker-bulk
print_info "Services de matching traditionnels démarrés..."
sleep 3

# 🚀 NOUVEAU : SuperSmartMatch
docker-compose up -d supersmartmatch
print_success "🚀 SuperSmartMatch (Service Unifié) démarré !"
sleep 3

# Services avancés
docker-compose up -d user-behavior-api feedback-service personalization-service data-adapter
print_info "Services d'IA et personnalisation démarrés..."
sleep 3

# API principale et frontend
docker-compose up -d api frontend
print_info "API principale et frontend démarrés..."
sleep 3

# Services de monitoring
docker-compose up -d redis-commander rq-dashboard
print_info "Services de monitoring démarrés..."

# Vérification du statut
print_status "Vérification du statut des services..."
sleep 10

# Fonction pour vérifier un service
check_service() {
    local service_name=$1
    local url=$2
    local max_retries=30
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        if curl -sf "$url" >/dev/null 2>&1; then
            print_success "$service_name est opérationnel"
            return 0
        fi
        ((retry++))
        sleep 2
    done
    
    print_warning "$service_name - timeout (peut encore démarrer)"
    return 1
}

# Vérification des services principaux
echo ""
print_status "Vérification de la santé des services..."

check_service "API Principale" "http://localhost:5050/health"
check_service "CV Parser" "http://localhost:5051/health"
check_service "Job Parser" "http://localhost:5055/health"
check_service "Matching API" "http://localhost:5052/health"
check_service "🚀 SuperSmartMatch" "http://localhost:5070/health"
check_service "Personnalisation" "http://localhost:5060/health"
check_service "Analyse Comportementale" "http://localhost:5057/health"
check_service "Frontend" "http://localhost:3000"

# Affichage des URLs d'accès
echo ""
echo "===================================================================="
echo -e "${GREEN}🎉 NEXTEN DÉMARRÉ AVEC SUCCÈS !${NC}"
echo "===================================================================="
echo ""
echo -e "${BLUE}🌐 ACCÈS AUX SERVICES${NC}"
echo "===================================================================="
echo "🏠 Frontend Principal        : http://localhost:3000"
echo "🔌 API Principale            : http://localhost:5050"
echo ""
echo -e "${PURPLE}🚀 SUPERSMARTMATCH - NOUVEAU SERVICE UNIFIÉ${NC}"
echo "📡 SuperSmartMatch API        : http://localhost:5070"
echo "📚 Documentation Swagger      : http://localhost:5070/docs"
echo "📖 Documentation ReDoc        : http://localhost:5070/redoc"
echo "🏥 Health Check               : http://localhost:5070/health"
echo "🧠 Algorithmes disponibles    : http://localhost:5070/algorithms"
echo ""
echo -e "${BLUE}🔧 SERVICES INDIVIDUELS (optionnels)${NC}"
echo "📄 CV Parser                 : http://localhost:5051"
echo "📋 Job Parser                : http://localhost:5055"
echo "🎯 Matching API              : http://localhost:5052"
echo "👤 Personnalisation          : http://localhost:5060"
echo "📊 Analyse Comportementale   : http://localhost:5057"
echo "🔄 Feedback Service           : http://localhost:5058"
echo "🔗 Data Adapter              : http://localhost:5053"
echo ""
echo -e "${BLUE}📊 MONITORING ET ADMINISTRATION${NC}"
echo "🗄️  MinIO Console              : http://localhost:9001 (admin/minioadmin)"
echo "📊 Redis Commander           : http://localhost:8081"
echo "📈 RQ Dashboard              : http://localhost:9181"
echo ""
echo -e "${GREEN}🚀 NOUVEAUTÉS SUPERSMARTMATCH${NC}"
echo "===================================================================="
echo "✨ Sélection automatique du meilleur algorithme"
echo "⚡ Interface unifiée pour tous vos algorithmes"
echo "🧠 6 algorithmes intégrés : Original, Enhanced, SmartMatch, Semantic, Custom, Hybrid"
echo "📈 Cache intelligent et fallback automatique"
echo "📊 Comparaisons entre algorithmes en temps réel"
echo ""
echo -e "${YELLOW}📝 MODIFICATION DE VOTRE FRONT-END${NC}"
echo "===================================================================="
echo "Remplacez vos appels multiples par un seul :"
echo "❌ Ancien : http://localhost:5052/api/match (+ 4 autres services)"
echo "✅ Nouveau : http://localhost:5070/api/v1/match (service unifié)"
echo ""
echo -e "${BLUE}📋 TESTS ET VALIDATION${NC}"
echo "===================================================================="
echo "# Tester SuperSmartMatch"
echo "cd super-smart-match-service"
echo "./test-supersmartmatch.sh"
echo ""
echo "# Voir les logs en temps réel"
echo "docker-compose logs -f supersmartmatch"
echo ""
echo "# Arrêter tous les services"
echo "docker-compose down"
echo ""
echo -e "${GREEN}🎯 RECOMMANDATION${NC}"
echo "===================================================================="
echo "👉 Utilisez SuperSmartMatch (port 5070) pour tous vos nouveaux développements"
echo "👉 Migrez progressivement votre front-end vers l'API unifiée"
echo "👉 Les anciens services restent disponibles pour la compatibilité"
echo ""
echo -e "${GREEN}🎉 Nexten est prêt ! Happy Matching ! 🚀${NC}"
echo "===================================================================="

# Test rapide de SuperSmartMatch
if [ "$1" = "--test" ] || [ "$1" = "-t" ]; then
    echo ""
    print_status "Lancement des tests SuperSmartMatch..."
    sleep 5
    cd super-smart-match-service
    chmod +x test-supersmartmatch.sh
    ./test-supersmartmatch.sh
fi
