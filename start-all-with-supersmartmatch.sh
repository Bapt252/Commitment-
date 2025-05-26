#!/bin/bash

# Script de démarrage COMPLET avec SuperSmartMatch
# Auteur: Nexten Team

echo "🚀 NEXTEN - Démarrage avec SuperSmartMatch"
echo "======================================================================"
echo "🎯 Service unifié de matching - Tous vos algorithmes en un seul endpoint"
echo "======================================================================"

# Configuration
SERVICES_TO_START="postgres redis storage supersmartmatch api cv-parser job-parser matching-api personalization-service data-adapter frontend"
WAIT_TIME=5

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Fonction pour afficher les étapes
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérification des prérequis
print_step "Vérification des prérequis..."

if ! command -v docker &> /dev/null; then
    print_error "Docker n'est pas installé"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose n'est pas installé"
    exit 1
fi

print_success "Docker et Docker Compose disponibles"

# Vérification du fichier .env
if [ ! -f ".env" ]; then
    print_warning "Fichier .env non trouvé"
    if [ -f ".env.example" ]; then
        print_step "Création du fichier .env depuis .env.example..."
        cp .env.example .env
        print_warning "⚠️ IMPORTANT: Éditez le fichier .env pour ajouter votre clé OpenAI !"
        echo "   Ouvrez .env et ajoutez: OPENAI=votre_cle_api_openai"
    else
        print_error "Fichier .env.example non trouvé"
        echo "Créez un fichier .env avec au minimum:"
        echo "OPENAI=votre_cle_api_openai"
        exit 1
    fi
else
    print_success "Fichier .env trouvé"
fi

# Nettoyage des anciens conteneurs
print_step "Nettoyage des anciens conteneurs..."
docker-compose down --remove-orphans

# Construction des images
print_step "Construction des images Docker..."
docker-compose build --parallel

if [ $? -ne 0 ]; then
    print_error "Erreur lors de la construction des images"
    exit 1
fi

print_success "Images construites avec succès"

# Démarrage des services de base
print_step "Démarrage des services de base (postgres, redis, storage)..."
docker-compose up -d postgres redis storage

echo "Attente de la disponibilité des services de base..."
sleep 15

# Vérification des services de base
print_step "Vérification des services de base..."
for service in postgres redis storage; do
    if docker-compose ps $service | grep -q "(healthy)"; then
        print_success "$service: Opérationnel"
    else
        print_warning "$service: En cours de démarrage..."
    fi
done

# 🚀 Démarrage de SuperSmartMatch (nouveau service unifié)
print_step "🚀 Démarrage de SuperSmartMatch - Service Unifié de Matching..."
docker-compose up -d supersmartmatch

echo "Attente du démarrage de SuperSmartMatch..."
sleep 10

if docker-compose ps supersmartmatch | grep -q "(healthy)\|(starting)"; then
    print_success "🎯 SuperSmartMatch: Démarré avec succès"
else
    print_warning "🔄 SuperSmartMatch: En cours de démarrage..."
fi

# Démarrage des services de parsing
print_step "Démarrage des services de parsing..."
docker-compose up -d cv-parser cv-parser-worker job-parser job-parser-worker

echo "Attente des services de parsing..."
sleep 10

# Démarrage des services de matching
print_step "Démarrage des services de matching..."
docker-compose up -d matching-api matching-worker-high matching-worker-standard

echo "Attente des services de matching..."
sleep 10

# Démarrage des services avancés
print_step "Démarrage des services avancés..."
docker-compose up -d personalization-service user-behavior-api feedback-service data-adapter

echo "Attente des services avancés..."
sleep 10

# Démarrage de l'API principale
print_step "Démarrage de l'API principale..."
docker-compose up -d api

echo "Attente de l'API principale..."
sleep 10

# Démarrage du frontend
print_step "Démarrage du frontend..."
docker-compose up -d frontend

echo "Attente du frontend..."
sleep 10

# Démarrage des outils de monitoring
print_step "Démarrage des outils de monitoring..."
docker-compose up -d redis-commander rq-dashboard

echo "Attente des outils de monitoring..."
sleep 5

# Vérification finale des services
echo ""
echo "======================================================================"
print_step "🔍 Vérification finale des services"
echo "======================================================================"

# Fonction pour vérifier un service
check_service() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-""}
    
    echo -n "  Vérification de $service_name ($port)... "
    
    if curl -s --max-time 5 "http://localhost:$port$endpoint" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        echo -e "${RED}❌ KO${NC}"
        return 1
    fi
}

# Vérification des services principaux
check_service "🚀 SuperSmartMatch (UNIFIÉ)" "5070" "/health"
check_service "🌐 API Principale" "5050" "/health"
check_service "📄 CV Parser" "5051" "/health"
check_service "📋 Job Parser" "5055" "/health"
check_service "🎯 Matching API" "5052" "/health"
check_service "🎨 Personnalisation" "5060" "/health"
check_service "📊 Analyse Comportementale" "5057" "/health"
check_service "🔄 Data Adapter" "5053" "/health"
check_service "🖥️ Frontend" "3000" "/"

# Services de monitoring
echo ""
print_step "🔧 Outils de monitoring"
check_service "Redis Commander" "8081" "/"
check_service "RQ Dashboard" "9181" "/"
check_service "MinIO Console" "9001" "/"

echo ""
echo "======================================================================"
print_success "🎉 NEXTEN avec SuperSmartMatch démarré avec succès !"
echo "======================================================================"

echo ""
echo -e "${CYAN}🚀 SUPERSMARTMATCH - SERVICE UNIFIÉ${NC}"
echo "======================================================================"
echo -e "${MAGENTA}📡 API SuperSmartMatch:${NC}      http://localhost:5070"
echo -e "${MAGENTA}📚 Documentation Swagger:${NC}    http://localhost:5070/docs"
echo -e "${MAGENTA}📖 Documentation ReDoc:${NC}      http://localhost:5070/redoc"
echo -e "${MAGENTA}🔍 Health Check:${NC}             http://localhost:5070/health"
echo -e "${MAGENTA}🧠 Algorithmes disponibles:${NC} http://localhost:5070/algorithms"
echo ""
echo -e "${YELLOW}💡 NOUVEAU: Un seul endpoint pour tous vos algorithmes !${NC}"
echo "   Au lieu de 5 services séparés, utilisez SuperSmartMatch"
echo "   Sélection automatique du meilleur algorithme selon le contexte"
echo ""

echo -e "${CYAN}🌐 SERVICES PRINCIPAUX${NC}"
echo "======================================================================"
echo -e "${GREEN}📱 Frontend:${NC}                 http://localhost:3000"
echo -e "${GREEN}🌐 API Principale:${NC}          http://localhost:5050"
echo -e "${GREEN}📄 CV Parser:${NC}               http://localhost:5051"
echo -e "${GREEN}📋 Job Parser:${NC}              http://localhost:5055"
echo -e "${GREEN}🎯 Matching API:${NC}            http://localhost:5052"
echo -e "${GREEN}🎨 Personnalisation:${NC}        http://localhost:5060"
echo -e "${GREEN}📊 Analyse Comportementale:${NC} http://localhost:5057"
echo -e "${GREEN}🔄 Data Adapter:${NC}            http://localhost:5053"
echo ""

echo -e "${CYAN}🔧 OUTILS DE MONITORING${NC}"
echo "======================================================================"
echo -e "${BLUE}🗃️ Redis Commander:${NC}         http://localhost:8081"
echo -e "${BLUE}📊 RQ Dashboard:${NC}             http://localhost:9181"
echo -e "${BLUE}💾 MinIO Console:${NC}            http://localhost:9001 (admin/minioadmin)"
echo ""

echo -e "${CYAN}🧪 TESTS RAPIDES${NC}"
echo "======================================================================"
echo "# Test SuperSmartMatch"
echo "curl -X POST http://localhost:5070/api/v1/match \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"candidate\": {\"competences\": [\"Python\"]}, \"jobs\": [{\"id\": 1, \"competences\": [\"Python\"]}], \"algorithm\": \"auto\"}'"
echo ""
echo "# Test santé générale"
echo "curl http://localhost:5070/health"
echo ""

echo -e "${YELLOW}⚠️ IMPORTANT${NC}"
echo "======================================================================"
echo "1. 🔑 Vérifiez que votre clé OpenAI est configurée dans .env"
echo "2. 🚀 Utilisez SuperSmartMatch (port 5070) pour unifier vos algorithmes"
echo "3. 📊 Consultez les logs: docker-compose logs -f supersmartmatch"
echo "4. 🔄 Redémarrage: docker-compose restart supersmartmatch"
echo ""

echo -e "${GREEN}🎯 Prêt pour le matching intelligent avec SuperSmartMatch !${NC}"
