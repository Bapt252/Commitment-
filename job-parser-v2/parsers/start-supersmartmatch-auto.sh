#!/bin/bash

echo "🚀 Démarrage automatique de SuperSmartMatch"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}▶️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Étape 1: Vérifier si SuperSmartMatch est déjà actif
print_step "Vérification de l'état actuel de SuperSmartMatch..."

for port in 5062 5061 5060; do
    if curl -s --connect-timeout 2 "http://localhost:$port/health" > /dev/null 2>&1; then
        print_success "SuperSmartMatch déjà actif sur port $port"
        curl -s "http://localhost:$port/health" | python3 -m json.tool 2>/dev/null
        echo ""
        echo "🧪 Lancement du test automatique..."
        chmod +x test-supersmartmatch-auto-detect.sh
        ./test-supersmartmatch-auto-detect.sh
        exit 0
    fi
done

print_warning "SuperSmartMatch non actif, tentative de démarrage..."

# Étape 2: Rechercher les fichiers docker-compose avec SuperSmartMatch
print_step "Recherche des configurations SuperSmartMatch..."

COMPOSE_FILES=(
    "docker-compose.yml"
    "docker-compose.supersmartmatch.yml"
    "docker-compose.v2.yml"
    "matching-service/docker-compose.yml"
    "matching-service/docker-compose.v2.yml"
)

FOUND_COMPOSE=""
for file in "${COMPOSE_FILES[@]}"; do
    if [ -f "$file" ]; then
        if grep -q -i "supersmartmatch" "$file" 2>/dev/null; then
            print_success "Configuration SuperSmartMatch trouvée: $file"
            FOUND_COMPOSE="$file"
            break
        fi
    fi
done

# Étape 3: Démarrer SuperSmartMatch
if [ -n "$FOUND_COMPOSE" ]; then
    print_step "Démarrage de SuperSmartMatch avec $FOUND_COMPOSE..."
    
    # Extraire le nom du service SuperSmartMatch
    SERVICE_NAME=$(grep -A 5 -B 5 -i "supersmartmatch" "$FOUND_COMPOSE" | grep -E "^\s*[a-zA-Z].*:" | head -1 | sed 's/://g' | xargs)
    
    if [ -n "$SERVICE_NAME" ]; then
        print_step "Démarrage du service: $SERVICE_NAME"
        docker-compose -f "$FOUND_COMPOSE" up -d "$SERVICE_NAME"
    else
        print_step "Démarrage de tous les services SuperSmartMatch"
        docker-compose -f "$FOUND_COMPOSE" up -d
    fi
    
    print_step "Attente du démarrage (30 secondes)..."
    sleep 30
    
else
    print_warning "Aucune configuration SuperSmartMatch trouvée"
    print_step "Tentative de démarrage avec docker-compose standard..."
    
    # Chercher des services avec "smart" ou "match" dans le nom
    if [ -f "docker-compose.yml" ]; then
        SMART_SERVICES=$(grep -E "^\s*.*smart.*:" docker-compose.yml | sed 's/://g' | xargs)
        MATCH_SERVICES=$(grep -E "^\s*.*match.*:" docker-compose.yml | sed 's/://g' | xargs)
        
        if [ -n "$SMART_SERVICES" ]; then
            print_step "Démarrage des services 'smart': $SMART_SERVICES"
            docker-compose up -d $SMART_SERVICES
        fi
        
        if [ -n "$MATCH_SERVICES" ]; then
            print_step "Démarrage des services 'match': $MATCH_SERVICES"
            docker-compose up -d $MATCH_SERVICES
        fi
        
        if [ -z "$SMART_SERVICES" ] && [ -z "$MATCH_SERVICES" ]; then
            print_step "Démarrage de tous les services"
            docker-compose up -d
        fi
    else
        print_error "Aucun fichier docker-compose.yml trouvé"
        exit 1
    fi
    
    print_step "Attente du démarrage (30 secondes)..."
    sleep 30
fi

# Étape 4: Vérifier que SuperSmartMatch est maintenant actif
print_step "Vérification du démarrage..."

SUPERSMARTMATCH_FOUND=false
for port in 5062 5061 5060 5052; do
    health_response=$(curl -s --connect-timeout 3 "http://localhost:$port/health" 2>/dev/null)
    if [[ $? -eq 0 ]] && [[ "$health_response" == *"healthy"* ]]; then
        print_success "Service actif sur port $port"
        echo "$health_response" | python3 -m json.tool 2>/dev/null
        
        # Test si c'est SuperSmartMatch
        match_test=$(curl -s --connect-timeout 2 "http://localhost:$port/match" -X POST \
            -H "Content-Type: application/json" \
            -d '{"candidate":{"name":"test"},"offers":[{"id":"test"}]}' 2>/dev/null)
            
        if [[ $? -eq 0 ]] && [[ "$match_test" != *"Not Found"* ]] && [[ "$match_test" != *"404"* ]]; then
            print_success "SuperSmartMatch confirmé sur port $port !"
            SUPERSMARTMATCH_FOUND=true
        fi
    fi
done

# Étape 5: Lancer les tests
if [ "$SUPERSMARTMATCH_FOUND" = true ]; then
    echo ""
    print_success "SuperSmartMatch démarré avec succès !"
    print_step "Lancement des tests automatiques..."
    
    chmod +x test-supersmartmatch-auto-detect.sh
    ./test-supersmartmatch-auto-detect.sh
    
else
    print_warning "SuperSmartMatch démarré mais pas complètement opérationnel"
    print_step "Test du service de matching disponible..."
    
    chmod +x test-supersmartmatch-auto-detect.sh
    ./test-supersmartmatch-auto-detect.sh
fi

echo ""
echo "🔍 Pour diagnostiquer manuellement:"
echo "   docker ps | grep -i smart"
echo "   docker-compose logs | grep -i smart"
echo "   curl http://localhost:5062/health"
echo "   curl http://localhost:5052/health"